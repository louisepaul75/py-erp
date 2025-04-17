"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/document/use-toast"
import { useDocuments, useCreateDocument } from "@/hooks/document/use-documents"
import { OrderSplitHeader } from "@/components/document/order-split/order-split-header"
import { OrderSplitSourceItems } from "@/components/document/order-split/order-split-source-items"
import { OrderSplitNewOrder } from "@/components/document/order-split/order-split-new-order"

/**
 * Props for the OrderSplitView component
 */
interface OrderSplitViewProps {
  onClose: () => void
  sourceDocumentId: string // Required: The order to split
}

/**
 * OrderSplitView component that displays a view for splitting an order
 * It allows selecting specific items to move to a new order
 */
export function OrderSplitView({ onClose, sourceDocumentId }: OrderSplitViewProps) {
  const { toast } = useToast()
  const { data: documents } = useDocuments()
  const createDocument = useCreateDocument()

  // Get the source document
  const sourceDocument = documents?.find((doc) => doc.id === sourceDocumentId)

  // State for selected items to move to the new order
  const [selectedItems, setSelectedItems] = useState<Record<string, boolean>>({})

  // State for new order details
  const [newOrderNumber, setNewOrderNumber] = useState("")
  const [newOrderDate, setNewOrderDate] = useState(new Date().toISOString().split("T")[0])
  const [newOrderStatus, setNewOrderStatus] = useState("OPEN")
  const [newOrderNotes, setNewOrderNotes] = useState("")

  // Initialize selected items when source document changes
  useEffect(() => {
    if (sourceDocument) {
      const newSelectedItems: Record<string, boolean> = {}
      sourceDocument.items.forEach((item) => {
        newSelectedItems[item.id] = false
      })
      setSelectedItems(newSelectedItems)
    }
  }, [sourceDocument])

  // Get selected items list
  const selectedItemsList = sourceDocument?.items.filter((item) => selectedItems[item.id]) || []

  // Calculate total amount for selected items
  const selectedAmount = selectedItemsList.reduce((total, item) => total + item.price * item.quantity, 0)

  // Calculate remaining amount
  const remainingAmount = (sourceDocument?.amount || 0) - selectedAmount

  // Toggle item selection
  const toggleItemSelection = (itemId: string) => {
    setSelectedItems({
      ...selectedItems,
      [itemId]: !selectedItems[itemId],
    })
  }

  // Toggle all items
  const toggleAllItems = (value: boolean) => {
    if (sourceDocument) {
      const newSelectedItems: Record<string, boolean> = {}
      sourceDocument.items.forEach((item) => {
        newSelectedItems[item.id] = value
      })
      setSelectedItems(newSelectedItems)
    }
  }

  // Split order
  const splitOrder = async () => {
    try {
      if (!sourceDocument) {
        toast({
          title: "Fehler",
          description: "Quelldokument nicht gefunden.",
          variant: "destructive",
        })
        return
      }

      if (selectedItemsList.length === 0) {
        toast({
          title: "Fehler",
          description: "Bitte wählen Sie mindestens eine Position aus.",
          variant: "destructive",
        })
        return
      }

      if (!newOrderNumber) {
        toast({
          title: "Fehler",
          description: "Bitte geben Sie eine Auftragsnummer ein.",
          variant: "destructive",
        })
        return
      }

      // Create new order with selected items
      createDocument.mutate(
        {
          type: "ORDER",
          number: newOrderNumber,
          customerId: sourceDocument.customer.id,
          date: newOrderDate,
          status: newOrderStatus,
          notes: newOrderNotes || `Auftrag erstellt durch Splitting von ${sourceDocument.number}`,
          items: selectedItemsList,
          amount: selectedAmount,
        },
        {
          onSuccess: () => {
            toast({
              title: "Auftrag gesplittet",
              description: `Neuer Auftrag ${newOrderNumber} wurde erfolgreich erstellt.`,
            })
            onClose()
          },
        },
      )
    } catch (error) {
      toast({
        title: "Fehler",
        description: `Fehler beim Splitten des Auftrags: ${error instanceof Error ? error.message : "Unbekannter Fehler"}`,
        variant: "destructive",
      })
    }
  }

  // Get status options
  const statusOptions = [
    { value: "OPEN", label: "Offen" },
    { value: "CONFIRMED", label: "Bestätigt" },
    { value: "COMPLETED", label: "Abgeschlossen" },
    { value: "CANCELED", label: "Storniert" },
  ]

  if (!sourceDocument) {
    return (
      <div className="flex flex-col h-full bg-gray-50 items-center justify-center">
        <div className="w-96 p-6 bg-white rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Fehler</h3>
          <p className="text-muted-foreground">Der ausgewählte Auftrag wurde nicht gefunden.</p>
          <Button className="w-full mt-4" onClick={onClose}>
            Schließen
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <OrderSplitHeader
        sourceDocument={sourceDocument}
        selectedItemsCount={selectedItemsList.length}
        selectedAmount={selectedAmount}
      />

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left panel - Source order items */}
        <div className="w-1/2 border-r bg-white overflow-auto">
          <div className="p-6">
            <OrderSplitSourceItems
              sourceDocument={sourceDocument}
              selectedItems={selectedItems}
              toggleItemSelection={toggleItemSelection}
              toggleAllItems={toggleAllItems}
              remainingAmount={remainingAmount}
            />
          </div>
        </div>

        {/* Right panel - New order details */}
        <div className="w-1/2 bg-white overflow-auto">
          <div className="p-6">
            <OrderSplitNewOrder
              sourceDocument={sourceDocument}
              newOrderNumber={newOrderNumber}
              setNewOrderNumber={setNewOrderNumber}
              newOrderDate={newOrderDate}
              setNewOrderDate={setNewOrderDate}
              newOrderStatus={newOrderStatus}
              setNewOrderStatus={setNewOrderStatus}
              newOrderNotes={newOrderNotes}
              setNewOrderNotes={setNewOrderNotes}
              statusOptions={statusOptions}
              selectedItemsList={selectedItemsList}
              selectedAmount={selectedAmount}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t shadow-sm p-4">
        <div className="container mx-auto flex justify-between items-center">
          <Button variant="outline" size="lg" onClick={onClose}>
            Abbrechen
          </Button>
          <Button
            size="lg"
            onClick={splitOrder}
            disabled={selectedItemsList.length === 0 || !newOrderNumber || !newOrderDate || createDocument.isPending}
            className="px-8"
          >
            {createDocument.isPending ? "Wird erstellt..." : "Auftrag splitten"}
          </Button>
        </div>
      </div>
    </div>
  )
}
