# React Frontend Testing Guide

This directory contains the tests for the React frontend of PyERP. We use Jest and React Testing Library for testing React components and functionality.

## Test Structure

- `__tests__/`: Root directory for all tests
  - `components/`: Tests for React components
  - `utils/`: Tests for utility functions and hooks
  - Other test files can be organized by feature or page

## Running Tests

You can run the tests using the following commands from the `frontend-react` directory:

```bash
# Run all tests
npm test

# Run tests in watch mode (useful during development)
npm run test:watch

# Run tests with coverage report
npm run test:coverage
```

## CI Integration

Tests are automatically run as part of the CI/CD pipeline on GitHub Actions. The workflow is configured to:

1. Run tests using the Jest test runner
2. Generate test coverage reports
3. Report results to Codecov

## Writing Tests

Here's a basic example of how to write a test for a React component:

```jsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import YourComponent from '@/components/YourComponent';

describe('YourComponent', () => {
  it('renders correctly', () => {
    render(<YourComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const user = userEvent.setup();
    render(<YourComponent />);
    
    await user.click(screen.getByRole('button', { name: 'Click Me' }));
    
    expect(screen.getByText('Button Clicked')).toBeInTheDocument();
  });
});
```

### Test Utilities

We provide several test utilities to make testing easier:

- `render` wrapper with providers in `utils/test-utils.js`
- Mock data in `utils/mocks/`
- Test fixtures in `utils/fixtures/`

## Best Practices

1. Test behavior, not implementation details
2. Write meaningful test descriptions
3. Group related tests with `describe` blocks
4. Keep tests independent of each other
5. Use mock data consistently
6. Test both success and error scenarios
7. Aim for high test coverage (at least 70% or higher)

## Debugging Tests

When tests fail, you can debug them with:

```bash
# Run a specific test file
npm test -- path/to/test-file.test.js

# Run tests with verbose output
npm test -- --verbose

# Run a specific test by name
npm test -- -t "name of your test"
``` 