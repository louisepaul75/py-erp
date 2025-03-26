"use client"

import { useState, useEffect } from "react"
import { Plus, Download, Upload, Trash, Edit, Search, Filter, ChevronDown, ArrowUpDown, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select } from "@/components/ui/select"
import { ProductFilters } from "@/components/products/product-filters"
import ProductMobile from "@/components/products/product-mobile"
import ProductDetailDialog from "@/components/products/product-detail-dialog"
import DeleteConfirmDialog from "@/components/products/delete-confirm-dialog"
import { Product, ApiResponse } from "../types/product"
import { productApi } from "@/lib/products/api"
import { StatusBadge } from "@/components/ui"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Container } from "@/components/ui/container"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

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
    <Container>
      <div className="max-w-5xl mx-auto py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2 text-primary">Produkte</h1>
            <p className="text-muted-foreground">Verwalten Sie Ihre Produktliste</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Exportieren
            </Button>
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Importieren
            </Button>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Neues Produkt
            </Button>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Produktliste</CardTitle>
            <CardDescription>Alle Produkte in Ihrem Katalog</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-4 flex flex-wrap items-center gap-2">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500 dark:text-gray-300" />
                <Input
                  type="search"
                  placeholder="Suche nach Produkt..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
              <div className="flex items-center gap-2">
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
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                >
                  <span>Status</span>
                  <ChevronDown className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                >
                  <span>Kategorie</span>
                  <ChevronDown className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800/50">
                  <TableHead className="w-[40px] font-medium cursor-pointer text-slate-700 dark:text-slate-300">
                    <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300 dark:border-gray-600">
                      <Check className="h-3 w-3" />
                    </div>
                  </TableHead>
                  <TableHead className="font-medium cursor-pointer text-slate-700 dark:text-slate-300">
                    <div className="flex items-center gap-1">
                      <span>SKU</span>
                      <ArrowUpDown className="h-4 w-4" />
                    </div>
                  </TableHead>
                  <TableHead className="font-medium cursor-pointer text-slate-700 dark:text-slate-300">
                    <div className="flex items-center gap-1">
                      <span>Name</span>
                      <ArrowUpDown className="h-4 w-4" />
                    </div>
                  </TableHead>
                  <TableHead className="font-medium cursor-pointer text-slate-700 dark:text-slate-300">
                    <div className="flex items-center gap-1">
                      <span>Status</span>
                      <ArrowUpDown className="h-4 w-4" />
                    </div>
                  </TableHead>
                  <TableHead className="font-medium cursor-pointer text-slate-700 dark:text-slate-300">
                    <div className="flex items-center gap-1">
                      <span>Category</span>
                      <ArrowUpDown className="h-4 w-4" />
                    </div>
                  </TableHead>
                  <TableHead className="font-medium cursor-pointer text-slate-700 dark:text-slate-300 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProducts.map((product) => (
                  <TableRow key={product.id} onClick={() => handleRowClick(product)}>
                    <TableCell>
                      <div className="flex h-4 w-4 items-center justify-center rounded border border-gray-300 dark:border-gray-600">
                        {selectedProducts.includes(product.id) && <Check className="h-3 w-3" />}
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">{product.sku}</TableCell>
                    <TableCell>{product.name}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <StatusBadge status={product.is_active ? "active" : "inactive"}>
                          {product.is_active ? "Active" : "Inactive"}
                        </StatusBadge>
                        {product.is_new && (
                          <StatusBadge status="info" className="bg-purple-500">
                            New
                          </StatusBadge>
                        )}
                        {product.is_discontinued && (
                          <StatusBadge status="warning">
                            Discontinued
                          </StatusBadge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{product.category}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditClick(product);
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteClick(product);
                          }}
                        >
                          <Trash className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {/* Pagination */}
            {!isLoading && filteredProducts.length > 0 && (
              <div className="mt-4 flex items-center justify-between">
                <div className="text-sm text-slate-500 dark:text-slate-400">
                  <strong>{selectedProducts.length}</strong> items selected
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-500 dark:text-slate-400">
                      Einträge pro Seite:
                    </span>
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
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(pagination.pageIndex - 1)}
                      disabled={pagination.pageIndex === 0}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange(pagination.pageIndex + 1)}
                      disabled={pagination.pageIndex >= totalPages - 1}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

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
    </Container>
  )
} 