import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility function for merging Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date string to a localized date string
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

/**
 * Generate a unique mold number in the format F1xxxx
 */
export function generateMoldNumber(): string {
  // Get the highest existing mold number from the mock data
  // In a real application, this would be fetched from the database
  const highestNumber = Math.max(
    ...mockMolds.map((mold) => {
      const numPart = mold.moldNumber.substring(2)
      return Number.parseInt(numPart, 10)
    }),
    0,
  )

  // Generate the next number
  const nextNumber = highestNumber + 1

  // Format with leading zeros to ensure 4 digits
  return `F1${nextNumber.toString().padStart(4, "0")}`
}

/**
 * Mock molds data for the generateMoldNumber function
 */
const mockMolds = [{ moldNumber: "F10001" }, { moldNumber: "F10002" }, { moldNumber: "F10003" }]

