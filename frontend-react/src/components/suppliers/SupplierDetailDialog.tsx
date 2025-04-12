'use client';

import * as React from 'react';
import { Supplier } from '@/types/supplier'; // Assuming Supplier type is defined here
import { ParentProductSummary } from '@/types/product'; // Assuming a summary type
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter, // Added for potential actions
} from '@/components/ui/dialog';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button'; // Added
import { Input } from '@/components/ui/input'; // Added
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"; // Added
import { ScrollArea } from "@/components/ui/scroll-area"; // Added
import { toast } from "sonner"; // Added for notifications

interface SupplierDetailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  supplier: Supplier | null; // Pass the full supplier object
}

// Define a type for search results - adjust as needed based on API response
interface ProductSearchResult {
  id: number; // Parent Product ID
  sku: string; // Parent Product SKU
  name: string; // Parent Product Name
  matched_sku?: string; // SKU of the matched item (Parent or Variant)
  matched_name?: string; // Name of the matched item
  is_variant: boolean; // Flag indicating if the match was a variant
}

// Helper function to get CSRF token from cookies
function getCookie(name: string): string | null {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export function SupplierDetailDialog({ open, onOpenChange, supplier }: SupplierDetailDialogProps) {
  const isSynced = !!supplier?.syncedAt; // Use syncedAt based on type assumption

  // State for assigned products
  const [assignedProducts, setAssignedProducts] = React.useState<ParentProductSummary[]>([]);
  const [assignedLoading, setAssignedLoading] = React.useState(false);
  const [assignedError, setAssignedError] = React.useState<string | null>(null);

  // State for product search
  const [searchQuery, setSearchQuery] = React.useState('');
  const [searchResults, setSearchResults] = React.useState<ProductSearchResult[]>([]);
  const [searchLoading, setSearchLoading] = React.useState(false);
  const [searchError, setSearchError] = React.useState<string | null>(null);

  // --- API Functions ---
  const fetchAssignedProducts = async (supplierId: number) => {
    setAssignedLoading(true);
    setAssignedError(null);
    try {
      const response = await fetch(`/api/v1/business/suppliers/${supplierId}/products/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: ParentProductSummary[] = await response.json();
      setAssignedProducts(data);
    } catch (error) {
      console.error("Failed to fetch assigned products:", error);
      setAssignedError('Failed to fetch assigned products.');
      toast.error("Could not load assigned products.");
    } finally {
      setAssignedLoading(false);
    }
  };

  const searchProducts = async () => {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    setSearchError(null);
    setSearchResults([]);
    try {
      const response = await fetch(`/api/v1/products/search/?q=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: ProductSearchResult[] = await response.json();
      setSearchResults(data);
      if (!data.length) {
        toast.info("No products found matching your query.");
      }
    } catch (error) {
      console.error("Failed to search products:", error);
      setSearchError('Product search failed.');
      toast.error("Product search failed.");
    } finally {
        setSearchLoading(false);
    }
  };

  const assignProduct = async (parentProductId: number) => {
    if (!supplier) return;
    const csrftoken = getCookie('csrftoken'); // Get CSRF token

    if (!csrftoken) {
        toast.error("CSRF token not found. Cannot assign product.");
        console.error("CSRF token not found.");
        return;
    }

    try {
        const response = await fetch(`/api/v1/business/suppliers/${supplier.id}/assign-product/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken, // Include CSRF token
            },
            body: JSON.stringify({ product_id: parentProductId }),
        });

        if (!response.ok) {
            // Attempt to parse error message from backend if available
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                // Ignore if response is not JSON
            }
            console.error("Assign product response error:", response.status, errorData);
            throw new Error(errorData?.detail || `HTTP error! status: ${response.status}`);
        }

        toast.success(`Product assigned successfully!`);
        // Refresh assigned products list and clear search
        fetchAssignedProducts(supplier.id);
        setSearchQuery('');
        setSearchResults([]);

    } catch (error) {
        console.error("Failed to assign product:", error);
        toast.error(`Failed to assign product: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };
  // --- End API Functions ---

  // Effect to fetch assigned products when the dialog opens or supplier changes
  React.useEffect(() => {
    if (open && supplier) {
      fetchAssignedProducts(supplier.id);
      // Reset search state when dialog opens for a new supplier
      setSearchQuery('');
      setSearchResults([]);
      setSearchError(null);
      setSearchLoading(false);
    } else {
      // Clear data when dialog closes or supplier is null
      setAssignedProducts([]);
      setAssignedError(null);
      setAssignedLoading(false);
    }
  }, [open, supplier]); // Dependency array includes open and supplier

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[800px] max-h-[90vh] flex flex-col"> {/* Increased width */}
        <DialogHeader>
          <DialogTitle>
            {supplier ? supplier.name : 'Supplier Details'}
          </DialogTitle>
          <DialogDescription>
            Detailed information and associated products for the selected supplier.
          </DialogDescription>
        </DialogHeader>

        {/* Wrap content in ScrollArea for overflow */}
        <ScrollArea className="flex-grow pr-6 -mr-6"> {/* Allow content to scroll */}
          {!supplier ? (
            // Display Skeleton or message if supplier is null
            <div className="space-y-4 py-4">
               <Skeleton className="h-8 w-3/4 mb-2" />
               <Skeleton className="h-4 w-1/2" />
               <Skeleton className="h-4 w-1/2" />
               <Skeleton className="h-4 w-full" />
               <Skeleton className="h-4 w-1/3" />
               <Skeleton className="h-4 w-1/3" />
               <Skeleton className="h-6 w-1/4" />
            </div>
          ) : (
            // Display supplier details and products
            <div className="py-4 space-y-6"> {/* Increased spacing */}
              {/* Supplier Information Card (existing) */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle>Supplier Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-3">
                    <div className="space-y-1">
                      <Label htmlFor="detail-name" className="text-xs text-muted-foreground">Company Name</Label>
                      <div id="detail-name">{supplier.name || '-'}</div>
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="detail-contact" className="text-xs text-muted-foreground">Contact Person</Label>
                      <div id="detail-contact">{supplier.contactPerson || '-'}</div>
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="detail-email" className="text-xs text-muted-foreground">Email</Label>
                      <div id="detail-email" className="truncate">{supplier.email || '-'}</div>
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="detail-phone" className="text-xs text-muted-foreground">Phone</Label>
                      <div id="detail-phone">{supplier.phone || '-'}</div>
                    </div>
                    <div className="space-y-1 md:col-span-2">
                      <Label htmlFor="detail-address" className="text-xs text-muted-foreground">Address</Label>
                      <div id="detail-address">{supplier.address || '-'}</div>
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="detail-tax-id" className="text-xs text-muted-foreground">Tax ID</Label>
                      <div id="detail-tax-id">{supplier.taxId || '-'}</div>
                    </div>
                    <div className="space-y-1">
                       <Label htmlFor="detail-creditor-id" className="text-xs text-muted-foreground">Creditor ID</Label>
                       <div id="detail-creditor-id">{supplier.creditorId || '-'}</div>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs text-muted-foreground">Sync Status</Label>
                      <div>
                        <Badge
                          variant={isSynced ? 'default' : 'outline'}
                          className={
                            isSynced
                              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-300 dark:border-green-700'
                              : ''
                          }
                        >
                          {isSynced ? 'Synced' : 'Not Synced'}
                          {isSynced && supplier.syncedAt && ` (${new Date(supplier.syncedAt).toLocaleDateString()})`}
                        </Badge>
                      </div>
                    </div>
                    {/* Conditionally render accountingId if it exists */}
                    {supplier.accountingId !== undefined && (
                       <div className="space-y-1">
                         <Label htmlFor="detail-accounting-id" className="text-xs text-muted-foreground">Accounting ID</Label>
                         <div id="detail-accounting-id">{supplier.accountingId || '-'}</div>
                       </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Assigned Products Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Assigned Products</CardTitle>
                  <CardDescription>
                    Parent products currently assigned to this supplier.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {assignedLoading && <Skeleton className="h-20 w-full" />}
                  {assignedError && <p className="text-sm text-destructive">{assignedError}</p>}
                  {!assignedLoading && !assignedError && (
                    assignedProducts.length > 0 ? (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>SKU</TableHead>
                            <TableHead>Name</TableHead>
                            {/* Add more columns if needed */}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {assignedProducts.map((product) => (
                            <TableRow key={product.id}>
                              <TableCell className="font-medium">{product.sku}</TableCell>
                              <TableCell>{product.name}</TableCell>
                              {/* Add actions like 'Remove' later */}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <p className="text-sm text-muted-foreground">No products assigned to this supplier yet.</p>
                    )
                  )}
                </CardContent>
              </Card>

              {/* Add Product Card */}
              <Card>
                <CardHeader>
                  <CardTitle>Assign New Product</CardTitle>
                  <CardDescription>
                    Search for Parent or Variant products by SKU or Name and assign the Parent Product to this supplier.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex space-x-2">
                    <Input
                      placeholder="Search by SKU or Name..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && searchProducts()} // Allow Enter key search
                      disabled={searchLoading}
                    />
                    <Button onClick={searchProducts} disabled={searchLoading || !searchQuery.trim()}>
                      {searchLoading ? 'Searching...' : 'Search'}
                    </Button>
                  </div>

                  {searchError && <p className="text-sm text-destructive">{searchError}</p>}

                  {/* Search Results */}
                  {searchResults.length > 0 && (
                    <div className="border rounded-md max-h-60 overflow-y-auto"> {/* Scrollable results */}
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Matched Item</TableHead>
                            <TableHead>Parent Product</TableHead>
                            <TableHead>Action</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {searchResults.map((result) => (
                            <TableRow key={`${result.id}-${result.matched_sku || 'parent'}`}>
                              <TableCell>
                                <div className='font-medium'>{result.matched_name} ({result.matched_sku})</div>
                                {result.is_variant && <Badge variant="outline" className="text-xs">Variant</Badge>}
                              </TableCell>
                              <TableCell>
                                {result.name} ({result.sku})
                              </TableCell>
                              <TableCell>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => assignProduct(result.id)}
                                  // Consider disabling if already assigned
                                  disabled={assignedProducts.some(p => p.id === result.id)}
                                >
                                  {assignedProducts.some(p => p.id === result.id) ? 'Assigned' : 'Assign'}
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </ScrollArea> {/* End ScrollArea */}

        {/* Optional Footer for Close button or other actions */}
        {/* <DialogFooter className="mt-auto pt-4 border-t">
          <Button variant="outline" onClick={() => onOpenChange(false)}>Close</Button>
        </DialogFooter> */}
      </DialogContent>
    </Dialog>
  );
} 