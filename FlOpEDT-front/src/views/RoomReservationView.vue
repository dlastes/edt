<template>
  <h1>RoomReservation App</h1>
  <CustomDatePicker v-model:week="selectedDate.week" v-model:year="selectedDate.year"></CustomDatePicker>

  <div class="container" style="max-width: 960px;">
    <div class="row">
      <select v-model="selectedRoom" class="form-select w-auto" aria-label="Select room">
        <option :value="undefined">All rooms</option>
        <option v-for="room in rooms" :value="room">{{ room.name }}</option>
      </select>
    </div>
    <div class="row">
      <Calendar v-bind="calendarValues"></Calendar>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FlopAPI } from '@/assets/js/api'
import { convertDecimalTimeToHuman } from '@/assets/js/helpers'
import { apiKey, currentWeekKey, requireInjection } from '@/assets/js/keys'
import type { CourseType, Department, FlopWeek, TimeSettings, WeekDay } from '@/assets/js/types'
import {
  CalendarRoomReservationSlotElement,
  CalendarScheduledCourseSlotElement,
  CalendarSlotElement,
  RoomReservation,
  ScheduledCourse,
  Time
} from '@/assets/js/types'
import Calendar from '@/components/calendar/Calendar.vue'
import CalendarRoomReservationSlot from '@/components/calendar/CalendarRoomReservationSlot.vue'
import CalendarScheduledCourseSlot from '@/components/calendar/CalendarScheduledCourseSlot.vue'
import CustomDatePicker from '@/components/DatePicker.vue'
import { getDepartment } from '@/main'
import { computed, onMounted, ref, shallowRef, watchEffect } from 'vue'

interface Room {
  id: number,
  name: string
}

const api = ref<FlopAPI>(requireInjection(apiKey))
const currentWeek = ref(requireInjection(currentWeekKey))
const currentDepartment = ref(getDepartment())

// API data
const departments = ref<Array<Department>>()
const weekDays = ref<Array<WeekDay>>([])
const rooms = ref<Array<Room>>([])
const scheduledCourses = ref<Array<ScheduledCourse>>([])
const courseTypes = ref<Array<CourseType>>([])
const roomReservations = ref<Array<RoomReservation>>([])

// Time Settings
const timeSettings = ref<Array<TimeSettings>>()
const dayStartTime = ref<Time>({value: 0, text: ''})
const dayFinishTime = ref<Time>({value: 0, text: ''})
const lunchBreakStartTime = ref<Time>({value: 0, text: ''})
const lunchBreakFinishTime = ref<Time>({value: 0, text: ''})

// Fill with current date, uses date picker afterwards
const selectedDate = ref<FlopWeek>({
  week: currentWeek.value.week,
  year: currentWeek.value.year,
})

const selectedRoom = ref<Room>()

const reservations = ref()

const dateSlots = ref<{ [index: string]: Array<{ props: CalendarSlotElement, component: any }> }>({})

const calendarValues = computed(() => {
  return {
    days: weekDays.value,
    slots: dateSlots.value,
    startTime: dayStartTime.value.value - (60 + (dayStartTime.value.value % 60)),
    endTime: dayFinishTime.value.value + (60 - (dayFinishTime.value.value % 60)),
  }
})

// Update weekDays
watchEffect(() => {
  fetchWeekDays(selectedDate.value.week, selectedDate.value.year).then(value => {
    weekDays.value = value
  })
})

watchEffect(() => {
  let department = currentDepartment.value
  if (!department) {
    return
  }
  fetchCourseTypes(department).then(value => {
    courseTypes.value = value
  })
})

// Update room reservations
watchEffect(() => {
  fetchRoomReservations(selectedDate.value.week, selectedDate.value.year, {}).then(value => {
    roomReservations.value = value
  })
})

watchEffect(() => {
  let params: { roomId?: number } = {}
  if (selectedRoom.value) {
    params.roomId = selectedRoom.value.id
  }

  dateSlots.value = {}
  roomReservations.value.forEach(reservation => {
    if (params.roomId && reservation.room.id != params.roomId) {
      return
    }
    let date = reservation.date.split('-')
    let day = `${date[2]}/${date[1]}`
    let startTimeRaw = reservation.start_time.split(':')
    let startTimeValue = parseInt(startTimeRaw[0]) * 60 + parseInt(startTimeRaw[1])
    let startTime = createTime(startTimeValue)
    let endTimeRaw = reservation.end_time.split(':')
    let endTimeValue = parseInt(endTimeRaw[0]) * 60 + parseInt(endTimeRaw[1])
    let endTime: Time = createTime(endTimeValue)

    let slot = new CalendarRoomReservationSlotElement()
    slot.reservation = reservation
    slot.title = reservation.title
    slot.startTime = startTime
    slot.endTime = endTime

    if (!dateSlots.value[day]) {
      dateSlots.value[day] = []
    }
    addSlot(day, slot, shallowRef(CalendarRoomReservationSlot))
  })
})

