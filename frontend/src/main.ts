import { createApp, App as VueApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';
import i18n from './plugins/i18n';

// Declare app property on Window interface
declare global {
  interface Window {
    app: VueApp<Element>;
  }
}

// Create and mount the Vue application
const app = createApp(App);

// Use Pinia for state management
const pinia = createPinia();
app.use(pinia);

// Use the router
app.use(router);

// Use Vuetify
app.use(vuetify);

// Use i18n
app.use(i18n);

// Mount the app to the DOM
app.mount('#vue-app');

// Make the app available in development mode for debugging
if (import.meta.env.DEV) {
  window.app = app;
}
