import React from 'react';
import { render, screen } from '@testing-library/react';
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  StatusBadge
} from '@/components/ui/data/Table';

describe('Table Components', () => {
  describe('Table', () => {
    it('renders table with children', () => {
      render(
        <Table>
          <tbody>
            <tr>
              <td>Test Content</td>
            </tr>
          </tbody>
        </Table>
      );
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      const { container } = render(
        <Table className="custom-table">
          <tbody>
            <tr>
              <td>Content</td>
            </tr>
          </tbody>
        </Table>
      );
      const table = container.querySelector('table');
      expect(table).toHaveClass('custom-table');
    });

    it('applies default styles', () => {
      const { container } = render(
        <Table>
          <tbody>
            <tr>
              <td>Content</td>
            </tr>
          </tbody>
        </Table>
      );
      const wrapper = container.firstChild as HTMLElement;
      expect(wrapper).toHaveClass('rounded-md', 'border', 'overflow-hidden');
      
      const table = container.querySelector('table');
      expect(table).toHaveClass('w-full', 'text-sm');
    });
  });

  describe('TableHeader', () => {
    it('renders header with children', () => {
      render(
        <table>
          <TableHeader>
            <tr>
              <th>Header Content</th>
            </tr>
          </TableHeader>
        </table>
      );
      expect(screen.getByText('Header Content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <table>
          <TableHeader className="custom-header">
            <tr>
              <th>Header</th>
            </tr>
          </TableHeader>
        </table>
      );
      const header = screen.getByRole('rowgroup');
      expect(header).toHaveClass('custom-header');
    });
  });

  describe('TableBody', () => {
    it('renders body with children', () => {
      render(
        <table>
          <TableBody>
            <tr>
              <td>Body Content</td>
            </tr>
          </TableBody>
        </table>
      );
      expect(screen.getByText('Body Content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <table>
          <TableBody className="custom-body">
            <tr>
              <td>Content</td>
            </tr>
          </TableBody>
        </table>
      );
      const body = screen.getByRole('rowgroup');
      expect(body).toHaveClass('custom-body');
    });
  });

  describe('TableRow', () => {
    it('renders row with children', () => {
      render(
        <table>
          <tbody>
            <TableRow>
              <td>Row Content</td>
            </TableRow>
          </tbody>
        </table>
      );
      expect(screen.getByText('Row Content')).toBeInTheDocument();
    });

    it('applies custom className', () => {
      render(
        <table>
          <tbody>
            <TableRow className="custom-row">
              <td>Content</td>
            </TableRow>
          </tbody>
        </table>
      );
      const row = screen.getByRole('row');
      expect(row).toHaveClass('custom-row');
    });
  });

  describe('TableHead', () => {
    it('renders header cell with children', () => {
      render(
        <table>
          <thead>
            <tr>
              <TableHead>Header Cell</TableHead>
            </tr>
          </thead>
        </table>
      );
      expect(screen.getByText('Header Cell')).toBeInTheDocument();
    });

    it('applies default styles', () => {
      render(
        <table>
          <thead>
            <tr>
              <TableHead>Header</TableHead>
            </tr>
          </thead>
        </table>
      );
      const headerCell = screen.getByRole('columnheader');
      expect(headerCell).toHaveClass('px-4', 'py-3', 'text-left', 'font-medium');
    });

    it('applies custom className', () => {
      render(
        <table>
          <thead>
            <tr>
              <TableHead className="custom-header-cell">Header</TableHead>
            </tr>
          </thead>
        </table>
      );
      const headerCell = screen.getByRole('columnheader');
      expect(headerCell).toHaveClass('custom-header-cell');
    });
  });

  describe('TableCell', () => {
    it('renders cell with children', () => {
      render(
        <table>
          <tbody>
            <tr>
              <TableCell>Cell Content</TableCell>
            </tr>
          </tbody>
        </table>
      );
      expect(screen.getByText('Cell Content')).toBeInTheDocument();
    });

    it('applies default styles', () => {
      render(
        <table>
          <tbody>
            <tr>
              <TableCell>Content</TableCell>
            </tr>
          </tbody>
        </table>
      );
      const cell = screen.getByRole('cell');
      expect(cell).toHaveClass('px-4', 'py-3');
    });

    it('applies custom className', () => {
      render(
        <table>
          <tbody>
            <tr>
              <TableCell className="custom-cell">Content</TableCell>
            </tr>
          </tbody>
        </table>
      );
      const cell = screen.getByRole('cell');
      expect(cell).toHaveClass('custom-cell');
    });
  });

  describe('StatusBadge', () => {
    it('renders active status correctly', () => {
      render(<StatusBadge status="active">Active</StatusBadge>);
      const badge = screen.getByText('Active');
      expect(badge).toHaveClass(
        'bg-green-100',
        'text-green-800',
        'border-green-200'
      );
    });

    it('renders pending status correctly', () => {
      render(<StatusBadge status="pending">Pending</StatusBadge>);
      const badge = screen.getByText('Pending');
      expect(badge).toHaveClass(
        'bg-yellow-100',
        'text-yellow-800',
        'border-yellow-200'
      );
    });

    it('renders inactive status correctly', () => {
      render(<StatusBadge status="inactive">Inactive</StatusBadge>);
      const badge = screen.getByText('Inactive');
      expect(badge).toHaveClass(
        'bg-gray-100',
        'text-gray-800',
        'border-gray-200'
      );
    });

    it('applies custom className', () => {
      render(
        <StatusBadge status="active" className="custom-badge">
          Active
        </StatusBadge>
      );
      const badge = screen.getByText('Active');
      expect(badge).toHaveClass('custom-badge');
    });

    it('applies default badge styles', () => {
      render(<StatusBadge status="active">Active</StatusBadge>);
      const badge = screen.getByText('Active');
      expect(badge).toHaveClass(
        'inline-flex',
        'items-center',
        'rounded-full',
        'px-2.5',
        'py-0.5',
        'text-xs',
        'font-medium'
      );
    });
  });
}); 