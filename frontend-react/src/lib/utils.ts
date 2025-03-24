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

