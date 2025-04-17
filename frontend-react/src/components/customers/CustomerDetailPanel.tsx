"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation"; // Keep router for Edit/New Order links
import Link from "next/link";
import { Customer } from "@/types/sales-types";
import { ConsentStatus, VerifiedStatus } from "@/types/sales-types";
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

// UI Components (Keep all needed imports)
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import CustomerDocumentsTable from "@/components/customers/customer-documents-table";

// Icons (Keep all needed imports)
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
  StickyNote,
  Users,
  FileText,
  ShoppingBag,
  PhoneCall,
  History,
  Info,
  MessageSquare,
  ShieldCheck,
  UserCheck,
  BadgeCheck,
} from "lucide-react";

// --- Import components from the draft ---
// TODO: Ensure these components are copied from frontend-react/temp/customer-management-2/components/customers/ to frontend-react/src/components/customers/ or an appropriate shared location.
import { DeactivateCustomerDialog } from "@/components/customers/deactivate-customer-dialog"; // Added Import
import CustomerShopAccountsCard from "@/components/customers/customer-shop-accounts-card"; // Added Import
import CustomerCallHistoryCard from "@/components/customers/customer-call-history-card"; // Added Import
import CustomerHistoryCard from "@/components/customers/customer-history-card"; // Added Import
import CustomerAddressesCard from "@/components/customers/customer-addresses-card"; // Added Import
import CustomerNotesBlock from "@/components/customers/customer-notes-block"; // Added Import
// --- End draft component imports ---

// Basic currency formatter (Keep or import from utils)
const formatCurrency = (value: number | undefined | null) => {
    if (value == null) return '-';
    return new Intl.NumberFormat("default", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 2,
    }).format(value);
};

// Helper to get initials (Keep or import from utils)
const getInitials = (firstName?: string, lastName?: string, companyName?: string, isCompany?: boolean): string => {
    if (isCompany) {
        return (companyName || 'Co').substring(0, 2).toUpperCase();
    }
    const first = (firstName || '').charAt(0);
    const last = (lastName || '').charAt(0);
    return `${first}${last}`.toUpperCase() || '??';
};

// --- Add Enums (Example - define properly in types file) ---
// enum ConsentStatus { Yes = 'YES', No = 'NO', NotSet = 'NOT_SET' }
// enum VerifiedStatus { Yes = 'YES', No = 'NO', NotSet = 'NOT_SET' }
// --- End Enums ---

interface CustomerDetailPanelProps {
  customerId: string | null;
}

