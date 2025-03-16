import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Filter, ArrowUpDown, Calendar, Download } from "lucide-react"

export default function BewegungenTab() {
  return (
    <div className="p-6">
      <div className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="relative flex-1 max-w-xs">
              <Input
                className="pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800"
                placeholder="Suchen..."
              />
              <div className="absolute left-3 top-1/2 -translate-y-1/2">
                <Search className="h-4 w-4 text-slate-400" />
              </div>
            </div>
            <Button variant="ghost" size="sm" className="h-9 rounded-full">
              <Filter className="h-4 w-4 mr-1" />
              <span className="text-xs">Filter</span>
            </Button>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="h-9 rounded-full">
              <Calendar className="h-4 w-4 mr-1" />
              <span className="text-xs">Zeitraum</span>
            </Button>
            <Button variant="outline" size="sm" className="h-9 rounded-full">
              <Download className="h-4 w-4 mr-1" />
              <span className="text-xs">Exportieren</span>
            </Button>
          </div>
        </div>

        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium">Bewegungen</CardTitle>
            <Button variant="ghost" size="sm" className="h-8 rounded-full">
              <ArrowUpDown className="h-4 w-4 mr-1" />
              <span className="text-xs">Sortieren</span>
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableHead className="font-medium">Kunden-Nr</TableHead>
                    <TableHead className="font-medium">Kunde</TableHead>
                    <TableHead className="font-medium">Art</TableHead>
                    <TableHead className="font-medium">Beleg-Nr</TableHead>
                    <TableHead className="font-medium">Datum</TableHead>
                    <TableHead className="font-medium">Menge</TableHead>
                    <TableHead className="font-medium">Preis</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell>1891810</TableCell>
                    <TableCell>ADK</TableCell>
                    <TableCell>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                        L
                      </span>
                    </TableCell>
                    <TableCell>202060</TableCell>
                    <TableCell>22.10.2024</TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>66,70 €</TableCell>
                  </TableRow>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell>1440011</TableCell>
                    <TableCell>E.&A. vor dem Brocke Mackenbrock G...</TableCell>
                    <TableCell>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">
                        R
                      </span>
                    </TableCell>
                    <TableCell>2010292</TableCell>
                    <TableCell>23.09.2024</TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>27,80 €</TableCell>
                  </TableRow>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell>1440011</TableCell>
                    <TableCell>E.&A. vor dem Brocke Mackenbrock G...</TableCell>
                    <TableCell>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        A
                      </span>
                    </TableCell>
                    <TableCell>210870</TableCell>
                    <TableCell>18.09.2024</TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>27,80 €</TableCell>
                  </TableRow>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell>DE20060</TableCell>
                    <TableCell>Tropp</TableCell>
                    <TableCell>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        A
                      </span>
                    </TableCell>
                    <TableCell>210688</TableCell>
                    <TableCell>06.08.2024</TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>24,20 €</TableCell>
                  </TableRow>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell>DE20060</TableCell>
                    <TableCell>Tropp</TableCell>
                    <TableCell>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        A
                      </span>
                    </TableCell>
                    <TableCell>210689</TableCell>
                    <TableCell>06.08.2024</TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>24,20 €</TableCell>
                  </TableRow>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell>128017</TableCell>
                    <TableCell>Tropp</TableCell>
                    <TableCell>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        A
                      </span>
                    </TableCell>
                    <TableCell>210690</TableCell>
                    <TableCell>06.08.2024</TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>52,30 €</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <input type="checkbox" id="nur-r" className="h-4 w-4 rounded border-slate-300 dark:border-slate-600" />
            <label htmlFor="nur-r" className="text-sm">
              Nur R
            </label>
          </div>
          <div className="text-sm text-slate-500 dark:text-slate-400">Gesamt: 6 Einträge</div>
        </div>
      </div>
    </div>
  )
}

