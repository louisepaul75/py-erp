// Vue I18n configuration
import { createI18n } from 'vue-i18n';

// Import language files
import enCommon from '../i18n/locales/en';
import deCommon from '../i18n/locales/de';
import csCommon from '../i18n/locales/cs';

// Define messages for each locale
const messages = {
  en: {
    ...enCommon,
    app: {
      title: 'pyERP',
      version: 'Version',
    },
    nav: {
      home: 'Home',
      dashboard: 'Dashboard',
      dashboard_2: 'Dashboard 2',
      settings: 'Settings',
      profile: 'Profile',
      logout: 'Logout',
      login: 'Login',
      products: 'Products',
      sales: 'Sales',
      inventory: 'Inventory',
      production: 'Production',
      test: 'Test Page'
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
      profile: 'Profile',
      settings: 'Settings',
      adminDashboard: 'Admin Dashboard',
      lightMode: 'Light Mode',
      darkMode: 'Dark Mode',
      language: 'Language',
      logout: 'Logout',
      login: 'Login'
    },
  },
  de: {
    ...deCommon,
    app: {
      title: 'pyERP',
      version: 'Version',
    },
    nav: {
      home: 'Startseite',
      dashboard: 'Dashboard',
      dashboard_2: 'Dashboard 2',
      settings: 'Einstellungen',
      profile: 'Profil',
      logout: 'Abmelden',
      login: 'Anmelden',
      products: 'Produkte',
      sales: 'Verkäufe',
      inventory: 'Lagerbestand',
      production: 'Produktion',
      test: 'Testseite'
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
      profile: 'Profil',
      settings: 'Einstellungen',
      adminDashboard: 'Admin-Dashboard',
      lightMode: 'Heller Modus',
      darkMode: 'Dunkler Modus',
      language: 'Sprache',
      logout: 'Abmelden',
      login: 'Anmelden'
    },
  },
  cs: {
    ...csCommon,
    app: {
      title: 'pyERP',
      version: 'Verze',
    },
    nav: {
      home: 'Domů',
      dashboard: 'Nástěnka',
      dashboard_2: 'Nástěnka 2',
      settings: 'Nastavení',
      profile: 'Profil',
      logout: 'Odhlásit',
      login: 'Přihlásit',
      products: 'Produkty',
      sales: 'Prodej',
      inventory: 'Sklad',
      production: 'Výroba',
      test: 'Testovací stránka'
    },
    auth: {
      login: 'Přihlásit',
      register: 'Registrovat',
      email: 'E-mail',
      password: 'Heslo',
      forgotPassword: 'Zapomenuté heslo?',
      rememberMe: 'Zapamatovat si mě',
    },
    common: {
      save: 'Uložit',
      cancel: 'Zrušit',
      delete: 'Odstranit',
      edit: 'Upravit',
      create: 'Vytvořit',
      search: 'Hledat',
      loading: 'Načítání...',
      noResults: 'Žádné výsledky nebyly nalezeny',
      profile: 'Profil',
      settings: 'Nastavení',
      adminDashboard: 'Administrátorská nástěnka',
      lightMode: 'Světlý režim',
      darkMode: 'Tmavý režim',
      language: 'Jazyk',
      logout: 'Odhlásit',
      login: 'Přihlásit'
    },
  }
};

// Create i18n instance
const i18n = createI18n({
  legacy: false,
  locale: 'en', // set default locale
  fallbackLocale: 'en',
  messages,
  globalInjection: true,
  silentTranslationWarn: true,
  silentFallbackWarn: true
});

export default i18n; 