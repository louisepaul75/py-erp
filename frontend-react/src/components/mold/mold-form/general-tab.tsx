"use client";

import { useState } from "react";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertTriangle,
  Check,
  Minus,
  Barcode,
  ChevronDown,
  Plus,
  Trash,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { DatePickerField } from "@/components/mold/form/date-picker-field";
import { TagSelector } from "@/components/mold/form/tag-selector";
import { ImageUploader } from "@/components/mold/form/image-uploader";
import type { UseFormReturn } from "react-hook-form";
import type { MoldFormValues } from "@/components/mold/form/mold-form-schema";
import type { Technology } from "@/types/mold/technology";
import type { Alloy } from "@/types/mold/alloy";
import type { Tag } from "@/types/mold/tag";
import type { MoldSize } from "@/types/mold/mold-size";
import { MoldActivityStatus } from "@/types/mold/mold";
import type { Mold } from "@/types/mold/mold";
import useAppTranslation from "@/hooks/useTranslationWrapper";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

/**
 * Props for the GeneralTab component
 */
interface GeneralTabProps {
  form: UseFormReturn<MoldFormValues>;
  mode: "create" | "edit" | "duplicate";
  mold: Mold | null;
  technologies: Technology[];
  alloys: Alloy[];
  tags: Tag[];
  moldSizes: MoldSize[];
  onSubmit: (data: MoldFormValues) => Promise<void>;
  onScanBarcode: () => void;
  onOpenLocationDialog: () => void;
  onAddTechnology: () => void;
  onDeleteTechnology: (name: string) => void;
  onAddMoldSize: () => void;
  onDeleteMoldSize: (name: string ) => void;
}

/**
 * Render the status icon based on the mold status
 */
function renderStatusIcon(
  isActive: boolean,
  activityStatus?: MoldActivityStatus
) {
  if (!activityStatus) {
    return isActive ? (
      <Check className="h-4 w-4 text-green-500" />
    ) : (
      <Minus className="h-4 w-4 text-amber-500" />
    );
  }

  switch (activityStatus) {
    case MoldActivityStatus.ACTIVE:
      return <Check className="h-4 w-4 text-green-500" />;
    case MoldActivityStatus.INACTIVE:
      return <Minus className="h-4 w-4 text-amber-500" />;
    case MoldActivityStatus.MIXED:
      return <AlertTriangle className="h-4 w-4 text-blue-500" />;
  }
}

/**
 * Render the status text based on the mold status
 */
function renderStatusText(
  isActive: boolean,
  activityStatus?: MoldActivityStatus
) {
  if (!activityStatus) {
    return isActive ? "Active" : "Inactive";
  }

  switch (activityStatus) {
    case MoldActivityStatus.ACTIVE:
      return "Active";
    case MoldActivityStatus.INACTIVE:
      return "Inactive";
    case MoldActivityStatus.MIXED:
      return "Mixed";
  }
}

/**
 * General tab for the mold form
 */
