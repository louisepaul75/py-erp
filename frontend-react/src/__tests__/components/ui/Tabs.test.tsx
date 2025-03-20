import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';

describe('Tabs component', () => {
  it('renders tabs and verifies tab triggers', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          <TabsTrigger value="tab2">Tab 2</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Tab 1 Content</TabsContent>
        <TabsContent value="tab2">Tab 2 Content</TabsContent>
      </Tabs>
    );
    
    // Check tab triggers are rendered with correct state
    const tab1Trigger = screen.getByRole('tab', { name: 'Tab 1' });
    const tab2Trigger = screen.getByRole('tab', { name: 'Tab 2' });
    
    expect(tab1Trigger).toBeInTheDocument();
    expect(tab2Trigger).toBeInTheDocument();
    
    // Check default states
    expect(tab1Trigger).toHaveAttribute('data-state', 'active');
    expect(tab2Trigger).toHaveAttribute('data-state', 'inactive');
    
    // We can check the tabpanel is in the document
    const tabPanels = screen.getAllByRole('tabpanel');
    const activePanel = tabPanels.find(panel => panel.getAttribute('data-state') === 'active');
    expect(activePanel).toBeDefined();
  });
  
  it('applies custom classes to tabs components', () => {
    render(
      <Tabs defaultValue="tab1">
        <TabsList className="custom-list-class">
          <TabsTrigger value="tab1" className="custom-trigger-class">Tab 1</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1" className="custom-content-class">Content</TabsContent>
      </Tabs>
    );
    
    // Verify custom classes are applied
    expect(screen.getByRole('tablist')).toHaveClass('custom-list-class');
    expect(screen.getByRole('tab')).toHaveClass('custom-trigger-class');
    expect(screen.getByRole('tabpanel')).toHaveClass('custom-content-class');
  });
  
  it('forwards refs correctly', () => {
    const listRef = React.createRef<HTMLDivElement>();
    const triggerRef = React.createRef<HTMLButtonElement>();
    const contentRef = React.createRef<HTMLDivElement>();
    
    render(
      <Tabs defaultValue="tab1">
        <TabsList ref={listRef}>
          <TabsTrigger value="tab1" ref={triggerRef}>Tab 1</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1" ref={contentRef}>Content</TabsContent>
      </Tabs>
    );
    
    // Verify refs are populated
    expect(listRef.current).not.toBeNull();
    expect(triggerRef.current).not.toBeNull();
    expect(contentRef.current).not.toBeNull();
  });
  
  it('supports additional props', () => {
    render(
      <Tabs defaultValue="tab1" data-testid="tabs-root">
        <TabsList data-testid="tabs-list">
          <TabsTrigger value="tab1" data-testid="tabs-trigger">Tab 1</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1" data-testid="tabs-content">Content</TabsContent>
      </Tabs>
    );
    
    // Verify data-testid props are passed through
    expect(screen.getByTestId('tabs-root')).toBeInTheDocument();
    expect(screen.getByTestId('tabs-list')).toBeInTheDocument();
    expect(screen.getByTestId('tabs-trigger')).toBeInTheDocument();
    expect(screen.getByTestId('tabs-content')).toBeInTheDocument();
  });
  
  it('activates the correct tab with defaultValue', () => {
    render(
      <Tabs defaultValue="tab2">
        <TabsList>
          <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          <TabsTrigger value="tab2">Tab 2</TabsTrigger>
        </TabsList>
        <TabsContent value="tab1">Tab 1 Content</TabsContent>
        <TabsContent value="tab2">Tab 2 Content</TabsContent>
      </Tabs>
    );
    
    // Check second tab is active by default
    const tab1Trigger = screen.getByRole('tab', { name: 'Tab 1' });
    const tab2Trigger = screen.getByRole('tab', { name: 'Tab 2' });
    
    expect(tab1Trigger).toHaveAttribute('data-state', 'inactive');
    expect(tab2Trigger).toHaveAttribute('data-state', 'active');
    
    // The active tab panel should be associated with the active tab trigger
    const tabPanels = screen.getAllByRole('tabpanel');
    const activePanel = tabPanels.find(panel => panel.getAttribute('data-state') === 'active');
    expect(activePanel).toBeDefined();
    expect(activePanel).toHaveAttribute('aria-labelledby', tab2Trigger.id);
  });
}); 