"use client";

import type React from "react";

import { useState } from "react";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ImageIcon, Upload } from "lucide-react";
import type { Control } from "react-hook-form";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface ImageUploaderProps {
  control: Control<any>;
  name: string;
}

export function ImageUploader({ control, name }: ImageUploaderProps) {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);

  const { t } = useAppTranslation("mold");

  const handleImageUpload = (
    e: React.ChangeEvent<HTMLInputElement>,
    onChange: (value: string) => void
  ) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      onChange("pending-upload");
    }
  };

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{t("mold_image")}</FormLabel>
          <FormControl>
            <div className="border rounded-md p-4 flex flex-col items-center justify-center gap-4">
              {imagePreview ? (
                <div className="relative w-full h-40">
                  <img
                    src={imagePreview || "/placeholder.svg"}
                    alt="Mold preview"
                    className="w-full h-full object-contain"
                  />
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    className="absolute top-2 right-2"
                    onClick={() => {
                      setImagePreview(null);
                      setImageFile(null);
                      field.onChange("");
                    }}
                  >
                    {t("remove")}
                  </Button>
                </div>
              ) : (
                <div className="w-full h-40 border-2 border-dashed rounded-md flex flex-col items-center justify-center text-muted-foreground">
                  <ImageIcon className="h-10 w-10 mb-2" />
                  <p>{t("no_image_uploaded")}</p>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Input
                  type="file"
                  accept="image/*"
                  id="image-upload"
                  className="hidden"
                  onChange={(e) => handleImageUpload(e, field.onChange)}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    document.getElementById("image-upload")?.click();
                  }}
                  className="flex items-center gap-2"
                >
                  <Upload className="h-4 w-4" />
                  {t("upload_image")}
                </Button>
              </div>
            </div>
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
