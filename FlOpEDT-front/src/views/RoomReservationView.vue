<template>
  <h1>RoomReservation App</h1>
  <CustomDatePicker v-model:week="selectedDate.week" v-model:year="selectedDate.year"></CustomDatePicker>
  <h2>Selected week: {{ selectedDate.week }}/ {{ selectedDate.year }}</h2>
  <p>Departments: {{ departments }}</p>
  <p>WeekDays: {{ weekDays }}</p>
  <p>Times: {{ dayStartTime }}-{{ lunchBreakStartTime }}|{{ lunchBreakFinishTime }}-{{ dayFinishTime }}</p>
  <p>Rooms: {{ rooms }}</p>
  <div v-if="rooms" class="container w-auto">
    <div v-for="room in rooms" class="row">
      <button type="button" class="btn btn-primary" @click="onRoomChanged(room)">
        {{ room.name }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { apiKey, currentWeekKey, requireInjection } from '@/assets/js/keys'
import type { FlopWeek, TimeSettings } from '@/assets/js/types'
import CustomDatePicker from '@/components/DatePicker.vue'
import { onMounted, ref, watchEffect } from 'vue'

const api = ref(requireInjection(apiKey))
const currentWeek = ref(requireInjection(currentWeekKey))

// API data
const departments = ref<Array<{ id: number, abbrev: string }>>()
const weekDays = ref([])
const rooms = ref([])

// Time Settings
const timeSettings = ref<Array<TimeSettings>>()
const dayStartTime = ref()
const dayFinishTime = ref()
const lunchBreakStartTime = ref()
const lunchBreakFinishTime = ref()

// Fill with current date, uses date picker afterwards
const selectedDate = ref<FlopWeek>({
  week: currentWeek.value.week,
  year: currentWeek.value.year,
})

watchEffect(() => {
  onWeekChanged(selectedDate.value)
})

watchEffect(() => {
  onTimeSettingsChanged(timeSettings.value)
})

function onWeekChanged (newWeek: FlopWeek) {
  console.log(`Selected week: ${newWeek.week}/${newWeek.year}`)
  fetchWeekDays(newWeek.week, newWeek.year).then(value => {
    weekDays.value = value
  })
}

function onRoomChanged (room: { id: number, name: string }) {
  console.log(`Selected room: ${room.name}`)
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
  dayStartTime.value = convertDecimalTimeToHuman(minStartTime / 60)
  dayFinishTime.value = convertDecimalTimeToHuman(maxFinishTime / 60)
  lunchBreakStartTime.value = convertDecimalTimeToHuman(minLunchBreakStartTime / 60)
  lunchBreakFinishTime.value = convertDecimalTimeToHuman(maxLunchBreakFinishTime / 60)
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
  return await api.value.fetch.all.rooms()
}

async function fetchTimeSettings () {
  return await api.value.fetch.all.timesettings()
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
