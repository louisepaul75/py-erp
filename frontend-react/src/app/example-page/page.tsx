'use client';

import { useState } from 'react';
import { 
  Button, 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent, 
  CardFooter,
  Input,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  StatusBadge
} from '@/components/ui';
import { Search, Plus, Filter, Download, Trash, Edit, Settings } from 'lucide-react';
import { Separator } from '@/components/ui/separator';

// Sample data
const SAMPLE_DATA = [
  { id: 1, name: 'Product A', category: 'Electronics', price: 299.99, stock: 45, status: 'active' },
  { id: 2, name: 'Product B', category: 'Clothing', price: 59.99, stock: 12, status: 'active' },
  { id: 3, name: 'Product C', category: 'Home', price: 149.99, stock: 0, status: 'inactive' },
  { id: 4, name: 'Product D', category: 'Electronics', price: 499.99, stock: 8, status: 'active' },
  { id: 5, name: 'Product E', category: 'Books', price: 19.99, stock: 3, status: 'pending' },
];

export default function ExamplePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(false);

  // Filter data based on search query and category
  const filteredData = SAMPLE_DATA.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === '' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Handle search
  const handleSearch = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  // Get unique categories
  const categories = Array.from(new Set(SAMPLE_DATA.map(item => item.category)));

  return (
    <div className="container mx-auto py-20 px-4 md:px-6 h-full overflow-auto">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-amber-500">Product Management</h1>
            <p className="text-gray-400 mt-1">Manage your product inventory</p>
          </div>
          <Button icon={Plus} className="mt-4 md:mt-0">Add New Product</Button>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle icon={Filter}>Filters</CardTitle>
            <CardDescription>Filter and search products</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input 
                icon={Search}
                placeholder="Search products..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                fullWidth
              />
              
              <div>
                <label className="text-sm font-medium mb-1 block">Category</label>
                <select 
                  className="w-full rounded-md border border-amber-800/30 bg-amber-950/20 px-3 py-2 text-sm focus:border-amber-500 focus:outline-none"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-end">
                <Button 
                  icon={Search} 
                  onClick={handleSearch} 
                  loading={loading}
                  fullWidth
                >
                  Search
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
              <div>
                <CardTitle icon={Settings}>Products</CardTitle>
                <CardDescription>Showing {filteredData.length} products</CardDescription>
              </div>
              <Button 
                variant="outline" 
                icon={Download} 
                size="sm" 
                className="mt-4 md:mt-0"
              >
                Export
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Stock</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.length > 0 ? (
                  filteredData.map(product => (
                    <TableRow key={product.id}>
                      <TableCell>{product.id}</TableCell>
                      <TableCell>{product.name}</TableCell>
                      <TableCell>{product.category}</TableCell>
                      <TableCell>${product.price.toFixed(2)}</TableCell>
                      <TableCell>{product.stock}</TableCell>
                      <TableCell>
                        <StatusBadge status={product.status as 'active' | 'pending' | 'inactive'}>
                          {product.status.charAt(0).toUpperCase() + product.status.slice(1)}
                        </StatusBadge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" icon={Edit} aria-label="Edit" />
                          <Button variant="ghost" size="sm" icon={Trash} aria-label="Delete" />
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-gray-400">
                      No products found matching your criteria
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
          <CardFooter highlighted className="flex justify-between">
            <div className="text-sm text-gray-400">
              Showing {filteredData.length} of {SAMPLE_DATA.length} products
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled>Previous</Button>
              <Button variant="outline" size="sm" disabled>Next</Button>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
} 