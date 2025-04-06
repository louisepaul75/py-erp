"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import AlloyManager from "@/components/mold/alloy-manager";
import TagManager from "@/components/mold/tag-manager";
import { Beaker, Tag } from "lucide-react"
import { useQueryClient } from "@tanstack/react-query"
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props for the SettingsDialog component
 */
interface SettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * SettingsDialog component provides a dialog for managing alloys and tags
 */
export default function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
  // State to track the active tab
  const [activeTab, setActiveTab] = useState("alloys")
  const queryClient = useQueryClient()

    const { t } = useAppTranslation("mold");

  // Wenn der Dialog geschlossen wird, aktualisieren wir die Molds-Daten
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      // Explizit den Cache für Molds invalidieren, wenn der Dialog geschlossen wird
      queryClient.invalidateQueries({ queryKey: ["molds"] })
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t("settings_dialog_title")}</DialogTitle>
          <DialogDescription>{t("settings_dialog_description")}</DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="alloys" value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="alloys" className="flex items-center gap-2">
              <Beaker className="h-4 w-4" />
              <span>{t("settings_tab_alloys")}</span>
            </TabsTrigger>
            <TabsTrigger value="tags" className="flex items-center gap-2">
              <Tag className="h-4 w-4" />
              <span>{t("settings_tab_tags")}</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="alloys" className="mt-6">
            <AlloyManager />
          </TabsContent>

          <TabsContent value="tags" className="mt-6">
            <TagManager />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}

