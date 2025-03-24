import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '@/components/ui/common/Button';
import { Download, Plus } from 'lucide-react';

// Mock the ShadcnButton and cn function
jest.mock('@/components/ui/button', () => ({
  Button: ({ children, className, ...props }: any) => (
    <button className={className} {...props} data-testid="shadcn-button">
      {children}
    </button>
  ),
}));

jest.mock('@/lib/utils', () => ({
  cn: (...inputs: any[]) => inputs.filter(Boolean).join(' '),
}));

jest.mock('@/lib/theme-config', () => ({
  componentStyles: {
    button: {
      base: 'base-style',
      variants: {
        primary: 'primary-style',
        secondary: 'secondary-style',
        outline: 'outline-style',
        ghost: 'ghost-style',
        link: 'link-style',
        destructive: 'destructive-style',
      },
      sizes: {
        default: 'default-size',
        sm: 'sm-size',
        lg: 'lg-size',
        icon: 'icon-size',
        xs: 'xs-size',
      },
    },
  },
}));

describe('Button Component', () => {
  it('renders correctly with default props', () => {
    render(<Button>Click me</Button>);
    
    const button = screen.getByText('Click me');
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('base-style');
    expect(button).toHaveClass('primary-style');
    expect(button).toHaveClass('default-size');
  });

  it('renders with custom className', () => {
    render(<Button className="custom-class">Click me</Button>);
    
    const button = screen.getByText('Click me');
    expect(button).toHaveClass('custom-class');
  });

  it('applies the correct variant styles', () => {
    const variants = ['primary', 'secondary', 'outline', 'ghost', 'link', 'destructive'];
    const { rerender } = render(<Button>Button</Button>);
    
    for (const variant of variants) {
      rerender(<Button variant={variant as any}>Button</Button>);
      const button = screen.getByText('Button');
      expect(button).toHaveClass(`${variant}-style`);
    }
  });

  it('applies the correct size styles', () => {
    const sizes = ['default', 'sm', 'lg', 'icon', 'xs'];
    const { rerender } = render(<Button>Button</Button>);
    
    for (const size of sizes) {
      rerender(<Button size={size as any}>Button</Button>);
      const button = screen.getByText('Button');
      expect(button).toHaveClass(`${size}-size`);
    }
  });

  it('renders with left icon', () => {
    render(<Button icon={Download}>Download</Button>);
    
    const button = screen.getByText('Download');
    // Find the icon component inside the button
    const iconElement = button.querySelector('svg');
    expect(iconElement).toBeInTheDocument();
  });

  it('renders with right icon', () => {
    render(<Button icon={Download} iconPosition="right">Download</Button>);
    
    const button = screen.getByText('Download');
    // Find the icon component inside the button
    const iconElement = button.querySelector('svg');
    expect(iconElement).toBeInTheDocument();
  });

  it('renders as full width when fullWidth is true', () => {
    render(<Button fullWidth>Full Width</Button>);
    
    const button = screen.getByText('Full Width');
    expect(button).toHaveClass('w-full');
  });

  it('renders in loading state', () => {
    render(<Button loading>Loading</Button>);
    
    const button = screen.getByText('Loading');
    expect(button).toBeDisabled();
    
    // Check for the loading spinner
    const spinner = button.querySelector('svg.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('renders as disabled', () => {
    render(<Button disabled>Disabled</Button>);
    
    const button = screen.getByText('Disabled');
    expect(button).toBeDisabled();
  });

  it('handles click events when not disabled', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick}>Click me</Button>);
    
    const button = screen.getByText('Click me');
    await user.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not trigger click events when disabled', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick} disabled>Click me</Button>);
    
    const button = screen.getByText('Click me');
    await user.click(button);
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('does not trigger click events when loading', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick} loading>Click me</Button>);
    
    const button = screen.getByText('Click me');
    await user.click(button);
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('renders an icon-only button correctly', () => {
    render(<Button size="icon" icon={Plus} aria-label="Add item" />);
    
    const button = screen.getByLabelText('Add item');
    // Icon should be present without any margin since there's no children
    const iconElement = button.querySelector('svg');
    expect(iconElement).toBeInTheDocument();
    expect(iconElement).not.toHaveClass('mr-2');
  });

  it('forwards additional HTML attributes correctly', () => {
    render(
      <Button 
        data-testid="test-button"
        aria-label="Test button"
        title="Button title"
      >
        Button
      </Button>
    );
    
    const button = screen.getByTestId('shadcn-button');
    expect(button).toHaveAttribute('aria-label', 'Test button');
    expect(button).toHaveAttribute('title', 'Button title');
  });
}); 