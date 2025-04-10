"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";
import { formatDate } from "@/lib/utils";

// UI Components
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge, BadgeProps } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// Define a basic Document type (adjust fields based on your API response)
interface Document {
  id: number | string;
  number: string;
  type: "Order" | "Invoice" | "DeliveryNote" | string; // Or more specific types
  date: string | Date;
  status: string; // e.g., "Draft", "Confirmed", "Paid", "Shipped"
  amount: number;
}

// Basic currency formatter (copy or import from utils)
const formatCurrency = (value: number | undefined | null) => {
    if (value == null) return '-';
    return new Intl.NumberFormat("default", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 2,
    }).format(value);
};

// Helper to determine Badge variant based on status (customize as needed)
const getStatusBadgeVariant = (status: string): BadgeProps["variant"] => {
    const lowerStatus = status.toLowerCase();
    if (lowerStatus.includes("paid") || lowerStatus.includes("completed") || lowerStatus.includes("delivered")) return "default";
    if (lowerStatus.includes("pending") || lowerStatus.includes("confirmed")) return "default";
    if (lowerStatus.includes("draft")) return "secondary";
    if (lowerStatus.includes("cancelled") || lowerStatus.includes("error")) return "destructive";
    return "outline";
};

// Helper to get the correct link path based on document type
const getDocumentLink = (doc: Document): string => {
    switch (doc.type.toLowerCase()) {
        case 'order':
            return `/sales/orders/${doc.id}`;
        case 'invoice':
            return `/sales/invoices/${doc.id}`;
        case 'deliverynote':
             return `/logistics/delivery-notes/${doc.id}`; // Adjust path as needed
        default:
            return '#'; // Fallback or handle unknown types
    }
}

export interface CustomerDocumentsTableProps {
  customerId: string;
}

export default function CustomerDocumentsTable({ customerId }: CustomerDocumentsTableProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!customerId) return; // Don't fetch if customerId is not available

    const fetchDocuments = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const token = await authService.getToken();
        if (!token) throw new Error("Authentication required.");

        // Adjust API endpoint as needed
        // Option 1: Nested resource
        // const endpoint = `${API_URL}/sales/customers/${customerId}/documents/`;
        // Option 2: Filter parameter
        const endpoint = `${API_URL}/sales/documents/?customerId=${customerId}`; // Example endpoint

        const response = await fetch(endpoint, {
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
         // Assuming API returns { results: [...] } or just [...]
        const fetchedDocuments: Document[] = Array.isArray(data) ? data : data.results || [];
        setDocuments(fetchedDocuments);

      } catch (err) {
        console.error("Error fetching customer documents:", err);
        setError(err instanceof Error ? err.message : "Failed to load documents");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocuments();
  }, [customerId]);

  // Loading State
  if (isLoading) {
    return (
        <div className="space-y-2 py-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
        </div>
    );
  }

  // Error State
  if (error) {
    return (
        <Alert variant="destructive" className="my-4">
            <AlertTitle>Error Loading Documents</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
        </Alert>
    );
  }

  // No Documents State
  if (documents.length === 0) {
    return <p className="text-center py-6 text-muted-foreground">No documents found for this customer.</p>;
  }

  // Render Table
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[120px]">Number</TableHead>
          <TableHead className="w-[100px]">Type</TableHead>
          <TableHead className="hidden md:table-cell">Date</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Amount</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {documents.map((doc) => (
          <TableRow key={doc.id}>
            <TableCell>
              <Link
                href={getDocumentLink(doc)}
                className="font-medium text-primary hover:underline"
              >
                {doc.number}
              </Link>
            </TableCell>
            <TableCell>{doc.type}</TableCell>
            <TableCell className="hidden md:table-cell">{formatDate(doc.date)}</TableCell>
            <TableCell>
              <Badge variant={getStatusBadgeVariant(doc.status)}>{doc.status}</Badge>
            </TableCell>
            <TableCell className="text-right">{formatCurrency(doc.amount)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
} 