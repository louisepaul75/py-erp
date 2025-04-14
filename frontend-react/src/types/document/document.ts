/**
 * Document types
 */
export type DocumentType = "ORDER" | "DELIVERY" | "INVOICE" | "CREDIT"

/**
 * Document item interface
 */
export interface DocumentItem {
  id: string
  productId: string
  description: string
  quantity: number
  price: number
  status?: string // z.B. "CANCELED" für stornierte Positionen
}

/**
 * Customer interface
 */
export interface Customer {
  id: string
  name: string
}

/**
 * Payment status for invoices
 */
export type PaymentStatus = "PAID" | "OPEN" | "OVERDUE" | "REMINDER_1" | "REMINDER_2" | "REMINDER_3" | "COLLECTION"

/**
 * Payment information interface
 */
export interface PaymentInfo {
  method: string // "INVOICE", "PREPAYMENT", "CREDIT_CARD", "PAYPAL", etc.
  dueDate?: string // Fälligkeitsdatum
  paymentDate?: string // Tatsächliches Zahlungsdatum
  status: PaymentStatus
  remindersSent?: number // Anzahl der gesendeten Mahnungen
  lastReminderDate?: string // Datum der letzten Mahnung
}

/**
 * Document interface
 */
export interface Document {
  id: string
  type: DocumentType
  number: string
  date: string
  status: string
  customer: Customer
  amount: number
  items: DocumentItem[]
  notes?: string
  paymentInfo?: PaymentInfo // Zahlungsinformationen für Rechnungen
}

/**
 * Document relationship interface
 */
export interface DocumentRelationship {
  id: string
  sourceId: string
  targetId: string
  relationType: string
  relatedDocument: Document
}
