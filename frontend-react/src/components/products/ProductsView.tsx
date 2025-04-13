"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient, useMutation, QueryClient, UseQueryResult } from '@tanstack/react-query';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Search, PlusCircle, ChevronLeft, ChevronRight, Loader2, Edit, Save, X, Filter } from 'lucide-react';
import { productApi } from '@/lib/products/api';
import { Product, ApiResponse, Supplier } from '@/components/types/product';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useLastVisited } from "@/context/LastVisitedContext";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { type AppRouterInstance } from 'next/dist/shared/lib/app-router-context.shared-runtime';
import { TwoPaneLayout, type MaximizedPaneState } from '@/components/ui/TwoPaneLayout';
import { type Variant } from '@/lib/products/api';
import Image from 'next/image';

// TODO: Ensure QueryClientProvider is set up in layout.tsx or a providers file

// Define the expected input type for creating/updating a product
// Make most fields optional for update
type ProductFormData = Partial<Product> & {
  name: string; // Name is likely always required
  sku: string;  // SKU is likely always required
  height_mm?: number | null;
  length_mm?: number | null;
  width_mm?: number | null;
  weight?: number | null;
  is_hanging?: boolean;
  is_one_sided?: boolean;
  is_new?: boolean;
  legacy_base_sku?: string | null;
};

// Define default empty state for a new product
const defaultProductData: ProductFormData = {
  name: '',
  sku: '',
  description: '',
  is_active: true,
  is_discontinued: false,
  category: '',
  release_date: null,
  tags: [],
  keywords: '',
  primary_image: null,
  variants_count: 0,
  height_mm: null,
  length_mm: null,
  width_mm: null,
  weight: null,
  is_hanging: false,
  is_one_sided: false,
  is_new: false,
  legacy_base_sku: undefined,
};

