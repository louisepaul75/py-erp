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
      "navigation.business": "Geschäftsbereich",
      "navigation.employees": "Mitarbeiter",
      "navigation.suppliers": "Lieferanten",
      "navigation.settings": "Einstellungen",
      "navigation.mold_management": "Formenverwaltung",
      "navigation.sales_dashboard": "Verkaufsübersicht",
      "navigation.customers": "Kunden",
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
    mold: {
      // Settings Dialog (used in settings-dialog.tsx)
      settings_dialog_title: "Einstellungen",
      settings_dialog_description: "Verwalten Sie Ihre Legierungen und Tags",
      settings_tab_technologies: "Technologien",
      settings_tab_alloys: "Legierungen",
      settings_tab_tags: "Tags",
      settings_tab_moldSizes: "Formgrößen",

      // Technology Manager (technology-manager.tsx)
      card_title_technologies: "Technologien verwalten",
      card_description_technologies:
        "Hinzufügen, bearbeiten oder entfernen Sie Technologien, die in der Formenproduktion verwendet werden.",
      new_technology_placeholder: "Neuer Technologiename",
      technology_name: "Technologie-Name",
      add_button: "Hinzufügen", // Defined here, reused elsewhere
      error_loading_technologies:
        "Fehler beim Laden der Technologien. Bitte versuchen Sie es später erneut.",
      no_data_technologies:
        "Keine Technologien gefunden. Fügen Sie oben Ihre erste Technologie hinzu.",
      error_create_technology: "Fehler beim Erstellen der Technologie:",
      error_update_technology: "Fehler beim Aktualisieren der Technologie:",
      error_delete_technology: "Fehler beim Löschen der Technologie:",
      edit_button: "Bearbeiten", // Defined here, reused elsewhere
      delete_button: "Löschen", // Defined here, reused elsewhere
      save_button: "Speichern", // Defined here, reused elsewhere
      cancel_button: "Abbrechen", // Defined here, reused elsewhere
      actions: "Aktionen",
      delete_manager_description: "Dies wird die Technologie dauerhaft löschen",
      delete_warning: "Diese Aktion kann nicht rückgängig gemacht werden.",
      description_name: "Beschreibung",
      save_name: "Größenname",
      update_button: "Aktualisieren",

      // Alloy Manager (alloy-manager.tsx)
      card_title_alloys: "Legierungen verwalten",
      card_description_alloys:
        "Hinzufügen, bearbeiten oder entfernen Sie Legierungen, die in der Formenproduktion verwendet werden.",
      new_alloy_placeholder: "Neuer Legierungsname",
      error_loading_alloys:
        "Fehler beim Laden der Legierungen. Bitte versuchen Sie es später erneut.",
      no_data_alloys:
        "Keine Legierungen gefunden. Fügen Sie oben Ihre erste Legierung hinzu.",
      error_create_alloy: "Fehler beim Erstellen der Legierung:",
      error_update_alloy: "Fehler beim Aktualisieren der Legierung:",
      error_delete_alloy: "Fehler beim Löschen der Legierung:",
      allow_name: "Legierungsname",
      permanent_alloy_delete: "Dies wird die Legierung dauerhaft löschen",

      // Article Table (article-table.tsx)
      header_title_articles: "Artikel zu dieser Form",
      add_article_button: "Artikel hinzufügen",
      error_loading_articles:
        "Fehler beim Laden der Artikel. Bitte versuchen Sie es später erneut.",
      no_data_articles:
        "Keine Artikel gefunden. Fügen Sie Ihren ersten Artikel über die Schaltfläche oben hinzu.",
      error_create_article: "Fehler beim Erstellen des Artikels:",
      error_update_article: "Fehler beim Aktualisieren des Artikels:",
      error_delete_article: "Fehler beim Löschen des Artikels:",
      permanent_article_delete: "Dies wird den Artikel dauerhaft löschen",

      // Filter Panel (filter-panel.tsx)
      technology_heading: "Technologie",
      alloy_heading: "Legierung",
      mold_size_heading: "Formgröße",
      tags_heading: "Tags",
      activity_status_heading: "Aktivitätsstatus",
      no_technologies: "Keine Technologien verfügbar",
      no_alloys: "Keine Legierungen verfügbar",
      no_mold_sizes: "Keine Formgrößen verfügbar",
      no_tags: "Keine Tags verfügbar",
      activity_status_all: "Alle",
      activity_status_active: "Aktiv",
      activity_status_inactive: "Inaktiv",
      activity_status_mixed: "Gemischt",

      // Mold Form Dialog (mold-form-dialog.tsx)
      dialog_title_create: "Neue Form hinzufügen",
      dialog_title_edit: "Form bearbeiten",
      dialog_title_duplicate: "Form duplizieren",
      error_submit: "Fehler beim Senden des Formulars:",
      dialog_title_default: "Formular",
      dialog_description_create: "Fügen Sie dem System eine neue Form hinzu.",
      dialog_description_edit:
        "Bearbeiten Sie die Details der ausgewählten Form.",
      dialog_description_duplicate:
        "Erstellen Sie eine Kopie der ausgewählten Form mit einer neuen Formnummer.",
      // German
      tab_general_information: "Allgemeine Informationen",
      tab_articles: "Artikel",
      saving: "Speichern...",
      // German translations
      dialog_submit_create: "Erstellen",
      dialog_submit_edit: "Änderungen speichern",
      dialog_submit_duplicate: "Duplikat erstellen",
      status: "Status",
      select_status: "Status auswählen",
      enter_name: "Geben Sie einen Namen für den neuen Zweck ein",
      enter_optional_name: "Geben Sie einen Namen und optional eine Beschreibung für die neue Größe ein.",

      // Mold Size Manager (mold-size-manager.tsx)
      card_title_mold_sizes: "Formgrößen verwalten",
      card_description_mold_sizes:
        "Hinzufügen, bearbeiten oder entfernen Sie Formgrößen, die in der Produktion verwendet werden.",
      new_mold_size_placeholder: "Neuer Formgrößenname",
      new_mold_size_description_placeholder: "Beschreibung (optional)",
      add_mold_size_button: "Formgröße hinzufügen",
      error_loading_mold_sizes:
        "Fehler beim Laden der Formgrößen. Bitte versuchen Sie es später erneut.",
      no_data_mold_sizes:
        "Keine Formgrößen gefunden. Fügen Sie oben Ihre erste Formgröße hinzu.",
      error_create_mold_size: "Fehler beim Erstellen der Formgröße:",
      error_update_mold_size: "Fehler beim Aktualisieren der Formgröße:",
      error_delete_mold_size: "Fehler beim Löschen der Formgröße:",
      delete_mold_manager_description_part1:
        "Dies wird die Formgröße dauerhaft löschen",
      delete_mold_manager_description_part2:
        "und von allen Formen entfernen, die sie verwenden. Diese Aktion kann nicht rückgängig gemacht werden.",

      // Mold Table (mold-table.tsx)
      refresh_button: "Aktualisieren",
      refresh_data: "Daten aktualisiere",
      error_loading_molds:
        "Fehler beim Laden der Formen. Bitte versuchen Sie es später erneut.",
      no_data_molds:
        "Keine Formen gefunden. Passen Sie Ihre Filter an oder fügen Sie eine neue Form hinzu.",
      delete_dialog_title: "Sind Sie sicher?",
      delete_dialog_description:
        'Dies löscht die Form "{moldNumber}" und alle zugehörigen Artikel dauerhaft. Diese Aktion kann nicht rückgängig gemacht werden.',
      // German translations
      delete_dialog_description_part1: "Dies wird die Form dauerhaft löschen",
      delete_dialog_description_part2:
        "und alle zugehörigen Artikel. Diese Aktion kann nicht rückgängig gemacht werden.",
      error_delete_mold_table: "Fehler beim Löschen der Form:",
      error_save_mold_table: "Fehler beim Speichern der Form:",
      // Tag Manager (tag-manager.tsx)
      card_title_tags: "Tags verwalten",
      card_description_tags:
        "Hinzufügen, bearbeiten oder entfernen Sie Tags, die zur Kategorisierung von Formen verwendet werden.",
      new_tag_placeholder: "Neuer Tag-Name",
      error_loading_tags:
        "Fehler beim Laden der Tags. Bitte versuchen Sie es später erneut.",
      no_data_tags:
        "Keine Tags gefunden. Fügen Sie oben Ihren ersten Tag hinzu.",
      error_create_tag: "Fehler beim Erstellen des Tags:",
      error_update_tag: "Fehler beim Aktualisieren des Tags:",
      error_delete_tag: "Fehler beim Löschen des Tags:",
      // German translations
      delete_tag_description_part1: "Dies wird den Tag dauerhaft löschen",
      delete_tag_description_part2:
        "und von allen Formen entfernen, denen er zugewiesen wurde. Diese Aktion kann nicht rückgängig gemacht werden.",

      //  activity log
      // German (mold namespace) New Keys
      select_placeholder_activity_type: "Aktivitätstyp",
      all_activities: "Alle Aktivitäten",
      select_placeholder_entity_type: "Entitätstyp",
      all_entities: "Alle Entitäten",
      entity_mold: "Form",
      entity_article: "Artikel",
      entity_instance: "Instanz",
      entity_technology: "Technologie",
      entity_alloy: "Legierung",
      entity_tag: "Tag",
      entity_mold_size: "Formgröße",
      select_placeholder_user: "Benutzer",
      all_users: "Alle Benutzer",
      select_placeholder_date_range: "Zeitraum",
      all_time: "Gesamte Zeit",
      date_range_today: "Heute",
      date_range_yesterday: "Gestern",
      date_range_last_7_days: "Letzte 7 Tage",
      date_range_last_30_days: "Letzte 30 Tage",
      clear_filters: "Filter löschen",
      tablehead_timestamp: "Zeitstempel",
      tablehead_activity: "Aktivität",
      tablehead_details: "Details",
      tablehead_user: "Benutzer",
      tablehead_changes: "Änderungen",
      error_loading_activity_logs:
        "Fehler beim Laden der Aktivitätsprotokolle. Bitte versuchen Sie es später erneut.",
      no_data_activity_logs:
        "Keine Aktivitätsprotokolle gefunden. Passen Sie Ihre Filter an.",
      detailed_changes: "Ausführliche Änderungen:",
      no_changes: "Keine Änderungen",
      search_logs_placeholder: "Protokolle durchsuchen...",
      none: "Keine",
      yes: "Ja",
      no: "Nein",
      relative_seconds_ago: "Sekunden her",
      relative_minute_ago: "Minute her",
      relative_minutes_ago: "Minuten her",
      relative_hour_ago: "Stunde her",
      relative_hours_ago: "Stunden her",
      relative_day_ago: "Tag her",
      relative_days_ago: "Tage her",
      relative_month_ago: "Monat her",
      relative_months_ago: "Monate her",
      unknown_time: "Unbekannte Zeit",

      search_molds_placeholder: "Formen suchen...",
      filters: "Filter",
      clear_all: "Alles löschen",
      add_new: "Neu hinzufügen", // Reused from earlier if needed, but kept unique here for clarity
      legacy_mold_number: "Alte Formnummer",
      mold_number: "Formnummer",
      technology: "Technologie",
      alloy: "Legierung",
      warehouse_location: "Lagerort",
      mold_size: "Formgröße",
      number_of_articles: "Anzahl der Artikel",
      activity_status: "Aktivitätsstatus",
      tags: "Tags",
      created_date: "Erstellungsdatum",

      // Mold Table Row
      status_active: "Aktiv",
      status_inactive: "Inaktiv",
      status_mixed: "Gemischt",
      open_menu: "Menü öffnen",
      edit: "Bearbeiten", // Reused from earlier
      duplicate: "Duplizieren",

      // Article Form Dialog
      article_form_title: "Neuen Artikel hinzufügen",
      article_form_description:
        "Geben Sie die Artikeldetails ein. Sie können entweder die alte oder die neue Artikelnummer oder beide angeben.",
      old_article_number: "Alte Artikelnummer",
      new_article_number: "Neue Artikelnummer",
      article_description: "Beschreibung",
      frequency: "Häufigkeit",
      frequency_description:
        "Wie viele Instanzen dieses Artikels auf der Form vorkommen",
      old_article_placeholder: "Alte Artikelnummer eingeben",
      new_article_placeholder: "Neue Artikelnummer eingeben",
      article_description_placeholder: "Artikelbeschreibung eingeben",

      // Articles Tab
      articles_tab_title: "Artikel zu dieser Form",
      no_articles_heading: "Noch keine Artikel hinzugefügt",
      no_articles_message:
        "Fügen Sie Artikel über die Schaltfläche oben hinzu.",
      articles_note:
        "Hinweis: Artikel werden beim Erstellen der Form gespeichert.",

      // Barcode Scanner Dialog
      scan_barcode_title: "Barcode scannen",
      scan_barcode_description:
        "Scannen oder geben Sie einen Lagerort-Barcode ein.",
      barcode_placeholder: "LA000",
      confirm_button: "Bestätigen",
      barcode_instructions:
        "Positionieren Sie den Barcode vor der Kamera Ihres Geräts oder geben Sie den Code manuell ein.",

      // General Tab
      activity_status_label: "Aktivitätsstatus",
      current_status_prefix: "Aktueller Status: ",
      set_active_instruction: "Legen Sie fest, ob diese Form derzeit aktiv ist",
      warning_status:
        "Warnung: Das Ändern dieses Status aktualisiert alle Artikel und Instanzen entsprechend.",
      legacy_mold_number_label: "Alte Formnummer",
      legacy_mold_number_placeholder: "Alte Formnummer eingeben",
      mold_number_label: "Formnummer",
      mold_number_placeholder: "F1xxxx",
      mold_number_description_create: "Automatisch generierte Formnummer",
      mold_number_description_edit: "Formnummer kann nicht geändert werden",
      technology_label: "Technologie",
      technology_placeholder: "Technologie auswählen",
      alloy_label: "Legierung",
      alloy_placeholder: "Legierung auswählen",
      mold_size_label: "Formgröße",
      mold_size_placeholder: "Formgröße auswählen",
      warehouse_location_label: "Lagerort",
      warehouse_location_placeholder: "Lagerort auswählen",
      warehouse_location_description:
        "Klicken Sie, um einen Lagerort auszuwählen oder einen Barcode zu scannen",
      number_of_articles_label: "Anzahl der Artikel",
      number_of_articles_description: "Automatisch aus den Artikeln berechnet",
      start_date_label: "Startdatum",
      end_date_label: "Enddatum",
      new_purpose: "Neuen Zweck hinzufügen",
      delete_purpose: "Aktuellen Zweck löschen",
      add_size: "Neue Größe hinzufügen",
      delete_size: "Aktuelle Größe löschen",

      // Warehouse Location Dialog
      warehouse_dialog_title: "Lagerort auswählen",
      warehouse_dialog_description:
        "Wählen Sie einen Lagerort aus der Liste oder suchen Sie nach LA-Nummer oder Standort.",
      search_locations_placeholder: "Standorte suchen...",
      no_locations_found: "Keine Standorte gefunden",
      location: "Standort",

      // article row
      change_status: "Status ändern",

      // Image uploader
      mold_image: "Formbild",
      mold_preview_alt: "Formvorschau",
      remove: "Entfernen",
      no_image_uploaded: "Kein Bild hochgeladen",
      upload_image: "Bild hochladen",

      // Tag Selector (tag-selector.tsx)
      select_tags_description:
        "Wählen Sie Tags aus, um diese Form zu kategorisieren",
      search_tags_placeholder: "Tags durchsuchen...",
      no_tags_found: "Keine Tags gefunden",
      select_tags: "Tags auswählen...",

      // German
      mold_management_system: "Formenverwaltungssystem",
      mold_management_description:
        "Verwalten Sie Ihre Formen, Artikel und verfolgen Sie Aktivitäten",
      tab_molds: "Formen",
      tab_activity_log: "Aktivitätsprotokoll",
    },
    // Optional: Add de/settings content from de/settings.json if needed for SSR/fallback
    settings: {
        "admin_settings": "Admin-Einstellungen",
        "user_settings": "Benutzereinstellungen",
        // ... other potential de keys ...
    },
  },
  en: {
    common: {
      "navigation.home": "Home",
      "navigation.products": "Products",
      "navigation.sales": "Sales",
      "navigation.production": "Production",
      "navigation.inventory": "Inventory",
      "navigation.business": "Business",
      "navigation.employees": "Employees",
      "navigation.suppliers": "Suppliers",
      "navigation.settings": "Settings",
      "navigation.mold_management": "mold management",
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
    mold: {
      // Settings Dialog (used in settings-dialog.tsx)
      settings_dialog_title: "Settings",
      settings_dialog_description: "Manage your alloys and tags",
      settings_tab_technologies: "Technologies",
      settings_tab_alloys: "Alloys",
      settings_tab_tags: "Tags",
      settings_tab_moldSizes: "Mold Sizes",

      // Technology Manager (technology-manager.tsx)
      card_title_technologies: "Manage Technologies",
      card_description_technologies:
        "Add, edit, or remove technologies used in mold production.",
      new_technology_placeholder: "New technology name",
      technology_name: "Technology Name",
      add_button: "Add", // Defined here, reused elsewhere
      error_loading_technologies:
        "Error loading technologies. Please try again later.",
      no_data_technologies:
        "No technologies found. Add your first technology above.",
      error_create_technology: "Failed to create technology:",
      error_update_technology: "Failed to update technology:",
      error_delete_technology: "Failed to delete technology:",
      edit_button: "Edit", // Defined here, reused elsewhere
      delete_button: "Delete", // Defined here, reused elsewhere
      save_button: "Save", // Defined here, reused elsewhere
      cancel_button: "Cancel", // Defined here, reused elsewhere
      actions: "Actions",
      delete_manager_description: "This will permanently delete the technology",
      delete_warning: "This action cannot be undone.",
      description_name: "Description",
      save_name: "Save Name",
      update_button: "Update",

      // Alloy Manager (alloy-manager.tsx)
      card_title_alloys: "Manage Alloys",
      card_description_alloys:
        "Add, edit, or remove alloys used in mold production.",
      new_alloy_placeholder: "New alloy name",
      error_loading_alloys: "Error loading alloys. Please try again later.",
      no_data_alloys: "No alloys found. Add your first alloy above.",
      error_create_alloy: "Failed to create alloy:",
      error_update_alloy: "Failed to update alloy:",
      error_delete_alloy: "Failed to delete alloy:",
      allow_name: "Alloy Name",
      permanent_alloy_delete: "This will permanently delete the alloy",

      // Article Table (article-table.tsx)
      header_title_articles: "Articles on this Mold",
      add_article_button: "Add Article",
      error_loading_articles: "Error loading articles. Please try again later.",
      no_data_articles:
        "No articles found. Add your first article using the button above.",
      error_create_article: "Failed to create article:",
      error_update_article: "Failed to update article:",
      error_delete_article: "Failed to delete article:",
      permanent_article_delete: "This will permanently delete the article",

      // Filter Panel (filter-panel.tsx)
      technology_heading: "Technology",
      alloy_heading: "Alloy",
      mold_size_heading: "Mold Size",
      tags_heading: "Tags",
      activity_status_heading: "Activity Status",
      no_technologies: "No technologies available",
      no_alloys: "No alloys available",
      no_mold_sizes: "No mold sizes available",
      no_tags: "No tags available",
      activity_status_all: "All",
      activity_status_active: "Active",
      activity_status_inactive: "Inactive",
      activity_status_mixed: "Mixed",

      // Mold Form Dialog (mold-form-dialog.tsx)
      dialog_title_create: "Add New Mold",
      dialog_title_edit: "Edit Mold",
      dialog_title_duplicate: "Duplicate Mold",
      error_submit: "Error submitting form:",
      dialog_title_default: "Mold Form",
      dialog_description_create: "Add a new mold to the system.",
      dialog_description_edit: "Edit the selected mold's details.",
      dialog_description_duplicate:
        "Create a duplicate of the selected mold with a new mold number.",
      tab_general_information: "General Information",
      tab_articles: "Articles",
      saving: "Saving...",
      dialog_submit_create: "Create",
      dialog_submit_edit: "Save Changes",
      dialog_submit_duplicate: "Create Duplicate",
      status: "Status",
      select_status: "Select status",
      enter_name: "Enter a name for the new purpose.",
      enter_optional_name: "Enter a name and optionally a description for the new size.",

      // Mold Size Manager (mold-size-manager.tsx)
      card_title_mold_sizes: "Manage Mold Sizes",
      card_description_mold_sizes:
        "Add, edit, or remove mold sizes used in production.",
      new_mold_size_placeholder: "New mold size name",
      new_mold_size_description_placeholder: "Description (optional)",
      add_mold_size_button: "Add Mold Size",
      error_loading_mold_sizes:
        "Error loading mold sizes. Please try again later.",
      no_data_mold_sizes:
        "No mold sizes found. Add your first mold size above.",
      error_create_mold_size: "Failed to create mold size:",
      error_update_mold_size: "Failed to update mold size:",
      error_delete_mold_size: "Failed to delete mold size:",
      delete_mold_manager_description_part1:
        "This will permanently delete the mold size",
      delete_mold_manager_description_part2:
        "and remove it from all molds that use it. This action cannot be undone.",

      // Mold Table (mold-table.tsx)
      refresh_button: "Refresh",
      refresh_data: "Refresh data",
      error_loading_molds: "Error loading molds. Please try again later.",
      no_data_molds:
        "No molds found. Try adjusting your filters or add a new mold.",
      delete_dialog_title: "Are you sure?",
      delete_dialog_description:
        'This will permanently delete the mold "{moldNumber}" and all its associated articles. This action cannot be undone.',
      // English translations
      delete_dialog_description_part1: "This will permanently delete the mold",
      delete_dialog_description_part2:
        "and all its associated articles. This action cannot be undone.",
      error_delete_mold_table: "Failed to delete mold:",
      error_save_mold_table: "Failed to save mold:",

      // Tag Manager (tag-manager.tsx)
      card_title_tags: "Manage Tags",
      card_description_tags:
        "Add, edit, or remove tags used to categorize molds.",
      new_tag_placeholder: "New tag name",
      error_loading_tags: "Error loading tags. Please try again later.",
      no_data_tags: "No tags found. Add your first tag above.",
      error_create_tag: "Failed to create tag:",
      error_update_tag: "Failed to update tag:",
      error_delete_tag: "Failed to delete tag:",
      // English translations
      delete_tag_description_part1: "This will permanently delete the tag",
      delete_tag_description_part2:
        "and remove it from all molds it has been assigned to. This action cannot be undone.",

      // activity logs
      // English (mold namespace) New Keys
      select_placeholder_activity_type: "Activity Type",
      all_activities: "All Activities",
      select_placeholder_entity_type: "Entity Type",
      all_entities: "All Entities",
      entity_mold: "Mold",
      entity_article: "Article",
      entity_instance: "Instance",
      entity_technology: "Technology",
      entity_alloy: "Alloy",
      entity_tag: "Tag",
      entity_mold_size: "Mold Size",
      select_placeholder_user: "User",
      all_users: "All Users",
      select_placeholder_date_range: "Date Range",
      all_time: "All Time",
      date_range_today: "Today",
      date_range_yesterday: "Yesterday",
      date_range_last_7_days: "Last 7 Days",
      date_range_last_30_days: "Last 30 Days",
      clear_filters: "Clear Filters",
      tablehead_timestamp: "Timestamp",
      tablehead_activity: "Activity",
      tablehead_details: "Details",
      tablehead_user: "User",
      tablehead_changes: "Changes",
      error_loading_activity_logs:
        "Error loading activity logs. Please try again later.",
      no_data_activity_logs:
        "No activity logs found. Try adjusting your filters.",
      detailed_changes: "Detailed Changes:",
      no_changes: "No changes",
      search_logs_placeholder: "Search logs...",
      none: "None",
      yes: "Yes",
      no: "No",
      relative_seconds_ago: "seconds ago",
      relative_minute_ago: "minute ago",
      relative_minutes_ago: "minutes ago",
      relative_hour_ago: "hour ago",
      relative_hours_ago: "hours ago",
      relative_day_ago: "day ago",
      relative_days_ago: "days ago",
      relative_month_ago: "month ago",
      relative_months_ago: "months ago",
      unknown_time: "Unknown time",

      // Mold Table Actions & Header
      search_molds_placeholder: "Search molds...",
      filters: "Filters",
      clear_all: "Clear All",
      add_new: "Add New",
      legacy_mold_number: "Legacy Mold Number",
      mold_number: "Mold Number",
      technology: "Technology",
      alloy: "Alloy",
      warehouse_location: "Warehouse Location",
      mold_size: "Mold Size",
      number_of_articles: "Number of Articles",
      activity_status: "Activity Status",
      tags: "Tags",
      created_date: "Created Date",

      // Mold Table Row
      status_active: "Active",
      status_inactive: "Inactive",
      status_mixed: "Mixed",
      open_menu: "Open menu",
      edit: "Edit",
      duplicate: "Duplicate",

      // Article Form Dialog
      article_form_title: "Add New Article",
      article_form_description:
        "Enter article details. You can specify either the old or new article number, or both.",
      old_article_number: "Old Article Number",
      new_article_number: "New Article Number",
      article_description: "Description",
      frequency: "Frequency",
      frequency_description:
        "How many instances of this article appear on the mold",
      old_article_placeholder: "Enter old article number",
      new_article_placeholder: "Enter new article number",
      article_description_placeholder: "Enter article description",

      // Articles Tab
      articles_tab_title: "Articles on this Mold",
      no_articles_heading: "No articles added yet",
      no_articles_message: "Add articles using the button above.",
      articles_note: "Note: Articles will be saved when you create the mold.",

      // Barcode Scanner Dialog
      scan_barcode_title: "Scan Barcode",
      scan_barcode_description: "Scan or enter a warehouse location barcode.",
      barcode_placeholder: "LA000",
      confirm_button: "Confirm",
      barcode_instructions:
        "Position the barcode in front of your device's camera or enter the code manually.",

      // General Tab
      activity_status_label: "Activity Status",
      current_status_prefix: "Current status: ",
      set_active_instruction: "Set whether this mold is currently active",
      warning_status:
        "Warning: Changing this status will update all articles and instances accordingly.",
      legacy_mold_number_label: "Legacy Mold Number",
      legacy_mold_number_placeholder: "Enter legacy mold number",
      mold_number_label: "Mold Number",
      mold_number_placeholder: "F1xxxx",
      mold_number_description_create: "Automatically generated mold number",
      mold_number_description_edit: "Mold number cannot be changed",
      technology_label: "Technology",
      technology_placeholder: "Select a technology",
      alloy_label: "Alloy",
      alloy_placeholder: "Select an alloy",
      mold_size_label: "Mold Size",
      mold_size_placeholder: "Select a mold size",
      warehouse_location_label: "Warehouse Location",
      warehouse_location_placeholder: "Select warehouse location",
      warehouse_location_description:
        "Click to select a warehouse location or scan a barcode",
      number_of_articles_label: "Number of Articles",
      number_of_articles_description: "Automatically calculated from articles",
      start_date_label: "Start Date",
      end_date_label: "End Date",
      new_purpose: "Add new purpose",
      delete_purpose: "Add new purpose",
      add_size: "Add new size.",
      delete_size: "Delete current size.",

      // Warehouse Location Dialog
      warehouse_dialog_title: "Select Warehouse Location",
      warehouse_dialog_description:
        "Choose a warehouse location from the list or search by LA number or location.",
      search_locations_placeholder: "Search locations...",
      no_locations_found: "No locations found",
      location: "Location",

      // article row
      change_status: "Change Status",

      // Image Uploader (image-uploader.tsx)
      mold_image: "Mold Image",
      mold_preview_alt: "Mold preview",
      remove: "Remove",
      no_image_uploaded: "No image uploaded",
      upload_image: "Upload Image",

      // Tag Selector (tag-selector.tsx)
      select_tags_description: "Select tags to categorize this mold",
      search_tags_placeholder: "Search tags...",
      no_tags_found: "No tags found",
      select_tags: "Select tags...",

      // English
      mold_management_system: "Mold Management System",
      mold_management_description:
        "Manage your molds, articles, and track activities",
      tab_molds: "Molds",
      tab_activity_log: "Activity Log",
    },
    settings: { // Full en/settings content
      "admin_settings": "Admin Settings",
      "user_settings": "User Settings",
      "account": "Account",
      "preferences": "Preferences",
      "user_management": "User Management",
      "system": "System",
      "data_viewer": "Data Viewer",
      "advanced_settings": "Advanced Settings",
      "profile_information": "Profile Information",
      "update_your_profile_details": "Update your personal information and contact details.",
      "customize_your_experience": "Customize your application experience.",
      "manage_users_and_permissions": "Manage users, roles, and permissions.",
      "api_connections": "API Connections",
      "manage_external_api_connections": "Enable or disable connections to external systems.",
      "database_viewer": "Database Viewer",
      "view_and_export_database_tables": "View database tables and export data to Excel.",
      "legacy_erp_connection": "Legacy ERP Connection",
      "legacy_erp_description": "Connect to the legacy ERP system for data synchronization.",
      "images_cms_connection": "Images CMS Connection",
      "images_cms_description": "Connect to the external image content management system.",
      "table_name": "Table Name",
      "row_count": "Row Count",
      "last_updated": "Last Updated",
      "actions": "Actions",
      "export_excel": "Export Excel",
      "search_tables": "Search tables...",
      "account_placeholder": "Manage your account settings, profile information, and security preferences.",
      "preferences_placeholder": "Customize your application experience with personalized settings and notifications.",
      "user_management_placeholder": "Manage user accounts, roles, and permissions. Configure access controls and user groups.",
      "username": "Username",
      "username_cannot_change": "Username cannot be changed.",
      "email": "Email",
      "first_name": "First Name",
      "last_name": "Last Name",
      "save_changes": "Save Changes",
      "email_required": "Email is required",
      "email_invalid": "Email is invalid",
      "profile_update_error": "Failed to update profile. Please try again.",
      "profile_update_success": "Profile updated successfully",
      "account_security": "Account Security",
      "manage_account_security": "Manage your account security settings",
      "change_password": "Change Password",
      "email_notifications": "Email Notifications",
      "email_notifications_description": "Receive email notifications about important system events",
      "dashboard_welcome": "Dashboard Welcome Message",
      "dashboard_welcome_description": "Show welcome message on the dashboard",
      "old_password": "Current Password",
      "new_password": "New Password",
      "confirm_password": "Confirm Password",
      "old_password_required": "Current password is required",
      "new_password_required": "New password is required",
      "confirm_password_required": "Please confirm your new password",
      "password_too_short": "Password must be at least 8 characters long",
      "passwords_dont_match": "Passwords don't match",
      "password_changed_success": "Password changed successfully",
      "password_change_error": "Failed to change password. Please check your current password.",
      "cancel": "Cancel",
      "system_configuration": "System Configuration",
      "configure_advanced_system_settings": "Configure advanced system settings and parameters",
      "maintenance_mode": "Maintenance Mode",
      "maintenance_mode_description": "Put the system in maintenance mode. Only administrators can access the system.",
      "debug_mode": "Debug Mode",
      "debug_mode_description": "Enable detailed logging and debugging features",
      "cache_lifetime": "Cache Lifetime",
      "cache_lifetime_description": "Time in seconds before cached data expires",
      "seconds": "seconds",
      "log_level": "Log Level",
      "log_level_description": "Set the system-wide logging level",
      "log_level_error": "Error",
      "log_level_warning": "Warning",
      "log_level_info": "Info",
      "log_level_debug": "Debug",
      "save_configuration": "Save Configuration",
      "system_information": "System Information",
      "view_system_details": "View detailed system information and status",
      "system_version": "System Version",
      "database_version": "Database Version",
      "server_environment": "Server Environment",
      "last_system_update": "Last System Update",
      "user_debug_info": "User Debug Information",
      "user_group": "User Group",
      "admin_status": "Admin Status",
      "admin_yes": "Yes",
      "admin_no": "No",
      "configuration_saved": "Configuration saved successfully",
      "configuration_save_error": "Failed to save configuration. Please try again."
    },
  },
  cs: { // Restore CS section structure
    common: { // Placeholder CS common
      "navigation.settings": "Nastavení",
      // ... other cs/common keys if available ...
    },
    mutterTab: { /* Placeholder cs/mutterTab content */ },
    settings_system: { /* Placeholder cs/settings_system content */ },
    settings_currency: { /* Placeholder cs/settings_currency content */ },
    mold: { /* Placeholder cs/mold content */ },
    settings: { // Full cs/settings content
      "admin_settings": "Nastavení administrátora",
      "user_settings": "Uživatelská nastavení",
      "account": "Účet",
      "preferences": "Předvolby",
      "user_management": "Správa uživatelů",
      "system": "Systém",
      "data_viewer": "Prohlížeč dat",
      "advanced_settings": "Pokročilá nastavení",
      "profile_information": "Informace o profilu",
      "update_your_profile_details": "Aktualizujte své osobní údaje a kontaktní informace.",
      "customize_your_experience": "Přizpůsobte si prostředí aplikace.",
      "manage_users_and_permissions": "Spravujte uživatele, role a oprávnění.",
      "api_connections": "API připojení",
      "manage_external_api_connections": "Povolte nebo zakažte připojení k externím systémům.",
      "database_viewer": "Prohlížeč databáze",
      "view_and_export_database_tables": "Zobrazte databázové tabulky a exportujte data do Excelu.",
      "legacy_erp_connection": "Připojení k původnímu ERP",
      "legacy_erp_description": "Připojení k původnímu ERP systému pro synchronizaci dat.",
      "images_cms_connection": "Připojení k CMS obrázků",
      "images_cms_description": "Připojení k externímu systému pro správu obrázků.",
      "table_name": "Název tabulky",
      "row_count": "Počet řádků",
      "last_updated": "Poslední aktualizace",
      "actions": "Akce",
      "export_excel": "Export do Excelu",
      "search_tables": "Hledat v tabulkách...",
      "account_placeholder": "Spravujte nastavení svého účtu, informace o profilu a bezpečnostní předvolby.",
      "preferences_placeholder": "Přizpůsobte si prostředí aplikace pomocí osobních nastavení a oznámení.",
      "user_management_placeholder": "Spravujte uživatelské účty, role a oprávnění. Konfigurujte přístupová práva a uživatelské skupiny.",
      "username": "Uživatelské jméno",
      "username_cannot_change": "Uživatelské jméno nelze změnit.",
      "email": "E-mail",
      "first_name": "Jméno",
      "last_name": "Příjmení",
      "save_changes": "Uložit změny",
      "email_required": "E-mail je povinný",
      "email_invalid": "Neplatný formát e-mailu",
      "profile_update_error": "Aktualizace profilu se nezdařila. Zkuste to prosím znovu.",
      "profile_update_success": "Profil byl úspěšně aktualizován",
      "account_security": "Zabezpečení účtu",
      "manage_account_security": "Spravujte nastavení zabezpečení vašeho účtu",
      "change_password": "Změnit heslo",
      "email_notifications": "E-mailová oznámení",
      "email_notifications_description": "Dostávejte e-mailová oznámení o důležitých událostech systému",
      "dashboard_welcome": "Uvítací zpráva na nástěnce",
      "dashboard_welcome_description": "Zobrazit uvítací zprávu na nástěnce",
      "old_password": "Současné heslo",
      "new_password": "Nové heslo",
      "confirm_password": "Potvrdit heslo",
      "old_password_required": "Současné heslo je povinné",
      "new_password_required": "Nové heslo je povinné",
      "confirm_password_required": "Potvrďte prosím nové heslo",
      "password_too_short": "Heslo musí mít alespoň 8 znaků",
      "passwords_dont_match": "Hesla se neshodují",
      "password_changed_success": "Heslo bylo úspěšně změněno",
      "password_change_error": "Změna hesla se nezdařila. Zkontrolujte prosím své současné heslo.",
      "cancel": "Zrušit",
      "system_configuration": "Konfigurace systému",
      "configure_advanced_system_settings": "Konfigurace pokročilých systémových nastavení a parametrů", // Adjusted to match EN key structure
      "maintenance_mode": "Režim údržby",
      "maintenance_mode_description": "Uveďte systém do režimu údržby. Přístup mají pouze administrátoři.", // Adjusted to match EN key structure
      "debug_mode": "Režim ladění",
      "debug_mode_description": "Povolit podrobné protokolování a ladicí funkce", // Adjusted to match EN key structure
      "cache_lifetime": "Životnost mezipaměti",
      "cache_lifetime_description": "Doba v sekundách, po kterou jsou položky v mezipaměti platné.",
      "seconds": "sekund",
      "log_level": "Úroveň protokolování",
      "log_level_description": "Nastavit úroveň protokolování pro celý systém", // Adjusted to match EN key structure
      "log_level_error": "Chyba",
      "log_level_warning": "Varování",
      "log_level_info": "Informace",
      "log_level_debug": "Ladění",
      "save_configuration": "Uložit konfiguraci",
      "system_information": "Informace o systému", // Adjusted to match EN key structure
      "view_system_details": "Zobrazit podrobné informace o systému a stavu", // Adjusted to match EN key structure
      "system_version": "Verze systému",
      "database_version": "Verze databáze",
      "server_environment": "Prostředí serveru",
      "last_system_update": "Poslední aktualizace systému",
      "user_debug_info": "Informace o ladění uživatele",
      "user_group": "Uživatelská skupina",
      "admin_status": "Status administrátora",
      "admin_yes": "Ano",
      "admin_no": "Ne",
      "configuration_saved": "Konfigurace byla úspěšně uložena",
      "configuration_save_error": "Uložení konfigurace se nezdařilo. Zkuste to prosím znovu."
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
