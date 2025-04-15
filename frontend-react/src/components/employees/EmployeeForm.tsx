'use client'

import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { format, parseISO } from 'date-fns';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Save, X } from "lucide-react";
import type { Employee, EmployeeUpdateData } from '@/lib/api/employees';
import type { UserSummary } from '@/lib/api/users';

// Define type for form data locally within the form component
// This might differ slightly from the main Employee type if needed for form handling
type EmployeeFormData = {
  first_name: string;
  last_name: string;
  email: string | null;
  phone_number: string | null;
  address: string | null;
  department: string | null;
  job_title: string | null;
  employee_number: string | null; // Keep for display, but maybe not editable
  date_hired: string; // Use string for input type='date'
  date_of_birth: string; // Use string for input type='date'
  user: number | null; 
}; 

// Helper function to initialize form data from the employee prop
const initializeFormData = (employee: Employee): EmployeeFormData => ({
  first_name: employee.first_name || '',
  last_name: employee.last_name || '',
  email: employee.email || '',
  phone_number: employee.phone_number || '',
  address: employee.address || '',
  department: employee.department || '',
  job_title: employee.job_title || '',
  employee_number: employee.employee_number || '-', // Display existing number
  date_hired: employee.date_hired ? format(parseISO(employee.date_hired), 'yyyy-MM-dd') : '',
  date_of_birth: employee.date_of_birth ? format(parseISO(employee.date_of_birth), 'yyyy-MM-dd') : '',
  user: employee.user,
});

interface EmployeeFormProps {
  initialData: Employee;
  users: UserSummary[];
  isLoadingUsers: boolean;
  isSaving: boolean;
  onSave: (formData: EmployeeUpdateData) => void;
  onCancel: () => void;
}