export function ProductsView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const queryClient: QueryClient = useQueryClient();
  const { toast } = useToast();

  // Read initial product ID from URL query parameters
  const initialProductIdParam = searchParams.get('productId');
  const initialProductId = initialProductIdParam ? parseInt(initialProductIdParam, 10) : null;
  // Ensure initialProductId is a valid number, otherwise null
  const validInitialProductId = Number.isNaN(initialProductId) ? null : initialProductId;

  const [selectedItemId, setSelectedItemId] = useState<number | null>(validInitialProductId);
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 20 });
  const [searchTerm, setSearchTerm] = useState("");
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");
  const [detailViewMode, setDetailViewMode] = useState<'parent' | 'variants'>('parent');
  const [isEditing, setIsEditing] = useState(false);
  const [isEditingNew, setIsEditingNew] = useState(false);
  const [productFormData, setProductFormData] = useState<ProductFormData>(defaultProductData);
  const [apiError, setApiError] = useState<string | null>(null);
  const [maximizedPane, setMaximizedPane] = useState<MaximizedPaneState>('left');
  const [filterActive, setFilterActive] = useState(true);

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm), 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Reset pagination when search term or filter changes
  useEffect(() => {
    setPagination(prev => ({ ...prev, pageIndex: 0 }));
  }, [debouncedSearchTerm, filterActive]);

  // --- Data Fetching with React Query ---

  // Query for the list of products
  const productsQuery = useQuery<ApiResponse<Product>, Error>({
    queryKey: ['products', pagination.pageIndex, pagination.pageSize, debouncedSearchTerm, filterActive],
    queryFn: async ({ signal }) => {
      const params: Record<string, any> = {
        page: pagination.pageIndex + 1,
        page_size: pagination.pageSize,
        is_active: filterActive,
      };
      if (debouncedSearchTerm) {
         params.q = debouncedSearchTerm;
         return productApi.getProductsDirectSearch(params, signal);
      } else {
         return productApi.getProducts(params, signal);
      }
    },
    placeholderData: (previousData) => previousData,
    staleTime: 5 * 60 * 1000,
    refetchOnMount: true,
  });

  // Query for the details of the selected product
  const productDetailQuery = useQuery<Product & { suppliers?: Supplier[] }, Error>({
    queryKey: ['product', selectedItemId],
    queryFn: ({ signal }) => productApi.getProduct(selectedItemId!, signal) as Promise<Product & { suppliers?: Supplier[] }>,
    enabled: selectedItemId !== null && !isEditingNew,
    staleTime: 15 * 60 * 1000,
  });

  // Use useEffect to handle side effects of productDetailQuery changes
  useEffect(() => {
    if (productDetailQuery.isSuccess && productDetailQuery.data && !isEditing) {
      const data = productDetailQuery.data;
      setProductFormData({
        ...defaultProductData,
        ...data,
        name: data.name ?? '',
        sku: data.sku ?? '',
      });
      setApiError(null);
    } else if (productDetailQuery.isError) {
      setApiError(`Error loading details: ${productDetailQuery.error.message}`);
    }
  }, [productDetailQuery.data, productDetailQuery.isSuccess, productDetailQuery.isError, isEditing]);

  // Query for the variants of the selected product
  const variantsQuery: UseQueryResult<Variant[], Error> = useQuery<Variant[], Error>({
    queryKey: ['productVariants', selectedItemId],
    queryFn: async ({ signal }) => {
      return productApi.getProductVariants(selectedItemId!, signal);
    },
    enabled: !!selectedItemId,
    staleTime: 5 * 60 * 1000,
  });

  // --- Mutations ---

  const createProductMutation = useMutation<Product, Error, ProductFormData>({
    mutationFn: (data) => productApi.createProduct({
      ...data,
      description: data.description ?? '',
    } as Omit<Product, "id"> & { parent_id?: string | number | undefined }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.setQueryData(['product', data.id], data);
      setSelectedItemId(data.id);
      setIsEditing(false);
      setIsEditingNew(false);
      setApiError(null);
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set('productId', String(data.id));
      router.replace(`${pathname}?${newSearchParams.toString()}`);
      toast({ title: "Success", description: "Product created successfully." });
    },
    onError: (error) => {
      console.error("Error creating product:", error);
      setApiError(`Error creating product: ${error.message}`);
    },
  });

  const updateProductMutation = useMutation<
    Product,
    Error,
    { id: number; data: ProductFormData }
  >({
    mutationFn: async ({ id, data }) => {
      const updatedProduct = await productApi.updateProduct(String(id), data);
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.setQueryData(['product', id], updatedProduct);

      // ** Check if a supplier needs to be assigned **
      const supplierToAssign = data.supplier;
      if (supplierToAssign && supplierToAssign.id) {
        try {
          await productApi.assignSupplierToProduct(String(id), supplierToAssign.id);
          queryClient.invalidateQueries({ queryKey: ['product', id] });
          toast({ title: "Success", description: `Product updated and supplier '${supplierToAssign.name}' assigned.` });
        } catch (assignError) {
          console.error("Error assigning supplier after product update:", assignError);
          // Show update success, but supplier assignment failure
          toast({
            title: "Update Successful, Assignment Failed",
            description: `Product details saved, but failed to assign supplier '${supplierToAssign.name}'. Please try assigning again manually. Error: ${assignError instanceof Error ? assignError.message : 'Unknown error'} `,
            variant: "destructive",
            duration: 7000,
          });
        }
      } else {
        // If no supplier was selected, or it was set to 'none', show standard success message
        toast({ title: "Success", description: "Product updated successfully." });
      }

      // Reset form state regardless of supplier assignment result
      if (selectedItemId === id && updatedProduct) {
        setProductFormData({
          ...defaultProductData,
          ...updatedProduct,
          name: updatedProduct.name ?? '',
          sku: updatedProduct.sku ?? '',
        });
      }
      setIsEditing(false);
      setApiError(null);
      return updatedProduct;
    },
    onError: (error) => {
      console.error("Error updating product:", error);
      setApiError(`Error updating product: ${error.message}`);
    },
  });

  // --- Event Handlers ---

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleSelectItem = (id: number) => {
    if (isEditing) {
      alert("Please save or cancel your current changes before selecting another product.");
      return;
    }
    setSelectedItemId(id);
    setIsEditing(false);
    setIsEditingNew(false);
    setDetailViewMode('parent');
    setApiError(null);
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set('productId', String(id));
    router.replace(`${pathname}?${newSearchParams.toString()}`);
    // Switch to split view if left pane was maximized
    if (maximizedPane === 'left') {
        setMaximizedPane('none');
    }
  };

  const handlePaginationChange = (updater: (old: { pageIndex: number, pageSize: number }) => { pageIndex: number, pageSize: number }) => {
    if (isEditing) {
      alert("Please save or cancel your current changes before changing pages.");
      return;
    }
    setPagination(prev => updater(prev));
  };

  const handleCreateNew = () => {
    if (isEditing) {
      alert("Please save or cancel your current changes before creating a new product.");
      return;
    }
    setSelectedItemId(null);
    setProductFormData(defaultProductData);
    setIsEditing(true);
    setIsEditingNew(true);
    setDetailViewMode('parent');
    setApiError(null);
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.delete('productId');
    router.replace(`${pathname}?${newSearchParams.toString()}`);
  };

  const handleEdit = () => {
    const currentData = productDetailQuery.data;
    if (!selectedItemId || !currentData) {
      alert("Cannot edit. No product selected or details not loaded.");
      return;
    }
    setProductFormData({
      ...defaultProductData,
      ...currentData,
      name: currentData.name ?? '',
      sku: currentData.sku ?? '',
    });
    setIsEditing(true);
    setIsEditingNew(false);
    setApiError(null);
  };

  const handleCancelEdit = () => {
    const currentData = productDetailQuery.data;
    setIsEditing(false);
    setApiError(null);
    if (isEditingNew) {
      setIsEditingNew(false);
      setSelectedItemId(null);
      setProductFormData(defaultProductData);
      const newSearchParams = new URLSearchParams(searchParams);
      if (newSearchParams.has('productId')) {
        newSearchParams.delete('productId');
        router.replace(`${pathname}?${newSearchParams.toString()}`);
      }
    } else if (selectedItemId && currentData) {
      setProductFormData({
        ...defaultProductData,
        ...currentData,
        name: currentData.name ?? '',
        sku: currentData.sku ?? '',
      });
    } else {
      setProductFormData(defaultProductData);
    }
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    // Handle number conversion for specific fields
    let processedValue: string | number | null = value;
    if (type === 'number') {
      processedValue = value === '' ? null : parseFloat(value);
      if (isNaN(processedValue as number)) {
        processedValue = null; // Handle invalid number input
      }
    }
    setProductFormData(prev => ({ ...prev, [name]: processedValue }));
  };

  const handleCheckboxChange = (field: keyof ProductFormData, checked: boolean | 'indeterminate') => {
    if (typeof checked === 'boolean') {
      setProductFormData(prev => ({ ...prev, [field]: checked }));
    }
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);

    if (!productFormData.name || !productFormData.sku) {
      setApiError("Product Name and SKU are required.");
      return;
    }

    if (!isEditingNew && selectedItemId === null) {
       setApiError("Cannot update: Product ID is missing.");
       return;
    }

    const dataToSave: ProductFormData = {
        ...productFormData,
        name: productFormData.name,
        sku: productFormData.sku,
        description: productFormData.description ?? '',
    };
    console.log("Data being sent to API:", dataToSave);

    if (isEditingNew) {
      createProductMutation.mutate(dataToSave);
    } else {
      updateProductMutation.mutate({ id: selectedItemId!, data: dataToSave });
    }
  };

  const handleSupplierChange = (supplierIdString: string) => {
    console.log(`handleSupplierChange called with value: '${supplierIdString}'`);
    let selectedSupplier: Supplier | null = null;
    const availableSuppliers = productDetailQuery.data?.suppliers;
    console.log('Available suppliers:', availableSuppliers ? availableSuppliers.map((s: Supplier) => ({ id: s.id, name: s.name })) : 'Not loaded');

    if (supplierIdString && supplierIdString !== "none" && availableSuppliers) {
      selectedSupplier = availableSuppliers.find((s: Supplier) => String(s.id) === supplierIdString) ?? null;
      console.log(`Found supplier object:`, selectedSupplier ? { id: selectedSupplier.id, name: selectedSupplier.name } : null);
    } else {
       console.log("Value is 'none' or suppliers not available. Setting supplier to null.");
       selectedSupplier = null; // Explicitly null if 'none' or unavailable
    }

    setProductFormData(prev => {
      console.log('Current productFormData.supplier:', prev.supplier ? { id: prev.supplier.id, name: prev.supplier.name } : null);
      if ((!prev.supplier && !selectedSupplier) || (prev.supplier?.id === selectedSupplier?.id)) {
             console.log("Supplier state effectively unchanged (same ID or both null), skipping update.");
             return prev;
      }
      console.log("Updating productFormData.supplier to:", selectedSupplier ? { id: selectedSupplier.id, name: selectedSupplier.name } : null);
      return {
        ...prev,
        supplier: selectedSupplier
      };
    });
  };

  // --- Render Logic ---
  const products = productsQuery.data?.results ?? [];
  const totalCount = productsQuery.data?.count ?? 0;
  const selectedProduct = productDetailQuery.data;
  const isMutating = createProductMutation.isPending || updateProductMutation.isPending;

  const { addVisitedItem } = useLastVisited();
  useEffect(() => {
    if (!isEditing && selectedProduct) {
      const currentParams = new URLSearchParams(searchParams);
      currentParams.set('productId', String(selectedProduct.id));
      const pathWithQuery = `${pathname}?${currentParams.toString()}`;

      addVisitedItem({
        type: 'product',
        id: String(selectedProduct.id),
        name: selectedProduct.name,
        path: pathWithQuery,
      });
    }
  }, [selectedProduct, isEditing, addVisitedItem, pathname, searchParams]);

  const showDetailPlaceholder = !isEditingNew && selectedItemId === null;
  const showDetailLoading = !isEditingNew && productDetailQuery.isLoading;
  const displayData = !isEditing && selectedProduct ? selectedProduct : productFormData;
  const canRenderDetails = !showDetailPlaceholder && !showDetailLoading && (displayData || isEditingNew);

  const leftPane = (
    <>
      <CardHeader>
        <CardTitle>Product List</CardTitle>
        <div className="flex items-center justify-between mt-2 space-x-2">
          <div className="relative flex-grow">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              type="search"
              placeholder="Search SKU or Name..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="pl-10 h-9 w-full"
              disabled={productsQuery.isFetching || isEditing}
            />
          </div>
          <Button
            variant="outline"
            size="icon"
            aria-label="Filter Products"
            onClick={() => alert('Filter button clicked - Implement filter logic')}
            disabled={productsQuery.isFetching || isEditing}
          >
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto">
        {productsQuery.isLoading ? (
          <p>Loading products...</p>
        ) : productsQuery.isError ? (
          <p>Error loading products: {productsQuery.error.message}</p>
        ) : products.length > 0 ? (
          <Table>
            <TableCaption>Product List - Page {pagination.pageIndex + 1}</TableCaption>
            <TableHeader>
              <TableRow>
                <TableHead>Image</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead>Legacy SKU</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Active</TableHead>
                <TableHead>Variants</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {products.map((product) => (
                <TableRow 
                  key={product.id} 
                  className={
                    selectedItemId === product.id
                      ? "bg-primary/10"
                      : undefined
                  }
                  onClick={() => handleSelectItem(product.id)}
                >
                  <TableCell>
                    {product.primary_image ? (
                      <Image 
                        src={product.primary_image.thumbnail_url || product.primary_image.image_url}
                        alt={product.name}
                        width={40}
                        height={40}
                        className="rounded object-cover"
                      />
                    ) : (
                      <></>
                    )}
                  </TableCell>
                  <TableCell>{product.sku}</TableCell>
                  <TableCell>{product.legacy_base_sku}</TableCell>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.is_active ? "Yes" : "No"}</TableCell>
                  <TableCell>{product.variants_count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <p className="text-muted-foreground text-center p-4">No products found.</p>
        )}

        {totalCount > 0 && (
          <div className="mt-4 flex justify-between items-center px-2 py-1 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePaginationChange((old) => ({ ...old, pageIndex: old.pageIndex - 1 }))}
              disabled={pagination.pageIndex === 0 || productsQuery.isFetching || isEditing}
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
              onClick={() => handlePaginationChange((old) => ({ ...old, pageIndex: old.pageIndex + 1 }))}
              disabled={pagination.pageIndex + 1 >= Math.ceil(totalCount / pagination.pageSize) || productsQuery.isFetching || isEditing}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        )}
      </CardContent>
      <div className="p-4 border-t flex-shrink-0">
        <Button className='w-full' onClick={handleCreateNew} disabled={isEditing}>
          <PlusCircle className="mr-2 h-4 w-4" />
          New Product
        </Button>
      </div>
    </>
  );

  const rightPane = (
    <>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{isEditingNew ? 'Create New Product' : 'Product Details'}</CardTitle>
        <div className="flex gap-2">
          {!isEditing && selectedItemId && (
            <Button variant="outline" size="sm" onClick={handleEdit} disabled={productDetailQuery.isLoading}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Button>
          )}
          {isEditing && (
            <>
              <Button variant="outline" size="sm" onClick={handleCancelEdit} disabled={isMutating}>
                <X className="mr-2 h-4 w-4" />
                Cancel
              </Button>
              <Button size="sm" onClick={handleSave} disabled={isMutating || !productFormData.name || !productFormData.sku}>
                {isMutating ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</>
                ) : (
                  <><Save className="mr-2 h-4 w-4" />Save</>
                )}
              </Button>
            </>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto">
        {showDetailPlaceholder && (
          <p className="text-muted-foreground flex items-center justify-center h-full">Select a product or create a new one.</p>
        )}
        {showDetailLoading && (
          <p className="text-muted-foreground flex items-center justify-center h-full">Loading details for item {selectedItemId}...</p>
        )}
        {apiError && (
          <Alert variant="destructive" className="my-4">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{apiError}</AlertDescription>
          </Alert>
        )}

        {canRenderDetails && (
          <>
            {!isEditingNew && selectedItemId && displayData ? (
              <Tabs defaultValue="parent" value={detailViewMode} onValueChange={(value) => setDetailViewMode(value as 'parent' | 'variants')} className="p-4 h-full flex flex-col">
                <TabsList className="mb-4">
                  <TabsTrigger value="parent">Parent Details</TabsTrigger>
                  <TabsTrigger value="variants" disabled={!selectedItemId || variantsQuery.isLoading}>
                    Variants {
                      selectedItemId && variantsQuery.isLoading ? ' (Loading...)' :
                      selectedItemId && variantsQuery.isError ? ' (Error)' :
                      selectedItemId && variantsQuery.data?.length ? ` (${variantsQuery.data.length})` :
                      ' (0)' // Default or if no product selected
                    }
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="parent" className="flex-grow overflow-y-auto space-y-4">
                  <ProductDetailFormContent
                    productData={productFormData}
                    isEditing={isEditing}
                    handleFormChange={handleFormChange}
                    handleCheckboxChange={handleCheckboxChange}
                    handleSupplierChange={handleSupplierChange}
                    isMutating={isMutating}
                    fetchedProduct={selectedProduct}
                    suppliers={productDetailQuery.data?.suppliers ?? []}
                    router={router}
                  />
                </TabsContent>
                <TabsContent value="variants" className="flex-grow overflow-y-auto space-y-4">
                  <ProductVariantContent
                    selectedItemId={selectedItemId}
                    variantsQuery={variantsQuery}
                  />
                </TabsContent>
              </Tabs>
            ) : (
              <div className='p-4 space-y-4 flex-grow overflow-y-auto'>
                <ProductDetailFormContent
                  productData={productFormData}
                  isEditing={isEditing}
                  handleFormChange={handleFormChange}
                  handleCheckboxChange={handleCheckboxChange}
                  handleSupplierChange={handleSupplierChange}
                  isMutating={isMutating}
                  fetchedProduct={null}
                  suppliers={[]}
                  router={router}
                />
              </div>
            )}
          </>
        )}
      </CardContent>
    </>
  );

  return (
    <TwoPaneLayout
      maximizedPaneOverride={maximizedPane}
      onMaximizeChange={setMaximizedPane}
      leftPaneContent={leftPane}
      rightPaneContent={rightPane}
    />
  );
}

interface ProductDetailFormContentProps {
  productData: ProductFormData;
  isEditing: boolean;
  handleFormChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleCheckboxChange: (field: keyof ProductFormData, checked: boolean | 'indeterminate') => void;
  handleSupplierChange: (supplierIdString: string) => void;
  isMutating: boolean;
  fetchedProduct?: Product | null;
  suppliers?: Supplier[];
  router: AppRouterInstance;
}

function ProductDetailFormContent({
  productData,
  isEditing,
  handleFormChange,
  handleCheckboxChange,
  handleSupplierChange,
  isMutating,
  fetchedProduct,
  suppliers = [],
  router
}: ProductDetailFormContentProps) {
  const selectValue = productData.supplier?.id?.toString() ?? "none";
  console.log(`Rendering ProductDetailFormContent. Select value prop is: '${selectValue}'`, "productData.supplier:", productData.supplier ? { id: productData.supplier.id, name: productData.supplier.name } : null);

  return (
    <form onSubmit={(e) => e.preventDefault()} className="space-y-6">
      {/* Display image from fetchedProduct only when not editing */}
      {!isEditing && fetchedProduct?.primary_image && (
        <div className="mb-4">
          <img
            src={fetchedProduct.primary_image}
            alt={fetchedProduct.name}
            className="max-w-xs max-h-48 object-contain rounded-md border"
          />
        </div>
      )}

      <div className="space-y-1">
        <Label htmlFor="product-name" className={isEditing ? "" : "text-muted-foreground"}>Product Name <span className="text-red-500">*</span></Label>
        {isEditing ? (
          <Input
            id="product-name"
            name="name"
            placeholder="e.g., Basic Widget"
            value={productData.name ?? ''}
            onChange={handleFormChange}
            required
            disabled={isMutating}
          />
        ) : (
          <h2 className='text-2xl font-bold text-primary'>{fetchedProduct?.name || '-'}</h2>
        )}
      </div>

      {/* Details Grid 1 */}
      <h3 className="text-lg font-semibold border-b pb-1 mb-3">Core Details</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-x-4 gap-y-4 text-sm">
        {/* SKU */}
        <div className="space-y-1">
          <Label htmlFor="product-sku" className={isEditing ? "" : "text-muted-foreground font-medium"}>SKU <span className="text-red-500">*</span></Label>
          {isEditing ? (
            <Input id="product-sku" name="sku" placeholder="e.g., WID-001" value={productData.sku ?? ''} onChange={handleFormChange} required disabled={isMutating} />
          ) : (
             <p>{fetchedProduct?.sku || '-'}</p>
          )}
        </div>

        {/* Legacy SKU */}
        <div className="space-y-1">
          <Label htmlFor="product-legacy-sku" className={isEditing ? "" : "text-muted-foreground font-medium"}>Legacy SKU</Label>
          {isEditing ? (
            <Input id="product-legacy-sku" name="legacy_base_sku" placeholder="Optional legacy SKU" value={productData.legacy_base_sku ?? ''} onChange={handleFormChange} disabled={isMutating} />
          ) : (
            <p>{fetchedProduct?.legacy_base_sku || 'N/A'}</p>
          )}
        </div>

        {/* Category */}
        <div className="space-y-1">
          <Label htmlFor="product-category" className={isEditing ? "" : "text-muted-foreground font-medium"}>Category</Label>
           {isEditing ? (
            <Input id="product-category" name="category" placeholder="e.g., Widgets" value={productData.category ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
              <p>{fetchedProduct?.category || 'N/A'}</p>
           )}
        </div>

        {/* Supplier Select Field */}
        <div className="space-y-1">
          {/* <Label htmlFor="product-supplier" className={isEditing ? "" : "text-muted-foreground font-medium"}>Supplier</Label> */}
          {isEditing ? (
            <Select
              value={selectValue}
              onValueChange={handleSupplierChange}
              disabled={isMutating}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select Supplier" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">-- None --</SelectItem>
                {suppliers.map((supplier) => (
                  <SelectItem key={supplier.id} value={supplier.id.toString()}>
                    {supplier.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            fetchedProduct?.supplier ? (
              <Button
                variant="outline"
                size="sm"
                className="p-1 h-auto justify-start"
                onClick={() => router.push(`/business/suppliers?supplierId=${fetchedProduct.supplier?.id}`)}
                title={`View details for ${fetchedProduct.supplier.name}`}
              >
                {fetchedProduct.supplier.name}
              </Button>
            ) : (
               <p>N/A</p>
            )
          )}
        </div>

        {/* Active */}
        <div className="space-y-1">
           <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Status</Label>
           {isEditing ? (
             <div className="flex items-center space-x-2 pt-1">
               <Checkbox id="product-active" checked={productData.is_active ?? false} onCheckedChange={(checked) => handleCheckboxChange('is_active', checked)} disabled={isMutating} />
               <Label htmlFor="product-active" className="text-sm font-medium">Active</Label>
             </div>
           ) : (
             <Badge variant={fetchedProduct?.is_active ? 'default' : 'secondary'}>{fetchedProduct?.is_active ? 'Active' : 'Inactive'}</Badge>
           )}
        </div>

        {/* Discontinued */}
        <div className="space-y-1">
          <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Lifecycle</Label>
          {isEditing ? (
            <div className="flex items-center space-x-2 pt-1">
              <Checkbox id="product-discontinued" checked={productData.is_discontinued ?? false} onCheckedChange={(checked) => handleCheckboxChange('is_discontinued', checked)} disabled={isMutating} />
              <Label htmlFor="product-discontinued" className="text-sm font-medium">Discontinued</Label>
            </div>
          ) : (
              <Badge variant={fetchedProduct?.is_discontinued ? 'destructive' : 'secondary'}>{fetchedProduct?.is_discontinued ? 'Discontinued' : 'Active Lifecycle'}</Badge>
          )}
        </div>

        {/* Release Date */}
        <div className="space-y-1">
           <Label htmlFor="product-release-date" className={isEditing ? "" : "text-muted-foreground font-medium"}>Release Date</Label>
           {isEditing ? (
            <Input id="product-release-date" name="release_date" type="date" value={productData.release_date ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
              <p>{fetchedProduct?.release_date ? new Date(fetchedProduct.release_date).toLocaleDateString() : 'N/A'}</p>
           )}
        </div>

         {/* Variants Count (Display Only) */}
         <div className="space-y-1">
           <Label className='font-medium text-muted-foreground'>Variants</Label>
           <p>{fetchedProduct?.variants_count ?? 0}</p>
         </div>
      </div>

      {/* Dimensions Section */}
      <h3 className="text-lg font-semibold border-b pb-1 mb-3 pt-4">Dimensions & Weight</h3>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-x-4 gap-y-4 text-sm">
         {/* Height */}
         <div className="space-y-1">
           <Label htmlFor="product-height" className={isEditing ? "" : "text-muted-foreground font-medium"}>Height (mm)</Label>
           {isEditing ? (
             <Input id="product-height" name="height_mm" type="number" placeholder="e.g., 100" value={productData.height_mm ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
             <p>{fetchedProduct?.height_mm ?? 'N/A'}</p>
           )}
         </div>
         {/* Length */}
         <div className="space-y-1">
           <Label htmlFor="product-length" className={isEditing ? "" : "text-muted-foreground font-medium"}>Length (mm)</Label>
           {isEditing ? (
             <Input id="product-length" name="length_mm" type="number" placeholder="e.g., 150" value={productData.length_mm ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
             <p>{fetchedProduct?.length_mm ?? 'N/A'}</p>
           )}
         </div>
         {/* Width */}
         <div className="space-y-1">
           <Label htmlFor="product-width" className={isEditing ? "" : "text-muted-foreground font-medium"}>Width (mm)</Label>
           {isEditing ? (
             <Input id="product-width" name="width_mm" type="number" placeholder="e.g., 50" value={productData.width_mm ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
             <p>{fetchedProduct?.width_mm ?? 'N/A'}</p>
           )}
         </div>
         {/* Weight */}
         <div className="space-y-1">
           <Label htmlFor="product-weight" className={isEditing ? "" : "text-muted-foreground font-medium"}>Weight (g)</Label> 
           {isEditing ? (
             <Input id="product-weight" name="weight" type="number" placeholder="e.g., 250" value={productData.weight ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
             <p>{fetchedProduct?.weight ?? 'N/A'}</p>
           )}
         </div>
      </div>

       {/* Flags Section */}
       <h3 className="text-lg font-semibold border-b pb-1 mb-3 pt-4">Flags</h3>
       <div className="grid grid-cols-1 md:grid-cols-3 gap-x-4 gap-y-4 text-sm">
         {/* Hanging */}
         <div className="space-y-1">
            <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Packaging</Label>
            {isEditing ? (
              <div className="flex items-center space-x-2 pt-1">
                <Checkbox id="product-hanging" checked={productData.is_hanging ?? false} onCheckedChange={(checked) => handleCheckboxChange('is_hanging', checked)} disabled={isMutating} />
                <Label htmlFor="product-hanging" className="text-sm font-medium">Hanging</Label>
              </div>
            ) : (
                <Badge variant={fetchedProduct?.is_hanging ? 'default' : 'secondary'}>{fetchedProduct?.is_hanging ? 'Hanging' : 'Not Hanging'}</Badge>
            )}
         </div>
         {/* One-Sided */}
         <div className="space-y-1">
           <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Design</Label>
            {isEditing ? (
              <div className="flex items-center space-x-2 pt-1">
                <Checkbox id="product-one-sided" checked={productData.is_one_sided ?? false} onCheckedChange={(checked) => handleCheckboxChange('is_one_sided', checked)} disabled={isMutating} />
                <Label htmlFor="product-one-sided" className="text-sm font-medium">One-Sided</Label>
              </div>
            ) : (
                 <Badge variant={fetchedProduct?.is_one_sided ? 'default' : 'secondary'}>{fetchedProduct?.is_one_sided ? 'One-Sided' : 'Multi-Sided'}</Badge>
            )}
         </div>
         {/* New */}
         <div className="space-y-1">
           <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Release Status</Label>
            {isEditing ? (
              <div className="flex items-center space-x-2 pt-1">
                <Checkbox id="product-new" checked={productData.is_new ?? false} onCheckedChange={(checked) => handleCheckboxChange('is_new', checked)} disabled={isMutating} />
                <Label htmlFor="product-new" className="text-sm font-medium">Novelty</Label>
              </div>
            ) : (
                 <Badge variant={fetchedProduct?.is_new ? 'default' : 'secondary'}>{fetchedProduct?.is_new ? 'Novelty' : 'Established'}</Badge>
            )}
         </div>
       </div>

      {/* Description */}
      <h3 className="text-lg font-semibold border-b pb-1 mb-3 pt-4">Description</h3>
      <div className="space-y-1">
        {isEditing ? (
          <Textarea id="product-description" name="description" placeholder="Detailed description..." value={productData.description ?? ''} onChange={handleFormChange} disabled={isMutating} className={"min-h-[100px]"} rows={4} />
        ) : (
            <p className="text-sm text-muted-foreground min-h-[20px]">
              {fetchedProduct?.description || 'No description provided.'}
            </p>
        )}
      </div>

      {/* Tags & Keywords */}
      {(isEditing || (Array.isArray(fetchedProduct?.tags) && fetchedProduct.tags.length > 0) || fetchedProduct?.keywords) && (
        <div className="pt-4">
          <h3 className="text-lg font-semibold border-b pb-1 mb-3">Tags & Keywords</h3>
          {isEditing ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label htmlFor="product-tags">Tags (comma-separated)</Label>
                <Input id="product-tags" name="tags" placeholder="e.g., tag1, tag2" value={Array.isArray(productData.tags) ? productData.tags.join(', ') : ''} onChange={(e) => handleFormChange({ target: { name: 'tags', value: e.target.value.split(',').map(t => t.trim()).filter(Boolean) } } as any)} disabled={isMutating} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="product-keywords">Keywords (comma-separated)</Label>
                <Input id="product-keywords" name="keywords" placeholder="e.g., keyword1, keyword2" value={productData.keywords ?? ''} onChange={handleFormChange} disabled={isMutating} />
              </div>
            </div>
          ) : (
            <div className="flex flex-wrap gap-1">
              {Array.isArray(fetchedProduct?.tags) && fetchedProduct.tags.map((tag) => (
                <Badge key={tag} variant="outline">{tag}</Badge>
              ))}
              {typeof fetchedProduct?.keywords === 'string' && fetchedProduct.keywords.split(/[,; ]+/).map((keyword) => (
                keyword && <Badge key={keyword} variant="secondary">{keyword}</Badge>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Timestamps (Display Only) */}
      {!isEditing && fetchedProduct && (
        <div className="text-xs text-muted-foreground mt-6 pt-4 border-t">
          <p>Created: {fetchedProduct.created_at ? new Date(fetchedProduct.created_at).toLocaleString() : 'N/A'}</p>
          <p>Last Updated: {fetchedProduct.updated_at ? new Date(fetchedProduct.updated_at).toLocaleString() : 'N/A'}</p>
        </div>
      )}
    </form>
  );
}

interface ProductVariantContentProps {
  selectedItemId: number | null;
  variantsQuery: UseQueryResult<Variant[], Error>;
}

function ProductVariantContent({
  selectedItemId,
  variantsQuery
}: ProductVariantContentProps) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newVariantData, setNewVariantData] = useState<{ 
    variant_code: string;
    name: string;
    is_active: boolean;
  }>({ 
    variant_code: '',
    name: '',
    is_active: true,
  });
  const [createError, setCreateError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // --- DEBUGGING LOGS ---
  console.log('ProductVariantContent Render');
  console.log('  selectedItemId:', selectedItemId);
  console.log('  variantsQuery Status:', {
    isLoading: variantsQuery.isLoading,
    isFetching: variantsQuery.isFetching,
    isSuccess: variantsQuery.isSuccess,
    isError: variantsQuery.isError,
    isFetched: variantsQuery.isFetched,
    dataUpdatedAt: variantsQuery.dataUpdatedAt,
  });
  console.log('  variantsQuery.data:', variantsQuery.data);
  // --- END DEBUGGING LOGS ---

  const createVariantMutation = useMutation<
    Variant,
    Error,
    Partial<Variant> & { parent_id: number }
  >({
    mutationFn: async (data) => {
      if (!selectedItemId) throw new Error("Parent product ID is missing");
      return productApi.createProduct({ 
          ...data,
          parent_id: selectedItemId 
      }) as Promise<Variant>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productVariants', selectedItemId] });
      setShowCreateForm(false);
      setNewVariantData({ variant_code: '', name: '', is_active: true });
      setCreateError(null);
    },
    onError: (error) => {
      console.error("Error creating variant:", error);
      setCreateError(`Failed to create variant: ${error.message}`);
    }
  });

  const handleCreateVariantSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newVariantData.variant_code || !newVariantData.name) {
      setCreateError("Variant Code and Name are required.");
      return;
    }
    if (!selectedItemId) {
      setCreateError("Cannot create variant: Parent Product ID is missing.");
      return;
    }
    setCreateError(null);
    createVariantMutation.mutate({ ...newVariantData, parent_id: selectedItemId });
  };

  const handleVariantFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewVariantData(prev => ({ ...prev, [name]: value }));
  };

  // Use the array directly from the query data
  const variants = variantsQuery.data ?? [];
  // Get the count from the array length
  const totalVariants = variants.length;

  if (variantsQuery.isLoading) {
    return <p>Loading variants...</p>;
  }

  if (variantsQuery.isError) {
    return <p className="text-red-500">Error loading variants: {variantsQuery.error.message}</p>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        {/* Display count derived from the array length */}
        <h3 className="text-lg font-semibold">Product Variants ({totalVariants})</h3>
        <Button size="sm" onClick={() => setShowCreateForm(!showCreateForm)} variant="outline">
          <PlusCircle className="mr-2 h-4 w-4" />
          {showCreateForm ? 'Cancel' : 'New Variant'}
        </Button>
      </div>

      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Variant</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateVariantSubmit} className="space-y-4">
              <div className="space-y-1">
                <Label htmlFor="variant_code">Variant Code <span className="text-red-500">*</span></Label>
                <Input 
                  id="variant_code"
                  name="variant_code"
                  value={newVariantData.variant_code}
                  onChange={handleVariantFormChange}
                  required
                  disabled={createVariantMutation.isPending}
                  placeholder="e.g., RED, XL"
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="variant_name">Variant Name <span className="text-red-500">*</span></Label>
                <Input 
                  id="variant_name"
                  name="name" 
                  value={newVariantData.name}
                  onChange={handleVariantFormChange}
                  required
                  disabled={createVariantMutation.isPending}
                  placeholder="e.g., Product Name - Red"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="variant_is_active"
                  checked={newVariantData.is_active}
                  onCheckedChange={(checked) => setNewVariantData(prev => ({ ...prev, is_active: checked === true }))}
                  disabled={createVariantMutation.isPending}
                />
                <Label htmlFor="variant_is_active">Active</Label>
              </div>
              {createError && <p className="text-sm text-red-500">{createError}</p>}
              <DialogFooter>
                <Button 
                  type="submit" 
                  size="sm"
                  disabled={createVariantMutation.isPending}
                >
                  {createVariantMutation.isPending ? 'Creating...' : 'Create Variant'}
                </Button>
              </DialogFooter>
            </form>
          </CardContent>
        </Card>
      )}

      {variants.length > 0 ? (
        <Table>
          <TableCaption>List of variants for product ID {selectedItemId}</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Image</TableHead>
              <TableHead>SKU</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Variant Code</TableHead>
              <TableHead>Active</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {variants.map((variant: Variant) => (
              <TableRow key={variant.id}>
                <TableCell>
                  {variant.images && variant.images.length > 0 ? (
                    <Image 
                      src={variant.images[0].thumbnail_url || variant.images[0].image_url}
                      alt={variant.name || variant.sku}
                      width={40}
                      height={40}
                      className="rounded object-cover"
                    />
                  ) : (
                    <></>
                  )}
                </TableCell>
                <TableCell>{variant.sku}</TableCell>
                <TableCell>{variant.name}</TableCell>
                <TableCell>{variant.variant_code}</TableCell>
                <TableCell>{variant.is_active ? 'Yes' : 'No'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <p className="text-muted-foreground text-center p-4">No variants found for this product.</p>
      )}
    </div>
  );
}
