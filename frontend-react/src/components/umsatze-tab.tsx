import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowDown, TrendingUp, Package, Euro, Calendar, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function UmsatzeTab() {
  // Beispieldaten für die Visualisierung
  const yearlyData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] // Monatliche Daten für das aktuelle Jahr
  const previousYearData = [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0] // Monatliche Daten für das Vorjahr

  // Funktion zum Rendern der Mini-Sparkline
  const renderSparkline = (data: number[], color: string) => {
    const max = Math.max(...data, 1)
    const width = 100 / data.length

    return (
      <div className="flex items-end h-8 w-full gap-[1px]">
        {data.map((value, index) => (
          <div
            key={index}
            className={`${color} rounded-sm`}
            style={{
              height: `${(value / max) * 100}%`,
              width: `${width}%`,
              minHeight: "1px",
            }}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Übersichtskarten */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-slate-500 dark:text-slate-400">Umsatz (Jahr)</CardTitle>
            <Euro className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold">0,00 €</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center mt-1">
              <ArrowDown className="h-3 w-3 text-red-500 mr-1" />
              <span className="text-red-500">100%</span>
              <span className="ml-1">zum Vorjahr</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-slate-500 dark:text-slate-400">Umsatz (5 Jahre)</CardTitle>
            <TrendingUp className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold">455,00 €</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {renderSparkline([0, 76.2, 120, 150, 108.8], "bg-blue-400 dark:bg-blue-500")}
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-slate-500 dark:text-slate-400">Stückzahl (Jahr)</CardTitle>
            <Package className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold">0</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center mt-1">
              <ArrowDown className="h-3 w-3 text-red-500 mr-1" />
              <span className="text-red-500">100%</span>
              <span className="ml-1">zum Vorjahr</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium text-slate-500 dark:text-slate-400">Stückzahl (Gesamt)</CardTitle>
            <Calendar className="h-4 w-4 text-slate-500 dark:text-slate-400" />
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold">16</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              {renderSparkline([0, 3, 4, 5, 4], "bg-green-400 dark:bg-green-500")}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Hauptdaten */}
      <div className="flex flex-col lg:flex-row gap-6">
        <Card className="flex-1 border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium">Umsatzübersicht</CardTitle>
            <Button variant="ghost" size="sm" className="h-8 rounded-full">
              <BarChart3 className="h-4 w-4 mr-1" />
              <span className="text-xs">Diagramm</span>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableHead className="font-medium"></TableHead>
                    <TableHead className="font-medium text-right">Jahr</TableHead>
                    <TableHead className="font-medium text-right">Vorjahr</TableHead>
                    <TableHead className="font-medium text-right">5 Jahre</TableHead>
                    <TableHead className="font-medium text-right">Gesamt</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell className="font-medium">Stück</TableCell>
                    <TableCell className="text-right">0</TableCell>
                    <TableCell className="text-right">3</TableCell>
                    <TableCell className="text-right">13</TableCell>
                    <TableCell className="text-right font-medium">16</TableCell>
                  </TableRow>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell className="font-medium">EUR</TableCell>
                    <TableCell className="text-right">0,00 €</TableCell>
                    <TableCell className="text-right">76,20 €</TableCell>
                    <TableCell className="text-right">455,00 €</TableCell>
                    <TableCell className="text-right font-medium">561,30 €</TableCell>
                  </TableRow>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell className="font-medium">Ø Preis</TableCell>
                    <TableCell className="text-right">0,00 €</TableCell>
                    <TableCell className="text-right">25,40 €</TableCell>
                    <TableCell className="text-right">35,00 €</TableCell>
                    <TableCell className="text-right font-medium">35,08 €</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <Card className="w-full lg:w-80 border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
            <CardTitle className="text-sm font-medium">Lagerbestand</CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm">Bestand</span>
              <span className="text-sm font-medium bg-blue-50 dark:bg-blue-900/20 px-3 py-1 rounded-full">6</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Min. Bestand</span>
              <span className="text-sm font-medium bg-yellow-50 dark:bg-yellow-900/20 px-3 py-1 rounded-full">2</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Zugang/Jahr</span>
              <span className="text-sm font-medium bg-blue-50 dark:bg-blue-900/20 px-3 py-1 rounded-full">0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Letzter Zugang</span>
              <span className="text-sm font-medium bg-blue-50 dark:bg-blue-900/20 px-3 py-1 rounded-full">
                22.05.2023
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Abgänge ges.</span>
              <span className="text-sm font-medium bg-blue-50 dark:bg-blue-900/20 px-3 py-1 rounded-full">19</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm">Letzter Abgang</span>
              <span className="text-sm font-medium bg-blue-50 dark:bg-blue-900/20 px-3 py-1 rounded-full">
                22.10.2024
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

