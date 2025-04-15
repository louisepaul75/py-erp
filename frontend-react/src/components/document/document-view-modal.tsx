"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import type { Document, DocumentType, PaymentStatus } from "@/types/document/document"
import { formatDate } from "@/lib/utils"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useState } from "react"
import { DocumentRelatedList } from "@/components/document/document-related-list"
import { DocumentHistory } from "@/components/document/document-history"
import {
  calculateDaysOverdue,
  calculatePaymentStatus,
  getPaymentStatusColor,
  getPaymentStatusText,
} from "@/lib/payment-utils"
import { AlertCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

/**
 * Props for the DocumentViewModal component
 */
interface DocumentViewModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  document: Document
}

/**
 * DocumentViewModal component that displays a modal with document details
 */
export function DocumentViewModal({ open, onOpenChange, document }: DocumentViewModalProps) {
  // State for the active tab
  const [activeTab, setActiveTab] = useState("details")

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

  // Get badge color based on document status
  const getStatusColor = (status: string) => {
    switch (status) {
      case "OPEN":
        return "bg-yellow-100 text-yellow-800"
      case "COMPLETED":
        return "bg-green-100 text-green-800"
      case "CANCELED":
        return "bg-red-100 text-red-800"
      case "PAID":
        return "bg-blue-100 text-blue-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  // Calculate the total amount
  const calculateTotal = () => {
    return document.items.reduce((total, item) => total + item.quantity * item.price, 0)
  }

  // Berechne den Zahlungsstatus für Rechnungen
  const paymentStatus = document.type === "INVOICE" ? calculatePaymentStatus(document) : null
  const daysOverdue = document.type === "INVOICE" ? calculateDaysOverdue(document) : null
  const isInvoiceWithPaymentMethod = document.type === "INVOICE" && document.paymentInfo?.method === "INVOICE"

  // Berechne den Fortschritt für die Mahnstufen
  const getReminderProgress = () => {
    if (!paymentStatus) return 0

    switch (paymentStatus) {
      case "PAID":
        return 100
      case "OPEN":
        return 0
      case "OVERDUE":
        return 20
      case "REMINDER_1":
        return 40
      case "REMINDER_2":
        return 60
      case "REMINDER_3":
        return 80
      case "COLLECTION":
        return 100
      default:
        return 0
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>Document Details</DialogTitle>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="details">Document Details</TabsTrigger>
            <TabsTrigger value="payment" disabled={document.type !== "INVOICE"}>
              Payment Info
            </TabsTrigger>
            <TabsTrigger value="related">Related Documents</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium">Document Type</p>
                  <Badge className={getTypeColor(document.type)}>{document.type}</Badge>
                </div>
                <div>
                  <p className="text-sm font-medium">Document Number</p>
                  <p>{document.number}</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Customer</p>
                  <p>{document.customer.name}</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Date</p>
                  <p>{formatDate(document.date)}</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Status</p>
                  <Badge className={getStatusColor(document.status)}>{document.status}</Badge>
                </div>
                <div>
                  <p className="text-sm font-medium">Total Amount</p>
                  <p className="font-bold">{calculateTotal().toFixed(2)} €</p>
                </div>

                {isInvoiceWithPaymentMethod && paymentStatus && (
                  <div className="col-span-2">
                    <p className="text-sm font-medium">Payment Status</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={getPaymentStatusColor(paymentStatus as PaymentStatus)}>
                        {getPaymentStatusText(paymentStatus as PaymentStatus)}
                      </Badge>
                      {daysOverdue && daysOverdue > 0 && (
                        <span className="text-sm text-muted-foreground">
                          ({daysOverdue} {daysOverdue === 1 ? "Tag" : "Tage"} überfällig)
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {document.notes && (
                <div>
                  <p className="text-sm font-medium">Notes</p>
                  <p className="text-sm text-muted-foreground">{document.notes}</p>
                </div>
              )}

              <div className="border rounded-md">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Product ID</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Total</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {document.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.productId}</TableCell>
                        <TableCell>{item.description}</TableCell>
                        <TableCell>{item.quantity}</TableCell>
                        <TableCell>{item.price.toFixed(2)} €</TableCell>
                        <TableCell>{(item.quantity * item.price).toFixed(2)} €</TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell colSpan={4} className="text-right font-bold">
                        Total:
                      </TableCell>
                      <TableCell className="font-bold">{calculateTotal().toFixed(2)} €</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="payment">
            {document.type === "INVOICE" && (
              <div className="space-y-6 py-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Zahlungsinformationen</CardTitle>
                    <CardDescription>Details zur Zahlung und zum aktuellen Status</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm font-medium">Zahlungsart</p>
                        <p>{document.paymentInfo?.method || "Keine Zahlungsart angegeben"}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Zahlungsstatus</p>
                        {paymentStatus ? (
                          <Badge className={getPaymentStatusColor(paymentStatus as PaymentStatus)}>
                            {getPaymentStatusText(paymentStatus as PaymentStatus)}
                          </Badge>
                        ) : (
                          <span>Unbekannt</span>
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium">Fälligkeitsdatum</p>
                        <p>
                          {document.paymentInfo?.dueDate ? formatDate(document.paymentInfo.dueDate) : "Nicht angegeben"}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Zahlungsdatum</p>
                        <p>
                          {document.paymentInfo?.paymentDate
                            ? formatDate(document.paymentInfo.paymentDate)
                            : "Noch nicht bezahlt"}
                        </p>
                      </div>
                    </div>

                    {document.paymentInfo?.method === "INVOICE" &&
                      paymentStatus &&
                      paymentStatus !== "PAID" &&
                      paymentStatus !== "OPEN" && (
                        <>
                          <div className="mt-6">
                            <div className="flex justify-between mb-2">
                              <span className="text-sm font-medium">Mahnstatus</span>
                              <span className="text-sm text-muted-foreground">
                                {daysOverdue && daysOverdue > 0
                                  ? `${daysOverdue} ${daysOverdue === 1 ? "Tag" : "Tage"} überfällig`
                                  : ""}
                              </span>
                            </div>
                            <Progress value={getReminderProgress()} className="h-2" />
                            <div className="flex justify-between mt-1 text-xs text-muted-foreground">
                              <span>Fällig</span>
                              <span>1. Mahnung</span>
                              <span>2. Mahnung</span>
                              <span>3. Mahnung</span>
                              <span>Inkasso</span>
                            </div>
                          </div>

                          <div className="bg-amber-50 border border-amber-200 rounded-md p-4 mt-4">
                            <div className="flex gap-2">
                              <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                              <div>
                                <h4 className="font-medium text-amber-800">Zahlungserinnerung</h4>
                                <p className="text-sm text-amber-700 mt-1">
                                  {paymentStatus === "OVERDUE" &&
                                    "Die Zahlung ist überfällig. Eine Zahlungserinnerung sollte gesendet werden."}
                                  {paymentStatus === "REMINDER_1" &&
                                    "Die erste Mahnung wurde gesendet. Falls keine Zahlung erfolgt, wird die zweite Mahnung fällig."}
                                  {paymentStatus === "REMINDER_2" &&
                                    "Die zweite Mahnung wurde gesendet. Falls keine Zahlung erfolgt, wird die dritte Mahnung fällig."}
                                  {paymentStatus === "REMINDER_3" &&
                                    "Die dritte Mahnung wurde gesendet. Falls keine Zahlung erfolgt, wird der Vorgang an das Inkasso übergeben."}
                                  {paymentStatus === "COLLECTION" && "Der Vorgang wurde an das Inkasso übergeben."}
                                </p>
                                {document.paymentInfo?.lastReminderDate && (
                                  <p className="text-sm text-amber-700 mt-2">
                                    Letzte Mahnung gesendet am: {formatDate(document.paymentInfo.lastReminderDate)}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        </>
                      )}
                  </CardContent>
                </Card>

                {document.paymentInfo?.method === "INVOICE" && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Zahlungsbedingungen</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm font-medium">Zahlungsziel</p>
                          <p>30 Tage netto</p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">Skonto</p>
                          <p>2% bei Zahlung innerhalb von 14 Tagen</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="related">
            <DocumentRelatedList documentId={document.id} />
          </TabsContent>

          <TabsContent value="history">
            <DocumentHistory documentId={document.id} />
          </TabsContent>
        </Tabs>

        <div className="flex justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
