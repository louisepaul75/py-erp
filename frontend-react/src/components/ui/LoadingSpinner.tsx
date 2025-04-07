import React from 'react';

interface LoadingSpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  ...props 
}) => {
  const sizeMap = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div 
      className="flex justify-center items-center" 
      role="status"
      aria-label="Loading"
      {...props}
    >
      <div className={`animate-spin rounded-full border-t-2 border-b-2 border-primary ${sizeMap[size]}`}></div>
    </div>
  );
}; 