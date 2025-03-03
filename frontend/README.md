# pyERP Vue.js Frontend

This directory contains the Vue.js 3.5 frontend for the pyERP application.

## Setup

### Prerequisites

- Node.js (v16+)
- npm (v8+)

### Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start the development server with hot-reload
npm run dev
```

The development server runs on http://localhost:3000.

When running in development mode, use the Django URL `/vue/` which will connect to the Vite dev server automatically.

## Building for Production

```bash
# Build for production
npm run build
```

This will build the Vue.js application and output the files to `../static/vue/`.

## Project Structure

```
frontend/
├── src/                   # Source files
│   ├── assets/            # Static assets
│   ├── components/        # Vue components
│   ├── views/             # Vue views (pages)
│   ├── store/             # Pinia store modules
│   ├── router/            # Vue Router configuration
│   ├── utils/             # Utility functions
│   ├── App.vue            # Root Vue component
│   └── main.ts            # Vue application entry point
├── public/                # Public static assets
├── package.json           # Project dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
└── .eslintrc.cjs          # ESLint configuration
```

## Integration with Django

The Vue.js application integrates with Django in two modes:

1. **Development Mode**: The Django template loads the application from the Vite development server
2. **Production Mode**: The built assets are served from Django's static files

The integration is managed through the `vue_base.html` template and the `VueAppView` view.

## Adding New Components

To create a new component:

1. Create a `.vue` file in the `src/components` directory
2. Import and use the component in your view or other components

Example:

```vue
<!-- src/components/MyComponent.vue -->
<template>
  <div>
    <h2>{{ title }}</h2>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const title = ref('My Component');
</script>
``` 