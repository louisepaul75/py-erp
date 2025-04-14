"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Customer } from "@/types/sales-types"; // Import the type
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";

// UI Components
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
// Import the CustomerForm component
import CustomerForm from "@/components/customers/customer-form";

// Icons
import { ArrowLeft } from "lucide-react";

// TODO: Replace with your project's toast notification system
const showToast = (title: string, description: string, variant: 'default' | 'destructive' = 'default') => {
    console.log(`Toast [${variant}]: ${title} - ${description}`);
    // Example using a hypothetical toast function:
    // toast({ title, description, variant });
};

export default function NewCustomerPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateCustomer = async (customerData: Partial<Customer>) => {
    setIsSubmitting(true);
    setError(null);

    // Remove fields that should not be sent on create (adapt as needed)
    const dataToSend: Omit<Partial<Customer>, 'id' | 'orderCount' | 'totalSpent' | 'since'> = {
      ...customerData,
    };
    // Remove undefined fields if necessary for your API
    Object.keys(dataToSend).forEach(key => dataToSend[key] === undefined && delete dataToSend[key]);

    try {
      const token = await authService.getToken();
      if (!token) {
        throw new Error("Authentication required.");
      }

      const response = await fetch(`${API_URL}/sales/customers/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(dataToSend),
      });

      if (!response.ok) {
        let errorMessage = `API request failed: ${response.status} ${response.statusText}`;
        try {
            const errorData = await response.json();
            // Try to get a more specific error message from the API response
            errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData) || errorMessage;
        } catch (jsonError) {
            // Ignore if response is not JSON
        }
        throw new Error(errorMessage);
      }

      const newCustomer: Customer = await response.json();

      showToast("Customer Created", "The new customer has been successfully created.");

      // Navigate to the new customer's detail page
      router.push(`/sales/customers/${newCustomer.id}`);

    } catch (err) {
      console.error("Error creating customer:", err);
      const message = err instanceof Error ? err.message : "An unexpected error occurred.";
      setError(message);
      showToast("Error", message, "destructive");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-6 h-full overflow-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
         <Button variant="outline" size="icon" asChild>
             <Link href="/sales/customers">
                 <ArrowLeft className="h-4 w-4" />
                 <span className="sr-only">Back to Customers</span>
             </Link>
         </Button>
         <h1 className="text-2xl font-bold tracking-tight md:text-3xl">Create New Customer</h1>
      </div>

       {/* Error Display */}
       {error && (
          <Alert variant="destructive">
              <AlertTitle>Failed to Create Customer</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
          </Alert>
       )}

      {/* Render the Customer Form */}
      <CustomerForm
         onSubmit={handleCreateCustomer}
         isSubmitting={isSubmitting}
         mode="create"
      />

    </div>
  );
} 