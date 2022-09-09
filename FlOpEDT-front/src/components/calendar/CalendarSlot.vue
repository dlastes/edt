<template>
  <div class="border border-dark">
    <p class="m-0">{{ title }}</p>
    <p class="m-0">
      <slot>CONTENT</slot>
    </p>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

interface Props {
  title: string,
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
