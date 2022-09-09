<template>
  <h1>RoomReservation App</h1>
  <CustomDatePicker v-model:week="selectedDate.week" v-model:year="selectedDate.year"></CustomDatePicker>
  <p>Times: {{ dayStartTime.text }}-{{ lunchBreakStartTime.text }}|{{ lunchBreakFinishTime.text }}-{{
      dayFinishTime.text
    }}
  </p>

  <div class="container">
    <div class="row">
      <select v-model="selectedRoom" class="form-select" aria-label="Select room">
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
import type { Department, FlopWeek, Time, TimeSettings } from '@/assets/js/types'
import Calendar from '@/components/calendar/Calendar.vue'
import CustomDatePicker from '@/components/DatePicker.vue'
import { getDepartment } from '@/main'
import { computed, onMounted, ref, watchEffect } from 'vue'

interface Room {
  id: number,
  name: string
}

const api = ref<FlopAPI>(requireInjection(apiKey))
const currentWeek = ref(requireInjection(currentWeekKey))

// API data
const departments = ref<Array<Department>>()
const weekDays = ref([])
const rooms = ref<Array<Room>>([])

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

const dateSlots = ref<{ [index: string]: Array<{ startTime: Time, endTime: Time, title: string, content: string }> }>({})

const calendarValues = computed(() => {
  return {
    days: weekDays.value,
    slots: dateSlots.value,
    startTime: dayStartTime.value.value - 60,
    endTime: dayFinishTime.value.value + 60,
  }
})

// Update weekDays
watchEffect(() => {
  fetchWeekDays(selectedDate.value.week, selectedDate.value.year).then(value => {
    weekDays.value = value
  })
})

// Update room reservations
watchEffect(() => {
  let params: { roomId?: number } = {}
  if (selectedRoom.value) {
    params.roomId = selectedRoom.value.id
  }

  fetchRoomReservations(selectedDate.value.week, selectedDate.value.year, params).then(value => {
    dateSlots.value = {}
    value.forEach(reservation => {
      let date = reservation.date.split('-')
      let day = `${date[2]}/${date[1]}`
      let startTimeRaw = reservation.start_time.split(':')
      let startTimeValue = parseInt(startTimeRaw[0]) * 60 + parseInt(startTimeRaw[1])
      let startTime: Time = {
        value: startTimeValue,
        text: convertDecimalTimeToHuman(startTimeValue)
      }
      let endTimeRaw = reservation.end_time.split(':')
      let endTimeValue = parseInt(endTimeRaw[0]) * 60 + parseInt(endTimeRaw[1])
      let endTime: Time = {
        value: endTimeValue,
        text: convertDecimalTimeToHuman(endTimeValue)
      }
      let content = `${reservation.description}\n${reservation.responsible}`
      if (!dateSlots.value[day]) {
        dateSlots.value[day] = []
      }
      dateSlots.value[day].push({startTime: startTime, endTime: endTime, title: reservation.title, content: content})
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

  storeTime(dayStartTime.value, minStartTime)
  storeTime(dayFinishTime.value, maxFinishTime)
  storeTime(lunchBreakStartTime.value, minLunchBreakStartTime)
  storeTime(lunchBreakFinishTime.value, maxLunchBreakFinishTime)
}

function storeTime (store: Time, time: number) {
  store.text = convertDecimalTimeToHuman(time / 60)
  store.value = time
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

</script>

<script lang="ts">
export default {
  name: 'RoomReservationView',
  components: {}
}

</script>

<style scoped>

</style>
