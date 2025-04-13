'use client'

export const dynamic = 'force-dynamic';

import React, { useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next' 
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query' 
import { format, parseISO } from 'date-fns' 

import {
  ResizableHandle, 
  ResizablePanel, 
  ResizablePanelGroup, 
} from "@/components/ui/resizable" 
import { ScrollArea } from "@/components/ui/scroll-area" 
import { Button } from "@/components/ui/button" 
import { Skeleton } from "@/components/ui/skeleton" 
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert" 
import { AlertCircle, Loader2, Edit, Save, X } from "lucide-react" 
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card" 
import { Separator } from "@/components/ui/separator" 
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar" 
import { Input } from "@/components/ui/input" 
import { Label } from "@/components/ui/label" 
import { Textarea } from "@/components/ui/textarea" 
import { useToast } from "@/hooks/use-toast" 
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select" 
import { TwoPaneLayout, type MaximizedPaneState } from "@/components/ui/TwoPaneLayout"

import { fetchEmployees, fetchEmployeeById, updateEmployee, type Employee, type EmployeeUpdateData } from '@/lib/api/employees' 
import { fetchUsers, type UserSummary } from '@/lib/api/users' 

// Import the new components (assuming they exist in the specified paths)
import EmployeeList from '@/components/employees/EmployeeList';
import EmployeeDetailView from '@/components/employees/EmployeeDetailView';
import EmployeeForm from '@/components/employees/EmployeeForm';

// Define type for form data
type EmployeeFormData = Partial<Omit<Employee, 'id'>> & { 
  // Ensure all editable fields are potentially nullable/string as needed by inputs
  first_name: string;
  last_name: string;
  email: string | null;
  phone_number: string | null;
  address: string | null;
  department: string | null;
  job_title: string | null;
  date_hired: string;
  date_of_birth: string;
  user: number | null; // Add user ID field
}; 

export default function EmployeesPage() {
  const { t } = useTranslation(['common']); 
  const queryClient = useQueryClient(); 
  const { toast } = useToast(); 
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null); 
  const [isEditing, setIsEditing] = useState(false); 
  const [maximizedPane, setMaximizedPane] = useState<MaximizedPaneState>('left');

  // Query for fetching the list of employees
  const { 
    data: employees = [], 
    isLoading: isLoadingList,
    isError: isErrorList,
    error: errorList 
  } = useQuery<Employee[]>({ 
    queryKey: ['employees'], 
    queryFn: fetchEmployees,
    // Only run this query on the client-side
    enabled: typeof window !== 'undefined' 
  }); 

  // Query for fetching the list of users
  const { 
    data: users = [], 
    isLoading: isLoadingUsers,
  } = useQuery<UserSummary[]>({ 
    queryKey: ['users'], 
    queryFn: fetchUsers,
    // Only run this query on the client-side
    enabled: typeof window !== 'undefined' 
  }); 

  // Query for fetching the details of the selected employee
  const { 
    data: selectedEmployee,
    isLoading: isLoadingDetail,
    isFetching: isFetchingDetail,
    isError: isErrorDetail,
    error: errorDetail
  } = useQuery<Employee>({ 
    queryKey: ['employee', selectedEmployeeId], 
    queryFn: () => fetchEmployeeById(selectedEmployeeId!),
    enabled: !!selectedEmployeeId,
  }); 

  // Mutation for Updating Employee
  const updateMutation = useMutation({
    mutationFn: (data: { id: number; formData: EmployeeUpdateData }) => 
      updateEmployee(data.id, data.formData),
    onSuccess: (updatedEmployee) => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      queryClient.setQueryData(['employee', updatedEmployee.id], updatedEmployee);
      setIsEditing(false);
      toast({ title: t('success'), description: t('employee_updated_successfully') });
    },
    onError: (error) => {
      console.error("Update failed:", error);
      toast({ 
          title: t('error'), 
          description: t('failed_update_employee_error', { message: error.message }),
          variant: "destructive"
      });
    },
  }); 

  // Event Handlers
  const handleSelectItem = useCallback((id: number) => {
    if (isEditing) {
        const discard = confirm(t('confirm_discard_changes'));
        if (!discard) return;
    }
    setSelectedEmployeeId(id);
    setIsEditing(false);
    if (maximizedPane === 'left') {
        setMaximizedPane('none');
    }
  }, [isEditing, t, maximizedPane]); 

  const handleEdit = useCallback(() => {
    setIsEditing(true);
  }, []); 

  const handleCancelEdit = useCallback(() => {
    setIsEditing(false);
  }, []); 

  const handleSave = useCallback((formData: EmployeeUpdateData) => {
    if (!selectedEmployeeId) return;
    if (!formData.first_name || !formData.last_name) {
        toast({ title: t('validation_error'), description: t('first_last_name_required'), variant: "destructive" });
        return;
    }
    updateMutation.mutate({ id: selectedEmployeeId, formData: formData });
  }, [selectedEmployeeId, updateMutation, t, toast]); 

  // Determine Right Pane Content
  const renderRightPane = () => {
    if (isEditing && selectedEmployee) {
      return (
        <EmployeeForm
          initialData={selectedEmployee}
          users={users}
          isLoadingUsers={isLoadingUsers}
          isSaving={updateMutation.isPending}
          onSave={handleSave}
          onCancel={handleCancelEdit}
        />
      );
    }

    if (selectedEmployeeId) {
      if (isLoadingDetail) {
        return (
          <Card className="flex flex-col h-full">
            <CardHeader><CardTitle>{t('loading_details')}</CardTitle></CardHeader>
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center space-x-4 mb-6">
                <div className="h-16 w-16 rounded-full bg-muted animate-pulse"></div>
                <div className="space-y-2">
                    <div className="h-6 w-32 bg-muted animate-pulse rounded"></div>
                    <div className="h-4 w-24 bg-muted animate-pulse rounded"></div>
                </div>
              </div>
              <div className="h-4 w-1/4 bg-muted animate-pulse rounded mb-2"></div>
              <div className="h-4 w-3/4 bg-muted animate-pulse rounded mb-4"></div>
              <div className="h-4 w-1/4 bg-muted animate-pulse rounded mb-2"></div>
              <div className="h-4 w-1/2 bg-muted animate-pulse rounded mb-4"></div>
            </CardContent>
          </Card>
        );
      }
      if (isErrorDetail) {
        return (
           <Card className="flex flex-col h-full">
            <CardHeader><CardTitle>{t('error')}</CardTitle></CardHeader>
             <CardContent className="p-6">
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>{t('error_loading_details')}</AlertTitle>
                  <AlertDescription>
                    {(errorDetail as Error)?.message || t('failed_load_employee_details')}
                  </AlertDescription>
                </Alert>
             </CardContent>
           </Card>
        );
      }
      if (selectedEmployee) {
        return (
          <EmployeeDetailView
             employee={selectedEmployee}
             users={users}
             isLoadingUsers={isLoadingUsers}
             isFetchingDetail={isFetchingDetail}
             onEdit={handleEdit}
          />
        );
      }
    }

    return (
      <Card className="flex flex-col h-full items-center justify-center">
        <CardContent className="text-center">
          <p className="text-muted-foreground p-6">
             {t('select_employee_details')}
          </p>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="p-4 h-[calc(100vh-8rem)]">
      <TwoPaneLayout
        maximizedPaneOverride={maximizedPane}
        onMaximizeChange={setMaximizedPane}
        containerClassName="gap-4 h-full"
        leftPaneContent={
            <EmployeeList
                employees={employees}
                isLoading={isLoadingList}
                isError={isErrorList}
                error={errorList as Error | null}
                selectedEmployeeId={selectedEmployeeId}
                isEditing={isEditing}
                onSelectItem={handleSelectItem}
            />
        }
        rightPaneContent={renderRightPane()}
      />
    </div>
  ) 
} 