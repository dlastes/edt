<template>
  <div class="container ms-1">
    <div class="row p-0">
      <div class="col-1 p-0 me-3"></div>
      <div v-for="day in days" class="col text-center border-dark border-bottom border-end border-top"
           :class="{'border-start border-dark': day === days[0]}">
        <div>{{ day.name }} {{ day.date }}</div>
      </div>
    </div>
    <div class="row" :style="{height: height}">
      <div class="col-1 p-0 me-3">
        <div :style="{height: height}" style="position: relative" class="col">
          <div v-for="hour in hourIndicators" :style="computeHourStyle(hour)">
            <h6 class="translate-middle-y">{{ hour.text }}</h6>
            <hr class="border border-primary border-1 vw-100 position-absolute top-0">
          </div>
        </div>
      </div>
      <div v-for="day in days" class="col text-center border-dark border-bottom border-end"
           :class="{'border-start border-dark': day === days[0]}">
        <div :style="{height: height}" style="position: relative" class="col">
          <CalendarSlot v-for="slot in displayableSlots[day.date]"
                        class="noselect"
                        @click.left="onSlotClicked(slot)"
                        @click.right.prevent
                        @contextmenu="onSlotRightClicked(slot)"
                        :style="computeStyle(slot)"
                        :title="slot.title">{{ slot.content }}
          </CalendarSlot>
        </div>
      </div>
    </div>
  </div>
  <!--      <div class="col m-0 p-1 text-end">
          <div class="row">
            <div>H</div>
          </div>
          <div :style="{height: height}" style="position: relative" class="col">
            <div v-for="hour in hourIndicators" :style="computeHourStyle(hour)">
              <div class="translate-middle-y">{{ hour.text }}</div>
              <hr class="border border-primary border-1 vw-100 position-absolute top-0">
            </div>
          </div>
        </div>
        <div v-for="day in days" class="col text-center border-dark border-bottom border-end border-top"
             :class="{'border-start border-dark': day === days[0]}">
          <div class="row border-bottom border-dark">
            <div>{{ day.name }} {{ day.date }}</div>
          </div>
          <div :style="{height: height}" style="position: relative" class="col">
            <CalendarSlot v-for="slot in displayableSlots[day.date]"
                          class="noselect"
                          @click.left="onSlotClicked(slot)"
                          @click.right.prevent
                          @contextmenu="onSlotRightClicked(slot)"
                          :style="computeStyle(slot)"
                          :title="slot.title">{{ slot.content }}
            </CalendarSlot>
          </div>
        </div>-->
</template>

<script setup lang="ts">
import { convertDecimalTimeToHuman } from '@/assets/js/helpers'
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
  return out
})

const hourIndicators = computed(() => {
  let start = Math.trunc(props.startTime / 60)
  let end = Math.trunc(props.endTime / 60)
  let hours = []
  for (let hour = start; hour <= end; ++hour) {
    let time: Time = {value: hour * 60, text: convertDecimalTimeToHuman(hour)}
    hours.push(time)
  }
  return hours
})

function onSlotClicked (slot: Slot) {
  console.log('Left click')
  console.log(slot.title)
}

function onSlotRightClicked (slot: Slot) {
  console.log('Right click')
  console.log(slot.title)
}

// Positioning and sizing

const heightValue = 500

const height = computed(() => {
  return `${heightValue}px`
})

function positionRelativeToColumn (value: number): number {
  return 100 * (value - props.startTime) / (props.endTime - props.startTime)
}

function computeSize (slot: Slot): string {
  let startPos = positionRelativeToColumn(slot.startTime.value)
  let endPos = positionRelativeToColumn(slot.endTime.value)
  let out = endPos - startPos
  return `${out}%`
}

function computeYOffset (time: number): string {
  let out = positionRelativeToColumn(time)
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
  let top = computeYOffset(slot.startTime.value)
  let height = computeSize(slot)
  return {
    height: height,
    top: top,
    position: 'absolute',
    width: '100%',
    'border-radius': '5px',
  }
}

function computeHourStyle (hour: Time): object {
  let top = computeYOffset(hour.value)
  return {
    height: height,
    top: top,
    position: 'absolute',
    width: '100%',
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
