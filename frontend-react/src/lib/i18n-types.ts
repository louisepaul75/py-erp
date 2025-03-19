/**
 * TypeScript-Typen für i18n-Übersetzungen
 * Diese Datei definiert die Typen für alle Übersetzungsschlüssel
 * und ermöglicht Autovervollständigung und Typsicherheit.
 */

export interface Resources {
  common: typeof import('../../public/locales/de/common.json');
  auth: {
    login: string;
    logout: string;
    register: string;
    email: string;
    password: string;
    forgotPassword: string;
    passwordReset: string;
    rememberMe: string;
    loginFailed: string;
    unauthorized: string;
  };
  products: {
    productList: string;
    productDetails: string;
    addProduct: string;
    editProduct: string;
    deleteProduct: string;
    productName: string;
    productDescription: string;
    productPrice: string;
    productCategory: string;
    productStock: string;
    productUnit: string;
  };
  dashboard: {
    overview: string;
    recentOrders: string;
    salesStats: string;
    topProducts: string;
    customerActivity: string;
    inventoryAlerts: string;
    orderStatus: string;
  };
}

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: Resources;
  }
} 