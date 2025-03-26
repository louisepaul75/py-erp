import { cn } from "@/lib/utils"
import * as React from "react"

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function Container({ className, children, ...props }: ContainerProps) {
  return (
    <div className={cn("container px-4 mx-auto", className)} {...props}>
      {children}
    </div>
  )
} 