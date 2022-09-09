<template>
  <div class="container">
    <div class="row"> <!-- Header -->
      <div v-for="day in days" class="col col-day">
        <div class="row border-end border-bottom border-top border-dark" :class="{'border-start': day === days[0]}">
          <div>{{ day.name }} {{ day.date }}</div>
        </div>
        <div v-for="slot in slots[day.date]">
          <CalendarSlot>{{ slot }}</CalendarSlot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Time } from '@/assets/js/types'
import CalendarSlot from '@/components/calendar/CalendarSlot.vue'
import { defineProps } from 'vue'

interface Props {
  days: {
    [index: number]: {
      name: string,
      date: string,
    }
  },
  slots: {
    [index: number]: Array<{
      startTime: Time,
      endTime: Time,
      content: string,
    }>
  },
}

const props = defineProps<Props>()

//const days = ref(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

</script>

<script lang="ts">
export default {
  name: 'Calendar',
  components: {},
}

</script>

<style scoped>
.col-day {
  text-align: center;
}
</style>
