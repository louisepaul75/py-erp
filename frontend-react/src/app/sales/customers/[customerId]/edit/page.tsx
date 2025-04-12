"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Customer } from "@/types/sales-types";
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";

// UI Components
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton"; // For loading state
import CustomerForm from "@/components/customers/customer-form"; // Import the form

// Icons
import { ArrowLeft } from "lucide-react";

// TODO: Replace with your project's toast notification system
const showToast = (title: string, description: string, variant: 'default' | 'destructive' = 'default') => {
    console.log(`Toast [${variant}]: ${title} - ${description}`);
};

export default function EditCustomerPage() {
  const params = useParams();
  const router = useRouter();
  const customerId = params.customerId as string;

  const [customer, setCustomer] = useState<Partial<Customer> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch existing customer data on component mount
  useEffect(() => {
    if (!customerId) {
      setError("Customer ID is missing.");
      setIsLoading(false);
      return;
    }

    const fetchCustomerDetails = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const token = await authService.getToken();
        if (!token) throw new Error("Authentication required.");

        const customerEndpoint = `${API_URL}/sales/customers/${customerId}/`;
        const response = await fetch(customerEndpoint, {
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
           if (response.status === 404) throw new Error('Customer not found.');
           throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        const data: Customer = await response.json();
        setCustomer(data); // Set fetched data for the form
      } catch (err) {
        console.error("Error fetching customer details for edit:", err);
        setError(err instanceof Error ? err.message : "Failed to load customer data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomerDetails();
  }, [customerId]);

  // Handle form submission (Update)
  const handleUpdateCustomer = async (customerData: Partial<Customer>) => {
    setIsSubmitting(true);
    setError(null);

    // Prepare data: remove read-only fields if necessary, add ID
    const dataToSend: Partial<Customer> = {
      ...customerData,
      // Ensure ID isn't overwritten if not present in customerData (should be)
      id: customerId,
    };
     // Remove fields that shouldn't be sent or API handles (e.g., derived fields)
    delete dataToSend.orderCount;
    delete dataToSend.totalSpent;
    // Remove undefined fields if necessary for your API
    Object.keys(dataToSend).forEach(key => dataToSend[key] === undefined && delete dataToSend[key]);


    try {
      const token = await authService.getToken();
      if (!token) throw new Error("Authentication required.");

      const response = await fetch(`${API_URL}/sales/customers/${customerId}/`, {
        method: "PUT", // Or PATCH depending on your API
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
            errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData) || errorMessage;
        } catch (jsonError) {}
        throw new Error(errorMessage);
      }

      showToast("Customer Updated", "The customer details have been successfully updated.");
      // Navigate back to the customer's detail page
      router.push(`/sales/customers/${customerId}`);
      // Optional: invalidate query cache if using React Query

    } catch (err) {
      console.error("Error updating customer:", err);
      const message = err instanceof Error ? err.message : "An unexpected error occurred.";
      setError(message);
      showToast("Error", message, "destructive");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Loading State for initial fetch
  if (isLoading) {
    return (
        <div className="container mx-auto px-4 py-8 space-y-6">
            {/* Simplified Header Skeleton */}
            <div className="flex items-center gap-4 mb-6">
                <Skeleton className="h-9 w-9 rounded-md" />
                <Skeleton className="h-6 w-48" />
            </div>
             {/* Form Skeleton */}
             <Skeleton className="h-[600px] w-full" /> {/* Adjust height as needed */}
        </div>
    );
  }

  // Error State for initial fetch or no customer
  if (error || !customer) {
    return (
        <div className="container mx-auto px-4 py-8">
            <Button variant="outline" size="sm" asChild className="mb-4">
                 <Link href="/sales/customers">
                     <ArrowLeft className="mr-2 h-4 w-4" /> Back to List
                 </Link>
            </Button>
            <Alert variant="destructive">
                <AlertTitle>Error Loading Customer Data</AlertTitle>
                <AlertDescription>{error || "Customer could not be found or loaded."}</AlertDescription>
            </Alert>
      </div>
    );
  }

  // Render the form with fetched data
  return (
     <div className="container mx-auto px-4 py-8 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
            <Button variant="outline" size="icon" asChild>
                {/* Link back to the detail page */}
                <Link href={`/sales/customers/${customerId}`}>
                    <ArrowLeft className="h-4 w-4" />
                    <span className="sr-only">Back to Customer Details</span>
                </Link>
            </Button>
            <h1 className="text-2xl font-bold tracking-tight md:text-3xl">
                Edit Customer: {customer.isCompany ? customer.companyName : `${customer.firstName || ''} ${customer.lastName || ''}`.trim()}
            </h1>
        </div>

        {/* Error Display for submission errors */}
        {error && !isLoading && (
            <Alert variant="destructive">
                <AlertTitle>Failed to Update Customer</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        )}

        {/* Render the Customer Form in edit mode */}
        <CustomerForm
            initialData={customer} // Pass fetched data
            onSubmit={handleUpdateCustomer} // Pass update handler
            isSubmitting={isSubmitting}
            mode="edit" // Set mode to edit
        />
     </div>
  );
} 