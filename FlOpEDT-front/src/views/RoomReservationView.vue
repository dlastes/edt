<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-auto">
        <CustomDatePicker v-model:week="selectedDate.week" v-model:year="selectedDate.year"></CustomDatePicker>
        <div class="col-auto">
          <div class="mb-3">
            <label for="select-room" class="form-label">Room:</label>
            <select v-model="selectedRoom" id="select-room" class="form-select w-auto" aria-label="Select room">
              <option :value="undefined">All rooms</option>
              <option v-for="room in selectedDepartmentsRooms" :value="room">{{ room.name }}</option>
            </select>
          </div>
          <div class="mb-3">
            <label for="select-department" class="form-label">Department:</label>
            <select v-model="selectedDepartment" id="select-department" class="form-select w-auto ms-1"
                    aria-label="Select department">
              <option :value="undefined">All departments</option>
              <option v-for="dept in departments" :value="dept">{{ dept.abbrev }}</option>
            </select>
          </div>
        </div>
      </div>
      <div class="col">
        <div ref="modalLoading" class="modal fade" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1"
             aria-labelledby="exampleModalLabel"
             aria-hidden="true">
          <div class="modal-dialog modal-sm modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-body text-center">
                Loading data, please wait...
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Ignore</button>
              </div>
            </div>
          </div>
        </div>
        <Calendar v-bind="calendarValues"></Calendar>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FlopAPI } from '@/assets/js/api'
import { convertDecimalTimeToHuman } from '@/assets/js/helpers'
import { apiKey, currentWeekKey, requireInjection } from '@/assets/js/keys'
import type {
  CalendarRoomReservationSlotData,
  CalendarScheduledCourseSlotData,
  CalendarSlot,
  CourseType,
  Department,
  FlopWeek,
  TimeSettings,
  WeekDay
} from '@/assets/js/types'
import { RoomReservation, ScheduledCourse, Time } from '@/assets/js/types'
import Calendar from '@/components/calendar/Calendar.vue'
import CalendarRoomReservationSlot from '@/components/calendar/CalendarRoomReservationSlot.vue'
import CalendarScheduledCourseSlot from '@/components/calendar/CalendarScheduledCourseSlot.vue'
import CustomDatePicker from '@/components/DatePicker.vue'
import { getDepartment } from '@/main'
import { Modal } from 'bootstrap'
import { computed, onMounted, ref, shallowRef, watchEffect } from 'vue'

interface Room {
  id: number,
  name: string
}

const api = ref<FlopAPI>(requireInjection(apiKey))
const currentWeek = ref(requireInjection(currentWeekKey))
const currentDepartment = getDepartment()

// API data
const departments = ref<Array<Department>>()
const weekDays = ref<Array<WeekDay>>([])
const rooms = ref<{ [departmentId: number]: Array<Room> }>([])
const scheduledCourses = ref<{ [departmentId: number]: Array<ScheduledCourse> }>([])
const courseTypes = ref<{ [departmentId: number]: Array<CourseType> }>([])
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

const modalLoading = ref()
const mounted = ref(false)

const selectedRoom = ref<Room>()
const selectedDepartment = ref<Department>()
const selectedDepartments = computed(() => {
  let selected: Array<Department> = []

  if (!selectedDepartment.value) {
    // All departments
    if (!departments.value) {
      // No department fetched, cannot continue
      return []
    }
    selected = departments.value
  } else {
    // Department selected, get its name
    selected.push(selectedDepartment.value)
  }
  return selected
})

const dateSlots = ref<{ [index: string]: Array<CalendarSlot> }>({})

// Update rooms list on department selection
const selectedDepartmentsRooms = computed(() => {
  if (!selectedRoom) {
    return Object.values(rooms.value)
  }
  // Use a Set so that rooms accessible to multiple departments are displayed once
  let out: Set<Room> = new Set()
  selectedDepartments.value.forEach(dept => {
    if (!(dept.id in rooms.value)) {
      return
    }
    out = new Set([...out, ...rooms.value[dept.id]])
  })
  return [...out]
})

const selectedDepartmentsCourses = computed(() => {
  let courses: { [departmentId: number]: Array<ScheduledCourse> } = {}
  selectedDepartments.value.forEach(dept => {
    if (!(dept.id in scheduledCourses.value)) {
      return
    }
    courses[dept.id] = scheduledCourses.value[dept.id]
  })
  return courses
})

const selectedDepartmentsCourseTypes = computed(() => {
  let out: Array<CourseType> = []
  selectedDepartments.value.forEach(dept => {
    if (!(dept.id in courseTypes.value)) {
      return
    }
    out.push(...courseTypes.value[dept.id])
  })
  return [...out]
})

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

// Week selection watcher
watchEffect(() => {
  let date = selectedDate.value
  updateRoomReservations(date)
})

// Week selection and departments watcher
watchEffect(() => {
  let date = selectedDate.value

  if (!departments.value) {
    return
  }
  updateScheduledCourses(date, departments.value)
})

