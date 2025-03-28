import { faker } from '@faker-js/faker'
import { de } from '@faker-js/faker/locales'
import type {
  ContainerItem,
  ContainerSlot,
  ContainerUnit,
  SlotCode,
  ContainerLocation,
  ContainerArticle,
  WarehouseLocation
} from "@/types/warehouse-types"

faker.locale = 'de'

interface ActivityLogEntry {
  id: string
  timestamp: Date
  user: string
  action: string
  entityId: string
  entityType: string
  beforeState: string
  afterState: string
}

const possibleActions = [
  'Artikel eingelagert',
  'Artikel entnommen',
  'Bestand korrigiert',
  'Status geändert',
  'Standort geändert',
  'Inventur durchgeführt'
]

const mockUsers = [
  'Max Mustermann',
  'Anna Schmidt',
  'Thomas Weber',
  'Lisa Meyer',
  'Michael Wagner'
]

function generateMockSlotCode(): SlotCode {
  return {
    code: faker.string.alphanumeric(4).toUpperCase(),
    color: faker.helpers.arrayElement(['red', 'green', 'blue', 'yellow'])
  }
}

function generateMockContainerSlots(count: number = 4): ContainerSlot[] {
  return Array.from({ length: count }, () => ({
    id: faker.string.uuid(),
    code: generateMockSlotCode(),
    unitId: faker.string.uuid()
  }))
}

function generateMockContainerUnits(count: number = 2): ContainerUnit[] {
  return Array.from({ length: count }, () => ({
    id: faker.string.uuid(),
    unitNumber: faker.number.int({ min: 1, max: 100 }),
    slots: Array.from({ length: faker.number.int({ min: 1, max: 4 }) }, () => faker.string.uuid()),
    articleNumber: faker.string.alphanumeric(8).toUpperCase(),
    oldArticleNumber: faker.string.alphanumeric(8).toUpperCase(),
    description: faker.commerce.productDescription(),
    stock: faker.number.int({ min: 0, max: 100 })
  }))
}

export function generateMockActivityLogs(
  entityId?: string,
  entityType: 'location' | 'container' = 'location',
  count: number = 10
): ActivityLogEntry[] {
  return Array.from({ length: count }, () => ({
    id: faker.string.uuid(),
    timestamp: faker.date.recent({ days: 30 }),
    user: faker.helpers.arrayElement(mockUsers),
    action: faker.helpers.arrayElement(possibleActions),
    entityId: entityId || faker.string.uuid(),
    entityType,
    beforeState: faker.helpers.arrayElement([
      'Verfügbar',
      'In Bearbeitung',
      'Gesperrt',
      'Inventur ausstehend'
    ]),
    afterState: faker.helpers.arrayElement([
      'Verfügbar',
      'In Bearbeitung',
      'Gesperrt',
      'Inventur abgeschlossen'
    ])
  }))
}

export function generateMockContainers(count: number = 5, includeLocation: boolean = false): ContainerItem[] {
  return Array.from({ length: count }, () => {
    const container: ContainerItem = {
      id: faker.string.uuid(),
      containerCode: faker.string.alphanumeric(6).toUpperCase(),
      type: faker.helpers.arrayElement(['Karton', 'Palette', 'Gitterbox', 'Behälter']),
      description: faker.commerce.productDescription(),
      status: faker.helpers.arrayElement(['Neu', 'In Benutzung', 'Beschädigt']),
      purpose: faker.helpers.arrayElement(['Lagerung', 'Transport', 'Ausstellung']),
      stock: faker.number.int({ min: 0, max: 1000 }),
      articleNumber: faker.string.alphanumeric(8).toUpperCase(),
      oldArticleNumber: faker.string.alphanumeric(8).toUpperCase(),
      slots: generateMockContainerSlots().map(slot => ({
        id: slot.id,
        code: {
          code: slot.code.code,
          color: slot.code.color
        }
      })),
      units: generateMockContainerUnits()
    }

    if (includeLocation && Math.random() > 0.5) {
      const locationObj: ContainerLocation = {
        laNumber: `LA${1000 + faker.number.int({ min: 0, max: 999 })}`,
        shelf: faker.number.int({ min: 1, max: 20 }),
        compartment: faker.number.int({ min: 1, max: 10 }),
        floor: faker.number.int({ min: 1, max: 5 })
      }

      const articles: ContainerArticle[] = Array.from(
        { length: faker.number.int({ min: 1, max: 5 }) },
        () => ({
          id: faker.string.uuid(),
          articleNumber: faker.number.int({ min: 100000, max: 999999 }),
          oldArticleNumber: `${13200 + faker.number.int({ min: 0, max: 9 })}-BE`,
          description: faker.helpers.arrayElement([
            'Dampfer Herrschung',
            'neuer Raddampfer Diessen',
            'Teufel',
            'Mond mit Mütze',
            'Kuckucksuhr'
          ]),
          stock: faker.number.int({ min: 1, max: 100 })
        })
      )

      return {
        ...container,
        location: `${locationObj.laNumber} - Regal ${locationObj.shelf}/${locationObj.compartment}/${locationObj.floor}`,
        shelf: locationObj.shelf,
        compartment: locationObj.compartment,
        floor: locationObj.floor,
        articles
      }
    }

    return container
  })
}

export function generateLANumber(existingLocations?: { laNumber: string }[]): string {
  // Format: LA-YYYYMMDD-XXXX where XXXX is a random number
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  // Keep generating numbers until we find a unique one
  let random: string
  let laNumber: string
  do {
    random = faker.string.numeric(4)
    laNumber = `LA-${year}${month}${day}-${random}`
  } while (existingLocations?.some(loc => loc.laNumber === laNumber))

  return laNumber
}

export function generateMockData(count: number = 10): WarehouseLocation[] {
  return Array.from({ length: count }, () => ({
    id: faker.string.uuid(),
    laNumber: generateLANumber(),
    location: faker.helpers.arrayElement(['Hauptlager 1', 'Hauptlager 2', 'Externes Lager', 'Nebenlager']),
    forSale: faker.datatype.boolean(),
    specialStorage: faker.datatype.boolean(),
    shelf: faker.number.int({ min: 1, max: 20 }),
    compartment: faker.number.int({ min: 1, max: 10 }),
    floor: faker.number.int({ min: 1, max: 5 }),
    containerCount: faker.number.int({ min: 0, max: 10 }),
    status: faker.helpers.arrayElement(['free', 'in-use'])
  }))
} 