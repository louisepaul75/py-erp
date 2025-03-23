import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to the dashboard page
  redirect('/dashboard');
  
  // This won't be rendered, but is needed for TypeScript
  return null;
} 