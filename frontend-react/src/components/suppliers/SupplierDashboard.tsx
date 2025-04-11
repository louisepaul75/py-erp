'use client'; // Required for hooks like useQuery and client components

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { MoreHorizontal, PlusCircle, Search } from 'lucide-react';

import { Supplier } from '@/types/supplier';
import { fetchSuppliers, deleteSupplier, FetchSuppliersResult, SyncStatus } from '@/lib/api/suppliers';
// Remove SortableTable import
// import { SortableTable } from '@/components/ui/sortable-table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
// Import standard table components
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  TableCaption, // Optional: if you want a caption
} from '@/components/ui/table';

// Import the dialog component
import { SupplierDialog } from './SupplierDialog';
import { SupplierDeleteDialog } from './SupplierDeleteDialog'; // Import delete dialog

// Import Pagination component
import { Pagination } from '@/components/ui/pagination';

// Import Select components
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Define a simplified Column type for structure, removing sortable
interface TableColumn<T> {
  id: string;
  header: string;
  cell: (row: T) => React.ReactNode;
}

// Adjust columns definition - remove sortable property
const getColumns = (
  onEdit: (supplier: Supplier) => void,
  onDelete: (supplier: Supplier) => void
): TableColumn<Supplier>[] => [
  {
    id: 'name',
    header: 'Name',
    cell: (row) => row.name,
  },
  {
    id: 'contactPerson',
    header: 'Contact Person',
    cell: (row) => row.contactPerson || '-',
  },
  {
    id: 'email',
    header: 'Email',
    cell: (row) => row.email || '-',
  },
  {
    id: 'phone',
    header: 'Phone',
    cell: (row) => row.phone || '-',
  },
  {
    id: 'taxId',
    header: 'Tax ID',
    cell: (row) => row.taxId || '-',
  },
  {
    id: 'actions',
    header: 'Actions',
    cell: (supplier) => {
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
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Add state for pagination
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10); // Or make this configurable
  // Add state for filter
  const [syncStatusFilter, setSyncStatusFilter] = useState<SyncStatus>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deletingSupplier, setDeletingSupplier] = useState<Supplier | null>(null);

  const {
    data, // Will now be FetchSuppliersResult | undefined
    isLoading,
    error,
    isError,
  } = useQuery<FetchSuppliersResult, Error>({
    // Include filter in the queryKey
    queryKey: ['suppliers', searchTerm, page, pageSize, syncStatusFilter],
    // Pass filter to fetchSuppliers
    queryFn: () => fetchSuppliers(searchTerm, page, pageSize, syncStatusFilter),
    // keepPreviousData: true, // Optional: Keep showing old data while fetching new page
  });

  const deleteMutation = useMutation({
    mutationFn: deleteSupplier,
    onSuccess: (_, deletedId) => {
      toast({
        title: "Supplier Deleted",
        description: `Supplier with ID ${deletedId} has been deleted successfully.`
      });
      // Invalidate the specific page query including filter
      queryClient.invalidateQueries({ queryKey: ['suppliers', searchTerm, page, pageSize, syncStatusFilter] });
      // Optional: Check if the deleted item was the last on the page and go back
      if (data?.data.length === 1 && page > 1) {
        setPage(page - 1);
      }
      setIsDeleteDialogOpen(false);
      setDeletingSupplier(null);
    },
    onError: (error) => {
      toast({
        title: "Error Deleting Supplier",
        description: error.message || "An unknown error occurred.",
        variant: "destructive",
      });
       setIsDeleteDialogOpen(false);
       setDeletingSupplier(null);
    },
  });

  const handleAddSupplier = () => {
    setEditingSupplier(null);
    setIsDialogOpen(true);
  };

  const handleEditSupplier = (supplier: Supplier) => {
    setEditingSupplier(supplier);
    setIsDialogOpen(true);
  };

  const handleDeleteSupplier = (supplier: Supplier) => {
    setDeletingSupplier(supplier);
    setIsDeleteDialogOpen(true);
  };

  const confirmDeleteSupplier = () => {
    if (deletingSupplier) {
      deleteMutation.mutate(deletingSupplier.id);
    }
  };

  // Handler for search input changes - reset page to 1
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(1); // Reset to first page on new search
  };

  // Handler for sync status filter changes
  const handleSyncStatusChange = (value: string) => {
    // Ensure the value is a valid SyncStatus type
    const newStatus = value as SyncStatus;
    setSyncStatusFilter(newStatus);
    setPage(1); // Reset to first page on filter change
  };

  const tableColumns = getColumns(handleEditSupplier, handleDeleteSupplier);

  // Updated Loading State Skeleton to resemble standard table
  if (isLoading) {
    const skeletonRowCount = 3; // Number of skeleton rows to show
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-end"> {/* Only show Add button skeleton */}
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                {tableColumns.map((col) => (
                  <TableHead key={col.id}><Skeleton className="h-5 w-20" /></TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {[...Array(skeletonRowCount)].map((_, index) => (
                <TableRow key={index}>
                  {tableColumns.map((col) => (
                    <TableCell key={col.id}><Skeleton className="h-4 w-full" /></TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    );
  }

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

  return (
    <div className="space-y-4">
      {/* Modify header: Add filter dropdown next to search */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <div className="flex flex-1 items-center gap-2 w-full sm:w-auto">
          {/* Search input */}
          <div className="relative flex-grow sm:flex-grow-0 sm:max-w-xs">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search suppliers..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="pl-8 w-full"
            />
          </div>
          {/* Sync Status Filter Dropdown */}
          <Select value={syncStatusFilter} onValueChange={handleSyncStatusChange}>
            <SelectTrigger className="w-full sm:w-[180px]">
              <SelectValue placeholder="Sync status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="synced">Synced</SelectItem>
              <SelectItem value="not_synced">Not Synced</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {/* Add supplier button */}
        <Button onClick={handleAddSupplier} className="w-full sm:w-auto">
          <PlusCircle className="mr-2 h-4 w-4" /> Add Supplier
        </Button>
      </div>

      {/* Use standard Table components */}
      <div className="rounded-md border"> {/* Add border and rounding */}
        <Table>
          {/* Optional: Add a caption */}
          {/* <TableCaption>A list of your suppliers.</TableCaption> */}
          <TableHeader>
            <TableRow>
              {tableColumns.map((column) => (
                <TableHead key={column.id}>{column.header}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {/* Check data.data instead of suppliers */} 
            {data && data.data.length > 0 ? (
              data.data.map((supplier) => (
                <TableRow key={supplier.id}>
                  {tableColumns.map((column) => (
                    <TableCell key={column.id}>
                      {column.cell(supplier)}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={tableColumns.length} className="h-24 text-center">
                  No suppliers found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Render Pagination if more than one page */}
      {data && data.meta.totalPages > 1 && (
        <Pagination
          currentPage={page}
          totalPages={data.meta.totalPages}
          onPageChange={setPage}
        />
      )}

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