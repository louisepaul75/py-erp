"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form" // Korrigierter Import
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useCreateDocument } from "@/hooks/document/use-documents"
import type { DocumentType } from "@/types/document/document"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DocumentItemsForm } from "@/components/document/document-items-form"
import { Checkbox } from "@/components/ui/checkbox"
import { CollectiveInvoiceHierarchicalView } from "@/components/document/collective-invoice-hierarchical-view"

/**
 * Schema for document creation form validation
 */
const formSchema = z.object({
  type: z.enum(["ORDER", "DELIVERY", "INVOICE", "CREDIT"]),
  number: z.string().min(1, "Document number is required"),
  customerId: z.string().min(1, "Customer is required"),
  date: z.string().min(1, "Date is required"),
  status: z.string().min(1, "Status is required"),
  notes: z.string().optional(),
})

/**
 * Type for the form values
 */
type FormValues = z.infer<typeof formSchema>

/**
 * Props for the DocumentCreateModal component
 */
interface DocumentCreateModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * DocumentCreateModal component that displays a modal for creating a new document
 */
export function DocumentCreateModal({ open, onOpenChange }: DocumentCreateModalProps) {
  // State for the active tab
  const [activeTab, setActiveTab] = useState("details")

  // State for document items
  const [items, setItems] = useState<any[]>([])

  // Initialize form with react-hook-form and zod validation
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      type: "ORDER",
      number: "",
      customerId: "",
      date: new Date().toISOString().split("T")[0],
      status: "OPEN",
      notes: "",
    },
  })

  // State for collective invoice mode - default to true for INVOICE type
  const [collectiveInvoiceMode, setCollectiveInvoiceMode] = useState(form.getValues().type === "INVOICE")

  // Watch for type changes to update UI accordingly
  const documentType = form.watch("type")

  // Update collectiveInvoiceMode when document type changes
  useEffect(() => {
    const subscription = form.watch((value, { name }) => {
      if (name === "type") {
        setCollectiveInvoiceMode(value.type === "INVOICE")
      }
    })
    return () => subscription.unsubscribe()
  }, [form])

  // Mutation for creating a document
  const createDocument = useCreateDocument()

  // Handle form submission
  const onSubmit = (values: FormValues) => {
    createDocument.mutate(
      {
        ...values,
        items,
      },
      {
        onSuccess: () => {
          onOpenChange(false)
          form.reset()
          setItems([])
        },
      },
    )
  }

  // Get document type options
  const documentTypes: { value: DocumentType; label: string }[] = [
    { value: "ORDER", label: "Order" },
    { value: "DELIVERY", label: "Delivery Note" },
    { value: "INVOICE", label: "Invoice" },
    { value: "CREDIT", label: "Credit Note" },
  ]

  // Get status options based on document type
  const getStatusOptions = (type: DocumentType) => {
    switch (type) {
      case "ORDER":
        return [
          { value: "OPEN", label: "Open" },
          { value: "CONFIRMED", label: "Confirmed" },
          { value: "COMPLETED", label: "Completed" },
          { value: "CANCELED", label: "Canceled" },
        ]
      case "DELIVERY":
        return [
          { value: "OPEN", label: "Open" },
          { value: "SHIPPED", label: "Shipped" },
          { value: "DELIVERED", label: "Delivered" },
          { value: "CANCELED", label: "Canceled" },
        ]
      case "INVOICE":
        return [
          { value: "OPEN", label: "Open" },
          { value: "PAID", label: "Paid" },
          { value: "CANCELED", label: "Canceled" },
        ]
      case "CREDIT":
        return [
          { value: "OPEN", label: "Open" },
          { value: "PROCESSED", label: "Processed" },
          { value: "CANCELED", label: "Canceled" },
        ]
      default:
        return [
          { value: "OPEN", label: "Open" },
          { value: "COMPLETED", label: "Completed" },
          { value: "CANCELED", label: "Canceled" },
        ]
    }
  }

  // Mock customer data
  const customers = [
    { id: "1", name: "Acme Inc." },
    { id: "2", name: "Globex Corporation" },
    { id: "3", name: "Initech" },
    { id: "4", name: "Umbrella Corporation" },
  ]

  // If in collective invoice mode, show the hierarchical view
  if (collectiveInvoiceMode && documentType === "INVOICE") {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-[95vw] h-[95vh] max-h-[95vh] flex flex-col p-0">
          <CollectiveInvoiceHierarchicalView
            onClose={() => {
              setCollectiveInvoiceMode(false)
              onOpenChange(false)
            }}
          />
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Create New Document</DialogTitle>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="details">Document Details</TabsTrigger>
            <TabsTrigger value="items">Document Items</TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <Form {...form}>
              <form className="space-y-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="type"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Document Type</FormLabel>
                        <Select
                          onValueChange={(value) => {
                            field.onChange(value)
                          }}
                          defaultValue={field.value}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select document type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {documentTypes.map((type) => (
                              <SelectItem key={type.value} value={type.value}>
                                {type.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="number"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Document Number</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g., ORD-2023-001" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="customerId"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Customer</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select customer" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {customers.map((customer) => (
                              <SelectItem key={customer.id} value={customer.id}>
                                {customer.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="date"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Date</FormLabel>
                        <FormControl>
                          <Input type="date" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="status"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Status</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select status" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {getStatusOptions(form.watch("type") as DocumentType).map((status) => (
                            <SelectItem key={status.value} value={status.value}>
                              {status.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
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
                        <Textarea placeholder="Additional information about this document" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Collective Invoice Option - only show for INVOICE type */}
                {documentType === "INVOICE" && (
                  <div className="flex items-center space-x-2 pt-2">
                    <Checkbox
                      id="collectiveInvoice"
                      checked={collectiveInvoiceMode}
                      onCheckedChange={(checked) => {
                        setCollectiveInvoiceMode(!!checked)
                      }}
                    />
                    <label
                      htmlFor="collectiveInvoice"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Create as Collective Invoice (Standard) - Uncheck for manual item entry
                    </label>
                  </div>
                )}

                <div className="flex justify-between">
                  <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                    Cancel
                  </Button>
                  {documentType === "INVOICE" ? (
                    <Button
                      type="button"
                      onClick={() => (collectiveInvoiceMode ? setCollectiveInvoiceMode(true) : setActiveTab("items"))}
                    >
                      {collectiveInvoiceMode ? "Continue to Collective Invoice" : "Next: Add Items Manually"}
                    </Button>
                  ) : (
                    <Button type="button" onClick={() => setActiveTab("items")}>
                      Next: Add Items
                    </Button>
                  )}
                </div>
              </form>
            </Form>
          </TabsContent>

          <TabsContent value="items">
            <DocumentItemsForm
              items={items}
              setItems={setItems}
              onBack={() => setActiveTab("details")}
              onSubmit={() => onSubmit(form.getValues())}
              isSubmitting={createDocument.isPending}
            />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
