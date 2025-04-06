/**
 * Component Library Index
 * 
 * This file exports all enhanced UI components for easy imports
 */

// Common UI Components
export * from './common/Button';
export * from './common/Card';
export * from './common/Input';
export * from './label';
export * from './radio-group';
export * from './textarea';
export * from './select';
export * from './form';
export * from './checkbox';

// Data Display Components
export { 
  Table as EnhancedTable,
  TableHeader as EnhancedTableHeader,
  TableBody as EnhancedTableBody,
  TableRow as EnhancedTableRow,
  TableHead as EnhancedTableHead,
  TableCell as EnhancedTableCell,
  StatusBadge 
} from './data/Table';
export * from './avatar';
export * from './badge';
export * from './calendar';
export * from './separator';
export * from './table';

// Feedback Components
export { Badge } from './badge';
export * from './alert';
export * from './alert-dialog';
export * from './toast';
export * from './toaster';
export * from './use-toast';

// Overlay Components
export * from './dialog';
export * from './dropdown-menu';
export * from './popover';
export * from './sheet';
export * from './tooltip';

// Loading Components
export * from './progress';
export * from './skeleton';
export * from './spinner';
export * from './LoadingSpinner';

// Interactive Components
export * from './slider';
export * from './switch';
export * from './tabs';
export * from './toggle';
export * from './toggle-group';

// Layout Components
export * from './scroll-area';
export * from './container';

// Re-export theme configuration
export { themeColors, componentStyles, cn } from '@/lib/theme-config'; 