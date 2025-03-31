"use client"

import { FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import type { Control } from "react-hook-form"

interface DatePickerFieldProps {
  control: Control<any>
  name: string
  label: string
  description?: string
}

export function DatePickerField({ control, name, label, description }: DatePickerFieldProps) {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className="flex flex-col">
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type="date"
              {...field}
              value={field.value ? field.value.split("T")[0] : ""}
              onChange={(e) => {
                // Wenn ein Datum ausgewählt wurde, konvertieren wir es in ein ISO-String-Format
                if (e.target.value) {
                  const date = new Date(e.target.value)
                  field.onChange(date.toISOString())
                } else {
                  field.onChange("")
                }
              }}
              className="w-full"
            />
          </FormControl>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  )
}

