"use client"

import { Button } from "@/components/ui/button"
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

// Widget type display mapping
const widgetTypeNames: Record<string, string> = {
  "menu-tiles": "Menü Kacheln",
  "quick-links": "Schnellzugriff",
  "news-pinboard": "Pinnwand",
  "sales-analysis": "Verkaufsanalyse"
};

export function LayoutEditorSidebar({
  isVisible,
  availableWidgets,
  selectedWidgetId,
  onAddWidget,
  onRemoveSelectedWidget,
}: LayoutEditorSidebarProps) {
  if (!isVisible) {
    return null; // Don't render anything if not visible
  }

  return (
    <Card className="fixed top-0 right-0 h-screen z-10 w-[250px] border-l flex flex-col bg-background">
      <CardHeader className="pt-4 pb-2">
        <CardTitle className="text-lg">Layout Editor</CardTitle>
      </CardHeader>
      <Separator />
      <CardContent className="flex-1 overflow-y-auto pt-6">
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">
              Verfügbare Widgets
            </label>
            <div className="grid gap-2">
              {availableWidgets.map((type) => (
                <Button
                  key={type}
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => onAddWidget(type)}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  {widgetTypeNames[type] || type}
                </Button>
              ))}
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <h3 className="text-sm font-medium">Ausgewähltes Widget</h3>
            {selectedWidgetId ? (
              <div className="space-y-2">
                <div className="px-2 py-1 bg-muted rounded text-sm">
                  {selectedWidgetId}
                </div>
                <Button
                  variant="destructive"
                  className="w-full"
                  onClick={onRemoveSelectedWidget}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Widget entfernen
                </Button>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Klicke auf ein Widget im Layout, um es auszuwählen
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  ); 
} 