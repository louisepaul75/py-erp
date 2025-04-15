"use client";

import * as React from "react";
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
// Updated icons: removed Eye, kept PlusCircle, Edit, Filter
// Add ArrowUpDown for sorting
import { PlusCircle, Edit, Search, Filter, ArrowUpDown, X } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
// Assume formatDate exists or create a basic one if needed
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils"; // Added for class names
// Import the hook
import { useDataTable } from "@/hooks/useDataTable";

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
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Add state for other filters if implemented, e.g.:
  // const [filterHasOrders, setFilterHasOrders] = useState(false);

  useEffect(() => {
    const fetchCustomers = async () => {
      setIsLoading(true);
      setError(null);
      setCustomers([]);

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

      } catch (err) {
        console.error("Error fetching customers:", err);
        setError(err instanceof Error ? err.message : "Failed to load customers");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomers();
  }, []);

  // Use the data table hook
  const { 
    processedData: customerList, // Renamed for clarity
    sortConfig,
    requestSort,
    searchTerm,
    setSearchTerm 
  } = useDataTable<Customer>({
    initialData: customers, // Use the fetched customers
    initialSortKey: 'name', // Default sort by name
    searchableFields: [ // Define fields for the hook to search
      'customer_number',
      'name',
      'firstName',
      'lastName',
      'companyName',
      'emailMain',
      'phoneMain',
      'vat_id'
    ]
  });

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
    <div className="flex flex-col h-full overflow-hidden">
      <CardHeader>
        <CardTitle>Customer List</CardTitle>
        <div className="flex items-center justify-between mt-2 space-x-2">
          <div className="relative flex-grow">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
            {/* Connect Input to hook's state */}
            <Input
              type="search"
              placeholder="Search No., Name, VAT, Email..."
              value={searchTerm} // Use hook's searchTerm
              onChange={(e) => setSearchTerm(e.target.value)} // Use hook's setSearchTerm
              className="pl-10 h-9 w-full"
              disabled={isLoading}
            />
             {/* Add clear button for search */}
             {searchTerm && (
               <Button
                 variant="ghost"
                 size="icon"
                 className="absolute right-2 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full text-muted-foreground hover:text-foreground"
                 onClick={() => setSearchTerm('')}
                 disabled={isLoading}
               >
                 <X className="h-3 w-3" />
               </Button>
             )}
          </div>
          <Button
            variant="outline"
            size="icon"
            aria-label="Filter Customers"
            onClick={() => alert('Filter button clicked - Implement filter logic')}
            disabled={isLoading}
          >
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-grow flex flex-col overflow-hidden min-h-0">
        <div className="flex-1 overflow-y-auto h-full scrollbar-thin max-md:scrollbar md:scrollbar-none">
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
          ) : customerList.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  {/* Name Header - Make sortable */}
                  <TableHead>
                     <Button variant="ghost" onClick={() => requestSort('name')} className="px-0 hover:bg-transparent">
                       Name
                        {sortConfig.key === 'name' && (
                         <ArrowUpDown className={`ml-2 h-3 w-3 ${sortConfig.direction === 'asc' ? '' : 'rotate-180'}`} />
                        )}
                        {sortConfig.key !== 'name' && <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />}
                     </Button>
                  </TableHead>
                  {/* Email Header - Make sortable */}
                  <TableHead className="hidden md:table-cell">
                     <Button variant="ghost" onClick={() => requestSort('emailMain')} className="px-0 hover:bg-transparent">
                       Email
                        {sortConfig.key === 'emailMain' && (
                         <ArrowUpDown className={`ml-2 h-3 w-3 ${sortConfig.direction === 'asc' ? '' : 'rotate-180'}`} />
                        )}
                        {sortConfig.key !== 'emailMain' && <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />}
                     </Button>
                  </TableHead>
                  {/* Phone Header - Non-sortable (example) */}
                  <TableHead className="hidden md:table-cell">Phone</TableHead>
                  {/* Orders Header - Make sortable */}
                  <TableHead className="hidden sm:table-cell">
                     <Button variant="ghost" onClick={() => requestSort('orderCount')} className="px-0 hover:bg-transparent">
                       Orders
                        {sortConfig.key === 'orderCount' && (
                         <ArrowUpDown className={`ml-2 h-3 w-3 ${sortConfig.direction === 'asc' ? '' : 'rotate-180'}`} />
                        )}
                        {sortConfig.key !== 'orderCount' && <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />}
                     </Button>
                  </TableHead>
                  {/* Since Header - Make sortable */}
                  <TableHead className="hidden lg:table-cell">
                     <Button variant="ghost" onClick={() => requestSort('since')} className="px-0 hover:bg-transparent">
                       Since
                        {sortConfig.key === 'since' && (
                         <ArrowUpDown className={`ml-2 h-3 w-3 ${sortConfig.direction === 'asc' ? '' : 'rotate-180'}`} />
                        )}
                        {sortConfig.key !== 'since' && <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />}
                     </Button>
                  </TableHead>
                  {/* Total Spent Header - Make sortable */}
                  <TableHead className="hidden lg:table-cell text-right">
                     <Button variant="ghost" onClick={() => requestSort('totalSpent')} className="px-0 hover:bg-transparent justify-end w-full">
                       Total Spent
                        {sortConfig.key === 'totalSpent' && (
                         <ArrowUpDown className={`ml-2 h-3 w-3 ${sortConfig.direction === 'asc' ? '' : 'rotate-180'}`} />
                        )}
                        {sortConfig.key !== 'totalSpent' && <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />}
                     </Button>
                  </TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {customerList.map((customer) => {
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
        </div>
      </CardContent>
      <div className="p-4 border-t flex-shrink-0">
        <Button className="w-full" onClick={handleCreateCustomer}>
          <PlusCircle className="mr-2 h-4 w-4" />
          New Customer
        </Button>
      </div>
    </div>
  );
} 