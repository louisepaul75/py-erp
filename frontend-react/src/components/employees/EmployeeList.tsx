'use client'

import React from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";
import type { Employee } from '@/lib/api/employees';

interface EmployeeListProps {
  employees: Employee[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  selectedEmployeeId: number | null;
  isEditing: boolean; // To disable selection while parent is in edit mode
  onSelectItem: (id: number) => void;
}

const EmployeeList: React.FC<EmployeeListProps> = ({
  employees,
  isLoading,
  isError,
  error,
  selectedEmployeeId,
  isEditing,
  onSelectItem,
}) => {
  const { t } = useTranslation(['common']);

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="p-4">
        <CardTitle className="text-lg">{t('navigation.employees')}</CardTitle>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto p-0">
        <ScrollArea className="h-full">
          <div className="p-4 space-y-2">
            {isLoading && (
              <>
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </>
            )}
            {isError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>{t('error')}</AlertTitle>
                <AlertDescription>
                  {error?.message || t('failed_load_employees')}
                </AlertDescription>
              </Alert>
            )}
            {!isLoading && !isError && (employees || []).map((employee) => (
              <Button
                key={employee.id}
                variant={selectedEmployeeId === employee.id ? "secondary" : "ghost"}
                onClick={() => onSelectItem(employee.id)}
                className="w-full justify-start h-auto py-2 px-3 text-left"
                aria-current={selectedEmployeeId === employee.id}
                // Optionally disable buttons if parent is editing *another* employee
                disabled={isEditing && selectedEmployeeId !== employee.id}
              >
                <div className="flex flex-col">
                  <span className="font-medium">
                    {employee.first_name} {employee.last_name}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {employee.employee_number} - {employee.job_title || t('na')}
                  </span>
                </div>
              </Button>
            ))}
            {!isLoading && !isError && employees?.length === 0 && (
              <p className="text-sm text-muted-foreground p-4 text-center">
                {t('no_employees_found')}
              </p>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default EmployeeList; 