"use client"
import { X, Settings } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import PrinterSettings from "./printer-settings"
import PurposeSettings from "./purpose-settings"
import ContainerTypeSettings from "./container-type-settings"
import ScaleSettings from "./scale-settings"

interface SettingsDialogProps {
  isOpen: boolean
  onClose: () => void
}

export default function SettingsDialog({ isOpen, onClose }: SettingsDialogProps) {
  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Description asChild>
          <div className="sr-only" id="settings-dialog-description">
            Dialog zum Verwalten der Systemeinstellungen, einschließlich Drucker, Waagen, Schüttenzwecke und Schüttentypen.
          </div>
        </Dialog.Description>
        <Dialog.Content 
          className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-4xl translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white p-0 shadow-lg focus:outline-none overflow-hidden"
          aria-describedby="settings-dialog-description"
        >
          <div className="flex items-center justify-between p-4 border-b">
            <Dialog.Title className="text-xl font-semibold flex items-center gap-2 text-black">
              <Settings className="h-5 w-5" />
              Einstellungen
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4 text-black" />
              </Button>
            </Dialog.Close>
          </div>

          <div className="p-6 overflow-y-auto" style={{ maxHeight: "calc(85vh - 60px)" }}>
            <Tabs defaultValue="printers" className="w-full">
              <TabsList className="grid w-full grid-cols-4 mb-6">
                <TabsTrigger value="printers">Drucker</TabsTrigger>
                <TabsTrigger value="scales">Waagen</TabsTrigger>
                <TabsTrigger value="purposes">Schüttenzwecke</TabsTrigger>
                <TabsTrigger value="containerTypes">Schüttentypen</TabsTrigger>
              </TabsList>

              <TabsContent value="printers" className="mt-0">
                <PrinterSettings />
              </TabsContent>

              <TabsContent value="scales" className="mt-0">
                <ScaleSettings />
              </TabsContent>

              <TabsContent value="purposes" className="mt-0">
                <PurposeSettings />
              </TabsContent>

              <TabsContent value="containerTypes" className="mt-0">
                <ContainerTypeSettings />
              </TabsContent>
            </Tabs>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

