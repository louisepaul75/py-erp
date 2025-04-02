// components/ProductDetail/DetailsTab.tsx
import { useState } from "react";
import { Button, Input } from "@/components/ui";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/ui";
import { Plus, Minus, Tag, Zap } from "lucide-react";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
} from "@/components/ui/alert-dialog";
import React from "react";
import { cn } from "@/lib/utils";

interface VariantDetails {
  tags: string[];
  priceChanges: string;
  malgruppe: string;
  malkostenEur: string;
  malkostenCzk: string;
  selbstkosten: string;
}

interface DetailsTabProps {
  variantDetails: VariantDetails;
  onDetailChange: (field: keyof VariantDetails, value: string) => void;
  onAddTag: () => void;
  onRemoveTag: (tag: string) => void;
  isEditing: boolean;
}

export default function DetailsTab({
  variantDetails,
  onDetailChange,
  onAddTag,
  onRemoveTag,
  isEditing,
}: DetailsTabProps) {
  return (
    <div className="p-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 ">
        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm overflow-auto">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
            <CardTitle className="text-sm font-medium">Tags</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="p-4">
              <div className="flex flex-wrap gap-2 mb-4">
                {variantDetails.tags.map((tag) => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    {tag}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-4 w-4 ml-1"
                      onClick={() => onRemoveTag(tag)}
                      disabled={!isEditing}
                    >
                      <Minus className="h-3 w-3" />
                    </Button>
                  </Badge>
                ))}
              </div>
              <Button
                variant="outline"
                size="sm"
                className="w-full rounded-lg"
                onClick={onAddTag}
                disabled={!isEditing}
              >
                <Plus className="h-3.5 w-3.5 mr-1" />
                Tag hinzufügen
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className=" dark:border-slate-700 shadow-sm overflow-auto">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 ">
            <CardTitle className="text-sm font-medium">Publish</CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Status</span>
                <Badge
                  variant={"default"}
                  className={cn("text-xs", "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-900/50")}
                >
                  Aktiv
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Sichtbarkeit</span>
                <Badge variant="secondary">
                  Öffentlich
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Erstellt am</span>
                <span className="text-sm">01.01.2023</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Aktualisiert am</span>
                <span className="text-sm">22.10.2024</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
          <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
            <CardTitle className="text-sm font-medium">Preise</CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            <Select defaultValue="de" disabled={!isEditing}>
              <SelectTrigger className="w-full p-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 mb-3">
                <SelectValue placeholder="Select Tax..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="de">DE - 19% Germany</SelectItem>
              </SelectContent>
            </Select>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Laden</span>
                <span className="text-sm font-medium">37,40 €</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Handel</span>
                <span className="text-sm font-medium">17,30 €</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Empf.</span>
                <span className="text-sm font-medium">29,50 €</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Einkauf</span>
                <span className="text-sm font-medium">9,63 €</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border border-slate-200 dark:border-slate-700 shadow-sm mb-6">
        <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
          <CardTitle className="text-sm font-medium">Preisänderungen</CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <Textarea
            value={variantDetails.priceChanges}
            onChange={(e) => onDetailChange("priceChanges", e.target.value)}
            className="w-full border border-slate-200 dark:border-slate-700 rounded-lg p-3 h-24 resize-none bg-slate-50 dark:bg-slate-800"
            disabled={!isEditing}
          />
        </CardContent>
      </Card>

      <Card className="border border-slate-200 dark:border-slate-700 shadow-sm">
        <CardHeader className="p-4 pb-2 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
          <CardTitle className="text-sm font-medium">
            Zusätzliche Informationen
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Malgruppe
              </label>
              <div className="md:col-span-3">
                <Input
                  value={variantDetails.malgruppe}
                  onChange={(e) => onDetailChange("malgruppe", e.target.value)}
                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Malkosten
              </label>
              <div className="md:col-span-3 flex gap-3">
                <Input
                  value={variantDetails.malkostenEur}
                  onChange={(e) =>
                    onDetailChange("malkostenEur", e.target.value)
                  }
                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
                <Input
                  value={variantDetails.malkostenCzk}
                  onChange={(e) =>
                    onDetailChange("malkostenCzk", e.target.value)
                  }
                  className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
              <label className="text-sm font-medium text-slate-500 dark:text-slate-400">
                Selbstkosten
              </label>
              <div className="md:col-span-3">
                <Input
                  value={variantDetails.selbstkosten}
                  onChange={(e) =>
                    onDetailChange("selbstkosten", e.target.value)
                  }
                  className="w-full md:w-1/3 border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-lg"
                  disabled={!isEditing}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
