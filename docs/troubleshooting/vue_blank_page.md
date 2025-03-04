# Vue.js Blank Page Troubleshooting

## Overview

This document tracks the progress and findings related to troubleshooting the blank page issue when accessing the Vue.js frontend on localhost:8050 and localhost:3000.

## Issue Description

When accessing the Vue.js frontend on localhost:8050 (Django server) or localhost:3000 (Vue.js dev server), only a blank white page is displayed with no content or errors visible in the UI.

## Investigation Steps

### 1. Initial Setup Verification

- **Docker Container Status**: Confirmed that the Docker container `docker-pyerp-1` is running with ports 8050, 3000, and 6379 properly mapped.
- **Server Logs**: Examined Django server logs which showed successful API requests for authentication and profile data.
- **Static Files Warning**: Identified a warning about missing static directory: `(staticfiles.W004) The directory '/app/pyerp/static' in the STATICFILES_DIRS setting does not exist.`

### 2. Static Files Configuration

- **Missing Directory**: Created the missing static directory in the Docker container:
  ```bash
  docker exec docker-pyerp-1 mkdir -p /app/pyerp/static
  ```
- **Static Files Settings**: Verified that the Django settings have the correct static files configuration:
  ```python
  STATIC_URL = 'static/'
  STATIC_ROOT = BASE_DIR / 'staticfiles'
  STATICFILES_DIRS = [
      BASE_DIR / 'pyerp' / 'static',
  ]
  ```

### 3. Vue.js Configuration

- **Template Mount Point**: Identified a discrepancy between the Vue.js mount point in the Django template and the Vue.js application:
  - Django template (`vue_base.html`) had `<div id="app"></div>` as the mount point
  - Vue.js frontend (`index.html`) had `<div id="vue-app"></div>` as the mount point
  - Vue.js application (`main.ts`) was mounting to `#vue-app`

- **Fixed Mount Point**: Updated all mount points to use `#vue-app` consistently across:
  ```typescript
  // In main.ts - Mount the app to the DOM
  app.mount('#vue-app');
  ```
  ```html
  <!-- In vue_base.html -->
  <div id="vue-app"></div>
  ```
  ```html
  <!-- In index.html -->
  <div id="vue-app"></div>
  ```

### 4. Development Mode Configuration

- **Vue.js Dev Server**: Verified that the Vue.js development server is running on port 3000 as expected.
- **Django Template**: Confirmed that the Django template correctly loads the Vue.js application from the development server when in debug mode:
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

- **Debug Flag**: Ensured that the debug flag is correctly passed to the template context in the Django view:
  ```python
  def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      
      # Explicitly pass debug flag to template
      context['debug'] = settings.DEBUG
      
      # ... rest of the method
  ```

### 5. Header Styling Issue

- **Old Blue Header**: Identified that the old blue header was still showing instead of the new Vue.js header.
- **Template Inheritance Issue**: Discovered that templates extending "base.html" were using the Django styling instead of the Vue.js styling.
- **Missing base.html**: Created a base.html template that extends the vue_base.html template to ensure all templates use the Vue.js styling:
  ```html
  {% extends "base/vue_base.html" %}
  ```

## Current Status

The issue has been identified as a combination of mount point mismatches and template inheritance issues. The fix has been implemented by:
1. Ensuring all mount points consistently use `#vue-app`
2. Creating a base.html template that extends vue_base.html to ensure all templates use the Vue.js styling

## Next Steps

1. Restart the Docker container to apply the changes
2. Verify that the Vue.js application loads correctly on both localhost:8050 and localhost:3000
3. If the issue persists, check browser console logs for any JavaScript errors
4. Consider adding more detailed error handling and logging in the Vue.js application

## Lessons Learned

1. Ensure consistency between mount points in Django templates and Vue.js application code
2. Verify that static directories exist before starting the application
3. Check that the debug flag is correctly passed to the template context
4. Monitor both Django and Vue.js logs for errors during startup
5. When integrating Vue.js with Django, ensure all configuration points are aligned
6. Pay attention to template inheritance and how it affects the rendering of the application 