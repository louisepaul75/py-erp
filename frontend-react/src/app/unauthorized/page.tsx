import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Zugriff verweigert - pyERP',
};

export default function UnauthorizedPage() {
  return (
    <div className="flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8 h-full overflow-auto">
      <div className="max-w-md w-full text-center space-y-8">
        <div>
          <h1 className="text-6xl font-extrabold text-red-500">403</h1>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Zugriff verweigert
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Du hast nicht die erforderlichen Berechtigungen, um auf diese Seite zuzugreifen.
          </p>
        </div>
        <div className="flex flex-col space-y-4">
          <Link href="/dashboard" className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            Zurück zum Dashboard
          </Link>
          <Link href="/" className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200">
            Zurück zur Startseite
          </Link>
        </div>
      </div>
    </div>
  );
} 