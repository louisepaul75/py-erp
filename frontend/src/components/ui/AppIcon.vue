<template>
  <v-icon
    :icon="icon"
    :color="color"
    :size="size"
    :class="customClass"
  ></v-icon>
</template>

<script setup lang="ts">
defineProps({
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: undefined
  },
  size: {
    type: String,
    default: undefined,
    validator: (value: string) => ['x-small', 'small', 'default', 'large', 'x-large'].includes(value)
  },
  customClass: {
    type: String,
    default: ''
  }
});
</script>

<style scoped>
/* Add custom styles if needed */
</style> 