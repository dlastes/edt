<template>
  <ModalForm :is-open="props.isOpen" @closed="emitClose">
    <template #title>Room reservation</template>
    <template #body>
      <div class="form-floating mb-3">
        <input
            :id="generateId('title')"
            type="text"
            class="form-control"
            placeholder="Title"
            maxlength="30"
            :value="reservation.title"
        />
        <label :for="generateId('title')" class="form-label">Title</label>
      </div>
      <div class="form-floating mb-3">
        <textarea
            :id="generateId('description')"
            type="text"
            class="form-control"
            placeholder="Description"
            rows="2"
            :value="reservation.description"
        ></textarea>
        <label :for="generateId('description')" class="form-label"
        >Description</label
        >
      </div>
      <div class="form-floating mb-3">
        <input
            :id="generateId('room')"
            type="text"
            class="form-control"
            placeholder="Room"
            maxlength="30"
            :value="reservation.room"
        />
        <label :for="generateId('room')" class="form-label">Room</label>
      </div>
      <div class="form-floating mb-3">
        <input
            :id="generateId('type')"
            type="text"
            class="form-control"
            placeholder="Type"
            maxlength="30"
            :value="reservation.type"
        />
        <label :for="generateId('type')" class="form-label">Type</label>
      </div>
    </template>
  </ModalForm>
</template>

<script setup lang="ts">
import type { RoomReservation } from '@/assets/js/types'
import ModalForm from '@/components/ModalForm.vue'
import { defineProps } from 'vue'

interface Emits {
  (e: 'closed'): void;
}

const emit = defineEmits<Emits>()

interface Props {
  reservation: RoomReservation;
  isOpen: boolean;
}

const props = defineProps<Props>()

function generateId (element: string) {
  return `edit-room-reservation-${element}-${props.reservation.id}`
}

function emitClose () {
  emit('closed')
}
</script>

<script lang="ts">
export default {
  name: 'RoomReservationForm',
  components: {},
}
</script>

<style scoped></style>
