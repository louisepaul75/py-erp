import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button, buttonVariants } from '@/components/ui/button';

// Mock the cn function from utils
jest.mock('@/lib/utils', () => ({
  cn: (...inputs: any[]) => inputs.filter(Boolean).join(' '),
}));

// Mock class-variance-authority
jest.mock('class-variance-authority', () => {
  const mockCva = () => {
    const variantFn = jest.fn(({ variant, size, className } = {}) => {
      const classes = ['button-base-class'];
      
      if (variant) {
        classes.push(`variant-${variant}`);
      }
      
      if (size) {
        classes.push(`size-${size}`);
      }
      
      if (className) {
        classes.push(className);
      }
      
      return classes.join(' ');
    });
    
    return variantFn;
  };
  
  return { cva: mockCva };
});

describe('Button Component', () => {
  it('renders correctly with default props', () => {
    render(<Button>Click me</Button>);
    
    const button = screen.getByRole('button', { name: 'Click me' });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('button-base-class');
    expect(button).toHaveClass('variant-default');
    expect(button).toHaveClass('size-default');
  });

  it('renders with custom className', () => {
    render(<Button className="custom-class">Click me</Button>);
    
    const button = screen.getByRole('button', { name: 'Click me' });
    expect(button).toHaveClass('custom-class');
  });

  it('renders all variant styles correctly', () => {
    const variants = ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'];
    const { rerender } = render(<Button>Button</Button>);
    
    for (const variant of variants) {
      rerender(<Button variant={variant as any}>Button</Button>);
      const button = screen.getByRole('button', { name: 'Button' });
      expect(button).toHaveClass(`variant-${variant}`);
    }
  });

  it('renders all size variants correctly', () => {
    const sizes = ['default', 'sm', 'lg', 'icon', 'xs'];
    const { rerender } = render(<Button>Button</Button>);
    
    for (const size of sizes) {
      rerender(<Button size={size as any}>Button</Button>);
      const button = screen.getByRole('button', { name: 'Button' });
      expect(button).toHaveClass(`size-${size}`);
    }
  });

  it('renders a disabled button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    
    const button = screen.getByRole('button', { name: 'Disabled' });
    expect(button).toBeDisabled();
  });

  it('handles click events', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick}>Click me</Button>);
    
    const button = screen.getByRole('button', { name: 'Click me' });
    await user.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', async () => {
    const handleClick = jest.fn();
    const user = userEvent.setup();
    
    render(<Button onClick={handleClick} disabled>Click me</Button>);
    
    const button = screen.getByRole('button', { name: 'Click me' });
    await user.click(button);
    
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('renders with form attributes', () => {
    render(
      <Button form="test-form" type="submit" formAction="/submit">
        Submit
      </Button>
    );
    
    const button = screen.getByRole('button', { name: 'Submit' });
    expect(button).toHaveAttribute('form', 'test-form');
    expect(button).toHaveAttribute('type', 'submit');
    expect(button).toHaveAttribute('formAction', '/submit');
  });

  it('forwards ref to the button element', () => {
    const ref = React.createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Button with ref</Button>);
    
    expect(ref.current).not.toBeNull();
    expect(ref.current?.tagName).toBe('BUTTON');
    expect(ref.current?.textContent).toBe('Button with ref');
  });

  it('renders as a custom element when asChild is true', () => {
    render(
      <Button asChild>
        <a href="/">Link Button</a>
      </Button>
    );
    
    const linkButton = screen.getByRole('link', { name: 'Link Button' });
    expect(linkButton).toBeInTheDocument();
    expect(linkButton).toHaveAttribute('href', '/');
    expect(linkButton).toHaveClass('button-base-class');
  });

  it('accepts and applies additional HTML attributes', () => {
    render(
      <Button
        data-testid="test-button"
        aria-label="Test button"
        title="Button title"
      >
        Button
      </Button>
    );
    
    const button = screen.getByTestId('test-button');
    expect(button).toHaveAttribute('aria-label', 'Test button');
    expect(button).toHaveAttribute('title', 'Button title');
  });

  it('renders button with children correctly', () => {
    render(
      <Button>
        <span data-testid="icon">🔍</span>
        <span>Search</span>
      </Button>
    );
    
    const button = screen.getByRole('button');
    const icon = screen.getByTestId('icon');
    
    expect(button).toContainElement(icon);
    expect(button).toHaveTextContent('🔍Search');
  });

  it('exports buttonVariants for use in other components', () => {
    // Test that buttonVariants is exported and is a function
    expect(typeof buttonVariants).toBe('function');
  });
}); 