// Update the list of rooms and course types on departments fetched
watchEffect(() => {
  if (!departments.value) {
    return
  }
  rooms.value = {}
  courseTypes.value = {}

  departments.value.forEach(dept => {
    // Fetch the rooms of each selected department
    fetchRooms(dept.abbrev).then(value => {
      rooms.value[dept.id] = value
    })

    fetchCourseTypes(dept.abbrev).then(value => {
      courseTypes.value[dept.id] = value
    })
  })
})

// Display reservations of the selected room
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
    let slot = createRoomReservationSlot(reservation)
    addSlot(day, slot)
  })

  Object.keys(selectedDepartmentsCourses.value).map(Number).forEach(deptId => {
    selectedDepartmentsCourses.value[deptId].forEach(course => {
      if (params.roomId && course.room != params.roomId) {
        return
      }
      let day = weekDays.value.find(weekDay => {
        return weekDay.ref === course.day
      })
      if (!day) {
        return
      }
      let courseType = selectedDepartmentsCourseTypes.value.find(courseType => {
        return courseType.name === course.course.type
      })
      if (!courseType) {
        return
      }

      let date = day.date
      let slot = createScheduledCourseSlot(course, courseType, deptId)
      addSlot(date, slot)
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

function createRoomReservationSlot (reservation: RoomReservation): CalendarSlot {
  let startTimeRaw = reservation.start_time.split(':')
  let startTimeValue = parseInt(startTimeRaw[0]) * 60 + parseInt(startTimeRaw[1])
  let startTime = createTime(startTimeValue)
  let endTimeRaw = reservation.end_time.split(':')
  let endTimeValue = parseInt(endTimeRaw[0]) * 60 + parseInt(endTimeRaw[1])
  let endTime: Time = createTime(endTimeValue)

  let slotData: CalendarRoomReservationSlotData = {
    reservation: reservation,
    startTime: startTime,
    endTime: endTime,
    title: reservation.title,
    id: `roomreservation-${reservation.room.name}-${reservation.date}-${reservation.start_time}`,
    displayStyle: {background: '#00ff00'}
  }
  return {
    data: slotData,
    component: shallowRef(CalendarRoomReservationSlot)
  }
}

function createScheduledCourseSlot (course: ScheduledCourse, courseType: CourseType, deptId: number): CalendarSlot {
  let startTime = createTime(course.start_time)
  let endTime = createTime(course.start_time + courseType.duration)

  let departmentName = ''
  if (departments.value) {
    let department = departments.value.find(dept => dept.id === deptId)
    if (department) {
      departmentName = department.abbrev
    }
  }
  let slotData: CalendarScheduledCourseSlotData = {
    course: course,
    department: departmentName,
    startTime: startTime,
    endTime: endTime,
    title: course.course.module.abbrev,
    id: `scheduledcourse-${course.course.id}`,
    displayStyle: {background: '#ff0000'}
  }
  return {
    data: slotData,
    component: shallowRef(CalendarScheduledCourseSlot)
  }
}

function addSlot (date: string, slot: CalendarSlot) {
  if (!dateSlots.value[date]) {
    dateSlots.value[date] = []
  }

  dateSlots.value[date].push(slot)
}

function updateRoomReservations (date: FlopWeek) {
  let week = date.week
  let year = date.year

  showLoading()
  fetchRoomReservations(week, year, {}).then(value => {
    roomReservations.value = value
  })
}

function updateScheduledCourses (date: FlopWeek, departments: Array<Department>) {
  let week = date.week
  let year = date.year

  showLoading()
  scheduledCourses.value = {}
  let count = departments.length
  departments.forEach(dept => {
    fetchScheduledCourses(week, year, dept.abbrev).then(value => {
      scheduledCourses.value[dept.id] = value
      if (--count == 0) {
        hideLoading()
      }
    })
  })
}

function hideLoading (): void {
  if (!mounted.value) {
    return
  }
  const modal = Modal.getOrCreateInstance(modalLoading.value, {})
  modal.hide()
}

function showLoading (): void {
  if (!mounted.value) {
    return
  }
  const modal = Modal.getOrCreateInstance(modalLoading.value, {})
  modal.show()
}

onMounted(() => {
  fetchDepartments().then(value => {
    departments.value = value

    // Select the current department by default
    if (departments.value) {
      selectedDepartment.value = departments.value.find(dept => dept.abbrev === currentDepartment)
    }
  })

  fetchTimeSettings().then(value => {
    timeSettings.value = value
  })
  mounted.value = true
})

// Fetch functions
async function fetchDepartments () {
  return await api.value.fetch.all.departments()
}

async function fetchWeekDays (week: number, year: number) {
  return await api.value.fetch.target.weekdays(week, year)
}

async function fetchRooms (department: string) {
  return await api.value.fetch.all.rooms(department)
}

async function fetchTimeSettings () {
  return await api.value.fetch.all.timeSettings()
}

async function fetchRoomReservations (week: number, year: number, params: { roomId?: number }) {
  return await api.value.fetch.target.roomReservations(week, year, params)
}

async function fetchScheduledCourses (week: number, year: number, department: string) {
  return await api.value.fetch.target.scheduledCourses(week, year, department)
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
