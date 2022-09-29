<template>
    <DynamicSelectedElement :value="props.value">
        <template #input>
            <div>
                <label :for="`${props.value.name}-range-min`" class="form-label">Min: {{ minVal }}</label>
                <input
                    type="range"
                    class="form-range"
                    :id="`${props.value.name}-range-min`"
                    v-model.number="minVal"
                    :max="maxVal"
                />
            </div>
            <div>
                <label :for="`${props.value.name}-range-max`" class="form-label">Max: {{ maxVal }}</label>
                <input
                    type="range"
                    class="form-range"
                    :id="`${props.value.name}-range-max`"
                    v-model.number="maxVal"
                    :min="minVal"
                />
            </div>
        </template>
    </DynamicSelectedElement>
</template>

<script setup lang="ts">
import DynamicSelectedElement from '@/components/dynamicSelect/DynamicSelectedElement.vue'
import { computed, ref, watch } from 'vue'
import type { DynamicSelectElementNumericValue } from '@/assets/js/types'

interface Props {
    value: DynamicSelectElementNumericValue
}

const props = defineProps<Props>()

interface Emits {
    (e: 'update:value', value: DynamicSelectElementNumericValue): void
}

const emit = defineEmits<Emits>()

const elementValue = ref(props.value)

const minVal = computed({
    get() {
        return elementValue.value.min
    },
    set(value) {
        elementValue.value.min = value
    },
})

const maxVal = computed({
    get() {
        return elementValue.value.max
    },
    set(value) {
        elementValue.value.max = value
    },
})

// Bind the model to elementValue
emit('update:value', elementValue.value)
</script>

<script lang="ts">
export default {
    name: 'DynamicSelectedElementNumeric',
    components: {},
}
</script>

<style scoped></style>
