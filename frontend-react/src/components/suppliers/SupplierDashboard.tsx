'use client'; // Required for hooks like useQuery and client components

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
// ColumnDef is not needed for SortableTable
// import { ColumnDef } from '@tanstack/react-table';
import { MoreHorizontal, PlusCircle } from 'lucide-react';

import { Supplier } from '@/types/supplier';
import { fetchSuppliers, deleteSupplier } from '@/lib/api/suppliers';
// Correct import name for the sortable table
import { SortableTable } from '@/components/ui/sortable-table';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Skeleton } from '@/components/ui/skeleton'; // For loading state
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'; // For error state
import { useToast } from '@/hooks/use-toast'; // Import useToast

// Import the dialog component
import { SupplierDialog } from './SupplierDialog';
import { SupplierDeleteDialog } from './SupplierDeleteDialog'; // Import delete dialog

// Define the Column type expected by SortableTable
interface Column<T> {
  id: string; // Use id instead of accessorKey for SortableTable
  header: string;
  cell: (row: T) => React.ReactNode;
  sortable?: boolean;
}

// Adjust columns definition to match SortableTable's expected structure
// and accept handlers
const getColumns = (
  onEdit: (supplier: Supplier) => void,
  onDelete: (supplier: Supplier) => void
): Column<Supplier>[] => [
  {
    id: 'name', // Use id
    header: 'Name',
    cell: (row) => row.name, // Direct access or formatting
    sortable: true,
  },
  {
    id: 'contactPerson',
    header: 'Contact Person',
    cell: (row) => row.contactPerson || '-',
    sortable: true,
  },
  {
    id: 'email',
    header: 'Email',
    cell: (row) => row.email || '-',
    sortable: true,
  },
  {
    id: 'phone',
    header: 'Phone',
    cell: (row) => row.phone || '-',
    sortable: true,
  },
  {
    id: 'taxId',
    header: 'Tax ID',
    cell: (row) => row.taxId || '-',
    sortable: false, // Example: Tax ID might not be sortable
  },
  {
    id: 'actions',
    header: 'Actions',
    sortable: false,
    cell: (supplier) => { // Cell function receives the row data directly
      // const supplier = row.original; // No longer needed

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem onClick={() => navigator.clipboard.writeText(supplier.id.toString())}>
              Copy ID
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onEdit(supplier)}>Edit</DropdownMenuItem>
            <DropdownMenuItem onClick={() => onDelete(supplier)} className="text-red-600">
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

export function SupplierDashboard() {
  const queryClient = useQueryClient(); // Get query client instance
  const { toast } = useToast(); // Get toast function

  // State for dialog visibility and supplier being edited
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);

  // State for Delete dialog
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deletingSupplier, setDeletingSupplier] = useState<Supplier | null>(null);

  // Fetch suppliers using TanStack Query
  const {
    data: suppliers,
    isLoading,
    error,
    isError,
  } = useQuery<Supplier[], Error>({
    queryKey: ['suppliers'], // Unique key for this query
    queryFn: fetchSuppliers, // Function to fetch data
    // Optional: Add staleTime, refetchOnWindowFocus, etc. as needed
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteSupplier,
    onSuccess: (_, deletedId) => { // API function likely takes ID
      toast({
        title: "Supplier Deleted",
        // description: `${deletingSupplier?.name} has been deleted.`, // Name might be unavailable after deletion
        description: `Supplier with ID ${deletedId} has been deleted successfully.`
      });
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      setIsDeleteDialogOpen(false); // Close confirmation dialog
      setDeletingSupplier(null); // Clear deleting supplier state
    },
    onError: (error) => {
      toast({
        title: "Error Deleting Supplier",
        description: error.message || "An unknown error occurred.",
        variant: "destructive",
      });
       setIsDeleteDialogOpen(false); // Close confirmation dialog even on error
       setDeletingSupplier(null);
    },
  });

  // Handlers for dialog actions
  const handleAddSupplier = () => {
    setEditingSupplier(null); // Ensure no supplier is pre-filled
    setIsDialogOpen(true);
  };

  const handleEditSupplier = (supplier: Supplier) => {
    setEditingSupplier(supplier);
    setIsDialogOpen(true);
  };

  // Open delete confirmation dialog
  const handleDeleteSupplier = (supplier: Supplier) => {
    setDeletingSupplier(supplier);
    setIsDeleteDialogOpen(true);
  };

  // Confirm and execute deletion
  const confirmDeleteSupplier = () => {
    if (deletingSupplier) {
      deleteMutation.mutate(deletingSupplier.id);
    }
  };

  // Get columns definition with handlers
  const tableColumns = getColumns(handleEditSupplier, handleDeleteSupplier);

  // Loading State
  if (isLoading) {
    // Show skeleton loaders matching the table structure
    return (
      <div className="space-y-4">
         <div className="flex items-center justify-between">
             <Skeleton className="h-8 w-40" /> {/* Placeholder for Search/Filter */}
             <Skeleton className="h-10 w-32" /> {/* Placeholder for Add Button */}
         </div>
        <div className="rounded-md border">
            <div className="p-4"><Skeleton className="h-8 w-full mb-4" /></div> {/* Header row */}
            <div className="p-4 space-y-3">
                <Skeleton className="h-6 w-full" /> {/* Data row 1 */}
                <Skeleton className="h-6 w-full" /> {/* Data row 2 */}
                <Skeleton className="h-6 w-full" /> {/* Data row 3 */}
            </div>
        </div>
      </div>
    );
  }

  // Error State
  if (isError) {
    return (
        <Alert variant="destructive">
            <AlertTitle>Error Fetching Suppliers</AlertTitle>
            <AlertDescription>
            {error?.message || 'An unexpected error occurred. Please try again.'}
            </AlertDescription>
      </Alert>
    );
  }

  // Success State
  return (
    <div className="space-y-4"> {/* Add spacing */}
      {/* Add Button outside the table */}
      <div className="flex justify-end">
        <Button onClick={handleAddSupplier}>
          <PlusCircle className="mr-2 h-4 w-4" /> Add Supplier
        </Button>
      </div>

      {/* Use SortableTable component */}
      <SortableTable
        columns={tableColumns}
        data={suppliers || []}
        // Pass handleRowClick or onRowClick if needed by SortableTable for other interactions
        // handleRowClick={(supplier) => console.log('Row clicked:', supplier)}
      />

      {/* Add/Edit Dialog */}
      <SupplierDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        supplier={editingSupplier}
      />

      {/* Delete Confirmation Dialog */}
      <SupplierDeleteDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        supplier={deletingSupplier}
        onConfirmDelete={confirmDeleteSupplier}
        isDeleting={deleteMutation.isPending}
      />
    </div>
  );
} 