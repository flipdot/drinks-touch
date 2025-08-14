<template>
  <div>
    <NuxtRouteAnnouncer />
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
useHead({
  titleTemplate: (titleChunk) =>
    `${titleChunk ? `${titleChunk} -` : ''}Getränkescanner`,
})
</script>
