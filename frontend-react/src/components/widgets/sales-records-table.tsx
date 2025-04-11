"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge, badgeVariants, type BadgeProps } from "@/components/ui/badge";
import type { VariantProps } from "class-variance-authority";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X } from "lucide-react";
import { instance as api } from "@/lib/api";
import { format } from 'date-fns';
import { toast } from "sonner";
import debounce from 'lodash/debounce';

interface Customer {
  id: number;
  name: string;
}

interface SalesRecord {
  id: number;
  record_number: string;
  record_date: string;
  customer: Customer; // Assuming serializer nests customer info
  total_amount: number;
  payment_status: string;
}

interface SalesRecordItem {
  id: number;
  variant_product: { // Assuming nested structure
      sku: string;
      display_name: string;
  };
  quantity: number;
  unit_price: number;
  total_price: number;
  fulfillment_status: string;
}

// Helper to format currency (implement or import a proper one if available)
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(amount);
};

// --- Record Items Modal ---
interface RecordItemsModalProps {
  recordId: number;
  recordNumber: string;
  trigger: React.ReactNode;
}

function RecordItemsModal({ recordId, recordNumber, trigger }: RecordItemsModalProps) {
  const [items, setItems] = useState<SalesRecordItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const fetchItems = async () => {
    if (!recordId || !isOpen) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.get(`v1/sales/records/${recordId}/items/`).json<SalesRecordItem[]>();
      // Now 'data' should be the array directly if the API returns it
      if (Array.isArray(data)) {
          setItems(data);
      } else {
          console.error("Unexpected response structure for items:", data);
          throw new Error("Received non-array data for record items.");
      }
    } catch (err: any) {
      console.error("Error fetching record items:", err);
      // Improved error message extraction
      let detail = "Failed to load record items.";
      if (err.response) {
        try {
          const errorBody = await err.response.json();
          detail = errorBody?.detail || JSON.stringify(errorBody) || detail;
        } catch (parseErr) {
          detail = err.message || detail;
        }
      } else {
          detail = err.message || detail;
      }
      setError(detail);
      toast.error(`Error loading items for ${recordNumber}: ${detail}`);
    } finally {
      setIsLoading(false);
    }
  };

 // Fetch items when the dialog opens
  useEffect(() => {
    if (isOpen) {
      fetchItems();
    } else {
      // Reset state when closing
      setItems([]);
      setError(null);
      setIsLoading(false);
    }
  }, [isOpen, recordId]);


  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Items for Record: {recordNumber}</DialogTitle>
        </DialogHeader>
        <div className="flex-grow overflow-y-auto pr-2">
          {isLoading && (
             <div className="space-y-2">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
             </div>
          )}
          {error && <p className="text-red-500 text-sm">Error: {error}</p>}
          {!isLoading && !error && items.length === 0 && (
            <p className="text-muted-foreground text-center py-4">No items found for this record.</p>
          )}
          {!isLoading && !error && items.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>SKU</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
                  <TableHead className="text-right">Unit Price</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium">{item.variant_product?.sku ?? 'N/A'}</TableCell>
                    <TableCell>{item.variant_product?.display_name ?? 'N/A'}</TableCell>
                    <TableCell className="text-right">{item.quantity}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.unit_price)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.total_price)}</TableCell>
                    <TableCell><Badge variant="outline">{item.fulfillment_status}</Badge></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Define the expected structure for paginated results
interface PaginatedSalesRecords {
    count: number;
    next: string | null;
    previous: string | null;
    results: SalesRecord[];
}

// Define possible choices based on the backend model
const RECORD_TYPE_CHOICES = [
  { value: "INVOICE", label: "Invoice" },
  { value: "PROPOSAL", label: "Proposal" },
  { value: "DELIVERY_NOTE", label: "Delivery Note" },
  { value: "CREDIT_NOTE", label: "Credit Note" },
  { value: "ORDER_CONFIRMATION", label: "Order Confirmation" },
];

