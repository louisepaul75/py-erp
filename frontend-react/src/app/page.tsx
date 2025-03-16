import { redirect } from 'next/navigation';

export default function Home() {
  redirect('/dashboard');
  
  // This won't be rendered, but is needed for TypeScript
  return null;
} 