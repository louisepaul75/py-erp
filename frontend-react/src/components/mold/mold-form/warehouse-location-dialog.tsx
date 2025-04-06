"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import type { WarehouseLocation } from "@/types/mold/warehouse-location";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props for the WarehouseLocationDialog component
 */
interface WarehouseLocationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  locations: WarehouseLocation[];
  onSelect: (location: string) => void;
}

/**
 * Dialog for selecting a warehouse location
 */
export function WarehouseLocationDialog({
  open,
  onOpenChange,
  locations,
  onSelect,
}: WarehouseLocationDialogProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const { t } = useAppTranslation("mold");

  // Filter locations based on search term
  const filteredLocations =
    locations?.filter(
      (loc) =>
        loc.laNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
        loc.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (loc.description &&
          loc.description.toLowerCase().includes(searchTerm.toLowerCase()))
    ) || [];

  // {t("")}
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("warehouse_dialog_title")}</DialogTitle>
          <DialogDescription>
            {t("warehouse_dialog_description")}
          </DialogDescription>
        </DialogHeader>

        <div className="flex items-center border rounded-md px-3 py-2 mb-4">
          <Search className="h-4 w-4 mr-2 text-muted-foreground" />
          <Input
            placeholder={t("search_locations_placeholder")}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="border-0 p-0 shadow-none focus-visible:ring-0"
          />
        </div>

        <ScrollArea className="h-72">
          <div className="space-y-2">
            {filteredLocations.length === 0 ? (
              <p className="text-center text-muted-foreground py-4">
                {t("no_locations_found")}
              </p>
            ) : (
              filteredLocations.map((location) => (
                <Button
                  key={location.id}
                  variant="outline"
                  className="w-full justify-start text-left h-auto py-3"
                  onClick={() =>
                    onSelect(`${location.laNumber} - ${location.location}`)
                  }
                >
                  <div>
                    <div className="font-medium">
                      {location.laNumber} - {t("location")} {location.location}
                    </div>
                    {location.description && (
                      <div className="text-sm text-muted-foreground">
                        {location.description}
                      </div>
                    )}
                  </div>
                </Button>
              ))
            )}
          </div>
        </ScrollArea>

        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("cancel_button")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
