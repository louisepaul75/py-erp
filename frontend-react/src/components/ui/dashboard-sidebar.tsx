"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Edit, Save, Trash2, Plus, X } from "lucide-react"
import { 
  Sheet, 
  SheetContent, 
  SheetHeader, 
  SheetTitle, 
  SheetDescription 
} from "@/components/ui/sheet"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"

export interface SavedLayout {
  id: string
  name: string
  layouts: any // Using any here, but in a real app, you'd want to define the proper type
  isActive: boolean
}

interface DashboardSidebarProps {
  isOpen: boolean
  onClose: () => void
  isEditMode: boolean
  toggleEditMode: () => void
  saveLayout: () => void
  savedLayouts: SavedLayout[]
  activeLayoutId: string | null
  onLayoutSelect: (layoutId: string) => void
  onSaveNewLayout: (name: string) => void
  onUpdateLayout: (layout: SavedLayout) => void
  onDeleteLayout: (layoutId: string) => void
}

export function DashboardSidebar({
  isOpen,
  onClose,
  isEditMode,
  toggleEditMode,
  saveLayout,
  savedLayouts,
  activeLayoutId,
  onLayoutSelect,
  onSaveNewLayout,
  onUpdateLayout,
  onDeleteLayout
}: DashboardSidebarProps) {
  const [newLayoutName, setNewLayoutName] = useState("")
  const [isAddingNew, setIsAddingNew] = useState(false)

  const handleSaveNewLayout = () => {
    if (newLayoutName.trim()) {
      onSaveNewLayout(newLayoutName.trim())
      setNewLayoutName("")
      setIsAddingNew(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSaveNewLayout()
    } else if (e.key === "Escape") {
      setIsAddingNew(false)
      setNewLayoutName("")
    }
  }

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-[300px] sm:w-[400px]">
        <SheetHeader>
          <SheetTitle>Dashboard Layouts</SheetTitle>
          <SheetDescription>
            Manage your saved dashboard layouts
          </SheetDescription>
        </SheetHeader>
        
        <div className="py-4">
          {isEditMode ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Currently in edit mode. Rearrange widgets and then save your changes.
              </p>
              <div className="flex gap-2">
                <Button variant="outline" onClick={toggleEditMode} className="flex-1">
                  <X className="mr-2 h-4 w-4" />
                  Cancel
                </Button>
                <Button onClick={saveLayout} className="flex-1">
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </Button>
              </div>
            </div>
          ) : (
            <Button 
              variant="outline" 
              onClick={toggleEditMode} 
              className="w-full border-primary text-primary hover:bg-primary/10"
            >
              <Edit className="mr-2 h-4 w-4" />
              Edit Layout
            </Button>
          )}
        </div>
        
        <div className="py-2">
          <h3 className="mb-2 text-sm font-medium">Saved Layouts</h3>
          <ScrollArea className="h-[300px] rounded-md border p-2">
            <div className="space-y-2">
              {savedLayouts.map((layout) => (
                <div
                  key={layout.id}
                  className={cn(
                    "flex items-center justify-between p-2 rounded-md cursor-pointer hover:bg-accent",
                    layout.id === activeLayoutId && "bg-accent"
                  )}
                  onClick={() => onLayoutSelect(layout.id)}
                >
                  <span className="text-sm font-medium">{layout.name}</span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteLayout(layout.id)
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              
              {isAddingNew ? (
                <div className="flex items-center gap-2 p-2">
                  <Input
                    value={newLayoutName}
                    onChange={(e) => setNewLayoutName(e.target.value)}
                    placeholder="Layout name"
                    className="h-8 text-sm"
                    autoFocus
                    onKeyDown={handleKeyDown}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={handleSaveNewLayout}
                  >
                    <Save className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => {
                      setIsAddingNew(false)
                      setNewLayoutName("")
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <Button
                  variant="ghost"
                  className="w-full justify-start text-sm text-primary"
                  onClick={() => setIsAddingNew(true)}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Save Current Layout
                </Button>
              )}
            </div>
          </ScrollArea>
        </div>
      </SheetContent>
    </Sheet>
  )
} 