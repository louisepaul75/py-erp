# pyERP Component Library

This component library provides a set of reusable UI components for the pyERP system. All components are designed with a consistent warm light brown color scheme and follow best practices for accessibility and responsiveness.

## Getting Started

Import components from the UI library:

```tsx
import { Button, Card, Input, Table } from '@/components/ui';
```

## Theme Configuration

The theme configuration is centralized in `src/lib/theme-config.ts`. This file contains:

- Color definitions
- Component styles
- Helper functions

You can import theme values directly:

```tsx
import { themeColors, componentStyles, cn } from '@/components/ui';
```

## Component Categories

### Common Components

Basic UI elements used throughout the application:

- **Button**: Enhanced button with variants, icons, and loading states
- **Card**: Card container with header, content, and footer sections
- **Input**: Text input with labels, icons, and validation

### Data Components

Components for displaying and manipulating data:

- **Table**: Data table with consistent styling
- **StatusBadge**: Visual indicators for status (active, pending, inactive)

## Usage Examples

### Button Component

```tsx
import { Button } from '@/components/ui';
import { Download, Plus } from 'lucide-react';

// Primary button
<Button>Default Button</Button>

// Secondary button with icon
<Button variant="secondary" icon={Download}>Download</Button>

// Outline button with right-aligned icon
<Button variant="outline" icon={Plus} iconPosition="right">Add Item</Button>

// Icon-only button
<Button size="icon" icon={Plus} aria-label="Add item" />

// Loading state
<Button loading>Processing...</Button>
```

### Card Component

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui';
import { Settings } from 'lucide-react';

<Card>
  <CardHeader>
    <CardTitle icon={Settings}>Card Title</CardTitle>
    <CardDescription>Card description text</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Input Component

```tsx
import { Input } from '@/components/ui';
import { Search, Mail } from 'lucide-react';

// Basic input with label
<Input label="Username" placeholder="Enter username" />

// Input with left icon
<Input icon={Search} placeholder="Search..." />

// Input with right icon
<Input icon={Mail} iconPosition="right" placeholder="Email address" />

// Input with validation error
<Input 
  label="Email" 
  placeholder="Enter email"
  error="Please enter a valid email address" 
/>
```

### Table Component

```tsx
import { 
  Table, 
  TableHeader, 
  TableBody, 
  TableRow, 
  TableHead, 
  TableCell, 
  StatusBadge 
} from '@/components/ui';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Email</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>John Doe</TableCell>
      <TableCell>john@example.com</TableCell>
      <TableCell>
        <StatusBadge status="active">Active</StatusBadge>
      </TableCell>
    </TableRow>
    <TableRow>
      <TableCell>Jane Smith</TableCell>
      <TableCell>jane@example.com</TableCell>
      <TableCell>
        <StatusBadge status="pending">Pending</StatusBadge>
      </TableCell>
    </TableRow>
  </TableBody>
</Table>
```

## Best Practices

1. **Use the enhanced components** instead of the base shadcn components for consistent styling
2. **Follow the established patterns** when creating new components
3. **Maintain mobile compatibility** by using responsive design patterns
4. **Document new components** with examples and prop descriptions
5. **Keep the dark mode theme** consistent with the warm light brown color scheme 