"use client";

import React, { useState, useEffect } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Search, PlusCircle, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { productApi } from '@/lib/products/api';
import { Product, ApiResponse } from '@/components/types/product';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useLastVisited } from "@/context/LastVisitedContext";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Import Table components
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

// TODO: Ensure QueryClientProvider is set up in layout.tsx or a providers file

// Define the expected input type for creating a product
// This should match the data collected in the form
// plus any other required fields (like parent_id for variants)
type CreateProductInput = {
  name: string;
  sku: string;
  description?: string; // Optional?
  is_active: boolean;
  parent_id?: number | string; // For creating variants
  // Add any other non-optional fields required by productApi.createProduct
};

export function ProductsView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Read initial product ID from URL query parameters
  const initialProductIdParam = searchParams.get('productId');
  const initialProductId = initialProductIdParam ? parseInt(initialProductIdParam, 10) : null;
  // Ensure initialProductId is a valid number, otherwise null
  const validInitialProductId = Number.isNaN(initialProductId) ? null : initialProductId;

  const [selectedItemId, setSelectedItemId] = useState<number | null>(validInitialProductId);
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 20 });
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");
  const [isCreatingParent, setIsCreatingParent] = useState(false);
  const [detailViewMode, setDetailViewMode] = useState<'parent' | 'variants'>('parent');
  const [newProductData, setNewProductData] = useState<CreateProductInput>({
    name: '',
    sku: '',
    description: '',
    is_active: true,
  });

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm), 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Reset pagination when search term changes
  useEffect(() => {
    setPagination(prev => ({ ...prev, pageIndex: 0 }));
  }, [debouncedSearchTerm]);

  // --- Data Fetching with React Query ---

  // Query for the list of products
  const productsQuery = useQuery<ApiResponse<Product>, Error>({
    queryKey: ['products', pagination.pageIndex, pagination.pageSize, debouncedSearchTerm],
    queryFn: async ({ signal }) => {
      const params = {
        page: pagination.pageIndex + 1,
        page_size: pagination.pageSize,
      };
      if (debouncedSearchTerm) {
        // Use direct search if term exists
        return productApi.getProductsDirectSearch({ ...params, q: debouncedSearchTerm }, signal);
      } else {
        // Otherwise, use standard list endpoint
        return productApi.getProducts(params, signal);
      }
    },
    placeholderData: (previousData: ApiResponse<Product> | undefined) => previousData,
    staleTime: 5 * 60 * 1000,
    refetchOnMount: true,
  });

  // Query for the details of the selected product
  const productDetailQuery = useQuery<Product, Error>({
    queryKey: ['product', selectedItemId],
    queryFn: ({ signal }) => productApi.getProduct(selectedItemId!, signal), // Non-null assertion ok due to 'enabled'
    enabled: selectedItemId !== null, // Only run query when an item is selected
    staleTime: 15 * 60 * 1000, // Keep details fresh for 15 minutes
  });

  // Query for the variants of the selected product
  const variantsQuery = useQuery<ApiResponse<Product>, Error>({
    // Use selectedItemId in the queryKey to refetch when selection changes
    queryKey: ['productVariants', selectedItemId],
    queryFn: async ({ signal }) => {
      // Assume productApi has a method to get variants
      // Replace with actual API call if different
      return productApi.getProductVariants(selectedItemId!, signal);
    },
    // Only enable if an item is selected AND it's a parent (has variants_count > 0)
    enabled: !!selectedItemId && !!productDetailQuery.data && productDetailQuery.data.variants_count > 0,
    staleTime: 5 * 60 * 1000, // Cache variants for 5 minutes
  });

  // --- Mutations ---
  const queryClient = useQueryClient();

  const createProductMutation = useMutation<Product, Error, CreateProductInput>({
    mutationFn: (productData) => productApi.createProduct(productData),
    onSuccess: (data) => {
      // Invalidate and refetch the products list to show the new product
      queryClient.invalidateQueries({ queryKey: ['products'] });
      // Reset form and state
      handleParentProductCreated(data);
      setNewProductData({ name: '', sku: '', description: '', is_active: true });
      // Optionally, display a success toast message
    },
    onError: (error) => {
      // Handle error, e.g., display an error message/toast
      console.error("Error creating product:", error);
      // Keep the form open and populated so the user can retry
    },
  });

  // --- Event Handlers ---
  // TODO: Implement handleSelectItem, handlePaginationChange, handleCreateNew

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleSelectItem = (id: number) => {
    setSelectedItemId(id);
    setIsCreatingParent(false);
    setDetailViewMode('parent'); // Reset to parent view on new selection
    // Update URL without adding to history
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('productId', String(id));
    router.replace(`${pathname}?${newSearchParams.toString()}`);
  };

  const handlePaginationChange = (updater: (old: { pageIndex: number, pageSize: number }) => { pageIndex: number, pageSize: number }) => {
    setPagination(prev => updater(prev));
  };

  const handleCreateNew = () => {
    setIsCreatingParent(true);
    setSelectedItemId(null);
    // Remove productId from URL
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.delete('productId');
    router.replace(`${pathname}?${newSearchParams.toString()}`);
  };

  const handleCancelCreate = () => {
    setIsCreatingParent(false);
    // Optionally: Select the first item or clear selection
    // For now, just remove the product ID from the URL if it was there
    // (If we select the first item, handleSelectItem will update the URL)
    if (searchParams.has('productId')) {
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.delete('productId');
      router.replace(`${pathname}?${newSearchParams.toString()}`);
    }
    // TODO: Decide if we should automatically select the first item from the list here
  };

  const handleParentProductCreated = (product: Product) => {
    setIsCreatingParent(false);
    setSelectedItemId(product.id);
    // Update URL with the new product ID
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('productId', String(product.id));
    router.replace(`${pathname}?${newSearchParams.toString()}`);
  };

  // Handle changes in the create form
  const handleCreateFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setNewProductData(prev => ({ ...prev, [name]: value }));
  };

  const handleCreateFormCheckboxChange = (checked: boolean | 'indeterminate') => {
    if (typeof checked === 'boolean') {
      setNewProductData(prev => ({ ...prev, is_active: checked }));
    }
  };

  // Handle form submission
  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Basic validation (can be enhanced)
    if (!newProductData.name || !newProductData.sku) {
      // TODO: Show validation errors more gracefully
      alert("Product Name and SKU are required.");
      return;
    }
    // Ensure the data passed matches CreateProductInput
    // Currently, newProductData matches the basic fields
    createProductMutation.mutate(newProductData);
  };

  // --- Render Logic ---
  const products = productsQuery.data?.results ?? [];
  const totalCount = productsQuery.data?.count ?? 0;
  const selectedProduct = productDetailQuery.data;

  // Add to last visited context when selection changes and data is loaded
  const { addVisitedItem } = useLastVisited();
  useEffect(() => {
    if (selectedProduct && !isCreatingParent) {
      const currentParams = new URLSearchParams(searchParams);
      currentParams.set('productId', String(selectedProduct.id));
      const pathWithQuery = `${pathname}?${currentParams.toString()}`;

      addVisitedItem({
        type: 'product', // Simple type for now
        id: String(selectedProduct.id),
        name: selectedProduct.name,
        path: pathWithQuery,
      });
    }
  }, [selectedProduct, isCreatingParent, addVisitedItem, pathname, searchParams]);

  return (
    <div className="flex flex-col md:flex-row gap-4 h-full">
      {/* Left Pane: Product List / Filters */}
      <Card className="w-full md:w-1/3 flex flex-col">
        <CardHeader>
          <CardTitle>Product List</CardTitle>
          {/* Search Input */}
          <div className="relative mt-2">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              type="search"
              placeholder="Search SKU..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="pl-10 h-9 w-full"
            />
          </div>
        </CardHeader>
        <CardContent className="flex-grow overflow-y-auto">
          {/* Replace ProductList with Table implementation */}
          {productsQuery.isLoading ? (
            <p>Loading products...</p>
          ) : productsQuery.isError ? (
            <p>Error loading products: {productsQuery.error.message}</p>
          ) : products.length > 0 ? (
            <Table>
              <TableCaption>Product List - Page {pagination.pageIndex + 1}</TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead>SKU</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Active</TableHead>
                  <TableHead>Variants</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((product) => (
                  <TableRow
                    key={product.id}
                    onClick={() => handleSelectItem(product.id)}
                    className={`cursor-pointer ${selectedItemId === product.id ? 'bg-muted' : ''}`}
                  >
                    <TableCell>{product.sku}</TableCell>
                    <TableCell>{product.name}</TableCell>
                    <TableCell>{product.is_active ? 'Yes' : 'No'}</TableCell>
                    <TableCell>{product.variants_count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <p className="text-muted-foreground text-center p-4">No products found.</p>
          )}

          {/* Refined Pagination Controls */}
          {totalCount > 0 && (
            <div className="mt-4 flex justify-between items-center px-2 py-1 border-t">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePaginationChange((old: any) => ({ ...old, pageIndex: old.pageIndex - 1 }))}
                disabled={pagination.pageIndex === 0 || productsQuery.isFetching}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {pagination.pageIndex + 1} of {Math.ceil(totalCount / pagination.pageSize)}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePaginationChange((old: any) => ({ ...old, pageIndex: old.pageIndex + 1 }))}
                disabled={pagination.pageIndex + 1 >= Math.ceil(totalCount / pagination.pageSize) || productsQuery.isFetching}
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          )}

        </CardContent>
        <div className="p-4 border-t flex-shrink-0">
          <Button className='w-full' onClick={handleCreateNew}>
            <PlusCircle className="mr-2 h-4 w-4" />
            New Product
          </Button>
        </div>
      </Card>

      {/* Right Pane: Product Details / Create Form */}
      <Card className="w-full md:w-2/3 flex flex-col">
        <CardHeader>
          <CardTitle>Product Details</CardTitle>
        </CardHeader>
        <CardContent className="flex-grow overflow-y-auto">
          {isCreatingParent ? (
            // Create Parent Product Form
            <form onSubmit={handleCreateSubmit} className='p-4 space-y-4'>
              <p className="text-muted-foreground mb-4">Enter details for the new parent product.</p>
              
              {/* Display API Error Message */}
              {createProductMutation.isError && (
                 <Alert variant="destructive">
                   <AlertTitle>Error Creating Product</AlertTitle>
                   <AlertDescription>
                     {createProductMutation.error?.message || 'An unknown error occurred.'}
                   </AlertDescription>
                 </Alert>
               )}

              <div className="space-y-2">
                <Label htmlFor="product-name">Product Name <span className="text-red-500">*</span></Label>
                <Input 
                  id="product-name" 
                  name="name" 
                  placeholder="e.g., Basic Widget" 
                  value={newProductData.name}
                  onChange={handleCreateFormChange}
                  required
                  disabled={createProductMutation.isPending}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="product-sku">SKU <span className="text-red-500">*</span></Label>
                <Input 
                  id="product-sku" 
                  name="sku" 
                  placeholder="e.g., WID-001" 
                  value={newProductData.sku}
                  onChange={handleCreateFormChange}
                  required
                  disabled={createProductMutation.isPending}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="product-description">Description</Label>
                <Textarea 
                  id="product-description" 
                  name="description" 
                  placeholder="Detailed description of the product..."
                  value={newProductData.description}
                  onChange={handleCreateFormChange}
                  disabled={createProductMutation.isPending}
                />
              </div>
              
              <div className="flex items-center space-x-2 pt-2">
                <Checkbox 
                  id="product-active" 
                  name="is_active"
                  checked={newProductData.is_active}
                  onCheckedChange={handleCreateFormCheckboxChange}
                  disabled={createProductMutation.isPending}
                />
                <Label htmlFor="product-active" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  Active Product
                </Label>
              </div>

              <div className='flex justify-end gap-2 pt-4'>
                 <Button 
                   variant="outline" 
                   onClick={handleCancelCreate} 
                   type="button" // Important: prevent form submission
                   disabled={createProductMutation.isPending}
                 >
                   Cancel
                 </Button>
                 <Button
                   type="submit"
                   disabled={createProductMutation.isPending}
                 >
                   {createProductMutation.isPending ? (
                     <>
                       <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                       Creating...
                     </>
                   ) : (
                     'Create Product'
                   )}
                 </Button>
              </div>
            </form>
          ) : selectedItemId === null ? (
             <p className="text-muted-foreground flex items-center justify-center h-full">Select a product to view details.</p>
          ) : productDetailQuery.isLoading ? (
            <p className="text-muted-foreground flex items-center justify-center h-full">Loading details for item {selectedItemId}...</p>
          ) : productDetailQuery.isError ? (
             <p className="text-destructive flex items-center justify-center h-full">Error loading details: {productDetailQuery.error.message}</p>
          ) : selectedProduct ? (
             // Use Tabs if the selected product has variants
             selectedProduct.variants_count > 0 ? (
               <Tabs defaultValue="parent" value={detailViewMode} onValueChange={(value) => setDetailViewMode(value as 'parent' | 'variants')} className="p-4 h-full flex flex-col">
                 <TabsList className="mb-4">
                   <TabsTrigger value="parent">Parent Details</TabsTrigger>
                   <TabsTrigger value="variants">Variants ({selectedProduct.variants_count})</TabsTrigger>
                 </TabsList>
                 <TabsContent value="parent" className="flex-grow overflow-y-auto space-y-4">
                   {/* Existing Parent Detail Display Logic */} 
                   {selectedProduct.primary_image && (
                     <div className="mb-4">
                       <img
                         src={selectedProduct.primary_image}
                         alt={selectedProduct.name}
                         className="max-w-xs max-h-48 object-contain rounded-md border"
                       />
                     </div>
                   )}
                   <h2 className='text-2xl font-bold text-primary mb-2'>{selectedProduct.name}</h2>
                   <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                     <div><span className='font-medium text-muted-foreground'>SKU:</span> {selectedProduct.sku}</div>
                     <div><span className='font-medium text-muted-foreground'>Category:</span> {selectedProduct.category || 'N/A'}</div>
                     <div><span className='font-medium text-muted-foreground'>Active:</span> <Badge variant={selectedProduct.is_active ? 'default' : 'secondary'}>{selectedProduct.is_active ? 'Yes' : 'No'}</Badge></div>
                     <div><span className='font-medium text-muted-foreground'>Variants:</span> {selectedProduct.variants_count}</div>
                     {selectedProduct.release_date &&
                       <div><span className='font-medium text-muted-foreground'>Release Date:</span> {new Date(selectedProduct.release_date).toLocaleDateString()}</div>
                     }
                     <div><span className='font-medium text-muted-foreground'>Discontinued:</span> <Badge variant={selectedProduct.is_discontinued ? 'destructive' : 'secondary'}>{selectedProduct.is_discontinued ? 'Yes' : 'No'}</Badge></div>
                   </div>
                   <Separator className="my-4" />
                   <div>
                     <h3 className="text-lg font-semibold mb-1">Description</h3>
                     <p className="text-sm text-muted-foreground">{selectedProduct.description || 'No description provided.'}</p>
                   </div>
                   {(selectedProduct.tags?.length > 0 || selectedProduct.keywords) && (
                     <div>
                       <h3 className="text-lg font-semibold mb-2">Tags & Keywords</h3>
                       <div className="flex flex-wrap gap-1">
                         {selectedProduct.tags?.map((tag) => (
                           <Badge key={tag} variant="outline">{tag}</Badge>
                         ))}
                         {selectedProduct.keywords?.split(/[,; ]+/).map((keyword) => (
                           keyword && <Badge key={keyword} variant="secondary">{keyword}</Badge>
                         ))}
                       </div>
                     </div>
                   )}
                   <div className="text-xs text-muted-foreground mt-4">
                     <p>Created: {new Date(selectedProduct.created_at).toLocaleString()}</p>
                     <p>Last Updated: {new Date(selectedProduct.updated_at).toLocaleString()}</p>
                   </div>
                   {/* End of Existing Parent Detail Display Logic */}
                 </TabsContent>
                 <TabsContent value="variants" className="flex-grow overflow-y-auto space-y-4">
                   <h3 className="text-lg font-semibold mb-2">Product Variants</h3>
                   {/* TODO: Implement Variant List Display */} 
                   {variantsQuery.isLoading && <p>Loading variants...</p>}
                   {variantsQuery.isError && <p className="text-destructive">Error loading variants: {variantsQuery.error.message}</p>}
                   {variantsQuery.data && (
                     <p>Variants data loaded. (Count: {variantsQuery.data.results?.length})</p>
                     // Placeholder: Replace with actual variant list/table
                     // <VariantTable variants={variantsQuery.data.results} /> 
                   )}
                   
                   {/* TODO: Add Create Variant Button */} 
                   <Button size="sm" disabled> {/* Disable until create logic is added */} 
                     <PlusCircle className="mr-2 h-4 w-4" />
                     Create New Variant
                   </Button>
                 </TabsContent>
               </Tabs>
             ) : (
               // Render standard details if no variants
               <div className='p-4 space-y-4 flex-grow overflow-y-auto'>
                 {/* Existing Parent Detail Display Logic (Duplicated for non-variant case) */} 
                 {selectedProduct.primary_image && (
                     <div className="mb-4">
                       <img
                         src={selectedProduct.primary_image}
                         alt={selectedProduct.name}
                         className="max-w-xs max-h-48 object-contain rounded-md border"
                       />
                     </div>
                   )}
                   <h2 className='text-2xl font-bold text-primary mb-2'>{selectedProduct.name}</h2>
                   <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                     <div><span className='font-medium text-muted-foreground'>SKU:</span> {selectedProduct.sku}</div>
                     <div><span className='font-medium text-muted-foreground'>Category:</span> {selectedProduct.category || 'N/A'}</div>
                     <div><span className='font-medium text-muted-foreground'>Active:</span> <Badge variant={selectedProduct.is_active ? 'default' : 'secondary'}>{selectedProduct.is_active ? 'Yes' : 'No'}</Badge></div>
                     <div><span className='font-medium text-muted-foreground'>Variants:</span> {selectedProduct.variants_count}</div>
                     {selectedProduct.release_date &&
                       <div><span className='font-medium text-muted-foreground'>Release Date:</span> {new Date(selectedProduct.release_date).toLocaleDateString()}</div>
                     }
                     <div><span className='font-medium text-muted-foreground'>Discontinued:</span> <Badge variant={selectedProduct.is_discontinued ? 'destructive' : 'secondary'}>{selectedProduct.is_discontinued ? 'Yes' : 'No'}</Badge></div>
                   </div>
                   <Separator className="my-4" />
                   <div>
                     <h3 className="text-lg font-semibold mb-1">Description</h3>
                     <p className="text-sm text-muted-foreground">{selectedProduct.description || 'No description provided.'}</p>
                   </div>
                   {(selectedProduct.tags?.length > 0 || selectedProduct.keywords) && (
                     <div>
                       <h3 className="text-lg font-semibold mb-2">Tags & Keywords</h3>
                       <div className="flex flex-wrap gap-1">
                         {selectedProduct.tags?.map((tag) => (
                           <Badge key={tag} variant="outline">{tag}</Badge>
                         ))}
                         {selectedProduct.keywords?.split(/[,; ]+/).map((keyword) => (
                           keyword && <Badge key={keyword} variant="secondary">{keyword}</Badge>
                         ))}
                       </div>
                     </div>
                   )}
                   <div className="text-xs text-muted-foreground mt-4">
                     <p>Created: {new Date(selectedProduct.created_at).toLocaleString()}</p>
                     <p>Last Updated: {new Date(selectedProduct.updated_at).toLocaleString()}</p>
                   </div>
               </div>
             )
          ) : (
             <p className="text-muted-foreground flex items-center justify-center h-full">Product details not found.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
