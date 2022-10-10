<template>
    <ModalForm
        :is-open="props.isOpen"
        :is-locked="isFormLocked"
        :on-cancel="onFormCancel"
        :on-save="onFormSave"
        @interface="onFormInterface"
        class="text-start"
    >
        <template #title>Room reservation</template>
        <template #body>
            <!-- Title -->
            <div class="form-floating mb-3">
                <input
                    :id="generateId('title')"
                    type="text"
                    class="form-control"
                    placeholder="Title"
                    maxlength="30"
                    v-model="title"
                />
                <label :for="generateId('title')" class="form-label">Title</label>
            </div>
            <!-- Description -->
            <div class="form-floating mb-3">
                <textarea
                    :id="generateId('description')"
                    type="text"
                    class="form-control"
                    placeholder="Description"
                    rows="2"
                    v-model="description"
                ></textarea>
                <label :for="generateId('description')" class="form-label">Description</label>
            </div>
            <!-- Room -->
            <div class="form-floating mb-3">
                <select class="form-select" :id="generateId('room')" v-model="selectedRoom">
                    <option value="-1" disabled>Select a room</option>
                    <option v-for="room in props.rooms" :key="room.id" :value="room.id">
                        {{ room.name }}
                    </option>
                </select>
                <label :for="generateId('room')" class="form-label">Room</label>
            </div>
            <!-- Date -->
            <div class="mb-3">
                <DayPicker
                    :start-date="date"
                    :should-reset="shouldDayPickerReset"
                    :on-reset="(shouldDayPickerReset = false)"
                    @update:date="updateDate"
                    :min-date="new Date()"
                    :clearable="false"
                >
                    <template #input="{ value }">
                        <div class="form-floating">
                            <input
                                :id="generateId('date')"
                                type="text"
                                class="form-control"
                                placeholder="Date"
                                :value="value"
                            />
                            <label :for="generateId('date')" class="form-label">Date</label>
                        </div>
                    </template>
                </DayPicker>
            </div>
            <div class="row m-0 gx-1 mb-3">
                <div class="col" style="min-width: 100px">
                    <!-- Start time -->
                    <TimePicker
                        :hours="startTime.hours"
                        :minutes="startTime.minutes"
                        @update-time="updateStartTime"
                        :should-reset="shouldStartTimePickerReset"
                        @on-reset="shouldStartTimePickerReset = false"
                    >
                        <template #input="{ value }">
                            <div class="form-floating">
                                <input
                                    :id="generateId('startTime')"
                                    type="text"
                                    class="form-control"
                                    placeholder="Start time"
                                    :value="value"
                                    readonly
                                />
                                <label :for="generateId('startTime')" class="form-label">Start time</label>
                            </div>
                        </template>
                    </TimePicker>
                </div>
                <div class="col" style="min-width: 100px">
                    <!-- End time -->
                    <TimePicker
                        :hours="endTime.hours"
                        :minutes="endTime.minutes"
                        @update-time="updateEndTime"
                        :should-reset="shouldEndTimePickerReset"
                        @on-reset="shouldEndTimePickerReset = false"
                    >
                        <template #input="{ value }">
                            <div class="form-floating">
                                <input
                                    :id="generateId('endTime')"
                                    type="text"
                                    class="form-control"
                                    placeholder="End time"
                                    :value="value"
                                    readonly
                                />
                                <label :for="generateId('endTime')" class="form-label">End time</label>
                            </div>
                        </template>
                    </TimePicker>
                </div>
            </div>
            <!-- Responsible -->
            <div class="form-floating mb-3">
                <input
                    :id="generateId('responsible')"
                    type="text"
                    class="form-control"
                    placeholder="Responsible"
                    :value="reservationResponsibleUsername"
                    disabled
                />
                <label :for="generateId('responsible')" class="form-label">Responsible</label>
            </div>
            <!-- Type -->
            <div class="form-floating mb-3">
                <select class="form-select" :id="generateId('reservationType')" v-model="selectedType">
                    <option :value="-1" disabled>Select a reservation type</option>
                    <option v-for="type in props.reservationTypes" :key="type.id" :value="type.id">
                        {{ type.name }}
                    </option>
                </select>
                <label :for="generateId('reservationType')" class="form-label">Reservation type</label>
            </div>
            <!-- Periodicity -->
            <div class="mb-3 border rounded p-2">
                <div class="form-check form-switch">
                    <input
                        class="form-check-input"
                        type="checkbox"
                        v-model="isPeriodic"
                        role="switch"
                        :id="generateId('isPeriodic')"
                    />
                    <label class="form-check-label" :for="generateId('isPeriodic')">Repeat?</label>
                </div>
                <div v-if="isPeriodic">
                    <div class="row mb-2 gx-1">
                        <!-- Periodicity start date -->
                        <div class="col">
                            <DayPicker
                                :start-date="periodicityStart"
                                :should-reset="shouldDayPickerReset"
                                :on-reset="(shouldDayPickerReset = false)"
                                @update:date="updatePeriodicityStartDate"
                                :min-date="new Date()"
                                :clearable="false"
                            >
                                <template #input="{ value }">
                                    <div class="form-floating">
                                        <input
                                            :id="generateId('periodicity-start-date')"
                                            type="text"
                                            class="form-control"
                                            placeholder="Date"
                                            :value="value"
                                            readonly
                                        />
                                        <label :for="generateId('periodicity-start-date')" class="form-label"
                                            >Start date</label
                                        >
                                    </div>
                                </template>
                            </DayPicker>
                        </div>
                        <!-- Periodicity end date -->
                        <div class="col">
                            <DayPicker
                                :start-date="periodicityEnd"
                                :should-reset="shouldDayPickerReset"
                                :on-reset="(shouldDayPickerReset = false)"
                                @update:date="updatePeriodicityEndDate"
                                :min-date="periodicityEndMinDate"
                                :clearable="false"
                            >
                                <template #input="{ value }">
                                    <div class="form-floating">
                                        <input
                                            :id="generateId('periodicity-end-date')"
                                            type="text"
                                            class="form-control"
                                            placeholder="Date"
                                            :value="value"
                                            readonly
                                        />
                                        <label :for="generateId('periodicity-end-date')" class="form-label"
                                            >End date</label
                                        >
                                    </div>
                                </template>
                            </DayPicker>
                        </div>
                    </div>
                    <PeriodicitySelect
                        :class="selectPeriodicityClass"
                        :types="props.periodicityTypes"
                        :weekdays="props.weekdays"
                        v-model:model-type="selectedPeriodicityType"
                        v-model:modelPeriodicity="periodicityChoice"
                    ></PeriodicitySelect>
                </div>
            </div>
            <!-- Send email -->
            <div class="form-check form-switch mb-3">
                <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="email"
                    role="switch"
                    :id="generateId('email')"
                />
                <label class="form-check-label" :for="generateId('email')">Send a confirm email?</label>
            </div>
        </template>
    </ModalForm>
