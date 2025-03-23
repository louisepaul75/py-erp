import React from 'react';
import { render } from '@testing-library/react';
import Loading from '../../app/loading';

describe('Loading', () => {
  it('renders without crashing and returns null', () => {
    const { container } = render(<Loading />);
    
    // The component returns null, so the container should be empty
    expect(container.firstChild).toBeNull();
  });
}); 