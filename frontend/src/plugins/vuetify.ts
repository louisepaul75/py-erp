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
          error: '#B00020',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00'
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
          error: '#CF6679',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00'
        }
      }
    }
  }
});
