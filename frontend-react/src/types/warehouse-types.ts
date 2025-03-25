export type WarehouseLocation = {
  id: string
  laNumber: string
  location: string
  forSale: boolean
  specialStorage: boolean
  shelf: number
  compartment: number
  floor: number
  containerCount: number
  status: "free" | "in-use"
}

export type SlotCode = {
  code: string
  color: string
}

export type ContainerSlot = {
  id: string
  code: SlotCode
  unitId: string
}

export type ContainerUnit = {
  id: string
  unitNumber: number
  slots: string[] // Array of slot IDs
  articleNumber?: string
  oldArticleNumber?: string
  description?: string
  stock?: number
}

export type ContainerItem = {
  id: string
  containerCode: string
  type: string
  articleNumber: string
  oldArticleNumber: string
  description: string
  stock: number
  slots: ContainerSlot[]
  units: ContainerUnit[]
}

export type ContainerTypeDefinition = {
  id: string
  name: string
  standardSlots: number
}

