import React from 'react';
import { render, screen } from '@testing-library/react';
import UmsatzeTab from '@/components/umsatze-tab';

// Mock the icons
jest.mock('lucide-react', () => ({
  ArrowDown: () => <div data-testid="arrow-down-icon" />,
  TrendingUp: () => <div data-testid="trending-up-icon" />,
  Package: () => <div data-testid="package-icon" />,
  Euro: () => <div data-testid="euro-icon" />,
  Calendar: () => <div data-testid="calendar-icon" />,
  BarChart3: () => <div data-testid="bar-chart-icon" />,
}));

describe('UmsatzeTab Component', () => {
  beforeEach(() => {
    render(<UmsatzeTab />);
  });

  test('renders overview cards with correct titles', () => {
    const cardTitles = [
      'Umsatz (Jahr)', 
      'Umsatz (5 Jahre)', 
      'Stückzahl (Jahr)', 
      'Stückzahl (Gesamt)'
    ];
    
    cardTitles.forEach(title => {
      expect(screen.getByText(title)).toBeInTheDocument();
    });
  });

  test('renders values in overview cards', () => {
    const values = ['0,00 €', '455,00 €', '0', '16'];
    
    values.forEach(value => {
      expect(screen.getAllByText(value).length).toBeGreaterThanOrEqual(1);
    });
    
    // Check for comparison text
    const comparisonTexts = screen.getAllByText('100%');
    expect(comparisonTexts.length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('zum Vorjahr').length).toBeGreaterThanOrEqual(1);
  });

  test('renders all icons', () => {
    expect(screen.getAllByTestId('arrow-down-icon').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByTestId('trending-up-icon')).toBeInTheDocument();
    expect(screen.getByTestId('package-icon')).toBeInTheDocument();
    expect(screen.getByTestId('euro-icon')).toBeInTheDocument();
    expect(screen.getByTestId('calendar-icon')).toBeInTheDocument();
    expect(screen.getByTestId('bar-chart-icon')).toBeInTheDocument();
  });

  test('renders main data cards with correct titles', () => {
    expect(screen.getByText('Umsatzübersicht')).toBeInTheDocument();
    expect(screen.getByText('Lagerbestand')).toBeInTheDocument();
  });

  test('renders chart button', () => {
    const chartButton = screen.getByText('Diagramm');
    expect(chartButton).toBeInTheDocument();
  });

  test('renders table with correct headers', () => {
    const tableHeaders = ['Jahr', 'Vorjahr', '5 Jahre', 'Gesamt'];
    
    tableHeaders.forEach(header => {
      expect(screen.getByText(header)).toBeInTheDocument();
    });
  });

  test('renders table with correct row labels', () => {
    const rowLabels = ['Stück', 'EUR', 'Ø Preis'];
    
    rowLabels.forEach(label => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });

  test('renders inventory information correctly', () => {
    const inventoryLabels = [
      'Bestand', 
      'Min. Bestand', 
      'Zugang/Jahr', 
      'Letzter Zugang', 
      'Abgänge ges.', 
      'Letzter Abgang'
    ];
    
    inventoryLabels.forEach(label => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
    
    const inventoryValues = ['6', '2', '0', '22.05.2023', '19', '22.10.2024'];
    
    inventoryValues.forEach(value => {
      expect(screen.getAllByText(value).length).toBeGreaterThanOrEqual(1);
    });
  });

  test('renders table with correct monetary values', () => {
    const monetaryValues = [
      '0,00 €', 
      '76,20 €', 
      '455,00 €', 
      '561,30 €', 
      '25,40 €', 
      '35,00 €', 
      '35,08 €'
    ];
    
    monetaryValues.forEach(value => {
      expect(screen.getAllByText(value).length).toBeGreaterThanOrEqual(1);
    });
  });

  test('renders sparklines', () => {
    // Check for sparkline containers
    const cardContents = document.querySelectorAll('.p-4.pt-0');
    let foundSparkline = false;
    
    cardContents.forEach(content => {
      const sparklineElements = content.querySelectorAll('.flex.items-end.h-8.w-full.gap-\\[1px\\]');
      if (sparklineElements.length > 0) {
        foundSparkline = true;
      }
    });
    
    expect(foundSparkline).toBeTruthy();
  });
}); 