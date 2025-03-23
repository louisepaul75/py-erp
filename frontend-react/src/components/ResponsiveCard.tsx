import React from 'react';
import { cn } from '@/lib/utils';
import { useScreenSize } from '@/utils/responsive';
import { TouchFeedback } from './TouchFeedback';

type ResponsiveCardProps = {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
  onClick?: () => void;
  footer?: React.ReactNode;
};

export function ResponsiveCard({
  title,
  description,
  icon,
  children,
  className,
  onClick,
  footer,
}: ResponsiveCardProps) {
  const { isMobile } = useScreenSize();

  const cardContent = (
    <>
      <div className={cn(
        "flex items-start", 
        isMobile ? "flex-col space-y-2" : "space-x-4"
      )}>
        {icon && (
          <div className={cn(
            "flex-shrink-0",
            isMobile ? "mb-1" : ""
          )}>
            {icon}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h3 className={cn(
            "font-medium text-gray-900 dark:text-gray-100",
            isMobile ? "text-lg" : "text-xl"
          )}>
            {title}
          </h3>
          {description && (
            <p className="mt-1 text-gray-500 dark:text-gray-400 text-sm">
              {description}
            </p>
          )}
        </div>
      </div>
      
      {children && (
        <div className={cn("mt-4", isMobile ? "text-sm" : "")}>
          {children}
        </div>
      )}
      
      {footer && (
        <div className={cn(
          "mt-6 pt-4 border-t border-gray-100 dark:border-gray-800",
          isMobile ? "text-sm" : ""
        )}>
          {footer}
        </div>
      )}
    </>
  );

  const cardClasses = cn(
    "bg-white dark:bg-gray-800 overflow-hidden rounded-lg shadow p-6",
    "transition-all duration-200",
    isMobile ? "p-4" : "p-6",
    className
  );

  if (onClick) {
    return (
      <TouchFeedback 
        className={cardClasses}
        activeClassName="bg-gray-50 dark:bg-gray-700"
        onClick={onClick}
      >
        {cardContent}
      </TouchFeedback>
    );
  }

  return (
    <div className={cardClasses}>
      {cardContent}
    </div>
  );
} 