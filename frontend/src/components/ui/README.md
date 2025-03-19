# PyERP UI Component Library

This directory contains all reusable UI components for the PyERP application. These components are designed to be consistent with the style guide and provide a unified look and feel across the application.

## Usage

Components can be used in two ways:

### 1. Global Components

All components are registered globally and can be used directly in any Vue component:

```vue
<template>
  <app-button color="primary">Click Me</app-button>
</template>
```

### 2. Import Components

You can also import components individually:

```vue
<template>
  <app-button color="primary">Click Me</app-button>
</template>

<script setup>
import { AppButton } from '@/components/ui';
</script>
```

## Style Guide

All components should follow the style guide defined in the `Components.vue` view. This ensures consistency across the application. When making changes to a component, make sure to update the style guide as well.

## Components

- `AppButton`: A reusable button component with various styles and configurations.
- `AppDataTable`: A searchable data table component with various sizes.
- `AppFilterTable`: A filterable data table component with advanced filtering options.
- `AppServerTable`: A server-side data table component with pagination, sorting, and search.
- `AppIcon`: A reusable icon component with various sizes and colors.
- `AppTextField`: A reusable text field component with various configurations.
- `AppTextarea`: A reusable textarea component for multi-line text input.

## Theme Configuration

The application uses a centralized theme configuration defined in `src/plugins/theme.ts`. This ensures consistent colors, spacing, and other design tokens across the application.

## Adding New Components

1. Create a new component in the `ui` directory.
2. Export the component in the `index.ts` file.
3. Add the component to the style guide in `Components.vue`.
4. Document the component in this README.

## Guidelines

- Keep components simple and focused.
- Use props for configuration.
- Document all props and emits.
- Use the theme configuration for colors, spacing, etc.
- Test components thoroughly.
- Update the style guide when making changes. 