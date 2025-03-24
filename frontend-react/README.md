# pyERP Frontend

This is the React frontend for the pyERP system. It's built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui components.

## Features

- Modern UI with Tailwind CSS
- Component library with Radix UI
- Type safety with TypeScript
- Server-side rendering with Next.js

## Getting Started

### Prerequisites

- Node.js (v18 or later)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend-react directory
3. Install dependencies:

```bash
npm install
# or
yarn install
```

### Development

To start the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

### Building for Production

To build the application for production:

```bash
npm run build
# or
yarn build
```

### Testing

Run the test suite:

```bash
npm run test
# or
yarn test
```

For test coverage:

```bash
npm run test:coverage
# or
yarn test:coverage
```

### Mutation Testing

Mutation testing helps to evaluate the quality of your test suite by making small changes (mutations) to your code and checking if your tests can detect these changes.

To run mutation tests:

```bash
npm run test:mutation
# or
yarn test:mutation
```

To view the mutation testing report in a browser:

```bash
npm run test:mutation:report
# or
yarn test:mutation:report
```

This will serve the HTML report on a local server, typically at http://localhost:3000.

To start the production server:

```bash
npm run start
# or
yarn start
```

## Project Structure

```
frontend-react/
├── public/              # Static assets
├── src/
│   ├── app/             # Next.js app router pages
│   │   ├── ui-components/   # UI Components / Style Guide page
│   │   ├── example-page/    # Example implementation page
│   │   └── ...
│   ├── components/      # React components
│   │   ├── ui/          # UI component library
│   │   │   ├── common/      # Common UI components (Button, Card, Input)
│   │   │   ├── data/        # Data display components (Table, Charts)
│   │   │   ├── feedback/    # Feedback components (Alerts, Toasts)
│   │   │   ├── layout/      # Layout components (Grid, Container)
│   │   │   ├── index.ts     # Component library exports
│   │   │   └── README.md    # Component library documentation
│   │   └── ...          # Application-specific components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utility functions and configuration
│   │   └── theme-config.ts  # Theme configuration
│   └── ...
└── ...
```

## Component Library

The project includes a comprehensive UI component library with a consistent warm light brown color scheme. All components are designed to be:

- **Consistent**: Following the same design language
- **Accessible**: Meeting WCAG standards
- **Responsive**: Working on all device sizes
- **Themeable**: Supporting dark mode with warm light brown colors

### Using Components

Import components from the UI library:

```tsx
import { Button, Card, Input, Table } from '@/components/ui';
```

See the [Component Library Documentation](./src/components/ui/README.md) for detailed usage examples.

### Theme Configuration

The theme configuration is centralized in `src/lib/theme-config.ts`. This file contains:

- Color definitions
- Component styles
- Helper functions

You can import theme values directly:

```tsx
import { themeColors, componentStyles, cn } from '@/components/ui';
```

## Style Guide

The UI Components / Style Guide page (`/ui-components`) provides a visual reference of all available components and their variants. Use this as a reference when building new pages.

## Example Implementation

The Example Page (`/example-page`) demonstrates how to use the component library in a real application. It shows:

- Page layout structure
- Component composition
- State management
- Responsive design patterns

## Best Practices

1. **Use the enhanced components** from `@/components/ui` instead of the base shadcn components
2. **Follow the established patterns** when creating new components or pages
3. **Maintain mobile compatibility** by using responsive design patterns
4. **Document new components** with examples and prop descriptions
5. **Keep the dark mode theme** consistent with the warm light brown color scheme
6. **Centralize theme changes** in the theme-config.ts file

## Adding New Components

When adding new components to the library:

1. Create the component in the appropriate category folder
2. Export it in the index.ts file
3. Add documentation with examples
4. Add it to the Style Guide page

## Development Workflow

1. Start the development server: `npm run dev`
2. Visit the Style Guide: `http://localhost:3000/ui-components`
3. Build your page using the component library
4. Test on different screen sizes and in dark mode

## Technologies Used

- Next.js
- React
- TypeScript
- Tailwind CSS
- Radix UI 