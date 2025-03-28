import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";

// Check if we're running on the client side
const isClient = typeof window !== "undefined";

// Define static resources for the 'common' namespace to avoid initial loading delay
export const resources = {
  de: {
    common: {
      "navigation.home": "Home",
      "navigation.products": "Produkte",
      "navigation.sales": "Vertrieb",
      "navigation.production": "Produktion",
      "navigation.inventory": "Lager",
      "navigation.settings": "Einstellungen",
    },
    mutterTab: {
      active: "Aktiv",
      articleNumber: "Artikelnummer",
      delete: "Löschen",
      save: "Speichern",
      confirmDeleteTitle: "Sind Sie sicher?",
      confirmDeleteDescription:
        "Möchten Sie dieses Produkt wirklich entfernen?",
      cancel: "Abbrechen",
      ok: "OK",
      productDetails: "Produktdetails",
      designation: "Bezeichnung",
      description: "Beschreibung",
      dimensions: "Maße & Eigenschaften",
      unit: "Einheit: mm",
      height: "Höhe",
      length: "Länge",
      width: "Breite",
      weight: "Gewicht (g)",
      hanging: "Hängend",
      oneSided: "Einseitig",
      novelty: "Neuheit",
      categories: "Kategorien",
      add: "Hinzufügen",
      remove: "Entfernen",
    },
    settings_system: {
      api_endpoints: "API-Endpunkte",
      automations: "Automatisierungen",
      logs: "Protokolle",
      changes: "Änderungen",
      schedule: "Zeitplan",
      refresh: "Aktualisieren",
      download: "Herunterladen",
      search: "Suchen",
      no_results_found: "Keine Ergebnisse gefunden",
      loading: "Laden",
      loading_endpoints: "Loading endpoints...",
      no_endpoints_found: "No endpoints found",
      actions: "Aktionen",
      status: "Zustand",
      name: "Bezeichnung",
      description: "Beschreibung",
      last_run: "Letzter Lauf",
      last_sync: "Letzte Synchronisierung",
      active: "Aktiv",
      error: "Fehler",
      errors: "Fehler",
      pending: "Ausstehend",
      success: "Erfolg",
      failed: "Fehlgeschlagen",
      stopped: "Gestoppt",
      added: "Hinzugefügt",
      removed: "Entfernt",
      modified: "Geändert",
      cancel: "Abbrechen",
      save: "Speichern",
      search_placeholder: "Endpunkte durchsuchen",
      external_api_endpoints: "Externe API-Endpunkte",
      manage_api_endpoints:
        "Verwalten und Überwachen aller externen API-Integrationen",
      django_erp_automations: "Django ERP-Automatisierungen",
      manage_automations:
        "Verwalten und Planen automatisierter Aufgaben in Ihrem ERP-System",
      view_changes: "Änderungen anzeigen",
      all_changes: "Alle Änderungen",
      added_changes: "Hinzugefügte Änderungen",
      removed_changes: "Entfernte Änderungen",
      modified_changes: "Geänderte Änderungen",
      integration_dashboard: "Integrations-Dashboard",
      view_logs: "Protokolle anzeigen",
      all_logs: "Alle Protokolle",
      error_logs: "Fehlerprotokolle",
      warning_logs: "Warnprotokolle",
      info_logs: "Info-Protokolle",
      schedule_automation: "Automatisierung planen",
      configure_schedule: "Konfigurieren, wann {name} ausgeführt werden soll",
      configure_when: "Konfigurieren, wann",
      should_run: "ausgeführt werden soll",
      daily: "Täglich",
      weekly: "Wöchentlich",
      monthly: "Monatlich",
      custom_schedule: "Benutzerdefinierter Zeitplan",
      custom: "Benutzerdefiniert",
      time: "Zeit",
      day_of_week: "Wochentag",
      day_of_month: "Tag des Monats",
      cron_expression: "Cron-Ausdruck",
      view_all_logs: "Alle Protokolle dafür anzeigen",
      all: "Alle",
      warnings: "Warnungen",
      info: "Info",
      view_all_changes: "Alle Änderungen dafür ansehen",
      download_changes: "nderungen herunterladen",
      loading_changes: "Änderungen werden geladen...",
      no_change: "Keine Änderungen gefunden",
      before: "Vorher",
      after: "Nachher",
      monday: "Montag",
      tuesday: "Dienstag",
      wednesday: "Mittwoch",
      thursday: "Donnerstag",
      friday: "Freitag",
      saturday: "Samstag",
      sunday: "Sonntag",
      save_schedule: "Zeitplan speichern",
      saving: "Speichern...",
      use_cron_syntax:
        "Verwenden Sie Cron-Syntax, um einen benutzerdefinierten Zeitplan zu definieren",
      scheduled: "Geplant", // German
      running: "Läuft",
      loading_automations: "Automatisierungen werden geladen...",
      no_automations_found: "Keine Automatisierungen gefunden",
      search_automations: "Automatisierungen suchen...",
      start: "Starten",
      pause: "Pause",
    },
    settings_currency: {
      // Currency Form
      add_currency: "Neue Währung hinzufügen",
      edit_currency: "Währung bearbeiten",
      add_currency_description: "Fügen Sie eine neue Währung zum System hinzu.",
      edit_currency_description:
        "Bearbeiten Sie die Details der ausgewählten Währung.",
      currency_code: "Währungscode",
      currency_code_description: "Dreistelliger ISO-Währungscode",
      currency_name: "Name",
      currency_name_description: "Vollständiger Name der Währung",
      real_time_rate: "Echtzeit-Kurs",
      real_time_rate_description: "Aktueller Wechselkurs zu Euro (EUR)",
      calculation_rate: "Verrechnungskurs",
      calculation_rate_description: "Interner Verrechnungskurs zu Euro (EUR)",
      fetch_rate_error: "Bitte geben Sie einen gültigen Währungscode ein.",
      fetch_rate_success:
        "Der aktuelle Kurs für {code} wurde erfolgreich abgerufen.",
      fetch_rate_error_message:
        "Der Wechselkurs konnte nicht abgerufen werden.",
      euro_base_currency:
        "Euro (EUR) ist die Basiswährung und hat immer den Kurs 1.0000.",
      save_currency_success: "Währung erfolgreich hinzugefügt.",
      update_currency_success: "Währung erfolgreich aktualisiert.",
      save_currency_error: "Die Währung konnte nicht gespeichert werden.",
      cancel: "Abbrechen",
      save: "Speichern",
      currency_code_length_error:
        "Währungscode muss genau 3 Zeichen lang sein.",
      currency_name_min_length_error:
        "Name muss mindestens 2 Zeichen lang sein.",
      positive_rate_error: "Kurs muss positiv sein.",
      rate_updated: "Kurs aktualisiert.",
      hint: "Hinweis",
      currency_updated: "Währung aktualisiert.",
      currency_added: "Währung hinzugefügt.",
      error: "Fehler",
      the_current_rate_for: "Der aktuelle Kurs für",
      was_successfully_retrieved: "wurde erfolgreich abgerufen",
      is_being_saved: "Wird gespeichert...",

      // Currency List
      search_currency_placeholder: "Währung suchen...",
      refresh: "Aktualisieren",
      no_currencies_found: "Keine Währungen gefunden.",
      loading_data: "Daten werden geladen...",
      actions: "Aktionen",
      last_updated: "Letzte Aktualisierung",
      trend_analysis: "Trendanalyse",
      currencies: "Währungen",
      add_new_currency: "Neue Währung",
      was_successfully_updated: "wurde erfolgreich aktualisiert",
      was_successfully_added: "wurde erfolgreich hinzugefügt",
      all_exchange_rates_refer_to_base_currency:
        "Alle Wechselkurse beziehen sich auf die Basiswährung",
      code: "Code",

      // Delete Currency Dialog
      delete_currency: "Währung löschen",
      delete_currency_description:
        "Sind Sie sicher, dass Sie die Währung {name} ({code}) löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.",
      delete_currency_success: "Währung erfolgreich gelöscht.",
      delete_currency_error: "Die Währung konnte nicht gelöscht werden.",
      deleting: "Wird gelöscht...",
      currency_deleted: "Währung gelöscht",
      delete_confirm:
        "löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.",
      delete: "Löschen",
      context_waraning:
        "useCurrencyContext must be used within a CurrencyProvider",

      // Currency History Chart
      historical_exchange_rates: "Historische Kursdaten",
      select_currency_for_history:
        "Bitte wählen Sie eine Währung aus, um historische Kursdaten anzuzeigen.",
      exchange_rate_trend: "Wechselkursverlauf: {name} ({code})",
      exchange_rate_to_euro: "Wechselkursverlauf im Verhältnis zum Euro (EUR)",
      day: "Tag",
      week: "Woche",
      month: "Monat",
      quarter: "Quartal",
      year: "Jahr",
      chart: "Liniendiagramm",
      table: "Tabelle",
      date: "Datum",
      rate: "Kurs",
      no_history_data: "Keine historischen Daten verfügbar.",
    },
  },
  en: {
    common: {
      "navigation.home": "Home",
      "navigation.products": "Products",
      "navigation.sales": "Sales",
      "navigation.production": "Production",
      "navigation.inventory": "Inventory",
      "navigation.settings": "Settings",
    },
    mutterTab: {
      active: "Active",
      articleNumber: "Article Number",
      delete: "Delete",
      save: "Save",
      confirmDeleteTitle: "Are you sure?",
      confirmDeleteDescription: "Do you really want to delete this product?",
      cancel: "Cancel",
      ok: "OK",
      productDetails: "Product Details",
      designation: "Designation",
      description: "Description",
      dimensions: "Dimensions & Properties",
      unit: "Unit: mm",
      height: "Height",
      length: "Length",
      width: "Width",
      weight: "Weight (g)",
      hanging: "Hanging",
      oneSided: "One-Sided",
      novelty: "Novelty",
      categories: "Categories",
      add: "Add",
      remove: "Remove",
    },
    settings_system: {
      api_endpoints: "API Endpoints",
      automations: "Automations",
      logs: "Logs",
      changes: "Changes",
      schedule: "Schedule",
      refresh: "Refresh",
      download: "Download",
      search: "Search",
      no_results_found: "No results found",
      loading: "Loading",
      loading_endpoints: "Loading endpoints...",
      no_endpoints_found: "No endpoints found",
      actions: "Actions",
      status: "Status",
      name: "Name",
      description: "Description",
      last_run: "Last Run",
      last_sync: "Last Sync",
      active: "Active",
      error: "Error",
      errors: "Errors",
      pending: "Pending",
      success: "Success",
      failed: "Failed",
      stopped: "Stopped",
      added: "Added",
      removed: "Removed",
      modified: "Modified",
      cancel: "Cancel",
      save: "Save",
      search_placeholder: "Search endpoints...",
      external_api_endpoints: "External API Endpoints",
      manage_api_endpoints: "Manage and monitor all external API integrations",
      django_erp_automations: "Django ERP Automations",
      manage_automations:
        "Manage and schedule automated tasks running on your ERP system",
      view_changes: "View Changes",
      all_changes: "All Changes",
      added_changes: "Added Changes",
      removed_changes: "Removed Changes",
      modified_changes: "Modified Changes",
      integration_dashboard: "Integration Dashboard",
      view_logs: "View Logs",
      all_logs: "All Logs",
      error_logs: "Error Logs",
      warning_logs: "Warning Logs",
      info_logs: "Info Logs",
      schedule_automation: "Schedule Automation",
      configure_schedule: "Configure when {name} should run",
      configure_when: "Configure when",
      should_run: "should run",
      daily: "Daily",
      weekly: "Weekly",
      monthly: "Monthly",
      custom_schedule: "Custom Schedule",
      custom: "Custom",
      time: "Time",
      day_of_week: "Day of Week",
      day_of_month: "Day of Month",
      cron_expression: "Cron Expression",
      view_all_logs: "View all logs for this",
      all: "All",
      warnings: "Warnings",
      info: "Info",
      view_all_changes: "View all changes for this",
      download_changes: "Download changes",
      loading_changes: "Loading Changes...",
      no_change: "No changes found",
      before: "Before",
      after: "After",
      monday: "Monday",
      tuesday: "Tuesday",
      wednesday: "Wednesday",
      thursday: "Thursday",
      friday: "Friday",
      saturday: "Saturday",
      sunday: "Sunday",
      save_schedule: "Save Schedule",
      saving: "Saving...",
      use_cron_syntax: "Use cron syntax to define a custom schedule",
      scheduled: "Scheduled", // English
      running: "Running",
      loading_automations: "Loading automations...",
      no_automations_found: "No automations found",
      search_automations: "Search automations...",
      start: "Start", // English
      pause: "Pause",
    },
    settings_currency: {
      // Currency Form
      add_currency: "Add Currency",
      edit_currency: "Edit Currency",
      add_currency_description: "Add a new currency to the system.",
      edit_currency_description: "Edit the details of the selected currency.",
      currency_code: "Currency Code",
      currency_code_description: "Three-letter ISO currency code",
      currency_name: "Name",
      currency_name_description: "Full name of the currency",
      real_time_rate: "Real-Time Rate",
      real_time_rate_description: "Current exchange rate to Euro (EUR)",
      calculation_rate: "Calculation Rate",
      calculation_rate_description: "Internal calculation rate to Euro (EUR)",
      fetch_rate_error: "Please enter a valid currency code.",
      fetch_rate_success:
        "The current rate for {code} was successfully retrieved.",
      fetch_rate_error_message: "The exchange rate could not be retrieved.",
      euro_base_currency:
        "Euro (EUR) is the base currency and always has a rate of 1.0000.",
      save_currency_success: "Currency added successfully.",
      update_currency_success: "Currency updated successfully.",
      save_currency_error: "The currency could not be saved.",
      cancel: "Cancel",
      save: "Save",
      currency_code_length_error:
        "Currency code must be exactly 3 characters long.",
      currency_name_min_length_error:
        "Name must be at least 2 characters long.",
      positive_rate_error: "Rate must be positive.",
      currency_updated: "Currency updated successfully.",
      currency_added: "Currency added successfully.",
      hint: "Hint",
      rate_updated: "Rate updated successfully.",
      error: "Error",
      the_current_rate_for: "The current rate for",
      was_successfully_retrieved: "was successfully retrieved",
      is_being_saved: "Is being saved...",

      // Currency List
      search_currency_placeholder: "Search currency...",
      refresh: "Refresh",
      no_currencies_found: "No currencies found.",
      loading_data: "Loading data...",
      actions: "Actions",
      last_updated: "Last Updated",
      trend_analysis: "Trend Analysis",
      currencies: "Currencies",
      add_new_currency: "New Currency",
      was_successfully_updated: "was successfully updated",
      was_successfully_added: "was successfully added",
      all_exchange_rates_refer_to_base_currency:
        "All exchange rates refer to the base currency",
      code: "Code",

      // Delete Currency Dialog
      delete_currency: "Delete Currency",
      delete_currency_description:
        "Are you sure you want to delete the currency {name} ({code})? This action cannot be undone.",
      delete_currency_success: "Currency deleted successfully.",
      delete_currency_error: "The currency could not be deleted.",
      deleting: "Deleting...",
      currency_deleted: "Currency deleted",
      delete_confirm:
        "Do you want to delete this? This action cannot be undone.",
      delete: "Delete",
      context_waraning:
        "useCurrencyContext muss innerhalb eines CurrencyProviders verwendet werden.",

      // Currency History Chart
      historical_exchange_rates: "Historical Exchange Rates",
      select_currency_for_history:
        "Please select a currency to view historical exchange rates.",
      exchange_rate_trend: "Exchange Rate Trend: {name} ({code})",
      exchange_rate_to_euro: "Exchange rate relative to Euro (EUR)",
      day: "Day",
      week: "Week",
      month: "Month",
      quarter: "Quarter",
      year: "Year",
      chart: "Chart",
      table: "Table",
      date: "Date",
      rate: "Rate",
      no_history_data: "No historical data available.",
    },
  },
};

// Don't initialize i18next on the server
if (isClient) {
  i18n
    // load translations using http (default public/locales)
    .use(Backend)
    // detect user language
    .use(LanguageDetector)
    // pass the i18n instance to react-i18next
    .use(initReactI18next)
    // init i18next
    .init({
      fallbackLng: "de", // default language
      supportedLngs: ["de", "en", "cs"],
      debug: process.env.NODE_ENV === "development",

      interpolation: {
        escapeValue: false, // not needed for react as it escapes by default
      },

      // react-specific options
      react: {
        useSuspense: false, // prevents issues with SSR
      },

      // load translation resources from
      backend: {
        loadPath: "/locales/{{lng}}/{{ns}}.json",
      },

      // Provide static resources for immediate use
      resources,

      defaultNS: "common",
      ns: ["common", "auth", "products", "dashboard", "settings"],

      // Initialize with resources to prevent loading delays
      preload: ["de", "en"],
    });
}

export default i18n;
