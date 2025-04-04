import { cn } from './utils';

// Theme colors configuration
export const themeColors = {
  // Amber palette
  amber50: '#fffbeb',
  amber100: '#fef3c7',
  amber200: '#fde68a',
  amber300: '#fcd34d',
  amber400: '#fbbf24',
  amber500: '#f59e0b',
  amber600: '#d97706',
  amber700: '#b45309',
  amber800: '#92400e',
  amber900: '#78350f',
  amber950: '#451a03',

  // Gray palette
  gray50: '#f9fafb',
  gray100: '#f3f4f6',
  gray200: '#e5e7eb',
  gray300: '#d1d5db',
  gray400: '#9ca3af',
  gray500: '#6b7280',
  gray600: '#4b5563',
  gray700: '#374151',
  gray800: '#1f2937',
  gray900: '#111827',
  gray950: '#030712',

  // Status colors
  success: '#22c55e',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',

  // Semantic colors
  primary: '#f59e0b',
  primaryHover: '#d97706',
  primaryActive: '#b45309',
  ring: '#f59e0b',
  background: '#ffffff',
  card: '#ffffff',
  muted: '#f3f4f6',
  foreground: '#111827',
  mutedForeground: '#6b7280',
  border: '#e5e7eb'
} as const;

// Component styles configuration
export const componentStyles = {
  // Button styles
  button: {
    base: 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
    variants: {
      primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
      outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
      ghost: 'hover:bg-accent hover:text-accent-foreground',
      link: 'underline-offset-4 hover:underline text-primary',
      destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    },
    sizes: {
      default: 'h-10 py-2 px-4',
      sm: 'h-9 px-3',
      lg: 'h-11 px-8',
      icon: 'h-10 w-10',
      xs: 'h-8 px-2 text-xs'
    },
  },

  // Card styles
  card: {
    default: 'rounded-xl text-card-foreground bg-card shadow-sm border border-border',
    highlighted: 'rounded-xl text-card-foreground bg-primary/10 shadow-md border border-primary/20',
    header: 'flex flex-col space-y-1.5 p-6 bg-primary/10',
    footer: 'flex items-center p-6 pt-0 bg-primary/10'
  },

  // Input styles
  input: {
    default: 'flex h-10 w-auto rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
    withIcon: 'flex h-10 w-auto rounded-md border border-input bg-background pl-8 pr-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
    error: 'border-destructive focus-visible:ring-destructive',
    label: 'text-sm font-medium block',
    container: 'space-y-2',
    errorText: 'text-xs text-destructive mt-1'
  },

  // Table styles
  table: {
    container: 'w-full border-collapse',
    header: 'bg-muted border-b border-border',
    headerCell: 'h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0',
    headerText: 'font-medium text-foreground',
    row: 'border-b border-border transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted',
    cell: 'p-4 align-middle [&:has([role=checkbox])]:pr-0',
    footer: 'bg-muted border-t border-border',
    border: 'border-border'
  },

  // Status badge styles
  statusBadge: {
    base: 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
    active: 'bg-success text-success-foreground',
    pending: 'bg-warning text-warning-foreground',
    inactive: 'bg-muted text-muted-foreground',
    error: 'bg-destructive text-destructive-foreground'
  },

  // Filter styles
  filter: {
    container: 'flex flex-wrap items-center gap-2',
    tag: 'flex items-center gap-1 rounded-md bg-amber-500/10 px-2 py-1 text-xs text-amber-500',
    clearButton: 'h-auto p-0 text-xs text-amber-500 hover:text-amber-600'
  },

  // Icon styles
  icon: {
    base: 'h-4 w-4',
    sm: 'h-3 w-3',
    lg: 'h-5 w-5',
    xl: 'h-6 w-6',
    primary: 'text-amber-500',
    secondary: 'text-gray-500',
    success: 'text-green-500',
    warning: 'text-yellow-500',
    error: 'text-red-500',
    info: 'text-blue-500'
  },

  // Separator styles
  separator: {
    horizontal: 'h-[1px] w-full bg-gray-200',
    vertical: 'h-full w-[1px] bg-gray-200'
  }
} as const;

export { cn }; 