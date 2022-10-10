<template>
    <div
        ref="modalRef"
        class="modal fade"
        data-bs-backdrop="static"
        data-bs-keyboard="false"
        tabindex="-1"
        aria-labelledby="modalTitleLabel"
        aria-hidden="true"
    >
        <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 id="modalTitleLabel" class="modal-title">Reservation deletion</h5>
                    <button type="button" class="btn-close" aria-label="Close" @click.stop="cancel"></button>
                </div>
                <div class="modal-body">
                    <span>
                        You are about to remove a reservation related to a periodicity, would you want to remove only
                        this reservation, all the related reservations or this one and all the next?
                    </span>
                </div>
                <div class="modal-footer">
                    <slot name="buttons">
                        <button type="button" class="btn btn-secondary" @click.stop="cancel">Cancel</button>
                        <button type="button" class="btn btn-primary" @click.stop="confirmCurrent">
                            Just this one
                        </button>
                        <button type="button" class="btn btn-primary" @click.stop="confirmAll">All</button>
                        <button type="button" class="btn btn-primary" @click.stop="confirmFuture">
                            This one and all the next
                        </button>
                    </slot>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { Modal } from 'bootstrap'
import { onMounted, ref, watch } from 'vue'
import { DialogInterface, RoomReservation } from '@/assets/js/types'

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
const modalRef = ref()

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

watch(
    () => props.isOpen,
    (newValue) => {
        if (!isMounted.value) {
            return
        }
        const modal = Modal.getOrCreateInstance(modalRef.value)
        if (!modal) {
            return
        }
        if (newValue) {
            open(modal)
        } else {
            close(modal)
        }
    }
)

function open(modal: Modal) {
    modal.show()
}

function close(modal: Modal) {
    modal.hide()
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
