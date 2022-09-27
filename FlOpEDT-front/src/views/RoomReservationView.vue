<template>
    <div>
        <div class="loader" v-if="loaderIsVisible"></div>
        <div class="container-fluid">
            <div class="row">
                <!-- Week picker and filters -->
                <div class="col-auto">
                    <WeekPicker v-model:week="selectedDate.week" v-model:year="selectedDate.year"></WeekPicker>
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
                                    v-for="room in Object.values(rooms.perIdOfSelectedDepartments.value)
                                        .filter((r) => r.is_basic)
                                        .sort((r1, r2) => {
                                            return r1.name.toLowerCase().localeCompare(r2.name.toLowerCase())
                                        })"
                                    :key="room.id"
                                    :value="room"
                                >
                                    {{ room.name }}
                                </option>
                            </select>
                        </div>
                        <!-- Department filter -->
                        <div class="mb-3">
                            <label for="select-department" class="form-label">Department:</label>
                            <select
                                id="select-department"
                                v-model="selectedDepartment"
                                class="form-select w-auto ms-1"
                                aria-label="Select department"
                            >
                                <option :value="undefined">All departments</option>
                                <option v-for="dept in departments.list.value" :key="dept.id" :value="dept">
                                    {{ dept.abbrev }}
                                </option>
                            </select>
                        </div>
                    </div>
                </div>
                <!-- Calendar -->
                <div class="col">
                    <HourCalendar @drag="handleDrag" :values="calendarValues"></HourCalendar>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { FlopAPI } from '@/assets/js/api'
import { convertDecimalTimeToHuman, listGroupBy, parseReason, toStringAtLeastTwoDigits } from '@/assets/js/helpers'
import { apiKey, apiToken, currentWeekKey, requireInjection } from '@/assets/js/keys'
import type {
    CalendarDragEvent,
    CalendarRoomReservationSlotData,
    CalendarScheduledCourseSlotData,
    CalendarSlot,
    CourseType,
    Department,
    FlopWeek,
    Room,
    RoomReservation,
    RoomReservationType,
    TimeSettings,
    User,
    WeekDay,
} from '@/assets/js/types'
import { ScheduledCourse, Time } from '@/assets/js/types'
import HourCalendar from '@/components/calendar/HourCalendar.vue'
import CalendarScheduledCourseSlot from '@/components/calendar/CalendarScheduledCourseSlot.vue'
import WeekPicker from '@/components/WeekPicker.vue'
import { getDepartment } from '@/main'
import type { ComputedRef, Ref } from 'vue'
import { computed, onMounted, ref, shallowRef, watchEffect } from 'vue'
import CalendarRoomReservationSlot from '@/components/calendar/CalendarRoomReservationSlot.vue'

const api = ref<FlopAPI>(requireInjection(apiKey))
const authToken = requireInjection(apiToken)
const currentWeek = ref(requireInjection(currentWeekKey))
const currentDepartment = getDepartment()
let loadingCounter = 0

interface Rooms {
    list: ComputedRef<Array<Room>>
    perDepartment: Ref<{ [departmentId: string]: Array<Room> }>
    perSelectedDepartments: ComputedRef<{ [departmentId: string]: Array<Room> }>
    listPerSelectedDepartments: ComputedRef<Array<Room>>
    perIdOfSelectedDepartments: ComputedRef<{ [roomId: string]: Room }>
    perId: ComputedRef<{ [roomId: string]: Room }>
}

interface ScheduledCourses {
    list: ComputedRef<Array<ScheduledCourse>>
    perDepartment: Ref<{ [departmentId: string]: Array<ScheduledCourse> }>
    perDay: ComputedRef<{ [day: string]: Array<ScheduledCourse> }>
    perSelectedDepartments: ComputedRef<{ [departmentId: string]: Array<ScheduledCourse> }>
}

interface CourseTypes {
    perDepartment: Ref<{ [departmentId: string]: Array<CourseType> }>
    listPerSelectedDepartments: ComputedRef<Array<CourseType>>
}

interface RoomReservations {
    list: Ref<Array<RoomReservation>>
    perDay: ComputedRef<{ [day: string]: Array<RoomReservation> }>
}

interface RoomReservationTypes {
    list: Ref<Array<RoomReservationType>>
    perId: ComputedRef<{ [typeId: string]: RoomReservationType }>
}

interface Users {
    list: Ref<Array<User>>
    perId: ComputedRef<{ [userId: string]: User }>
}

