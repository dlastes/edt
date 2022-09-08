<template>
  <div class="btn-group" role="group" aria-label="Basic example">
    <button type="button" class="btn btn-success" @click="decrementWeek">&lt;</button>
    <div id="weekNumbers">
      <button v-for="weekId in weeks" type="button" class="btn btn-success"
              :class="{ selected: weekId === actualCurrentWeekId }"
              @click="updateWeek(weekId)">
        {{ allWeeks[weekId].number }}
      </button>
    </div>
    <button type="button" class="btn btn-success" @click="incrementWeek">&gt;</button>
  </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue'
import { computed, defineProps, ref } from 'vue'

interface Props {
  week: number,
  year: number,
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'weekChanged', id: number): void
  (e: 'yearChanged', value: string): void
}>()

const currentWeekNumber = ref(props.week)
const currentYear = ref(props.year)
const actualCurrentWeekId = ref(0)

const toDisplay = ref(8)
const toDisplayLeft = ref(toDisplay.value * 0.5)
const toDisplayRight = ref(toDisplay.value - toDisplayLeft.value)
const indexDisplay = ref(0)

interface Week {
  id: number,
  number: number,
  year: number
}

const allWeeks: Ref<Array<Week>> = ref([])

let id = 0
for (let y = -1; y <= 1; ++y) {
  for (let w = 1; w <= 52; ++w) {
    let newWeek: Week = {id: id++, number: w, year: currentYear.value + y}
    allWeeks.value.push(newWeek)
    if (newWeek.number === currentWeekNumber.value && newWeek.year === currentYear.value) {
      indexDisplay.value = newWeek.id
      actualCurrentWeekId.value = newWeek.id
    }
  }
}

const weeks = computed(() => {
  return Array.from({length: toDisplay.value}, (x, i) => indexDisplay.value + i - toDisplayLeft.value)
})

function decrementWeek () {
  if (indexDisplay.value - 1 > 0) {
    indexDisplay.value--
  }
}

function incrementWeek () {
  if (indexDisplay.value + 1 < allWeeks.value.length) {
    indexDisplay.value++
  }
}

function updateWeek (id: number) {
  if (id < 0 || id > allWeeks.value.length) {
    return
  }
  currentWeekNumber.value = allWeeks.value[id].number
  emit('weekChanged', currentWeekNumber.value)
}
</script>

<script lang="ts">
export default {
  name: 'WeekBanner',
  components: {},
}

</script>

<style scoped>
button {
  width: 50px;
}

.selected {
  background-color: blue;
}
</style>
