"use client";

import { useState, useEffect } from "react";
import { Customer } from "@/types/sales-types"; // Import the type
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { PlusCircle, Eye, Edit } from "lucide-react"; // Icons for buttons
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"; // For error display
import { Skeleton } from "@/components/ui/skeleton"; // For loading state

export default function CustomerList() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [filteredCustomers, setFilteredCustomers] = useState<Customer[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Add state for pagination if needed:
  // const [currentPage, setCurrentPage] = useState(1);
  // const [itemsPerPage, setItemsPerPage] = useState(20);

  useEffect(() => {
    const fetchCustomers = async () => {
      setIsLoading(true);
      setError(null);
      setCustomers([]); // Clear previous data
      setFilteredCustomers([]);

      try {
        const token = await authService.getToken(); // Assuming auth is needed
        if (!token) {
          // Redirect or handle unauthenticated state
          // window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
          throw new Error("Authentication required.");
        }

        // Construct the endpoint URL (base URL is already /api)
        const customerEndpoint = `${API_URL}/sales/customers/`;

        const response = await fetch(customerEndpoint, {
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
          // credentials: 'include', // Include if using cookie-based auth
        });

        if (!response.ok) {
           // Basic error handling, can be expanded like in WarehouseLocationList
          if (response.status === 401) {
             throw new Error('Authentication failed. Please try logging in again.');
          } else if (response.status === 403) {
              throw new Error('Permission denied.');
          }
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        // Assuming the API returns a list directly or within a 'results' field
        const fetchedCustomers: Customer[] = Array.isArray(data) ? data : data.results || [];

        // Add basic validation/mapping if needed
        const validCustomers = fetchedCustomers.map(cust => ({
            id: cust.id,
            customer_number: cust.customer_number || 'N/A',
            name: cust.name || 'No Name',
            customer_group: cust.customer_group || 'Unknown',
            vat_id: cust.vat_id || '-',
            // Map other fields as necessary
        }));

        setCustomers(validCustomers);
        setFilteredCustomers(validCustomers); // Initialize filter with all data

      } catch (err) {
        console.error("Error fetching customers:", err);
        setError(err instanceof Error ? err.message : "Failed to load customers");
        // Optionally load mock data in dev
        // if (process.env.NODE_ENV === 'development') { ... }
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomers();
  }, []); // Runs once on mount

  // Effect for client-side filtering
  useEffect(() => {
    let filtered = [...customers];

    if (searchTerm) {
      const lowerSearchTerm = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (customer) =>
          customer.customer_number.toLowerCase().includes(lowerSearchTerm) ||
          customer.name.toLowerCase().includes(lowerSearchTerm) ||
          (customer.vat_id && customer.vat_id.toLowerCase().includes(lowerSearchTerm))
          // Add other searchable fields if needed
      );
    }

    // Add other filters here (e.g., customer_group) if implemented

    setFilteredCustomers(filtered);
    // Reset to first page when filters change if pagination is implemented
    // setCurrentPage(1);
  }, [customers, searchTerm /* add other filter states here */]);


  // Placeholder functions for actions - implement routing/modals later
  const handleViewCustomer = (id: number) => {
      console.log("View customer:", id);
      // TODO: Implement navigation to detail page e.g., router.push(`/sales/customers/${id}`)
  };

  const handleEditCustomer = (id: number) => {
      console.log("Edit customer:", id);
      // TODO: Implement navigation to edit page or open modal
  };

   const handleCreateCustomer = () => {
      console.log("Create new customer");
       // TODO: Implement navigation to create page or open modal
   };

   // Calculate pagination if needed
   // const totalPages = Math.ceil(filteredCustomers.length / itemsPerPage);
   // const paginatedCustomers = filteredCustomers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);


  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary">Customers</h1>
         <Button onClick={handleCreateCustomer}>
           <PlusCircle className="mr-2 h-4 w-4" /> New Customer
         </Button>
      </div>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

      <Card>
        <CardHeader>
           {/* Filters Section */}
           <div className="flex items-center gap-4">
             <Input
               placeholder="Search by No., Name, VAT ID..."
               value={searchTerm}
               onChange={(e) => setSearchTerm(e.target.value)}
               className="max-w-sm"
             />
             {/* Add Dropdowns for filtering here if needed */}
           </div>
        </CardHeader>
        <CardContent>
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
                  <TableHead>Customer No.</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Group</TableHead>
                  <TableHead>VAT ID</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                 {/* Use paginatedCustomers if pagination is implemented */}
                {filteredCustomers.map((customer) => (
                  <TableRow key={customer.id}>
                    <TableCell>{customer.customer_number}</TableCell>
                    <TableCell>{customer.name}</TableCell>
                    <TableCell>{customer.customer_group}</TableCell>
                    <TableCell>{customer.vat_id}</TableCell>
                    <TableCell>
                       <div className="flex gap-2">
                           <Button variant="ghost" size="sm" onClick={() => handleViewCustomer(customer.id)}>
                               <Eye className="h-4 w-4" />
                           </Button>
                           <Button variant="ghost" size="sm" onClick={() => handleEditCustomer(customer.id)}>
                               <Edit className="h-4 w-4" />
                           </Button>
                       </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
           ) : (
             <div className="text-center py-10 text-muted-foreground">
               No customers found.
             </div>
           )}

           {/* Add Pagination controls here if implemented */}

        </CardContent>
      </Card>
    </div>
  );
} 