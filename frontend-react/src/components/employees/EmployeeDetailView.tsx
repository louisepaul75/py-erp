'use client'

import React from 'react';
import { useTranslation } from 'react-i18next';
import { format, parseISO } from 'date-fns';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Edit, Loader2 } from "lucide-react";
import type { Employee } from '@/lib/api/employees';
import type { UserSummary } from '@/lib/api/users';

// Helper to display data or a placeholder (kept local for now)
const DetailItem = ({ label, value }: { label: string; value: string | null | undefined }) => (
  <div className="grid grid-cols-3 gap-4 py-2">
    <dt className="text-sm font-medium text-muted-foreground">{label}</dt>
    <dd className="text-sm col-span-2">{value || '-'}</dd> {/* Use '-' as placeholder */}  
  </div>
);

// Helper to format dates (kept local for now)
const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return '-'; // Use '-' as placeholder
  try {
    return format(parseISO(dateString), 'PPP'); // e.g., Jan 1, 2023
  } catch (e) {
    console.error("Date parsing error:", e);
    return 'Invalid Date';
  }
}

interface EmployeeDetailViewProps {
  employee: Employee;
  users: UserSummary[];
  isLoadingUsers: boolean;
  isFetchingDetail: boolean; // To show subtle loading indicator on refetch
  onEdit: () => void;
}

const EmployeeDetailView: React.FC<EmployeeDetailViewProps> = ({
  employee,
  users,
  isLoadingUsers,
  isFetchingDetail,
  onEdit,
}) => {
  const { t } = useTranslation(['common']);

  // Find the assigned user details
  const assignedUser = employee.user ? users.find(u => u.id === employee.user) : null;

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="p-6 flex flex-row items-center justify-between">
        <CardTitle className="text-lg">{t('employee_details')}</CardTitle> {/* Placeholder key */}
        <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={onEdit}>
                <Edit className="mr-2 h-4 w-4" />
                {t('edit')} {/* Placeholder key */} 
            </Button>
           {isFetchingDetail && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto p-0">
        <ScrollArea className="h-full">
          <div className="p-6">
            <dl>
              {/* Basic Info Header */}            
              <div className="flex items-center space-x-4 mb-6">
                  <Avatar className="h-16 w-16">
                      {/* Add logic for actual image source if available */}
                      <AvatarImage src={undefined} alt={`${employee.first_name} ${employee.last_name}`} />
                      <AvatarFallback>
                      {employee.first_name?.charAt(0).toUpperCase()}
                      {employee.last_name?.charAt(0).toUpperCase()}
                      </AvatarFallback>
                  </Avatar>
                  <div>
                      <h3 className="text-xl font-semibold">{employee.first_name} {employee.last_name}</h3>
                      <p className="text-sm text-muted-foreground">{employee.job_title || '-'}</p>
                  </div>
              </div>
              <Separator className="my-4" />

              {/* Contact Information Card */}            
              <Card>
                  <CardHeader><CardTitle>{t('contact_information')}</CardTitle></CardHeader> {/* Placeholder key */} 
                  <CardContent>
                      <DetailItem label={t('email')} value={employee.email} /> {/* Placeholder key */} 
                      <DetailItem label={t('phone')} value={employee.phone_number} /> {/* Placeholder key */} 
                      <DetailItem label={t('address')} value={employee.address} /> {/* Placeholder key */} 
                  </CardContent>
              </Card>
              <Separator className="my-4" />

              {/* Employment Details Card */}            
              <Card>
                  <CardHeader><CardTitle>{t('employment_details')}</CardTitle></CardHeader> {/* Placeholder key */} 
                  <CardContent>
                      <DetailItem label={t('employee_number')} value={employee.employee_number} /> {/* Placeholder key */} 
                      <DetailItem label={t('department')} value={employee.department} /> {/* Placeholder key */} 
                      <DetailItem label={t('date_hired')} value={formatDate(employee.date_hired)} /> {/* Placeholder key */} 
                      <DetailItem label={t('date_of_birth')} value={formatDate(employee.date_of_birth)} /> {/* Placeholder key */} 
                  </CardContent>
              </Card>
              <Separator className="my-4" />

              {/* User Account Card */}            
              <Card>
                  <CardHeader><CardTitle>{t('user_account')}</CardTitle></CardHeader> {/* Placeholder key */} 
                  <CardContent>
                      {employee.user ? (
                          assignedUser ? (
                              <>
                                  <DetailItem label={t('username')} value={assignedUser.username} /> {/* Placeholder key */} 
                                  <DetailItem label={t('name')} value={`${assignedUser.first_name} ${assignedUser.last_name}`.trim()} /> {/* Placeholder key */} 
                                  <DetailItem label={t('email')} value={assignedUser.email} /> {/* Placeholder key */} 
                              </>
                          ) : isLoadingUsers ? (
                              <div className="flex items-center py-2">
                                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                  <span className="text-sm">{t('loading_user_details')}</span> {/* Placeholder key */} 
                              </div>
                          ) : (
                              <DetailItem label={t('user_id')} value={`${employee.user} (${t('user_details_not_available')})`} /> /* Placeholder keys */ 
                          )
                      ) : (
                          <DetailItem label={t('user_account')} value={t('no_user_associated')} /> /* Placeholder keys */ 
                      )}
                  </CardContent>
              </Card>
            </dl>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default EmployeeDetailView; 