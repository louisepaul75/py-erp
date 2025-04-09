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

// Define the expected input type for creating/updating a product
// Make most fields optional for update
type ProductFormData = Partial<Product> & {
  name: string; // Name is likely always required
  sku: string;  // SKU is likely always required
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
  // Add other fields as needed
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
    const { name, value } = e.target;
    setProductFormData(prev => ({ ...prev, [name]: value }));
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
    return isEditing ? productData[field] : fetchedProduct ? fetchedProduct[field] : undefined;
  };

  const nameValue = getValue('name') ?? '';
  const skuValue = getValue('sku') ?? '';
  const categoryValue = getValue('category') ?? '';
  const descriptionValue = getValue('description') ?? '';
  const isActiveValue = getValue('is_active') ?? true;
  const isDiscontinuedValue = getValue('is_discontinued') ?? false;
  const releaseDateValue = getValue('release_date');
  const tagsValue = getValue('tags');
  const keywordsValue = getValue('keywords') ?? '';

  return (
    <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
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

      <div className="grid grid-cols-2 gap-x-4 gap-y-4 text-sm">
        <div className="space-y-1">
          <Label htmlFor="product-sku" className={isEditing ? "" : "text-muted-foreground"}>SKU <span className="text-red-500">*</span></Label>
          {isEditing ? (
            <Input
              id="product-sku"
              name="sku"
              placeholder="e.g., WID-001"
              value={skuValue}
              onChange={handleFormChange}
              required
              disabled={isMutating}
            />
          ) : (
             <p>{skuValue || '-'}</p>
          )}
        </div>

        <div className="space-y-1">
          <Label htmlFor="product-category" className={isEditing ? "" : "text-muted-foreground"}>Category</Label>
           {isEditing ? (
            <Input
              id="product-category"
              name="category"
              placeholder="e.g., Widgets"
              value={categoryValue}
              onChange={handleFormChange}
              disabled={isMutating}
            />
           ) : (
              <p>{categoryValue || 'N/A'}</p>
           )}
        </div>

         <div className="space-y-1">
           <Label htmlFor="product-active" className={isEditing ? "" : "text-muted-foreground"}>Active</Label>
           {isEditing ? (
             <div className="flex items-center space-x-2 pt-1">
               <Checkbox
                 id="product-active"
                 checked={isActiveValue}
                 onCheckedChange={(checked) => handleCheckboxChange('is_active', checked)}
                 disabled={isMutating}
                 aria-labelledby="product-active-label"
               />
               <Label htmlFor="product-active" id="product-active-label" className="text-sm font-medium">
               </Label>
             </div>
           ) : (
             <Badge variant={isActiveValue ? 'default' : 'secondary'}>{isActiveValue ? 'Yes' : 'No'}</Badge>
           )}
         </div>

        <div>
           <span className='font-medium text-muted-foreground'>Variants:</span> {fetchedProduct?.variants_count ?? 0}
        </div>

         <div className="space-y-1">
           <Label htmlFor="product-release-date" className={isEditing ? "" : "text-muted-foreground"}>Release Date</Label>
           {isEditing ? (
            <Input
              id="product-release-date"
              name="release_date"
              type="date"
              value={releaseDateValue ? String(releaseDateValue).split('T')[0] : ''}
              onChange={handleFormChange}
              disabled={isMutating}
            />
           ) : (
              <p>{releaseDateValue ? new Date(releaseDateValue).toLocaleDateString() : 'N/A'}</p>
           )}
         </div>

        <div className="space-y-1">
          <Label htmlFor="product-discontinued" className={isEditing ? "" : "text-muted-foreground"}>Discontinued</Label>
          {isEditing ? (
            <div className="flex items-center space-x-2 pt-1">
              <Checkbox
                id="product-discontinued"
                checked={isDiscontinuedValue}
                onCheckedChange={(checked) => handleCheckboxChange('is_discontinued', checked)}
                disabled={isMutating}
                aria-labelledby="product-discontinued-label"
              />
               <Label htmlFor="product-discontinued" id="product-discontinued-label" className="text-sm font-medium">
               </Label>
            </div>
          ) : (
              <Badge variant={isDiscontinuedValue ? 'destructive' : 'secondary'}>{isDiscontinuedValue ? 'Yes' : 'No'}</Badge>
          )}
        </div>
      </div>

      <Separator className="my-4" />

      <div className="space-y-1">
        <Label htmlFor="product-description" className={isEditing ? "" : "text-muted-foreground"}>Description</Label>
        {isEditing ? (
          <Textarea
            id="product-description"
            name="description"
            placeholder="Detailed description of the product..."
            value={descriptionValue}
            onChange={handleFormChange}
            disabled={isMutating}
            className={"min-h-[100px]"}
            rows={4}
          />
        ) : (
            <p className="text-sm text-muted-foreground min-h-[20px]">
              {descriptionValue || 'No description provided.'}
            </p>
        )}
      </div>

      {(isEditing || (Array.isArray(tagsValue) && tagsValue.length > 0) || keywordsValue) && (
        <div>
          <h3 className="text-lg font-semibold mb-2">Tags & Keywords</h3>
          {isEditing ? (
            <div className="space-y-2">
              <div className="space-y-1">
                <Label htmlFor="product-tags">Tags (comma-separated)</Label>
                <Input
                  id="product-tags"
                  name="tags"
                  placeholder="e.g., tag1, tag2"
                  value={Array.isArray(tagsValue) ? tagsValue.join(', ') : ''}
                  onChange={(e) => setProductFormData(prev => ({...prev, tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)}))}
                  disabled={isMutating}
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="product-keywords">Keywords (comma-separated)</Label>
                <Input
                  id="product-keywords"
                  name="keywords"
                  placeholder="e.g., keyword1, keyword2"
                  value={keywordsValue}
                  onChange={handleFormChange}
                  disabled={isMutating}
                />
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

      {!isEditing && fetchedProduct && (
        <div className="text-xs text-muted-foreground mt-4">
          <p>Created: {new Date(fetchedProduct.created_at).toLocaleString()}</p>
          <p>Last Updated: {new Date(fetchedProduct.updated_at).toLocaleString()}</p>
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
  return (
    <>
      <h3 className="text-lg font-semibold mb-2">Product Variants</h3>
      {variantsQuery.isLoading && <p>Loading variants...</p>}
      {variantsQuery.isError && <p className="text-destructive">Error loading variants: {variantsQuery.error.message}</p>}
      {variantsQuery.isSuccess && variantsQuery.data && (
        <>
         {/* TODO: Implement actual Variant Table/List Display based on variantsQuery.data.results */} 
          <p>Variants loaded: {variantsQuery.data.results?.length ?? 0}</p>
          {variantsQuery.data.results?.length === 0 && (
             <p className="text-muted-foreground italic mt-2">This product has no variants.</p>
          )}
          {/* Placeholder for table */}
          {/* <VariantTable variants={variantsQuery.data.results} parentId={selectedItemId} /> */}
        </>
      )}

      <Button size="sm" disabled className="mt-4"> {/* TODO: Implement create variant logic */}
        <PlusCircle className="mr-2 h-4 w-4" />
        Create New Variant
      </Button>
    </>
  );
}
