<template>
  <div class="container">
    <div class="row"> <!-- Header -->
      <div v-for="day in days" class="col text-center border-dark border-bottom border-end border-top"
           :class="{'border-start border-dark': day === days[0]}">
        <div class="row border-bottom border-dark">
          <div>{{ day.name }} {{ day.date }}</div>
        </div>
        <div :style="{height: height}" class="col">
          <CalendarSlot v-for="slot in displayableSlots[day.date]"
                        :style="computeStyle(slot)"
                        :title="slot.title">{{ slot.content }}
          </CalendarSlot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Time } from '@/assets/js/types'
import CalendarSlot from '@/components/calendar/CalendarSlot.vue'
import { computed, defineProps } from 'vue'

interface Slot {
  startTime: Time,
  endTime: Time,
  title: string
  content: string,
}

interface Props {
  days: {
    [index: number]: {
      name: string,
      date: string,
    }
  },
  slots: {
    [index: string]: Array<Slot>
  },
  startTime: number,
  endTime: number,
}

const props = defineProps<Props>()

const displayableSlots = computed(() => {
  let out: { [index: string]: Array<Slot> } = {}
  Object.keys(props.slots).forEach(index => {
    if (!(index in out)) {
      out[index] = []
    }
    out[index] = props.slots[index].filter(tmpSlot => canBeDisplayed(tmpSlot))
  })
  console.log(out)
  return out
})

const heightValue = 300

const height = computed(() => {
  return `${heightValue}px`
})

function computeSize (slot: Slot): string {
  let out = heightValue * (slot.startTime.value - slot.endTime.value) / (props.startTime - props.endTime)
  console.log(slot.title)
  console.log(out)
  return `${out}px`
}

function computeYOffset (slot: Slot): string {
  let out = (slot.startTime.value - props.startTime) * 100 / (props.endTime - props.startTime)
  console.log(slot.title)
  console.log(out)
  return `${out}%`
}

function canBeDisplayed (slot: Slot): boolean {
  let out = slot.startTime.value >= props.startTime
  if (!out) {
    console.log(`Slot ${slot.title} cannot be displayed because it does not begin after day start time`)
  }
  return out
}

function computeStyle (slot: Slot): object {
  console.log('Top')
  let top = computeYOffset(slot)
  console.log('Height')
  let height = computeSize(slot)
  return {
    height: height,
    top: top,
    position: 'relative',
  }
}

</script>

<script lang="ts">
export default {
  name: 'Calendar',
  components: {},
}

</script>

<style scoped>

</style>
