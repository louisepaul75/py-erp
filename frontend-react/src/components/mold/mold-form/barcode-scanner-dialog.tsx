"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Barcode } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props for the BarcodeScannerDialog component
 */
interface BarcodeScannerDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (barcode: string) => void;
}

/**
 * Dialog for scanning or entering a barcode
 */
export function BarcodeScannerDialog({
  open,
  onOpenChange,
  onSubmit,
}: BarcodeScannerDialogProps) {
  const [scannedBarcode, setScannedBarcode] = useState("");

  const { t } = useAppTranslation("mold");

  const handleSubmit = () => {
    if (scannedBarcode.trim() !== "") {
      onSubmit(scannedBarcode);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("scan_barcode_title")}</DialogTitle>
          <DialogDescription>{t("scan_barcode_description")}</DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4 py-4">
          <div className="flex items-center gap-2">
            <Input
              placeholder="LA000"
              value={scannedBarcode}
              onChange={(e) => setScannedBarcode(e.target.value)}
              className="flex-1"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
            />
            <Button type="button" onClick={handleSubmit}>
              Confirm
            </Button>
          </div>
          <div className="text-center">
            <Barcode className="h-12 w-12 mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              {t("barcode_instructions")}
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("cancel_button")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
