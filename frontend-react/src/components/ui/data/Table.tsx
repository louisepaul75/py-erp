'use client';

import React from 'react';
import { componentStyles, cn } from '@/lib/theme-config';

interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  children: React.ReactNode;
}

/**
 * Enhanced Table component with consistent styling
 */
export function Table({ className, children, ...props }: TableProps) {
  return (
    <div className={cn("rounded-md border overflow-hidden", componentStyles.table.border)}>
      <table className={cn("w-full text-sm", className)} {...props}>
        {children}
      </table>
    </div>
  );
}

interface TableHeaderProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export function TableHeader({ className, children, ...props }: TableHeaderProps) {
  return (
    <thead className={cn(componentStyles.table.header, className)} {...props}>
      {children}
    </thead>
  );
}

interface TableBodyProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export function TableBody({ className, children, ...props }: TableBodyProps) {
  return (
    <tbody 
      className={cn("divide-y", componentStyles.table.divider, className)} 
      {...props}
    >
      {children}
    </tbody>
  );
}

interface TableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  children: React.ReactNode;
}

export function TableRow({ className, children, ...props }: TableRowProps) {
  return (
    <tr className={cn(componentStyles.table.row, className)} {...props}>
      {children}
    </tr>
  );
}

interface TableHeadProps extends React.ThHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode;
}

export function TableHead({ className, children, ...props }: TableHeadProps) {
  return (
    <th 
      className={cn(
        "px-4 py-3 text-left font-medium", 
        componentStyles.table.headerText,
        className
      )} 
      {...props}
    >
      {children}
    </th>
  );
}

interface TableCellProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode;
}

export function TableCell({ className, children, ...props }: TableCellProps) {
  return (
    <td className={cn("px-4 py-3", className)} {...props}>
      {children}
    </td>
  );
}

interface StatusBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: 'active' | 'pending' | 'inactive';
  children: React.ReactNode;
}

export function StatusBadge({ status, className, children, ...props }: StatusBadgeProps) {
  return (
    <span 
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        componentStyles.status[status],
        className
      )} 
      {...props}
    >
      {children}
    </span>
  );
} 