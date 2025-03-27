import React from 'react';
import { render } from '@testing-library/react';
import Home from '../../app/page';
import Dashboard from '../../app/dashboard/page';

// Mock the Dashboard component
jest.mock('../../app/dashboard/page', () => {
  return {
    __esModule: true,
    default: () => <div data-testid="dashboard">Dashboard</div>
  };
});

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the Dashboard component', () => {
    const { getByTestId } = render(<Home />);
    expect(getByTestId('dashboard')).toBeInTheDocument();
  });
}); 