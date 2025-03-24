import { render, screen } from '@testing-library/react';
import DetailsTab from '@/components/details-tab';

describe('DetailsTab Component', () => {
  it('renders the component with correct heading and instruction text', () => {
    render(<DetailsTab />);
    
    // Check if the heading is rendered
    expect(screen.getByText('Produktdetails')).toBeInTheDocument();
    
    // Check if the instruction text is rendered
    expect(screen.getByText('Wählen Sie einen Artikel aus der Liste links, um die Details anzuzeigen.')).toBeInTheDocument();
  });

  it('has the correct container padding', () => {
    const { container } = render(<DetailsTab />);
    
    // Find the main container div
    const mainDiv = container.firstChild as HTMLElement;
    
    // Check if it has the p-4 class for padding
    expect(mainDiv).toHaveClass('p-4');
  });

  it('has the correct heading styling', () => {
    render(<DetailsTab />);
    
    const heading = screen.getByText('Produktdetails');
    
    // Check if heading has the expected classes
    expect(heading).toHaveClass('text-lg');
    expect(heading).toHaveClass('font-medium');
    expect(heading).toHaveClass('mb-4');
  });

  it('has the correct paragraph styling', () => {
    render(<DetailsTab />);
    
    const paragraph = screen.getByText('Wählen Sie einen Artikel aus der Liste links, um die Details anzuzeigen.');
    
    // Check if paragraph has the expected classes
    expect(paragraph).toHaveClass('text-sm');
    expect(paragraph).toHaveClass('text-gray-600');
  });
}); 