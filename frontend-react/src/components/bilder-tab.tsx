import React from 'react'

export default function BilderTab() {
  return (
    <div className="p-4">
      <h3 className="text-lg font-medium mb-4">Bilder</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="border rounded-lg p-4 bg-slate-50 dark:bg-slate-800 flex flex-col items-center justify-center h-48">
          <div className="w-16 h-16 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-500 dark:text-slate-400">
              <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
              <circle cx="9" cy="9" r="2" />
              <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
            </svg>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">Bild hinzufügen</p>
        </div>
      </div>
    </div>
  )
} 