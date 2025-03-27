import type { Order, OrderItem, BinLocation } from "@/types/types"

// Helper function to generate bin locations
function generateBinLocations(count: number, baseId: string): BinLocation[] {
  const bins: BinLocation[] = []

  for (let i = 1; i <= count; i++) {
    const shelf = Math.floor(10 + Math.random() * 20)
    const compartment = Math.floor(1 + Math.random() * 5)
    const floor = Math.floor(1 + Math.random() * 5)

    bins.push({
      id: `${baseId}-bin-${i}`,
      binCode: `SC${Math.floor(10000 + Math.random() * 90000)}.X${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`,
      location: `${shelf}/${compartment}/${floor}`,
    })
  }

  return bins
}

// Helper function to generate a large number of mock items with bin assignments
function generateMockItems(count: number, baseId: string, bins: BinLocation[]): OrderItem[] {
  const items: OrderItem[] = []

  for (let i = 1; i <= count; i++) {
    const oldNumber = `ALT-${Math.floor(1000 + Math.random() * 9000)}`
    const newNumber = `NEU-${Math.floor(2000 + Math.random() * 9000)}`
    const quantityTotal = Math.floor(1 + Math.random() * 10)
    const quantityPicked = Math.floor(Math.random() * (quantityTotal + 1))

    // Assign 1-3 random bins to this item
    const binCount = Math.floor(1 + Math.random() * 3)
    const itemBins: string[] = []

    if (bins.length > 0) {
      const availableBins = [...bins]
      for (let j = 0; j < binCount && availableBins.length > 0; j++) {
        const randomIndex = Math.floor(Math.random() * availableBins.length)
        itemBins.push(availableBins[randomIndex].id)
        // Remove the bin to avoid duplicates (uncomment if you want unique bins per item)
        // availableBins.splice(randomIndex, 1)
      }
    }

    items.push({
      id: `${baseId}-item-${i}`,
      oldArticleNumber: oldNumber,
      newArticleNumber: newNumber,
      description: `Artikel ${i} (${oldNumber})`,
      quantityPicked,
      quantityTotal,
      binLocations: itemBins,
    })
  }

  return items
}