// API data
const departments = {
    list: ref<Array<Department>>([]),
}

const weekDays = {
    list: ref<Array<WeekDay>>([]),
}

const rooms: Rooms = {
    list: computed(() => {
        const out: Array<Room> = []
        Object.values(rooms.perDepartment.value).forEach((rooms) => {
            out.push(...rooms.filter((room) => !out.includes(room)))
        })
        return out
    }),
    perDepartment: ref({}),
    perSelectedDepartments: computed(() => {
        return filterBySelectedDepartments(rooms.perDepartment.value)
    }),
    listPerSelectedDepartments: computed(() => {
        const out: Array<Room> = []
        Object.values(rooms.perSelectedDepartments.value).forEach((rooms) => {
            out.push(...rooms.filter((room) => !out.includes(room)))
        })
        return out
    }),
    perIdOfSelectedDepartments: computed(() => {
        return Object.fromEntries(rooms.listPerSelectedDepartments.value.map((r) => [r.id, r]))
    }),
    perId: computed(() => {
        return Object.fromEntries(rooms.list.value.map((r) => [r.id, r]))
    }),
}

const scheduledCourses: ScheduledCourses = {
    list: computed(() => {
        return Object.values(scheduledCourses.perDepartment.value).flat(1)
    }),
    perDepartment: ref({}),
    perDay: computed(() => {
        return listGroupBy(scheduledCourses.list.value, (course) => course.day)
    }),
    perSelectedDepartments: computed(() => {
        return filterBySelectedDepartments(scheduledCourses.perDepartment.value)
    }),
}

const courseTypes: CourseTypes = {
    perDepartment: ref({}),
    listPerSelectedDepartments: computed(() => {
        return Object.values(filterBySelectedDepartments(courseTypes.perDepartment.value)).flat(1)
    }),
}

const roomReservations: RoomReservations = {
    list: ref([]),
    perDay: computed(() => {
        return listGroupBy(roomReservations.list.value, (reserv) => {
            const date = new Date(reserv.date)
            return createSlotId(date.getDate(), date.getMonth() + 1)
        })
    }),
}

const roomReservationTypes: RoomReservationTypes = {
    list: ref([]),
    perId: computed(() => {
        return Object.fromEntries(roomReservationTypes.list.value.map((t) => [t.id, t]))
    }),
}

const users: Users = {
    list: ref([]),
    perId: computed(() => {
        return Object.fromEntries(users.list.value.map((user) => [user.id, user]))
    }),
}

// Time Settings
const timeSettings = ref<Array<TimeSettings>>()
const dayStartTime = ref<Time>({ value: 0, text: '' })
const dayFinishTime = ref<Time>({ value: 0, text: '' })
const lunchBreakStartTime = ref<Time>({ value: 0, text: '' })
const lunchBreakFinishTime = ref<Time>({ value: 0, text: '' })

// Fill with current date, uses date picker afterwards
const selectedDate = ref<FlopWeek>({
    week: currentWeek.value.week,
    year: currentWeek.value.year,
})

const loaderIsVisible = ref(false)

const selectedRoom = ref<Room>()
const selectedDepartment = ref<Department>()
const selectedDepartments = computed(() => {
    let selected: Array<Department> = []

    if (!selectedDepartment.value) {
        // All departments
        if (!departments.list.value) {
            // No department fetched, cannot continue
            return []
        }
        selected = departments.list.value
    } else {
        // Department selected, get its name
        selected.push(selectedDepartment.value)
    }
    return selected
})

/**
 * Computes the slots to display all the room reservations, grouped by day.
 */
const roomReservationSlots = computed<{ [day: string]: Array<CalendarSlot> }>(() => {
    const out: { [day: string]: Array<CalendarSlot> } = {}
    Object.keys(roomReservations.perDay.value).forEach((day) => {
        roomReservations.perDay.value[day].forEach((reservation: RoomReservation) => {
            const roomId = selectedRoom?.value?.id
            // Get reservations which room is listed or is a part of a room listed in the selected departments
            if (roomId) {
                // A room is selected
                // Get its values
                const room = rooms.listPerSelectedDepartments.value.find((r) => r.id === reservation.room)
                if (!room) {
                    // The room is not listed in the selected departments
                    return
                }
                if (!room.basic_rooms.find((r) => r.id === roomId)) {
                    // The room is not the one selected or a part of the selected room
                    return
                }
            }
            const slot = createRoomReservationSlot(reservation)
            addSlotTo(day, slot, out)
        })
    })
    return out
})

