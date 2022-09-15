<template>
  <Popper class="frame" :show="isContextMenuOpened" :style="props.data.displayStyle"
          :id="props.data.id">
    <div @click="onClick" class="course">
      <p class="m-0">{{ props.data.course.course.module.abbrev }}</p>
      <p class="m-0">{{ props.data.course.tutor }}</p>
      <p class="m-0">{{ props.data.department }}</p>
    </div>
    <template #content>
      <CalendarSlotContextMenu :slot="props.data"></CalendarSlotContextMenu>
    </template>
  </Popper>
</template>

<script setup lang="ts">
import type { CalendarScheduledCourseSlotData, CalendarSlotInterface } from '@/assets/js/types'
import CalendarSlotContextMenu from '@/components/calendar/CalendarSlotContextMenu.vue'
import { onMounted, ref } from 'vue'

interface Props {
  data: CalendarScheduledCourseSlotData
}

const props = defineProps<Props>()

interface Emits {
  (e: 'interface', id: string, slotInterface: CalendarSlotInterface): void
}

const emit = defineEmits<Emits>()

const isContextMenuOpened = ref<boolean>(false)

function onClick () {
  console.log(props.data.title)
}

function openContextMenu (): boolean {
  // No interaction with courses
  return false
}

function closeContextMenu () {

}

function emitInterface () {
  emit('interface', props.data.id, {
    openContextMenu: openContextMenu,
    closeContextMenu: closeContextMenu
  })
}

onMounted(() => {
  emitInterface()
})

</script>

<script lang="ts">
export default {
  name: 'CalendarScheduledCourseSlot',
  components: {},
}

</script>

<style scoped>
div {
  min-height: 50px;
}

.frame {
  border-radius: 5px;
  width: 100%;
}

p {
  font-size: 0.625em;
  font-weight: bold;
  margin: 0;
}

.course {
  overflow: hidden;
  height: 100%;
}
</style>
