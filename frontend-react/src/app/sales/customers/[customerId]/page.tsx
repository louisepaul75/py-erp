"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Customer } from "@/types/sales-types";
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";
import { formatDate } from "@/lib/utils"; // Assuming formatDate exists
import { cn } from "@/lib/utils"; // For class merging

// UI Components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton"; // For loading state
import CustomerDocumentsTable from "@/components/customers/customer-documents-table";

// Icons
import {
  ArrowLeft,
  Edit,
  Mail,
  Phone,
  Plus,
  Globe,
  CreditCard,
  Percent,
  Truck,
  StickyNote, // Added for notes
  Users,      // Added for contacts
  FileText,   // Added for documents
} from "lucide-react";

// Basic currency formatter (can be moved to utils if needed)
const formatCurrency = (value: number | undefined | null) => {
    if (value == null) return '-';
    return new Intl.NumberFormat("default", { // Use locale from user settings if available
      style: "currency",
      currency: "EUR", // Use currency from user settings or config
      minimumFractionDigits: 2,
    }).format(value);
};

// Helper to get initials
const getInitials = (firstName?: string, lastName?: string, companyName?: string, isCompany?: boolean): string => {
    if (isCompany) {
        return (companyName || 'Co').substring(0, 2).toUpperCase();
    }
    const first = (firstName || '').charAt(0);
    const last = (lastName || '').charAt(0);
    return `${first}${last}`.toUpperCase() || '??';
};


