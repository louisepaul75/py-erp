# React Testing Improvement Plan

## Overview

Our recent test analysis showed several issues with React component testing, particularly around asynchronous state updates and API mocking. This document outlines a specific, prioritized plan to address these issues and improve the quality of our React tests.

## Current Issues

1. **React act() warnings**: State updates not wrapped in act() causing warnings
2. **Network mocking inconsistency**: Inconsistent approaches to mocking fetch/API calls
3. **Flaky tests**: Tests that sometimes pass and sometimes fail due to timing issues
4. **Low coverage**: Critical UI components have very low test coverage (dashboard.tsx < 3%)

## Priority 1: Fix act() Warnings (Week 1-2)

### Tasks

1. **Update Footer.test.tsx**: 
   - [x] Create test-helpers.tsx utility file
   - [ ] Refactor Footer tests to use the new mockFetch utility
   - [ ] Update rendering to consistently use act()
   - [ ] Ensure all tests properly wait for state updates

2. **Fix Auth Hook Tests**:
   - [ ] Refactor authHooks.test.tsx to use the test utilities
   - [ ] Update act() usage in mutation tests
   - [ ] Create consistent mocking pattern for auth service

3. **Create CI check for act() warnings**:
   - [ ] Add --strict mode to Jest config to fail on act() warnings
   - [ ] Update CI pipeline to include this check

## Priority 2: Standardize API Mocking (Week 3-4)

### Tasks

1. **Refactor All API Mocks**:
   - [ ] Update all component tests to use the mockFetch/mockApiEndpoint utilities
   - [ ] Ensure cleanup happens in afterEach hooks
   - [ ] Document the standard pattern in the testing docs

2. **Create Mock API Responses Library**:
   - [ ] Create fixtures directory with standard API responses
   - [ ] Update tests to use these fixtures
   - [ ] Ensure fixtures are synchronized with API types

3. **Implement MSW for More Complex Scenarios**:
   - [ ] Research and set up MSW (Mock Service Worker)
   - [ ] Create handlers for common API endpoints
   - [ ] Update complex tests to use MSW

## Priority 3: Increase Coverage of Critical Components (Week 5-8)

### Tasks

1. **Dashboard Components**:
   - [ ] Create comprehensive tests for dashboard.tsx (currently 2.64% coverage)
   - [ ] Test all interactive elements and state changes
   - [ ] Test layout responsiveness

2. **Article Page**:
   - [ ] Create tests for article-page.tsx
   - [ ] Test state management and API interactions
   - [ ] Test rendering of dynamic content

3. **Settings Page**:
   - [ ] Create tests for settings/page.tsx
   - [ ] Test form validation and submission
   - [ ] Test error states and success messages

## Priority 4: Implement End-to-End Testing (Week 9-12)

### Tasks

1. **Set Up Playwright**:
   - [ ] Install and configure Playwright
   - [ ] Create first simple E2E test for login flow
   - [ ] Set up CI integration

2. **Create E2E Test Suite**:
   - [ ] Identify critical user journeys
   - [ ] Create tests for each journey
   - [ ] Set up reporting and screenshots

3. **Visual Regression Testing**:
   - [ ] Research and implement visual regression testing
   - [ ] Create baseline screenshots
   - [ ] Add to CI pipeline

## Implementation Details

### Fixing Footer.test.tsx

Here's how we'll update the Footer component test:

```tsx
// Footer.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { Footer } from '@/components/Footer';
import { mockFetch } from '../utils/test-helpers';

describe('Footer', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders copyright information', () => {
    render(<Footer />);
    expect(screen.getByText(/© \d{4} pyERP System/)).toBeInTheDocument();
  });

  it('shows version number when API is available', async () => {
    // Using our new mockFetch utility
    mockFetch({
      '/health/': { 
        status: 'healthy', 
        version: '1.0.0',
        database: { status: 'healthy', message: 'Connected' },
        environment: 'test' 
      }
    });

    await act(async () => {
      render(<Footer />);
    });

    await waitFor(() => {
      expect(screen.getByText(/v1\.0\.0/)).toBeInTheDocument();
    });
  });
}
```

### Fixing Auth Hook Tests

```tsx
// authHooks.test.tsx
import { renderHook, act } from '@testing-library/react-hooks';
import { useUser, useLogin } from '@/lib/auth/authHooks';
import { createQueryClientWrapper } from '../utils/test-helpers';
import * as authService from '@/lib/auth/authService';

// Mock the service
jest.mock('@/lib/auth/authService', () => ({
  authService: {
    getCurrentUser: jest.fn(),
    login: jest.fn(),
    logout: jest.fn(),
  },
}));

describe('useUser', () => {
  it('returns user data when authenticated', async () => {
    const mockUser = { id: 1, username: 'test' };
    (authService.authService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
    
    const wrapper = createQueryClientWrapper();
    const { result, waitFor } = renderHook(() => useUser(), { wrapper });
    
    await waitFor(() => !result.current.isLoading);
    
    expect(result.current.data).toEqual(mockUser);
  });
});
```

## Success Criteria

1. Zero act() warnings in the test suite
2. Consistent API mocking across all tests
3. 80%+ coverage for critical UI components
4. No flaky tests in CI pipeline
5. Full E2E coverage of critical user journeys

## Reporting and Monitoring

We'll track progress using the following:

1. Weekly report on remaining act() warnings
2. Test coverage report for UI components
3. CI build time and reliability metrics
4. Documentation updates tracking

By following this plan, we'll significantly improve the quality and reliability of our React test suite, leading to fewer bugs and more confident releases. 