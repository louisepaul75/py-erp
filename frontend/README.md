# pyERP Frontend

This directory contains the Vue.js frontend for the pyERP system. It's built with Vue 3, TypeScript, and Vite for a modern, type-safe, and fast development experience.

## Setup

### Prerequisites

- Node.js 20.x (recommended) - Node.js 23.x has compatibility issues with some dependencies
  - Specifically, the `@builder.io/sdk-vue` package depends on `isolated-vm`, which fails to compile with Node.js 23.x due to C++20 compatibility issues
- npm 10.x or later

We recommend using [nvm (Node Version Manager)](https://github.com/nvm-sh/nvm) to manage your Node.js versions:

```bash
# Install nvm (if not already installed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Install and use Node.js 20.x
nvm install 20
nvm use 20
```

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start the development server
npm run dev
```

The development server will run on port 3000 by default. It's configured to work with the Django backend running on port 8050.

### Production Build

```bash
# Build for production
npm run build
```

The production build will be output to the `dist` directory, which can be served by the Django backend.

## Architecture

The frontend is organized into the following structure:

- `src/` - Source code
  - `assets/` - Static assets (images, fonts, etc.)
  - `components/` - Reusable Vue components
  - `router/` - Vue Router configuration
  - `services/` - API and other services
  - `store/` - Pinia stores for state management
  - `utils/` - Utility functions
  - `views/` - Page components

## Asset Handling

The frontend includes utilities for handling static assets, particularly images, in a consistent way across different deployment environments.

### Asset Utilities

Located in `src/utils/assetUtils.ts`, these utilities provide:

- **`getStaticAssetUrl(path)`**: Constructs the correct URL for static assets based on the current environment
- **`getNoImageUrl()`**: Returns the URL to the no-image placeholder
- **`getValidImageUrl(imageObj)`**: Validates image URLs and provides fallbacks
- **`handleImageError(event)`**: Event handler for image loading errors

### Usage

```vue
<script setup lang="ts">
import { getValidImageUrl, handleImageError, getNoImageUrl } from '@/utils/assetUtils';

// In your component logic
const getProductImage = (product) => {
  if (product.primary_image) {
    return getValidImageUrl(product.primary_image);
  }
  return getNoImageUrl();
};
</script>

<template>
  <!-- In your template -->
  <img :src="getProductImage(product)" @error="handleImageError" />
</template>
```

### Environment Detection

The asset utilities work in conjunction with the API service to determine the correct base URL based on the deployment environment:

- Checks localStorage for any manually set URL
- Detects if running on specific IP addresses
- Detects if running on localhost
- Falls back to environment variables or window.location.origin

## Integration with Django

The frontend is integrated with the Django backend in two ways:

1. **Development Mode**: In development, the Vue.js dev server runs on port 3000, and the Django template loads the application from this server.

2. **Production Mode**: In production, the Vue.js application is built and served as static files by the Django server.

### Development Mode Integration

The Django template (`pyerp/templates/base/vue_base.html`) includes the following code to load the Vue.js application from the development server:

```html
{% if not debug %}
    <!-- Production mode - load built assets -->
    {% if vue_manifest %}
        <script type="module" src="{% static vue_manifest.main.file %}"></script>
        {% for css in vue_manifest.main.css %}
            <link rel="stylesheet" href="{% static css %}">
        {% endfor %}
    {% endif %}
{% else %}
    <!-- Development mode - connect to Vite dev server -->
    <script type="module">
        // During development, this connects to the Vite dev server for HMR
        import { createApp } from 'http://localhost:3000/@vite/client';

        // Load main entry from Vite dev server
        import('http://localhost:3000/src/main.ts');
    </script>
{% endif %}
```

## Common Issues and Troubleshooting

### Blank Page on localhost:8050 or localhost:3000

If you see a blank page when accessing the application, check the following:

1. **Mount Point Mismatch**: Ensure that the mount point in `main.ts` matches the element ID in the HTML template:
   - Django template (`vue_base.html`) has `<div id="vue-app"></div>` as the mount point
   - Vue.js frontend (`index.html`) has `<div id="vue-app"></div>` as the mount point
   - Vue.js application (`main.ts`) should mount to the correct element: `app.mount('#vue-app')`

2. **Static Directory Missing**: Ensure that the static directory exists:
   ```bash
   mkdir -p pyerp/static
   ```

3. **Debug Flag Not Passed**: Make sure the debug flag is correctly passed to the template context:
   ```python
   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['debug'] = settings.DEBUG
       # ... rest of the method
   ```

4. **Template Inheritance**: Ensure that the base.html template extends the vue_base.html template:
   ```html
   {% extends "base/vue_base.html" %}
   ```

5. **Browser Console Errors**: Check the browser console for JavaScript errors that might prevent the application from loading.

### Authentication Issues

If you're experiencing authentication issues, check the following:

1. **Token Endpoints**: Ensure that the token endpoints in `auth.ts` match the proxy configuration in `vite.config.ts`.

2. **CORS Configuration**: Verify that the CORS settings in Django allow requests from the Vue.js development server.

3. **JWT Configuration**: Check that the JWT signing key is properly configured in the Django settings.

## Development Guidelines

### Code Style

- Follow the Vue.js Style Guide (Priority A and B rules)
- Use TypeScript for all new code
- Use Composition API with `<script setup>` syntax
- Use Pinia for state management
- Use Vue Router for navigation

### Component Structure

- Use single-file components (SFCs)
- Keep components small and focused
- Use props and events for component communication
- Use slots for component composition

### Testing

- Write unit tests for complex components and services
- Use Vue Test Utils for component testing
- Use Jest for unit testing

## Resources

- [Vue.js Documentation](https://vuejs.org/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
