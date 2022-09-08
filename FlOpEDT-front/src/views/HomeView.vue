<template>
  <main class="text-center">
    You are in department {{ department }}.
  </main>
</template>

<script setup lang="ts">

import { apiKey, requireInjection } from '@/assets/js/keys'
import { getDepartment } from '@/main'

const api = requireInjection(apiKey)

const department = getDepartment()

</script>
