<template>
  <table class="w-100" @click="clicked">
    <tr class="p-0 flex-nowrap">
      <th class="p-0 me-3"></th>
      <th
          v-for="day in days"
          :key="day.date"
          class="col text-center border-dark border-bottom border-end border-top"
          :class="{ 'border-start border-dark': day === days[0] }"
      >
        <div>{{ day.name }} {{ day.date }}</div>
      </th>
    </tr>
    <tr class="flex-nowrap position-relative" :style="{ height: height }">
      <td class="p-0 h-100" style="min-width: 50px; width: 50px">
        <div
            v-for="hour in hourIndicators"
            :key="hour.value"
            :style="computeHourStyle(hour)"
            class="translate-middle-y"
        >
          <h6 class="text-wrap">{{ hour.text }}</h6>
          <hr
              class="border border-primary border-1 w-100 position-absolute top-0"
              style="transform: translateY(-3px)"
          />
        </div>
      </td>
      <td
          v-for="day in days"
          :key="day.date"
          class="col border-dark border-bottom border-end p-0"
          :class="{ 'border-start border-dark': day === days[0] }"
          :style="{ height: height }"
          style="min-width: 65px"
      >
        <div class="position-relative h-100">
          <component
              :is="slot.component"
              v-for="slot in displayableSlots[day.date]"
              :key="slot.data.id"
              :data="slot.data"
              :style="computeStyle(slot.data)"
              class="noselect slot m-0 border border-dark"
              @click.right.prevent
              @contextmenu="openContextMenu(slot.data.id)"
              @interface="storeSlotInterface"
          >
          </component>
        </div>
      </td>
    </tr>
  </table>
</template>

<script setup lang="ts">
import { convertDecimalTimeToHuman } from '@/assets/js/helpers'
import type { CalendarSlot, CalendarSlotData, CalendarSlotInterface, Time, } from '@/assets/js/types'
import { computed, defineProps, ref } from 'vue'

interface Props {
  days: {
    [index: number]: {
      name: string;
      date: string;
    };
  };
  slots: {
    [index: string]: Array<CalendarSlot>;
  };
  startTime: number;
  endTime: number;
}

const props = defineProps<Props>()

const displayableSlots = computed(() => {
  const out: { [index: string]: Array<CalendarSlot> } = {}
  Object.keys(props.slots).forEach((index) => {
    if (!(index in out)) {
      out[index] = []
    }
    out[index] = props.slots[index].filter((tmpSlot) =>
        canBeDisplayed(tmpSlot.data)
    )
  })
  return out
})

const hourIndicators = computed(() => {
  const start = Math.trunc(props.startTime / 60)
  const end = Math.trunc(props.endTime / 60)
  const hours = []
  for (let hour = start; hour <= end; ++hour) {
    const time: Time = {
      value: hour * 60,
      text: convertDecimalTimeToHuman(hour),
    }
    hours.push(time)
  }
  return hours
})

const slotInterfaces = ref<{ [key: string]: CalendarSlotInterface }>({})

const currentContextMenu = ref<string>('')

function storeSlotInterface (id: string, slotInterface: CalendarSlotInterface) {
  slotInterfaces.value[id] = slotInterface
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
  return (
      pixelsPerHour *
      (Math.trunc(props.endTime / 60) - Math.trunc(props.startTime / 60))
  )
})

const height = computed(() => {
  return `${heightValue.value}px`
})

function positionRelativeToColumn (value: number): number {
  return (100 * (value - props.startTime)) / (props.endTime - props.startTime)
}

function computeHeight (slot: CalendarSlotData): string {
  const startPos = positionRelativeToColumn(slot.startTime.value)
  const endPos = positionRelativeToColumn(slot.endTime.value)

  const out = endPos - startPos
  return `${out}%`
}

function computeYOffset (time: number): string {
  const out = positionRelativeToColumn(time)
  return `${out}%`
}

function canBeDisplayed (slot: CalendarSlotData): boolean {
  const out = slot.startTime.value >= props.startTime
  if (!out) {
    console.log(
        `Slot ${slot.title} cannot be displayed because it does not begin after day start time`
    )
  }
  return out
}

function computeStyle (slot: CalendarSlotData): object {
  const top = computeYOffset(slot.startTime.value)
  const height = computeHeight(slot)
  return {
    height: height,
    top: top,
    position: 'absolute',
    'text-align': 'center',
  }
}

function computeHourStyle (hour: Time): object {
  const top = computeYOffset(hour.value)
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
  name: 'CalendarComponent',
  components: {},
}
</script>

<style>
.slot > div {
  height: 100%;
}
</style>
