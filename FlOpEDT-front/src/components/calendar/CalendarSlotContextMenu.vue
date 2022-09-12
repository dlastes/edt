<template>
  <div class="card p-0 m-0">
    <div class="card-body p-1 m-0">
      <div class="btn-group" role="group" aria-label="Slot context menu">
        <button type="button" class="btn btn-primary" onclick="">Edit</button>
        <button type="button" class="btn btn-danger" onclick="">Delete</button>
        <button type="button" class="btn btn-info" onclick="">Duplicate</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CalendarSlotElement } from '@/assets/js/types'
import { defineProps } from 'vue'

interface Props {
  slot: CalendarSlotElement
}

const props = defineProps<Props>()

</script>

<script lang="ts">
export default {
  name: 'CalendarSlotContextMenu',
  components: {},
}
</script>

<style scoped>

</style>
