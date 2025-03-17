// Vuetify configuration
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { md3 } from 'vuetify/blueprints';
import '@mdi/font/css/materialdesignicons.css';
import 'vuetify/styles';

// Define custom theme based on the existing color scheme
export default createVuetify({
  blueprint: md3,
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#d2bc9b',
          'primary-darken-1': '#c0aa89',
          secondary: '#343a40',
          'secondary-darken-1': '#212529',
          background: '#f8f9fa',
          surface: '#ffffff',
          error: '#dc3545',
          info: '#0dcaf0',
          success: '#198754',
          warning: '#ffc107',
          'on-primary': '#ffffff',
          'on-secondary': '#ffffff',
          'on-surface': '#212529',
          'on-background': '#212529'
        }
      },
      dark: {
        dark: true,
        colors: {
          primary: '#d2bc9b',
          'primary-darken-1': '#c0aa89',
          secondary: '#343a40',
          'secondary-darken-1': '#212529',
          background: '#121212',
          surface: '#212121',
          error: '#dc3545',
          info: '#0dcaf0',
          success: '#198754',
          warning: '#ffc107',
          'on-primary': '#ffffff',
          'on-secondary': '#ffffff',
          'on-surface': '#ffffff',
          'on-background': '#ffffff'
        }
      }
    }
  }
});
