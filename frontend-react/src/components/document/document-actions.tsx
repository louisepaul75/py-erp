"use client"

import { Button } from "@/components/ui/button"
import {
  Eye,
  Edit,
  MoreHorizontal,
  Truck,
  Receipt,
  Split,
  Combine,
  Plus,
  RotateCcw,
  CreditCard,
  GitBranch,
  XCircle,
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import type { Document } from "@/types/document/document"

/**
 * Props for the DocumentActions component
 */
interface DocumentActionsProps {
  document: Document
  onView: () => void
  onEdit: () => void
  onCancelDocument: () => void
  onViewFlow?: () => void
  onSplitOrder: () => void
  onMergeOrders: () => void
  onCreateCollectiveInvoice: () => void
  onCreateDeliveryNote: () => void
  onCreateCreditNote: () => void
  onCancelOrder: () => void // New function for order cancellation
  onExecuteAction: (title: string, description: string, action: () => Promise<void>) => void
}

/**
 * DocumentActions component that displays actions for a document
 */
export function DocumentActions({
  document,
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
}: DocumentActionsProps) {
  // Document action functions
  const createDeliveryFromOrder = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Lieferschein aus Auftrag erstellen", document.id)
  }

  const extendOrder = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Auftrag ergänzen", document.id)
  }

  const cancelOrder = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Auftrag stornieren", document.id)
  }

  const createInvoiceFromDelivery = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Rechnung aus Lieferschein erstellen", document.id)
  }

  const createPartialDelivery = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Teillieferung erstellen", document.id)
  }

  const createCollectiveDelivery = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Sammellieferung erstellen", document.id)
  }

  const cancelDelivery = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Lieferschein stornieren", document.id)
  }

  const createReturn = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Retoure erstellen", document.id)
  }

  const cancelInvoice = async () => {
    // Simulation of API call
    await new Promise((resolve) => setTimeout(resolve, 1000))
    console.log("Rechnung stornieren", document.id)
  }

  return (
    <div className="flex justify-end gap-2">
      <Button variant="ghost" size="icon" onClick={onView}>
        <Eye className="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" onClick={onEdit}>
        <Edit className="h-4 w-4" />
      </Button>
      {/* Removed delete button */}
      {onViewFlow && (
        <Button variant="ghost" size="icon" onClick={onViewFlow}>
          <GitBranch className="h-4 w-4" />
        </Button>
      )}

      {/* Document Actions Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>Dokument-Aktionen</DropdownMenuLabel>
          <DropdownMenuSeparator />

          {/* ORDER specific actions */}
          {document.type === "ORDER" && (
            <>
              <DropdownMenuGroup>
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground px-2 py-1.5">
                  Auftragsvorgänge
                </DropdownMenuLabel>
                <DropdownMenuItem onClick={onSplitOrder}>
                  <Split className="mr-2 h-4 w-4" />
                  <span>Auftrag splitten</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onMergeOrders}>
                  <Combine className="mr-2 h-4 w-4" />
                  <span>Zusammenführen</span>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() =>
                    onExecuteAction(
                      "Auftrag ergänzen",
                      `Möchten Sie den Auftrag ${document.number} ergänzen?`,
                      extendOrder,
                    )
                  }
                >
                  <Plus className="mr-2 h-4 w-4" />
                  <span>Ergänzen</span>
                </DropdownMenuItem>
                {/* New option for canceling order with positions */}
                <DropdownMenuItem onClick={onCancelOrder}>
                  <XCircle className="mr-2 h-4 w-4 text-destructive" />
                  <span>Auftrag/Positionen stornieren</span>
                </DropdownMenuItem>
              </DropdownMenuGroup>

              <DropdownMenuSeparator />

              <DropdownMenuGroup>
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground px-2 py-1.5">
                  Lieferprozesse
                </DropdownMenuLabel>
                <DropdownMenuItem onClick={onCreateDeliveryNote}>
                  <Truck className="mr-2 h-4 w-4" />
                  <span>Lieferschein erstellen</span>
                </DropdownMenuItem>
              </DropdownMenuGroup>
            </>
          )}

          {/* DELIVERY specific actions */}
          {document.type === "DELIVERY" && (
            <>
              <DropdownMenuGroup>
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground px-2 py-1.5">
                  Lieferprozesse
                </DropdownMenuLabel>
                <DropdownMenuItem
                  onClick={() =>
                    onExecuteAction(
                      "Retoure erstellen",
                      `Möchten Sie für den Lieferschein ${document.number} eine Retoure erstellen?`,
                      createReturn,
                    )
                  }
                >
                  <RotateCcw className="mr-2 h-4 w-4" />
                  <span>Retoure erstellen</span>
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() =>
                    onExecuteAction(
                      "Sammellieferung erstellen",
                      `Möchten Sie eine Sammellieferung mit ${document.number} erstellen?`,
                      createCollectiveDelivery,
                    )
                  }
                >
                  <Combine className="mr-2 h-4 w-4" />
                  <span>Sammellieferung</span>
                </DropdownMenuItem>
              </DropdownMenuGroup>

              <DropdownMenuSeparator />

              <DropdownMenuGroup>
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground px-2 py-1.5">
                  Fakturierung
                </DropdownMenuLabel>
                <DropdownMenuItem
                  onClick={() =>
                    onExecuteAction(
                      "Rechnung aus Lieferschein erstellen",
                      `Möchten Sie aus dem Lieferschein ${document.number} eine Rechnung erstellen?`,
                      createInvoiceFromDelivery,
                    )
                  }
                >
                  <Receipt className="mr-2 h-4 w-4" />
                  <span>Rechnung erstellen</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onCreateCollectiveInvoice}>
                  <Combine className="mr-2 h-4 w-4" />
                  <span>Sammelrechnung erstellen</span>
                </DropdownMenuItem>
              </DropdownMenuGroup>
            </>
          )}

          {/* INVOICE specific actions */}
          {document.type === "INVOICE" && (
            <>
              <DropdownMenuGroup>
                <DropdownMenuLabel className="text-xs font-normal text-muted-foreground px-2 py-1.5">
                  Fakturierung
                </DropdownMenuLabel>
                <DropdownMenuItem onClick={onCreateCreditNote}>
                  <CreditCard className="mr-2 h-4 w-4" />
                  <span>Gutschrift erstellen</span>
                </DropdownMenuItem>
              </DropdownMenuGroup>
            </>
          )}

          {/* Common actions for all document types */}
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuLabel className="text-xs font-normal text-muted-foreground px-2 py-1.5">
              Allgemeine Aktionen
            </DropdownMenuLabel>
            {document.status !== "CANCELED" && (
              <DropdownMenuItem onClick={onCancelDocument}>
                <XCircle className="mr-2 h-4 w-4 text-destructive" />
                <span>Dokument stornieren</span>
              </DropdownMenuItem>
            )}
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
