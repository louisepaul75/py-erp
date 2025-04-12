'use client';

import * as React from 'react';
import { Building2, Edit, Mail, Phone, Trash, Eye } from 'lucide-react';

import { Supplier } from '@/types/supplier'; // Assuming Supplier type is defined here
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

interface SupplierCardProps {
  supplier: Supplier;
  onEdit: (supplier: Supplier) => void;
  onDelete: (supplier: Supplier) => void;
  onViewDetails: (supplier: Supplier) => void;
}

export function SupplierCard({ supplier, onEdit, onDelete, onViewDetails }: SupplierCardProps) {
  // Assume supplier type has `syncedAt?: string | null`
  const isSynced = !!supplier.syncedAt;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start gap-2">
          <CardTitle className="text-lg font-semibold leading-tight truncate">{supplier.name}</CardTitle>
          <Badge variant={isSynced ? 'default' : 'outline'} className={isSynced ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border-green-300 dark:border-green-700' : ''}>
            {isSynced ? 'Synced' : 'Not Synced'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pb-3 text-sm text-muted-foreground space-y-1.5">
        <div className="flex items-center">
          <Building2 className="mr-2 h-4 w-4 flex-shrink-0" />
          <span className="truncate" title={supplier.contactPerson || ''}>{supplier.contactPerson || '-'}</span>
        </div>
        <div className="flex items-center">
          <Mail className="mr-2 h-4 w-4 flex-shrink-0" />
          <span className="truncate" title={supplier.email || ''}>{supplier.email || '-'}</span>
        </div>
        <div className="flex items-center">
          <Phone className="mr-2 h-4 w-4 flex-shrink-0" />
          <span className="truncate" title={supplier.phone || ''}>{supplier.phone || '-'}</span>
        </div>
      </CardContent>
      <CardFooter className="pt-3">
        <div className="flex justify-end w-full gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onViewDetails(supplier)}
            aria-label="View supplier details"
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onEdit(supplier)}
            aria-label="Edit supplier"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-red-600 hover:text-red-700"
            onClick={() => onDelete(supplier)}
            aria-label="Delete supplier"
          >
            <Trash className="h-4 w-4" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
} 