/**
 * Utility functions for handling static assets and URLs
 */

// Import the base URL determination function from the API service
import { determineBaseUrl } from '@/services/api';

/**
 * Get the correct URL for a static asset
 * @param path The path to the static asset, relative to the static directory
 * @returns The full URL to the static asset
 */
export const getStaticAssetUrl = (path: string): string => {
  // Get the base URL for the current environment
  const baseUrl = determineBaseUrl();
  
  // Ensure path starts with a slash
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  
  // Return the full URL
  return `${baseUrl}${normalizedPath}`;
};

/**
 * Get a fallback image URL when the primary image is not available
 * @returns The URL to the no-image placeholder
 */
export const getNoImageUrl = (): string => {
  return getStaticAssetUrl('/static/images/no-image.png');
};

/**
 * Validate an image URL and return a fallback if invalid
 * @param imageObj The image object with a URL property
 * @returns A valid image URL or the fallback no-image URL
 */
export const getValidImageUrl = (imageObj?: { url?: string }): string => {
  // If no image object or URL, return placeholder
  if (!imageObj?.url) {
    return getNoImageUrl();
  }

  // Check if URL is valid
  try {
    new URL(imageObj.url);
    return imageObj.url;
  } catch (e) {
    return getNoImageUrl();
  }
};

/**
 * Handle image loading errors by replacing with the no-image placeholder
 * @param event The error event from the image
 */
export const handleImageError = (event: Event): void => {
  const img = event.target as HTMLImageElement;
  img.src = getNoImageUrl();
}; 