// Mock data function - replace with actual API call
export async function fetchOrders(): Promise<Order[]> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1000))

  // Generate a large number of orders
  const orders: Order[] = []

  // First add our detailed sample orders
  const order1Bins = [{ id: "1-bin-1", binCode: "SC12345.XA", location: "11/2/3" }]

  const order3Bins = [
    { id: "3-bin-1", binCode: "SC23456.XB", location: "12/1/2" },
    { id: "3-bin-2", binCode: "SC34567.XC", location: "12/1/3" },
  ]

  const sampleOrders = [
    {
      id: "1",
      orderNumber: "A-10001",
      customerNumber: "K-5001",
      customerName: "Müller GmbH",
      deliveryDate: new Date(2023, 11, 15),
      orderDate: new Date(2023, 11, 10),
      isOrder: true,
      isDeliveryNote: false,
      itemsPicked: 5,
      totalItems: 10,
      pickingStatus: "inProgress",
      pickingSequence: 1,
      customerAddress: "Industriestraße 45, 70565 Stuttgart",
      contactPerson: "Thomas Müller",
      phoneNumber: "+49 711 123456",
      email: "info@mueller-gmbh.de",
      notes: "Lieferung bitte bis 14 Uhr",
      binLocations: order1Bins,
      items: generateMockItems(300, "1", order1Bins), // Generate 300 items for this order
    },
    {
      id: "2",
      orderNumber: "A-10002",
      customerNumber: "K-3045",
      customerName: "Schmidt & Co KG",
      deliveryDate: new Date(2023, 11, 16),
      orderDate: new Date(2023, 11, 9),
      isOrder: true,
      isDeliveryNote: true,
      itemsPicked: 0,
      totalItems: 5,
      pickingStatus: "notStarted",
      pickingSequence: 2,
      customerAddress: "Hauptstraße 28, 80331 München",
      contactPerson: "Julia Schmidt",
      phoneNumber: "+49 89 987654",
      email: "j.schmidt@schmidt-co.de",
      binLocations: [],
      items: generateMockItems(5, "2", []),
    },
    {
      id: "3",
      orderNumber: "L-2001",
      customerNumber: "K-1022",
      customerName: "Bauer Logistik",
      deliveryDate: new Date(2023, 11, 14),
      orderDate: new Date(2023, 11, 8),
      isOrder: false,
      isDeliveryNote: true,
      itemsPicked: 8,
      totalItems: 8,
      pickingStatus: "completed",
      pickingSequence: 3,
      customerAddress: "Logistikweg 12, 60306 Frankfurt",
      contactPerson: "Michael Bauer",
      phoneNumber: "+49 69 555666",
      email: "m.bauer@bauer-logistik.de",
      binLocations: order3Bins,
      items: generateMockItems(8, "3", order3Bins),
    },
    {
      id: "4",
      orderNumber: "A-10003",
      customerNumber: "K-7890",
      customerName: "Weber Industrie",
      deliveryDate: new Date(2023, 11, 17),
      orderDate: new Date(2023, 11, 11),
      isOrder: true,
      isDeliveryNote: false,
      itemsPicked: 2,
      totalItems: 15,
      pickingStatus: "problem",
      pickingSequence: 4,
      customerAddress: "Industriepark 78, 40474 Düsseldorf",
      contactPerson: "Stefan Weber",
      phoneNumber: "+49 211 778899",
      email: "s.weber@weber-industrie.de",
      notes: "Artikel 5001 nicht auf Lager",
      binLocations: [{ id: "4-bin-1", binCode: "SC45678.XD", location: "13/3/1" }],
      items: generateMockItems(15, "4", [{ id: "4-bin-1", binCode: "SC45678.XD", location: "13/3/1" }]),
    },
    {
      id: "5",
      orderNumber: "L-2002",
      customerNumber: "K-4567",
      customerName: "Fischer AG",
      deliveryDate: new Date(2023, 11, 18),
      orderDate: new Date(2023, 11, 12),
      isOrder: false,
      isDeliveryNote: true,
      itemsPicked: 0,
      totalItems: 3,
      pickingStatus: "notStarted",
      pickingSequence: 5,
      customerAddress: "Fischerstraße 10, 50667 Köln",
      contactPerson: "Anna Fischer",
      phoneNumber: "+49 221 112233",
      email: "a.fischer@fischer-ag.de",
      binLocations: [],
      items: generateMockItems(3, "5", []),
    },
    {
      id: "6",
      orderNumber: "A-10004",
      customerNumber: "K-9876",
      customerName: "Hoffmann Elektronik",
      deliveryDate: new Date(2023, 11, 20),
      orderDate: new Date(2023, 11, 13),
      isOrder: true,
      isDeliveryNote: true,
      itemsPicked: 6,
      totalItems: 12,
      pickingStatus: "inProgress",
      pickingSequence: 6,
      customerAddress: "Elektronikweg 5, 01067 Dresden",
      contactPerson: "Peter Hoffmann",
      phoneNumber: "+49 351 445566",
      email: "p.hoffmann@hoffmann-elektronik.de",
      binLocations: [
        { id: "6-bin-1", binCode: "SC56789.XE", location: "14/2/2" },
        { id: "6-bin-2", binCode: "SC67890.XF", location: "14/2/3" },
      ],
      items: generateMockItems(12, "6", [
        { id: "6-bin-1", binCode: "SC56789.XE", location: "14/2/2" },
        { id: "6-bin-2", binCode: "SC67890.XF", location: "14/2/3" },
      ]),
    },
    {
      id: "7",
      orderNumber: "A-10005",
      customerNumber: "K-2345",
      customerName: "Schulz Metallbau",
      deliveryDate: new Date(2023, 11, 21),
      orderDate: new Date(2023, 11, 14),
      isOrder: true,
      isDeliveryNote: false,
      itemsPicked: 9,
      totalItems: 9,
      pickingStatus: "completed",
      pickingSequence: 7,
      customerAddress: "Metallstraße 22, 30159 Hannover",
      contactPerson: "Klaus Schulz",
      phoneNumber: "+49 511 334455",
      email: "k.schulz@schulz-metallbau.de",
      binLocations: [
        { id: "7-bin-1", binCode: "SC78901.XG", location: "15/1/1" },
        { id: "7-bin-2", binCode: "SC89012.XH", location: "15/1/2" },
      ],
      items: generateMockItems(9, "7", [
        { id: "7-bin-1", binCode: "SC78901.XG", location: "15/1/1" },
        { id: "7-bin-2", binCode: "SC89012.XH", location: "15/1/2" },
      ]),
    },
    {
      id: "8",
      orderNumber: "L-2003",
      customerNumber: "K-6543",
      customerName: "Koch Versand",
      deliveryDate: new Date(2023, 11, 19),
      orderDate: new Date(2023, 11, 10),
      isOrder: false,
      isDeliveryNote: true,
      itemsPicked: 1,
      totalItems: 7,
      pickingStatus: "problem",
      pickingSequence: 8,
      customerAddress: "Versandweg 33, 20095 Hamburg",
      contactPerson: "Maria Koch",
      phoneNumber: "+49 40 667788",
      email: "m.koch@koch-versand.de",
      notes: "Lieferung verzögert wegen Artikelmangel",
      binLocations: [{ id: "8-bin-1", binCode: "SC90123.XI", location: "16/3/2" }],
      items: generateMockItems(7, "8", [{ id: "8-bin-1", binCode: "SC90123.XI", location: "16/3/2" }]),
    },
  ]

  orders.push(...sampleOrders)

  // Then generate additional orders to reach a large number
  for (let i = sampleOrders.length + 1; i <= 500; i++) {
    const itemCount = Math.floor(1 + Math.random() * 20)
    const itemsPicked = Math.floor(Math.random() * (itemCount + 1))
    const binCount = Math.floor(Math.random() * 3) + 1

    const bins = generateBinLocations(binCount, i.toString())

    const order: Order = {
      id: i.toString(),
      orderNumber: `A-${10000 + i}`,
      customerNumber: `K-${1000 + Math.floor(Math.random() * 9000)}`,
      customerName: `Kunde ${i}`,
      deliveryDate: new Date(2023, 11, Math.floor(1 + Math.random() * 30)),
      orderDate: new Date(2023, 11, Math.floor(1 + Math.random() * 30)),
      isOrder: Math.random() > 0.3,
      isDeliveryNote: Math.random() > 0.5,
      itemsPicked,
      totalItems: itemCount,
      pickingStatus: ["notStarted", "inProgress", "completed", "problem"][Math.floor(Math.random() * 4)] as any,
      pickingSequence: i,
      customerAddress: `Adresse ${i}`,
      contactPerson: `Kontakt ${i}`,
      phoneNumber: `+49 ${Math.floor(100 + Math.random() * 900)} ${Math.floor(100000 + Math.random() * 900000)}`,
      email: `kontakt${i}@example.com`,
      binLocations: bins,
      items: generateMockItems(Math.floor(3 + Math.random() * 10), i.toString(), bins),
    }

    orders.push(order)
  }

  return orders
}

