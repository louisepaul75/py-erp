import { redirect } from "next/navigation"

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-6">
        Welcome to pyERP
      </h1>
      <p className="text-gray-600 dark:text-gray-300 mb-4">
        This is the React frontend for the pyERP system.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        {['Products', 'Sales', 'Production', 'Inventory'].map((module) => (
          <div key={module} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200 mb-2">
              {module}
            </h2>
            <p className="text-gray-500 dark:text-gray-400">
              Access the {module.toLowerCase()} module to manage your business data.
            </p>
          </div>
        ))}
      </div>
    </div>
  );
} 