</template>

<script setup lang="ts">
import { parseReason } from '@/assets/js/helpers'
import { apiKey, requireInjection } from '@/assets/js/keys'
import type {
    FormInterface,
    ReservationPeriodicity,
    ReservationPeriodicityByMonth,
    ReservationPeriodicityByWeek,
    ReservationPeriodicityData,
    ReservationPeriodicityEachMonthSameDate,
    ReservationPeriodicityType,
    ReservationPeriodicityTypeName,
    Room,
    RoomReservation,
    RoomReservationType,
    User,
    WeekDay,
} from '@/assets/js/types'
import DayPicker from '@/components/DayPicker.vue'
import ModalForm from '@/components/ModalForm.vue'
import TimePicker from '@/components/TimePicker.vue'
import { computed, defineProps, ref, watch } from 'vue'
import PeriodicitySelect from '@/components/roomreservation/periodicity/PeriodicitySelect.vue'

interface Emits {
    (e: 'saved', reservation: RoomReservation): void

    (e: 'closed'): void

    (e: 'cancelled'): void
}

const emit = defineEmits<Emits>()

interface Props {
    reservation: RoomReservation
    isOpen: boolean
    isNew: boolean
    rooms: { [roomId: number]: Room }
    reservationTypes: Array<RoomReservationType>
    users: { [userId: number]: User }
    periodicityTypes: Array<ReservationPeriodicityType>
    weekdays: Array<WeekDay>
    periodicity: ReservationPeriodicity | null
}

