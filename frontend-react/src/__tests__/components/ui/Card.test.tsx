import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/common/Card';
import { AlertCircle } from 'lucide-react';

describe('Card Components', () => {
  describe('Card', () => {
    it('renders children correctly', () => {
      render(
        <Card>
          <div data-testid="child">Test Content</div>
        </Card>
      );
      expect(screen.getByTestId('child')).toBeInTheDocument();
    });

    it('applies default variant styles', () => {
      const { container } = render(
        <Card>
          <div>Test Content</div>
        </Card>
      );
      const card = container.firstChild;
      expect(card).toHaveClass('bg-card');
    });

    it('applies highlighted variant styles', () => {
      const { container } = render(
        <Card variant="highlighted">
          <div>Test Content</div>
        </Card>
      );
      const card = container.firstChild;
      expect(card).toHaveClass('bg-primary/10');
    });

    it('applies additional className', () => {
      const { container } = render(
        <Card className="custom-class">
          <div>Test Content</div>
        </Card>
      );
      const card = container.firstChild;
      expect(card).toHaveClass('custom-class');
    });
  });

  describe('CardHeader', () => {
    it('renders children correctly', () => {
      render(
        <CardHeader>
          <div data-testid="header-child">Header Content</div>
        </CardHeader>
      );
      expect(screen.getByTestId('header-child')).toBeInTheDocument();
    });

    it('applies highlighted styles when highlighted prop is true', () => {
      const { container } = render(
        <CardHeader highlighted>
          <div>Header Content</div>
        </CardHeader>
      );
      const header = container.firstChild;
      expect(header).toHaveClass('bg-primary/10');
    });

    it('applies additional className', () => {
      const { container } = render(
        <CardHeader className="custom-header">
          <div>Header Content</div>
        </CardHeader>
      );
      const header = container.firstChild;
      expect(header).toHaveClass('custom-header');
    });
  });

  describe('CardTitle', () => {
    it('renders children correctly', () => {
      render(
        <CardTitle>
          <span data-testid="title-child">Title Content</span>
        </CardTitle>
      );
      expect(screen.getByTestId('title-child')).toBeInTheDocument();
    });

    it('renders with icon when provided', () => {
      render(
        <CardTitle icon={AlertCircle}>
          Title with Icon
        </CardTitle>
      );
      const icon = screen.getByTestId('circlealert');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveClass('mr-2', 'h-5', 'w-5');
    });

    it('applies text-primary class by default', () => {
      const { container } = render(
        <CardTitle>Title Content</CardTitle>
      );
      const title = container.firstChild;
      expect(title).toHaveClass('text-primary');
    });

    it('applies additional className', () => {
      const { container } = render(
        <CardTitle className="custom-title">
          Title Content
        </CardTitle>
      );
      const title = container.firstChild;
      expect(title).toHaveClass('custom-title');
    });
  });

  describe('CardDescription', () => {
    it('renders children correctly', () => {
      render(
        <CardDescription>
          <span data-testid="desc-child">Description Content</span>
        </CardDescription>
      );
      expect(screen.getByTestId('desc-child')).toBeInTheDocument();
    });

    it('applies additional className', () => {
      const { container } = render(
        <CardDescription className="custom-desc">
          Description Content
        </CardDescription>
      );
      const desc = container.firstChild;
      expect(desc).toHaveClass('custom-desc');
    });
  });

  describe('CardContent', () => {
    it('renders children correctly', () => {
      render(
        <CardContent>
          <div data-testid="content-child">Card Content</div>
        </CardContent>
      );
      expect(screen.getByTestId('content-child')).toBeInTheDocument();
    });

    it('applies additional className', () => {
      const { container } = render(
        <CardContent className="custom-content">
          Content
        </CardContent>
      );
      const content = container.firstChild;
      expect(content).toHaveClass('custom-content');
    });
  });

  describe('CardFooter', () => {
    it('renders children correctly', () => {
      render(
        <CardFooter>
          <div data-testid="footer-child">Footer Content</div>
        </CardFooter>
      );
      expect(screen.getByTestId('footer-child')).toBeInTheDocument();
    });

    it('applies highlighted styles when highlighted prop is true', () => {
      const { container } = render(
        <CardFooter highlighted>
          <div>Footer Content</div>
        </CardFooter>
      );
      const footer = container.firstChild;
      expect(footer).toHaveClass('bg-primary/10');
    });

    it('applies additional className', () => {
      const { container } = render(
        <CardFooter className="custom-footer">
          <div>Footer Content</div>
        </CardFooter>
      );
      const footer = container.firstChild;
      expect(footer).toHaveClass('custom-footer');
    });
  });
}); 