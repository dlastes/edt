<template>
  <div class="loader" :style="{ visibility: loaderVisibility }"></div>
  <div class="container-fluid">
    <div class="row">
      <!-- Week picker and filters -->
      <div class="col-auto">
        <WeekPicker
            v-model:week="selectedDate.week"
            v-model:year="selectedDate.year"
        ></WeekPicker>
        <!-- Filters -->
        <div class="col-auto">
          <!-- Room filter -->
          <div class="mb-3">
            <label for="select-room" class="form-label">Room:</label>
            <select
                id="select-room"
                v-model="selectedRoom"
                class="form-select w-auto"
                aria-label="Select room"
            >
              <option :value="undefined">All rooms</option>
              <option
                  v-for="room in Object.values(selectedDepartmentsRooms).filter(r=> r.is_basic)"
                  :key="room"
                  :value="room"
              >
                {{ room.name }}
              </option>
            </select>
          </div>
          <!-- Department filter -->
          <div class="mb-3">
            <label for="select-department" class="form-label"
            >Department:</label
            >
            <select
                id="select-department"
                v-model="selectedDepartment"
                class="form-select w-auto ms-1"
                aria-label="Select department"
            >
              <option :value="undefined">All departments</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept">
                {{ dept.abbrev }}
              </option>
            </select>
          </div>
        </div>
      </div>
      <!-- Calendar -->
      <div class="col">
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
  RoomReservation,
  RoomReservationType,
  TimeSettings,
  User,
  WeekDay,
} from '@/assets/js/types'
import { Room, ScheduledCourse, Time } from '@/assets/js/types'
import Calendar from '@/components/calendar/Calendar.vue'
import CalendarRoomReservationSlot from '@/components/calendar/CalendarRoomReservationSlot.vue'
import CalendarScheduledCourseSlot from '@/components/calendar/CalendarScheduledCourseSlot.vue'
import WeekPicker from '@/components/WeekPicker.vue'
import { getDepartment } from '@/main'
import { computed, onMounted, ref, shallowRef, watchEffect, } from 'vue'

const api = ref<FlopAPI>(requireInjection(apiKey))
const currentWeek = ref(requireInjection(currentWeekKey))
const currentDepartment = getDepartment()
let loadingCounter = 0

// API data
const departments = ref<Array<Department>>([])
const weekDays = ref<Array<WeekDay>>([])
const rooms = ref<{ [departmentId: number]: Array<Room> }>({})
const scheduledCourses = ref<{ [departmentId: number]: Array<ScheduledCourse> }>({})
const courseTypes = ref<{ [departmentId: number]: Array<CourseType> }>({})
const roomReservations = ref<Array<RoomReservation>>([])
const roomReservationTypes = ref<{ [id: number]: RoomReservationType }>({})
const allUsers = ref<{ [userId: number]: User }>({})

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

const loaderVisibility = ref('hidden')

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
  let departmentsList: Department[]
  if (!selectedDepartments.value) {
    departmentsList = departments.value
  } else {
    departmentsList = selectedDepartments.value
  }

  let objectList: { [roomId: number]: Room } = {}
  departmentsList.forEach((dept) => {
    if (!(dept.id in rooms.value)) {
      return
    }
    rooms.value[dept.id].forEach(room => {
      if (!(room.id in objectList)) {
        objectList[room.id] = room
      }
    })
  })
  return objectList
})

const allRooms = computed(() => {
  let departmentsList: Department[] = departments.value

  let objectList: { [roomId: number]: Room } = {}
  departmentsList.forEach((dept) => {
    if (!(dept.id in rooms.value)) {
      return
    }
    rooms.value[dept.id].forEach(room => {
      if (!(room.id in objectList)) {
        objectList[room.id] = room
      }
    })
  })
  return objectList
})

const selectedDepartmentsCourses = computed(() => {
  const courses: { [departmentId: number]: Array<ScheduledCourse> } = {}
  selectedDepartments.value.forEach((dept) => {
    if (!(dept.id in scheduledCourses.value)) {
      return
    }
    courses[dept.id] = scheduledCourses.value[dept.id]
  })
  return courses
})

