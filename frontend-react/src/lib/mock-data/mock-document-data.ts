import type { Document, DocumentRelationship } from "@/types/document"

/**
 * Mock customer data
 */
const mockCustomers = [
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

/**
 * Mock document items
 */
const mockItems = [
  { id: "item-1", productId: "PROD-100", description: "Laptop Computer", quantity: 2, price: 1200 },
  { id: "item-2", productId: "PROD-101", description: "Wireless Mouse", quantity: 5, price: 25 },
  { id: "item-3", productId: "PROD-102", description: "Office Chair", quantity: 1, price: 300 },
  { id: "item-4", productId: "PROD-103", description: "4K Monitor", quantity: 3, price: 450 },
  { id: "item-5", productId: "PROD-104", description: "Keyboard", quantity: 4, price: 75 },
  { id: "item-6", productId: "PROD-105", description: "Webcam", quantity: 2, price: 60 },
  { id: "item-7", productId: "PROD-106", description: "USB Hub", quantity: 10, price: 15 },
  { id: "item-8", productId: "PROD-107", description: "External Hard Drive", quantity: 3, price: 120 },
  { id: "item-9", productId: "PROD-108", description: "Printer", quantity: 1, price: 200 },
  { id: "item-10", productId: "PROD-109", description: "Scanner", quantity: 1, price: 150 },
]

/**
 * Mock documents
 */
export const mockDocuments: Document[] = [
  {
    id: "doc-1",
    type: "ORDER",
    number: "ORD-2023-001",
    date: "2023-01-15",
    status: "OPEN",
    customer: mockCustomers[0],
    amount: 2400,
    items: [mockItems[0], mockItems[1]],
    notes: "Rush order",
  },
  {
    id: "doc-2",
    type: "DELIVERY",
    number: "DEL-2023-001",
    date: "2023-01-18",
    status: "SHIPPED",
    customer: mockCustomers[0],
    amount: 2400,
    items: [mockItems[0], mockItems[1]],
    notes: "Partial delivery",
  },
  {
    id: "doc-3",
    type: "INVOICE",
    number: "INV-2023-001",
    date: "2023-01-25",
    status: "OPEN",
    customer: mockCustomers[0],
    amount: 2400,
    items: [mockItems[0], mockItems[1]],
    notes: "Payment due in 30 days",
  },
  {
    id: "doc-4",
    type: "CREDIT",
    number: "CRD-2023-001",
    date: "2023-02-01",
    status: "OPEN",
    customer: mockCustomers[0],
    amount: 1200,
    items: [mockItems[0]],
    notes: "Credit for damaged item",
  },
  {
    id: "doc-5",
    type: "ORDER",
    number: "ORD-2023-002",
    date: "2023-02-10",
    status: "CONFIRMED",
    customer: mockCustomers[1],
    amount: 1500,
    items: [mockItems[2], mockItems[3]],
    notes: "Customer requested expedited shipping",
  },
  {
    id: "doc-6",
    type: "DELIVERY",
    number: "DEL-2023-002",
    date: "2023-02-12",
    status: "SHIPPED",
    customer: mockCustomers[1],
    amount: 1500,
    items: [mockItems[2], mockItems[3]],
    notes: "Shipped via UPS",
  },
  {
    id: "doc-7",
    type: "INVOICE",
    number: "INV-2023-002",
    date: "2023-02-20",
    status: "OPEN",
    customer: mockCustomers[1],
    amount: 1500,
    items: [mockItems[2], mockItems[3]],
    notes: "Net 30 terms",
  },
  {
    id: "doc-8",
    type: "ORDER",
    number: "ORD-2023-003",
    date: "2023-03-01",
    status: "OPEN",
    customer: mockCustomers[2],
    amount: 800,
    items: [mockItems[4], mockItems[5]],
    notes: "New customer",
  },
  {
    id: "doc-9",
    type: "DELIVERY",
    number: "DEL-2023-003",
    date: "2023-03-03",
    status: "DELIVERED",
    customer: mockCustomers[2],
    amount: 800,
    items: [mockItems[4], mockItems[5]],
    notes: "Delivered to front desk",
  },
  {
    id: "doc-10",
    type: "INVOICE",
    number: "INV-2023-003",
    date: "2023-03-10",
    status: "PAID",
    customer: mockCustomers[2],
    amount: 800,
    items: [mockItems[4], mockItems[5]],
    notes: "Paid in full",
  },
  {
    id: "doc-11",
    type: "ORDER",
    number: "ORD-2023-004",
    date: "2023-03-15",
    status: "OPEN",
    customer: mockCustomers[3],
    amount: 3000,
    items: [mockItems[6], mockItems[7], mockItems[8]],
    notes: "Large order",
  },
  {
    id: "doc-12",
    type: "DELIVERY",
    number: "DEL-2023-004",
    date: "2023-03-17",
    status: "SHIPPED",
    customer: mockCustomers[3],
    amount: 3000,
    items: [mockItems[6], mockItems[7], mockItems[8]],
    notes: "Multiple boxes",
  },
  {
    id: "doc-13",
    type: "INVOICE",
    number: "INV-2023-004",
    date: "2023-03-25",
    status: "OPEN",
    customer: mockCustomers[3],
    amount: 3000,
    items: [mockItems[6], mockItems[7], mockItems[8]],
    notes: "Requires approval",
  },
  {
    id: "doc-14",
    type: "ORDER",
    number: "ORD-2023-005",
    date: "2023-04-01",
    status: "OPEN",
    customer: mockCustomers[4],
    amount: 1000,
    items: [mockItems[9]],
    notes: "Check inventory",
  },
  {
    id: "doc-15",
    type: "DELIVERY",
    number: "DEL-2023-005",
    date: "2023-04-03",
    status: "DELIVERED",
    customer: mockCustomers[4],
    amount: 1000,
    items: [mockItems[9]],
    notes: "Left at loading dock",
  },
  {
    id: "doc-16",
    type: "INVOICE",
    number: "INV-2023-005",
    date: "2023-04-10",
    status: "OPEN",
    customer: mockCustomers[4],
    amount: 1000,
    items: [mockItems[9]],
    notes: "Awaiting payment",
  },
]

/**
 * Mock relationships
 */
export const mockRelationships: DocumentRelationship[] = [
  {
    id: "rel-1",
    sourceId: "doc-1",
    targetId: "doc-2",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-2")!,
  },
  {
    id: "rel-2",
    sourceId: "doc-2",
    targetId: "doc-3",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-3")!,
  },
  {
    id: "rel-3",
    sourceId: "doc-3",
    targetId: "doc-4",
    relationType: "CANCELS",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-4")!,
  },
  {
    id: "rel-4",
    sourceId: "doc-5",
    targetId: "doc-6",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-6")!,
  },
  {
    id: "rel-5",
    sourceId: "doc-6",
    targetId: "doc-7",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-7")!,
  },
  {
    id: "rel-6",
    sourceId: "doc-8",
    targetId: "doc-9",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-9")!,
  },
  {
    id: "rel-7",
    sourceId: "doc-9",
    targetId: "doc-10",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-10")!,
  },
  {
    id: "rel-8",
    sourceId: "doc-11",
    targetId: "doc-12",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-12")!,
  },
  {
    id: "rel-9",
    sourceId: "doc-12",
    targetId: "doc-13",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-13")!,
  },
  {
    id: "rel-10",
    sourceId: "doc-14",
    targetId: "doc-15",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-15")!,
  },
  {
    id: "rel-11",
    sourceId: "doc-15",
    targetId: "doc-16",
    relationType: "BASED_ON",
    relatedDocument: mockDocuments.find((doc) => doc.id === "doc-16")!,
  },
]