const EmployeeForm: React.FC<EmployeeFormProps> = ({
  initialData,
  users,
  isLoadingUsers,
  isSaving,
  onSave,
  onCancel,
}) => {
  const { t } = useTranslation(['common']);
  const [formData, setFormData] = useState<EmployeeFormData>(() => initializeFormData(initialData));

  // Update form data if the initialData prop changes (e.g., after a save and re-fetch)
  useEffect(() => {
    setFormData(initializeFormData(initialData));
  }, [initialData]);

  const handleFormChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }, []);

  const handleUserChange = useCallback((value: string) => {
    const userId = value === 'null' ? null : parseInt(value, 10);
    // Ensure NaN is treated as null if parseInt fails unexpectedly
    setFormData(prev => ({ ...prev, user: isNaN(userId) ? null : userId }));
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Prepare data for saving, potentially converting types or omitting fields
    const saveData: EmployeeUpdateData = {
      ...formData,
      // Ensure dates are in correct format or null/undefined if empty
      date_hired: formData.date_hired || undefined, // API might expect undefined or null
      date_of_birth: formData.date_of_birth || null, // API might expect null
      // Omit employee_number if it's not meant to be updated
      employee_number: undefined, 
      // Ensure user is number | null
      user: formData.user,
    };
    onSave(saveData);
  };

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="p-6 flex flex-row items-center justify-between">
        <CardTitle className="text-lg">
            {t('editing_employee', { name: `${formData.first_name} ${formData.last_name}`.trim() })} {/* Placeholder key */} 
        </CardTitle>
        <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={onCancel} disabled={isSaving}>
                <X className="mr-2 h-4 w-4" />
                {t('cancel')} {/* Placeholder key */} 
            </Button>
            {/* Link button type to form submission */}
            <Button size="sm" onClick={handleSubmit} disabled={isSaving} type="submit" form="employee-form">
                {isSaving ? (
                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{t('saving')}</> /* Placeholder key */ 
                ) : (
                    <><Save className="mr-2 h-4 w-4" />{t('save')}</> /* Placeholder key */ 
                )}
            </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto p-0">
        <ScrollArea className="h-full">
          {/* Use form tag and link submit button via form id */}
          <form id="employee-form" className="p-6 space-y-4" onSubmit={handleSubmit}> 
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                      <Label htmlFor="first_name">{t('first_name')} <span className="text-red-500">*</span></Label> {/* Placeholder key */} 
                      <Input id="first_name" name="first_name" value={formData.first_name} onChange={handleFormChange} required disabled={isSaving} />
                  </div>
                  <div className="space-y-1">
                      <Label htmlFor="last_name">{t('last_name')} <span className="text-red-500">*</span></Label> {/* Placeholder key */} 
                      <Input id="last_name" name="last_name" value={formData.last_name} onChange={handleFormChange} required disabled={isSaving} />
                  </div>
              </div>
              <div className="space-y-1">
                  <Label htmlFor="job_title">{t('job_title')}</Label> {/* Placeholder key */} 
                  <Input id="job_title" name="job_title" value={formData.job_title || ''} onChange={handleFormChange} disabled={isSaving} />
              </div>
              <div className="space-y-1">
                  <Label htmlFor="email">{t('email')}</Label> {/* Placeholder key */} 
                  <Input id="email" name="email" type="email" value={formData.email || ''} onChange={handleFormChange} disabled={isSaving} />
              </div>
              <div className="space-y-1">
                  <Label htmlFor="phone_number">{t('phone')}</Label> {/* Placeholder key */} 
                  <Input id="phone_number" name="phone_number" value={formData.phone_number || ''} onChange={handleFormChange} disabled={isSaving} />
              </div>
              <div className="space-y-1">
                  <Label htmlFor="address">{t('address')}</Label> {/* Placeholder key */} 
                  <Textarea id="address" name="address" value={formData.address || ''} onChange={handleFormChange} disabled={isSaving} />
              </div>
              <Separator className="my-4" />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                      <Label htmlFor="department">{t('department')}</Label> {/* Placeholder key */} 
                      <Input id="department" name="department" value={formData.department || ''} onChange={handleFormChange} disabled={isSaving} />
                  </div>
                  <div className="space-y-1">
                      <Label htmlFor="employee_number">{t('employee_number')}</Label> {/* Placeholder key */} 
                      {/* Make employee number read-only */}
                      <Input id="employee_number" name="employee_number" value={formData.employee_number || '-'} disabled={true} readOnly className="text-muted-foreground bg-muted" />
                  </div>
                  <div className="space-y-1">
                      <Label htmlFor="date_hired">{t('date_hired')}</Label> {/* Placeholder key */} 
                      <Input id="date_hired" name="date_hired" type="date" value={formData.date_hired} onChange={handleFormChange} disabled={isSaving} />
                  </div>
                  <div className="space-y-1">
                      <Label htmlFor="date_of_birth">{t('date_of_birth')}</Label> {/* Placeholder key */} 
                      <Input id="date_of_birth" name="date_of_birth" type="date" value={formData.date_of_birth} onChange={handleFormChange} disabled={isSaving} />
                  </div>
              </div>
              <Separator className="my-4" />
              <div className="space-y-1">
                  <Label htmlFor="user">{t('associated_user_account')}</Label> {/* Placeholder key */} 
                  <Select
                      value={formData.user?.toString() ?? 'null'}
                      onValueChange={handleUserChange}
                      disabled={isSaving || isLoadingUsers}
                  >
                      <SelectTrigger id="user">
                          <SelectValue placeholder={t('select_user_placeholder')} /> {/* Placeholder key */} 
                      </SelectTrigger>
                      <SelectContent>
                          <SelectItem value="null">-- {t('unassigned')} --</SelectItem> {/* Placeholder key */} 
                          {isLoadingUsers && <SelectItem value="loading" disabled>{t('loading_ellipsis')}</SelectItem>} {/* Placeholder key */} 
                          {!isLoadingUsers && users.map(user => (
                              <SelectItem key={user.id} value={user.id.toString()}>
                                  {user.first_name} {user.last_name} ({user.username})
                              </SelectItem>
                          ))}
                      </SelectContent>
                  </Select>
              </div>
          </form>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default EmployeeForm; 