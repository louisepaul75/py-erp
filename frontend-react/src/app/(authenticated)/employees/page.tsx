'use client'

import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { format, parseISO } from 'date-fns'

import {
  // ResizableHandle, // Removed
  // ResizablePanel, // Removed
  // ResizablePanelGroup, // Removed
} from "@/components/ui/resizable" // Keep if other exports are used, remove otherwise if empty
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, Loader2, Edit } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

import { fetchEmployees, fetchEmployeeById, type Employee } from '@/lib/api/employees'

// Helper to display data or a placeholder
const DetailItem = ({ label, value }: { label: string; value: string | null | undefined }) => (
  <div className="grid grid-cols-3 gap-4 py-2">
    <dt className="text-sm font-medium text-muted-foreground">{label}</dt>
    <dd className="text-sm col-span-2">{value || '-'}</dd>
  </div>
);

export default function EmployeesPage() {
  const { t } = useTranslation(['common']);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null);

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

  // Query for fetching the details of the selected employee
  const { 
    data: selectedEmployee,
    isLoading: isLoadingDetail,
    isFetching: isFetchingDetail, // Use isFetching for background refresh indicators
    isError: isErrorDetail,
    error: errorDetail
  } = useQuery<Employee>({ 
    queryKey: ['employee', selectedEmployeeId], 
    queryFn: () => fetchEmployeeById(selectedEmployeeId!), // Assert non-null as it's enabled only when ID exists
    enabled: !!selectedEmployeeId, // Only run query if an ID is selected
    // Optional: Add staleTime/cacheTime if desired
  });

  // Helper to format dates
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    try {
      return format(parseISO(dateString), 'PPP'); // e.g., Jan 1, 2023
    } catch (e) {
      return 'Invalid Date';
    }
  }

  return (
    // Add an outer div with padding and increased calculated height subtraction
    <div className="p-4 h-[calc(100vh-8rem)]"> 
      {/* Updated main container to match ProductsView structure */}
      <div className="flex flex-col md:flex-row gap-4 h-full">
        {/* Left Pane: Wrapped in Card */}
        <Card className="w-full md:w-1/3 flex flex-col">
          <CardHeader className="p-4"> {/* Use CardHeader */}
            <CardTitle className="text-lg">{t('navigation.employees')}</CardTitle> {/* Use CardTitle */}
            {/* TODO: Add Search/Filter controls here */}
          </CardHeader>
          {/* Use CardContent for scrollable area */}
          <CardContent className="flex-grow overflow-y-auto p-0"> {/* Remove padding from CardContent if ScrollArea handles it */}
            <ScrollArea className="h-full"> {/* Ensure ScrollArea fills CardContent */}
              <div className="p-4 space-y-2"> {/* Keep padding inside ScrollArea */}
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
                    onClick={() => setSelectedEmployeeId(employee.id)}
                    className="w-full justify-start h-auto py-2 px-3 text-left"
                    aria-current={selectedEmployeeId === employee.id}
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
        </Card> {/* End Left Pane Card */}

        {/* Right Pane: Wrapped in Card */}
        <Card className="w-full md:w-2/3 flex flex-col">
           <CardHeader className="p-6 flex flex-row items-center justify-between"> {/* Use CardHeader, keep flex for spinner */}
             <CardTitle className="text-lg">Employee Details</CardTitle> {/* Use CardTitle */}
             {/* Container for buttons and spinner */}
             <div className="flex items-center gap-2">
               {/* Edit Button - Visible only when an employee is selected */}
               {selectedEmployeeId && (
                 <Button
                   variant="outline"
                   size="sm"
                   onClick={() => { /* TODO: Implement edit functionality */ }}
                   // disabled={isLoadingDetail || isFetchingDetail} // Optional: Disable while loading/fetching
                 >
                   <Edit className="mr-2 h-4 w-4" />
                   Edit
                 </Button>
               )}
               {/* Show a subtle loading spinner during background refetches */}
               {isFetchingDetail && !isLoadingDetail && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
             </div>
           </CardHeader>
           {/* Use CardContent for scrollable area */}
          <CardContent className="flex-grow overflow-y-auto p-0"> {/* Remove padding from CardContent */}
            <ScrollArea className="h-full"> {/* Ensure ScrollArea fills CardContent */}
              <div className="p-6"> {/* Keep padding inside ScrollArea */}
                {!selectedEmployeeId && (
                  <div className="flex items-center justify-center h-full min-h-[200px]">
                    <p className="text-muted-foreground">
                      {t('select_employee_details') || 'Select an employee to view details'}
                    </p>
                  </div>
                )}

                {selectedEmployeeId && isLoadingDetail && (
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

                {selectedEmployeeId && isErrorDetail && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error Loading Details</AlertTitle>
                    <AlertDescription>
                      {(errorDetail as Error)?.message || "Failed to load employee details."}
                    </AlertDescription>
                  </Alert>
                )}

                {selectedEmployeeId && !isLoadingDetail && !isErrorDetail && selectedEmployee && (
                  <dl>
                    <div className="flex items-center space-x-4 mb-6">
                       <Avatar className="h-16 w-16">
                          {/* TODO: Add actual avatar URL if available */}
                          <AvatarImage src={undefined} alt={`${selectedEmployee.first_name} ${selectedEmployee.last_name}`} />
                          <AvatarFallback>
                            {selectedEmployee.first_name?.charAt(0).toUpperCase()}
                            {selectedEmployee.last_name?.charAt(0).toUpperCase()}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <h3 className="text-xl font-semibold">{selectedEmployee.first_name} {selectedEmployee.last_name}</h3>
                          <p className="text-sm text-muted-foreground">{selectedEmployee.job_title || '-'}</p>
                        </div>
                    </div>

                    <Separator className="my-4" />

                    <Card>
                      <CardHeader>
                        <CardTitle>Contact Information</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <DetailItem label="Email" value={selectedEmployee.email} />
                        <DetailItem label="Phone" value={selectedEmployee.phone_number} />
                        <DetailItem label="Address" value={selectedEmployee.address} />
                      </CardContent>
                    </Card>

                    <Separator className="my-4" />

                    <Card>
                      <CardHeader>
                         <CardTitle>Employment Details</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <DetailItem label="Employee Number" value={selectedEmployee.employee_number} />
                        <DetailItem label="Department" value={selectedEmployee.department} />
                        <DetailItem label="Date Hired" value={formatDate(selectedEmployee.date_hired)} />
                        <DetailItem label="Date of Birth" value={formatDate(selectedEmployee.date_of_birth)} />
                         {/* TODO: Add related User info if needed */}
                        {/* <DetailItem label="System User" value={selectedEmployee.user?.username} /> */}
                      </CardContent>
                    </Card>
                  </dl>
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card> {/* End Right Pane Card */}
      </div> // End flex container
    </div> // End outer padding div
  )
} 