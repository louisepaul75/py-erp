"use client"

import type React from "react"

import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Edit, Trash2, AlertCircle } from "lucide-react"
import { addCustomerShippingAddress } from "@/lib/api/customers"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Badge } from "@/components/ui/badge"
import { CountrySelect } from "@/components/ui/country-select"
import type { ShippingAddress } from "@/lib/types"

/**
 * Komponente zur Anzeige und Verwaltung von Lieferadressen eines Kunden
 */
export default function CustomerAddressesCard({
  addresses,
  customerId,
}: {
  addresses: ShippingAddress[]
  customerId: string
}) {
  const [showAddressDialog, setShowAddressDialog] = useState(false)
  const [editingAddress, setEditingAddress] = useState<ShippingAddress | null>(null)
  const [deleteAddressId, setDeleteAddressId] = useState<string | null>(null)
  const [selectedCountry, setSelectedCountry] = useState<string>("DE") // Default: Deutschland
  const queryClient = useQueryClient()

  // Mutation for adding a new address
  const addAddressMutation = useMutation({
    mutationFn: (addressData: Omit<ShippingAddress, "id" | "customerId" | "createdAt" | "updatedAt">) =>
      addCustomerShippingAddress(customerId, addressData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customer", customerId] })
      setShowAddressDialog(false)
      setEditingAddress(null)
    },
  })

  const handleEditAddress = (address: ShippingAddress) => {
    setEditingAddress(address)
    setSelectedCountry(address.country)
    setShowAddressDialog(true)
  }

  const handleAddAddress = () => {
    setEditingAddress(null)
    setSelectedCountry("DE") // Default: Deutschland
    setShowAddressDialog(true)
  }

  const handleSaveAddress = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)

    const addressData = {
      street: formData.get("street") as string,
      streetNumber: formData.get("streetNumber") as string,
      postalCode: formData.get("postalCode") as string,
      city: formData.get("city") as string,
      country: selectedCountry,
      state: formData.get("state") as string,
      isDefault: formData.get("isDefault") === "on",
      addressLabel: formData.get("addressLabel") as string,
    }

    addAddressMutation.mutate(addressData)
  }

  const handleDeleteAddress = (addressId: string) => {
    setDeleteAddressId(addressId)
  }

  const confirmDeleteAddress = () => {
    // In einer echten Anwendung würde hier die Adresse gelöscht werden
    setDeleteAddressId(null)
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Lieferadressen</CardTitle>
          <Button variant="outline" size="sm" onClick={handleAddAddress}>
            <Plus className="mr-2 h-4 w-4" />
            Hinzufügen
          </Button>
        </CardHeader>
        <CardContent>
          {addresses.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground">
              Keine Lieferadressen für diesen Kunden gefunden.
            </div>
          ) : (
            <div className="space-y-4">
              {addresses.map((address) => (
                <div key={address.id} className="rounded-lg border p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium">
                        {address.addressLabel || "Lieferadresse"}
                        {address.isDefault && (
                          <Badge variant="outline" className="ml-2">
                            Standard
                          </Badge>
                        )}
                      </h3>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm" onClick={() => handleEditAddress(address)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-destructive hover:text-destructive"
                        onClick={() => handleDeleteAddress(address.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="mt-2 space-y-1 text-sm">
                    <p>{`${address.street} ${address.streetNumber}`}</p>
                    <p>{`${address.postalCode} ${address.city}`}</p>
                    <p>{address.country}</p>
                    {address.state && <p>{address.state}</p>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog zum Hinzufügen/Bearbeiten einer Adresse */}
      <Dialog open={showAddressDialog} onOpenChange={setShowAddressDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>{editingAddress ? "Lieferadresse bearbeiten" : "Lieferadresse hinzufügen"}</DialogTitle>
            <DialogDescription>
              {editingAddress
                ? "Aktualisieren Sie die Daten der Lieferadresse."
                : "Geben Sie die Daten der neuen Lieferadresse ein."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSaveAddress}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="addressLabel" className="text-right">
                  Bezeichnung
                </Label>
                <Input
                  id="addressLabel"
                  name="addressLabel"
                  defaultValue={editingAddress?.addressLabel || ""}
                  placeholder="z.B. Hauptsitz, Lager"
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="street" className="text-right">
                  Straße
                </Label>
                <Input
                  id="street"
                  name="street"
                  defaultValue={editingAddress?.street || ""}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="streetNumber" className="text-right">
                  Hausnummer
                </Label>
                <Input
                  id="streetNumber"
                  name="streetNumber"
                  defaultValue={editingAddress?.streetNumber || ""}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="postalCode" className="text-right">
                  PLZ
                </Label>
                <Input
                  id="postalCode"
                  name="postalCode"
                  defaultValue={editingAddress?.postalCode || ""}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="city" className="text-right">
                  Ort
                </Label>
                <Input
                  id="city"
                  name="city"
                  defaultValue={editingAddress?.city || ""}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="country" className="text-right">
                  Land
                </Label>
                <div className="col-span-3">
                  <CountrySelect value={selectedCountry} onValueChange={setSelectedCountry} />
                </div>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="state" className="text-right">
                  Bundesland
                </Label>
                <Input id="state" name="state" defaultValue={editingAddress?.state || ""} className="col-span-3" />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <div></div>
                <div className="col-span-3 flex items-center space-x-2">
                  <Checkbox id="isDefault" name="isDefault" defaultChecked={editingAddress?.isDefault || false} />
                  <Label htmlFor="isDefault">Als Standard-Lieferadresse festlegen</Label>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" disabled={addAddressMutation.isPending}>
                {addAddressMutation.isPending ? "Wird gespeichert..." : "Speichern"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete confirmation dialog */}
      <AlertDialog open={!!deleteAddressId} onOpenChange={(open) => !open && setDeleteAddressId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              Lieferadresse löschen
            </AlertDialogTitle>
            <AlertDialogDescription>
              Sind Sie sicher, dass Sie diese Lieferadresse löschen möchten? Diese Aktion kann nicht rückgängig gemacht
              werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDeleteAddress}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Löschen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
