<template>
  <Popper
      :id="props.data.id"
      class="frame"
      :show="isContextMenuOpened"
      :style="props.data.displayStyle"
      @click.left="onClick"
  >
    <div>
      <RoomReservationForm
          :reservation="props.data.reservation"
          :is-open="isEditing"
          @closed="closeEdit"
      ></RoomReservationForm>
      <p class="m-0">{{ props.data.title }}</p>
      <p class="m-0">{{ props.data.reservation.description }}</p>
      <p class="m-0">{{ props.data.reservation.responsible }}</p>
    </div>
    <template #content>
      <CalendarSlotContextMenu :data="props.data"></CalendarSlotContextMenu>
    </template>
  </Popper>
</template>

<script setup lang="ts">
import type { CalendarRoomReservationSlotData, CalendarSlotInterface, } from '@/assets/js/types'
import CalendarSlotContextMenu from '@/components/calendar/CalendarSlotContextMenu.vue'
import RoomReservationForm from '@/components/RoomReservationForm.vue'
import { onMounted, ref } from 'vue'

interface Props {
  data: CalendarRoomReservationSlotData;
}

const props = defineProps<Props>()

interface Emits {
  (e: 'interface', id: string, slotInterface: CalendarSlotInterface): void;
}

const emit = defineEmits<Emits>()

const isContextMenuOpened = ref<boolean>(false)
const clickCount = ref(0)
const timer = ref()
const isEditing = ref(false)

function onClick () {
  if (++clickCount.value == 1) {
    timer.value = setTimeout(() => {
      clickCount.value = 0
      onSingleClick()
    }, 300)
    return
  }
  clearTimeout(timer.value)
  clickCount.value = 0
  onDoubleClick()
}

function onSingleClick () {
  if (isEditing.value) {
    // Ignore click when form is open
    return
  }
  console.log(`Click on ${props.data.title}`)
}

function onDoubleClick () {
  if (isEditing.value) {
    // Ignore click when form is open
    return
  }
  openEdit()
}

function openContextMenu (): boolean {
  isContextMenuOpened.value = true
  return isContextMenuOpened.value
}

function closeContextMenu () {
  isContextMenuOpened.value = false
}

function openEdit () {
  isEditing.value = true
}

function closeEdit () {
  isEditing.value = false
}

function emitInterface () {
  emit('interface', props.data.id, {
    openContextMenu: openContextMenu,
    closeContextMenu: closeContextMenu,
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
  font-weight: bold;
  margin: 0;
}
</style>
