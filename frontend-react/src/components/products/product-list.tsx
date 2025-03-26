"use client"

import { useState, useEffect } from "react"
import { Plus, Download, Upload, Trash } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import ProductFilters from "@/components/products/product-filters"
import ProductTable from "@/components/products/product-table"
import ProductMobile from "@/components/products/product-mobile"
import ProductDetailDialog from "@/components/products/product-detail-dialog"
import DeleteConfirmDialog from "@/components/products/delete-confirm-dialog"
import { Product, ApiResponse } from "../types/product"
import { productApi } from "@/lib/products/api"

export type { Product }

export default function ProductList() {
  // State for products and filtering
  const [products, setProducts] = useState<Product[]>([])
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([])
  const [selectedProducts, setSelectedProducts] = useState<number[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [categoryFilter, setCategoryFilter] = useState("all")
  const [isNewFilter, setIsNewFilter] = useState("all")
  const [isActiveFilter, setIsActiveFilter] = useState("all")
  
  // Pagination state
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 50,
  })
  const [totalItems, setTotalItems] = useState(0)
  
  // UI state
  const [isLoading, setIsLoading] = useState(true)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch products when pagination changes
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setIsLoading(true)
        const response = (await productApi.getProducts({
          page: pagination.pageIndex + 1, // Backend uses 1-based index
          page_size: pagination.pageSize,
        })) as ApiResponse

        setProducts(response.results)
        setFilteredProducts(response.results)
        setTotalItems(response.count)
        console.log("Fetched products:", response)
      } catch (error) {
        console.error("Error fetching products:", error)
        setError("Fehler beim Laden der Produkte")
      } finally {
        setIsLoading(false)
      }
    }
    fetchProducts()
  }, [pagination.pageIndex, pagination.pageSize])

  // Apply filters when filter state changes
  useEffect(() => {
    let filtered = [...products]

    // Text search
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(
        (product) => 
          product.sku.toLowerCase().includes(term) || 
          product.name.toLowerCase().includes(term)
      )
    }

    // Status filter
    if (statusFilter !== "all") {
      if (statusFilter === "active") {
        filtered = filtered.filter(product => product.is_active)
      } else if (statusFilter === "inactive") {
        filtered = filtered.filter(product => !product.is_active)
      } else if (statusFilter === "discontinued") {
        filtered = filtered.filter(product => product.is_discontinued)
      }
    }

    // Category filter
    if (categoryFilter !== "all") {
      filtered = filtered.filter(product => product.category === categoryFilter)
    }

    // New product filter
    if (isNewFilter !== "all") {
      filtered = filtered.filter(product => 
        isNewFilter === "new" ? product.is_new : !product.is_new
      )
    }

    // Active filter
    if (isActiveFilter !== "all") {
      filtered = filtered.filter(product => 
        isActiveFilter === "active" ? product.is_active : !product.is_active
      )
    }

    setFilteredProducts(filtered)
  }, [products, searchTerm, statusFilter, categoryFilter, isNewFilter, isActiveFilter])

  // Handlers
  const handleSelectProduct = (id: number, checked: boolean) => {
    if (id === 0) {
      // Select/deselect all
      if (checked) {
        setSelectedProducts(filteredProducts.map(product => product.id))
      } else {
        setSelectedProducts([])
      }
    } else {
      if (checked) {
        setSelectedProducts([...selectedProducts, id])
      } else {
        setSelectedProducts(selectedProducts.filter(productId => productId !== id))
      }
    }
  }

  const handleRowClick = (product: Product) => {
    setSelectedProduct(product)
    setIsDetailOpen(true)
  }

  const handleEditClick = (product: Product) => {
    // This would open an edit form in a real application
    console.log("Edit product:", product)
  }

  const handleDeleteClick = (product: Product) => {
    setSelectedProduct(product)
    setIsDeleteConfirmOpen(true)
  }

  const handleConfirmDelete = async () => {
    if (!selectedProduct) return

    try {
      // In a real application, this would call an API to delete the product
      // await productApi.deleteProduct(selectedProduct.id)
      
      // For now, just remove it from the local state
      setProducts(products.filter(p => p.id !== selectedProduct.id))
      setSelectedProducts(selectedProducts.filter(id => id !== selectedProduct.id))
      
      console.log(`Product ${selectedProduct.id} deleted`)
    } catch (error) {
      console.error("Error deleting product:", error)
      setError("Fehler beim Löschen des Produkts")
    }
  }

  const handlePageChange = (page: number) => {
    setPagination({ ...pagination, pageIndex: page })
    // Scroll to top
    window.scrollTo(0, 0)
  }

  const handleItemsPerPageChange = (value: string) => {
    const newPageSize = parseInt(value, 10)
    setPagination({ pageIndex: 0, pageSize: newPageSize })
  }

  // Calculate total pages for pagination
  const totalPages = Math.ceil(totalItems / pagination.pageSize)

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <h1 className="text-2xl font-bold">Produkte</h1>
        
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Importieren
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportieren
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-red-500"
            disabled={selectedProducts.length === 0}
          >
            <Trash className="h-4 w-4 mr-2" />
            Ausgewählte löschen ({selectedProducts.length})
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Neues Produkt
          </Button>
        </div>
      </div>

      <ProductFilters
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        categoryFilter={categoryFilter}
        setCategoryFilter={setCategoryFilter}
        isNewFilter={isNewFilter}
        setIsNewFilter={setIsNewFilter}
        isActiveFilter={isActiveFilter}
        setIsActiveFilter={setIsActiveFilter}
      />

      {/* Error message */}
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
          <p>{error}</p>
        </div>
      )}

      {/* Desktop Table View */}
      <div className="hidden md:block">
        <ProductTable
          products={filteredProducts}
          selectedProducts={selectedProducts}
          handleSelectProduct={handleSelectProduct}
          handleRowClick={handleRowClick}
          handleEditClick={handleEditClick}
          handleDeleteClick={handleDeleteClick}
          isLoading={isLoading}
        />
      </div>

      {/* Mobile List View */}
      <ProductMobile
        products={filteredProducts}
        selectedProducts={selectedProducts}
        handleSelectProduct={handleSelectProduct}
        handleRowClick={handleRowClick}
        handleEditClick={handleEditClick}
        handleDeleteClick={handleDeleteClick}
      />

      {/* Pagination */}
      {!isLoading && filteredProducts.length > 0 && (
        <div className="flex flex-col sm:flex-row items-center justify-between mt-6 gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Einträge pro Seite:</span>
            <Select
              value={pagination.pageSize.toString()}
              onValueChange={handleItemsPerPageChange}
              options={[
                { value: "10", label: "10" },
                { value: "20", label: "20" },
                { value: "50", label: "50" },
                { value: "100", label: "100" },
              ]}
            />
          </div>

          {totalPages > 1 && (
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(pagination.pageIndex - 1)}
                disabled={pagination.pageIndex === 0}
              >
                Zurück
              </Button>
              
              <div className="text-sm mx-2">
                Seite {pagination.pageIndex + 1} von {totalPages}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(pagination.pageIndex + 1)}
                disabled={pagination.pageIndex >= totalPages - 1}
              >
                Weiter
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Dialogs */}
      <ProductDetailDialog
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        product={selectedProduct}
      />

      <DeleteConfirmDialog
        isOpen={isDeleteConfirmOpen}
        onClose={() => setIsDeleteConfirmOpen(false)}
        onConfirm={handleConfirmDelete}
        product={selectedProduct}
      />
    </div>
  )
} 