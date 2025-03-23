import { render, screen } from '@testing-library/react';
import BilderTab from '@/components/bilder-tab';

// Mock the Lucide icons
jest.mock('lucide-react', () => ({
  Plus: () => <div data-testid="plus-icon" />,
  Minus: () => <div data-testid="minus-icon" />,
  ImageIcon: () => <div data-testid="image-icon" />,
  Upload: () => <div data-testid="upload-icon" />,
  X: () => <div data-testid="x-icon" />,
  Edit: () => <div data-testid="edit-icon" />,
}));

describe('BilderTab Component', () => {
  it('renders the component with correct title', () => {
    render(<BilderTab />);
    
    // Check if the title is rendered
    expect(screen.getByText('Bilder')).toBeInTheDocument();
  });

  it('renders action buttons', () => {
    render(<BilderTab />);
    
    // Check if the buttons are rendered
    expect(screen.getByText('Hinzufügen')).toBeInTheDocument();
    expect(screen.getByText('Entfernen')).toBeInTheDocument();
    expect(screen.getByText('Hochladen')).toBeInTheDocument();
  });

  it('renders image placeholders', () => {
    render(<BilderTab />);
    
    // Check if image placeholders are rendered
    expect(screen.getByText('Bild 1')).toBeInTheDocument();
    expect(screen.getByText('Bild 2')).toBeInTheDocument();
    expect(screen.getByText('Bild 3')).toBeInTheDocument();
    expect(screen.getByText('Bild 4')).toBeInTheDocument();
    expect(screen.getByText('Bild 5')).toBeInTheDocument();
  });

  it('renders add image placeholder', () => {
    render(<BilderTab />);
    
    // Check if the add image placeholder is rendered
    expect(screen.getByText('Bild hinzufügen')).toBeInTheDocument();
  });

  it('renders the correct icons', () => {
    render(<BilderTab />);
    
    // Check for the mocked icons
    const plusIcons = screen.getAllByTestId('plus-icon');
    expect(plusIcons.length).toBeGreaterThanOrEqual(2);
    
    const minusIcon = screen.getByTestId('minus-icon');
    expect(minusIcon).toBeInTheDocument();
    
    const uploadIcon = screen.getByTestId('upload-icon');
    expect(uploadIcon).toBeInTheDocument();
    
    const imageIcons = screen.getAllByTestId('image-icon');
    expect(imageIcons.length).toBe(5);
    
    const editIcons = screen.getAllByTestId('edit-icon');
    expect(editIcons.length).toBe(5);
    
    const xIcons = screen.getAllByTestId('x-icon');
    expect(xIcons.length).toBe(5);
  });

  it('has the correct structure', () => {
    const { container } = render(<BilderTab />);
    
    // Check if main container has correct padding
    const mainDiv = container.firstChild as HTMLElement;
    expect(mainDiv).toHaveClass('p-6');
    
    // Check if there's a card
    const card = screen.getByText('Bilder').closest('.border');
    expect(card).toBeInTheDocument();
  });
}); 