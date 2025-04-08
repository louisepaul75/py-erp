'use client' // Error components must be Client Components

import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-10rem)] text-center px-4">
      <h2 className="text-4xl font-bold mb-4">Etwas ist schiefgelaufen! (500)</h2>
      <p className="text-xl mb-8">Es gab ein Problem auf unserer Seite.</p>
      <button
        onClick={() => reset()} // Attempt to recover by re-rendering the segment
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >
        Erneut versuchen
      </button>
    </div>
  )
} 