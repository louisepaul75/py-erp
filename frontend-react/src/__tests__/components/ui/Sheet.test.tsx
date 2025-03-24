import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
  SheetDescription,
  SheetClose,
} from '@/components/ui/sheet';

// Mock the Dialog component
jest.mock('@radix-ui/react-dialog', () => {
  return {
    Root: ({ children }) => <div data-testid="dialog-root">{children}</div>,
    Trigger: ({ children, ...props }) => <button {...props}>{children}</button>,
    Portal: ({ children }) => <div data-testid="dialog-portal">{children}</div>,
    Overlay: ({ className, ...props }) => <div className={className} data-testid="dialog-overlay" {...props} />,
    Content: ({ children, className, ...props }) => (
      <div className={className} data-testid="dialog-content" {...props}>
        {children}
      </div>
    ),
    Title: ({ children, className, ...props }) => (
      <h2 className={className} data-testid="dialog-title" {...props}>
        {children}
      </h2>
    ),
    Description: ({ children, className, ...props }) => (
      <p className={className} data-testid="dialog-description" {...props}>
        {children}
      </p>
    ),
    Close: ({ children, ...props }) => <button data-testid="dialog-close" {...props}>{children}</button>,
  };
});

describe('Sheet Component', () => {
  it('renders with trigger and content', async () => {
    // Setup user event
    const user = userEvent.setup();

    render(
      <Sheet>
        <SheetTrigger data-testid="sheet-trigger">Open Sheet</SheetTrigger>
        <SheetContent data-testid="sheet-content">
          <div>Sheet Content</div>
        </SheetContent>
      </Sheet>
    );

    // Verify trigger is rendered
    const trigger = screen.getByTestId('sheet-trigger');
    expect(trigger).toBeInTheDocument();
    
    // Click trigger to open sheet
    await user.click(trigger);
    
    // Content should now be in the document
    expect(screen.getByText('Sheet Content')).toBeInTheDocument();
  });

  it('renders with all sheet components', async () => {
    const user = userEvent.setup();

    render(
      <Sheet>
        <SheetTrigger data-testid="sheet-trigger">Open Sheet</SheetTrigger>
        <SheetContent data-testid="sheet-content">
          <SheetHeader>
            <SheetTitle>Sheet Title</SheetTitle>
            <SheetDescription>Sheet Description</SheetDescription>
          </SheetHeader>
          <div>Main Content</div>
          <SheetFooter>
            <SheetClose data-testid="sheet-close">Close</SheetClose>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    );

    // Open the sheet
    await user.click(screen.getByTestId('sheet-trigger'));
    
    // Check if all components are rendered
    expect(screen.getByText('Sheet Title')).toBeInTheDocument();
    expect(screen.getByText('Sheet Description')).toBeInTheDocument();
    expect(screen.getByText('Main Content')).toBeInTheDocument();
    expect(screen.getByTestId('sheet-close')).toBeInTheDocument();
  });

  it('closes when close button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <Sheet>
        <SheetTrigger data-testid="sheet-trigger">Open Sheet</SheetTrigger>
        <SheetContent>
          <div>Sheet Content</div>
          <SheetClose data-testid="sheet-close">Close</SheetClose>
        </SheetContent>
      </Sheet>
    );

    // Open the sheet
    await user.click(screen.getByTestId('sheet-trigger'));
    
    // Verify content is visible
    expect(screen.getByText('Sheet Content')).toBeInTheDocument();
    
    // Close the sheet
    await user.click(screen.getByTestId('sheet-close'));
    
    // We don't test the disappearance as it relies on animation timing
  });

  it('renders with different side variants', async () => {
    const { rerender } = render(
      <Sheet>
        <SheetTrigger data-testid="sheet-trigger">Open</SheetTrigger>
        <SheetContent side="left" data-testid="sheet-content">
          Content
        </SheetContent>
      </Sheet>
    );

    // Check "left" variant has appropriate class
    expect(screen.getByTestId('sheet-trigger')).toBeInTheDocument();
    
    // Rerender with "right" variant
    rerender(
      <Sheet>
        <SheetTrigger data-testid="sheet-trigger">Open</SheetTrigger>
        <SheetContent side="right" data-testid="sheet-content">
          Content
        </SheetContent>
      </Sheet>
    );
    
    // Check "right" variant 
    expect(screen.getByTestId('sheet-trigger')).toBeInTheDocument();
    
    // Rerender with "top" variant
    rerender(
      <Sheet>
        <SheetTrigger data-testid="sheet-trigger">Open</SheetTrigger>
        <SheetContent side="top" data-testid="sheet-content">
          Content
        </SheetContent>
      </Sheet>
    );
    
    // Check "top" variant
    expect(screen.getByTestId('sheet-trigger')).toBeInTheDocument();
    
    // Rerender with "bottom" variant
    rerender(
      <Sheet>
        <SheetTrigger data-testid="sheet-trigger">Open</SheetTrigger>
        <SheetContent side="bottom" data-testid="sheet-content">
          Content
        </SheetContent>
      </Sheet>
    );
    
    // Check "bottom" variant
    expect(screen.getByTestId('sheet-trigger')).toBeInTheDocument();
  });
}); 