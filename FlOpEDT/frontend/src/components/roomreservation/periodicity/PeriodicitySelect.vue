<template>
    <div>
        <select
            v-model="selectedType"
            class="form-select mb-2"
            aria-label="Select periodicity type"
            :disabled="props.isDisabled"
        >
            <option :value="undefined" disabled>Select a periodicity type</option>
            <option v-for="type in props.types" :key="type[0]" :value="type">
                {{ type[1] }}
            </option>
        </select>
        <PeriodicityByWeekEdit
            v-if="selectedType && selectedType[0] === 'BW'"
            :weekdays="props.weekdays"
            :is-disabled="props.isDisabled"
            v-model:model="updatedModel[selectedType[0]]"
        ></PeriodicityByWeekEdit>
        <PeriodicityByMonthEdit
            v-if="selectedType && selectedType[0] === 'BM'"
            :weekdays="props.weekdays"
            :is-disabled="props.isDisabled"
            v-model:model="updatedModel[selectedType[0]]"
        ></PeriodicityByMonthEdit>
    </div>
</template>

<script setup lang="ts">
import type {
    ReservationPeriodicityData,
    ReservationPeriodicityType,
    ReservationPeriodicityTypeName,
    WeekDay,
} from '@/assets/js/types'
import { computed } from 'vue'
import PeriodicityByWeekEdit from '@/components/roomreservation/periodicity/PeriodicityByWeekEdit.vue'
import PeriodicityByMonthEdit from '@/components/roomreservation/periodicity/PeriodicityByMonthEdit.vue'

type PeriodicityModel = {
    [periodicityTypeName in ReservationPeriodicityTypeName]: ReservationPeriodicityData
}

interface Props {
    types: Array<ReservationPeriodicityType>
    weekdays: Array<WeekDay>
    modelType: ReservationPeriodicityType
    modelPeriodicity: PeriodicityModel
    isDisabled: boolean
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:modelPeriodicity', model: PeriodicityModel): void

    (e: 'update:modelType', model: ReservationPeriodicityType): void
}

const emit = defineEmits<Emits>()

const selectedType = computed({
    get() {
        return props.modelType
    },
    set(value) {
        emit('update:modelType', value)
    },
})

const updatedModel = computed({
    get() {
        return props.modelPeriodicity
    },
    set(value) {
        emit('update:modelPeriodicity', value)
    },
})
</script>

<script lang="ts">
export default {
    name: 'PeriodicitySelect',
    components: {},
}
</script>

<style scoped></style>
