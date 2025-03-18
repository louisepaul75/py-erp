<template>
  <v-textarea
    :label="label"
    :placeholder="placeholder"
    :rows="rows"
    :auto-grow="autoGrow"
    :prepend-icon="prependIcon"
    :append-icon="appendIcon"
    :required="required"
    :disabled="disabled"
    :readonly="readonly"
    :clearable="clearable"
    :hide-details="hideDetails"
    :density="density"
    :variant="variant"
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
  ></v-textarea>
</template>

<script setup lang="ts">
defineProps({
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  rows: {
    type: [String, Number],
    default: 3
  },
  autoGrow: {
    type: Boolean,
    default: false
  },
  prependIcon: {
    type: String,
    default: ''
  },
  appendIcon: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  clearable: {
    type: Boolean,
    default: false
  },
  hideDetails: {
    type: Boolean,
    default: false
  },
  density: {
    type: String,
    default: 'default',
    validator: (value: string) => ['default', 'comfortable', 'compact'].includes(value)
  },
  variant: {
    type: String,
    default: 'outlined',
    validator: (value: string) => ['filled', 'outlined', 'plain', 'underlined', 'solo'].includes(value)
  },
  modelValue: {
    type: String,
    default: ''
  }
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
/* Add custom styles if needed */
</style> 