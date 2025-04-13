'use client'

export const dynamic = 'force-dynamic';

import React, { useState, useEffect } from 'react'
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

// Helper to display data or a placeholder
const DetailItem = ({ label, value }: { label: string; value: string | null | undefined }) => (
  <div className="grid grid-cols-3 gap-4 py-2">
    <dt className="text-sm font-medium text-muted-foreground">{label}</dt>
    <dd className="text-sm col-span-2">{value || '-'}</dd>
  </div>
); 

export default function EmployeesPage() {
  const { t } = useTranslation(['common']); 
  const queryClient = useQueryClient(); 
  const { toast } = useToast(); 
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null); 
  const [isEditing, setIsEditing] = useState(false); 
  const [employeeFormData, setEmployeeFormData] = useState<EmployeeFormData | null>(null); 
  const [maximizedPane, setMaximizedPane] = useState<MaximizedPaneState>('left');

  // Query for fetching the list of employees
  const { 
    data: employees = [], 
    isLoading: isLoadingList,
    isError: isErrorList,
    error: errorList 
  } = useQuery<Employee[]>({ 
    queryKey: ['employees'], 
    queryFn: fetchEmployees 
  }); 

  // Query for fetching the list of users
  const { 
    data: users = [], 
    isLoading: isLoadingUsers,
  } = useQuery<UserSummary[]>({ 
    queryKey: ['users'], 
    queryFn: fetchUsers 
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

  // --- Form Data Initialization on Detail Load or Edit Start ---
  useEffect(() => {
    if (selectedEmployee && !isEditing) {
      setEmployeeFormData({
        ...selectedEmployee,
        date_hired: selectedEmployee.date_hired ? format(parseISO(selectedEmployee.date_hired), 'yyyy-MM-dd') : '',
        date_of_birth: selectedEmployee.date_of_birth ? format(parseISO(selectedEmployee.date_of_birth), 'yyyy-MM-dd') : '',
        // user is already included via spread, as it's number | null
      });
    }
    if (!selectedEmployeeId) {
        setIsEditing(false);
        setEmployeeFormData(null);
    }
  }, [selectedEmployee, isEditing, selectedEmployeeId]); 

  // --- Mutation for Updating Employee ---
  const updateMutation = useMutation({
    mutationFn: (data: { id: number; formData: EmployeeUpdateData }) => 
      updateEmployee(data.id, data.formData),
    onSuccess: (updatedEmployee) => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      queryClient.setQueryData(['employee', updatedEmployee.id], updatedEmployee);
      setIsEditing(false);
      setEmployeeFormData({
         ...updatedEmployee,
         date_hired: updatedEmployee.date_hired ? format(parseISO(updatedEmployee.date_hired), 'yyyy-MM-dd') : '',
         date_of_birth: updatedEmployee.date_of_birth ? format(parseISO(updatedEmployee.date_of_birth), 'yyyy-MM-dd') : '',
         // user: updatedEmployee.user // Already included via spread
      });
      toast({ title: "Success", description: "Employee updated successfully." });
    },
    onError: (error) => {
      console.error("Update failed:", error);
      toast({ 
          title: "Error", 
          description: `Failed to update employee: ${error.message}`,
          variant: "destructive"
      });
    },
  }); 

  // --- Event Handlers ---
  const handleSelectItem = (id: number) => {
    if (isEditing) {
        const discard = confirm("You have unsaved changes. Discard them and view the selected employee?");
        if (!discard) return;
    }
    setSelectedEmployeeId(id);
    setIsEditing(false);
    if (maximizedPane === 'left') {
        setMaximizedPane('none');
    }
  }; 

  const handleEdit = () => {
    if (!selectedEmployee) return;
    setEmployeeFormData({
      ...selectedEmployee,
       date_hired: selectedEmployee.date_hired ? format(parseISO(selectedEmployee.date_hired), 'yyyy-MM-dd') : '',
       date_of_birth: selectedEmployee.date_of_birth ? format(parseISO(selectedEmployee.date_of_birth), 'yyyy-MM-dd') : '',
       // user is already included via spread
    });
    setIsEditing(true);
  }; 

  const handleCancelEdit = () => {
    setIsEditing(false);
    if (selectedEmployee) {
        setEmployeeFormData({
            ...selectedEmployee,
            date_hired: selectedEmployee.date_hired ? format(parseISO(selectedEmployee.date_hired), 'yyyy-MM-dd') : '',
            date_of_birth: selectedEmployee.date_of_birth ? format(parseISO(selectedEmployee.date_of_birth), 'yyyy-MM-dd') : '',
            // user is already included via spread
        });
    }
  }; 

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEmployeeFormData(prev => prev ? { ...prev, [name]: value } : null);
  }; 

  // Handler for Select component changes (specific for user dropdown)
  const handleUserChange = (value: string) => {
    const userId = value === 'null' ? null : parseInt(value, 10);
    setEmployeeFormData(prev => prev ? { ...prev, user: userId } : null);
  }; 

  const handleSave = () => {
    if (!selectedEmployeeId || !employeeFormData) {
        toast({ title: "Error", description: "Cannot save, employee data is missing.", variant: "destructive" });
        return;
    }
    if (!employeeFormData.first_name || !employeeFormData.last_name) {
         toast({ title: "Validation Error", description: "First name and last name are required.", variant: "destructive" });
         return;
    }
    
    // Prepare data for update, ensuring user ID is correctly formatted
    const updateData: EmployeeUpdateData = {
        ...employeeFormData,
        date_hired: employeeFormData.date_hired || undefined,
        date_of_birth: employeeFormData.date_of_birth || null,
        // user is already number | null
    };

    updateMutation.mutate({ id: selectedEmployeeId, formData: updateData });
  }; 

  // Helper to format dates
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    try {
      return format(parseISO(dateString), 'PPP'); // e.g., Jan 1, 2023
    } catch (e) {
      return 'Invalid Date';
    }
  } 

  // Determine which data to display (form data if editing, otherwise fetched data)
  const displayEmployee = isEditing ? employeeFormData : selectedEmployee; 

  return (
    <div className="p-4 h-[calc(100vh-8rem)]">
      <TwoPaneLayout
        maximizedPaneOverride={maximizedPane}
        onMaximizeChange={setMaximizedPane}
        containerClassName="gap-4 h-full"
        leftPaneContent={
            <Card className="flex flex-col h-full">
                <CardHeader className="p-4">
                <CardTitle className="text-lg">{t('navigation.employees')}</CardTitle>
                </CardHeader>
                <CardContent className="flex-grow overflow-y-auto p-0">
                <ScrollArea className="h-full">
                    <div className="p-4 space-y-2">
                    {isLoadingList && (
                        <>
                        <Skeleton className="h-10 w-full" />
                        <Skeleton className="h-10 w-full" />
                        <Skeleton className="h-10 w-full" />
                        </>
                    )}
                    {isErrorList && (
                        <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Error</AlertTitle>
                        <AlertDescription>
                            {(errorList as Error)?.message || "Failed to load employees."}
                        </AlertDescription>
                        </Alert>
                    )}
                    {!isLoadingList && !isErrorList && (employees || []).map((employee) => (
                        <Button
                        key={employee.id}
                        variant={selectedEmployeeId === employee.id ? "secondary" : "ghost"}
                        onClick={() => handleSelectItem(employee.id)}
                        className="w-full justify-start h-auto py-2 px-3 text-left"
                        aria-current={selectedEmployeeId === employee.id}
                        disabled={isEditing && selectedEmployeeId === employee.id}
                        >
                        <div className="flex flex-col">
                            <span className="font-medium">
                            {employee.first_name} {employee.last_name}
                            </span>
                            <span className="text-xs text-muted-foreground">
                            {employee.employee_number} - {employee.job_title || 'N/A'}
                            </span>
                        </div>
                        </Button>
                    ))}
                    {!isLoadingList && !isErrorList && employees?.length === 0 && (
                        <p className="text-sm text-muted-foreground p-4 text-center">
                            No employees found.
                        </p>
                    )}
                    </div>
                </ScrollArea>
                </CardContent>
            </Card>
        }
        rightPaneContent={
            <Card className="flex flex-col h-full">
                <CardHeader className="p-6 flex flex-row items-center justify-between">
                <CardTitle className="text-lg">
                    {isEditing ? `Editing: ${employeeFormData?.first_name || ''} ${employeeFormData?.last_name || ''}` : 'Employee Details'}
                </CardTitle>
                <div className="flex items-center gap-2">
                    {!isEditing && selectedEmployeeId && (
                        <Button variant="outline" size="sm" onClick={handleEdit} disabled={isLoadingDetail}>
                            <Edit className="mr-2 h-4 w-4" />
                            Edit
                        </Button>
                    )}
                    {isEditing && (
                        <>
                            <Button variant="outline" size="sm" onClick={handleCancelEdit} disabled={updateMutation.isPending}>
                                <X className="mr-2 h-4 w-4" />
                                Cancel
                            </Button>
                            <Button size="sm" onClick={handleSave} disabled={updateMutation.isPending}>
                                {updateMutation.isPending ? (
                                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</>
                                ) : (
                                    <><Save className="mr-2 h-4 w-4" />Save</>
                                )}
                            </Button>
                        </>
                    )}
                    {!isEditing && isFetchingDetail && !isLoadingDetail && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
                </div>
            </CardHeader>
            <CardContent className="flex-grow overflow-y-auto p-0">
                <ScrollArea className="h-full">
                <div className="p-6">
                    {!selectedEmployeeId && !isEditing && (
                    <div className="flex items-center justify-center h-full min-h-[200px]">
                        <p className="text-muted-foreground">
                        {t('select_employee_details') || 'Select an employee to view details'}
                        </p>
                    </div>
                    )}
                    {selectedEmployeeId && isLoadingDetail && !isEditing && (
                        <div className="space-y-4 mt-4">
                        <Skeleton className="h-8 w-1/2" />
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-4 w-1/2" />
                        <Separator className="my-4" />
                        <Skeleton className="h-4 w-1/4" />
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-1/4" />
                        <Skeleton className="h-4 w-full" />
                        </div>
                    )}
                    {selectedEmployeeId && isErrorDetail && !isEditing && (
                        <Alert variant="destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertTitle>Error Loading Details</AlertTitle>
                            <AlertDescription>
                            {(errorDetail as Error)?.message || "Failed to load employee details."}
                            </AlertDescription>
                        </Alert>
                    )}

                    {displayEmployee && (
                        isEditing ? (
                            <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <Label htmlFor="first_name">First Name <span className="text-red-500">*</span></Label>
                                        <Input id="first_name" name="first_name" value={employeeFormData?.first_name || ''} onChange={handleFormChange} required disabled={updateMutation.isPending} />
                                    </div>
                                    <div className="space-y-1">
                                        <Label htmlFor="last_name">Last Name <span className="text-red-500">*</span></Label>
                                        <Input id="last_name" name="last_name" value={employeeFormData?.last_name || ''} onChange={handleFormChange} required disabled={updateMutation.isPending} />
                                    </div>
                                </div>
                                <div className="space-y-1">
                                    <Label htmlFor="job_title">Job Title</Label>
                                    <Input id="job_title" name="job_title" value={employeeFormData?.job_title || ''} onChange={handleFormChange} disabled={updateMutation.isPending} />
                                </div>
                                <div className="space-y-1">
                                    <Label htmlFor="email">Email</Label>
                                    <Input id="email" name="email" type="email" value={employeeFormData?.email || ''} onChange={handleFormChange} disabled={updateMutation.isPending} />
                                </div>
                                <div className="space-y-1">
                                    <Label htmlFor="phone_number">Phone</Label>
                                    <Input id="phone_number" name="phone_number" value={employeeFormData?.phone_number || ''} onChange={handleFormChange} disabled={updateMutation.isPending} />
                                </div>
                                <div className="space-y-1">
                                    <Label htmlFor="address">Address</Label>
                                    <Textarea id="address" name="address" value={employeeFormData?.address || ''} onChange={handleFormChange} disabled={updateMutation.isPending} />
                                </div>
                                <Separator className="my-4" />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-1">
                                        <Label htmlFor="department">Department</Label>
                                        <Input id="department" name="department" value={employeeFormData?.department || ''} onChange={handleFormChange} disabled={updateMutation.isPending} />
                                    </div>
                                    <div className="space-y-1">
                                        <Label htmlFor="employee_number">Employee Number</Label>
                                        <Input id="employee_number" name="employee_number" value={displayEmployee.employee_number || '-'} disabled={true} readOnly className="text-muted-foreground" />
                                    </div>
                                    <div className="space-y-1">
                                        <Label htmlFor="date_hired">Date Hired</Label>
                                        <Input id="date_hired" name="date_hired" type="date" value={employeeFormData?.date_hired || ''} onChange={handleFormChange} disabled={updateMutation.isPending} />
                                    </div>
                                    <div className="space-y-1">
                                        <Label htmlFor="date_of_birth">Date of Birth</Label>
                                        <Input id="date_of_birth" name="date_of_birth" type="date" value={employeeFormData?.date_of_birth || ''} onChange={handleFormChange} disabled={updateMutation.isPending} />
                                    </div>
                                </div>
                                {/* --- Add User Select Dropdown --- */}
                                <Separator className="my-4" />
                                <div className="space-y-1">
                                    <Label htmlFor="user">Associated User Account</Label>
                                    <Select
                                        value={employeeFormData?.user?.toString() ?? 'null'}
                                        onValueChange={handleUserChange}
                                        disabled={updateMutation.isPending || isLoadingUsers}
                                    >
                                        <SelectTrigger id="user">
                                            <SelectValue placeholder="Select user..." />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="null">-- Unassigned --</SelectItem>
                                            {isLoadingUsers && <SelectItem value="loading" disabled>Loading...</SelectItem>}
                                            {!isLoadingUsers && users.map(user => (
                                                <SelectItem key={user.id} value={user.id.toString()}>
                                                    {user.first_name} {user.last_name} ({user.username})
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                {/* --- End User Select Dropdown --- */}
                            </form>
                        ) : (
                            <dl>
                                <div className="flex items-center space-x-4 mb-6">
                                    <Avatar className="h-16 w-16">
                                        <AvatarImage src={undefined} alt={`${displayEmployee.first_name} ${displayEmployee.last_name}`} />
                                        <AvatarFallback>
                                        {displayEmployee.first_name?.charAt(0).toUpperCase()}
                                        {displayEmployee.last_name?.charAt(0).toUpperCase()}
                                        </AvatarFallback>
                                    </Avatar>
                                    <div>
                                        <h3 className="text-xl font-semibold">{displayEmployee.first_name} {displayEmployee.last_name}</h3>
                                        <p className="text-sm text-muted-foreground">{displayEmployee.job_title || '-'}</p>
                                    </div>
                                </div>
                                <Separator className="my-4" />
                                <Card>
                                    <CardHeader><CardTitle>Contact Information</CardTitle></CardHeader>
                                    <CardContent>
                                        <DetailItem label="Email" value={displayEmployee.email} />
                                        <DetailItem label="Phone" value={displayEmployee.phone_number} />
                                        <DetailItem label="Address" value={displayEmployee.address} />
                                    </CardContent>
                                </Card>
                                <Separator className="my-4" />
                                <Card>
                                    <CardHeader><CardTitle>Employment Details</CardTitle></CardHeader>
                                    <CardContent>
                                        <DetailItem label="Employee Number" value={displayEmployee.employee_number} />
                                        <DetailItem label="Department" value={displayEmployee.department} />
                                        <DetailItem label="Date Hired" value={formatDate(displayEmployee.date_hired)} />
                                        <DetailItem label="Date of Birth" value={formatDate(displayEmployee.date_of_birth)} />
                                    </CardContent>
                                </Card>

                                {/* Display Assigned User Information */}
                                <Separator className="my-4" />
                                <Card>
                                    <CardHeader><CardTitle>User Account</CardTitle></CardHeader>
                                    <CardContent>
                                        {displayEmployee.user ? (
                                            // Find the user in the users array
                                            (() => {
                                                const assignedUser = users.find(u => u.id === displayEmployee.user);
                                                if (assignedUser) {
                                                    return (
                                                        <>
                                                            <DetailItem label="Username" value={assignedUser.username} />
                                                            <DetailItem label="Name" value={`${assignedUser.first_name} ${assignedUser.last_name}`.trim()} />
                                                            <DetailItem label="Email" value={assignedUser.email} />
                                                        </>
                                                    );
                                                } else {
                                                    // User ID exists but not found in the list (could be loading)
                                                    return isLoadingUsers ? (
                                                        <div className="flex items-center py-2">
                                                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                            <span className="text-sm">Loading user details...</span>
                                                        </div>
                                                    ) : (
                                                        <DetailItem label="User ID" value={`${displayEmployee.user} (User details not available)`} />
                                                    );
                                                }
                                            })()
                                        ) : (
                                            <DetailItem label="User Account" value="No user account associated" />
                                        )}
                                    </CardContent>
                                </Card>
                            </dl>
                        )
                    )}

                </div>
                </ScrollArea>
            </CardContent>
        </Card>
        }
      />
    </div>
  ) 
} 