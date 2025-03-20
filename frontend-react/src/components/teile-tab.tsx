import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plus, Minus, ChevronLeft, ChevronRight, ArrowUpDown, Filter } from "lucide-react"

export default function TeileTab() {
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
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" className="h-9 rounded-full">
              <Filter className="h-4 w-4 mr-1" />
              <span className="text-xs">Filter</span>
            </Button>
            <Button variant="ghost" size="sm" className="h-9 rounded-full">
              <ArrowUpDown className="h-4 w-4 mr-1" />
              <span className="text-xs">Sortieren</span>
            </Button>
          </div>
        </div>

        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
            <CardTitle className="text-sm font-medium">Besteht aus</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium bg-slate-50 dark:bg-slate-800/50 w-1/2">
                      Besteht aus
                    </th>
                    <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium bg-slate-50 dark:bg-slate-800/50">
                      Anz
                    </th>
                    <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium"></th>
                    <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium"></th>
                  </tr>
                </thead>
                <tbody>
                  {[...Array(5)].map((_, i) => (
                    <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                      <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                      <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                      <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex justify-between bg-slate-50 dark:bg-slate-800/50 p-2 border-t border-slate-200 dark:border-slate-700">
              <Button variant="ghost" size="sm" className="h-8 w-8 rounded-full p-0">
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="flex items-center">
                <span className="text-xs text-slate-500 dark:text-slate-400">Seite 1 von 1</span>
              </div>
              <Button variant="ghost" size="sm" className="h-8 w-8 rounded-full p-0">
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
            <CardTitle className="text-sm font-medium">Ist Teil von</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium w-1/2">
                      Ist Teil von Variante
                    </th>
                    <th className="border-b border-slate-200 dark:border-slate-700 p-3 text-left font-medium">
                      Ist Teil von Artikel
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {[...Array(7)].map((_, i) => (
                    <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                      <td className="border-b border-slate-200 dark:border-slate-700 p-3"></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