const props = defineProps<Props>()

const api = requireInjection(apiKey)

class ReservationTime {
    hours = 0
    minutes = 0

    static toString = (time: ReservationTime): string => {
        return `${time.hours}:${time.minutes}:00`
    }

    public static fromString(time: string): ReservationTime {
        const array = time.split(':')
        const out = new ReservationTime()
        out.hours = parseInt(array[0])
        out.minutes = parseInt(array[1])
        return out
    }
}

const shouldDayPickerReset = ref(false)
const shouldStartTimePickerReset = ref(false)
const shouldEndTimePickerReset = ref(false)

const reservationResponsibleUsername = computed(() => {
    const user = props.users[props.reservation.responsible]
    return user ? `${user.first_name} ${user.last_name} (${user.username})` : 'Unknown'
})

const formInterface = ref<FormInterface>()
const isFormLocked = ref(false)

const title = ref(props.reservation.title)
const description = ref(props.reservation.description)
const selectedResponsible = ref(props.reservation.responsible)
const selectedRoom = ref(props.reservation.room)
const selectedType = ref(props.reservation.reservation_type)
const isPeriodic = ref(props.reservation.periodicity != null)
const email = ref(props.reservation.email)
const startTime = ref(ReservationTime.fromString(props.reservation.start_time))
const endTime = ref(ReservationTime.fromString(props.reservation.end_time))
const date = ref(props.reservation.date)

// Get the possibly existing periodicity values
const initPeriodicityId = computed(() => (props.periodicity ? props.periodicity.data.id : -1))
const periodicityStart = ref(props.periodicity ? props.periodicity.data.start : props.reservation.date)
const periodicityEndMinDate = computed(() => {
    const startDate = new Date(periodicityStart.value)
    return new Date(`${startDate.getFullYear()}-${startDate.getMonth() + 1}-${startDate.getDate() + 1}`)
})
const periodicityEnd = ref(
    props.periodicity ? props.periodicity.data.end : periodicityEndMinDate.value.toLocaleDateString()
)

const currentDay = new Date(props.reservation.date).getDay()
const currentWeekdayRef = computed(() => {
    const weekday = props.weekdays.find((d) => d.num === currentDay - 1)
    return weekday?.ref
})

const selectedPeriodicityType = ref<ReservationPeriodicityType | undefined>(
    props.periodicity
        ? props.periodicityTypes.find((t) => t[0] === props.periodicity?.data.periodicity_type)
        : undefined
)

// Update the reservation periodicity form if the provided periodicity have changed
watch(
    () => props.periodicity,
    (newValue) => {
        if (newValue) {
            selectedPeriodicityType.value = props.periodicityTypes.find((t) => t[0] === newValue.data.periodicity_type)
            periodicityStart.value = newValue.data.start
            periodicityEnd.value = newValue.data.end
        } else {
            selectedPeriodicityType.value = undefined
            periodicityStart.value = props.reservation.date
            periodicityEnd.value = periodicityEndMinDate.value.toLocaleDateString()
        }
    }
)

const periodicityID = ref(initPeriodicityId.value)

const requiredClass = 'border border-danger rounded'

const selectPeriodicityClass = computed(() => {
    return isPeriodic.value && selectedPeriodicityType.value === undefined ? requiredClass : ''
})

const originalDuration =
    endTime.value.hours * 60 + endTime.value.minutes - (startTime.value.hours * 60 + startTime.value.minutes)

