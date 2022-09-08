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
      <Calendar v-bind="{days: weekDays}"></Calendar>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FlopAPI } from '@/assets/js/api'
import { apiKey, currentWeekKey, requireInjection } from '@/assets/js/keys'
import type { Department, FlopWeek, Time, TimeSettings } from '@/assets/js/types'
import Calendar from '@/components/calendar/Calendar.vue'
import CustomDatePicker from '@/components/DatePicker.vue'
import { getDepartment } from '@/main'
import { onMounted, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'

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
const timeSlots = ref<Array<Time>>([])

// Fill with current date, uses date picker afterwards
const selectedDate = ref<FlopWeek>({
  week: currentWeek.value.week,
  year: currentWeek.value.year,
})

const selectedRoom = ref<Room>()

const reservations = ref()

// Selected date watcher
watchEffect(() => {
  onWeekChanged(selectedDate.value)
})

// Time settings watcher
watchEffect(() => {
  onTimeSettingsChanged(timeSettings.value)
})

// Day start and lunch break start times watcher
watchEffect(() => {
  for (let time = dayStartTime.value.value; time < lunchBreakStartTime.value.value; time += 15) {
    let timeSlot: Time = {text: '', value: 0}
    storeTime(timeSlot, time)
    timeSlots.value.push(timeSlot)
  }
})

// Selected room watcher
watchEffect(() => {
  if (selectedRoom.value) {
    fetchRoomReservations(rooms.value[0].id, selectedDate.value.week, selectedDate.value.year).then(value => console.log(value))
  }
})

function onWeekChanged (newWeek: FlopWeek) {
  fetchWeekDays(newWeek.week, newWeek.year).then(value => {
    weekDays.value = value
  })
}

function convertDecimalTimeToHuman (time: number): string {
  let hours = Math.trunc(time)
  let minutes = Math.trunc((time - hours) * 60)
  return `${hours}h${minutes > 0 ? minutes : '00'}`
}

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

async function fetchRoomReservations (idRoom: number, week: number, year: number) {
  return await api.value.fetch.target.roomReservations(idRoom, {week: week, year: year})
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
