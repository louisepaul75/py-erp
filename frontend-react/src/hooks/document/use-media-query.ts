"use client"

import { useEffect, useState } from "react"

/**
 * Custom hook for checking if a media query matches
 * @param query The media query to check
 * @returns Whether the media query matches
 */
export function useMediaQuery(query: string): boolean {
  // Initialize with a default value (false for SSR)
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    // Create a media query list
    const media = window.matchMedia(query)

    // Set the initial value
    setMatches(media.matches)

    // Define a callback function to handle changes
    const listener = (event: MediaQueryListEvent) => {
      setMatches(event.matches)
    }

    // Add the listener
    media.addEventListener("change", listener)

    // Clean up
    return () => {
      media.removeEventListener("change", listener)
    }
  }, [query])

  return matches
}
