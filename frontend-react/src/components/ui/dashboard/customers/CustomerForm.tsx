'use client';

import React, { useState } from 'react'; // Import useState
import { useForm, SubmitHandler, useFieldArray, Controller } from 'react-hook-form';
// ... other imports ...
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group" // Import RadioGroup
import { Badge } from "@/components/ui/badge"; // Import Badge
import { StarIcon } from 'lucide-react'; // Import StarIcon
import { z } from 'zod';

// ... addressSchema ...

// Define the Zod schema for the entire form validation
const customerFormSchema = z.object({
  customer_type: z.enum(['b2b', 'b2c']).default('b2b'), // Add customer type field
  name: z.string().min(2, { message: 'Customer name must be at least 2 characters.' }).max(100),
  // ... rest of schema
});

// Infer the TypeScript type from the Zod schema
// Export the type so it can be used elsewhere
export type CustomerFormData = z.infer<typeof customerFormSchema>;

// Define Props interface for the component
interface CustomerFormProps {
  initialData?: Partial<Customer & { shipping_addresses?: Address[], customer_type?: 'b2b' | 'b2c' }>; // Add customer_type to initialData
  // Add onSubmit prop later for actual data submission
  mode?: 'create' | 'edit'; // Add mode prop
}

// THE COMPONENT DEFINITION STARTS HERE
export default function CustomerForm({ initialData, mode = 'create' }: CustomerFormProps) {
  const router = useRouter();

  // === Hooks and State Setup ===
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    control,
    reset,
    watch, // Watch customer_type to potentially change fields later
    setValue, // Get setValue from useForm
    getValues, // Get getValues to read current state
  } = useForm<CustomerFormData>({
    resolver: zodResolver(customerFormSchema),
    defaultValues: {
      customer_type: initialData?.customer_type || 'b2b',
      name: initialData?.name || '',
      // ... other default values ...
      notes: initialData?.notes || '',
    },
  });

  const customerType = watch('customer_type'); // Watch the value

  const { fields, append, remove } = useFieldArray({
    control,
    name: "shipping_addresses"
  });

  // === Event Handlers ===
  const onSubmit: SubmitHandler<CustomerFormData> = async (data) => {
    console.log('Raw Form Data:', data);

    // 1. Restructure Billing Address
    const billing_address: Address | null = (
      data.billing_street || data.billing_city || data.billing_postal_code || data.billing_country
    ) ? {
      street: data.billing_street || '', // Ensure non-null strings
      city: data.billing_city || '',
      state: data.billing_state || null,
      postal_code: data.billing_postal_code || '',
      country: data.billing_country || '',
    } : null;

    // 2. Prepare the final payload for API
    const payload: Partial<Customer & { customer_type: 'b2b' | 'b2c', shipping_addresses?: Address[] }> = {
      // Map form fields to Customer fields
      customer_type: data.customer_type,
      name: data.name,
      tax_id: data.tax_id,
      phone: data.phone,
      email: data.email,
      website: data.website,
      billing_address: billing_address,
      shipping_addresses: data.shipping_addresses,
      payment_terms: data.payment_terms,
      bank_iban: data.bank_iban,
      bank_bic: data.bank_bic,
      notes: data.notes,
      // Add id if in edit mode
      ...(mode === 'edit' && initialData?.id && { id: initialData.id }),
    };

    console.log('Prepared API Payload:', payload);

    // 3. Simulate API Call
    try {
      // TODO: Replace with actual API call (e.g., createCustomer(payload) or updateCustomer(payload))
      await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API delay
      console.log('Simulated API call successful!');

      // 5. Provide Feedback/Redirect
      // TODO: Add toast notification for success
      // Reset form? reset();
      if (mode === 'create') {
         router.push('/dashboard/customers'); // Redirect to list after creating
      } else {
         // Maybe redirect back to detail page or list?
         router.push(`/dashboard/customers/${initialData?.id || ''}`);
      }
      router.refresh(); // Refresh server components

    } catch (error) {
      console.error('API call failed:', error);
      // TODO: Add toast notification for error
    }
  };

  // Function to handle making an address primary
  const handleMakePrimary = (selectedIndex: number) => {
    const currentAddresses = getValues('shipping_addresses') || [];
    const updatedAddresses = currentAddresses.map((addr, index) => ({
      ...addr,
      is_primary: index === selectedIndex
    }));
    setValue('shipping_addresses', updatedAddresses, { shouldValidate: true, shouldDirty: true }); // Update form state
  };

  // === JSX Return ===
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Customer Type Selection */}
      {mode === 'create' && ( // Only show selection in create mode
         <Card className="mb-6">
          <CardHeader>
            <CardTitle>Customer Type</CardTitle>
            <CardDescription>Select if this is a business (B2B) or a private person (B2C).</CardDescription>
          </CardHeader>
          <CardContent>
            <Controller
              name="customer_type"
              control={control}
              render={({ field }) => (
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="grid grid-cols-2 gap-4"
                >
                  <Label
                     htmlFor="b2b"
                     className={`flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground ${field.value === 'b2b' ? 'border-primary' : ''}`}
                  >
                    <RadioGroupItem value="b2b" id="b2b" className="sr-only" />
                    <span className="text-lg font-semibold">Business (B2B)</span>
                     {/* Optional: Add icon or description */}
                  </Label>
                   <Label
                     htmlFor="b2c"
                     className={`flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground ${field.value === 'b2c' ? 'border-primary' : ''}`}
                  >
                    <RadioGroupItem value="b2c" id="b2c" className="sr-only" />
                     <span className="text-lg font-semibold">Private (B2C)</span>
                      {/* Optional: Add icon or description */}
                  </Label>
                </RadioGroup>
              )}
            />
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="general" className="w-full">
        {/* Tab Triggers ... */}

        {/* Tab Contents ... */}
        <TabsContent value="general">
           <Card>
             {/* ... CardHeader ... */}
            <CardContent className="space-y-4">
               <div className="grid gap-2">
                 {/* Adjust Label based on customer type? */}
                 <Label htmlFor="name">{customerType === 'b2b' ? 'Company Name' : 'Customer Name'} *</Label>
                 <Input id="name" {...register('name')} />
                 {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
               </div>
               {/* Conditionally show Tax ID only for B2B? */}
               {customerType === 'b2b' && (
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="tax_id">Tax ID / VAT ID</Label>
                    <Input id="tax_id" {...register('tax_id')} />
                    {errors.tax_id && <p className="text-sm text-red-500">{errors.tax_id.message}</p>}
                  </div>
                 </div>
               )}
               {/* ... rest of general fields ... */}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Shipping Addresses Tab Content */}
        <TabsContent value="shipping">
          <Card>
            {/* ... CardHeader ... */}
            <CardContent className="space-y-4">
              {fields.map((field, index) => (
                <div key={field.id} className="p-4 border rounded-md space-y-3 relative">
                  {/* Remove Button ... */}
                   <div className="flex justify-between items-center mb-2">
                     <h4 className="font-medium text-sm">Address {index + 1}</h4>
                     {/* Display Badge if primary, Button if not */}
                     {watch(`shipping_addresses.${index}.is_primary`) ? (
                       <Badge variant="secondary">
                         <StarIcon className="mr-1 h-3 w-3" /> Primary
                       </Badge>
                     ) : (
                       <Button
                         type="button"
                         variant="outline"
                         size="sm"
                         onClick={() => handleMakePrimary(index)}
                       >
                         Make Primary
                       </Button>
                     )}
                   </div>
                   {/* ... Address Fields (Street, City, State, Postal, Country Controller) ... */}
                   <div className="grid gap-2">
                     <Label htmlFor={`shipping_addresses.${index}.street`}>Street</Label>
                     <Input id={`shipping_addresses.${index}.street`} {...register(`shipping_addresses.${index}.street`)} />
                   </div>
                   <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="grid gap-2">
                       <Label htmlFor={`shipping_addresses.${index}.city`}>City</Label>
                       <Input id={`shipping_addresses.${index}.city`} {...register(`shipping_addresses.${index}.city`)} />
                     </div>
                     <div className="grid gap-2">
                       <Label htmlFor={`shipping_addresses.${index}.state`}>State / Province</Label>
                       <Input id={`shipping_addresses.${index}.state`} {...register(`shipping_addresses.${index}.state`)} />
                     </div>
                     <div className="grid gap-2">
                       <Label htmlFor={`shipping_addresses.${index}.postal_code`}>Postal Code</Label>
                       <Input id={`shipping_addresses.${index}.postal_code`} {...register(`shipping_addresses.${index}.postal_code`)} />
                     </div>
                   </div>
                   <div className="grid gap-2">
                     <Label htmlFor={`shipping_addresses.${index}.country`}>Country</Label>
                      <Controller
                         name={`shipping_addresses.${index}.country`}
                         control={control}
                         render={({ field }) => (
                           <Select onValueChange={field.onChange} value={field.value || undefined} defaultValue={field.value || undefined}>
                             <SelectTrigger id={`shipping_addresses.${index}.country`}>
                               <SelectValue placeholder="Select a country" />
                             </SelectTrigger>
                             <SelectContent>
                               {COUNTRIES.map(country => (
                                 <SelectItem key={country.code} value={country.code}>{country.name}</SelectItem>
                               ))}
                             </SelectContent>
                           </Select>
                         )}
                       />
                   </div>
                   {/* Removed explicit is_primary field - handled by button */}
                 </div>
              ))}
              {/* ... Add Address Button ... */}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ... Other Tab Contents ... */}
      </Tabs>

      {/* Form Actions ... */}
    </form>
  );
}
