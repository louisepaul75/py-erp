export type FilterType = "all" | "orders" | "deliveryNotes"

export type PickingStatus = "notStarted" | "inProgress" | "completed" | "problem"

export type PickingMethod = "manual" | "scale"

export interface BinLocation {
  id: string
  binCode: string
  location: string
}

export interface OrderItem {
  id: string
  oldArticleNumber: string
  newArticleNumber: string
  description: string
  quantityPicked: number
  quantityTotal: number
  binLocations: string[] // IDs of bins where this item is located
}

export interface Order {
  id: string
  orderNumber: string
  customerNumber: string
  customerName: string
  deliveryDate: Date
  orderDate: Date
  isOrder: boolean
  isDeliveryNote: boolean
  itemsPicked: number
  totalItems: number
  pickingStatus: PickingStatus
  pickingSequence: number
  customerAddress?: string
  contactPerson?: string
  phoneNumber?: string
  email?: string
  notes?: string
  items: OrderItem[]
  binLocations: BinLocation[]
}