/**
 * Computes the slots to display all the scheduled courses, grouped by day.
 */
const scheduledCoursesSlots = computed<{ [date: string]: Array<CalendarSlot> }>(() => {
    const out: { [date: string]: Array<CalendarSlot> } = {}
    Object.entries(scheduledCourses.perSelectedDepartments.value).forEach((entry) => {
        const deptId = entry[0]
        entry[1].forEach((course) => {
            const roomId = selectedRoom?.value?.id

            // Get courses which room is listed or is a part of a room listed in the selected departments
            if (roomId) {
                // A room is selected
                // Get its values
                const room = rooms.listPerSelectedDepartments.value.find((r) => r.id === course.room)
                if (!room) {
                    // The room is not listed in the selected departments
                    return
                }
                if (!room.basic_rooms.find((r) => r.id === roomId)) {
                    // The room is not the one selected or a part of the selected room
                    return
                }
            }
            const day = weekDays.list.value.find((weekDay) => {
                return weekDay.ref === course.day
            })
            if (!day) {
                return
            }
            const courseType = courseTypes.listPerSelectedDepartments.value.find((courseType) => {
                return courseType.name === course.course.type
            })
            if (!courseType) {
                return
            }
            const date = day.date
            const slot = createScheduledCourseSlot(course, courseType, deptId)
            addSlotTo(date, slot, out)
        })
    })
    return out
})

const temporaryReservation = ref<RoomReservation>()
const temporaryCalendarSlots = computed<{ [date: string]: Array<CalendarSlot> }>(() => {
    const out: { [index: string]: Array<CalendarSlot> } = {}
    if (temporaryReservation.value) {
        const reservation = temporaryReservation.value
        const slot = createRoomReservationSlot(reservation)
        const date = new Date(reservation.date)
        const id = createSlotId(date.getDate(), date.getMonth() + 1)
        addSlotTo(id, slot, out)
    }
    return out
})

const calendarSlots = computed(() => {
    const out: { [index: string]: Array<CalendarSlot> } = {}

    for (const obj of [roomReservationSlots.value, scheduledCoursesSlots.value, temporaryCalendarSlots.value]) {
        Object.keys(obj).forEach((key) => {
            obj[key].forEach((slot) => {
                addSlotTo(key, slot, out)
            })
        })
    }
    return out
})

const calendarValues = computed(() => {
    return {
        days: weekDays.list.value,
        year: `${selectedDate.value.year}`,
        slots: calendarSlots.value,
        startTime: dayStartTime.value.value - (60 + (dayStartTime.value.value % 60)),
        endTime: dayFinishTime.value.value + (60 - (dayFinishTime.value.value % 60)),
    }
})

// Update weekDays
watchEffect(() => {
    console.log('Updating Week days')
    fetchWeekDays(selectedDate.value.week, selectedDate.value.year).then((value) => {
        weekDays.list.value = value
    })
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

    if (!departments.list.value) {
        return
    }
    updateScheduledCourses(date, departments.list.value)
})

// Time settings watcher
watchEffect(() => {
    console.log('Updating time settings')
    onTimeSettingsChanged(timeSettings.value)
})

/**
 * Takes an object having departments id as key and an array.
 * Returns the filtered entries of selected departments.
 * @param object
 */
function filterBySelectedDepartments<T>(object: { [key: string]: Array<T> }) {
    const out: { [departmentId: string]: Array<T> } = Object.fromEntries(
        Object.entries(object).filter(
            ([key]) => selectedDepartments.value.findIndex((dept) => `${dept.id}` === key) >= 0
        )
    )
    return out
}

function onTimeSettingsChanged(timeSettings?: Array<TimeSettings>) {
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
        minLunchBreakStartTime = Math.min(minLunchBreakStartTime, setting.lunch_break_start_time)
        maxLunchBreakFinishTime = Math.max(maxLunchBreakFinishTime, setting.lunch_break_finish_time)
    })

    dayStartTime.value = createTime(minStartTime)
    dayFinishTime.value = createTime(maxFinishTime)
    lunchBreakStartTime.value = createTime(minLunchBreakStartTime)
    lunchBreakFinishTime.value = createTime(maxLunchBreakFinishTime)
}

function createTime(time: number): Time {
    const text = convertDecimalTimeToHuman(time / 60)
    return new Time(time, text)
}

