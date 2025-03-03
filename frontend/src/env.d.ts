/// <reference types="vite/client" />

// Extend the Window interface to include our Vue app for debugging
declare global {
  interface Window {
    app: any;
  }
} 