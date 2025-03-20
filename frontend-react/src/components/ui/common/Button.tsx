'use client';

import React from 'react';
import { Button as ShadcnButton } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { componentStyles } from '@/lib/theme-config';
import { LucideIcon } from 'lucide-react';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'link' | 'destructive';
type ButtonSize = 'default' | 'sm' | 'lg' | 'icon' | 'xs';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  loading?: boolean;
  children?: React.ReactNode;
}

/**
 * Enhanced Button component with consistent styling
 * 
 * @example
 * // Primary button
 * <Button>Default Button</Button>
 * 
 * @example
 * // Secondary button with icon
 * <Button variant="secondary" icon={Download}>Download</Button>
 * 
 * @example
 * // Icon only button
 * <Button size="icon" icon={Plus} aria-label="Add item" />
 */
export function Button({
  variant = 'primary',
  size = 'default',
  icon: Icon,
  iconPosition = 'left',
  fullWidth = false,
  loading = false,
  className,
  children,
  ...props
}: ButtonProps) {
  // Get the appropriate styles
  const baseStyle = componentStyles.button.base;
  const variantStyle = componentStyles.button.variants[variant];
  const sizeStyle = componentStyles.button.sizes[size];
  
  return (
    <ShadcnButton
      variant={variant === 'primary' ? 'default' : variant}
      size={size}
      className={cn(
        baseStyle,
        variantStyle,
        sizeStyle,
        fullWidth ? 'w-full' : '',
        className || ''
      )}
      disabled={props.disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      
      {Icon && iconPosition === 'left' && !loading && (
        <Icon className={cn("h-4 w-4", children ? "mr-2" : "")} />
      )}
      
      {children}
      
      {Icon && iconPosition === 'right' && (
        <Icon className={cn("h-4 w-4", children ? "ml-2" : "")} />
      )}
    </ShadcnButton>
  );
} 