const PAYMENT_STATUS_CHOICES = [
  { value: "PENDING", label: "Pending" },
  { value: "PAID", label: "Paid" },
  { value: "OVERDUE", label: "Overdue" },
  { value: "CANCELLED", label: "Cancelled" },
  // Add PARTIALLY_PAID if used
  // { value: "PARTIALLY_PAID", label: "Partially Paid" }, 
];

// --- Sales Records Table ---
export default function SalesRecordsTable() {
  const [records, setRecords] = useState<SalesRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Add state for search and filters
  const [searchTerm, setSearchTerm] = useState("");
  const [recordTypeFilter, setRecordTypeFilter] = useState(""); // Empty string means 'all'
  const [paymentStatusFilter, setPaymentStatusFilter] = useState(""); // Empty string means 'all'
  // Add state for pagination later if needed
  // const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  // Add state for total record count for pagination display
  // const [totalCount, setTotalCount] = useState(0);

  // Debounced search handler
  const debouncedFetchRecords = useCallback(debounce((filters) => {
    fetchRecords(filters);
  }, 500), []); // Adjust debounce time as needed

  // Moved fetchRecords outside useEffect to be callable by debounce
  const fetchRecords = async (currentFilters = { searchTerm, recordTypeFilter, paymentStatusFilter }) => {
    setIsLoading(true);
    setError(null);
    try {
      // Construct query parameters
      const params = new URLSearchParams();
      if (currentFilters.searchTerm) {
        params.append('search', currentFilters.searchTerm);
      }
      if (currentFilters.recordTypeFilter) {
        params.append('record_type', currentFilters.recordTypeFilter);
      }
      if (currentFilters.paymentStatusFilter) {
        params.append('payment_status', currentFilters.paymentStatusFilter);
      }
      // Add pagination params later: 
      // params.append('page', (pagination.pageIndex + 1).toString());
      // params.append('page_size', pagination.pageSize.toString());

      const queryString = params.toString();
      const apiUrl = `v1/sales/records/${queryString ? '?' + queryString : ''}`;

      const responseData = await api.get(apiUrl).json<PaginatedSalesRecords | SalesRecord[]>();

       // Check if it's paginated or a simple array
       if (responseData && 'results' in responseData && Array.isArray(responseData.results)) {
           setRecords(responseData.results);
           // Set total count for pagination later: setTotalCount(responseData.count);
       } else if (Array.isArray(responseData)) { // Handle non-paginated results
           setRecords(responseData);
           // Maybe set total count to length if not paginated: setTotalCount(responseData.length);
       } else {
           console.error("Unexpected response structure:", responseData);
           throw new Error("Received unexpected data structure for sales records.");
       }
    } catch (err: any) {
      console.error("Error fetching sales records:", err);
      // Try to parse error response body if available
      let detail = "Failed to load sales records.";
      if (err.response) {
          try {
              const errorBody = await err.response.json();
              detail = errorBody?.detail || JSON.stringify(errorBody) || detail;
          } catch (parseErr) {
              // Ignore if error body isn't JSON
              detail = err.message || detail;
          }
      } else {
          detail = err.message || detail;
      }
      setError(detail);
      toast.error(`Error loading sales records: ${detail}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial fetch and fetch on filter changes (debounced for search)
  useEffect(() => {
     // Use debounced fetch for search term changes
    debouncedFetchRecords({ searchTerm, recordTypeFilter, paymentStatusFilter });
    // Cleanup debounce on unmount
    return () => debouncedFetchRecords.cancel(); 
  }, [searchTerm, recordTypeFilter, paymentStatusFilter, debouncedFetchRecords]);

  // Handler to clear all filters
  const clearFilters = () => {
    setSearchTerm("");
    setRecordTypeFilter("");
    setPaymentStatusFilter("");
  };

  const renderPaymentStatusBadge = (status: string) => {
      // Use type assertion for variants known to exist
      let variant: VariantProps<typeof badgeVariants>['variant'] = "secondary";
      switch (status) {
          case 'PAID': variant = 'default'; break; // Using 'default' (often green/blue) for PAID
          case 'PARTIALLY_PAID': variant = 'amber'; break; // Using 'amber' for warning-like status
          case 'PENDING': variant = 'outline'; break;
          case 'OVERDUE': variant = 'destructive'; break; // Added Overdue mapping
          case 'CANCELLED': variant = 'destructive'; break;
          // Add more cases as needed
      }
      // Explicitly cast to BadgeProps['variant'] to satisfy the component
      return <Badge variant={variant}>{status.replace('_', ' ')}</Badge>;
  };

  if (isLoading && records.length === 0) { // Show skeleton only on initial load
    return (
        <div className="space-y-2 mt-6">
            <div className="flex flex-wrap gap-2 mb-4">
                <Skeleton className="h-10 w-full sm:w-64" />
                <Skeleton className="h-10 w-[150px]" />
                <Skeleton className="h-10 w-[150px]" />
                <Skeleton className="h-10 w-[80px]" />
            </div>
            <Skeleton className="h-12 w-full" /> {/* Header Skeleton */}
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
        </div>
    );
  }

  if (error) {
    return <p className="text-red-500 mt-6">Error loading sales records: {error}</p>;
  }

  const hasActiveFilters = searchTerm || recordTypeFilter || paymentStatusFilter;

  return (
    <div className="mt-6 space-y-4">
        {/* Filter and Search Controls */}
        <div className="flex flex-wrap items-center gap-2">
            <Input
                placeholder="Search number or customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="h-9 max-w-xs"
            />
            <Select value={recordTypeFilter} onValueChange={setRecordTypeFilter}>
                <SelectTrigger className="h-9 w-[180px]">
                    <SelectValue placeholder="Filter by Record Type" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="">All Record Types</SelectItem>
                    {RECORD_TYPE_CHOICES.map(choice => (
                        <SelectItem key={choice.value} value={choice.value}>{choice.label}</SelectItem>
                    ))}
                </SelectContent>
            </Select>
            <Select value={paymentStatusFilter} onValueChange={setPaymentStatusFilter}>
                <SelectTrigger className="h-9 w-[180px]">
                    <SelectValue placeholder="Filter by Payment Status" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="">All Payment Statuses</SelectItem>
                    {PAYMENT_STATUS_CHOICES.map(choice => (
                        <SelectItem key={choice.value} value={choice.value}>{choice.label}</SelectItem>
                    ))}
                </SelectContent>
            </Select>
            {hasActiveFilters && (
                 <Button variant="ghost" size="sm" onClick={clearFilters} className="h-9 px-2">
                    <X className="h-4 w-4 mr-1" /> Clear
                 </Button>
            )}
        </div>
        
        {/* Optional: Loading indicator when refetching */}
        {isLoading && <p className="text-sm text-muted-foreground">Loading...</p>} 

        {/* Table Section */}
         <div className="border rounded-md">
            <Table>
                <TableHeader>
                <TableRow>
                    <TableHead>Record No.</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead className="text-right">Total Amount</TableHead>
                    <TableHead>Payment Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                </TableRow>
                </TableHeader>
                <TableBody>
                {!isLoading && records.length === 0 && (
                    <TableRow>
                    <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                        No sales records found matching your criteria.
                    </TableCell>
                    </TableRow>
                )}
                {records.map((record) => (
                    <RecordItemsModal
                        key={record.id}
                        recordId={record.id}
                        recordNumber={record.record_number}
                        trigger={
                            <TableRow className="cursor-pointer hover:bg-muted/50">
                                <TableCell className="font-medium">{record.record_number}</TableCell>
                                <TableCell>{format(new Date(record.record_date), 'yyyy-MM-dd')}</TableCell>
                                <TableCell>{record.customer?.name ?? 'N/A'}</TableCell>
                                <TableCell className="text-right">{formatCurrency(record.total_amount)}</TableCell>
                                <TableCell>{renderPaymentStatusBadge(record.payment_status)}</TableCell>
                                <TableCell className="text-right">
                                    <Button variant="ghost" size="sm" onClick={(e) => e.stopPropagation()} >
                                       View Items
                                    </Button>
                                </TableCell>
                            </TableRow>
                        }
                    />
                ))}
                </TableBody>
            </Table>
         </div>
      {/* Add Pagination controls here later */}
    </div>
  );
} 