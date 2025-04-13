"use client";

import React, { useState, ReactNode } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Maximize, Minimize, ArrowLeftToLine, ArrowRightToLine } from 'lucide-react';
import { cn } from "@/lib/utils"; // Assuming you have a utility for class names

export type MaximizedPaneState = 'left' | 'right' | 'none';

interface TwoPaneLayoutProps {
  leftPaneContent: ReactNode;
  rightPaneContent: ReactNode;
  leftPaneClassName?: string;
  rightPaneClassName?: string;
  containerClassName?: string;
  initialLeftPaneWidth?: string; // e.g., 'w-1/3', 'w-1/4'
  initialRightPaneWidth?: string; // e.g., 'w-2/3', 'w-3/4'
  maximizedPaneOverride?: MaximizedPaneState; // Allow external control
  onMaximizeChange?: (newState: MaximizedPaneState) => void; // Callback for state change
}

export function TwoPaneLayout({
  leftPaneContent,
  rightPaneContent,
  leftPaneClassName = "",
  rightPaneClassName = "",
  containerClassName = "gap-4",
  initialLeftPaneWidth = "md:w-1/3",
  initialRightPaneWidth = "md:w-2/3",
  maximizedPaneOverride,
  onMaximizeChange
}: TwoPaneLayoutProps) {
  const [internalMaximizedPane, setInternalMaximizedPane] = useState<MaximizedPaneState>('none');

  // Determine the effective state: use override if provided, otherwise internal state
  const maximizedPane = maximizedPaneOverride !== undefined ? maximizedPaneOverride : internalMaximizedPane;
  const setMaximizedPane = (newState: MaximizedPaneState) => {
    if (onMaximizeChange) {
      onMaximizeChange(newState);
    } else {
      setInternalMaximizedPane(newState);
    }
  };

  const isLeftMaximized = maximizedPane === 'left';
  const isRightMaximized = maximizedPane === 'right';
  const isSplit = maximizedPane === 'none';

  const toggleLeftMax = () => {
    const nextState: MaximizedPaneState = maximizedPane === 'left' ? 'none' : 'left';
    setMaximizedPane(nextState);
  };
  const toggleRightMax = () => {
    const nextState: MaximizedPaneState = maximizedPane === 'right' ? 'none' : 'right';
    setMaximizedPane(nextState);
  };

  return (
    <div className={cn("flex flex-col md:flex-row h-full", containerClassName)}>
      {/* Left Pane */}
      {!isRightMaximized && (
        <Card className={cn(
          "flex flex-col relative",
          isLeftMaximized ? "w-full" : `w-full ${initialLeftPaneWidth}`,
          leftPaneClassName
        )}>
          {/* Maximize/Minimize button for Left Pane */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-2 right-2 z-10 h-7 w-7"
            onClick={toggleLeftMax}
            title={isLeftMaximized ? "Restore Panes" : "Maximize Left Pane"}
          >
            {isLeftMaximized ? <ArrowRightToLine className="h-4 w-4" /> : <ArrowLeftToLine className="h-4 w-4" />}
          </Button>
           {/* Hide minimize button for right pane when left is maximized */}
          {!isLeftMaximized && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-10 z-10 h-7 w-7 md:hidden" // Only show on mobile when split
              onClick={toggleRightMax} // This should hide the left pane
              title={"Maximize Right Pane"}
             >
               <ArrowRightToLine className="h-4 w-4" />
            </Button>
          )}
          {leftPaneContent}
        </Card>
      )}

      {/* Right Pane */}
      {!isLeftMaximized && (
        <Card className={cn(
          "flex flex-col relative",
          isRightMaximized ? "w-full" : `w-full ${initialRightPaneWidth}`,
          rightPaneClassName
        )}>
           {/* Maximize/Minimize button for Right Pane */}
           <Button
             variant="ghost"
             size="icon"
             className="absolute top-2 right-2 z-10 h-7 w-7"
             onClick={toggleRightMax}
             title={isRightMaximized ? "Restore Panes" : "Maximize Right Pane"}
           >
             {isRightMaximized ? <ArrowLeftToLine className="h-4 w-4" /> : <ArrowRightToLine className="h-4 w-4" />}
           </Button>
            {/* Hide minimize button for left pane when right is maximized */}
           {!isRightMaximized && (
             <Button
               variant="ghost"
               size="icon"
               className="absolute top-2 left-2 z-10 h-7 w-7 md:hidden" // Only show on mobile when split
               onClick={toggleLeftMax} // This should hide the right pane
               title={"Maximize Left Pane"}
             >
               <ArrowLeftToLine className="h-4 w-4" />
             </Button>
           )}
          {rightPaneContent}
        </Card>
      )}
    </div>
  );
} 