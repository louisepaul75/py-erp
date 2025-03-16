import Link from "next/link"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm flex">
        <h1 className="text-4xl font-bold">Welcome to pyERP Frontend</h1>
      </div>
      <div className="mt-8 grid text-center lg:max-w-5xl lg:w-full lg:mb-0 lg:grid-cols-3 lg:text-left">
        <Link href="/dashboard" className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">
            Dashboard
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            View your business metrics and KPIs at a glance.
          </p>
        </Link>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">
            Inventory
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Manage your products, stock levels, and suppliers.
          </p>
        </div>

        <div className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100">
          <h2 className="mb-3 text-2xl font-semibold">
            Customers
          </h2>
          <p className="m-0 max-w-[30ch] text-sm opacity-50">
            Track customer information, orders, and interactions.
          </p>
        </div>
      </div>
    </main>
  )
} 