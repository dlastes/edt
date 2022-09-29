<template>
    <div>
        <label :for="props.id" class="form-label">{{ props.label }}</label>
        <select :id="props.id" class="form-select w-auto ms-1" aria-label="Select department">
            <option :value="undefined">Select an attribute</option>
            <option v-for="value in unselected" :key="value.id" :value="value.id" @click="selectValue(value.id)">
                {{ value.name }}
            </option>
        </select>
        <ul class="list-group">
            <li
                v-for="index in Array.from(Array(selected.length).keys())"
                :key="selected[index].id"
                :value="selected[index]"
                class="list-group-item"
            >
                <component
                    :is="props.component"
                    :value="selected[index]"
                    @update:value="updateValue(selected[index].id, $event)"
                    @removed="unselectValue(selected[index].id)"
                ></component>
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
import { computed, ref, watchEffect } from 'vue'
import type { DynamicSelectElementValue } from '@/assets/js/types'

interface Props {
    component: any
    values: Array<DynamicSelectElementValue>
    selectedValues: Array<DynamicSelectElementValue>
    label: string
    id: string
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:selectedValues', values: Array<DynamicSelectElementValue>): void
}

const emit = defineEmits<Emits>()

const updatedValues = ref(props.values)

watchEffect(() => {
    updatedValues.value = props.values
})

function updateValue(id: number, value: DynamicSelectElementValue) {
    const index = updatedValues.value.findIndex((val) => val.id === id)
    if (index < 0) {
        return
    }
    updatedValues.value[index] = value
    emitUpdate()
}

const selectedIds = ref<Array<number>>(props.selectedValues.map((value) => value.id))

const selected = computed(() => {
    return updatedValues.value.filter((val) => selectedIds.value.includes(val.id))
})

const unselected = computed(() => {
    return updatedValues.value.filter((val) => !selectedIds.value.includes(val.id))
})

function selectValue(id: number) {
    selectedIds.value.push(id)
    emitUpdate()
}

function unselectValue(id: number) {
    selectedIds.value = selectedIds.value.filter((valId) => valId != id)
    emitUpdate()
}

function emitUpdate() {
    emit('update:selectedValues', selected.value)
}
</script>

<script lang="ts">
export default {
    name: 'DynamicSelect',
    components: {},
}
</script>

<style scoped></style>
