import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Scale, TrendingUp, BarChart, RefreshCw } from "lucide-react"

export default function GewogenTab() {
  return (
    <div className="p-6">
      <div className="space-y-6">
        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 flex flex-row items-center">
            <Scale className="h-4 w-4 mr-2 text-slate-500 dark:text-slate-400" />
            <CardTitle className="text-sm font-medium">Gewicht</CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Input
                type="text"
                className="w-32 text-right border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                defaultValue="0"
              />
              <span className="text-sm text-slate-500 dark:text-slate-400">g</span>
              <Button variant="outline" size="sm" className="h-9 rounded-full ml-auto">
                <RefreshCw className="h-4 w-4 mr-1" />
                <span className="text-xs">Aktualisieren</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
              <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-medium">Gewichtsmessungen</CardTitle>
                <Button variant="ghost" size="sm" className="h-8 rounded-full">
                  <BarChart className="h-4 w-4 mr-1" />
                  <span className="text-xs">Diagramm</span>
                </Button>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                        <TableHead className="font-medium">Datum</TableHead>
                        <TableHead className="font-medium">Zeit</TableHead>
                        <TableHead className="font-medium">g</TableHead>
                        <TableHead className="font-medium">Stück</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {[...Array(12)].map((_, i) => (
                        <TableRow key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                          <TableCell></TableCell>
                          <TableCell></TableCell>
                          <TableCell></TableCell>
                          <TableCell></TableCell>
                        </TableRow>
                      ))}
                      <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                        <TableCell className="font-medium">0</TableCell>
                        <TableCell></TableCell>
                        <TableCell className="font-medium">0</TableCell>
                        <TableCell className="font-medium">0</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </div>

          <div>
            <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
              <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 flex flex-row items-center">
                <TrendingUp className="h-4 w-4 mr-2 text-slate-500 dark:text-slate-400" />
                <CardTitle className="text-sm font-medium">Statistik</CardTitle>
              </CardHeader>
              <CardContent className="p-4 space-y-6">
                <div>
                  <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Durchschnittsgewicht:</div>
                  <div className="text-xl font-medium">0 g</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500 dark:text-slate-400 mb-1">Standardabweichung:</div>
                  <div className="text-lg font-medium">0,00 g</div>
                  <div className="text-lg font-medium">0,00 %</div>
                </div>
                <Button className="w-full rounded-full">Ø übernehmen</Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

