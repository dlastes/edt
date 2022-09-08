<template>
  <div class="container">
    <div class="row"> <!-- Days header -->

    </div>
    <div class="row"> <!-- Grid -->
      <div class="container">
        <div class="col"> <!-- Hours -->

        </div>
        <div class="col" v-for="day in days">
          // TODO
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, ref } from 'vue'

interface Props {
}

const props = defineProps<Props>()

const days = ref(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

</script>

<script lang="ts">
export default {
  name: 'Calendar',
  components: {},
}

</script>

<style scoped>

</style>
