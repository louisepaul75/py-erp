"use client"

import type React from "react"

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ShoppingBag, Plus, Edit, Trash2, AlertCircle, ExternalLink } from "lucide-react"
import { fetchCustomerShopAccounts, addCustomerShopAccount, deleteCustomerShopAccount } from "@/lib/api/customers"
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
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
import type { ShopAccount, ShopPlatform } from "@/lib/types"

/**
 * Komponente zur Anzeige und Verwaltung von Shop-Accounts eines Kunden
 * Maximal 3 Accounts können hinzugefügt werden
 */
export default function CustomerShopAccountsCard({
  customerId,
}: {
  customerId: string
}) {
  const [showAccountDialog, setShowAccountDialog] = useState(false)
  const [editingAccount, setEditingAccount] = useState<ShopAccount | null>(null)
  const [deleteAccountId, setDeleteAccountId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Fetch shop accounts using TanStack Query
  const { data: shopAccounts, isLoading } = useQuery({
    queryKey: ["customerShopAccounts", customerId],
    queryFn: () => fetchCustomerShopAccounts(customerId),
  })

  // Mutation for adding a new shop account
  const addAccountMutation = useMutation({
    mutationFn: (accountData: Omit<ShopAccount, "id" | "customerId" | "createdAt" | "updatedAt">) =>
      addCustomerShopAccount(customerId, accountData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customerShopAccounts", customerId] })
      setShowAccountDialog(false)
      setEditingAccount(null)
    },
  })

  // Mutation for deleting a shop account
  const deleteAccountMutation = useMutation({
    mutationFn: (accountId: string) => deleteCustomerShopAccount(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customerShopAccounts", customerId] })
      setDeleteAccountId(null)
    },
  })

  const handleEditAccount = (account: ShopAccount) => {
    setEditingAccount(account)
    setShowAccountDialog(true)
  }

  const handleAddAccount = () => {
    setEditingAccount(null)
    setShowAccountDialog(true)
  }

  const handleSaveAccount = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)

    const accountData = {
      platform: formData.get("platform") as ShopPlatform,
      accountId: formData.get("accountId") as string,
      accountName: formData.get("accountName") as string,
      url: formData.get("url") as string,
      isPrimary: formData.get("isPrimary") === "on",
    }

    addAccountMutation.mutate(accountData)
  }

  const handleDeleteAccount = (accountId: string) => {
    setDeleteAccountId(accountId)
  }

  const confirmDeleteAccount = () => {
    if (deleteAccountId) {
      deleteAccountMutation.mutate(deleteAccountId)
    }
  }

  // Hilfsfunktion zum Abrufen des Plattform-Labels
  const getPlatformLabel = (platform: ShopPlatform): string => {
    switch (platform) {
      case "amazon":
        return "Amazon"
      case "ebay":
        return "eBay"
      case "shopware":
        return "Shopware"
      case "magento":
        return "Magento"
      case "woocommerce":
        return "WooCommerce"
      case "shopify":
        return "Shopify"
      default:
        return platform
    }
  }

  // Hilfsfunktion zum Abrufen der Plattform-Farbe
  const getPlatformColor = (platform: ShopPlatform): string => {
    switch (platform) {
      case "amazon":
        return "bg-[#FF9900] text-black"
      case "ebay":
        return "bg-[#E53238] text-white"
      case "shopware":
        return "bg-[#189EFF] text-white"
      case "magento":
        return "bg-[#F26322] text-white"
      case "woocommerce":
        return "bg-[#96588A] text-white"
      case "shopify":
        return "bg-[#7AB55C] text-white"
      default:
        return "bg-gray-500 text-white"
    }
  }

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <ShoppingBag className="h-5 w-5" />
            Shop-Accounts
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleAddAccount}
            disabled={shopAccounts && shopAccounts.length >= 3}
          >
            <Plus className="mr-2 h-4 w-4" />
            Hinzufügen
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-4">Shop-Accounts werden geladen...</div>
          ) : !shopAccounts || shopAccounts.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground">
              Keine Shop-Accounts für diesen Kunden gefunden.
            </div>
          ) : (
            <div className="space-y-4">
              {shopAccounts.map((account) => (
                <div key={account.id} className="flex items-center justify-between rounded-lg border p-4">
                  <div className="flex items-center gap-3">
                    <div className={`rounded-md px-2 py-1 ${getPlatformColor(account.platform)}`}>
                      {getPlatformLabel(account.platform)}
                    </div>
                    <div>
                      <div className="font-medium flex items-center gap-2">
                        {account.accountName}
                        {account.isPrimary && <Badge variant="outline">Primär</Badge>}
                      </div>
                      <div className="text-sm text-muted-foreground">ID: {account.accountId}</div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {account.url && (
                      <Button variant="ghost" size="sm" asChild>
                        <a href={account.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                    <Button variant="ghost" size="sm" onClick={() => handleEditAccount(account)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={() => handleDeleteAccount(account.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
              {shopAccounts.length >= 3 && (
                <div className="text-sm text-muted-foreground mt-2">
                  Maximale Anzahl von Shop-Accounts (3) erreicht.
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog zum Hinzufügen/Bearbeiten eines Shop-Accounts */}
      <Dialog open={showAccountDialog} onOpenChange={setShowAccountDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>{editingAccount ? "Shop-Account bearbeiten" : "Shop-Account hinzufügen"}</DialogTitle>
            <DialogDescription>
              {editingAccount
                ? "Aktualisieren Sie die Daten des Shop-Accounts."
                : "Geben Sie die Daten des neuen Shop-Accounts ein."}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSaveAccount}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="platform" className="text-right">
                  Plattform
                </Label>
                <Select name="platform" defaultValue={editingAccount?.platform || "amazon"}>
                  <SelectTrigger className="col-span-3">
                    <SelectValue placeholder="Plattform auswählen" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="amazon">Amazon</SelectItem>
                    <SelectItem value="ebay">eBay</SelectItem>
                    <SelectItem value="shopware">Shopware</SelectItem>
                    <SelectItem value="magento">Magento</SelectItem>
                    <SelectItem value="woocommerce">WooCommerce</SelectItem>
                    <SelectItem value="shopify">Shopify</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="accountName" className="text-right">
                  Name
                </Label>
                <Input
                  id="accountName"
                  name="accountName"
                  defaultValue={editingAccount?.accountName || ""}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="accountId" className="text-right">
                  Account-ID
                </Label>
                <Input
                  id="accountId"
                  name="accountId"
                  defaultValue={editingAccount?.accountId || ""}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="url" className="text-right">
                  URL
                </Label>
                <Input
                  id="url"
                  name="url"
                  type="url"
                  defaultValue={editingAccount?.url || ""}
                  placeholder="https://"
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <div></div>
                <div className="col-span-3 flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="isPrimary"
                    name="isPrimary"
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                    defaultChecked={editingAccount?.isPrimary || false}
                  />
                  <Label htmlFor="isPrimary">Als primären Account festlegen</Label>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" disabled={addAccountMutation.isPending}>
                {addAccountMutation.isPending ? "Wird gespeichert..." : "Speichern"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete confirmation dialog */}
      <AlertDialog open={!!deleteAccountId} onOpenChange={(open) => !open && setDeleteAccountId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              Shop-Account löschen
            </AlertDialogTitle>
            <AlertDialogDescription>
              Sind Sie sicher, dass Sie diesen Shop-Account löschen möchten? Diese Aktion kann nicht rückgängig gemacht
              werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDeleteAccount}
              disabled={deleteAccountMutation.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteAccountMutation.isPending ? "Wird gelöscht..." : "Löschen"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
