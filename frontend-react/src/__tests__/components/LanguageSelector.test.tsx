import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import LanguageSelector from '@/components/LanguageSelector';

// Mock the react-i18next hook
jest.mock('react-i18next', () => {
  const changeLanguageMock = jest.fn();
  
  return {
    // this mock makes sure any components using the translate hook can use it without a warning being shown
    useTranslation: () => {
      return {
        t: (str: string) => str,
        i18n: {
          changeLanguage: changeLanguageMock,
          language: 'en'
        }
      };
    }
  };
});

describe('LanguageSelector', () => {
  beforeEach(() => {
    // Clear all mocks between tests
    jest.clearAllMocks();
  });

  it('renders correctly with default language', () => {
    render(<LanguageSelector />);
    
    // Check if the component renders with English as default (as per our mock)
    const textElement = screen.getByText(/English/i);
    expect(textElement).toBeInTheDocument();
    
    // For emojis in text content, we need to check the containing element
    const spanElement = textElement.parentElement;
    expect(spanElement?.textContent).toContain('🇬🇧');
  });

  it('opens dropdown when clicked', () => {
    render(<LanguageSelector />);
    
    // Initially dropdown is closed
    expect(screen.queryByText('Deutsch')).not.toBeInTheDocument();
    
    // Click to open dropdown
    fireEvent.click(screen.getByText(/English/i));
    
    // Check if all language options are now visible
    expect(screen.getByText('Deutsch')).toBeInTheDocument();
    expect(screen.getByText('Čeština')).toBeInTheDocument();
  });

  it('changes language when an option is selected', () => {
    // Get the mock implementation to verify the call
    const { useTranslation } = require('react-i18next');
    const { i18n } = useTranslation();
    
    render(<LanguageSelector />);
    
    // Open dropdown
    fireEvent.click(screen.getByText(/English/i));
    
    // Select German
    fireEvent.click(screen.getByText('Deutsch'));
    
    // Check if changeLanguage was called with 'de'
    expect(i18n.changeLanguage).toHaveBeenCalledWith('de');
  });
}); 