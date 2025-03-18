<template>
  <v-btn
    :color="color"
    :variant="variant"
    :size="size"
    :disabled="disabled"
    @click="$emit('click')"
    class="app-button"
    v-bind="$attrs"
  >
    <v-icon v-if="prependIcon" :icon="prependIcon" start class="mr-1" />
    <v-icon v-if="icon && !$slots.default" :icon="icon" />
    <span v-else><slot></slot></span>
    <v-icon v-if="appendIcon" :icon="appendIcon" end class="ml-1" />
  </v-btn>
</template>

<script setup lang="ts">
defineProps({
  color: {
    type: String,
    default: 'primary'
  },
  variant: {
    type: String,
    default: 'elevated',
    validator: (value: string) => ['elevated', 'text', 'outlined', 'plain', 'tonal'].includes(value)
  },
  icon: {
    type: String,
    default: ''
  },
  prependIcon: {
    type: String,
    default: ''
  },
  appendIcon: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'default',
    validator: (value: string) => ['x-small', 'small', 'default', 'large', 'x-large'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

defineEmits(['click']);
</script>

<style scoped>
.app-button {
  font-weight: 500;
}

.app-button :deep(.v-btn__content) {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
</style> 