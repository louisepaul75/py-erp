import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '@/components/ui/common/Input';
import { Search } from 'lucide-react';

describe('Input Component', () => {
  it('renders basic input correctly', () => {
    render(<Input placeholder="Enter text" />);
    const input = screen.getByPlaceholderText('Enter text');
    expect(input).toBeInTheDocument();
  });

  it('renders with label', () => {
    render(<Input label="Username" placeholder="Enter username" />);
    const label = screen.getByText('Username');
    expect(label).toBeInTheDocument();
    expect(label).toHaveClass('text-sm', 'font-medium');
  });

  it('renders with error message', () => {
    render(
      <Input
        label="Email"
        error="Please enter a valid email"
        placeholder="Enter email"
      />
    );
    const errorMessage = screen.getByText('Please enter a valid email');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveClass('text-red-500');

    const input = screen.getByPlaceholderText('Enter email');
    expect(input).toHaveClass('border-red-500');
  });

  it('renders with left icon', () => {
    render(<Input icon={Search} placeholder="Search" />);
    const icon = screen.getByTestId('search');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('absolute', 'left-2.5', 'top-2.5');
  });

  it('renders with right icon', () => {
    render(
      <Input
        icon={Search}
        iconPosition="right"
        placeholder="Search"
      />
    );
    const icon = screen.getByTestId('search');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('absolute', 'right-2.5', 'top-2.5');

    const input = screen.getByPlaceholderText('Search');
    expect(input).toHaveClass('pr-8');
  });

  it('applies fullWidth class when fullWidth prop is true', () => {
    const { container } = render(
      <Input fullWidth placeholder="Full width input" />
    );
    const wrapper = container.firstChild as HTMLElement;
    const input = screen.getByPlaceholderText('Full width input');
    
    expect(wrapper).toHaveClass('w-full');
    expect(input).toHaveClass('w-full');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input ref={ref} placeholder="Ref test" />);
    
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it('handles user input correctly', async () => {
    const handleChange = jest.fn();
    render(
      <Input
        placeholder="Type here"
        onChange={handleChange}
      />
    );

    const input = screen.getByPlaceholderText('Type here');
    await userEvent.type(input, 'test input');

    expect(handleChange).toHaveBeenCalled();
    expect(input).toHaveValue('test input');
  });

  it('applies custom className correctly', () => {
    render(
      <Input
        className="custom-class"
        placeholder="Custom class test"
      />
    );
    const input = screen.getByPlaceholderText('Custom class test');
    expect(input).toHaveClass('custom-class');
  });

  it('passes through HTML input attributes', () => {
    render(
      <Input
        type="email"
        required
        disabled
        placeholder="Email input"
      />
    );
    const input = screen.getByPlaceholderText('Email input');
    
    expect(input).toHaveAttribute('type', 'email');
    expect(input).toBeRequired();
    expect(input).toBeDisabled();
  });

  it('renders with both label and error', () => {
    render(
      <Input
        label="Password"
        error="Password is required"
        placeholder="Enter password"
      />
    );
    
    expect(screen.getByText('Password')).toBeInTheDocument();
    expect(screen.getByText('Password is required')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter password')).toHaveClass('border-red-500');
  });
}); 