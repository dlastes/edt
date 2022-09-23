<template>
    <PopperComponent
        :id="props.data.id"
        class="frame"
        :show="isContextMenuOpened"
        :style="props.data.displayStyle"
        @click="onClick"
    >
        <div class="course">
            <div class="row">
                <p class="col-xl-6">{{ props.data.course.course.module.abbrev }}</p>
                <p class="col-xl-6">{{ props.data.department }}</p>
                <p class="col-xl-6">{{ props.data.course.tutor }}</p>
                <p class="col-xl-6">{{ roomName }}</p>
            </div>
        </div>
        <template #content></template>
    </PopperComponent>
</template>

<script setup lang="ts">
import type { CalendarScheduledCourseSlotData, CalendarSlotInterface } from '@/assets/js/types'
import { computed, onMounted, ref } from 'vue'

interface Props {
    data: CalendarScheduledCourseSlotData
}

const props = defineProps<Props>()

interface Emits {
    (e: 'interface', id: string, slotInterface: CalendarSlotInterface): void
}

const emit = defineEmits<Emits>()

const isContextMenuOpened = ref<boolean>(false)
const roomName = computed(() => {
    const r = props.data.rooms[props.data.course.room]
    return r?.name
})

function onClick() {
    console.log(props.data.title)
}

function openContextMenu(): boolean {
    // No interaction with courses
    return false
}

function closeContextMenu() {
    // No interaction
}

function emitInterface() {
    emit('interface', props.data.id, {
        openContextMenu: openContextMenu,
        closeContextMenu: closeContextMenu,
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
.frame {
    border-radius: 5px;
    width: 100%;
}

p {
    font-size: 0.75em;
    font-weight: bold;
    margin: 0;
}

.course {
    overflow: hidden;
    height: 100%;
}
</style>
