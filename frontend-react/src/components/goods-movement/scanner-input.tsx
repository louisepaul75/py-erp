"use client"

import type React from "react"

import { useRef, useEffect, type ReactNode } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface ScannerInputProps {
  label: string
  value: string
  onChange: (value: string) => void
  disabled?: boolean
  className?: string
  placeholder?: string
  icon?: ReactNode
}

export function ScannerInput({ label, value, onChange, disabled, className, placeholder, icon }: ScannerInputProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Auto-focus the input when it becomes enabled
    if (!disabled && inputRef.current) {
      inputRef.current.focus()
    }
  }, [disabled])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      if (inputRef.current?.value) {
        onChange(inputRef.current.value)
      }
    }
  }

  return (
    <div className={className}>
      {label && <Label htmlFor={label.replace(/\s+/g, "-").toLowerCase()}>{label}</Label>}
      <div className="relative">
        {icon && <div className="absolute left-2 top-1/2 transform -translate-y-1/2">{icon}</div>}
        <Input
          ref={inputRef}
          id={label ? label.replace(/\s+/g, "-").toLowerCase() : "scanner-input"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder || `Scannen oder eingeben...`}
          className={`${icon ? "pl-8" : ""} transition-all focus-visible:ring-2 focus-visible:ring-offset-1`}
          autoComplete="off"
        />
      </div>
    </div>
  )
}

