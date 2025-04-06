import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-10rem)] text-center px-4">
      <h1 className="text-4xl font-bold mb-4">404 - Seite nicht gefunden</h1>
      <p className="text-xl mb-8">Die angeforderte Seite existiert nicht.</p>
      <Link 
        href="/"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
      >
        Zurück zur Startseite
      </Link>
    </div>
  )
} 