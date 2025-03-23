// components/ProductDetail/VariantenTable.tsx
import { useState } from "react";
import { Button, Input } from "@/components/ui";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Download, Search, MoreHorizontal } from "lucide-react";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";

interface Variant {
  id: string;
  nummer: string;
  bezeichnung: string;
  auspraegung: string;
  prod: boolean;
  vertr: boolean;
  vkArtikel: boolean;
  releas: string;
  selected: boolean;
}

interface VariantenTableProps {
  variants: Variant[];
  setVariants: (variants: Variant[]) => void; // Pass setVariants
  searchTerm: string;
  onSearchChange: (term: string) => void;
  onExport: (filteredVariants: Variant[]) => void; 
  onToggleSelect: (id: string) => void;
  onToggleCheckbox: (id: string, field: "prod" | "vertr" | "vkArtikel") => void;
  onMoreAction: (id: string) => void;
  onEditVariant: () => void;
  onDeleteVariant: () => void;
}

export default function VariantenTable({
  variants,
  setVariants,
  searchTerm,
  onSearchChange,
  onExport,
  onToggleSelect,
  onToggleCheckbox,
  onMoreAction,
  onEditVariant,
  onDeleteVariant,
}: VariantenTableProps) {

  const handleSelectAll = () => {
    const allSelected = variants.every((v) => v.selected);
    console.log("allSelected",allSelected)
    setVariants(variants.map((v) => ({ ...v, selected: !allSelected })));
    console.log("handleSelectAll");
  };

  const [selectedVariantId, setSelectedVariantId] = useState<string | null>(
    null
  );

  const filteredVariants = variants.filter(
    (variant) =>
      variant.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      variant.bezeichnung.toLowerCase().includes(searchTerm.toLowerCase()) ||
      variant.auspraegung.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden">
      <div className="p-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="relative w-full sm:w-64">
            <Input
              className="pl-9 h-10 rounded-full border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus-visible:ring-blue-500"
              placeholder="Suchen..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
            />
            <div className="absolute left-3 top-1/2 -translate-y-1/2">
              <Search className="h-4 w-4 text-slate-400" />
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="h-9 rounded-full"
            onClick={() => onExport(filteredVariants)} // Pass filteredVariants to onExport
          >
            <Download className="h-4 w-4 mr-1" />
            Exportieren
          </Button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <TableHead className="w-12">
                {/* <input
                  type="checkbox"
                  checked={variants.every((v) => v.selected)}
                  onChange={() => variants.forEach((v) => onToggleSelect(v.id))}
                  className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                /> */}
                <input
                  type="checkbox"
                  checked={variants.length > 0 && variants.every((v) => v.selected)} // Ensure it only checks when there are rows
                  onChange={handleSelectAll}
                  className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                />
              </TableHead>
              <TableHead className="font-medium">Nummer</TableHead>
              <TableHead className="font-medium">Bezeichnung</TableHead>
              <TableHead className="font-medium">Ausprägung</TableHead>
              <TableHead className="w-12 text-center font-medium">
                Prod.
              </TableHead>
              <TableHead className="w-12 text-center font-medium">
                Vertr.
              </TableHead>
              <TableHead className="w-12 text-center font-medium">
                VK Artikel
              </TableHead>
              <TableHead className="font-medium">Releas</TableHead>
              <TableHead className="w-10"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredVariants.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} className="text-center py-4">
                  Keine Varianten gefunden
                </TableCell>
              </TableRow>
            ) : (
              filteredVariants.map((variant) => (
                <TableRow
                  key={variant.id}
                  className={
                    variant.selected ? "bg-blue-50/50 dark:bg-blue-900/10" : ""
                  }
                >
                  <TableCell>
                    <input
                      type="checkbox"
                      checked={variant.selected}
                      onChange={() => onToggleSelect(variant.id)}
                      className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                    />
                  </TableCell>
                  <TableCell className="font-medium">
                    {variant.nummer}
                  </TableCell>
                  <TableCell>{variant.bezeichnung}</TableCell>
                  <TableCell>{variant.auspraegung}</TableCell>
                  <TableCell className="text-center">
                    <input
                      type="checkbox"
                      checked={variant.prod}
                      onChange={() => onToggleCheckbox(variant.id, "prod")}
                      className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                    />
                  </TableCell>
                  <TableCell className="text-center">
                    <input
                      type="checkbox"
                      checked={variant.vertr}
                      onChange={() => onToggleCheckbox(variant.id, "vertr")}
                      className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                    />
                  </TableCell>
                  <TableCell className="text-center">
                    <input
                      type="checkbox"
                      checked={variant.vkArtikel}
                      onChange={() => onToggleCheckbox(variant.id, "vkArtikel")}
                      className="h-4 w-4 rounded border-slate-300 dark:border-slate-600"
                    />
                  </TableCell>
                  <TableCell>{variant.releas}</TableCell>
                  <TableCell>
                    <AlertDialog
                      open={selectedVariantId === variant.id}
                      onOpenChange={(open) =>
                        !open && setSelectedVariantId(null)
                      }
                    >
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 rounded-full"
                          onClick={() => {
                            setSelectedVariantId(variant.id);
                            onMoreAction(variant.id);
                          }}
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>
                            Aktionen für Variante {selectedVariantId}
                          </AlertDialogTitle>
                          <AlertDialogDescription>
                            Wählen Sie eine Aktion für diese Variante aus.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter className="flex flex-col sm:flex-row sm:justify-end gap-2">
                          <Button variant="outline" onClick={onEditVariant}>
                            Bearbeiten
                          </Button>
                          <Button
                            variant="destructive"
                            onClick={onDeleteVariant}
                          >
                            Löschen
                          </Button>
                          <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
