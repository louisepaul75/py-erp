"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useUpdateDocument } from "@/hooks/document/use-documents"
import type { Document, DocumentType } from "@/types/document/document"
import { DocumentItemsForm } from "@/components/document/document-items-form"
import { ArrowLeft, Save } from "lucide-react"
import { useToast } from "@/hooks/document/use-toast"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"

/**
 * Schema for document edit form validation
 */
const formSchema = z.object({
  // Basis-Dokumentinformationen
  type: z.enum(["ORDER", "DELIVERY", "INVOICE", "CREDIT"]),
  number: z.string().min(1, "Document number is required"),
  customerId: z.string().min(1, "Customer is required"),
  date: z.string().min(1, "Date is required"),
  status: z.string().min(1, "Status is required"),
  notes: z.string().optional(),

  // Kundeninformationen
  customerType: z.enum(["B2B", "B2C"]).default("B2B"),
  currency: z.string().default("EUR"),
  language: z.string().default("DE"),

  // Adressen
  billingAddress: z.object({
    name: z.string().min(1, "Name is required"),
    street: z.string().min(1, "Street is required"),
    postalCode: z.string().min(1, "Postal code is required"),
    city: z.string().min(1, "City is required"),
    country: z.string().min(1, "Country is required"),
  }),
  shippingAddress: z.object({
    name: z.string().min(1, "Name is required"),
    street: z.string().min(1, "Street is required"),
    postalCode: z.string().min(1, "Postal code is required"),
    city: z.string().min(1, "City is required"),
    country: z.string().min(1, "Country is required"),
  }),
  sameAddress: z.boolean().default(true),

  // Bestellinformationen
  orderType: z.string().min(1, "Order type is required"),
  shippingMethod: z.string().min(1, "Shipping method is required"),
  paymentMethod: z.string().min(1, "Payment method is required"),

  // Zahlungskonditionen
  paymentTerms: z.object({
    discountDays: z.number().min(0).default(0),
    discountPercentage: z.number().min(0).max(100).default(0),
    netDays: z.number().min(0).default(30),
  }),

  // Zusätzliche Kosten
  shippingCost: z.number().min(0).default(0),
  handlingFee: z.number().min(0).default(0),
  taxRate: z.number().min(0).max(100).default(19),
  taxIncluded: z.boolean().default(true),
})

/**
 * Type for the form values
 */
type FormValues = z.infer<typeof formSchema>

/**
 * Props for the DocumentEditModal component
 */
interface DocumentEditModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  document: Document
}

/**
 * DocumentEditModal component that displays a fullscreen view for editing a document
 */
