'use client';

import * as React from 'react';
import { Supplier } from '@/types/supplier'; // Assuming Supplier type is defined here
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';

interface SupplierDetailDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  supplier: Supplier | null; // Pass the full supplier object
}

export function SupplierDetailDialog({ open, onOpenChange, supplier }: SupplierDetailDialogProps) {
  const isSynced = !!supplier?.syncedAt; // Use syncedAt based on type assumption

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]"> {/* Adjusted size from draft */}
        <DialogHeader>
          <DialogTitle>
            {supplier ? supplier.name : 'Supplier Details'}
          </DialogTitle>
          <DialogDescription>
            Detailed information for the selected supplier.
          </DialogDescription>
        </DialogHeader>

        {!supplier ? (
          // Display Skeleton or message if supplier is null
          <div className="space-y-4 py-4">
             <Skeleton className="h-8 w-3/4 mb-2" />
             <Skeleton className="h-4 w-1/2" />
             <Skeleton className="h-4 w-1/2" />
             <Skeleton className="h-4 w-full" />
             <Skeleton className="h-4 w-1/3" />
             <Skeleton className="h-4 w-1/3" />
             <Skeleton className="h-6 w-1/4" />
          </div>
        ) : (
          // Display supplier details
          <div className="py-4 space-y-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Supplier Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-3">
                  <div className="space-y-1">
                    <Label htmlFor="detail-name" className="text-xs text-muted-foreground">Company Name</Label>
                    <div id="detail-name">{supplier.name || '-'}</div>
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="detail-contact" className="text-xs text-muted-foreground">Contact Person</Label>
                    <div id="detail-contact">{supplier.contactPerson || '-'}</div>
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="detail-email" className="text-xs text-muted-foreground">Email</Label>
                    <div id="detail-email" className="truncate">{supplier.email || '-'}</div>
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="detail-phone" className="text-xs text-muted-foreground">Phone</Label>
                    <div id="detail-phone">{supplier.phone || '-'}</div>
                  </div>
                  <div className="space-y-1 md:col-span-2">
                    <Label htmlFor="detail-address" className="text-xs text-muted-foreground">Address</Label>
                    <div id="detail-address">{supplier.address || '-'}</div>
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="detail-tax-id" className="text-xs text-muted-foreground">Tax ID</Label>
                    <div id="detail-tax-id">{supplier.taxId || '-'}</div>
                  </div>
                  <div className="space-y-1">
                     <Label htmlFor="detail-creditor-id" className="text-xs text-muted-foreground">Creditor ID</Label>
                     <div id="detail-creditor-id">{supplier.creditorId || '-'}</div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs text-muted-foreground">Sync Status</Label>
                    <div>
                      <Badge
                        variant={isSynced ? 'default' : 'outline'}
                        className={
                          isSynced
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-300 dark:border-green-700'
                            : ''
                        }
                      >
                        {isSynced ? 'Synced' : 'Not Synced'}
                        {isSynced && supplier.syncedAt && ` (${new Date(supplier.syncedAt).toLocaleDateString()})`}
                      </Badge>
                    </div>
                  </div>
                  {/* Conditionally render accountingId if it exists */}
                  {supplier.accountingId !== undefined && (
                     <div className="space-y-1">
                       <Label htmlFor="detail-accounting-id" className="text-xs text-muted-foreground">Accounting ID</Label>
                       <div id="detail-accounting-id">{supplier.accountingId || '-'}</div>
                     </div>
                  )}
                </div>
              </CardContent>
            </Card>
            {/* Placeholder for future tabs/actions - could add a close button if needed */}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
} 