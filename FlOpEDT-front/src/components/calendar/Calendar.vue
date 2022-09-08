<template>
  <div class="container">
    <div class="row"> <!-- Header -->
      <div v-for="day in days" class="col border-end border-bottom border-top border-dark col-day"
           :class="{'border-start': day === days[0]}">
        <div class="row">
          <div>{{ day.name }} {{ day.date }}</div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

interface Props {
  days: Array<{
    name: string,
    date: string
  }>,
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
