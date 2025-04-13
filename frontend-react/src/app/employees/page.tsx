import EmployeesView from '@/components/employees/EmployeesView'

export const dynamic = 'force-dynamic'; // Prevent static generation

export default function EmployeesPage() {
  return (
    // Optional: Add padding or other layout wrappers if needed globally
    <main className="container mx-auto px-4 py-8 h-full flex flex-col">
       <EmployeesView /> {/* Render the new view component */}
    </main>
  );
} 