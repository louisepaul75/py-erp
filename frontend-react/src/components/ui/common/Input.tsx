'use client';

import React, { forwardRef } from 'react';
import { Input as ShadcnInput } from '@/components/ui/input';
import { componentStyles, cn } from '@/lib/theme-config';
import { LucideIcon } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  label?: string;
  error?: string;
  fullWidth?: boolean;
}

/**
 * Enhanced Input component with consistent styling
 * 
 * @example
 * // Basic input with label
 * <Input label="Username" placeholder="Enter username" />
 * 
 * @example
 * // Input with icon
 * <Input icon={Search} placeholder="Search..." />
 * 
 * @example
 * // Input with error
 * <Input label="Email" error="Please enter a valid email" />
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    icon: Icon, 
    iconPosition = 'left', 
    label, 
    error, 
    fullWidth = false,
    className,
    ...props 
  }, ref) => {
    // Determine the appropriate style
    const inputStyle = Icon 
      ? componentStyles.input.withIcon 
      : componentStyles.input.default;
    
    return (
      <div className={cn("space-y-2", fullWidth ? "w-full" : "")}>
        {label && (
          <label className="text-sm font-medium block">
            {label}
          </label>
        )}
        
        <div className="relative">
          {Icon && iconPosition === 'left' && (
            <Icon 
              className="absolute left-2.5 top-2.5 h-4 w-4 text-amber-500 dark:text-amber-400" 
              data-testid={Icon.displayName?.toLowerCase() || 'icon'} 
            />
          )}
          
          <ShadcnInput
            ref={ref}
            className={cn(
              inputStyle,
              error ? "border-red-500 focus:border-red-500" : "",
              iconPosition === 'right' && Icon ? "pr-8" : "",
              fullWidth ? "w-full" : "",
              "dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:placeholder:text-gray-400",
              className || ""
            )}
            {...props}
          />
          
          {Icon && iconPosition === 'right' && (
            <Icon 
              className="absolute right-2.5 top-2.5 h-4 w-4 text-amber-500 dark:text-amber-400" 
              data-testid={Icon.displayName?.toLowerCase() || 'icon'} 
            />
          )}
        </div>
        
        {error && (
          <p className="text-xs text-red-500 dark:text-red-400 mt-1">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input'; 