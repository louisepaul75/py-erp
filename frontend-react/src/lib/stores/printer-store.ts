import { create } from 'zustand'

export interface Printer {
  id: string
  name: string
  ipAddress: string
}

interface PrinterStore {
  printers: Printer[]
  addPrinter: (printer: Printer) => void
  updatePrinter: (id: string, updatedPrinter: Printer) => void
  deletePrinter: (id: string) => void
}

export const usePrinterStore = create<PrinterStore>((set) => ({
  printers: [],
  
  addPrinter: (printer) =>
    set((state) => ({
      printers: [...state.printers, printer],
    })),

  updatePrinter: (id, updatedPrinter) =>
    set((state) => ({
      printers: state.printers.map((p) =>
        p.id === id ? updatedPrinter : p
      ),
    })),

  deletePrinter: (id) =>
    set((state) => ({
      printers: state.printers.filter((p) => p.id !== id),
    })),
})) 