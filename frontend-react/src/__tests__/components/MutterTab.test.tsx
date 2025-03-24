import React from 'react';
import { render, screen } from '@testing-library/react';
import MutterTab from '@/components/mutter-tab';

// Mock the icons
jest.mock('lucide-react', () => ({
  Plus: () => <div data-testid="plus-icon" />,
  Minus: () => <div data-testid="minus-icon" />,
}));

describe('MutterTab Component', () => {
  beforeEach(() => {
    render(<MutterTab />);
  });

  test('renders input fields with correct default values', () => {
    const descriptionInput = screen.getByText(/bezeichnung/i);
    expect(descriptionInput).toBeInTheDocument();
    
    const defaultValueInput = screen.getByDisplayValue('"Adler"-Lock');
    expect(defaultValueInput).toBeInTheDocument();
    
    const textArea = screen.getByText(/beschreibung/i);
    expect(textArea).toBeInTheDocument();
    
    // Check if textarea has the default text
    const longDescription = screen.getByText(/Erleben Sie die Eleganz und den Charme vergangener Zeiten/i);
    expect(longDescription).toBeInTheDocument();
  });

  test('renders measurements section with fields', () => {
    const measurementTitle = screen.getByText('Maße');
    expect(measurementTitle).toBeInTheDocument();
    
    // Check for checkboxes
    const hangingCheckbox = screen.getByLabelText('Hängend');
    expect(hangingCheckbox).toBeInTheDocument();
    expect(hangingCheckbox).not.toBeChecked();
    
    const onesidedCheckbox = screen.getByLabelText('Einseitig');
    expect(onesidedCheckbox).toBeInTheDocument();
    expect(onesidedCheckbox).not.toBeChecked();
    
    const noveltyCheckbox = screen.getByLabelText('Neuheit');
    expect(noveltyCheckbox).toBeInTheDocument();
    expect(noveltyCheckbox).not.toBeChecked();
    
    // Check for measurements inputs
    const boxSizeInput = screen.getByDisplayValue('B5');
    expect(boxSizeInput).toBeInTheDocument();
    
    // Use getAllByDisplayValue for values that appear multiple times
    const widthInputs = screen.getAllByDisplayValue('7');
    expect(widthInputs.length).toBeGreaterThanOrEqual(1);
    
    const depthInput = screen.getByDisplayValue('0,7');
    expect(depthInput).toBeInTheDocument();
    
    const weightInput = screen.getByDisplayValue('30');
    expect(weightInput).toBeInTheDocument();
  });

  test('renders categories section with add/remove buttons', () => {
    const categoriesTitle = screen.getByText('Kategorien');
    expect(categoriesTitle).toBeInTheDocument();
    
    // Check for buttons
    expect(screen.getByTestId('plus-icon')).toBeInTheDocument();
    expect(screen.getByTestId('minus-icon')).toBeInTheDocument();
  });

  test('renders table with correct headers and content', () => {
    const headers = ['Home', 'Sortiment', 'Tradition', 'Maschinerie'];
    
    headers.forEach(header => {
      expect(screen.getAllByText(header).length).toBeGreaterThanOrEqual(1);
    });
    
    // Check for specific cell content
    expect(screen.getByText('All Products')).toBeInTheDocument();
  });

  test('renders the layout with correct structure', () => {
    // Check for the main container with padding
    const input = screen.getByDisplayValue('"Adler"-Lock');
    const container = input.closest('div');
    expect(container?.parentElement?.parentElement?.parentElement?.className).toContain('p-4');
    
    // Check for the grid layout in measurements section
    const grid = screen.getByText('Boxgröße').closest('div')?.parentElement;
    expect(grid?.className).toContain('grid');
    expect(grid?.className).toContain('grid-cols-2');
  });
  
  test('renders measurement labels', () => {
    const labels = ['Breite', 'Höhe', 'Tiefe', 'Gewicht', 'Boxgröße'];
    
    labels.forEach(label => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });
}); 