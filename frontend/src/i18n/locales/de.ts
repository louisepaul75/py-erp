export default {
  common: {
    welcome: 'Willkommen',
    login: 'Anmelden',
    logout: 'Abmelden',
    register: 'Registrieren',
    profile: 'Profil',
    settings: 'Einstellungen',
    dashboard: 'Dashboard',
    save: 'Speichern',
    cancel: 'Abbrechen',
    delete: 'Löschen',
    edit: 'Bearbeiten',
    create: 'Erstellen',
    search: 'Suchen',
    loading: 'Laden...',
    error: 'Fehler',
    success: 'Erfolg',
    adminDashboard: 'Admin-Dashboard',
    language: 'Sprache',
    lightMode: 'Heller Modus',
    darkMode: 'Dunkler Modus',
    goToHome: 'Zur Startseite',
    noResults: 'Keine Ergebnisse gefunden'
  },
  app: {
    title: 'pyERP',
    version: 'Version'
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
    sales: 'Vertrieb',
    inventory: 'Lager',
    production: 'Produktion',
    testing: 'Testen',
    components: 'UI-Komponenten'
  },
  languages: {
    english: 'English',
    german: 'Deutsch',
    czech: 'Čeština'
  },
  validation: {
    required: 'Dieses Feld ist erforderlich',
    email: 'Bitte geben Sie eine gültige E-Mail-Adresse ein',
    minLength: 'Muss mindestens {min} Zeichen lang sein',
    maxLength: 'Darf höchstens {max} Zeichen lang sein'
  },
  errors: {
    general: 'Etwas ist schief gelaufen',
    notFound: '404',
    pageNotFound: 'Seite nicht gefunden',
    pageNotFoundMessage: 'Die gesuchte Seite existiert nicht oder wurde verschoben.',
    unauthorized: 'Nicht autorisierter Zugriff',
    forbidden: 'Zugriff verweigert'
  },
  auth: {
    username: 'Benutzername',
    password: 'Passwort',
    confirmPassword: 'Passwort bestätigen',
    currentPassword: 'Aktuelles Passwort',
    newPassword: 'Neues Passwort',
    email: 'E-Mail',
    firstName: 'Vorname',
    lastName: 'Nachname',
    changePassword: 'Passwort ändern',
    register: 'Registrieren',
    forgotPassword: 'Passwort vergessen?',
    rememberMe: 'Angemeldet bleiben'
  },
  dashboard: {
    overview: 'Übersicht',
    statistics: 'Statistiken',
    recentOrders: 'Aktuelle Bestellungen',
    recentSales: 'Aktuelle Verkäufe',
    stockAlerts: 'Bestandsalarme',
    metrics: {
      totalSales: 'Gesamtumsatz',
      totalOrders: 'Gesamtbestellungen',
      averageOrder: 'Durchschnittliche Bestellung',
      lowStock: 'Niedriger Bestand',
      topProducts: 'Top Produkte',
      monthlyRevenue: 'Monatlicher Umsatz',
      dailySales: 'Tagesverkäufe'
    },
    filters: {
      today: 'Heute',
      thisWeek: 'Diese Woche',
      thisMonth: 'Dieser Monat',
      lastMonth: 'Letzter Monat',
      custom: 'Benutzerdefiniert'
    },
    status: {
      pending: 'Ausstehend',
      processing: 'In Bearbeitung',
      completed: 'Abgeschlossen',
      cancelled: 'Storniert'
    }
  },
  inventory: {
    title: 'Lagerverwaltung',
    dashboard: 'Dashboard',
    warehouseManagement: 'Lagerverwaltung',
    lagerverwaltung: 'Lagerverwaltung',
    productInventory: 'Produktbestand',
    movements: 'Lagerbewegungen',
    storageLocations: 'Lagerorte',
    showOnlyWithProducts: 'Nur Lagerorte mit Produkten anzeigen',
    boxManagement: 'Schüttenverwaltung',
    schuettenverwaltung: 'Schüttenverwaltung',
    warehouseMap: 'Lagerkarte',
    name: 'Name',
    dimensions: 'Abmessungen',
    weightCapacity: 'Gewichtskapazität',
    slotCount: 'Anzahl der Slots',
    slotNamingScheme: 'Slot-Benennungsschema',
    locationCode: 'Standortcode',
    country: 'Land',
    cityBuilding: 'Stadt/Gebäude',
    unit: 'Einheit',
    compartment: 'Fach',
    shelf: 'Regal',
    errorFetchingBoxTypes: 'Fehler beim Abrufen der Schüttentypen',
    errorFetchingLocations: 'Fehler beim Abrufen der Lagerorte',
    totalBoxes: 'Gesamtanzahl Schütten',
    totalLocations: 'Gesamtanzahl Lagerorte',
    totalProducts: 'Gesamtanzahl Produkte',
    recentMovements: 'Aktuelle Bewegungen',
    boxesDescription: 'Gesamtanzahl der Schütten im System',
    locationsDescription: 'Gesamtanzahl der Lagerorte',
    productsDescription: 'Gesamtanzahl der Produkte im Lager',
    movementsDescription: 'Bewegungen in den letzten 7 Tagen',
    inventoryDashboard: 'Lager-Dashboard',
    dashboardDescription: 'Detaillierte Lagerstatistiken und Analysen werden hier in Kürze verfügbar sein',
    productInventoryDescription: 'Produktbestandsverwaltung wird hier in Kürze verfügbar sein',
    movementsPageDescription: 'Lagerbewegungsverfolgung wird hier in Kürze verfügbar sein',
    warehouseMapDescription: 'Interaktive Lagerkarte wird hier in Kürze verfügbar sein',
    boxCode: 'Schüttencode',
    boxType: 'Schüttentyp',
    storageLocation: 'Lagerort',
    statusLabel: 'Status',
    purposeLabel: 'Zweck',
    availableSlots: 'Verfügbare Slots',
    noLocation: 'Kein Lagerort',
    statusAVAILABLE: 'Verfügbar',
    statusIN_USE: 'In Verwendung',
    statusRESERVED: 'Reserviert',
    statusDAMAGED: 'Beschädigt',
    statusRETIRED: 'Ausgemustert',
    purposeSTORAGE: 'Lagerung',
    purposePICKING: 'Kommissionierung',
    purposeTRANSPORT: 'Transport',
    purposeWORKSHOP: 'Werkstatt',
    boxes: 'Schütten',
    boxTypes: 'Schüttentypen',
    noNotes: 'Keine Notizen',
    barcode: 'Barcode',
    location: 'Standort',
    overview: 'Übersicht',
    productMovements: 'Produktbewegungen',
    position: 'Position',
    flags: 'Kennzeichnungen',
    saleLocation: 'Verkaufsstandort',
    specialSpot: 'Sonderplatz',
    viewInventory: 'Bestand anzeigen',
    sale: 'Verkauf',
    status: {
      available: 'Verfügbar',
      in_use: 'In Verwendung',
      reserved: 'Reserviert',
      damaged: 'Beschädigt',
      retired: 'Ausgemustert'
    },
    purpose: {
      storage: 'Lagerung',
      picking: 'Kommissionierung',
      transport: 'Transport',
      workshop: 'Werkstatt'
    }
  },
  search: {
    placeholder: "Suchen...",
    noResults: "Keine Ergebnisse gefunden für \"{query}\"",
    startTyping: "Beginnen Sie mit der Eingabe",
    searching: "Suche läuft...",
    categories: {
      customers: "Kunden",
      sales_records: "Verkaufsbelege",
      parent_products: "Hauptprodukte",
      variant_products: "Produktvarianten",
      box_slots: "Box-Slots",
      storage_locations: "Lagerorte"
    }
  },
  sales: {
    records: {
      title: "Verkaufsbelege",
      noRecords: "Keine Verkaufsbelege gefunden",
      loading: "Verkaufsbelege werden geladen...",
      error: "Fehler beim Laden der Verkaufsbelege",
      headers: {
        recordNumber: "Beleg-Nr.",
        date: "Datum",
        type: "Typ",
        customer: "Kunde",
        total: "Gesamt",
        paymentStatus: "Zahlungsstatus",
        actions: "Aktionen"
      },
      types: {
        INVOICE: "Rechnung",
        PROPOSAL: "Angebot",
        DELIVERY_NOTE: "Lieferschein",
        CREDIT_NOTE: "Gutschrift",
        ORDER_CONFIRMATION: "Auftragsbestätigung"
      },
      paymentStatus: {
        PAID: "Bezahlt",
        PENDING: "Ausstehend",
        OVERDUE: "Überfällig",
        CANCELLED: "Storniert"
      },
      itemsDialog: {
        title: "Belegpositionen",
        noItems: "Keine Positionen für diesen Beleg gefunden",
        headers: {
          position: "Position",
          description: "Beschreibung",
          quantity: "Menge",
          unitPrice: "Einzelpreis",
          taxAmount: "MwSt.",
          subtotal: "Nettobetrag",
          total: "Gesamtbetrag",
          status: "Status"
        },
        fulfillmentStatus: {
          FULFILLED: "Erfüllt",
          PARTIAL: "Teilweise erfüllt",
          PENDING: "Ausstehend",
          CANCELLED: "Storniert"
        },
        close: "Schließen"
      },
      viewDetails: "Details anzeigen"
    }
  }
};
