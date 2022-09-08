<template>

</template>

<script setup lang="ts">
import type { Time } from '@/assets/js/types'
import { defineProps } from 'vue'

interface Props {
  time: Time,
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