function createRoomReservationSlot(reservation: RoomReservation): CalendarSlot {
    const startTimeRaw = reservation.start_time.split(':')
    const startTimeValue = parseInt(startTimeRaw[0]) * 60 + parseInt(startTimeRaw[1])
    const startTime = createTime(startTimeValue)
    const endTimeRaw = reservation.end_time.split(':')
    const endTimeValue = parseInt(endTimeRaw[0]) * 60 + parseInt(endTimeRaw[1])
    const endTime: Time = createTime(endTimeValue)

    let backgroundColor = '#ffffff'
    if (reservation.reservation_type in roomReservationTypes.perId.value) {
        const type = roomReservationTypes.perId.value[reservation.reservation_type]
        backgroundColor = type.bg_color
    }

    const slotData: CalendarRoomReservationSlotData = {
        reservation: reservation,
        rooms: rooms.perId.value,
        users: users.perId.value,
        reservationTypes: Object.values(roomReservationTypes.list.value),
        startTime: startTime,
        endTime: endTime,
        title: reservation.title,
        id: `roomreservation-${reservation.id}`,
        displayStyle: { background: backgroundColor },
    }
    return {
        data: slotData,
        component: shallowRef(CalendarRoomReservationSlot),
        actions: {
            delete: deleteRoomReservationSlot,
            save: updateRoomReservation,
        },
    }
}

function createScheduledCourseSlot(course: ScheduledCourse, courseType: CourseType, deptId: string): CalendarSlot {
    const startTime = createTime(course.start_time)
    const endTime = createTime(course.start_time + courseType.duration)

    let departmentName = ''
    if (departments.list.value) {
        const department = departments.list.value.find((dept) => `${dept.id}` === deptId)
        if (department) {
            departmentName = department.abbrev
        }
    }
    const type = Object.values(roomReservationTypes.list.value).find((type) => type.name === 'Course')
    let backgroundColor = '#ffffff'
    if (type) {
        backgroundColor = type.bg_color
    }
    const slotData: CalendarScheduledCourseSlotData = {
        course: course,
        department: departmentName,
        rooms: rooms.perIdOfSelectedDepartments.value,
        startTime: startTime,
        endTime: endTime,
        title: course.course.module.abbrev,
        id: `scheduledcourse-${course.course.id}`,
        displayStyle: { background: backgroundColor },
    }
    return {
        data: slotData,
        component: shallowRef(CalendarScheduledCourseSlot),
        actions: {
            // No course save
            save: undefined,
            // No course deletion
            delete: undefined,
        },
    }
}

function addSlotTo(date: string, slot: CalendarSlot, collection: { [p: string]: Array<CalendarSlot> }) {
    if (!collection[date]) {
        collection[date] = []
    }
    collection[date].push(slot)
}

function updateRoomReservations(date: FlopWeek) {
    const week = date.week
    const year = date.year

    showLoading()
    fetchRoomReservations(week, year, {}).then((value) => {
        roomReservations.list.value = value
        hideLoading()
    })
    temporaryReservation.value = undefined
}

function updateScheduledCourses(date: FlopWeek, departments: Array<Department>) {
    const week = date.week
    const year = date.year

    showLoading()
    scheduledCourses.perDepartment.value = {}
    let count = departments.length

    if (count === 0) {
        hideLoading()
        return
    }

    const coursesList: { [p: string]: ScheduledCourse[] } = {}
    departments.forEach((dept) => {
        fetchScheduledCourses(week, year, dept.abbrev).then((value) => {
            coursesList[dept.id] = value
            if (--count === 0) {
                scheduledCourses.perDepartment.value = coursesList
                hideLoading()
            }
        })
    })
}

function updateRoomReservation(newData: CalendarRoomReservationSlotData, oldData: CalendarRoomReservationSlotData) {
    const newReservation = newData.reservation
    const oldReservation = oldData.reservation

    if (oldReservation.id < 0) {
        // The reservation is a new one, just add it to the list
        roomReservations.list.value.push(newData.reservation)
        // Clear the temporary slot
        temporaryReservation.value = undefined
        return
    }

    // Find the reservation index from the list of reservations
    const index = roomReservations.list.value.findIndex((reserv) => reserv.id === oldReservation.id)

    if (index < 0) {
        // Reservation not found
        console.error(`Could not find reservation with id: ${oldReservation.id}`)
        return
    }
    // Replace the reservation at index
    roomReservations.list.value[index] = newReservation
}

function handleReason(level: string, message: string) {
    console.error(`${level}: ${message}`)
}

