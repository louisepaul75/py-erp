// Add type declarations for global variables injected by Django
interface Window {
  DJANGO_SETTINGS?: {
    CSRF_TOKEN?: string;
    [key: string]: any;
  };
} 