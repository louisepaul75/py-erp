"use client";

import React, { useState, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  PlusCircle,
  AlertCircle,
  Search,
  ArrowUpDown,
  X,
  ChevronLeft,
  ChevronRight,
  Filter,
} from "lucide-react";
import type { Employee } from "@/lib/api/employees";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { useEmployeesTable } from "@/hooks/useEmployeesTable";
import EmployeeFilterDialog, { EmployeeFilters } from "./employee-filter-dialog";

interface EmployeeListProps {
  employees: Employee[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  selectedEmployeeId: number | null;
  isEditing: boolean; // To disable selection while parent is in edit mode
  onSelectItem: (id: number) => void;
}

// Default filters
const initialFilters: EmployeeFilters = {
  isActive: null,
  isTerminated: null,
  employmentStatus: "all",
};

const EmployeeList: React.FC<EmployeeListProps> = ({
  employees,
  isLoading,
  isError,
  error,
  selectedEmployeeId,
  isEditing,
  onSelectItem,
}) => {
  const { t } = useTranslation(["common"]);
  const [isFilterDialogOpen, setIsFilterDialogOpen] = useState(false);

  // Use the employees table hook
  console.log("employees", employees);
  const {
    paginatedEmployees,
    sortConfig,
    requestSort,
    searchTerm,
    setSearchTerm,
    pagination,
    goToPage,
    goToNextPage,
    goToPreviousPage,
    filters,
    setFilters,
  } = useEmployeesTable({
    employees,
    isLoading,
    isError,
    error,
    searchableFields: [
      "employee_number",
      "first_name",
      "last_name",
      "email",
      "mobile_phone",
    ],
    initialFilters,
  });

  console.log("employees", employees);
  console.log("paginatedEmployees", paginatedEmployees);

  // Helper function to render sort indicator
  const renderSortIndicator = (key: keyof Employee) => {
    if (sortConfig.key === key) {
      return (
        <ArrowUpDown
          className={`ml-2 h-3 w-3 ${
            sortConfig.direction === "asc" ? "" : "rotate-180"
          }`}
        />
      );
    }
    return <ArrowUpDown className="ml-2 h-3 w-3 opacity-30" />;
  };

  const handleCreateEmployees = () => {
    console.log("Create new employee");
    //  router.push('/employees/new'); // Navigate to create page
  };

  // Handle filter changes
  const handleApplyFilters = useCallback((newFilters: EmployeeFilters) => {
    setFilters(newFilters);
  }, [setFilters]);

  // Determine if any filters are active
  const hasActiveFilters = filters && (
    filters.isActive !== null || 
    filters.isTerminated !== null || 
    filters.employmentStatus !== "all"
  );

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="p-4">
        <CardTitle className="text-lg">{t("navigation.employees")}</CardTitle>
        <div className="flex items-center justify-between mt-2 space-x-2">
          <div className="relative flex-grow">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              type="search"
              placeholder={t("search_employees")}
              className="pl-10 h-9"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              disabled={isLoading || isEditing}
            />
            {searchTerm && (
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full text-muted-foreground hover:text-foreground"
                onClick={() => setSearchTerm("")}
                disabled={isLoading || isEditing}
              >
                <X className="h-3 w-3" />
              </Button>
            )}
          </div>
          <Button
            variant={hasActiveFilters ? "default" : "outline"}
            size="icon"
            aria-label="Filter Employees"
            onClick={() => setIsFilterDialogOpen(true)}
            disabled={isLoading || isEditing}
            title={hasActiveFilters ? "Filters active" : "Filter employees"}
          >
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-grow overflow-hidden p-0">
        {isLoading && (
          <div className="p-4 space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        )}
        {isError && (
          <Alert variant="destructive" className="m-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>{t("error")}</AlertTitle>
            <AlertDescription>
              {error?.message || t("failed_load_employees")}
            </AlertDescription>
          </Alert>
        )}
        {!isLoading && !isError && (
          <div className="flex-1 overflow-y-auto h-full">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>
                    <Button
                      variant="ghost"
                      onClick={() => requestSort("employee_number")}
                      className="px-0 hover:bg-transparent"
                    >
                      {t("employee_number")}
                      {renderSortIndicator("employee_number")}
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button
                      variant="ghost"
                      onClick={() => requestSort("legacy_id")}
                      className="px-0 hover:bg-transparent"
                    >
                      {t("legacy_id")}
                      {renderSortIndicator("legacy_id")}
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button
                      variant="ghost"
                      onClick={() => requestSort("last_name")}
                      className="px-0 hover:bg-transparent"
                    >
                      {t("full_name")}
                      {renderSortIndicator("last_name")}
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button
                      variant="ghost"
                      onClick={() => requestSort("email")}
                      className="px-0 hover:bg-transparent"
                    >
                      {t("email")}
                      {renderSortIndicator("email")}
                    </Button>
                  </TableHead>
                  <TableHead>{t("mobile_phone")}</TableHead>
                  <TableHead>
                    <Button
                      variant="ghost"
                      onClick={() => requestSort("is_active")}
                      className="px-0 hover:bg-transparent"
                    >
                      {t("status")}
                      {renderSortIndicator("is_active")}
                    </Button>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paginatedEmployees.map((employee) => (
                  <TableRow
                    key={employee.id}
                    className={`cursor-pointer ${
                      selectedEmployeeId === employee.id ? "bg-muted" : ""
                    }`}
                    onClick={() => onSelectItem(employee.id)}
                  >
                    <TableCell>{employee.employee_number}</TableCell>
                    <TableCell>{employee.legacy_id || t("na")}</TableCell>
                    <TableCell>
                      <div className="font-medium">{`${employee.first_name} ${employee.last_name}`}</div>
                    </TableCell>
                    <TableCell>{employee.email || t("na")}</TableCell>
                    <TableCell>{employee.mobile_phone || t("na")}</TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                          employee.is_active
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {employee.is_active ? t("active") : t("inactive")}
                      </span>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {!isLoading && !isError && paginatedEmployees.length === 0 && (
              <p className="text-sm text-muted-foreground p-4 text-center">
                {t("no_employees_found")}
              </p>
            )}
          </div>
        )}
      </CardContent>
      {/* Add pagination controls */}
      {!isLoading && !isError && pagination.totalItems > 0 && (
        <div className="p-4 border-t flex justify-between items-center">
          <Button
            variant="outline"
            size="sm"
            onClick={goToPreviousPage}
            disabled={pagination.currentPage === 0 || isLoading || isEditing}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            {t("previous")}
          </Button>
          <span className="text-sm text-muted-foreground">
            {/* {t("page_of", {
              current: pagination.currentPage + 1,
              total: pagination.totalPages,
            })} */}
            Page {pagination.currentPage + 1 } of {pagination.totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={goToNextPage}
            disabled={
              pagination.currentPage >= pagination.totalPages - 1 ||
              isLoading ||
              isEditing
            }
          >
            {t("next")}
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}

      <div className="p-4 border-t flex-shrink-0">
        <Button className="w-full" onClick={handleCreateEmployees}>
          <PlusCircle className="mr-2 h-4 w-4" />
          New Employee
        </Button>
      </div>

      {/* Filter Dialog */}
      <EmployeeFilterDialog
        isOpen={isFilterDialogOpen}
        onClose={() => setIsFilterDialogOpen(false)}
        onApplyFilters={handleApplyFilters}
        initialFilters={filters || initialFilters}
      />
    </Card>
  );
};

export default EmployeeList;
