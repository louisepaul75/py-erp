"use client";

import type React from "react";
import { cn } from "@/lib/utils";

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  value: string;
  onValueChange: (value: string) => void;
  placeholder?: string;
  options: SelectOption[];
  error?: string;
}

export function Select({
  value,
  onValueChange,
  placeholder,
  options = [],
  error,
}: SelectProps) {
  // Stelle sicher, dass options ein Array ist
  const safeOptions = Array.isArray(options) ? options : [];

  return (
    <select
      value={value}
      onChange={(e) => onValueChange(e.target.value)}
      className={cn(
        "flex h-10 w-full rounded-md border border-slate-200 bg-white dark:border-slate-700 dark:bg-transparent px-3 py-2 text-sm text-slate-900 dark:text-slate-100 ring-offset-white focus:outline-none focus:ring-2 focus:ring-slate-950 dark:focus:ring-blue-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
        error && "border-red-500"
      )}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {safeOptions.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}

// Dummy-Komponenten für Kompatibilität
export const SelectGroup = ({ children }: { children: React.ReactNode }) => (
  <>{children}</>
);
export const SelectValue = ({ children }: { children: React.ReactNode }) => (
  <>{children}</>
);
export const SelectTrigger = ({ children }: { children: React.ReactNode }) => (
  <>{children}</>
);
export const SelectContent = ({ children }: { children: React.ReactNode }) => (
  <>{children}</>
);
export const SelectLabel = ({ children }: { children: React.ReactNode }) => (
  <>{children}</>
);
export const SelectItem = ({ children }: { children: React.ReactNode }) => (
  <>{children}</>
);
export const SelectSeparator = () => null;
export const SelectScrollUpButton = () => null;
export const SelectScrollDownButton = () => null;
