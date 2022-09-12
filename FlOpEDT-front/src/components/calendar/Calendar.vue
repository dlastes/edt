<template>
  <div class="container ms-1" @click="clicked">
    <div class="row p-0 flex-nowrap">
      <div class="col-1 p-0 me-3"></div>
      <div v-for="day in days" class="col text-center border-dark border-bottom border-end border-top"
           :class="{'border-start border-dark': day === days[0]}">
        <div>{{ day.name }} {{ day.date }}</div>
      </div>
    </div>
    <div class="row flex-nowrap position-relative" :style="{height: height}">
      <div class="col-1 p-0 me-3">
        <div v-for="hour in hourIndicators" :style="computeHourStyle(hour)" class="translate-middle-y">
          <h6 class="text-wrap">{{ hour.text }}</h6>
          <hr class="translate-middle-y border border-primary border-1 w-100 position-absolute top-0">
        </div>
      </div>
      <div v-for="day in days" class="col border-dark border-bottom border-end p-0 position-relative"
           :class="{'border-start border-dark': day === days[0]}" :style="{height: height}" style="min-width: 65px;">
        <component :is="slot.component" v-for="slot in displayableSlots[day.date]"
                   v-bind="{slot: slot.props, id: getSlotId(slot.props), style: computeStyle(slot.props)}"
                   class="noselect"
                   @click.right.prevent
                   @contextmenu="openContextMenu(getSlotId(slot.props))"
                   @interface="storeSlotInterface"
        >
        </component>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { convertDecimalTimeToHuman } from '@/assets/js/helpers'
import type { CalendarSlotInterface, Time } from '@/assets/js/types'
import { CalendarSlotElement } from '@/assets/js/types'
import { computed, defineProps, ref } from 'vue'

interface Slot {
  props: CalendarSlotElement,
  component: any,
  interface: object,
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
    out[index] = props.slots[index].filter(tmpSlot => canBeDisplayed(tmpSlot.props))
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

const slotInterfaces = ref<{ [key: string]: CalendarSlotInterface }>({})

const currentContextMenu = ref<string>('')

function storeSlotInterface (id: string, slotInterface: CalendarSlotInterface) {
  slotInterfaces.value[id] = slotInterface
}

function getSlotId (slot: CalendarSlotElement) {
  return slot.title.replace(' ', '-')
}

function openContextMenu (slotId: string) {
  closeCurrentContextMenu()

  // Store the current context menu if opened successfully
  if (slotInterfaces.value[slotId].openContextMenu()) {
    currentContextMenu.value = slotId
  }
}

function closeCurrentContextMenu () {
  // Close currently opened context menu (if exists)
  if (currentContextMenu.value) {
    slotInterfaces.value[currentContextMenu.value].closeContextMenu()
  }
}

function clicked () {
  closeCurrentContextMenu()
}

// Positioning and sizing

const pixelsPerHour = 50
const heightValue = computed(() => {
  return pixelsPerHour * (Math.trunc(props.endTime / 60) - Math.trunc(props.startTime / 60))
})

const height = computed(() => {
  return `${heightValue.value}px`
})

function positionRelativeToColumn (value: number): number {
  return 100 * (value - props.startTime) / (props.endTime - props.startTime)
}

function computeHeight (slot: CalendarSlotElement): string {
  let startPos = positionRelativeToColumn(slot.startTime.value)
  let endPos = positionRelativeToColumn(slot.endTime.value)
  let out = endPos - startPos
  return `${out}%`
}

function computeYOffset (time: number): string {
  let out = positionRelativeToColumn(time)
  return `${out}%`
}

function canBeDisplayed (slot: CalendarSlotElement): boolean {
  let out = slot.startTime.value >= props.startTime
  if (!out) {
    console.log(`Slot ${slot.title} cannot be displayed because it does not begin after day start time`)
  }
  return out
}

function computeStyle (slot: CalendarSlotElement): object {
  let top = computeYOffset(slot.startTime.value)
  let height = computeHeight(slot)
  return {
    height: height,
    top: top,
    position: 'absolute',
    'text-align': 'center',
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
