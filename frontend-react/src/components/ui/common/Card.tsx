'use client';

import React from 'react';
import {
  Card as ShadcnCard,
  CardContent as ShadcnCardContent,
  CardDescription as ShadcnCardDescription,
  CardFooter as ShadcnCardFooter,
  CardHeader as ShadcnCardHeader,
  CardTitle as ShadcnCardTitle,
} from '@/components/ui/card';
import { componentStyles, cn } from '@/lib/theme-config';
import { LucideIcon } from 'lucide-react';

// Card component with theme styling
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'highlighted';
  children?: React.ReactNode;
}

/**
 * Enhanced Card component with consistent styling
 */
export function Card({ variant = 'default', className, children, ...props }: CardProps) {
  const variantStyle = componentStyles.card[variant];
  
  return (
    <ShadcnCard className={cn(variantStyle, className)} {...props}>
      {children}
    </ShadcnCard>
  );
}

// Card Header component with theme styling
interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  highlighted?: boolean;
  children?: React.ReactNode;
}

export function CardHeader({ highlighted = false, className, children, ...props }: CardHeaderProps) {
  return (
    <ShadcnCardHeader 
      className={cn(
        highlighted && componentStyles.card.header,
        className
      )} 
      {...props}
    >
      {children}
    </ShadcnCardHeader>
  );
}

// Card Title component with theme styling
interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  icon?: LucideIcon;
  children?: React.ReactNode;
}

export function CardTitle({ icon: Icon, className, children, ...props }: CardTitleProps) {
  return (
    <ShadcnCardTitle className={cn("text-amber-500 flex items-center", className)} {...props}>
      {Icon && <Icon className="mr-2 h-5 w-5" />}
      {children}
    </ShadcnCardTitle>
  );
}

// Card Description component
export function CardDescription(props: React.HTMLAttributes<HTMLParagraphElement>) {
  return <ShadcnCardDescription {...props} />;
}

// Card Content component
export function CardContent(props: React.HTMLAttributes<HTMLDivElement>) {
  return <ShadcnCardContent {...props} />;
}

// Card Footer component with theme styling
interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  highlighted?: boolean;
  children?: React.ReactNode;
}

export function CardFooter({ highlighted = false, className, children, ...props }: CardFooterProps) {
  return (
    <ShadcnCardFooter 
      className={cn(
        highlighted && componentStyles.card.footer,
        className
      )} 
      {...props}
    >
      {children}
    </ShadcnCardFooter>
  );
} 