// Update scheduled courses
watchEffect(() => {
  let params: { department?: string } = {}
  let department = currentDepartment.value
  if (department) {
    params.department = department
  }

  fetchScheduledCourses(selectedDate.value.week, selectedDate.value.year, params).then(value => {
    value.forEach(course => {
      let day = weekDays.value.find(weekDay => {
        return weekDay.ref === course.day
      })

      if (!day) {
        return
      }

      let courseType = courseTypes.value.find(courseType => {
        return courseType.name === course.course.type
      })
      if (!courseType) {
        return
      }
      let date = day.date
      let startTime = createTime(course.start_time)
      let endTime = createTime(course.start_time + courseType.duration)

      let slot = new CalendarScheduledCourseSlotElement()
      slot.course = course
      slot.title = course.course.module.abbrev
      slot.startTime = startTime
      slot.endTime = endTime

      if (!dateSlots.value[date]) {
        dateSlots.value[date] = []
      }
      addSlot(date, slot, shallowRef(CalendarScheduledCourseSlot))
    })
  })
})

// Time settings watcher
watchEffect(() => {
  onTimeSettingsChanged(timeSettings.value)
})

function onTimeSettingsChanged (timeSettings?: Array<TimeSettings>) {
  if (!timeSettings) {
    return
  }

  let minStartTime = timeSettings[0].day_start_time
  let maxFinishTime = timeSettings[0].day_finish_time
  let minLunchBreakStartTime = timeSettings[0].lunch_break_start_time
  let maxLunchBreakFinishTime = timeSettings[0].lunch_break_finish_time
  timeSettings.forEach(setting => {
    minStartTime = Math.min(minStartTime, setting.day_start_time)
    maxFinishTime = Math.max(maxFinishTime, setting.day_finish_time)
    minLunchBreakStartTime = Math.min(minLunchBreakStartTime, setting.lunch_break_start_time)
    maxLunchBreakFinishTime = Math.max(maxLunchBreakFinishTime, setting.lunch_break_finish_time)
  })

  dayStartTime.value = createTime(minStartTime)
  dayFinishTime.value = createTime(maxFinishTime)
  lunchBreakStartTime.value = createTime(minLunchBreakStartTime)
  lunchBreakFinishTime.value = createTime(maxLunchBreakFinishTime)
}

function createTime (time: number): Time {
  let text = convertDecimalTimeToHuman(time / 60)
  return new Time(time, text)
}

function addSlot (date: string, slot: CalendarSlotElement, component: any) {
  if (!dateSlots.value[date]) {
    dateSlots.value[date] = []
  }
  dateSlots.value[date].push({props: slot, component: component})
}

onMounted(() => {
  fetchDepartments().then(value => {
    departments.value = value
  })

  fetchRooms().then(value => {
    rooms.value = value
  })

  fetchTimeSettings().then(value => {
    timeSettings.value = value
  })
})

// Fetch functions
async function fetchDepartments () {
  return await api.value.fetch.all.departments()
}

async function fetchWeekDays (week: number, year: number) {
  return await api.value.fetch.target.weekdays(week, year)
}

async function fetchRooms () {
  let department = getDepartment()
  if (!department) {
    console.log('No department provided, cannot fetch rooms.')
    return []
  }
  return await api.value.fetch.all.rooms(department)
}

async function fetchTimeSettings () {
  return await api.value.fetch.all.timeSettings()
}

async function fetchRoomReservations (week: number, year: number, params: { roomId?: number }) {
  return await api.value.fetch.target.roomReservations(week, year, params)
}

async function fetchScheduledCourses (week: number, year: number, params: { department?: string }) {
  return await api.value.fetch.target.scheduledCourses(week, year, params)
}

async function fetchCourseTypes (department: string) {
  return await api.value.fetch.all.coursetypes(department)
}
</script>

<script lang="ts">
export default {
  name: 'RoomReservationView',
  components: {}
}

</script>

<style scoped>

</style>
