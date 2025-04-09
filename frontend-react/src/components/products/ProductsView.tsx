"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient, useMutation, QueryClient, UseQueryResult } from '@tanstack/react-query';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Search, PlusCircle, ChevronLeft, ChevronRight, Loader2, Edit, Save, X } from 'lucide-react';
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
  legacy_base_sku: null,
};

export function ProductsView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const queryClient: QueryClient = useQueryClient();

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
      return debouncedSearchTerm
        ? productApi.getProductsDirectSearch({ ...params, q: debouncedSearchTerm }, signal)
        : productApi.getProducts(params, signal);
    },
    placeholderData: (previousData) => previousData,
    staleTime: 5 * 60 * 1000,
    refetchOnMount: true,
  });

  // Query for the details of the selected product
  const productDetailQuery = useQuery<Product, Error>({
    queryKey: ['product', selectedItemId],
    queryFn: ({ signal }) => productApi.getProduct(selectedItemId!, signal),
    enabled: selectedItemId !== null && !isEditingNew,
    staleTime: 15 * 60 * 1000,
    onSuccess: (data) => {
      if (!isEditing && data) {
        setProductFormData({
          ...defaultProductData,
          ...data,
          name: data.name ?? '',
          sku: data.sku ?? '',
        });
        setApiError(null);
      }
    },
    onError: (error) => {
      setApiError(`Error loading details: ${error.message}`);
    }
  });

  // Query for the variants of the selected product
  const variantsQuery: UseQueryResult<ApiResponse<Product>, Error> = useQuery<ApiResponse<Product>, Error>({
    queryKey: ['productVariants', selectedItemId],
    queryFn: async ({ signal }) => {
      if (typeof productApi.getProductVariants !== 'function') {
         console.warn("productApi.getProductVariants is not implemented. Returning empty results.");
         return { count: 0, next: null, previous: null, results: [] };
      }
      return productApi.getProductVariants(selectedItemId!, signal);
    },
    enabled: !!selectedItemId,
    staleTime: 5 * 60 * 1000,
  });

  // --- Mutations ---

  const createProductMutation = useMutation<Product, Error, ProductFormData>({
    mutationFn: (data) => productApi.createProduct(data),
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
      alert("Product created successfully!");
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
    mutationFn: ({ id, data }) => productApi.updateProduct(String(id), data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.setQueryData(['product', variables.id], data);
      if (selectedItemId === variables.id && data) {
        setProductFormData({
          ...defaultProductData,
          ...data,
          name: data.name ?? '',
          sku: data.sku ?? '',
        });
      }
      setIsEditing(false);
      setApiError(null);
      alert("Product updated successfully!");
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
    };

    if (isEditingNew) {
      createProductMutation.mutate(dataToSave);
    } else {
      updateProductMutation.mutate({ id: selectedItemId!, data: dataToSave });
    }
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

  return (
    <div className="flex flex-col md:flex-row gap-4 h-full">
      {/* Left Pane: Product List / Filters */}
      <Card className="w-full md:w-1/3 flex flex-col">
        <CardHeader>
          <CardTitle>Product List</CardTitle>
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
                    <TableCell>{product.variants_count ?? 0}</TableCell>
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
      </Card>

      {/* Right Pane: Product Details / Edit Form */}
      <Card className="w-full md:w-2/3 flex flex-col">
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
                    <TabsTrigger value="variants">Variants ({selectedProduct?.variants_count ?? 0})</TabsTrigger>
                  </TabsList>
                  <TabsContent value="parent" className="flex-grow overflow-y-auto space-y-4">
                    <ProductDetailFormContent
                      productData={productFormData}
                      isEditing={isEditing}
                      handleFormChange={handleFormChange}
                      handleCheckboxChange={handleCheckboxChange}
                      isMutating={isMutating}
                      fetchedProduct={selectedProduct}
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
                    isMutating={isMutating}
                    fetchedProduct={null}
                  />
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

interface ProductDetailFormContentProps {
  productData: ProductFormData;
  isEditing: boolean;
  handleFormChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleCheckboxChange: (field: keyof ProductFormData, checked: boolean | 'indeterminate') => void;
  isMutating: boolean;
  fetchedProduct?: Product | null;
}

function ProductDetailFormContent({
  productData,
  isEditing,
  handleFormChange,
  handleCheckboxChange,
  isMutating,
  fetchedProduct
}: ProductDetailFormContentProps) {
  const displayProduct = !isEditing && fetchedProduct ? fetchedProduct : productData;

  const getValue = (field: keyof ProductFormData) => {
    // Prioritize form data if editing, otherwise use fetched data
    return isEditing
      ? productData[field]
      : fetchedProduct
      ? fetchedProduct[field]
      : undefined;
  };

  // Get values for all fields, including new ones
  const nameValue = getValue('name') ?? '';
  const skuValue = getValue('sku') ?? '';
  const categoryValue = getValue('category') ?? '';
  const descriptionValue = getValue('description') ?? '';
  const isActiveValue = getValue('is_active') ?? true;
  const isDiscontinuedValue = getValue('is_discontinued') ?? false;
  const releaseDateValue = getValue('release_date');
  const tagsValue = getValue('tags') ?? []; // Default to empty array
  const keywordsValue = getValue('keywords') ?? '';
  const legacySkuValue = getValue('legacy_base_sku') ?? ''; // Use empty string for null display

  const heightValue = getValue('height_mm');
  const lengthValue = getValue('length_mm');
  const widthValue = getValue('width_mm');
  const weightValue = getValue('weight');

  const isHangingValue = getValue('is_hanging') ?? false;
  const isOneSidedValue = getValue('is_one_sided') ?? false;
  const isNewValue = getValue('is_new') ?? false;

  return (
    <form onSubmit={(e) => e.preventDefault()} className="space-y-6"> {/* Increased spacing */}
      {fetchedProduct?.primary_image && (
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
            value={nameValue}
            onChange={handleFormChange}
            required
            disabled={isMutating}
          />
        ) : (
          <h2 className='text-2xl font-bold text-primary'>{nameValue || '-'}</h2>
        )}
      </div>

      {/* Details Grid 1 (SKU, Category, Active, Variants, Release, Discontinued, Legacy SKU) */}
      <h3 className="text-lg font-semibold border-b pb-1 mb-3">Core Details</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-x-4 gap-y-4 text-sm"> {/* Changed to 3 columns */}
        {/* SKU */}
        <div className="space-y-1">
          <Label htmlFor="product-sku" className={isEditing ? "" : "text-muted-foreground font-medium"}>SKU <span className="text-red-500">*</span></Label>
          {isEditing ? (
            <Input id="product-sku" name="sku" placeholder="e.g., WID-001" value={skuValue} onChange={handleFormChange} required disabled={isMutating} />
          ) : (
             <p>{skuValue || '-'}</p>
          )}
        </div>

        {/* Legacy SKU */}
        <div className="space-y-1">
          <Label htmlFor="product-legacy-sku" className={isEditing ? "" : "text-muted-foreground font-medium"}>Legacy SKU</Label>
          {isEditing ? (
            <Input id="product-legacy-sku" name="legacy_base_sku" placeholder="Optional legacy SKU" value={legacySkuValue} onChange={handleFormChange} disabled={isMutating} />
          ) : (
            <p>{legacySkuValue || 'N/A'}</p>
          )}
        </div>

        {/* Category */}
        <div className="space-y-1">
          <Label htmlFor="product-category" className={isEditing ? "" : "text-muted-foreground font-medium"}>Category</Label>
           {isEditing ? (
            <Input id="product-category" name="category" placeholder="e.g., Widgets" value={categoryValue} onChange={handleFormChange} disabled={isMutating} />
           ) : (
              <p>{categoryValue || 'N/A'}</p>
           )}
        </div>

        {/* Active */}
        <div className="space-y-1">
           <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Status</Label>
           {isEditing ? (
             <div className="flex items-center space-x-2 pt-1">
               <Checkbox id="product-active" checked={isActiveValue} onCheckedChange={(checked) => handleCheckboxChange('is_active', checked)} disabled={isMutating} />
               <Label htmlFor="product-active" className="text-sm font-medium">Active</Label>
             </div>
           ) : (
             <Badge variant={isActiveValue ? 'default' : 'secondary'}>{isActiveValue ? 'Active' : 'Inactive'}</Badge>
           )}
        </div>

        {/* Discontinued */}
        <div className="space-y-1">
          <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Lifecycle</Label>
          {isEditing ? (
            <div className="flex items-center space-x-2 pt-1">
              <Checkbox id="product-discontinued" checked={isDiscontinuedValue} onCheckedChange={(checked) => handleCheckboxChange('is_discontinued', checked)} disabled={isMutating} />
              <Label htmlFor="product-discontinued" className="text-sm font-medium">Discontinued</Label>
            </div>
          ) : (
              <Badge variant={isDiscontinuedValue ? 'destructive' : 'secondary'}>{isDiscontinuedValue ? 'Discontinued' : 'Active Lifecycle'}</Badge>
          )}
        </div>

        {/* Release Date */}
        <div className="space-y-1">
           <Label htmlFor="product-release-date" className={isEditing ? "" : "text-muted-foreground font-medium"}>Release Date</Label>
           {isEditing ? (
            <Input id="product-release-date" name="release_date" type="date" value={releaseDateValue ? String(releaseDateValue).split('T')[0] : ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
              <p>{releaseDateValue ? new Date(releaseDateValue).toLocaleDateString() : 'N/A'}</p>
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-x-4 gap-y-4 text-sm"> {/* Changed to 4 columns */}
         {/* Height */}
         <div className="space-y-1">
           <Label htmlFor="product-height" className={isEditing ? "" : "text-muted-foreground font-medium"}>Height (mm)</Label>
           {isEditing ? (
             <Input id="product-height" name="height_mm" type="number" placeholder="e.g., 100" value={heightValue ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
             <p>{heightValue ?? 'N/A'}</p>
           )}
         </div>
         {/* Length */}
         <div className="space-y-1">
           <Label htmlFor="product-length" className={isEditing ? "" : "text-muted-foreground font-medium"}>Length (mm)</Label>
           {isEditing ? (
             <Input id="product-length" name="length_mm" type="number" placeholder="e.g., 150" value={lengthValue ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
             <p>{lengthValue ?? 'N/A'}</p>
           )}
         </div>
         {/* Width */}
         <div className="space-y-1">
           <Label htmlFor="product-width" className={isEditing ? "" : "text-muted-foreground font-medium"}>Width (mm)</Label>
           {isEditing ? (
             <Input id="product-width" name="width_mm" type="number" placeholder="e.g., 50" value={widthValue ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
             <p>{widthValue ?? 'N/A'}</p>
           )}
         </div>
         {/* Weight */}
         <div className="space-y-1">
           <Label htmlFor="product-weight" className={isEditing ? "" : "text-muted-foreground font-medium"}>Weight (g)</Label> {/* Assuming grams */} 
           {isEditing ? (
             <Input id="product-weight" name="weight" type="number" placeholder="e.g., 250" value={weightValue ?? ''} onChange={handleFormChange} disabled={isMutating} />
           ) : (
             <p>{weightValue ?? 'N/A'}</p>
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
                <Checkbox id="product-hanging" checked={isHangingValue} onCheckedChange={(checked) => handleCheckboxChange('is_hanging', checked)} disabled={isMutating} />
                <Label htmlFor="product-hanging" className="text-sm font-medium">Hanging</Label>
              </div>
            ) : (
                <Badge variant={isHangingValue ? 'info' : 'secondary'}>{isHangingValue ? 'Hanging' : 'Not Hanging'}</Badge> // Added custom variant style potential
            )}
         </div>
         {/* One-Sided */}
         <div className="space-y-1">
           <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Design</Label>
            {isEditing ? (
              <div className="flex items-center space-x-2 pt-1">
                <Checkbox id="product-one-sided" checked={isOneSidedValue} onCheckedChange={(checked) => handleCheckboxChange('is_one_sided', checked)} disabled={isMutating} />
                <Label htmlFor="product-one-sided" className="text-sm font-medium">One-Sided</Label>
              </div>
            ) : (
                 <Badge variant={isOneSidedValue ? 'info' : 'secondary'}>{isOneSidedValue ? 'One-Sided' : 'Multi-Sided'}</Badge>
            )}
         </div>
         {/* New */}
         <div className="space-y-1">
           <Label className={isEditing ? "" : "text-muted-foreground font-medium"}>Release Status</Label>
            {isEditing ? (
              <div className="flex items-center space-x-2 pt-1">
                <Checkbox id="product-new" checked={isNewValue} onCheckedChange={(checked) => handleCheckboxChange('is_new', checked)} disabled={isMutating} />
                <Label htmlFor="product-new" className="text-sm font-medium">Novelty</Label>
              </div>
            ) : (
                 <Badge variant={isNewValue ? 'info' : 'secondary'}>{isNewValue ? 'Novelty' : 'Established'}</Badge>
            )}
         </div>
       </div>

      {/* Description */}
      <h3 className="text-lg font-semibold border-b pb-1 mb-3 pt-4">Description</h3>
      <div className="space-y-1">
        {isEditing ? (
          <Textarea id="product-description" name="description" placeholder="Detailed description..." value={descriptionValue} onChange={handleFormChange} disabled={isMutating} className={"min-h-[100px]"} rows={4} />
        ) : (
            <p className="text-sm text-muted-foreground min-h-[20px]">
              {descriptionValue || 'No description provided.'}
            </p>
        )}
      </div>

      {/* Tags & Keywords */}
      {(isEditing || (Array.isArray(tagsValue) && tagsValue.length > 0) || keywordsValue) && (
        <div className="pt-4"> {/* Added padding top */} 
          <h3 className="text-lg font-semibold border-b pb-1 mb-3">Tags & Keywords</h3>
          {isEditing ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label htmlFor="product-tags">Tags (comma-separated)</Label>
                <Input id="product-tags" name="tags" placeholder="e.g., tag1, tag2" value={Array.isArray(tagsValue) ? tagsValue.join(', ') : ''} onChange={(e) => setProductFormData(prev => ({...prev, tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)}))} disabled={isMutating} />
              </div>
              <div className="space-y-1">
                <Label htmlFor="product-keywords">Keywords (comma-separated)</Label>
                <Input id="product-keywords" name="keywords" placeholder="e.g., keyword1, keyword2" value={keywordsValue} onChange={handleFormChange} disabled={isMutating} />
              </div>
            </div>
          ) : (
            <div className="flex flex-wrap gap-1">
              {Array.isArray(tagsValue) && tagsValue.map((tag) => (
                <Badge key={tag} variant="outline">{tag}</Badge>
              ))}
              {keywordsValue?.split(/[,; ]+/).map((keyword) => (
                keyword && <Badge key={keyword} variant="secondary">{keyword}</Badge>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Timestamps (Display Only) */}
      {!isEditing && fetchedProduct && (
        <div className="text-xs text-muted-foreground mt-6 pt-4 border-t"> {/* Added spacing and border */}
          <p>Created: {fetchedProduct.created_at ? new Date(fetchedProduct.created_at).toLocaleString() : 'N/A'}</p>
          <p>Last Updated: {fetchedProduct.updated_at ? new Date(fetchedProduct.updated_at).toLocaleString() : 'N/A'}</p>
        </div>
      )}
    </form>
  );
}

interface ProductVariantContentProps {
  selectedItemId: number | null;
  variantsQuery: UseQueryResult<ApiResponse<Product>, Error>;
}

function ProductVariantContent({
  selectedItemId,
  variantsQuery
}: ProductVariantContentProps) {
  const [isCreateVariantDialogOpen, setIsCreateVariantDialogOpen] = useState(false);
  const [newVariantData, setNewVariantData] = useState({ name: '', sku: '' }); // Basic form state
  const queryClient = useQueryClient(); // Get query client

  // TODO: Implement createVariantMutation
  // Example structure:
  // const createVariantMutation = useMutation<Product, Error, { parentId: number; data: { name: string; sku: string; is_active?: boolean } }>({
  //   mutationFn: ({ parentId, data }) => productApi.createProduct({ ...data, parent_id: parentId, is_active: data.is_active ?? true }), // Assuming createProduct handles variants via parent_id
  //   onSuccess: () => {
  //     queryClient.invalidateQueries({ queryKey: ['productVariants', selectedItemId] });
  //     queryClient.invalidateQueries({ queryKey: ['product', selectedItemId] }); // Also invalidate parent product to update variant count
  //     setIsCreateVariantDialogOpen(false);
  //     setNewVariantData({ name: '', sku: '' });
  //     alert("Variant created successfully!");
  //   },
  //   onError: (error) => {
  //     // TODO: Show error in dialog
  //     console.error("Error creating variant:", error);
  //     alert(`Error creating variant: ${error.message}`);
  //   },
  // });

  const handleCreateVariantSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItemId) {
      alert("Cannot create variant: Parent product ID is missing.");
      return;
    }
    if (!newVariantData.name || !newVariantData.sku) {
      alert("Variant Name and SKU are required.");
      return;
    }
    console.log("Submitting variant: ", { parentId: selectedItemId, data: newVariantData });
    // createVariantMutation.mutate({ parentId: selectedItemId, data: newVariantData });
    alert("Create variant mutation not yet implemented."); // Placeholder
  };

  const handleVariantFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewVariantData(prev => ({ ...prev, [name]: value }));
  };

  const variants = variantsQuery.data?.results ?? [];
  const isLoading = variantsQuery.isLoading;
  const isError = variantsQuery.isError;
  const error = variantsQuery.error;

  return (
    <div className="space-y-4"> {/* Added spacing */} 
      <div className="flex justify-between items-center"> {/* Header for title and button */} 
        <h3 className="text-lg font-semibold">Product Variants</h3>
        {/* Wrap button in DialogTrigger */} 
        <Dialog open={isCreateVariantDialogOpen} onOpenChange={setIsCreateVariantDialogOpen}>
          <DialogTrigger asChild>
             {/* Enable button if parent is selected */} 
            <Button size="sm" disabled={!selectedItemId /* || createVariantMutation.isPending */} >
              <PlusCircle className="mr-2 h-4 w-4" />
              Create New Variant
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Variant</DialogTitle>
              <DialogDescription>
                Enter the details for the new product variant.
                {/* TODO: Display creation errors here */}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreateVariantSubmit} className="space-y-4 py-4">
               <div className="space-y-1">
                 <Label htmlFor="variant-name">Variant Name <span className="text-red-500">*</span></Label>
                 <Input
                   id="variant-name"
                   name="name"
                   placeholder="e.g., Basic Widget - Red"
                   value={newVariantData.name}
                   onChange={handleVariantFormChange}
                   required
                   // disabled={createVariantMutation.isPending}
                 />
               </div>
               <div className="space-y-1">
                 <Label htmlFor="variant-sku">Variant SKU <span className="text-red-500">*</span></Label>
                 <Input
                   id="variant-sku"
                   name="sku"
                   placeholder="e.g., WID-001-RED"
                   value={newVariantData.sku}
                   onChange={handleVariantFormChange}
                   required
                   // disabled={createVariantMutation.isPending}
                 />
               </div>
              {/* TODO: Add more fields if necessary (e.g., attributes, price) */}
              <DialogFooter>
                 {/* Use DialogClose for cancel */} 
                <DialogClose asChild>
                   <Button type="button" variant="outline" /* disabled={createVariantMutation.isPending} */ >Cancel</Button>
                </DialogClose>
                <Button type="submit" /* disabled={createVariantMutation.isPending || !newVariantData.name || !newVariantData.sku} */ >
                   {/* {createVariantMutation.isPending ? "Creating..." : "Create Variant"} */}
                   Create Variant (Not Impl.)
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading && <p>Loading variants...</p>}
      {isError && <p className="text-destructive">Error loading variants: {error?.message}</p>}
      {/* Only render table/message when not loading and no error */}
      {!isLoading && !isError && (
        <> 
          {variants.length === 0 ? (
             <p className="text-muted-foreground italic mt-2">This product has no variants.</p>
           ) : (
             <Table>
               <TableHeader>
                 <TableRow>
                   <TableHead>SKU</TableHead>
                   <TableHead>Name</TableHead>
                   <TableHead>Active</TableHead>
                   {/* TODO: Add more columns as needed (e.g., attributes) */}
                   <TableHead>Actions</TableHead> {/* Placeholder for actions */}
                 </TableRow>
               </TableHeader>
               <TableBody>
                 {variants.map((variant) => (
                   <TableRow key={variant.id} /* onClick={() => handleSelectVariant(variant.id)} */ className="cursor-pointer hover:bg-muted/50">
                     <TableCell>{variant.sku}</TableCell>
                     <TableCell>{variant.name}</TableCell>
                     <TableCell>
                       <Badge variant={variant.is_active ? 'default' : 'secondary'}>
                         {variant.is_active ? 'Yes' : 'No'}
                       </Badge>
                     </TableCell>
                     <TableCell>
                       {/* TODO: Add Edit/Delete buttons or link to variant detail page */}
                       <Button variant="ghost" size="sm" disabled>...</Button>
                     </TableCell>
                   </TableRow>
                 ))}
               </TableBody>
             </Table>
           )}
        </>
      )}
    </div>
  );
}
