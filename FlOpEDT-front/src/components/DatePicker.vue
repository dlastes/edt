<template>
  <div class="row"> <!-- Date picker -->
    <Datepicker v-model="selectDate" :locale="locale" inline weekNumbers weekPicker :enableTimePicker="false"
                autoApply
                showNowButton
                :nowButtonLabel="nowLabel"/>
  </div>
</template>

<script setup lang="ts">
import type { Ref } from 'vue'
import { computed, defineEmits, defineProps, onMounted, ref, watchEffect } from 'vue'

interface Props {
  week: number,
  year: number,
}

const props = defineProps<Props>()

interface Emits {
  (e: 'update:week', value: number): void,

  (e: 'update:year', value: number): void,
}

const emits = defineEmits<Emits>()

const selectDate: Ref<Array<Date>> = ref([])

watchEffect(() => {
  let refDate = selectDate.value[0]
  if (!refDate) {
    return 1
  }
  let startDate = new Date(refDate.getFullYear(), 0, 1)
  let days = Math.floor((refDate.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000))

  emits('update:week', Math.ceil(days / 7))
  emits('update:year', refDate.getFullYear())
})

const locale = ref('fr')

const nowLabel = ref('Aujourd\'hui')

onMounted(() => {

})

</script>

<script lang="ts">
export default {
  name: 'DatePicker',
  components: {},
}

</script>

<style scoped>

</style>
