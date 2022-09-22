<template>
  <Popper
      :id="props.data.id"
      class="frame"
      :show="isContextMenuOpened"
      :style="props.data.displayStyle"
      arrow
      @click.left="onClick"
  >
    <div>
      <RoomReservationForm
          :reservation="props.data.reservation"
          :is-open="isEditing"
          :rooms="props.data.rooms"
          :reservation-types="props.data.reservationTypes"
          :users="props.data.users"
          @closed="closeEdit"
          @saved="props.data.onFormSave"
          @cancelled="onCancel"
      ></RoomReservationForm>
      <p class="m-0">{{ props.data.title }}</p>
      <p class="m-0">{{ props.data.reservation.description }}</p>
      <p class="m-0">{{ responsible }}</p>
      <p class="m-0">{{ roomName }}</p>
    </div>
    <template #content>
      <CalendarSlotContextMenu
          :data="props.data"
          :on-delete="onDelete"
          :on-edit="onDoubleClick"
          :on-duplicate="onDuplicate"
      ></CalendarSlotContextMenu>
    </template>
  </Popper>
</template>

<script setup lang="ts">
import type { CalendarRoomReservationSlotData, CalendarSlotActions, CalendarSlotInterface } from '@/assets/js/types'
import CalendarSlotContextMenu from '@/components/calendar/CalendarSlotContextMenu.vue'
import RoomReservationForm from '@/components/RoomReservationForm.vue'
import { computed, onMounted, ref } from 'vue'

interface Props {
  data: CalendarRoomReservationSlotData;
  actions: CalendarSlotActions;
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
const responsible = computed(() => {
  const user = props.data.users[props.data.reservation.responsible]
  return user?.username
})
const roomName = computed(() => {
  const r = props.data.rooms[props.data.reservation.room]
  return r?.name
})

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

function onDelete () {
  props.actions.delete(props.data)
}

function onDuplicate () {
  // TODO: Duplicate reservation and open edit form
  console.log('On duplicate')
}

function onCancel () {
  closeEdit()
  if (props.data.isNew) {
    onDelete()
  }
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
  // Open the form if the slot has just been created
  if (props.data.isNew) {
    isEditing.value = true
  }
})
</script>

<script lang="ts">
export default {
  name: 'CalendarRoomReservationSlot',
  components: {},
}
</script>

<style scoped>
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
