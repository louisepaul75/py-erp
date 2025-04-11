"use client"

import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useQueryClient, useMutation } from '@tanstack/react-query'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { useToast } from "@/hooks/use-toast"
import type { Supplier, NewSupplier, UpdateSupplier } from "@/types/supplier"
import { createSupplier, updateSupplier } from "@/lib/api/suppliers"

// Validation schema - Adjusted to match our Supplier type
// Making fields potentially nullable based on Supplier type, adding defaults where needed
const supplierFormSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  contactPerson: z.string().nullable().optional(),
  email: z.string().email("Invalid email address").nullable().optional(),
  phone: z.string().nullable().optional(),
  address: z.string().nullable().optional(),
  taxId: z.string().nullable().optional(),
  accountingId: z.string().nullable().optional(), // Added accountingId
  creditorId: z.string().nullable().optional(),
  notes: z.string().nullable().optional(),
  syncToAccounting: z.boolean().default(true), // UI Placeholder
})

type SupplierFormValues = z.infer<typeof supplierFormSchema>

interface SupplierDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  supplier?: Supplier | null // Allow null for explicit clearing
  onSuccess?: () => void // Make onSuccess optional
}

export function SupplierDialog({ open, onOpenChange, supplier, onSuccess }: SupplierDialogProps) {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const isEditing = !!supplier

  const form = useForm<SupplierFormValues>({
    resolver: zodResolver(supplierFormSchema),
    defaultValues: {
      name: "",
      contactPerson: null,
      email: null,
      phone: null,
      address: null,
      taxId: null,
      accountingId: null, // Added default
      creditorId: null,
      notes: null,
      syncToAccounting: true, // Default placeholder value
    },
  })

  // --- Mutations ---
  const createMutation = useMutation({
    mutationFn: createSupplier,
    onSuccess: (data) => {
      toast({
        title: "Supplier Created",
        description: `${data.name} has been created successfully.`,
      })
      queryClient.invalidateQueries({ queryKey: ['suppliers'] }) // Invalidate cache
      onOpenChange(false) // Close dialog
      onSuccess?.() // Call optional onSuccess callback
    },
    onError: (error) => {
      toast({
        title: "Error Creating Supplier",
        description: error.message || "An unknown error occurred.",
        variant: "destructive",
      })
    },
  })

  const updateMutation = useMutation({
    mutationFn: (data: UpdateSupplier) => updateSupplier(data.id, data),
    onSuccess: (data) => {
      toast({
        title: "Supplier Updated",
        description: `${data.name} has been updated successfully.`,
      })
      queryClient.invalidateQueries({ queryKey: ['suppliers'] }) // Invalidate cache
      queryClient.invalidateQueries({ queryKey: ['supplier', data.id] }) // Invalidate specific supplier if needed
      onOpenChange(false) // Close dialog
      onSuccess?.() // Call optional onSuccess callback
    },
    onError: (error) => {
      toast({
        title: "Error Updating Supplier",
        description: error.message || "An unknown error occurred.",
        variant: "destructive",
      })
    },
  })


  // Set form values when 'supplier' prop changes
  useEffect(() => {
    if (supplier) {
      form.reset({
        name: supplier.name || "",
        contactPerson: supplier.contactPerson || null,
        email: supplier.email || null,
        phone: supplier.phone || null,
        address: supplier.address || null,
        taxId: supplier.taxId || null,
        accountingId: supplier.accountingId || null, // Map accountingId
        creditorId: supplier.creditorId || null,
        notes: supplier.notes || null,
        syncToAccounting: true, // Reset placeholder (logic TBD)
      })
    } else {
      // Reset form to default values when supplier is null (e.g., for creating new)
      form.reset({
        name: "",
        contactPerson: null,
        email: null,
        phone: null,
        address: null,
        taxId: null,
        accountingId: null,
        creditorId: null,
        notes: null,
        syncToAccounting: true,
      })
    }
  }, [supplier, form])

  // Handle form submission
  const onSubmit = (values: SupplierFormValues) => {
    // Exclude the placeholder UI field from the data sent to the backend
    const { syncToAccounting, ...submitData } = values;

    if (isEditing && supplier) {
      updateMutation.mutate({ id: supplier.id, ...submitData })
    } else {
      // Cast to NewSupplier to match API expectation
      createMutation.mutate(submitData as NewSupplier)
    }
  }

  const isSubmitting = form.formState.isSubmitting || createMutation.isPending || updateMutation.isPending;

  return (
    // Set key based on supplier?.id to force re-render/reset state when supplier changes
    <Dialog open={open} onOpenChange={onOpenChange} key={supplier?.id ?? 'new'}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit Supplier" : "Create New Supplier"}</DialogTitle>
          <DialogDescription>
            {isEditing ? `Update details for ${supplier?.name}.` : "Fill in the details to create a new supplier."}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          {/* Using form.handleSubmit correctly with react-hook-form */}
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Company Name *</FormLabel>
                  <FormControl>
                    <Input placeholder="Acme Inc." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="contactPerson"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Contact Person</FormLabel>
                  <FormControl>
                    {/* Pass null if value is empty string */}
                    <Input placeholder="John Doe" {...field} value={field.value ?? ""} onChange={e => field.onChange(e.target.value || null)} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                     <Input type="email" placeholder="contact@acme.com" {...field} value={field.value ?? ""} onChange={e => field.onChange(e.target.value || null)} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="phone"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Phone</FormLabel>
                    <FormControl>
                      <Input placeholder="+1 (555) 123-4567" {...field} value={field.value ?? ""} onChange={e => field.onChange(e.target.value || null)} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="address"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Address</FormLabel>
                  <FormControl>
                    <Textarea placeholder="123 Main St, City, Country" {...field} value={field.value ?? ""} onChange={e => field.onChange(e.target.value || null)} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                    control={form.control}
                    name="taxId"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Tax ID</FormLabel>
                        <FormControl>
                            <Input placeholder="Tax ID or VAT number" {...field} value={field.value ?? ""} onChange={e => field.onChange(e.target.value || null)} />
                        </FormControl>
                        <FormMessage />
                        </FormItem>
                    )}
                    />
                <FormField
                    control={form.control}
                    name="accountingId"
                    render={({ field }) => (
                        <FormItem>
                        <FormLabel>Accounting ID</FormLabel>
                        <FormControl>
                            <Input placeholder="Internal Accounting Ref" {...field} value={field.value ?? ""} onChange={e => field.onChange(e.target.value || null)} />
                        </FormControl>
                        <FormMessage />
                        </FormItem>
                    )}
                 />
             </div>


            <FormField
              control={form.control}
              name="creditorId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Creditor ID</FormLabel>
                  <FormControl>
                    <Input placeholder="Creditor ID for Paperless DMS" {...field} value={field.value ?? ""} onChange={e => field.onChange(e.target.value || null)} />
                  </FormControl>
                  <FormDescription>Optional ID used for external system integrations (e.g., Paperless).</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Additional notes about this supplier" className="min-h-[100px]" {...field} value={field.value ?? ""} onChange={e => field.onChange(e.target.value || null)} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* --- Placeholder Checkbox --- */}
            <FormField
              control={form.control}
              name="syncToAccounting"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 bg-muted/40">
                  <FormControl>
                    <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>Sync to Accounting System (Placeholder)</FormLabel>
                    <FormDescription>
                      (This feature is not yet implemented)
                    </FormDescription>
                  </div>
                </FormItem>
              )}
            />
            {/* --- End Placeholder Checkbox --- */}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Saving..." : isEditing ? "Update Supplier" : "Create Supplier"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
} 