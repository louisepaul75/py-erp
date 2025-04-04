// components/ProductDetail/VariantenHeader.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Plus, Minus } from "lucide-react";
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
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

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

interface VariantenHeaderProps {
  onAddVariant: (newVariant: Variant) => void; // Updated to accept a new variant
  onRemoveVariants: () => void;
  variants: Variant[]; // Pass variants to check if any are selected
}

export default function VariantenHeader({
  onAddVariant,
  onRemoveVariants,
  variants,
}: VariantenHeaderProps) {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isRemoveDialogOpen, setIsRemoveDialogOpen] = useState(false);
  const [newVariant, setNewVariant] = useState<
    Omit<Variant, "id" | "selected">
  >({
    nummer: "",
    bezeichnung: "",
    auspraegung: "",
    prod: false,
    vertr: false,
    vkArtikel: false,
    releas: new Date().toLocaleDateString("de-DE"),
  });

  // Handle Add Variant
  const handleAddVariantConfirm = () => {
    const newVariantWithId: Variant = {
      ...newVariant,
      id: (variants.length + 1).toString(),
      selected: false,
    };
    onAddVariant(newVariantWithId); // Pass the new variant to the parent
    setIsAddDialogOpen(false); // Close the modal
    setNewVariant({
      nummer: "",
      bezeichnung: "",
      auspraegung: "",
      prod: false,
      vertr: false,
      vkArtikel: false,
      releas: new Date().toLocaleDateString("de-DE"),
    }); // Reset the form
  };

  // Handle Remove Variants
  const handleRemoveVariantsConfirm = () => {
    if (variants.some((v) => v.selected)) {
      // onRemoveVariants(); // Remove selected variants
      setIsRemoveDialogOpen(true);
    } else {
      setIsRemoveDialogOpen(true); // Show the "No Variants Selected" modal
    }
  };

  const handleRemoveAction = () => {
    onRemoveVariants(); // Remove selected variants
    setIsRemoveDialogOpen(false); // Close the dialog
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <CardTitle>Varianten</CardTitle>
            <CardDescription className="mt-1">
              Verwalten Sie verschiedene Ausführungen dieses Produkts
            </CardDescription>
          </div>
          <div className="flex gap-2 mt-2 md:mt-0">
            {/* Add Variant Button */}
            <AlertDialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
              <AlertDialogTrigger asChild>
                <Button variant="outline" size="sm" className="h-9 rounded-full">
                  <Plus className="h-4 w-4 mr-1" />
                  <span>Hinzufügen</span>
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Neue Variante hinzufügen</AlertDialogTitle>
                  <AlertDialogDescription>
                    Geben Sie die Details für die neue Variante ein.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <div className="space-y-4">
                  <Input
                    placeholder="Nummer"
                    value={newVariant.nummer}
                    onChange={(e) =>
                      setNewVariant({ ...newVariant, nummer: e.target.value })
                    }
                  />
                  <Input
                    placeholder="Bezeichnung"
                    value={newVariant.bezeichnung}
                    onChange={(e) =>
                      setNewVariant({
                        ...newVariant,
                        bezeichnung: e.target.value,
                      })
                    }
                  />
                  <Input
                    placeholder="Ausprägung"
                    value={newVariant.auspraegung}
                    onChange={(e) =>
                      setNewVariant({
                        ...newVariant,
                        auspraegung: e.target.value,
                      })
                    }
                  />
                </div>
                <AlertDialogFooter>
                  <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                  <AlertDialogAction onClick={handleAddVariantConfirm}>
                    Hinzufügen
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

            {/* Remove Variants Button */}
            <AlertDialog
              open={isRemoveDialogOpen}
              onOpenChange={setIsRemoveDialogOpen}
            >
              <AlertDialogTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-9 rounded-full"
                  onClick={handleRemoveVariantsConfirm}
                >
                  <Minus className="h-4 w-4 mr-1" />
                  <span>Entfernen</span>
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>
                    {variants.some((v) => v.selected)
                      ? "Sind Sie sicher?"
                      : "Keine Varianten ausgewählt"}
                  </AlertDialogTitle>
                  <AlertDialogDescription>
                    {variants.some((v) => v.selected)
                      ? "Möchten Sie die ausgewählten Varianten wirklich entfernen?"
                      : "Bitte wählen Sie mindestens eine Variante zum Entfernen aus."}
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                  {variants.some((v) => v.selected) && (
                    <AlertDialogAction onClick={handleRemoveAction}>
                      Entfernen
                    </AlertDialogAction>
                  )}
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </CardHeader>
    </Card>
  );
}
