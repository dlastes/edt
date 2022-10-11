<template>
    <ModalDialog :is-open="props.isOpen">
        <template #title>Reservation deletion</template>
        <template #body>
            <span>
                You are about to remove a reservation related to a periodicity, would you want to remove only this
                reservation, all the related reservations or this one and all the next?
            </span>
        </template>
        <template #buttons>
            <button type="button" class="btn btn-secondary" @click.stop="cancel">Cancel</button>
            <button type="button" class="btn btn-primary" @click.stop="confirmCurrent">Just this one</button>
            <button type="button" class="btn btn-primary" @click.stop="confirmAll">All</button>
            <button type="button" class="btn btn-primary" @click.stop="confirmFuture">This one and all the next</button>
        </template>
    </ModalDialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RoomReservation } from '@/assets/js/types'
import ModalDialog from '@/components/ModalDialog.vue'

interface Props {
    isOpen: boolean
    reservation: RoomReservation
    onCancel: () => void
    onConfirmCurrent: (reservation: RoomReservation) => void
    onConfirmAll: (reservation: RoomReservation) => void
    onConfirmFuture: (reservation: RoomReservation) => void
}

const props = defineProps<Props>()

const isMounted = ref(false)

function cancel() {
    props.onCancel()
}

function confirmCurrent() {
    props.onConfirmCurrent(props.reservation)
}

function confirmAll() {
    props.onConfirmAll(props.reservation)
}

function confirmFuture() {
    props.onConfirmFuture(props.reservation)
}

onMounted(() => {
    isMounted.value = true
})
</script>

<script lang="ts">
export default {
    name: 'DeletePeriodicReservationDialog',
    components: {},
}
</script>

<style scoped></style>
