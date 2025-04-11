'use client'; // Required for hooks like useQuery and client components

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PlusCircle, Search, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

import { Supplier } from '@/types/supplier';
import {
  fetchSuppliers,
  deleteSupplier,
  FetchSuppliersResult,
  SyncStatus,
  syncSuppliersFromAccounting,
} from '@/lib/api/suppliers';
// Remove table imports
// import {
//   Table,
//   TableHeader,
//   TableBody,
//   TableRow,
//   TableHead,
//   TableCell,
//   TableCaption,
// } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
// Remove Dropdown imports if only used by table actions
// import {
//   DropdownMenu,
//   DropdownMenuContent,
//   DropdownMenuItem,
//   DropdownMenuLabel,
//   DropdownMenuTrigger,
// } from '@/components/ui/dropdown-menu';
import { Skeleton } from '@/components/ui/skeleton'; // For loading state
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'; // For error state
import { useToast } from '@/hooks/use-toast';
import { Pagination } from '@/components/ui/pagination';
import { SupplierDialog } from './SupplierDialog';
import { SupplierDeleteDialog } from './SupplierDeleteDialog';
// Import SupplierCard
import { SupplierCard } from './SupplierCard';
// Import the new SupplierDetailDialog
import { SupplierDetailDialog } from './SupplierDetailDialog';

// Remove Column interface and getColumns function
/*
interface TableColumn<T> {
  id: string;
  header: string;
  cell: (row: T) => React.ReactNode;
}
const getColumns = (
  onEdit: (supplier: Supplier) => void,
  onDelete: (supplier: Supplier) => void
): TableColumn<Supplier>[] => [
  // ... columns definition ...
];
*/

export function SupplierDashboard() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [page, setPage] = useState(1);
  // Change pageSize for grid layout
  const [pageSize] = useState(9); // 3x3 grid on larger screens
  const [syncStatusFilter, setSyncStatusFilter] = useState<SyncStatus>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deletingSupplier, setDeletingSupplier] = useState<Supplier | null>(null);
  // Add state for sync loading
  const [isSyncing, setIsSyncing] = useState(false);
  // Add state for detail dialog
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [viewingSupplier, setViewingSupplier] = useState<Supplier | null>(null);

  const {
    data,
    isLoading,
    error,
    isError,
  } = useQuery<FetchSuppliersResult, Error>({
    queryKey: ['suppliers', searchTerm, page, pageSize, syncStatusFilter],
    // Pass updated pageSize
    queryFn: () => fetchSuppliers(searchTerm, page, pageSize, syncStatusFilter),
  });

  const syncMutation = useMutation({
    mutationFn: syncSuppliersFromAccounting,
    onMutate: () => {
      setIsSyncing(true);
    },
    onSuccess: (syncResult) => {
      toast({
        title: "Sync Successful",
        description: `${syncResult.count} suppliers synchronized from accounting system.`,
      });
      // Invalidate all supplier queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
    },
    onError: (error) => {
      toast({
        title: "Sync Failed",
        description: error.message || "An unknown error occurred during sync.",
        variant: "destructive",
      });
    },
    onSettled: () => {
      setIsSyncing(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteSupplier,
    onSuccess: (_, deletedId) => {
      toast({
        title: "Supplier Deleted",
        description: `Supplier with ID ${deletedId} has been deleted successfully.`
      });
      // Invalidate using updated pageSize
      queryClient.invalidateQueries({ queryKey: ['suppliers', searchTerm, page, pageSize, syncStatusFilter] });
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

  // Add handler for viewing details
  const handleViewDetails = (supplier: Supplier) => {
    setViewingSupplier(supplier);
    setIsDetailDialogOpen(true);
  };

  const confirmDeleteSupplier = () => {
    if (deletingSupplier) {
      deleteMutation.mutate(deletingSupplier.id);
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(1);
  };

  const handleSyncStatusChange = (value: string) => {
    const newStatus = value as SyncStatus;
    setSyncStatusFilter(newStatus);
    setPage(1);
  };

  const handleSync = () => {
    syncMutation.mutate();
  };

  // Loading state with card skeletons
  if (isLoading) {
    return (
      <div className="space-y-4">
        {/* Header remains the same */}
        <div className="flex flex-col sm:flex-row gap-4 justify-between items-center">
          {/* Search/Filter */} 
          <div className="flex flex-1 items-center gap-2 w-full sm:w-auto">
            <div className="relative flex-grow sm:flex-grow-0 sm:max-w-xs">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input type="search" placeholder="Search suppliers..." value={searchTerm} onChange={handleSearchChange} className="pl-8 w-full" />
            </div>
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
          {/* Action Buttons */} 
          <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
            <Button variant="outline" onClick={handleSync} disabled={isSyncing} className="w-full sm:w-auto">
              <RefreshCw className={cn("mr-2 h-4 w-4", isSyncing && "animate-spin")} />
              Sync from Accounting
            </Button>
            <Button onClick={handleAddSupplier} className="w-full sm:w-auto">
              <PlusCircle className="mr-2 h-4 w-4" /> Add Supplier
            </Button>
          </div>
        </div>
        {/* Card Skeleton Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(pageSize)].map((_, index) => (
            <Skeleton key={index} className="h-[180px] rounded-lg" /> // Adjust height as needed
          ))}
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
      {/* Header section (Search, Filter, Sync, Add) */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center">
        {/* Search/Filter */} 
        <div className="flex flex-1 items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-grow sm:flex-grow-0 sm:max-w-xs">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input type="search" placeholder="Search suppliers..." value={searchTerm} onChange={handleSearchChange} className="pl-8 w-full" />
          </div>
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
        {/* Action Buttons */} 
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <Button variant="outline" onClick={handleSync} disabled={isSyncing} className="w-full sm:w-auto">
            <RefreshCw className={cn("mr-2 h-4 w-4", isSyncing && "animate-spin")} />
            Sync from Accounting
          </Button>
          <Button onClick={handleAddSupplier} className="w-full sm:w-auto">
            <PlusCircle className="mr-2 h-4 w-4" /> Add Supplier
          </Button>
        </div>
      </div>

      {/* Grid for Supplier Cards */}
      {data && data.data.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.data.map((supplier) => (
            <SupplierCard
              key={supplier.id}
              supplier={supplier}
              onEdit={handleEditSupplier}
              onDelete={handleDeleteSupplier}
              onViewDetails={handleViewDetails}
            />
          ))}
        </div>
      ) : (
        // Empty state message
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">No suppliers found matching your criteria.</p>
          {/* Optionally add the Add button here too if desired */}
          {/* <Button onClick={handleAddSupplier}>
             <PlusCircle className="mr-2 h-4 w-4" /> Add First Supplier
             </Button> */}
        </div>
      )}

      {/* Pagination */}
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

      {/* Add the new View Details Dialog */}
      <SupplierDetailDialog
        open={isDetailDialogOpen}
        onOpenChange={setIsDetailDialogOpen}
        supplier={viewingSupplier}
      />
    </div>
  );
} 