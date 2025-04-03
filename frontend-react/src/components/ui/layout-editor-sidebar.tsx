"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plus, Trash2 } from "lucide-react"

interface LayoutEditorSidebarProps {
  isVisible: boolean;
  availableWidgets: string[];
  selectedWidgetId: string | null;
  onAddWidget: (widgetType: string) => void;
  onRemoveSelectedWidget: () => void;
}

export function LayoutEditorSidebar({
  isVisible,
  availableWidgets,
  selectedWidgetId,
  onAddWidget,
  onRemoveSelectedWidget,
}: LayoutEditorSidebarProps) {
  const [selectedWidgetType, setSelectedWidgetType] = useState<string | undefined>(undefined);

  const handleAddClick = () => {
    if (selectedWidgetType) {
      onAddWidget(selectedWidgetType);
      // Optionally reset dropdown after adding
      // setSelectedWidgetType(undefined); 
    }
  };

  if (!isVisible) {
    return null; // Don't render anything if not visible
  }

  return (
    <Card className="fixed top-0 right-0 h-screen z-10 w-[250px] border-l flex flex-col bg-background">
      <CardHeader className="pt-4 pb-2">
        <CardTitle className="text-lg">Layout Editor</CardTitle>
      </CardHeader>
      <Separator />
      <CardContent className="pt-4 flex-1 flex flex-col gap-4 overflow-y-auto">
        {/* Add Widget Section */}
        <div>
          <h4 className="mb-2 text-sm font-medium">Add Widget</h4>
          <div className="flex flex-col gap-2">
            <Select value={selectedWidgetType} onValueChange={setSelectedWidgetType}>
              <SelectTrigger>
                <SelectValue placeholder="Select widget type..." />
              </SelectTrigger>
              <SelectContent>
                {availableWidgets.map((widgetName) => (
                  <SelectItem key={widgetName} value={widgetName}>
                    {widgetName} {/* You might want a more user-friendly display name */}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button 
              onClick={handleAddClick} 
              disabled={!selectedWidgetType}
            >
              <Plus className="mr-2 h-4 w-4" /> Add Widget
            </Button>
          </div>
        </div>

        <Separator />

        {/* Modify Widget Section */}
        <div>
          <h4 className="mb-2 text-sm font-medium">Modify Widget</h4>
          <Button
            variant="destructive"
            onClick={onRemoveSelectedWidget}
            disabled={!selectedWidgetId}
            className="w-full"
          >
            <Trash2 className="mr-2 h-4 w-4" /> Remove Selected
          </Button>
          {/* TODO: Add widget configuration options here later */}
          {selectedWidgetId && (
            <p className="mt-2 text-xs text-muted-foreground">Selected: {selectedWidgetId}</p> // Temporary display
          )}
        </div>

      </CardContent>
    </Card>
  ); 
} 