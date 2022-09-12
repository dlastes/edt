<template>
  <Popper class="border border-dark frame m-0" :style="props.style" :show="isContextMenuOpened">
    <div @click="onClick"
         style="overflow: hidden;"
         :id="props.id">
      <p class="m-0">{{ props.slot.title }}</p>
      <p class="m-0">{{ props.slot.reservation.description }}</p>
      <p class="m-0">{{ props.slot.reservation.responsible }}</p>
    </div>
    <template #content>
      <CalendarSlotContextMenu :slot="props.slot"></CalendarSlotContextMenu>
    </template>
  </Popper>
</template>

<script setup lang="ts">
import type { CalendarRoomReservationSlotElement, CalendarSlotInterface } from '@/assets/js/types'
import CalendarSlotContextMenu from '@/components/calendar/CalendarSlotContextMenu.vue'
import { onMounted, ref } from 'vue'

interface Props {
  slot: CalendarRoomReservationSlotElement,
  id: string,
  style: object,
}

const props = defineProps<Props>()

interface Emits {
  (e: 'interface', id: string, slotInterface: CalendarSlotInterface): void
}

const emit = defineEmits<Emits>()

const isContextMenuOpened = ref<boolean>(false)

function onClick () {
  console.log(props.slot.title)
}

function openContextMenu (): boolean {
  isContextMenuOpened.value = true
  return isContextMenuOpened.value
}

function closeContextMenu (): boolean {
  isContextMenuOpened.value = false
  return isContextMenuOpened.value
}

function emitInterface () {
  emit('interface', props.id, {
    openContextMenu: openContextMenu,
    closeContextMenu: closeContextMenu
  })
}

onMounted(() => {
  emitInterface()
})

</script>

<script lang="ts">
export default {
  name: 'CalendarRoomReservationSlot',
  components: {},
}

</script>

<style scoped>
div {
  min-height: 50px;
}

.frame {
  border-radius: 5px;
  width: 100%;
}
</style>