export default function CustomerDetailPanel({ customerId }: CustomerDetailPanelProps) {
  const router = useRouter(); // Keep for navigation links

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!customerId) {
        setCustomer(null);
        setError(null);
        setIsLoading(false); // Not loading if no ID
        return; // Exit if no customerId
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
        const customerEndpoint = `${API_URL}/sales/customers/${customerId}/`;
        const response = await fetch(customerEndpoint, {
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
           if (response.status === 401) throw new Error('Authentication failed.');
           if (response.status === 403) throw new Error('Permission denied.');
           if (response.status === 404) throw new Error('Customer not found.');
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
  }, [customerId]); // Re-run effect ONLY when customerId changes

  // Placeholder State (No customer selected)
  if (!customerId && !isLoading) {
    return (
        <div className="h-full flex flex-col items-center justify-center text-center p-6">
             <Users className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-semibold text-muted-foreground">Select a customer</p>
            <p className="text-sm text-muted-foreground">Choose a customer from the list to view their details.</p>
        </div>
    );
  }

  // Loading State
  if (isLoading) {
     // Use CardHeader and CardContent structure for consistency
     return (
        <>
         <CardHeader>
            {/* Minimal header skeleton */}
            <div className="flex items-center gap-4">
                <Skeleton className="h-12 w-12 rounded-full" />
                <div className="space-y-2">
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-32" />
                </div>
            </div>
         </CardHeader>
         <CardContent className="space-y-6">
             {/* Body Skeleton matching the layout */}
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
         </CardContent>
       </>
     );
   }

  // Error State
  if (error) {
     // Use CardHeader and CardContent structure for consistency
     return (
        <>
         <CardHeader>
           <CardTitle>Error Loading Details</CardTitle>
         </CardHeader>
         <CardContent>
            <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
            </Alert>
         </CardContent>
        </>
     );
   }

  // No Customer Data State (after fetch attempt)
  if (!customer) {
       // Use CardHeader and CardContent structure for consistency
     return (
        <>
         <CardHeader>
            <CardTitle>Customer Not Found</CardTitle>
         </CardHeader>
         <CardContent>
            <p className="text-center text-muted-foreground py-8">
                The selected customer data could not be loaded or found.
            </p>
         </CardContent>
        </>
     );
   }


  // --- Render Customer Details (Copied & adapted from original page) ---

  const individualName = `${customer.firstName || ""} ${customer.lastName || ""}`.trim();
  const customerName = customer.isCompany
    ? customer.companyName || "Unknown Company"
    : individualName || customer.name || "Unknown Customer";
  const initials = getInitials(customer.firstName, customer.lastName, customer.companyName, customer.isCompany);

  // The main return content needs to be wrapped in CardHeader and CardContent
  return (
    <>
      {/* Header needs to go inside CardHeader */}
      <CardHeader className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        {/* Left side: Avatar, Name, Since */}
        <div className="flex items-center gap-4">
          {/* Removed Back button - handled by layout or parent */}
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
              {!customer.isActive && (
                  <Badge variant="destructive" className="ml-2">Inactive</Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
                Customer since {formatDate(customer.since)} <span className="hidden sm:inline">• ID: {customer.customer_number}</span>
            </p>
            {!customer.isActive && customer.inactiveReason && (
                 <p className="text-sm text-destructive mt-1">
                   Reason: {customer.inactiveReason}
                   {customer.inactiveReason === 'OTHER' && customer.inactiveReasonDetails && ` (${customer.inactiveReasonDetails})`}
                 </p>
             )}
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
           {/* Functional Buttons using Link component */}
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
           <DeactivateCustomerDialog
               customerId={customerId}
               customerName={customerName}
               isActive={customer.isActive ?? true}
            />
        </div>
      </CardHeader>

      {/* Main Content needs to go inside CardContent */}
      <CardContent className="flex-grow overflow-y-auto">
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
                <TabsList className="grid w-full grid-cols-6 mb-4">
                  <TabsTrigger value="documents">
                      <FileText className="mr-2 h-4 w-4"/> Documents
                  </TabsTrigger>
                  <TabsTrigger value="contacts">
                      <Users className="mr-2 h-4 w-4"/> Contacts
                  </TabsTrigger>
                  <TabsTrigger value="shop-accounts">
                      <ShoppingBag className="mr-2 h-4 w-4"/> Shop Accounts
                  </TabsTrigger>
                  <TabsTrigger value="call-history">
                      <PhoneCall className="mr-2 h-4 w-4"/> Calls
                  </TabsTrigger>
                  <TabsTrigger value="notes">
                      <MessageSquare className="mr-2 h-4 w-4"/> Notes
                  </TabsTrigger>
                  <TabsTrigger value="history">
                      <History className="mr-2 h-4 w-4"/> History
                  </TabsTrigger>
                </TabsList>

                {/* Documents Tab */}
                <TabsContent value="documents">
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                      <CardTitle>Recent Documents</CardTitle>
                      <Button variant="outline" size="sm" disabled>View All</Button>
                    </CardHeader>
                    <CardContent>
                       {/* Render the CustomerDocumentsTable component only if customerId exists*/}
                       {customerId && <CustomerDocumentsTable customerId={customerId} />}
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Contacts Tab */}
                <TabsContent value="contacts">
                  <Card>
                     <CardHeader className="flex flex-row items-center justify-between">
                        <CardTitle>Contact Persons & Details</CardTitle>
                        <Button variant="outline" size="sm" disabled><Plus className="mr-2 h-4 w-4" />Add Contact</Button>
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
                        <Button variant="outline" size="sm" disabled><Plus className="mr-2 h-4 w-4" />Add Note</Button>
                     </CardHeader>
                     <CardContent>
                         {/* Placeholder: Replace with actual notes component */}
                        {customerId && <CustomerNotesBlock customerId={customerId} />}
                         {/* <CustomerNotesCard customerId={customerId} printableNotes={customer.printableNotes} internalNotes={customer.internalNotes} /> */}
                     </CardContent>
                   </Card>
                </TabsContent>

                {/* Shop Accounts Tab */}
                <TabsContent value="shop-accounts">
                  {/* TODO: Pass actual shop accounts data fetched from API */}
                  {customerId && <CustomerShopAccountsCard customerId={customerId} />}
                </TabsContent>

                {/* Call History Tab */}
                <TabsContent value="call-history">
                  {/* TODO: Pass actual call history data fetched from API */}
                  {customerId && <CustomerCallHistoryCard customerId={customerId} />}
                </TabsContent>

                {/* History Tab */}
                <TabsContent value="history">
                   {/* TODO: Pass actual history data fetched from API */}
                  {customerId && <CustomerHistoryCard customerId={customerId} />}
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
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Billing Address</CardTitle>
                  <Button variant="ghost" size="sm" disabled><Edit className="h-4 w-4" /></Button>
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

              {/* Shipping Addresses Card - Use the imported component */}
              {/* TODO: Pass actual shipping addresses data fetched from API */}
              {/* Ensure Customer type includes shippingAddresses: Address[]; */}
              {customerId && <CustomerAddressesCard customerId={customerId} addresses={customer.shippingAddresses || []} />}

              {/* Payment Information Card */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Payment Details</CardTitle>
                   <Button variant="ghost" size="sm" disabled><Edit className="h-4 w-4" /></Button>
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

              {/* Marketing & Sales Card */}
              <Card>
                 <CardHeader>
                    <CardTitle>Marketing & Sales</CardTitle>
                 </CardHeader>
                 <CardContent className="space-y-4">
                    {/* Consent */}
                    <div>
                      <p className="text-sm font-medium mb-2">Advertising Consent</p>
                      <div className="space-y-1 text-sm">
                        <div className="flex items-center justify-between">
                           <span className="text-muted-foreground flex items-center"><BadgeCheck className="h-4 w-4 mr-1.5"/>Postal:</span>
                           <Badge variant={customer.postalAdvertising === ConsentStatus.GRANTED ? "secondary" : "outline"}>
                             {customer.postalAdvertising ?? 'Not Set'}
                           </Badge>
                         </div>
                         <div className="flex items-center justify-between">
                           <span className="text-muted-foreground flex items-center"><BadgeCheck className="h-4 w-4 mr-1.5"/>Email:</span>
                           <Badge variant={customer.emailAdvertising === ConsentStatus.GRANTED ? "secondary" : "outline"}>
                              {customer.emailAdvertising ?? 'Not Set'}
                           </Badge>
                         </div>
                       </div>
                     </div>

                    {/* Sales Rep */}
                    {customer.salesRepresentative && (
                      <>
                         <Separator />
                         <div>
                           <p className="text-sm font-medium mb-1 flex items-center"><UserCheck className="h-4 w-4 mr-1.5"/> Sales Representative</p>
                           <p className="text-sm text-muted-foreground">{customer.salesRepresentative}</p>
                         </div>
                       </>
                     )}

                    {/* Verification Status */}
                    <Separator />
                     <div>
                       <p className="text-sm font-medium mb-1 flex items-center"><ShieldCheck className="h-4 w-4 mr-1.5"/> Verification</p>
                       <Badge variant={customer.verifiedStatus === VerifiedStatus.VERIFIED ? "secondary" : "outline"}>
                         {customer.verifiedStatus ?? 'Not Set'}
                       </Badge>
                     </div>
                 </CardContent>
               </Card>

              {/* Notes Block Card */}
              {customerId && <CustomerNotesBlock customerId={customerId} />}
            </div>
          </div>
      </CardContent>
    </>
  );
} 