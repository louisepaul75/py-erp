import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Plus, Minus } from "lucide-react"

export default function MutterTab() {
  return (
    <div className="p-4">
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <label className="text-sm">Bezeichnung</label>
          <div className="flex-1">
            <Input defaultValue="&quot;Adler&quot;-Lock" />
          </div>
        </div>
        <div className="flex items-start gap-2">
          <label className="text-sm pt-1">Beschreibung</label>
          <div className="flex-1">
            <textarea
              className="w-full border rounded p-2 text-sm min-h-[150px]"
              defaultValue="Erleben Sie die Eleganz und den Charme vergangener Zeiten mit dieser exquisiten Zinnfigur, inspiriert von den Anfängen der Eisenbahngeschichte. Perfekt für Sammler und Liebhaber von Nostalgie, zeigt diese Figur einen klassischen Lokführer, gekleidet in traditioneller Montur, der stolz seine Maschine lenkt. Ideal für jede Vitrine oder als geschmackvolles Geschenk. Eine Hommage an die Ingenieurskunst und das kulturelle Erbe."
            />
          </div>
        </div>
      </div>

      <div className="mb-4">
        <h3 className="text-sm font-medium mb-2">Maße</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <input type="checkbox" id="hangend" />
            <label htmlFor="hangend" className="text-sm">
              Hängend
            </label>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm w-24">Boxgröße</label>
            <Input defaultValue="B5" className="w-32" />
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="einseitig" />
            <label htmlFor="einseitig" className="text-sm">
              Einseitig
            </label>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="neuheit" />
            <label htmlFor="neuheit" className="text-sm">
              Neuheit
            </label>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm w-24">Breite</label>
            <Input defaultValue="7" className="w-32" />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm w-24">Höhe</label>
            <Input defaultValue="7" className="w-32" />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm w-24">Tiefe</label>
            <Input defaultValue="0,7" className="w-32" />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm w-24">Gewicht</label>
            <Input defaultValue="30" className="w-32" />
          </div>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium">Kategorien</h3>
          <div className="flex gap-2">
            <Button variant="outline" size="icon" className="h-6 w-6">
              <Plus className="h-3 w-3" />
            </Button>
            <Button variant="outline" size="icon" className="h-6 w-6">
              <Minus className="h-3 w-3" />
            </Button>
          </div>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Home</TableHead>
              <TableHead>Sortiment</TableHead>
              <TableHead>Tradition</TableHead>
              <TableHead>Maschinerie</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Home</TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell>All Products</TableCell>
            </TableRow>
            <TableRow>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
            </TableRow>
            <TableRow>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
              <TableCell></TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

