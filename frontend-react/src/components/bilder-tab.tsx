import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plus, Minus, ImageIcon, Upload, X, Edit } from "lucide-react"

export default function BilderTab() {
  return (
    <div className="p-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="h-9 rounded-full">
              <Plus className="h-4 w-4 mr-1" />
              <span className="text-xs">Hinzufügen</span>
            </Button>
            <Button variant="outline" size="sm" className="h-9 rounded-full">
              <Minus className="h-4 w-4 mr-1" />
              <span className="text-xs">Entfernen</span>
            </Button>
          </div>
          <Button variant="outline" size="sm" className="h-9 rounded-full">
            <Upload className="h-4 w-4 mr-1" />
            <span className="text-xs">Hochladen</span>
          </Button>
        </div>

        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
            <CardTitle className="text-sm font-medium">Bilder</CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="group relative">
                  <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-2 flex flex-col items-center hover:border-blue-400 dark:hover:border-blue-500 transition-colors cursor-pointer">
                    <div className="bg-slate-100 dark:bg-slate-800 w-full aspect-square flex items-center justify-center mb-2 rounded-md overflow-hidden">
                      <ImageIcon className="h-10 w-10 text-slate-400" />
                    </div>
                    <span className="text-xs text-slate-500 dark:text-slate-400">Bild {i + 1}</span>
                  </div>
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <Button
                      variant="secondary"
                      size="icon"
                      className="h-6 w-6 rounded-full bg-white dark:bg-slate-700 shadow-sm"
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="secondary"
                      size="icon"
                      className="h-6 w-6 rounded-full bg-white dark:bg-slate-700 shadow-sm"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
              <div className="border border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-2 flex flex-col items-center justify-center h-full aspect-square cursor-pointer hover:border-blue-400 dark:hover:border-blue-500 transition-colors">
                <Plus className="h-8 w-8 text-slate-400 mb-2" />
                <span className="text-xs text-slate-500 dark:text-slate-400">Bild hinzufügen</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

