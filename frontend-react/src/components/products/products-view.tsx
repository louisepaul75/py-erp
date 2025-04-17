// ProductsView.tsx
"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  useQuery,
  useQueryClient,
  useMutation,
  QueryClient,
} from "@tanstack/react-query";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import {
  TwoPaneLayout,
  type MaximizedPaneState,
} from "@/components/ui/TwoPaneLayout";
import { productApi } from "@/lib/products/api";
import {
  Product,
  ApiResponse,
  Supplier,
  Variant,
} from "@/components/types/product";
import {
  ProductFormData,
  defaultProductData,
} from "@/components/products/types";
import { useToast } from "@/hooks/use-toast";
import { useLastVisited } from "@/context/LastVisitedContext";
import { ProductListPane } from "@/components/products/product-list-panel";
import { ProductDetailPane } from "@/components/products/product-detail-pane";
import { useProductsTable } from "@/hooks/useProductsTable";

export function ProductsView() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const queryClient: QueryClient = useQueryClient();
  const { toast } = useToast();
  const { addVisitedItem } = useLastVisited();

  const initialProductIdParam = searchParams.get("productId");
  const initialProductId = initialProductIdParam
    ? parseInt(initialProductIdParam, 10)
    : null;
  const validInitialProductId = Number.isNaN(initialProductId)
    ? null
    : initialProductId;

  const [selectedItemId, setSelectedItemId] = useState<number | null>(
    validInitialProductId
  );
  const [isEditingNew, setIsEditingNew] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [maximizedPane, setMaximizedPane] =
    useState<MaximizedPaneState>("left");
  const [filterActive, setFilterActive] = useState(true);

  // Pagination state
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 15 });
  const [searchQuery, setSearchQuery] = useState("");

  // Query for the list of products
  const productsQuery = useQuery<ApiResponse<Product>, Error>({
    queryKey: [
      "products",
      pagination.pageIndex,
      pagination.pageSize,
      searchQuery,
      filterActive,
    ],
    queryFn: async ({ signal }) => {
      const params: Record<string, any> = {
        page: pagination.pageIndex + 1,
        page_size: pagination.pageSize,
        is_active: filterActive,
      };
      
      // Add search parameter if provided
      if (searchQuery) {
        params.q = searchQuery;
      }
      
      console.log("API request params:", params);
      
      // Use direct search if searching, otherwise use regular endpoint
      if (searchQuery) {
        return productApi.getProductsDirectSearch(params, signal);
      }
      return productApi.getProducts(params, signal);
    },
    placeholderData: (previousData) => previousData,
    staleTime: 5 * 60 * 1000,
    refetchOnMount: true,
  });

  // Query for the details of the selected product
  const productDetailQuery = useQuery<
    Product & { suppliers?: Supplier[] },
    Error
  >({
    queryKey: ["product", selectedItemId],
    queryFn: ({ signal }) =>
      productApi.getProduct(selectedItemId!, signal) as Promise<
        Product & { suppliers?: Supplier[] }
      >,
    enabled: selectedItemId !== null && !isEditingNew,
    staleTime: 15 * 60 * 1000,
  });

  // Query for the variants of the selected product
  const variantsQuery = useQuery<Variant[], Error>({
    queryKey: ["productVariants", selectedItemId],
    queryFn: async ({ signal }) => {
      if (!selectedItemId) return [];
      const variants = await productApi.getProductVariants(
        selectedItemId,
        signal
      );
      // Ensure the returned data conforms to our Variant type
      return variants.map((variant) => ({
        id: variant.id,
        name: variant.name || "",
        sku: variant.sku || "",
        variant_code: variant.variant_code,
        is_active: variant.is_active,
        images: variant.images,
      }));
    },
    enabled: !!selectedItemId,
    staleTime: 5 * 60 * 1000,
  });

  // Handle search query changes
  const handleSearchChange = useCallback((term: string) => {
    setSearchQuery(term);
    // Reset to first page when search changes
    setPagination(prev => ({ ...prev, pageIndex: 0 }));
  }, []);

  // Handle pagination changes
  const handlePaginationChange = useCallback((pageIndex: number) => {
    setPagination(prev => ({ ...prev, pageIndex }));
  }, []);

  // Use the products table hook
  const {
    products,
    totalCount,
    isLoading,
    isError,
    error,
    sortConfig,
    requestSort,
    searchTerm,
    setSearchTerm,
    currentPage,
    totalPages,
    goToPage,
    goToNextPage,
    goToPreviousPage,
    isFetching,
  } = useProductsTable({
    productsQuery,
    onPaginationChange: handlePaginationChange,
    onSearchChange: handleSearchChange,
    pagination,
  });

  // Mutations
  const createProductMutation = useMutation<Product, Error, ProductFormData>({
    mutationFn: (data) =>
      productApi.createProduct({
        ...data,
        description: data.description ?? "",
      } as Omit<Product, "id"> & { parent_id?: string | number | undefined }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.setQueryData(["product", data.id], data);
      setSelectedItemId(data.id);
      setIsEditingNew(false);
      setIsEditing(false);
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set("productId", String(data.id));
      router.replace(`${pathname}?${newSearchParams.toString()}`);
      toast({ title: "Success", description: "Product created successfully." });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: `Error creating product: ${error.message}`,
        variant: "destructive",
      });
    },
  });

  const updateProductMutation = useMutation<
    Product,
    Error,
    { id: number; data: ProductFormData }
  >({
    mutationFn: async ({ id, data }) => {
      const updatedProduct = await productApi.updateProduct(String(id), data);
      queryClient.invalidateQueries({ queryKey: ["products"] });
      queryClient.setQueryData(["product", id], updatedProduct);

      const supplierToAssign = data.supplier;
      if (supplierToAssign && supplierToAssign.id) {
        try {
          await productApi.assignSupplierToProduct(
            String(id),
            String(supplierToAssign.id)
          );
          queryClient.invalidateQueries({ queryKey: ["product", id] });
          toast({
            title: "Success",
            description: `Product updated and supplier '${supplierToAssign.name}' assigned.`,
          });
        } catch (assignError) {
          toast({
            title: "Update Successful, Assignment Failed",
            description: `Product details saved, but failed to assign supplier '${
              supplierToAssign.name
            }'. Please try assigning again manually. Error: ${
              assignError instanceof Error
                ? assignError.message
                : "Unknown error"
            }`,
            variant: "destructive",
            duration: 7000,
          });
        }
      } else {
        toast({
          title: "Success",
          description: "Product updated successfully.",
        });
      }

      setIsEditing(false);
      return updatedProduct;
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: `Error updating product: ${error.message}`,
        variant: "destructive",
      });
    },
  });

  // Event Handlers
  const handleSelectItem = (id: number) => {
    if (isEditing) {
      alert(
        "Please save or cancel your current changes before selecting another product."
      );
      return;
    }
    setSelectedItemId(id);
    setIsEditingNew(false);
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.set("productId", String(id));
    router.replace(`${pathname}?${newSearchParams.toString()}`);
    if (maximizedPane === "left") {
      setMaximizedPane("none");
    }
  };

  const handleCreateNew = () => {
    if (isEditing) {
      alert(
        "Please save or cancel your current changes before creating a new product."
      );
      return;
    }
    setSelectedItemId(null);
    setIsEditingNew(true);
    setIsEditing(true);
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.delete("productId");
    router.replace(`${pathname}?${newSearchParams.toString()}`);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    if (isEditingNew) {
      setIsEditingNew(false);
      setSelectedItemId(null);
      const newSearchParams = new URLSearchParams(searchParams);
      if (newSearchParams.has("productId")) {
        newSearchParams.delete("productId");
        router.replace(`${pathname}?${newSearchParams.toString()}`);
      }
    }
  };

  const handleSave = (data: ProductFormData) => {
    if (isEditingNew) {
      createProductMutation.mutate(data);
    } else if (selectedItemId) {
      updateProductMutation.mutate({ id: selectedItemId, data });
    }
  };

  // Handle filter toggle
  const handleFilterToggle = useCallback(() => {
    setFilterActive(prev => !prev);
    // Reset to first page when filter changes
    setPagination(prev => ({ ...prev, pageIndex: 0 }));
  }, []);

  // Last Visited
  useEffect(() => {
    if (!isEditing && productDetailQuery.data) {
      const currentParams = new URLSearchParams(searchParams);
      currentParams.set("productId", String(productDetailQuery.data.id));
      const pathWithQuery = `${pathname}?${currentParams.toString()}`;

      addVisitedItem({
        type: "product",
        id: String(productDetailQuery.data.id),
        name: productDetailQuery.data.name,
        path: pathWithQuery,
      });
    }
  }, [
    productDetailQuery.data,
    isEditing,
    addVisitedItem,
    pathname,
    searchParams,
  ]);

  return (
    <TwoPaneLayout
      maximizedPaneOverride={maximizedPane}
      onMaximizeChange={setMaximizedPane}
      leftPaneContent={
        <ProductListPane
          productsQuery={productsQuery}
          products={products}
          selectedItemId={selectedItemId}
          isEditing={isEditing}
          onSelectItem={handleSelectItem}
          onCreateNew={handleCreateNew}
          onPaginationChange={(direction) => {
            if (direction === "prev") {
              goToPreviousPage();
            } else {
              goToNextPage();
            }
          }}
          pagination={pagination}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          sortConfig={sortConfig}
          requestSort={requestSort}
          onFilterToggle={handleFilterToggle}
          filterActive={filterActive}
        />
      }
      rightPaneContent={
        <ProductDetailPane
          selectedItemId={selectedItemId}
          isEditingNew={isEditingNew}
          productDetailQuery={productDetailQuery}
          variantsQuery={variantsQuery}
          isMutating={
            createProductMutation.isPending || updateProductMutation.isPending
          }
          onEdit={handleEdit}
          onCancelEdit={handleCancelEdit}
          onSave={handleSave}
          router={router}
        />
      }
    />
  );
}
