'use client';

import React from 'react';
import { CustomerDocument } from '@/lib/definitions';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { UploadIcon, DownloadIcon, FileTextIcon } from 'lucide-react'; // Example icons

interface CustomerDocumentsCardProps {
  documents: CustomerDocument[];
  // Add customerId if needed for uploading new documents
}

// Helper to format date (replace with a robust library like date-fns if needed)
const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric',
    });
  } catch (e) {
    console.error("Error formatting date:", e);
    return dateString; // Fallback
  }
};

// Helper to format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export default function CustomerDocumentsCard({ documents }: CustomerDocumentsCardProps) {
  // TODO: Implement uploading new documents functionality

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Documents</CardTitle>
        <Button size="sm" variant="outline" disabled> {/* TODO: Enable and implement upload */}
          <UploadIcon className="mr-2 h-4 w-4" /> Upload Document
        </Button>
      </CardHeader>
      <CardContent>
        {(!documents || documents.length === 0) ? (
          <p className="text-sm text-muted-foreground py-4 text-center">No documents found for this customer.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px] hidden sm:table-cell"></TableHead> {/* Icon column */}
                <TableHead>Filename</TableHead>
                <TableHead className="hidden md:table-cell">Type</TableHead>
                <TableHead className="hidden lg:table-cell">Size</TableHead>
                <TableHead className="hidden sm:table-cell">Uploaded</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.id}>
                   <TableCell className="hidden sm:table-cell">
                     <FileTextIcon className="h-5 w-5 text-muted-foreground" />
                   </TableCell>
                  <TableCell className="font-medium truncate max-w-xs">{doc.filename}</TableCell>
                  <TableCell className="hidden md:table-cell">{doc.file_type.toUpperCase()}</TableCell>
                  <TableCell className="hidden lg:table-cell">{formatFileSize(doc.size)}</TableCell>
                  <TableCell className="hidden sm:table-cell">{formatDate(doc.upload_date)}</TableCell>
                  <TableCell className="text-right">
                    {/* Add conditional rendering based on doc.url */}
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={!doc.url} // Disable if no URL
                      // onClick={() => window.open(doc.url, '_blank')} // Simple download/view action
                    >
                      <DownloadIcon className="h-4 w-4" />
                      <span className="sr-only">Download</span>
                    </Button>
                    {/* TODO: Add Delete button/action */}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
} 