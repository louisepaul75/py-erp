"use client"

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import type { Document, DocumentType, PaymentStatus } from "@/types/document/document"
import { formatDate } from "@/lib/utils"
import { DocumentActions } from "@/components/document/document-actions"
import {
  calculatePaymentStatus,
  getPaymentStatusText,
  getPaymentStatusColor,
} from "@/lib/payment-utils"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Clock } from "lucide-react"

/**
 * Props for the DocumentTable component
 */
interface DocumentTableProps {
  documents: Document[]
  onView: (document: Document) => void
  onEdit: (document: Document) => void
  onCancelDocument: (document: Document) => void
  onViewFlow?: (document: Document) => void
  onSplitOrder: (document: Document) => void
  onMergeOrders: (document: Document) => void
  onCreateCollectiveInvoice: (document: Document) => void
  onCreateDeliveryNote: (document: Document) => void
  onCreateCreditNote: (document: Document) => void
  onCancelOrder: (document: Document) => void
  onExecuteAction: (document: Document, title: string, description: string, action: () => Promise<void>) => void
}

/**
 * DocumentTable component that displays a table of documents
 */
export function DocumentTable({
  documents,
  onView,
  onEdit,
  onCancelDocument,
  onViewFlow,
  onSplitOrder,
  onMergeOrders,
  onCreateCollectiveInvoice,
  onCreateDeliveryNote,
  onCreateCreditNote,
  onCancelOrder,
  onExecuteAction,
}: DocumentTableProps) {
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

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Number</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Customer</TableHead>
          <TableHead>Date</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Payment</TableHead>
          <TableHead>Amount</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {documents.map((document) => {
          // Berechne den Zahlungsstatus für Rechnungen
          const paymentStatus = document.type === "INVOICE" ? calculatePaymentStatus(document) : null
          const isInvoiceWithPaymentMethod = document.type === "INVOICE" && document.paymentInfo?.method === "INVOICE"

          return (
            <TableRow key={document.id}>
              <TableCell className="font-medium">{document.number}</TableCell>
              <TableCell>
                <Badge className={getTypeColor(document.type)}>{document.type}</Badge>
              </TableCell>
              <TableCell>{document.customer.name}</TableCell>
              <TableCell>{formatDate(document.date)}</TableCell>
              <TableCell>
                <Badge className={getStatusColor(document.status)}>{document.status}</Badge>
              </TableCell>
              <TableCell>
                {document.type === "INVOICE" ? (
                  document.paymentInfo?.method === "INVOICE" &&
                  paymentStatus &&
                  paymentStatus !== "OPEN" &&
                  paymentStatus !== "PAID" ? (
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Badge className={getPaymentStatusColor(paymentStatus as PaymentStatus)}>
                            {getPaymentStatusText(paymentStatus as PaymentStatus)}
                          </Badge>
                        </TooltipTrigger>
                        <TooltipContent>
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            <span>
                              Fällig seit:{" "}
                              {document.paymentInfo?.dueDate ? formatDate(document.paymentInfo.dueDate) : "Unbekannt"}
                            </span>
                          </div>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  ) : (
                    <span className="text-sm text-muted-foreground">
                      {document.paymentInfo?.method || "Keine Zahlungsart"}
                    </span>
                  )
                ) : null}
              </TableCell>
              <TableCell>{document.amount.toFixed(2)} €</TableCell>
              <TableCell className="text-right">
                <DocumentActions
                  document={document}
                  onView={() => onView(document)}
                  onEdit={() => onEdit(document)}
                  onCancelDocument={() => onCancelDocument(document)}
                  onViewFlow={onViewFlow ? () => onViewFlow(document) : undefined}
                  onSplitOrder={() => onSplitOrder(document)}
                  onMergeOrders={() => onMergeOrders(document)}
                  onCreateCollectiveInvoice={() => onCreateCollectiveInvoice(document)}
                  onCreateDeliveryNote={() => onCreateDeliveryNote(document)}
                  onCreateCreditNote={() => onCreateCreditNote(document)}
                  onCancelOrder={() => onCancelOrder(document)}
                  onExecuteAction={(title, description, action) =>
                    onExecuteAction(document, title, description, action)
                  }
                />
              </TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}
