import React from 'react';
import { render } from '@testing-library/react';
import ConnectionStatusAnimation from '@/components/ConnectionStatusAnimation';

describe('ConnectionStatusAnimation', () => {
  beforeEach(() => {
    // Mock canvas methods
    HTMLCanvasElement.prototype.getContext = jest.fn().mockReturnValue({
      clearRect: jest.fn(),
      fillStyle: '',
      globalAlpha: 1,
      beginPath: jest.fn(),
      rect: jest.fn(),
      fill: jest.fn(),
      strokeStyle: '',
      lineWidth: 1,
      moveTo: jest.fn(),
      lineTo: jest.fn(),
      stroke: jest.fn(),
    });

    // Mock requestAnimationFrame to only execute once and then return without recursion
    const originalRAF = window.requestAnimationFrame;
    let hasExecuted = false;
    jest.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => {
      if (!hasExecuted) {
        hasExecuted = true;
        callback(0);
      }
      return 0;
    });

    // Mock cancelAnimationFrame
    jest.spyOn(window, 'cancelAnimationFrame').mockImplementation(jest.fn());

    // Mock canvas offsetWidth and offsetHeight
    Object.defineProperty(HTMLCanvasElement.prototype, 'offsetWidth', {
      configurable: true,
      value: 200,
    });

    Object.defineProperty(HTMLCanvasElement.prototype, 'offsetHeight', {
      configurable: true,
      value: 100,
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders without crashing', () => {
    const { container } = render(
      <ConnectionStatusAnimation status="healthy" />
    );
    expect(container.querySelector('canvas')).toBeInTheDocument();
  });

  it('applies the correct class name', () => {
    const { container } = render(
      <ConnectionStatusAnimation status="healthy" className="test-class" />
    );
    expect(container.querySelector('canvas')).toHaveClass('test-class');
  });

  it('creates the animation for healthy status', () => {
    render(
      <ConnectionStatusAnimation 
        status="healthy" 
        transactionCount={100} 
        transactionSpeed={200} 
      />
    );

    // Verify canvas context is called
    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
    
    // Verify requestAnimationFrame is called
    expect(window.requestAnimationFrame).toHaveBeenCalled();
  });

  it('creates the animation for warning status', () => {
    render(
      <ConnectionStatusAnimation 
        status="warning" 
        transactionCount={50} 
        transactionSpeed={500} 
      />
    );

    // Verify canvas context is called
    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
    
    // Verify requestAnimationFrame is called
    expect(window.requestAnimationFrame).toHaveBeenCalled();
  });

  it('creates the animation for error status', () => {
    render(
      <ConnectionStatusAnimation 
        status="error" 
        transactionCount={20} 
        transactionSpeed={1000} 
      />
    );

    // Verify canvas context is called
    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
    
    // Verify requestAnimationFrame is called
    expect(window.requestAnimationFrame).toHaveBeenCalled();
  });

  it('creates the animation for unknown status', () => {
    render(
      <ConnectionStatusAnimation 
        status="unknown" 
      />
    );

    // Verify canvas context is called
    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
    
    // Verify requestAnimationFrame is called
    expect(window.requestAnimationFrame).toHaveBeenCalled();
  });

  it('cleans up animation on unmount', () => {
    const { unmount } = render(
      <ConnectionStatusAnimation status="healthy" />
    );

    unmount();
    
    // Verify cancelAnimationFrame is called on unmount
    expect(window.cancelAnimationFrame).toHaveBeenCalled();
  });

  it('handles missing canvas context gracefully', () => {
    // Mock getContext to return null
    HTMLCanvasElement.prototype.getContext = jest.fn().mockReturnValue(null);
    
    // This should not throw
    expect(() => {
      render(<ConnectionStatusAnimation status="healthy" />);
    }).not.toThrow();
  });

  it('does not crash when transaction values are out of normal ranges', () => {
    // This should not throw with extreme values
    render(
      <ConnectionStatusAnimation 
        status="healthy" 
        transactionCount={99999} 
        transactionSpeed={1} 
      />
    );
    
    // This should not throw with negative values
    render(
      <ConnectionStatusAnimation 
        status="healthy" 
        transactionCount={-50} 
        transactionSpeed={-200} 
      />
    );
  });
}); 