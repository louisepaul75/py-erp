"use client"

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import MoldForm from "./mold-form"
import type { Mold } from "@/types/casting/mold"

interface AddMoldModalProps {
  isOpen: boolean
  onClose: () => void
  onAddMold: (mold: Mold) => void
}

export default function AddMoldModal({
  isOpen,
  onClose,
  onAddMold,
}: AddMoldModalProps) {
  const handleAddMold = (mold: Mold) => {
    onAddMold(mold)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Form hinzufügen</DialogTitle>
        </DialogHeader>
        <MoldForm onSubmit={handleAddMold} onCancel={onClose} />
      </DialogContent>
    </Dialog>
  )
} 