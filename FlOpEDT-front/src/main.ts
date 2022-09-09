import '@/assets/css/bootstrap.min.css'
import '@/assets/css/global.css'
import { api } from '@/assets/js/api'
import '@/assets/js/bootstrap.bundle.min'
import { apiKey, currentWeekKey } from '@/assets/js/keys'
import type { FlopWeek } from '@/assets/js/types'
import CustomDatePicker from '@/components/DatePicker.vue'
import WeekBanner from '@/components/WeekBanner.vue'
import router from '@/router'
import Datepicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import type { Ref } from 'vue'
import { createApp, readonly, ref } from 'vue'
import { useRoute } from 'vue-router'
import App from './App.vue'

const app = createApp(App)

app.use(router)

// Provide the api access
app.provide(apiKey, readonly(api))

// Provide the current week and year
let now = new Date()
let startDate = new Date(now.getFullYear(), 0, 1)
let days = Math.floor((now.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000))
let week = Math.ceil(days / 7)

const currentWeek: Ref<FlopWeek> = ref({
  week: week,
  year: now.getFullYear(),
})
app.provide(currentWeekKey, readonly(currentWeek.value))

export function getDepartment (): string | null {
  let dept = useRoute().params.dept
  if (dept instanceof Array) {
    if (dept.length === 0) {
      return null
    }
    return dept[0]
  }
  return dept
}

app.component('WeekBanner', WeekBanner).component('Datepicker', Datepicker).component('CustomDatePicker', CustomDatePicker)

app.mount('#app')
