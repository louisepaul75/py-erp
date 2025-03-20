import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';

type TouchFeedbackProps = {
  children: React.ReactNode;
  className?: string;
  activeClassName?: string;
  onClick?: () => void;
  disabled?: boolean;
};

export const TouchFeedback: React.FC<TouchFeedbackProps> = ({
  children,
  className = '',
  activeClassName = 'bg-opacity-10 bg-primary',
  onClick,
  disabled = false,
}) => {
  const [isActive, setIsActive] = useState(false);

  const handleTouchStart = useCallback(() => {
    if (!disabled) setIsActive(true);
  }, [disabled]);

  const handleTouchEnd = useCallback(() => {
    if (!disabled) setIsActive(false);
  }, [disabled]);

  const handleClick = useCallback(() => {
    if (!disabled && onClick) onClick();
  }, [disabled, onClick]);

  return (
    <div
      className={cn(
        className,
        isActive && activeClassName,
        disabled && 'opacity-50 cursor-not-allowed'
      )}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onTouchCancel={handleTouchEnd}
      onClick={handleClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}; 