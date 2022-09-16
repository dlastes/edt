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
          <h5 id="modalTitleLabel" class="modal-title">
            <slot name="title"></slot>
          </h5>
          <button
              type="button"
              class="btn-close"
              aria-label="Close"
              @click.stop="close"
          ></button>
        </div>
        <div class="modal-body">
          <slot name="body"></slot>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click.stop="close">
            Cancel
          </button>
          <button type="button" class="btn btn-primary" @click.stop="close">
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Modal } from 'bootstrap'
import { defineProps, onMounted, ref, watch } from 'vue'

interface Emits {
  (e: 'closed'): void;
}

const emit = defineEmits<Emits>()

interface Props {
  isOpen: boolean;
}

const props = defineProps<Props>()

const modalRef = ref()
const isMounted = ref(false)

watch(
    () => props.isOpen,
    (newValue, oldValue) => {
      if (newValue) {
        open()
      }
    }
)

function open () {
  if (!isMounted.value) {
    return
  }
  const modal = Modal.getOrCreateInstance(modalRef.value)
  if (!modal) {
    return
  }
  modal.show()
}

function close () {
  if (!isMounted.value) {
    return
  }
  const modal = Modal.getOrCreateInstance(modalRef.value)
  if (!modal) {
    return
  }
  modal.hide()
  emit('closed')
}

onMounted(() => {
  isMounted.value = true
})
</script>

<script lang="ts">
export default {
  name: 'ModalForm',
  components: {},
}
</script>

<style scoped></style>
