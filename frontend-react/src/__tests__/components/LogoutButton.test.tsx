import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LogoutButton } from '@/components/auth/LogoutButton';
import { useLogout } from '@/lib/auth/authHooks';

// Mock the auth hooks
jest.mock('@/lib/auth/authHooks', () => ({
  useLogout: jest.fn(),
}));

describe('LogoutButton Component', () => {
  // Mock implementation of useLogout
  const mutateMock = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock implementation for not pending state
    (useLogout as jest.Mock).mockReturnValue({
      mutate: mutateMock,
      isPending: false,
    });
  });

  it('renders correctly with default state', () => {
    render(<LogoutButton />);
    
    const button = screen.getByRole('button', { name: /abmelden/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('bg-red-500');
    expect(button).not.toBeDisabled();
  });

  it('calls logout.mutate when clicked', () => {
    render(<LogoutButton />);
    
    const button = screen.getByRole('button', { name: /abmelden/i });
    fireEvent.click(button);
    
    expect(mutateMock).toHaveBeenCalledTimes(1);
  });

  it('shows loading state when logout is pending', () => {
    // Mock the pending state
    (useLogout as jest.Mock).mockReturnValue({
      mutate: mutateMock,
      isPending: true,
    });
    
    render(<LogoutButton />);
    
    const button = screen.getByRole('button', { name: /abmeldung läuft/i });
    expect(button).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  it('has correct styling', () => {
    render(<LogoutButton />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('logout-button');
    expect(button).toHaveClass('px-4');
    expect(button).toHaveClass('py-2');
    expect(button).toHaveClass('rounded');
    expect(button).toHaveClass('bg-red-500');
    expect(button).toHaveClass('text-white');
    expect(button).toHaveClass('hover:bg-red-600');
    expect(button).toHaveClass('disabled:bg-red-300');
  });
}); 