export function DocumentEditModal({ open, onOpenChange, document }: DocumentEditModalProps) {
  // State for the active tab
  const [activeTab, setActiveTab] = useState<"details" | "items" | "addresses" | "payment" | "shipping">("details")

  // State for document items
  const [items, setItems] = useState(document.items)

  // Toast for notifications
  const { toast } = useToast()

  // Mutation for updating a document
  const updateDocument = useUpdateDocument()

  // Initialize form with react-hook-form and zod validation
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      // Basis-Dokumentinformationen
      type: document.type,
      number: document.number,
      customerId: document.customer.id,
      date: new Date(document.date).toISOString().split("T")[0],
      status: document.status,
      notes: document.notes || "",

      // Kundeninformationen (Beispielwerte)
      customerType: "B2B",
      currency: "EUR",
      language: "DE",

      // Adressen (Beispielwerte)
      billingAddress: {
        name: document.customer.name,
        street: "Musterstraße 123",
        postalCode: "12345",
        city: "Musterstadt",
        country: "Deutschland",
      },
      shippingAddress: {
        name: document.customer.name,
        street: "Musterstraße 123",
        postalCode: "12345",
        city: "Musterstadt",
        country: "Deutschland",
      },
      sameAddress: true,

      // Bestellinformationen (Beispielwerte)
      orderType: "ONLINE",
      shippingMethod: "DHL",
      paymentMethod: "INVOICE",

      // Zahlungskonditionen (Beispielwerte)
      paymentTerms: {
        discountDays: 14,
        discountPercentage: 2,
        netDays: 30,
      },

      // Zusätzliche Kosten (Beispielwerte)
      shippingCost: 5.95,
      handlingFee: 0,
      taxRate: 19,
      taxIncluded: true,
    },
  })

  // Watch for sameAddress changes to sync addresses
  const sameAddress = form.watch("sameAddress")
  const billingAddress = form.watch("billingAddress")

  // Sync shipping address with billing address when sameAddress is true
  const handleBillingAddressChange = (field: keyof typeof billingAddress, value: string) => {
    form.setValue(`billingAddress.${field}`, value)

    if (sameAddress) {
      form.setValue(`shippingAddress.${field}`, value)
    }
  }

  // Handle form submission
  const onSubmit = (values: FormValues) => {
    // Prepare shipping address based on sameAddress flag
    const finalValues = {
      ...values,
      shippingAddress: values.sameAddress ? values.billingAddress : values.shippingAddress,
    }

    updateDocument.mutate(
      {
        id: document.id,
        ...finalValues,
        items,
      },
      {
        onSuccess: () => {
          toast({
            title: "Dokument aktualisiert",
            description: "Das Dokument wurde erfolgreich aktualisiert.",
          })
          onOpenChange(false)
        },
      },
    )
  }

  // Get document type options
  const documentTypes: { value: DocumentType; label: string }[] = [
    { value: "ORDER", label: "Auftrag" },
    { value: "DELIVERY", label: "Lieferschein" },
    { value: "INVOICE", label: "Rechnung" },
    { value: "CREDIT", label: "Gutschrift" },
  ]

  // Get status options based on document type
  const getStatusOptions = (type: DocumentType) => {
    switch (type) {
      case "ORDER":
        return [
          { value: "OPEN", label: "Offen" },
          { value: "CONFIRMED", label: "Bestätigt" },
          { value: "COMPLETED", label: "Abgeschlossen" },
          { value: "CANCELED", label: "Storniert" },
        ]
      case "DELIVERY":
        return [
          { value: "OPEN", label: "Offen" },
          { value: "SHIPPED", label: "Versendet" },
          { value: "DELIVERED", label: "Geliefert" },
          { value: "CANCELED", label: "Storniert" },
        ]
      case "INVOICE":
        return [
          { value: "OPEN", label: "Offen" },
          { value: "PAID", label: "Bezahlt" },
          { value: "CANCELED", label: "Storniert" },
        ]
      case "CREDIT":
        return [
          { value: "OPEN", label: "Offen" },
          { value: "PROCESSED", label: "Verarbeitet" },
          { value: "CANCELED", label: "Storniert" },
        ]
      default:
        return [
          { value: "OPEN", label: "Offen" },
          { value: "COMPLETED", label: "Abgeschlossen" },
          { value: "CANCELED", label: "Storniert" },
        ]
    }
  }

  // Mock customer data
  const customers = [
    { id: "1", name: "Acme Inc." },
    { id: "2", name: "Globex Corporation" },
    { id: "3", name: "Initech" },
    { id: "4", name: "Umbrella Corporation" },
    { id: "5", name: "Stark Industries" },
    { id: "6", name: "Wayne Enterprises" },
    { id: "7", name: "Cyberdyne Systems" },
    { id: "8", name: "Oscorp Industries" },
    { id: "9", name: "Massive Dynamic" },
    { id: "10", name: "Soylent Corp" },
  ]

  // Order type options
  const orderTypeOptions = [
    { value: "ONLINE", label: "Online-Shop" },
    { value: "PHONE", label: "Telefon" },
    { value: "EMAIL", label: "E-Mail" },
    { value: "PERSONAL", label: "Persönlich" },
    { value: "FAX", label: "Fax" },
  ]

  // Shipping method options
  const shippingMethodOptions = [
    { value: "DHL", label: "DHL" },
    { value: "DPD", label: "DPD" },
    { value: "UPS", label: "UPS" },
    { value: "FEDEX", label: "FedEx" },
    { value: "PICKUP", label: "Selbstabholung" },
  ]

  // Payment method options
  const paymentMethodOptions = [
    { value: "INVOICE", label: "Rechnung" },
    { value: "PREPAYMENT", label: "Vorkasse" },
    { value: "CREDIT_CARD", label: "Kreditkarte" },
    { value: "PAYPAL", label: "PayPal" },
    { value: "DIRECT_DEBIT", label: "Lastschrift" },
    { value: "CASH", label: "Barzahlung" },
  ]

  // Language options
  const languageOptions = [
    { value: "DE", label: "Deutsch" },
    { value: "EN", label: "Englisch" },
    { value: "FR", label: "Französisch" },
    { value: "IT", label: "Italienisch" },
    { value: "ES", label: "Spanisch" },
  ]

  // Currency options
  const currencyOptions = [
    { value: "EUR", label: "Euro (€)" },
    { value: "USD", label: "US-Dollar ($)" },
    { value: "GBP", label: "Britisches Pfund (£)" },
    { value: "CHF", label: "Schweizer Franken (CHF)" },
  ]

  // Country options
  const countryOptions = [
    { value: "DE", label: "Deutschland" },
    { value: "AT", label: "Österreich" },
    { value: "CH", label: "Schweiz" },
    { value: "FR", label: "Frankreich" },
    { value: "IT", label: "Italien" },
    { value: "NL", label: "Niederlande" },
    { value: "BE", label: "Belgien" },
    { value: "LU", label: "Luxemburg" },
  ]

  // Get badge color based on document type
  const getTypeColor = (type: DocumentType) => {
    switch (type) {
      case "ORDER":
        return "bg-blue-100 text-blue-800"
      case "DELIVERY":
        return "bg-green-100 text-green-800"
      case "INVOICE":
        return "bg-purple-100 text-purple-800"
      case "CREDIT":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  // Calculate total amount
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  const shippingCost = form.watch("shippingCost") || 0
  const handlingFee = form.watch("handlingFee") || 0
  const taxRate = form.watch("taxRate") || 0
  const taxIncluded = form.watch("taxIncluded")

  const totalBeforeTax = subtotal + shippingCost + handlingFee
  let taxAmount = 0
  let totalAmount = 0

  if (taxIncluded) {
    // Wenn MwSt. bereits enthalten ist, berechnen wir den Nettobetrag und die MwSt.
    taxAmount = totalBeforeTax - totalBeforeTax / (1 + taxRate / 100)
    totalAmount = totalBeforeTax
  } else {
    // Wenn MwSt. nicht enthalten ist, addieren wir sie zum Nettobetrag
    taxAmount = totalBeforeTax * (taxRate / 100)
    totalAmount = totalBeforeTax + taxAmount
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 bg-white overflow-hidden flex flex-col">
      {/* Header */}
      <div className="border-b py-4 px-6 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => onOpenChange(false)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h2 className="text-2xl font-bold">Dokument bearbeiten</h2>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={getTypeColor(document.type)}>{document.type}</Badge>
              <span className="text-sm text-muted-foreground">{document.number}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm font-medium text-muted-foreground">Gesamtbetrag</div>
            <div className="text-xl font-bold">{totalAmount.toFixed(2)} €</div>
          </div>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Abbrechen
          </Button>
          <Button onClick={form.handleSubmit(onSubmit)} disabled={updateDocument.isPending} className="gap-2">
            <Save className="h-4 w-4" />
            Speichern
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <div className="flex overflow-x-auto">
          <button
            className={`px-6 py-4 font-medium text-sm relative whitespace-nowrap ${
              activeTab === "details" ? "text-primary" : "text-muted-foreground"
            }`}
            onClick={() => setActiveTab("details")}
          >
            Dokumentdetails
            {activeTab === "details" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>}
          </button>
          <button
            className={`px-6 py-4 font-medium text-sm relative whitespace-nowrap ${
              activeTab === "addresses" ? "text-primary" : "text-muted-foreground"
            }`}
            onClick={() => setActiveTab("addresses")}
          >
            Adressen
            {activeTab === "addresses" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>}
          </button>
          <button
            className={`px-6 py-4 font-medium text-sm relative whitespace-nowrap ${
              activeTab === "shipping" ? "text-primary" : "text-muted-foreground"
            }`}
            onClick={() => setActiveTab("shipping")}
          >
            Versand & Bestellung
            {activeTab === "shipping" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>}
          </button>
          <button
            className={`px-6 py-4 font-medium text-sm relative whitespace-nowrap ${
              activeTab === "payment" ? "text-primary" : "text-muted-foreground"
            }`}
            onClick={() => setActiveTab("payment")}
          >
            Zahlung & Kosten
            {activeTab === "payment" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>}
          </button>
          <button
            className={`px-6 py-4 font-medium text-sm relative whitespace-nowrap ${
              activeTab === "items" ? "text-primary" : "text-muted-foreground"
            }`}
            onClick={() => setActiveTab("items")}
          >
            Positionen ({items.length})
            {activeTab === "items" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></div>}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto bg-gray-50 p-6">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            {activeTab === "details" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto">
                {/* Document Information */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Dokumentinformationen</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Dokumenttyp</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Dokumenttyp auswählen" />
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
                          <FormLabel>Dokumentnummer</FormLabel>
                          <FormControl>
                            <Input placeholder="z.B. ORD-2023-001" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="status"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Status</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Status auswählen" />
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
                  </div>
                </div>

                {/* Customer Information */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Kundeninformationen</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="customerId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Kunde</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Kunde auswählen" />
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
                          <FormLabel>Datum</FormLabel>
                          <FormControl>
                            <Input type="date" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="customerType"
                      render={({ field }) => (
                        <FormItem className="space-y-3">
                          <FormLabel>Kundentyp</FormLabel>
                          <div>
                            <Badge
                              className={
                                field.value === "B2B" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"
                              }
                            >
                              {field.value === "B2B" ? "Geschäftskunde (B2B)" : "Privatkunde (B2C)"}
                            </Badge>
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Language and Currency */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <circle cx="12" cy="12" r="10" />
                        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                        <path d="M2 12h20" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Sprache und Währung</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="language"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Sprache</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Sprache auswählen" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {languageOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
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
                      name="currency"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Währung</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Währung auswählen" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {currencyOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Additional Information */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Zusätzliche Informationen</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="notes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Notizen</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Zusätzliche Informationen zu diesem Dokument"
                              className="min-h-[120px]"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === "addresses" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto">
                {/* Same Address Toggle */}
                <div className="bg-white p-6 rounded-lg border shadow-sm md:col-span-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="text-primary">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="20"
                          height="20"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                          <polyline points="9 22 9 12 15 12 15 22" />
                        </svg>
                      </div>
                      <h3 className="text-lg font-medium">Adressen</h3>
                    </div>
                    <FormField
                      control={form.control}
                      name="sameAddress"
                      render={({ field }) => (
                        <FormItem className="flex items-center space-x-2 space-y-0">
                          <FormLabel>Lieferadresse gleich Rechnungsadresse</FormLabel>
                          <FormControl>
                            <Switch checked={field.value} onCheckedChange={field.onChange} />
                          </FormControl>
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Billing Address */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Rechnungsadresse</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="billingAddress.name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Name / Firma</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Name oder Firmenname"
                              {...field}
                              onChange={(e) => handleBillingAddressChange("name", e.target.value)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="billingAddress.street"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Straße und Hausnummer</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Straße und Hausnummer"
                              {...field}
                              onChange={(e) => handleBillingAddressChange("street", e.target.value)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="billingAddress.postalCode"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>PLZ</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="Postleitzahl"
                                {...field}
                                onChange={(e) => handleBillingAddressChange("postalCode", e.target.value)}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="billingAddress.city"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Ort</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="Ort"
                                {...field}
                                onChange={(e) => handleBillingAddressChange("city", e.target.value)}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <FormField
                      control={form.control}
                      name="billingAddress.country"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Land</FormLabel>
                          <Select
                            onValueChange={(value) => handleBillingAddressChange("country", value)}
                            defaultValue={field.value}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Land auswählen" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {countryOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Shipping Address */}
                <div className={`bg-white p-6 rounded-lg border shadow-sm ${sameAddress ? "opacity-50" : ""}`}>
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M22 17.5H2" />
                        <path d="M22 21V15c0-4.1-3.9-7-8-7h-4c-4.1 0-8 2.9-8 7v6" />
                        <path d="M16 7V3h-4" />
                        <path d="M8 3v4" />
                        <path d="M2 21h20" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Lieferadresse</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="shippingAddress.name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Name / Firma</FormLabel>
                          <FormControl>
                            <Input placeholder="Name oder Firmenname" {...field} disabled={sameAddress} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="shippingAddress.street"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Straße und Hausnummer</FormLabel>
                          <FormControl>
                            <Input placeholder="Straße und Hausnummer" {...field} disabled={sameAddress} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="shippingAddress.postalCode"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>PLZ</FormLabel>
                            <FormControl>
                              <Input placeholder="Postleitzahl" {...field} disabled={sameAddress} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="shippingAddress.city"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Ort</FormLabel>
                            <FormControl>
                              <Input placeholder="Ort" {...field} disabled={sameAddress} />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>

                    <FormField
                      control={form.control}
                      name="shippingAddress.country"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Land</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value} disabled={sameAddress}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Land auswählen" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {countryOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === "shipping" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto">
                {/* Order Type */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                        <rect width="8" height="4" x="8" y="2" rx="1" ry="1" />
                        <path d="M12 11h4" />
                        <path d="M12 16h4" />
                        <path d="M8 11h.01" />
                        <path d="M8 16h.01" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Bestellart</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="orderType"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Bestellart</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Bestellart auswählen" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {orderTypeOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Shipping Method */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <rect width="16" height="16" x="4" y="4" rx="2" />
                        <path d="M4 13h16" />
                        <path d="M4 9h16" />
                        <path d="M4 17h16" />
                        <path d="M9 4v16" />
                        <path d="M17 4v16" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Versandart</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="shippingMethod"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Versandart</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Versandart auswählen" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {shippingMethodOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === "payment" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl mx-auto">
                {/* Payment Method */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <rect width="20" height="14" x="2" y="5" rx="2" />
                        <line x1="2" x2="22" y1="10" y2="10" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Zahlungsart</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="paymentMethod"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Zahlungsart</FormLabel>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Zahlungsart auswählen" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {paymentMethodOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                  {option.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Payment Terms */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <rect width="18" height="18" x="3" y="3" rx="2" />
                        <path d="M3 9h18" />
                        <path d="M9 21V9" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Zahlungskonditionen</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="paymentTerms.discountDays"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Skonto-Tage</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              min="0"
                              placeholder="z.B. 14"
                              {...field}
                              onChange={(e) => field.onChange(Number.parseInt(e.target.value) || 0)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="paymentTerms.discountPercentage"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Skonto-Prozentsatz (%)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              min="0"
                              max="100"
                              step="0.1"
                              placeholder="z.B. 2"
                              {...field}
                              onChange={(e) => field.onChange(Number.parseFloat(e.target.value) || 0)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="paymentTerms.netDays"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Zahlungsziel (Tage netto)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              min="0"
                              placeholder="z.B. 30"
                              {...field}
                              onChange={(e) => field.onChange(Number.parseInt(e.target.value) || 0)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Additional Costs */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <circle cx="12" cy="12" r="8" />
                        <line x1="12" x2="12" y1="8" y2="12" />
                        <line x1="12" x2="12.01" y1="16" y2="16" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Zusätzliche Kosten</h3>
                  </div>

                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="shippingCost"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Versandkosten</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              min="0"
                              step="0.01"
                              placeholder="z.B. 5.95"
                              {...field}
                              onChange={(e) => field.onChange(Number.parseFloat(e.target.value) || 0)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="handlingFee"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Bearbeitungsgebühr</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              min="0"
                              step="0.01"
                              placeholder="z.B. 2.50"
                              {...field}
                              onChange={(e) => field.onChange(Number.parseFloat(e.target.value) || 0)}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Tax Settings */}
                <div className="bg-white p-6 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z" />
                        <path d="M13 5v2" />
                        <path d="M13 17v2" />
                        <path d="M13 11v2" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">MwSt-Einstellungen</h3>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">MwSt-Satz (%)</label>
                      <div className="p-2 border rounded-md bg-gray-50 mt-1.5">{form.getValues("taxRate")}%</div>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Preise</label>
                      <div className="p-2 border rounded-md bg-gray-50 mt-1.5">
                        {form.getValues("taxIncluded") ? "inkl. MwSt." : "exkl. MwSt."}
                      </div>
                    </div>

                    {form.getValues("customerType") === "B2B" && (
                      <>
                        <div>
                          <label className="text-sm font-medium">USt-ID</label>
                          <div className="p-2 border rounded-md bg-gray-50 mt-1.5">DE123456789</div>
                        </div>
                        <div>
                          <label className="text-sm font-medium">USt-ID Status</label>
                          <div className="flex items-center gap-2 mt-1.5">
                            <Badge className="bg-green-100 text-green-800">Bestätigt</Badge>
                            <span className="text-xs text-muted-foreground">Geprüft am 01.03.2024</span>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Summary */}
                <div className="bg-white p-6 rounded-lg border shadow-sm md:col-span-2">
                  <div className="flex items-center gap-2 mb-6">
                    <div className="text-primary">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M3 3v18h18" />
                        <path d="m19 9-5 5-4-4-3 3" />
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium">Zusammenfassung</h3>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Zwischensumme:</span>
                      <span>{subtotal.toFixed(2)} €</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Versandkosten:</span>
                      <span>{shippingCost.toFixed(2)} €</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Bearbeitungsgebühr:</span>
                      <span>{handlingFee.toFixed(2)} €</span>
                    </div>
                    <div className="flex justify-between">
                      <span>MwSt. ({taxRate}%):</span>
                      <span>{taxAmount.toFixed(2)} €</span>
                    </div>
                    <div className="h-px bg-gray-200 my-2"></div>
                    <div className="flex justify-between font-bold">
                      <span>Gesamtbetrag:</span>
                      <span>{totalAmount.toFixed(2)} €</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "items" && (
              <div className="max-w-6xl mx-auto">
                <DocumentItemsForm
                  items={items}
                  setItems={setItems}
                  onBack={() => setActiveTab("details")}
                  onSubmit={form.handleSubmit(onSubmit)}
                  isSubmitting={updateDocument.isPending}
                  shippingCost={form.watch("shippingCost")}
                  setShippingCost={(value) => form.setValue("shippingCost", value)}
                  handlingFee={form.watch("handlingFee")}
                  setHandlingFee={(value) => form.setValue("handlingFee", value)}
                  taxRate={form.watch("taxRate")}
                  taxIncluded={form.watch("taxIncluded")}
                />
              </div>
            )}
          </form>
        </Form>
      </div>
    </div>
  )
}
