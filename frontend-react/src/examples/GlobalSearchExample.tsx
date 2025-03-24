"use client";

// Removed import of SimpleGlobalSearch to prevent issues
// import { SimpleGlobalSearch } from "@/components/SimpleGlobalSearch";
import { SearchResult } from "@/hooks/useGlobalSearch";
import { useRouter } from "next/navigation";

/**
 * Example implementation that has been disabled due to production errors
 */
export default function GlobalSearchExample() {
  const router = useRouter();
  
  // Simplified version that doesn't actually use the search component
  return (
    <div className="p-4 max-w-screen-lg mx-auto">
      <h1 className="text-2xl font-bold mb-6">Global Search Implementation</h1>
      
      <div className="flex flex-col gap-8">
        <section>
          <h2 className="text-xl font-semibold mb-4">Search Component</h2>
          <div className="w-full max-w-md">
            <div className="p-4 border rounded">
              Global search has been temporarily disabled
            </div>
          </div>
        </section>
        
        <section>
          <h2 className="text-xl font-semibold mb-4">Implementation Notes</h2>
          <div className="p-4 bg-muted rounded-md text-sm">
            <p className="mb-2">
              The search component has been temporarily disabled due to errors in production mode.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
