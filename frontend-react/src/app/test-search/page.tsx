"use client";

import React, { useState, useEffect } from 'react';
import { productApi } from '@/lib/products/api';
import { Product } from '@/components/types/product';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Button
} from "@/components/ui";

export default function TestSearchPage() {
  const [searchTerm, setSearchTerm] = useState('11205');
  const [results, setResults] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const handleSearch = async () => {
    try {
      setIsLoading(true);
      const response = await productApi.getProducts({
        q: searchTerm,
        page: 1,
        page_size: 20
      });

      if (response?.results) {
        console.log('Search results:', response);
        setResults(response.results);
        setTotalCount(response.count || 0);
      } else {
        setResults([]);
        setTotalCount(0);
      }
    } catch (error) {
      console.error('Error searching products:', error);
      setResults([]);
      setTotalCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial search on component mount
  useEffect(() => {
    handleSearch();
  }, []);

  return (
    <div className="container mx-auto py-8 px-4">
      <Card>
        <CardHeader>
          <CardTitle>Product Search Test</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-6">
            <Input
              type="search"
              placeholder="Search by name, legacy_base_sku, or legacy_sku..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
            <Button onClick={handleSearch} disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </Button>
          </div>

          <div className="mt-4">
            <p className="text-sm mb-2">Found {totalCount} products</p>
            {results.length > 0 ? (
              <div className="grid gap-4">
                {results.map((product) => (
                  <Card key={product.id} className="p-4">
                    <div className="flex flex-col gap-1">
                      <p className="font-bold">{product.name}</p>
                      <p className="text-sm">SKU: {product.sku}</p>
                      {product.legacy_base_sku && (
                        <p className="text-sm">Legacy Base SKU: {product.legacy_base_sku}</p>
                      )}
                      <p className="text-sm">Variants: {product.variants_count || 0}</p>
                      <p className="text-sm">Status: {product.is_active ? 'Active' : 'Inactive'}</p>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-center">No products found</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 