// Create an object of each type
const periodicityByWeek = computed<ReservationPeriodicityByWeek>(() => {
    return {
        id: selectedPeriodicityType.value && selectedPeriodicityType.value[0] === 'BW' ? initPeriodicityId.value : -1,
        start: periodicityStart.value,
        end: periodicityEnd.value,
        periodicity_type: 'BW',
        bw_weekdays: currentWeekdayRef.value ? [currentWeekdayRef.value] : [],
        bw_weeks_interval: 1,
    }
})
const periodicityByMonth = computed<ReservationPeriodicityByMonth>(() => {
    return {
        id: selectedPeriodicityType.value && selectedPeriodicityType.value[0] === 'BM' ? initPeriodicityId.value : -1,
        start: periodicityStart.value,
        end: periodicityEnd.value,
        periodicity_type: 'BM',
        bm_x_choice: 1,
        bm_day_choice: currentWeekdayRef.value ?? '',
    }
})
const periodicityEachMonthSameDate = computed<ReservationPeriodicityEachMonthSameDate>(() => {
    return {
        id: selectedPeriodicityType.value && selectedPeriodicityType.value[0] === 'EM' ? initPeriodicityId.value : -1,
        start: periodicityStart.value,
        end: periodicityEnd.value,
        periodicity_type: 'EM',
    }
})

// Fill the values specific to the periodicity type
if (props.periodicity) {
    switch (props.periodicity.data.periodicity_type) {
        case 'BW':
            {
                const byWeek = props.periodicity.data as ReservationPeriodicityByWeek
                periodicityByWeek.value.bw_weekdays = byWeek.bw_weekdays
                periodicityByWeek.value.bw_weeks_interval = byWeek.bw_weeks_interval
            }
            break
        case 'BM':
            {
                const byMonth = props.periodicity.data as ReservationPeriodicityByMonth
                periodicityByMonth.value.bm_day_choice = byMonth.bm_day_choice
                periodicityByMonth.value.bm_x_choice = byMonth.bm_x_choice
            }
            break
    }
}

const periodicityChoice = computed<{ [name in ReservationPeriodicityTypeName]: ReservationPeriodicityData }>(() => {
    return {
        BW: periodicityByWeek.value,
        BM: periodicityByMonth.value,
        EM: periodicityEachMonthSameDate.value,
    }
})

function resetValues() {
    title.value = props.reservation.title
    description.value = props.reservation.description
    selectedResponsible.value = props.reservation.responsible
    selectedRoom.value = props.reservation.room
    selectedType.value = props.reservation.reservation_type
    isPeriodic.value = props.reservation.periodicity != null
    periodicityID.value = initPeriodicityId.value
    email.value = props.reservation.email
    startTime.value = ReservationTime.fromString(props.reservation.start_time)
    endTime.value = ReservationTime.fromString(props.reservation.end_time)
    date.value = props.reservation.date

    shouldDayPickerReset.value = true
    shouldStartTimePickerReset.value = true
    shouldEndTimePickerReset.value = true
}

function onFormCancel() {
    resetValues()
    cancel()
}

async function onFormSave() {
    isFormLocked.value = true
    if (isPeriodic.value) {
        periodicityID.value = await savePeriodicity()
    }
    saveReservation()
}

async function savePeriodicity(): Promise<number> {
    if (!selectedPeriodicityType.value) {
        return Promise.reject('No periodicity has been defined.')
    }

    let apiMethod: typeof api.post | typeof api.put = api.put
    // Method is POST if the reservation has a new periodicity (either new type or didn't have before)
    if (
        !props.reservation.periodicity ||
        props.reservation.periodicity < 0 ||
        (props.periodicity && props.periodicity.data.periodicity_type != selectedPeriodicityType.value[0])
    ) {
        apiMethod = api.post
    }

    let apiCall
    let periodicityToUpdate: ReservationPeriodicityData
    let periodicityToUpdateActualType

    switch (selectedPeriodicityType.value[0]) {
        case 'BW':
            apiCall = apiMethod.reservationPeriodicityByWeek
            periodicityToUpdate = periodicityChoice.value.BW
            periodicityToUpdateActualType = periodicityToUpdate as ReservationPeriodicityByWeek
            break
        case 'EM':
            apiCall = apiMethod.reservationPeriodicityEachMonthSameDate
            periodicityToUpdate = periodicityChoice.value.EM
            periodicityToUpdateActualType = periodicityToUpdate as ReservationPeriodicityEachMonthSameDate
            break
        case 'BM':
            apiCall = apiMethod.reservationPeriodicityByMonth
            periodicityToUpdate = periodicityChoice.value.BM
            periodicityToUpdateActualType = periodicityToUpdate as ReservationPeriodicityByMonth
            break
    }
    periodicityToUpdateActualType.start = periodicityToUpdateActualType.start.replaceAll('/', '-')
    periodicityToUpdateActualType.end = periodicityToUpdateActualType.end.replaceAll('/', '-')
    return await apiCall(periodicityToUpdateActualType)
        .then((value) => {
            // Give it the id given by the api
            periodicityToUpdate.id = value.id
            return value.id
        })
        .catch((reason) => {
            handleReason(reason)
            return periodicityToUpdate.id
        })
}

