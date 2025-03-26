"use client"

import * as Dialog from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Product } from "../types/product"

interface ProductDetailDialogProps {
  isOpen: boolean
  onClose: () => void
  product: Product | null
}

export default function ProductDetailDialog({
  isOpen,
  onClose,
  product,
}: ProductDetailDialogProps) {
  if (!product) return null

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed left-[50%] top-[50%] z-50 max-h-[85vh] w-[90vw] max-w-2xl translate-x-[-50%] translate-y-[-50%] rounded-lg bg-white dark:bg-slate-800 p-4 shadow-lg focus:outline-none overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <Dialog.Title className="text-xl font-semibold">
              Produktdetails: {product.name}
            </Dialog.Title>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>

          <Tabs defaultValue="details">
            <TabsList className="w-full">
              <TabsTrigger value="details" className="flex-1">Grunddaten</TabsTrigger>
              <TabsTrigger value="technical" className="flex-1">Technische Daten</TabsTrigger>
              <TabsTrigger value="media" className="flex-1">Medien</TabsTrigger>
            </TabsList>

            <TabsContent value="details" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">SKU</h3>
                  <p>{product.sku}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Status</h3>
                  <div className="flex gap-2 mt-1">
                    <Badge variant={product.is_active ? "default" : "destructive"} className={product.is_active ? "bg-green-500" : ""}>
                      {product.is_active ? "Aktiv" : "Inaktiv"}
                    </Badge>
                    {product.is_new && <Badge variant="default" className="bg-purple-500">Neu</Badge>}
                    {product.is_discontinued && <Badge variant="outline">Eingestellt</Badge>}
                  </div>
                </div>
                <div className="col-span-2">
                  <h3 className="text-sm font-medium text-gray-500">Name</h3>
                  <p>{product.name}</p>
                </div>
                <div className="col-span-2">
                  <h3 className="text-sm font-medium text-gray-500">Kurzbeschreibung</h3>
                  <p>{product.short_description || "—"}</p>
                </div>
                <div className="col-span-2">
                  <h3 className="text-sm font-medium text-gray-500">Beschreibung</h3>
                  <p className="whitespace-pre-line">{product.description || "—"}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Kategorie</h3>
                  <p>{product.category || "—"}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Varianten</h3>
                  <p>{product.variants_count || 0}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Erstellt am</h3>
                  <p>{new Date(product.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Zuletzt aktualisiert</h3>
                  <p>{new Date(product.updated_at).toLocaleDateString()}</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="technical" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Gewicht</h3>
                  <p>{product.weight ? `${product.weight} g` : "—"}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Abmessungen</h3>
                  <p>
                    {product.length_mm && product.width_mm && product.height_mm
                      ? `${product.length_mm} × ${product.width_mm} × ${product.height_mm} mm`
                      : "—"}
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Hängend</h3>
                  <p>{product.is_hanging ? "Ja" : "Nein"}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Einseitig</h3>
                  <p>{product.is_one_sided ? "Ja" : "Nein"}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Legacy ID</h3>
                  <p>{product.legacy_id || "—"}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Legacy Base SKU</h3>
                  <p>{product.legacy_base_sku || "—"}</p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="media" className="space-y-4 mt-4">
              {product.images && product.images.length > 0 ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {product.images.map((image, index) => (
                    <div key={index} className="relative aspect-square rounded-md overflow-hidden">
                      <img
                        src={image}
                        alt={`${product.name} - Bild ${index + 1}`}
                        className="object-cover w-full h-full"
                      />
                      {product.primary_image === image && (
                        <div className="absolute top-2 right-2">
                          <Badge>Hauptbild</Badge>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  Keine Bilder vorhanden
                </div>
              )}
            </TabsContent>
          </Tabs>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
} 