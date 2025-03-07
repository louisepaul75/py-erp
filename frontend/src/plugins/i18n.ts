// Vue I18n configuration
import { createI18n } from 'vue-i18n';

// Define messages for each locale
const messages = {
  en: {
    app: {
      title: 'pyERP',
      version: 'Version',
    },
    nav: {
      home: 'Home',
      dashboard: 'Dashboard',
      settings: 'Settings',
      profile: 'Profile',
      logout: 'Logout',
      login: 'Login',
    },
    auth: {
      login: 'Login',
      register: 'Register',
      email: 'Email',
      password: 'Password',
      forgotPassword: 'Forgot Password?',
      rememberMe: 'Remember Me',
    },
    common: {
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      create: 'Create',
      search: 'Search',
      loading: 'Loading...',
      noResults: 'No results found',
    },
  },
  de: {
    app: {
      title: 'pyERP',
      version: 'Version',
    },
    nav: {
      home: 'Startseite',
      dashboard: 'Dashboard',
      settings: 'Einstellungen',
      profile: 'Profil',
      logout: 'Abmelden',
      login: 'Anmelden',
    },
    auth: {
      login: 'Anmelden',
      register: 'Registrieren',
      email: 'E-Mail',
      password: 'Passwort',
      forgotPassword: 'Passwort vergessen?',
      rememberMe: 'Angemeldet bleiben',
    },
    common: {
      save: 'Speichern',
      cancel: 'Abbrechen',
      delete: 'Löschen',
      edit: 'Bearbeiten',
      create: 'Erstellen',
      search: 'Suchen',
      loading: 'Lädt...',
      noResults: 'Keine Ergebnisse gefunden',
    },
  },
};

// Create i18n instance
export default createI18n({
  legacy: false, // Use Composition API
  locale: 'en', // Default locale
  fallbackLocale: 'en', // Fallback locale
  messages,
}); 