function saveReservation() {
    const obj: RoomReservation = {
        date: date.value.replaceAll('/', '-'),
        description: description.value,
        email: email.value,
        end_time: ReservationTime.toString(endTime.value),
        id: Math.max(0, props.reservation.id),
        periodicity: periodicityID.value,
        responsible: selectedResponsible.value,
        room: selectedRoom.value,
        start_time: ReservationTime.toString(startTime.value),
        title: title.value,
        reservation_type: selectedType.value,
    }
    const method = props.isNew ? api.post : api.put
    method
        .roomReservation(obj)
        .then(
            (value) => {
                emit('saved', value)
                close()
            },
            (reason) => handleReason(reason)
        )
        .catch((reason) => handleReason(reason))
}

function handleReason(reason: unknown) {
    formInterface.value?.dismissAlerts()
    parseReason(reason, formInterface.value?.addAlert)
    isFormLocked.value = false
}

function onFormInterface(value: FormInterface) {
    formInterface.value = value
}

function updateDate(newDate: string) {
    date.value = newDate
}

function updatePeriodicityStartDate(newDate: string) {
    periodicityStart.value = newDate
    const startDate = new Date(newDate)
    const endDate = new Date(periodicityEnd.value)

    if (
        startDate.getFullYear() === endDate.getFullYear() &&
        startDate.getMonth() === endDate.getMonth() &&
        startDate.getDate() >= endDate.getDate()
    ) {
        updatePeriodicityEndDate(periodicityEndMinDate.value.toLocaleDateString())
    }
}

function updatePeriodicityEndDate(newDate: string) {
    periodicityEnd.value = newDate
}

/**
 * Sets the reservation start time. The end time is changed so that the duration stays the same if
 * the new start time is after the end time.
 * @param time
 */
function updateStartTime(time: { hours: number; minutes: number }) {
    // Compute the new start time and the end time as number of minutes
    const newStartTimeAbsoluteTime = time.hours * 60 + time.minutes
    let endAbsoluteTime = endTime.value.hours * 60 + endTime.value.minutes

    // Make sure the start time stays before the end time
    if (newStartTimeAbsoluteTime >= endAbsoluteTime) {
        // New start time is after the end time
        // Apply the duration difference to the end time
        endAbsoluteTime = newStartTimeAbsoluteTime + originalDuration
        updateEndTime({ hours: Math.trunc(endAbsoluteTime / 60), minutes: endAbsoluteTime % 60 })
    }

    // Change the start time
    startTime.value = time
}

/**
 * Sets the reservation end time. The start time is changed so that the duration stays the same if
 * the new end time is before the end time.
 * @param time
 */
function updateEndTime(time: { hours: number; minutes: number }) {
    // Compute the new end time and the start time as number of minutes
    const newEndTimeAbsoluteTime = time.hours * 60 + time.minutes
    let startAbsoluteTime = startTime.value.hours * 60 + startTime.value.minutes

    // Make sure the end time stays after the start time
    if (newEndTimeAbsoluteTime <= startAbsoluteTime) {
        // New end time is before the start time
        // Apply the duration difference to the start time
        startAbsoluteTime = newEndTimeAbsoluteTime - originalDuration
        updateStartTime({ hours: Math.trunc(startAbsoluteTime / 60), minutes: startAbsoluteTime % 60 })
    }

    // Change the end time
    endTime.value = time
}

function generateId(element: string) {
    return `edit-room-reservation-${element}-${props.reservation.id}`
}

function close() {
    isFormLocked.value = false
    formInterface.value?.close()
    emit('closed')
}

function cancel() {
    formInterface.value?.close()
    emit('cancelled')
}
</script>

<script lang="ts">
export default {
    name: 'RoomReservationForm',
    components: {},
}
</script>

<style scoped></style>
