import { createApp } from 'vue';
import App from './App.vue';

// Create and mount the Vue application
const app = createApp(App);

// Mount the app to the DOM
app.mount('#vue-app');

// Make the app available in development mode for debugging
if (import.meta.env.DEV) {
  window.app = app;
} 