"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation"; // Added for navigation
import Link from "next/link"; // Added for links
import { Customer } from "@/types/sales-types"; // Assume this type will be updated
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
// Added Checkbox and Label if needed for filtering later
// import { Checkbox } from "@/components/ui/checkbox";
// import { Label } from "@/components/ui/label";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
// Added Avatar components
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
// Updated icons: removed Eye, kept PlusCircle, Edit
import { PlusCircle, Edit, Search } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
// Assume formatDate exists or create a basic one if needed
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils"; // Added for class names

// Basic currency formatter (similar to draft)
const formatCurrency = (value: number | undefined | null) => {
    if (value == null) return '-';
    return new Intl.NumberFormat("de-DE", { // Or use appropriate locale
      style: "currency",
      currency: "EUR", // Or use appropriate currency
    }).format(value);
};

// Define Props for CustomerList
interface CustomerListProps {
  onSelectCustomer: (id: string | number) => void;
  selectedCustomerId: string | null;
}

export default function CustomerList({ onSelectCustomer, selectedCustomerId }: CustomerListProps) {
  const router = useRouter(); // Added router hook
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Add state for other filters if implemented, e.g.:
  // const [filterHasOrders, setFilterHasOrders] = useState(false);

  useEffect(() => {
    const fetchCustomers = async () => {
      setIsLoading(true);
      setError(null);
      setCustomers([]);
      setFilteredCustomers([]);

      try {
        const token = await authService.getToken();
        if (!token) {
          throw new Error("Authentication required.");
        }

        const customerEndpoint = `${API_URL}/sales/customers/`;

        const response = await fetch(customerEndpoint, {
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          if (response.status === 401) {
             throw new Error('Authentication failed. Please try logging in again.');
          } else if (response.status === 403) {
              throw new Error('Permission denied.');
          }
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        const fetchedCustomers: Customer[] = Array.isArray(data) ? data : data.results || [];

        // Map to ensure essential fields exist, potentially enrich later
        const validCustomers = fetchedCustomers.map(cust => ({
            ...cust, // Keep existing fields
            id: cust.id,
            customer_number: cust.customer_number || 'N/A',
            name: cust.name || 'No Name', // This might be replaced by firstName/lastName/companyName
            // Add defaults/fallbacks for new fields expected from updated Customer type/API
            firstName: cust.firstName || '',
            lastName: cust.lastName || '',
            companyName: cust.companyName || '',
            isCompany: cust.isCompany || false,
            emailMain: cust.emailMain || '-',
            phoneMain: cust.phoneMain || '-',
            orderCount: cust.orderCount || 0,
            since: cust.since || new Date().toISOString(), // Default 'since' to now if missing
            totalSpent: cust.totalSpent || 0,
            avatar: cust.avatar || null, // Assuming avatar is a URL string or null
            customer_group: cust.customer_group || 'Unknown',
            vat_id: cust.vat_id || '-',
        }));

        setCustomers(validCustomers);
        setFilteredCustomers(validCustomers);

      } catch (err) {
        console.error("Error fetching customers:", err);
        setError(err instanceof Error ? err.message : "Failed to load customers");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomers();
  }, []);

  // Effect for client-side filtering
  useEffect(() => {
    let filtered = [...customers];
    const lowerSearchTerm = searchTerm.toLowerCase();

    if (lowerSearchTerm) {
      filtered = filtered.filter((customer) => {
          const fullName = `${customer.firstName || ''} ${customer.lastName || ''}`.toLowerCase();
          const companyName = (customer.companyName || '').toLowerCase();
          // Combine searchable fields
          return (
            customer.customer_number.toLowerCase().includes(lowerSearchTerm) ||
            (customer.isCompany ? companyName.includes(lowerSearchTerm) : fullName.includes(lowerSearchTerm)) ||
            (customer.vat_id && customer.vat_id.toLowerCase().includes(lowerSearchTerm)) ||
            (customer.emailMain && customer.emailMain.toLowerCase().includes(lowerSearchTerm)) ||
            (customer.phoneMain && customer.phoneMain.toLowerCase().includes(lowerSearchTerm))
          );
        }
      );
    }

    // Add other client-side filters here if needed
    // Example:
    // if (filterHasOrders) {
    //   filtered = filtered.filter(customer => (customer.orderCount || 0) > 0);
    // }

    setFilteredCustomers(filtered);
  }, [customers, searchTerm /*, filterHasOrders */]);


  // Updated action handlers
  const handleEditCustomer = (id: number | string) => {
      console.log("Edit customer:", id);
      router.push(`/sales/customers/${id}/edit`); // Navigate to edit page
  };

   const handleCreateCustomer = () => {
      console.log("Create new customer");
       router.push('/sales/customers/new'); // Navigate to create page
   };


  return (
    <>
      <CardHeader>
        <CardTitle>Customer List</CardTitle>
        <div className="relative mt-2">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            type="search"
            placeholder="Search No., Name, VAT, Email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 h-9 w-full"
          />
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto">
        {error && (
          <Alert variant="destructive" className="my-4">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {isLoading ? (
             <div className="space-y-4">
               <Skeleton className="h-10 w-full" />
               <Skeleton className="h-10 w-full" />
               <Skeleton className="h-10 w-full" />
            </div>
          ) : filteredCustomers.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead className="hidden md:table-cell">Email</TableHead>
                  <TableHead className="hidden md:table-cell">Phone</TableHead>
                  <TableHead className="hidden sm:table-cell">Orders</TableHead>
                  <TableHead className="hidden lg:table-cell">Since</TableHead>
                  <TableHead className="hidden lg:table-cell text-right">Total Spent</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCustomers.map((customer) => {
                    const customerName = customer.isCompany
                        ? customer.companyName
                        : `${customer.firstName || ''} ${customer.lastName || ''}`;
                    const fallbackInitials = (customer.isCompany
                        ? (customer.companyName || 'Co').substring(0, 2)
                        : `${(customer.firstName || 'U')[0]}${(customer.lastName || 'N')[0]}`).toUpperCase();

                    return (
                        <TableRow
                           key={customer.id}
                           onClick={() => onSelectCustomer(customer.id)}
                           className={cn(
                             "cursor-pointer",
                             String(customer.id) === selectedCustomerId ? 'bg-muted' : ''
                           )}
                           >
                            <TableCell>
                                <span className="font-medium">
                                    {customer.name || 'N/A'}
                                    <p className="text-xs text-muted-foreground font-normal block sm:hidden">{customer.customer_number}</p>
                                </span>
                            </TableCell>
                            <TableCell className="hidden md:table-cell">{customer.emailMain}</TableCell>
                            <TableCell className="hidden md:table-cell">{customer.phoneMain}</TableCell>
                            <TableCell className="hidden sm:table-cell text-center">{customer.orderCount}</TableCell>
                            <TableCell className="hidden lg:table-cell">{formatDate(customer.since)}</TableCell>
                            <TableCell className="hidden lg:table-cell text-right">{formatCurrency(customer.totalSpent)}</TableCell>
                            <TableCell>
                            <div className="flex gap-1 justify-end">
                                <Button variant="ghost" size="sm"
                                   onClick={(e) => {
                                       e.stopPropagation();
                                       handleEditCustomer(customer.id);
                                   }}
                                   >
                                    <Edit className="h-4 w-4" />
                                    <span className="sr-only">Edit Customer</span>
                                </Button>
                            </div>
                            </TableCell>
                        </TableRow>
                    );
                })}
              </TableBody>
            </Table>
           ) : (
             <div className="text-center py-10 text-muted-foreground">
               No customers found{searchTerm ? " matching your search" : ""}.
             </div>
           )}
      </CardContent>
      <div className="p-4 border-t flex-shrink-0">
        <Button className="w-full" onClick={handleCreateCustomer}>
          <PlusCircle className="mr-2 h-4 w-4" />
          New Customer
        </Button>
      </div>
    </>
  );
} 