function deleteRoomReservationSlot(toDelete: CalendarRoomReservationSlotData) {
    const reservation = toDelete.reservation

    if (reservation.id < 0) {
        temporaryReservation.value = undefined
        return
    }

    // Target reservation is in the database, so we need to remove it first
    api.value.delete
        .roomReservation(reservation.id, authToken)
        .then(
            (_) => {
                // Filter the list of reservations
                roomReservations.list.value = roomReservations.list.value.filter((r) => r.id != reservation.id)
            },
            (reason) => parseReason(reason, handleReason)
        )
        .catch((reason) => parseReason(reason, handleReason))
}

function hideLoading(): void {
    if (--loadingCounter <= 0) {
        loaderIsVisible.value = false
    }
}

function showLoading(): void {
    ++loadingCounter
    loaderIsVisible.value = true
}

let newReservationId = -1

function handleDrag(drag: CalendarDragEvent) {
    if (drag.startDate.getDate() != drag.endDate.getDate()) {
        console.error('Reserving a room for more than a day is not accepted.')
        return
    }
    const day = toStringAtLeastTwoDigits(drag.startDate.getDate())
    const month = toStringAtLeastTwoDigits(drag.startDate.getMonth() + 1)
    const year = drag.startDate.getFullYear()
    const date = `${year}-${month}-${day}`
    const reservation: RoomReservation = {
        date: date,
        description: '',
        email: true,
        end_time: drag.endTime.text,
        id: newReservationId--,
        periodicity: -1,
        reservation_type: -1,
        responsible: 553,
        room: selectedRoom.value?.id ?? -1,
        start_time: drag.startTime.text,
        title: '',
    }
    temporaryReservation.value = reservation
}

function createSlotId(day: string | number, month: string | number): string {
    return `${toStringAtLeastTwoDigits(day)}/${toStringAtLeastTwoDigits(month)}`
}

onMounted(() => {
    fetchDepartments().then((value) => {
        departments.list.value = value

        // Select the current department by default
        if (departments.list.value) {
            selectedDepartment.value = departments.list.value.find((dept) => dept.abbrev === currentDepartment)

            rooms.perDepartment.value = {}
            courseTypes.perDepartment.value = {}
            const roomsList: { [key: string]: Array<Room> } = {}
            const typesList: { [key: string]: Array<CourseType> } = {}
            const departmentsCount = departments.list.value.length
            let roomsCounter = departmentsCount
            let typesCounter = departmentsCount
            departments.list.value.forEach((dept) => {
                // Fetch the rooms of each selected department
                fetchRooms(dept.abbrev).then((value) => {
                    roomsList[dept.id] = value
                    if (--roomsCounter === 0) {
                        // Update the rooms list ref only once every department is handled
                        rooms.perDepartment.value = roomsList
                    }
                })

                fetchCourseTypes(dept.abbrev).then((value) => {
                    typesList[dept.id] = value
                    if (--typesCounter === 0) {
                        // Update the course types list ref only once every department is handled
                        courseTypes.perDepartment.value = typesList
                    }
                })
            })
        }
    })

    fetchTimeSettings().then((value) => {
        timeSettings.value = value
    })

    fetchRoomReservationTypes().then((value) => {
        roomReservationTypes.list.value = value
    })

    fetchUsers().then((value) => {
        users.list.value = value
    })
})

// Fetch functions
async function fetchDepartments() {
    return await api.value.fetch.all.departments()
}

async function fetchWeekDays(week: number, year: number) {
    return await api.value.fetch.target.weekdays(week, year)
}

async function fetchRooms(department: string) {
    return await api.value.fetch.all.rooms(department)
}

async function fetchTimeSettings() {
    return await api.value.fetch.all.timeSettings()
}

async function fetchRoomReservations(week: number, year: number, params: { roomId?: number }) {
    return await api.value.fetch.target.roomReservations(week, year, params)
}

async function fetchRoomReservationTypes() {
    return await api.value.fetch.all.roomReservationTypes()
}

async function fetchScheduledCourses(week: number, year: number, department: string) {
    return await api.value.fetch.target.scheduledCourses(week, year, department)
}

async function fetchCourseTypes(department: string) {
    return await api.value.fetch.all.courseTypes(department)
}

async function fetchUsers() {
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
    background: rgba(0, 0, 0, 0.6) url('@/assets/images/logo-head-gribou-rc-hand.svg') no-repeat 50% 50%;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    cursor: wait;
}
</style>
