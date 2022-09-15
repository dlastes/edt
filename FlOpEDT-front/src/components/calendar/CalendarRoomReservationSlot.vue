<template>
  <Popper class="frame" :show="isContextMenuOpened" :style="props.data.displayStyle"
          :id="props.data.id">
    <div @click="onClick">
      <p class="m-0">{{ props.data.title }}</p>
      <p class="m-0">{{ props.data.reservation.description }}</p>
      <p class="m-0">{{ props.data.reservation.responsible }}</p>
    </div>
    <template #content>
      <CalendarSlotContextMenu :slot="props.data"></CalendarSlotContextMenu>
    </template>
  </Popper>
</template>

<script setup lang="ts">
import type { CalendarRoomReservationSlotData, CalendarSlotInterface } from '@/assets/js/types'
import CalendarSlotContextMenu from '@/components/calendar/CalendarSlotContextMenu.vue'
import { onMounted, ref } from 'vue'

interface Props {
  data: CalendarRoomReservationSlotData
}

const props = defineProps<Props>()

interface Emits {
  (e: 'interface', id: string, slotInterface: CalendarSlotInterface): void
}

const emit = defineEmits<Emits>()

const isContextMenuOpened = ref<boolean>(false)

function onClick () {
  console.log(props.data.title)
}

function openContextMenu (): boolean {
  isContextMenuOpened.value = true
  return isContextMenuOpened.value
}

function closeContextMenu () {
  isContextMenuOpened.value = false
}

function emitInterface () {
  emit('interface', props.data.id, {
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

p {
  font-size: 0.625em;
  margin: 0;
}
</style>