const selectedDepartmentsCourseTypes = computed(() => {
  const out: Array<CourseType> = []
  selectedDepartments.value.forEach((dept) => {
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
    startTime:
        dayStartTime.value.value - (60 + (dayStartTime.value.value % 60)),
    endTime:
        dayFinishTime.value.value + (60 - (dayFinishTime.value.value % 60)),
  }
})

// Update weekDays
watchEffect(() => {
  console.log('Updating Week days')
  fetchWeekDays(selectedDate.value.week, selectedDate.value.year).then(
      (value) => {
        weekDays.value = value
      }
  )
})

// Week selection watcher
watchEffect(() => {
  console.log('Updating Rooms reservations')
  const date = selectedDate.value
  updateRoomReservations(date)
})

// Week selection and departments watcher
watchEffect(() => {
  console.log('Updating Scheduled courses')
  const date = selectedDate.value

  if (!departments.value) {
    return
  }
  updateScheduledCourses(date, departments.value)
})

// Display reservations of the selected room
watchEffect(() => {
  console.log('Filtering Room reservations')
  let roomId: number | undefined
  if (selectedRoom.value) {
    roomId = selectedRoom.value.id
  }

  dateSlots.value = {}
  roomReservations.value.forEach((reservation) => {
    // Get reservations which room is listed or is a part of a room listed in the selected departments
    if (roomId) {
      // A room is selected
      // Get its values
      if (!(reservation.room in selectedDepartmentsRooms.value)) {
        // The room is not listed in the selected departments
        return
      }
      const room = selectedDepartmentsRooms.value[reservation.room]
      if (!(room.basic_rooms.find(r => r.id === roomId))) {
        // The room is not the one selected or a part of the selected room
        return
      }
    }
    const date = reservation.date.split('-')
    const day = `${date[2]}/${date[1]}`
    const slot = createRoomReservationSlot(reservation)
    addSlot(day, slot)
  })

  Object.keys(selectedDepartmentsCourses.value).forEach((deptId) => {
    const id = parseInt(deptId)
    selectedDepartmentsCourses.value[id].forEach((course) => {
      // Get courses which room is listed or is a part of a room listed in the selected departments
      if (roomId) {
        // A room is selected
        // Get its values
        if (!(course.room in selectedDepartmentsRooms.value)) {
          // The room is not listed in the selected departments
          return
        }
        const room = selectedDepartmentsRooms.value[course.room]
        if (!(room.basic_rooms.find(r => r.id === roomId))) {
          // The room is not the one selected or a part of the selected room
          return
        }
      }
      const day = weekDays.value.find((weekDay) => {
        return weekDay.ref === course.day
      })
      if (!day) {
        return
      }
      const courseType = selectedDepartmentsCourseTypes.value.find(
          (courseType) => {
            return courseType.name === course.course.type
          }
      )
      if (!courseType) {
        return
      }
      const date = day.date
      const slot = createScheduledCourseSlot(course, courseType, id)
      addSlot(date, slot)
    })
  })
})

// Time settings watcher
watchEffect(() => {
  console.log('Updating time settings')
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
  timeSettings.forEach((setting) => {
    minStartTime = Math.min(minStartTime, setting.day_start_time)
    maxFinishTime = Math.max(maxFinishTime, setting.day_finish_time)
    minLunchBreakStartTime = Math.min(
        minLunchBreakStartTime,
        setting.lunch_break_start_time
    )
    maxLunchBreakFinishTime = Math.max(
        maxLunchBreakFinishTime,
        setting.lunch_break_finish_time
    )
  })

  dayStartTime.value = createTime(minStartTime)
  dayFinishTime.value = createTime(maxFinishTime)
  lunchBreakStartTime.value = createTime(minLunchBreakStartTime)
  lunchBreakFinishTime.value = createTime(maxLunchBreakFinishTime)
}

function createTime (time: number): Time {
  const text = convertDecimalTimeToHuman(time / 60)
  return new Time(time, text)
}

function createRoomReservationSlot (reservation: RoomReservation): CalendarSlot {
  const startTimeRaw = reservation.start_time.split(':')
  const startTimeValue =
      parseInt(startTimeRaw[0]) * 60 + parseInt(startTimeRaw[1])
  const startTime = createTime(startTimeValue)
  const endTimeRaw = reservation.end_time.split(':')
  const endTimeValue = parseInt(endTimeRaw[0]) * 60 + parseInt(endTimeRaw[1])
  const endTime: Time = createTime(endTimeValue)

  let backgroundColor = '#ffffff'
  if (reservation.reservation_type in roomReservationTypes.value) {
    const type = roomReservationTypes.value[reservation.reservation_type]
    backgroundColor = type.bg_color
  }

  const slotData: CalendarRoomReservationSlotData = {
    reservation: reservation,
    rooms: allRooms.value,
    users: allUsers.value,
    reservationTypes: Object.values(roomReservationTypes.value),
    startTime: startTime,
    endTime: endTime,
    title: reservation.title,
    id: `roomreservation-${reservation.room}-${reservation.date}-${reservation.start_time}`,
    displayStyle: {background: backgroundColor},
    onFormSave: updateRoomReservation,
  }
  return {
    data: slotData,
    component: shallowRef(CalendarRoomReservationSlot),
  }
}

function createScheduledCourseSlot (
    course: ScheduledCourse,
    courseType: CourseType,
    deptId: number
): CalendarSlot {
  const startTime = createTime(course.start_time)
  const endTime = createTime(course.start_time + courseType.duration)

  let departmentName = ''
  if (departments.value) {
    const department = departments.value.find((dept) => dept.id === deptId)
    if (department) {
      departmentName = department.abbrev
    }
  }
  const type = Object.values(roomReservationTypes.value).find(
      (type) => type.name === 'Course'
  )
  let backgroundColor = '#000000'
  if (type) {
    backgroundColor = type.bg_color
  }
  const slotData: CalendarScheduledCourseSlotData = {
    course: course,
    department: departmentName,
    rooms: selectedDepartmentsRooms.value,
    startTime: startTime,
    endTime: endTime,
    title: course.course.module.abbrev,
    id: `scheduledcourse-${course.course.id}`,
    displayStyle: {background: backgroundColor},
  }
  return {
    data: slotData,
    component: shallowRef(CalendarScheduledCourseSlot),
  }
}

function addSlot (date: string, slot: CalendarSlot) {
  if (!dateSlots.value[date]) {
    dateSlots.value[date] = []
  }

  dateSlots.value[date].push(slot)
}

function updateRoomReservations (date: FlopWeek) {
  const week = date.week
  const year = date.year

  showLoading()
  fetchRoomReservations(week, year, {}).then((value) => {
    roomReservations.value = value
    hideLoading()
  })
}

function updateScheduledCourses (
    date: FlopWeek,
    departments: Array<Department>
) {
  const week = date.week
  const year = date.year

  showLoading()
  scheduledCourses.value = {}
  let count = departments.length

  if (count === 0) {
    hideLoading()
    return
  }

  let coursesList: { [p: number]: ScheduledCourse[] } = {}
  departments.forEach((dept) => {
    fetchScheduledCourses(week, year, dept.abbrev).then((value) => {
      coursesList[dept.id] = value
      if (--count === 0) {
        scheduledCourses.value = coursesList
        hideLoading()
      }
    })
  })
}

function updateRoomReservation (reservation: RoomReservation) {
  let index = roomReservations.value.findIndex(reserv => reserv.id === reservation.id)
  if (index === -1) {
    console.error(`Could not find reservation with id: ${reservation.id}`)
    return
  }
  roomReservations.value[index] = reservation
}

function hideLoading (): void {
  if (--loadingCounter <= 0) {
    loaderVisibility.value = 'hidden'
  }
}

function showLoading (): void {
  ++loadingCounter
  loaderVisibility.value = 'visible'
}

onMounted(() => {
  fetchDepartments().then((value) => {
    departments.value = value

    // Select the current department by default
    if (departments.value) {
      selectedDepartment.value = departments.value.find(
          (dept) => dept.abbrev === currentDepartment
      )

      rooms.value = {}
      courseTypes.value = {}
      let roomsList: { [key: string]: Array<Room> } = {}
      let typesList: { [key: string]: Array<CourseType> } = {}
      let departmentsCount = departments.value.length
      let roomsCounter = departmentsCount
      let typesCounter = departmentsCount
      departments.value.forEach((dept) => {
        // Fetch the rooms of each selected department
        fetchRooms(dept.abbrev).then((value) => {
          roomsList[dept.id] = value
          if (--roomsCounter === 0) {
            // Update the rooms list ref only once every department is handled
            rooms.value = roomsList
          }
        })

        fetchCourseTypes(dept.abbrev).then((value) => {
          typesList[dept.id] = value
          if (--typesCounter === 0) {
            // Update the course types list ref only once every department is handled
            courseTypes.value = typesList
          }
        })
      })
    }
  })

  fetchTimeSettings().then((value) => {
    timeSettings.value = value
  })

  fetchRoomReservationTypes().then((value) => {
    value.forEach((reservationType) => {
      roomReservationTypes.value[reservationType.id] = reservationType
    })
  })

  fetchUsers().then((value) => {
    value.forEach(user => {
      allUsers.value[user.id] = user
    })
  })
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

async function fetchRoomReservations (
    week: number,
    year: number,
    params: { roomId?: number }
) {
  return await api.value.fetch.target.roomReservations(week, year, params)
}

async function fetchRoomReservationTypes () {
  return await api.value.fetch.all.roomReservationTypes()
}

async function fetchScheduledCourses (
    week: number,
    year: number,
    department: string
) {
  return await api.value.fetch.target.scheduledCourses(week, year, department)
}

async function fetchCourseTypes (department: string) {
  return await api.value.fetch.all.courseTypes(department)
}

async function fetchUsers () {
  return await api.value.fetch.all.users()
}
</script>

<script lang="ts">
export default {
  name: 'RoomReservationView',
  components: {},
}
</script>

<style scoped>
.loader {
  position: fixed;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.6) url("@/assets/images/logo-head-gribou-rc-hand.svg") no-repeat 50% 50%;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  cursor: wait;
}
</style>