export function GeneralTab({
  form,
  mode,
  mold,
  technologies,
  alloys,
  tags,
  moldSizes,
  onSubmit,
  onScanBarcode,
  onOpenLocationDialog,
  onAddTechnology,
  onDeleteTechnology,
  onAddMoldSize,
  onDeleteMoldSize,
}: GeneralTabProps) {
  const [statusChanged, setStatusChanged] = useState(false);

  const { t } = useAppTranslation("mold");



  return (
    <Form {...form}>
      <form
        id="mold-form"
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8"
      >
        {/* Activity Status */}
        <FormField
          control={form.control}
          name="isActive"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
              <div className="space-y-0.5">
                <FormLabel className="text-base">
                  {t("activity_status_label")}
                </FormLabel>
                <FormDescription className="flex items-center gap-2">
                  {mold?.activityStatus && mode === "edit" && (
                    <>
                      {renderStatusIcon(field.value, mold.activityStatus)}
                      <span>
                        {t("current_status_prefix")}{" "}
                        {renderStatusText(field.value, mold.activityStatus)}
                      </span>
                    </>
                  )}
                  {(!mold?.activityStatus || mode !== "edit") && (
                    <>{t("set_active_instruction")}</>
                  )}
                </FormDescription>
                {statusChanged && (
                  <div className="mt-2 text-amber-500 flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4" />
                    <span>{t("warning_status")}</span>
                  </div>
                )}
              </div>
              <FormControl>
                <Switch
                  checked={field.value}
                  onCheckedChange={(checked) => {
                    field.onChange(checked);
                    setStatusChanged(true);
                  }}
                />
              </FormControl>
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            {/* Left Column */}
            <FormField
              control={form.control}
              name="legacyMoldNumber"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("legacy_mold_number")}</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="Enter legacy mold number" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="moldNumber"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("mold_number_label")}</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="F1xxxx"
                      disabled={true}
                      className="bg-muted"
                    />
                  </FormControl>
                  <FormDescription>
                    {mode === "create" || mode === "duplicate"
                      ? t("mold_number_description_create")
                      : t("mold_number_description_edit")}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="technology"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("entity_technology")}</FormLabel>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full justify-between"
                      >
                        <span>{field.value || t("technology_placeholder")}</span>
                        <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-[var(--radix-dropdown-menu-trigger-width)]">
                      {technologies.map((tech) => (
                        <DropdownMenuItem
                          key={tech.id}
                          onSelect={() => field.onChange(tech.name)}
                          className="flex items-center justify-between"
                        >
                          {tech.name}
                          {field.value === tech.name && (
                            <Check className="h-4 w-4 ml-2" />
                          )}
                        </DropdownMenuItem>
                      ))}
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onSelect={(e) => {
                          e.preventDefault();
                          onAddTechnology();
                        }}
                        className="text-primary flex items-center"
                      >
                        <Plus className="h-4 w-4 mr-2" /> {t("new_purpose")}
                      </DropdownMenuItem>
                      {field.value && (
                        <DropdownMenuItem
                          onSelect={(e) => {
                            e.preventDefault();
                            onDeleteTechnology(field.value);
                            field.onChange("");
                          }}
                          className="text-destructive flex items-center"
                        >
                          <Trash className="h-4 w-4 mr-2" />{" "}
                          {t("delete_purpose")}
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="alloy"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("entity_alloy")}</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    value={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder={t("alloy_placeholder")} />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {alloys.map((alloy) => (
                        <SelectItem key={alloy.id} value={alloy.name}>
                          {alloy.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="moldSize"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Mold Size</FormLabel>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="outline"
                        className="w-full justify-between"
                      >
                        <span>{field.value || "Größe auswählen"}</span>
                        <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-[var(--radix-dropdown-menu-trigger-width)]">
                      {moldSizes.map((size) => (
                        <DropdownMenuItem
                          key={size.id}
                          onSelect={() => field.onChange(size.name)}
                          className="flex items-center justify-between"
                        >
                          {size.name}
                          {field.value === size.name && (
                            <Check className="h-4 w-4 ml-2" />
                          )}
                        </DropdownMenuItem>
                      ))}
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onSelect={(e) => {
                          e.preventDefault();
                          onAddMoldSize();
                        }}
                        className="text-primary flex items-center"
                      >
                        <Plus className="h-4 w-4 mr-2" /> {t("add_size")}
                      </DropdownMenuItem>
                      {field.value && (
                        <DropdownMenuItem
                          onSelect={(e) => {
                            e.preventDefault();
                            onDeleteMoldSize(field.value);
                            field.onChange("");
                          }}
                          className="text-destructive flex items-center"
                        >
                          <Trash className="h-4 w-4 mr-2" /> {t("delete_size")}
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="space-y-6">
            {/* Right Column */}
            <FormField
              control={form.control}
              name="warehouseLocation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("warehouse_location_label")}</FormLabel>
                  <div className="flex gap-2">
                    <FormControl>
                      <Input
                        {...field}
                        placeholder="Select warehouse location"
                        readOnly
                        onClick={onOpenLocationDialog}
                        className="cursor-pointer"
                      />
                    </FormControl>
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={onScanBarcode}
                      title={t("scan_barcode_title")}
                    >
                      <Barcode className="h-4 w-4" />
                    </Button>
                  </div>
                  <FormDescription>
                    {t("warehouse_location_description")}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="numberOfArticles"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("number_of_articles_label")}</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      value={field.value}
                      disabled
                      className="bg-muted cursor-not-allowed"
                    />
                  </FormControl>
                  <FormDescription>
                    {t("number_of_articles_description")}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Date Picker Fields */}
            <DatePickerField
              control={form.control}
              name="startDate"
              label={t("start_date_label")}
            />

            <DatePickerField
              control={form.control}
              name="endDate"
              label={t("end_date_label")}
            />

            {/* Image Uploader */}
            <ImageUploader control={form.control} name="imageUrl" />
          </div>
        </div>

        {/* Tag Selector */}
        <TagSelector control={form.control} name="tags" tags={tags} />
      </form>
    </Form>
  );
}
