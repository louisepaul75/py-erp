import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronUp, ArrowUpDown, Warehouse, Filter, Plus } from "lucide-react"

export default function LagerorteTab() {
  return (
    <div className="p-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Warehouse className="h-4 w-4 text-slate-500 dark:text-slate-400" />
            <h3 className="text-sm font-medium">Lagerorte</h3>
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
            <CardTitle className="text-sm font-medium">Lagerorte</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableHead className="font-medium w-1/4">
                      Lager
                      <ChevronUp className="inline-block ml-1 h-4 w-4" />
                    </TableHead>
                    <TableHead className="font-medium">Regal</TableHead>
                    <TableHead className="font-medium">Fach</TableHead>
                    <TableHead className="font-medium">Boden</TableHead>
                    <TableHead className="font-medium">Schütte</TableHead>
                    <TableHead className="font-medium">Slot(s)</TableHead>
                    <TableHead className="font-medium">Abverkauf</TableHead>
                    <TableHead className="font-medium">Sonder</TableHead>
                    <TableHead className="font-medium">Bestand</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell>18187 / Stammlager-Dies...</TableCell>
                    <TableCell>23</TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>6</TableCell>
                    <TableCell>SC832607</TableCell>
                    <TableCell>MZ</TableCell>
                    <TableCell className="text-center">
                      <div className="flex justify-center">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                          checked
                          readOnly
                        />
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex justify-center">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                          readOnly
                        />
                      </div>
                    </TableCell>
                    <TableCell>0</TableCell>
                  </TableRow>
                  <TableRow className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell>18187 / Stammlager-Dies...</TableCell>
                    <TableCell>23</TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>6</TableCell>
                    <TableCell>SC832607</TableCell>
                    <TableCell>MZ</TableCell>
                    <TableCell className="text-center">
                      <div className="flex justify-center">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                          checked
                          readOnly
                        />
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex justify-center">
                        <input
                          type="checkbox"
                          className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                          readOnly
                        />
                      </div>
                    </TableCell>
                    <TableCell>0</TableCell>
                  </TableRow>
                  {[...Array(15)].map((_, i) => (
                    <TableRow key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                      <TableCell></TableCell>
                      <TableCell></TableCell>
                      <TableCell></TableCell>
                      <TableCell></TableCell>
                      <TableCell></TableCell>
                      <TableCell></TableCell>
                      <TableCell></TableCell>
                      <TableCell></TableCell>
                      <TableCell></TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell></TableCell>
                    <TableCell className="font-medium">0</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-2">
          <Button className="rounded-full">Bestand ändern</Button>
          <Button variant="outline" className="rounded-full">
            Umbuchen
          </Button>
          <Button variant="outline" className="rounded-full ml-auto">
            <Plus className="h-4 w-4 mr-1" />
            <span>Neuer Lagerort</span>
          </Button>
        </div>
      </div>
    </div>
  )
}

