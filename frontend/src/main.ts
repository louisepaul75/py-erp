import { createApp, App as VueApp } from 'vue';
import App from './App.vue';
import router from './router';

// Declare app property on Window interface
declare global {
  interface Window {
    app: VueApp<Element>;
  }
}

// Create and mount the Vue application
const app = createApp(App);

// Use the router
app.use(router);

// Mount the app to the DOM
app.mount('#vue-app');

// Make the app available in development mode for debugging
if (import.meta.env.DEV) {
  window.app = app;
} 