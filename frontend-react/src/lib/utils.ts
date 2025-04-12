import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Safely get an element from the DOM, ensuring it exists before accessing properties
 * @param selector CSS selector or element ID
 * @param parent Optional parent element to search within
 * @returns The element or null if not found
 */
export function safeGetElement(
  selector: string | null | undefined,
  parent: Element | Document = document
): Element | null {
  if (!selector) return null;
  try {
    // If selector starts with #, assume it's an ID
    if (typeof selector === 'string' && selector.startsWith('#')) {
      return document.getElementById(selector.substring(1));
    }
    return parent.querySelector(selector);
  } catch (error) {
    console.error('Error accessing DOM element:', error);
    return null;
  }
}

/**
 * Safely get text content from an element
 * @param element DOM element or selector
 * @returns The text content or empty string if element is null
 */
export function safeGetTextContent(
  element: Element | string | null | undefined
): string {
  if (!element) return '';
  
  try {
    const el = typeof element === 'string' ? safeGetElement(element) : element;
    return el?.textContent || '';
  } catch (error) {
    console.error('Error getting text content:', error);
    return '';
  }
}

/**
 * Formats a date string or Date object into a localized string.
 * @param date The date to format (string, Date, or null/undefined)
 * @param options Intl.DateTimeFormat options
 * @returns Formatted date string or '-' if date is invalid
 */
export function formatDate(
  date: string | Date | null | undefined,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }
): string {
  if (!date) return '-';
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    // Check if the date is valid
    if (isNaN(dateObj.getTime())) {
        console.warn("Invalid date provided to formatDate:", date);
        return '-';
    }
    return new Intl.DateTimeFormat('default', options).format(dateObj);
  } catch (error) {
    console.error("Error formatting date:", error);
    return '-';
  }
}

