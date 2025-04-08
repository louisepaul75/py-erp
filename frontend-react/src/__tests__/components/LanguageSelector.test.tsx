import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/lib/i18n'; // Adjust path as necessary
import { LanguageSelector } from '@/components/LanguageSelector';

// Mock the react-i18next hook
const mockChangeLanguage = jest.fn();
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (str: string) => str,
    i18n: {
      changeLanguage: mockChangeLanguage,
      language: 'en'
    }
  })
}));

describe('LanguageSelector', () => {
  beforeEach(() => {
    // Clear all mocks between tests
    jest.clearAllMocks();
  });

  it('renders correctly with default language', () => {
    render(<LanguageSelector />);
    
    // Check if the button contains both the flag and language name
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('🇬🇧');
    expect(button).toHaveTextContent('English');
  });

  it('opens dropdown when clicked', async () => {
    const user = userEvent.setup();
    render(<LanguageSelector />);
    
    // Click the button to open dropdown
    const button = screen.getByRole('button');
    await user.click(button);
    
    // Wait for the dropdown to be mounted and visible
    await waitFor(() => {
      expect(button).toHaveAttribute('data-state', 'open');
      expect(document.querySelector('[role="menu"]')).toBeInTheDocument();
    });

    // Check if all languages are present in the dropdown
    const menu = document.querySelector('[role="menu"]');
    expect(menu).toBeInTheDocument();
    expect(menu).toHaveTextContent('Deutsch');
    expect(menu).toHaveTextContent('English');
    expect(menu).toHaveTextContent('Čeština');
  });

  it('changes language when an option is selected', async () => {
    const user = userEvent.setup();
    render(<LanguageSelector />);
    
    // Open dropdown
    const button = screen.getByRole('button');
    await user.click(button);
    
    // Wait for the dropdown to be mounted and visible
    await waitFor(() => {
      expect(button).toHaveAttribute('data-state', 'open');
      expect(document.querySelector('[role="menu"]')).toBeInTheDocument();
    });

    // Find and click the German option within the menu
    const menu = document.querySelector('[role="menu"]');
    const germanOption = within(menu).getByText('Deutsch');
    await user.click(germanOption);
    
    // Verify language change was called
    expect(mockChangeLanguage).toHaveBeenCalledWith('de');
  });
}); 