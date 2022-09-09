<template>
  <div class="card">
    <div class="card-body">
      <h5 class="card-title">Card title</h5>
      <p class="card-text">
        <slot>CONTENT</slot>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

interface Props {

}

const props = defineProps<Props>()

</script>

<script lang="ts">
export default {
  name: 'CalendarSlot',
  components: {},
}

</script>

<style scoped>
div {
  min-height: 50px;
}
</style>
