"use client"

import { memo } from "react"
import { Handle, Position } from "reactflow"
import { Badge } from "@/components/ui/badge"
import type { DocumentType } from "@/types/document/document"
import { formatDate } from "@/lib/utils"

/**
 * Props for the DocumentNode component
 */
interface DocumentNodeProps {
  data: {
    id: string
    number: string
    type: DocumentType
    date: string
    status: string
    amount: number
    customer: {
      id: string
      name: string
    }
    selected: boolean
    onSelect: () => void
  }
}

/**
 * DocumentNode component that displays a node in the document flow diagram
 * This component is memoized to prevent unnecessary re-renders
 */
export const DocumentNode = memo(({ data }: DocumentNodeProps) => {
  // Get background color based on document type
  const getBackgroundColor = (type: DocumentType) => {
    switch (type) {
      case "ORDER":
        return "bg-blue-50 border-blue-200"
      case "DELIVERY":
        return "bg-green-50 border-green-200"
      case "INVOICE":
        return "bg-purple-50 border-purple-200"
      case "CREDIT":
        return "bg-red-50 border-red-200"
      default:
        return "bg-gray-50 border-gray-200"
    }
  }

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
    <div
      className={`p-3 rounded-md border-2 shadow-sm ${getBackgroundColor(data.type)} ${
        data.selected ? "ring-2 ring-offset-2 ring-primary" : ""
      }`}
      style={{ width: 220 }}
      onClick={data.onSelect}
    >
      <Handle type="target" position={Position.Top} className="!bg-gray-400" />

      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-start">
          <Badge className={getTypeColor(data.type)}>{data.type}</Badge>
          <Badge className={getStatusColor(data.status)}>{data.status}</Badge>
        </div>

        <div className="font-medium text-sm">{data.number}</div>

        <div className="text-xs text-muted-foreground">{data.customer.name}</div>

        <div className="flex justify-between text-xs">
          <span>{formatDate(data.date)}</span>
          <span className="font-medium">{data.amount.toFixed(2)} €</span>
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-gray-400" />
    </div>
  )
})

DocumentNode.displayName = "DocumentNode"
