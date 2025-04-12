"use client";

import React, { useState, useEffect } from "react";
import { Customer, CustomerFormData } from "@/lib/definitions"; // Assuming definitions are updated
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { useRouter } from 'next/navigation'; // For redirection
import { createCustomerAPI, updateCustomerAPI } from "@/lib/api"; // Import API functions
// Consider adding a toast library for user feedback, e.g., react-hot-toast
// import toast from 'react-hot-toast';

// Define props for the form component
export interface CustomerFormProps {
  initialData?: Partial<Customer>; // For editing existing customer
  mode: "create" | "edit";
}

// Define the type for customer type state
type CustomerType = "b2b" | "b2c";

// Pass only initialData and mode
export default function CustomerForm({ initialData = {}, mode }: CustomerFormProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("basic");
  const [customerType, setCustomerType] = useState<CustomerType>(
    initialData.isCompany !== undefined ? (initialData.isCompany ? "b2b" : "b2c") : "b2b"
  );
  const [formData, setFormData] = useState<Partial<CustomerFormData>>(initialData); // Use specific form data type if different
  const [shippingAddresses, setShippingAddresses] = useState<Partial<any>[]>(initialData.shippingAddresses || []);
  const [isSubmitting, setIsSubmitting] = useState(false); // Internal loading state
  const [error, setError] = useState<string | null>(null); // Internal error state

  useEffect(() => {
    // Reset form state when initialData changes (e.g., navigating between edits)
    setFormData(initialData);
    setCustomerType(initialData.isCompany !== undefined ? (initialData.isCompany ? "b2b" : "b2c") : "b2b");
    setShippingAddresses(initialData.shippingAddresses || []);
    setError(null); // Clear previous errors
    setIsSubmitting(false); // Reset submitting state
  }, [initialData]);

  // --- Input Handlers --- //

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    let processedValue: string | number | boolean | undefined = value;

    if (type === "number") {
      processedValue = value === '' ? undefined : Number.parseFloat(value);
    } else if (type === 'checkbox') {
      // Handle checkboxes if needed, though handleCheckboxChange might be separate
      processedValue = (e.target as HTMLInputElement).checked;
    } // Add other type conversions if needed

    setFormData(prev => ({ ...prev, [name]: processedValue }));
  };

  const handleCheckboxChange = (name: keyof CustomerFormData, checked: boolean) => {
    setFormData(prev => ({ ...prev, [name]: checked }));
  };

  const handleSelectChange = (name: keyof CustomerFormData, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Handler for customer type change (radio buttons)
  const handleCustomerTypeChange = (type: CustomerType) => {
    setCustomerType(type);
    setFormData(prev => ({
      ...prev,
      isCompany: type === "b2b",
      // Clear conflicting fields if necessary
      companyName: type === 'b2c' ? undefined : prev.companyName,
      firstName: type === 'b2b' ? undefined : prev.firstName,
      // lastName is usually required for both, adjust as needed
    }));
  };

  // --- Form Submission --- //
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const finalData: CustomerFormData = {
      ...(formData as CustomerFormData), // Assert type if confident, or validate first
      isCompany: customerType === "b2b",
      // Ensure required fields are present based on type
      // TODO: Properly integrate shipping address state if implemented
      // shippingAddresses: shippingAddresses,
    };

    // Basic validation example (adapt as needed)
    if (customerType === 'b2b' && !finalData.companyName) {
        setError("Company Name is required for B2B customers.");
        setIsSubmitting(false);
        setActiveTab("basic"); // Switch to relevant tab
        return;
    }
    if (customerType === 'b2c' && !finalData.lastName) {
        setError("Last Name is required for B2C customers.");
        setIsSubmitting(false);
        setActiveTab("basic");
        return;
    }
    // Add more validation rules here

    try {
      let savedCustomer: Customer;
      if (mode === 'edit') {
        if (!initialData.id) {
          throw new Error("Cannot update customer without an ID.");
        }
        console.log("Updating customer with data:", finalData);
        savedCustomer = await updateCustomerAPI(initialData.id, finalData);
        // toast.success('Customer updated successfully!');
        console.log('Customer updated successfully!');
      } else {
        console.log("Creating customer with data:", finalData);
        savedCustomer = await createCustomerAPI(finalData);
        // toast.success('Customer created successfully!');
        console.log('Customer created successfully!');
      }
      // Redirect to the detail page of the newly created/updated customer
      router.push(`/dashboard/customers/${savedCustomer.id}`);
      // Optionally refresh data for the list page if needed in background
      // router.refresh(); // Re-fetches data for current route

    } catch (err: any) {
      console.error(`Failed to ${mode === 'edit' ? 'update' : 'create'} customer:`, err);
      // Use error message from API response or provide a generic one
      setError(err.message || `An error occurred while ${mode === 'edit' ? 'updating' : 'creating'} the customer.`);
      // toast.error(`Failed to ${mode === 'edit' ? 'update' : 'create'} customer: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // --- JSX --- //

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Customer Type Selection (only in create mode) */}
      {mode === "create" && (
        <Card>
          <CardHeader>
            <CardTitle>Customer Type</CardTitle>
            <CardDescription>Is this a company (B2B) or an individual (B2C)?</CardDescription>
          </CardHeader>
          <CardContent>
             <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                 {/* B2B Radio Button */}
                 <label
                    htmlFor="b2b"
                    className={cn(
                        "flex flex-col items-center justify-center rounded-md border-2 p-4 cursor-pointer transition-colors",
                        customerType === 'b2b' ? "border-primary bg-primary/5" : "border-muted hover:bg-accent hover:text-accent-foreground"
                    )}
                 >
                    <input
                      type="radio"
                      id="b2b"
                      name="customerType"
                      value="b2b"
                      checked={customerType === "b2b"}
                      onChange={() => handleCustomerTypeChange("b2b")}
                      className="peer sr-only"
                    />
                    <span className="text-lg font-semibold">Company (B2B)</span>
                 </label>
                 {/* B2C Radio Button */}
                 <label
                    htmlFor="b2c"
                     className={cn(
                        "flex flex-col items-center justify-center rounded-md border-2 p-4 cursor-pointer transition-colors",
                        customerType === 'b2c' ? "border-primary bg-primary/5" : "border-muted hover:bg-accent hover:text-accent-foreground"
                    )}
                 >
                    <input
                      type="radio"
                      id="b2c"
                      name="customerType"
                      value="b2c"
                      checked={customerType === "b2c"}
                      onChange={() => handleCustomerTypeChange("b2c")}
                      className="peer sr-only"
                    />
                    <span className="text-lg font-semibold">Individual (B2C)</span>
                 </label>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Form Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 md:grid-cols-5 mb-6">
          <TabsTrigger value="basic">Basic Info</TabsTrigger>
          <TabsTrigger value="address">Billing Address</TabsTrigger>
          <TabsTrigger value="shipping">Shipping</TabsTrigger>
          <TabsTrigger value="payment">Payment</TabsTrigger>
          <TabsTrigger value="notes">Notes & Other</TabsTrigger>
        </TabsList>

        {/* --- Tab Content --- */} 

        {/* Basic Info Tab */}
        <TabsContent value="basic">
            <Card>
                <CardHeader>
                    <CardTitle>Basic Information</CardTitle>
                    <CardDescription>Enter the customer's core details.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {/* Customer Number (read-only in edit mode) */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="customer_number">Customer Number</Label>
                            <Input
                                id="customer_number"
                                name="customer_number"
                                value={formData.customer_number || ''}
                                onChange={handleInputChange}
                                required
                                disabled={mode === 'edit'} // Usually assigned by system
                                placeholder={mode === 'edit' ? '' : 'Will be assigned'}
                            />
                        </div>
                        {/* Placeholder for Customer Group if needed */}
                        <div>
                           <Label htmlFor="customer_group">Customer Group</Label>
                           <Input id="customer_group" name="customer_group" value={formData.customer_group || ''} onChange={handleInputChange} placeholder="e.g., Wholesale, Retail"/>
                        </div>
                    </div>

                    {/* Conditional Fields based on Customer Type */}
                    {customerType === 'b2b' && (
                        <div>
                           <Label htmlFor="companyName">Company Name</Label>
                           <Input id="companyName" name="companyName" value={formData.companyName || ''} onChange={handleInputChange} required placeholder="e.g., ACME Corp."/>
                        </div>
                    )}

                    {customerType === 'b2c' && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                               <Label htmlFor="firstName">First Name</Label>
                               <Input id="firstName" name="firstName" value={formData.firstName || ''} onChange={handleInputChange} placeholder="e.g., John"/>
                            </div>
                             <div>
                               <Label htmlFor="lastName">Last Name</Label>
                               <Input id="lastName" name="lastName" value={formData.lastName || ''} onChange={handleInputChange} required placeholder="e.g., Doe"/>
                            </div>
                        </div>
                    )}

                     {/* Common Contact Fields */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                         <div>
                            <Label htmlFor="emailMain">Primary Email</Label>
                            <Input id="emailMain" name="emailMain" type="email" value={formData.emailMain || ''} onChange={handleInputChange} placeholder="e.g., info@example.com"/>
                         </div>
                         <div>
                            <Label htmlFor="phoneMain">Primary Phone</Label>
                            <Input id="phoneMain" name="phoneMain" type="tel" value={formData.phoneMain || ''} onChange={handleInputChange} placeholder="e.g., +1 234 567 890"/>
                         </div>
                     </div>
                     <div>
                        <Label htmlFor="website">Website</Label>
                        <Input id="website" name="website" type="url" value={formData.website || ''} onChange={handleInputChange} placeholder="e.g., https://example.com"/>
                     </div>
                </CardContent>
            </Card>
        </TabsContent>

        {/* Billing Address Tab */}
        <TabsContent value="address">
            <Card>
                <CardHeader>
                    <CardTitle>Billing Address</CardTitle>
                     <CardDescription>Enter the main address for invoicing.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div className="sm:col-span-2">
                           <Label htmlFor="billingStreet">Street</Label>
                           <Input id="billingStreet" name="billingStreet" value={formData.billingStreet || ''} onChange={handleInputChange} placeholder="e.g., 123 Main St"/>
                        </div>
                         <div>
                            <Label htmlFor="billingStreetNumber">Number</Label> {/* Assuming street number is separate */} 
                            <Input id="billingStreetNumber" name="billingStreetNumber" value={formData.billingStreetNumber || ''} onChange={handleInputChange} placeholder="e.g., Apt 4B"/>
                         </div>
                    </div>
                     <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                         <div>
                           <Label htmlFor="billingPostalCode">Postal Code</Label>
                           <Input id="billingPostalCode" name="billingPostalCode" value={formData.billingPostalCode || ''} onChange={handleInputChange} placeholder="e.g., 90210"/>
                        </div>
                        <div className="sm:col-span-2">
                            <Label htmlFor="billingCity">City</Label>
                            <Input id="billingCity" name="billingCity" value={formData.billingCity || ''} onChange={handleInputChange} placeholder="e.g., Beverly Hills"/>
                         </div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                           <Label htmlFor="billingState">State / Province</Label>
                           <Input id="billingState" name="billingState" value={formData.billingState || ''} onChange={handleInputChange} placeholder="e.g., CA"/>
                        </div>
                        <div>
                           <Label htmlFor="billingCountry">Country</Label>
                            {/* TODO: Replace with a proper Country Select component if available */}
                           <Input id="billingCountry" name="billingCountry" value={formData.billingCountry || ''} onChange={handleInputChange} placeholder="e.g., USA"/>
                        </div>
                    </div>
                 </CardContent>
            </Card>
        </TabsContent>

        {/* Shipping Address Tab */}
        <TabsContent value="shipping">
             <Card>
                <CardHeader>
                    <CardTitle>Shipping Addresses</CardTitle>
                    <CardDescription>Manage delivery addresses (optional).</CardDescription>
                </CardHeader>
                <CardContent>
                    {/* Placeholder for Shipping Address Management */}
                    <p className="text-muted-foreground text-center py-6">
                        Shipping address management UI will go here.
                        (Allows adding/editing multiple addresses)
                    </p>
                </CardContent>
             </Card>
        </TabsContent>

        {/* Payment Tab */}
        <TabsContent value="payment">
             <Card>
                <CardHeader>
                    <CardTitle>Payment & Billing</CardTitle>
                     <CardDescription>Configure payment terms and details.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <Label htmlFor="vat_id">VAT ID</Label>
                            <Input id="vat_id" name="vat_id" value={formData.vat_id || ''} onChange={handleInputChange} placeholder="e.g., DE123456789"/>
                        </div>
                        {/* Placeholder for Payment Terms */} 
                        <div>
                           <Label htmlFor="paymentTermsOverall">Payment Term</Label>
                           <Input id="paymentTermsOverall" name="paymentTermsOverall" value={formData.paymentTermsOverall || ''} onChange={handleInputChange} placeholder="e.g., 30 days net"/>
                        </div>
                    </div>
                     <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                         <div>
                           <Label htmlFor="discount">Customer Discount (%)</Label>
                           <Input id="discount" name="discount" type="number" step="0.01" value={formData.discount ?? ''} onChange={handleInputChange} placeholder="e.g., 5"/>
                        </div>
                        <div>
                            <Label htmlFor="creditLimit">Credit Limit (€)</Label> {/* Adjust currency symbol */} 
                            <Input id="creditLimit" name="creditLimit" type="number" step="0.01" value={formData.creditLimit ?? ''} onChange={handleInputChange} placeholder="e.g., 5000"/>
                         </div>
                    </div>
                    {/* TODO: Add fields for Bank Details (IBAN, BIC), Allowed Payment Methods (Multi-select?) */}
                 </CardContent>
             </Card>
        </TabsContent>

         {/* Notes & Other Tab */}
        <TabsContent value="notes">
            <Card>
                <CardHeader>
                    <CardTitle>Notes & Other Details</CardTitle>
                     <CardDescription>Additional information and internal notes.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                     <div>
                         <Label htmlFor="internalNotes">Internal Notes (not printed)</Label>
                         <Textarea
                             id="internalNotes"
                             name="internalNotes"
                             value={formData.internalNotes || ''}
                             onChange={handleInputChange}
                             rows={4}
                             placeholder="Add any internal remarks about this customer..."
                         />
                     </div>
                      <div>
                         <Label htmlFor="printableNotes">Printable Notes (on documents)</Label>
                         <Textarea
                             id="printableNotes"
                             name="printableNotes"
                             value={formData.printableNotes || ''}
                             onChange={handleInputChange}
                             rows={3}
                             placeholder="Add notes that should appear on orders/invoices..."
                         />
                     </div>
                     {/* TODO: Add Marketing Consent fields if needed (Checkboxes) */}
                </CardContent>
            </Card>
        </TabsContent>
      </Tabs>

       {/* Form Actions */} 
      <div className="flex flex-col items-end gap-4 mt-6">
        {error && (
          <p className="text-sm text-red-500">Error: {error}</p>
        )}
        <div className="flex justify-end gap-4">
             {/* Optional Cancel Button */}
             <Button type="button" variant="outline" onClick={() => router.back()} disabled={isSubmitting}>
                Cancel
             </Button>
             <Button type="submit" disabled={isSubmitting}>
               {isSubmitting ? "Saving..." : (mode === 'create' ? "Create Customer" : "Save Changes")}
            </Button>
        </div>
      </div>
    </form>
  );
} 