export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const customerId = params.customerId as string; // Assuming ID is always a string from URL

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!customerId) {
        setError("Customer ID is missing.");
        setIsLoading(false);
        return;
    }

    const fetchCustomerDetails = async () => {
      setIsLoading(true);
      setError(null);
      setCustomer(null);

      try {
        const token = await authService.getToken();
        if (!token) {
          throw new Error("Authentication required.");
        }

        // Construct the endpoint URL for a single customer
        const customerEndpoint = `${API_URL}/sales/customers/${customerId}/`;

        const response = await fetch(customerEndpoint, {
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
           if (response.status === 401) {
             throw new Error('Authentication failed.');
           } else if (response.status === 403) {
              throw new Error('Permission denied.');
           } else if (response.status === 404) {
               throw new Error('Customer not found.');
           }
          throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        const data: Customer = await response.json();
        setCustomer(data);

      } catch (err) {
        console.error("Error fetching customer details:", err);
        setError(err instanceof Error ? err.message : "Failed to load customer details");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomerDetails();
  }, [customerId]); // Re-run effect if customerId changes

  // Loading State
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 space-y-6">
        {/* Header Skeleton */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4">
                <Skeleton className="h-12 w-12 rounded-full" />
                <div className="space-y-2">
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-32" />
                </div>
            </div>
            <div className="flex gap-2">
                <Skeleton className="h-9 w-24" />
                <Skeleton className="h-9 w-24" />
                <Skeleton className="h-9 w-24" />
            </div>
        </div>
        {/* Body Skeleton */}
        <div className="grid gap-6 md:grid-cols-3">
            <div className="md:col-span-2 space-y-6">
                <Skeleton className="h-40 w-full" />
                <Skeleton className="h-64 w-full" />
            </div>
            <div className="space-y-6">
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-48 w-full" />
            </div>
        </div>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
        <div className="container mx-auto px-4 py-8">
            <Button variant="outline" size="sm" onClick={() => router.back()} className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" /> Back to List
            </Button>
            <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
            </Alert>
      </div>
    );
  }

  // No Customer Found State
  if (!customer) {
      return (
          <div className="container mx-auto px-4 py-8 text-center">
                <p>Customer data could not be loaded.</p>
                <Button variant="outline" size="sm" onClick={() => router.back()} className="mt-4">
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back to List
                </Button>
          </div>
      );
  }


  // Determine display name and initials
  const individualName = `${customer.firstName || ""} ${customer.lastName || ""}`.trim();
  const customerName = customer.isCompany
    ? customer.companyName || "Unknown Company"
    : individualName || customer.name || "Unknown Customer"; // Use name as fallback
  const initials = getInitials(customer.firstName, customer.lastName, customer.companyName, customer.isCompany);

  return (
    <div className="container mx-auto px-4 py-8 flex flex-col gap-6">
      {/* Header with navigation and actions */}
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        {/* Left side: Avatar, Name, Since */}
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => router.back()} className="hidden md:flex">
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">Back</span>
          </Button>
          <Avatar className="h-16 w-16 border">
            <AvatarImage src={customer.avatar || undefined} alt={customerName} />
            <AvatarFallback>{initials}</AvatarFallback>
          </Avatar>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight md:text-3xl">{customerName}</h1>
              {customer.isCompany ? (
                <Badge variant="secondary">Company</Badge>
              ) : (
                <Badge variant="secondary">Individual</Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
                Customer since {formatDate(customer.since)} <span className="hidden sm:inline">• ID: {customer.customer_number}</span>
            </p>
          </div>
        </div>
        {/* Right side: Action Buttons */}
        <div className="flex flex-wrap items-start gap-2">
           {/* Placeholder Buttons */}
           <Button variant="outline" size="sm" disabled>
                <Mail className="mr-2 h-4 w-4" /> Email
           </Button>
           <Button variant="outline" size="sm" disabled>
                <Phone className="mr-2 h-4 w-4" /> Call
           </Button>
           {/* Functional Buttons */}
           <Button variant="outline" size="sm" asChild>
             <Link href={`/sales/customers/${customerId}/edit`}>
               <Edit className="mr-2 h-4 w-4" /> Edit
             </Link>
           </Button>
           <Button size="sm" asChild>
             <Link href={`/sales/orders/new?customerId=${customerId}`}> {/* Adjust link as needed */}
               <Plus className="mr-2 h-4 w-4" /> New Order
             </Link>
           </Button>
        </div>
      </div>

      {/* Customer content grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3 lg:gap-8">
        {/* Main content - 2/3 width on lg screens */}
        <div className="lg:col-span-2 space-y-6">
          {/* Customer Summary Card */}
          <Card>
            <CardHeader>
              <CardTitle>Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Total Orders</p>
                  <p className="text-2xl font-bold">{customer.orderCount ?? '-'}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Total Spent</p>
                  <p className="text-2xl font-bold">{formatCurrency(customer.totalSpent)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Last Order</p>
                  <p className="text-lg font-semibold">
                    {customer.lastOrderDate ? formatDate(customer.lastOrderDate) : "Never"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tabs for Documents, Contacts, etc. */}
          <Tabs defaultValue="documents" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-4"> {/* Adjust cols based on tabs */}
              <TabsTrigger value="documents">
                  <FileText className="mr-2 h-4 w-4"/> Documents
              </TabsTrigger>
              <TabsTrigger value="contacts">
                  <Users className="mr-2 h-4 w-4"/> Contacts
              </TabsTrigger>
              <TabsTrigger value="notes">
                  <StickyNote className="mr-2 h-4 w-4"/> Notes
              </TabsTrigger>
            </TabsList>

            {/* Documents Tab */}
            <TabsContent value="documents">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Recent Documents</CardTitle>
                  {/* TODO: Add button to view all documents */}
                </CardHeader>
                <CardContent>
                   {/* Render the CustomerDocumentsTable component */}
                   <CustomerDocumentsTable customerId={customerId} />
                </CardContent>
              </Card>
            </TabsContent>

            {/* Contacts Tab */}
            <TabsContent value="contacts">
              <Card>
                 <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Contact Persons & Details</CardTitle>
                    {/* TODO: Add button to add new contact */}
                 </CardHeader>
                 <CardContent>
                    {/* Placeholder: Replace with actual contact components */}
                    <div className="text-center text-muted-foreground py-8">
                        Contact persons/details component will go here.
                    </div>
                    {/* <CustomerContactPersonsCard customerId={customerId} /> */}
                    {/* <CustomerContactInfosCard customerId={customerId} /> */}
                 </CardContent>
              </Card>
            </TabsContent>

             {/* Notes Tab */}
            <TabsContent value="notes">
               <Card>
                 <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle>Notes</CardTitle>
                    {/* TODO: Add button to add new note */}
                 </CardHeader>
                 <CardContent>
                     {/* Placeholder: Replace with actual notes component */}
                    <div className="text-center text-muted-foreground py-8">
                         Notes component will go here.
                    </div>
                     {/* <CustomerNotesCard customerId={customerId} printableNotes={customer.printableNotes} internalNotes={customer.internalNotes} /> */}
                 </CardContent>
               </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar - 1/3 width on lg screens */}
        <div className="lg:col-span-1 space-y-6">
          {/* Contact Information Card */}
          <Card>
            <CardHeader>
              <CardTitle>Contact Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {customer.emailMain && (
                <div className="flex items-center gap-3">
                  <Mail className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <a href={`mailto:${customer.emailMain}`} className="text-sm hover:underline truncate">
                    {customer.emailMain}
                  </a>
                </div>
              )}
              {customer.phoneMain && (
                <div className="flex items-center gap-3">
                  <Phone className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <a href={`tel:${customer.phoneMain}`} className="text-sm hover:underline truncate">
                    {customer.phoneMain}
                  </a>
                </div>
              )}
              {customer.isCompany && customer.vat_id && (
                 <>
                    <Separator />
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium w-16">VAT ID:</span>
                      <span className="text-sm text-muted-foreground">{customer.vat_id}</span>
                    </div>
                 </>
              )}
            </CardContent>
          </Card>

          {/* Billing Address Card */}
          <Card>
            <CardHeader>
              <CardTitle>Billing Address</CardTitle>
              {/* TODO: Add Edit Address button */}
            </CardHeader>
            <CardContent>
              <div className="space-y-1 text-sm text-muted-foreground">
                {customer.billingStreet && <p>{customer.billingStreet}</p>}
                {customer.billingPostalCode && customer.billingCity && <p>{`${customer.billingPostalCode} ${customer.billingCity}`}</p>}
                {customer.billingCountry && <p>{customer.billingCountry}</p>}
                {!customer.billingStreet && !customer.billingCity && !customer.billingCountry && <p>No billing address available.</p>}
              </div>
            </CardContent>
          </Card>

          {/* Payment Information Card */}
          <Card>
            <CardHeader>
              <CardTitle>Payment Details</CardTitle>
               {/* TODO: Add Edit Payment button */}
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
               {customer.paymentTermsOverall && (
                  <div className="flex justify-between">
                      <span className="text-muted-foreground">Payment Term:</span>
                      <span className="font-medium text-right">{customer.paymentTermsOverall}</span>
                  </div>
               )}
                {customer.discount !== null && customer.discount > 0 && (
                  <div className="flex justify-between">
                      <span className="text-muted-foreground flex items-center"><Percent className="h-4 w-4 mr-1" /> Discount:</span>
                      <span className="font-medium">{customer.discount}%</span>
                  </div>
                )}
                {customer.creditLimit !== null && (
                     <div className="flex justify-between">
                        <span className="text-muted-foreground">Credit Limit:</span>
                        <span className="font-medium">{formatCurrency(customer.creditLimit)}</span>
                    </div>
                )}
                {!customer.paymentTermsOverall && customer.discount === null && customer.creditLimit === null && (
                    <p className="text-center text-muted-foreground">No payment details available.</p>
                )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 