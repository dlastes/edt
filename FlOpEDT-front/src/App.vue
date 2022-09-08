<template>
  <header>
    <h1 class="border-solid border-bottom">HEADER</h1>
    <ul>
      <li>
        <router-link :to="{name:'home'}">Home</router-link>
      </li>
      <li>
        <router-link :to="{name:'room-reservation'}">Room Reservation</router-link>
      </li>
    </ul>
  </header>

  <RouterView/>

  <footer>
    <h1 class="border-solid border-top">FOOTER</h1>
  </footer>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>

</style>
