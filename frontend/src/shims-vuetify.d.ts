declare module 'vuetify' {
  import { Component } from 'vue';
  
  export const createVuetify: any;
  export const useTheme: any;
  export const useDisplay: any;
  export const useLayout: any;
}

declare module 'vuetify/components' {
  export const VApp: Component;
  export const VMain: Component;
  export const VContainer: Component;
  export const VRow: Component;
  export const VCol: Component;
  export const VBtn: Component;
  export const VCard: Component;
  export const VCardTitle: Component;
  export const VCardText: Component;
  export const VCardActions: Component;
  export const VTextField: Component;
  export const VSelect: Component;
  export const VCheckbox: Component;
  export const VRadio: Component;
  export const VRadioGroup: Component;
  export const VSwitch: Component;
  export const VList: Component;
  export const VListItem: Component;
  export const VListItemTitle: Component;
  export const VListItemSubtitle: Component;
  export const VListItemAction: Component;
  export const VDivider: Component;
  export const VToolbar: Component;
  export const VAppBar: Component;
  export const VIcon: Component;
  export const VMenu: Component;
  export const VDialog: Component;
  export const VAlert: Component;
  export const VSnackbar: Component;
  export const VProgressCircular: Component;
  export const VProgressLinear: Component;
  export const VTabs: Component;
  export const VTab: Component;
  export const VTabItem: Component;
  export const VTabsItems: Component;
  export const VFooter: Component;
  export const VNavigationDrawer: Component;
  export const VBadge: Component;
  export const VTooltip: Component;
  export const VChip: Component;
  export const VExpansionPanel: Component;
  export const VExpansionPanelTitle: Component;
  export const VExpansionPanelText: Component;
  export const VDataTable: Component;
  export const VPagination: Component;
  export const VSheet: Component;
  export const VSpacer: Component;
}

declare module 'vuetify/directives' {
  export const Ripple: any;
  export const Scroll: any;
  export const Resize: any;
  export const Intersect: any;
  export const Touch: any;
  export const ClickOutside: any;
}

declare module 'vuetify/blueprints' {
  export const md3: any;
}

declare module 'vue-i18n' {
  export const createI18n: any;
  export const useI18n: any;
} 