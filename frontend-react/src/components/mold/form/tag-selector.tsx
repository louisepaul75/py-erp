"use client";

import { useState } from "react";
import {
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, Search, TagIcon, X } from "lucide-react";
import type { Control } from "react-hook-form";
import type { Tag } from "@/types/mold/tag";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface TagSelectorProps {
  control: Control<any>;
  name: string;
  tags: Tag[];
}

export function TagSelector({ control, name, tags = [] }: TagSelectorProps) {
  const [tagsOpen, setTagsOpen] = useState(false);
  const [tagSearchTerm, setTagSearchTerm] = useState("");

  const { t } = useAppTranslation("mold");

  // Filter tags based on search term
  const filteredTags = (tags || []).filter((tag) =>
    tag?.name?.toLowerCase().includes(tagSearchTerm.toLowerCase())
  );

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className="flex flex-col">
          <FormLabel>{t("settings_tab_tags")}</FormLabel>
          <FormDescription>{t("select_tags_description")}</FormDescription>

          {/* Selected Tags Display */}
          {field.value.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4 p-2 border rounded-md bg-muted/20">
              {field.value.map((tag: string) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="flex items-center gap-1 py-1.5 px-3"
                >
                  <TagIcon className="h-3.5 w-3.5 mr-1" />
                  {tag}
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-5 w-5 p-0 ml-1 rounded-full hover:bg-muted"
                    onClick={() => {
                      const newTags = field.value.filter(
                        (t: string) => t !== tag
                      );
                      field.onChange(newTags);
                    }}
                  >
                    <X className="h-3 w-3" />
                    <span className="sr-only">
                      {t("settings_tab_tags")} {tag}
                    </span>
                  </Button>
                </Badge>
              ))}
            </div>
          )}

          {/* Tag Selector Dropdown */}
          <DropdownMenu open={tagsOpen} onOpenChange={setTagsOpen}>
            <DropdownMenuTrigger asChild>
              <Button
                type="button"
                variant="outline"
                className="w-full justify-between"
              >
                <span className="flex items-center gap-2">
                  <TagIcon className="h-4 w-4 opacity-70" />
                  {t("select_tags")}
                </span>
                <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className="w-[var(--radix-dropdown-menu-trigger-width)] p-0"
              align="start"
            >
              <div className="p-2 border-b">
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <Input
                    type="text"
                    placeholder={t("search_tags_placeholder")}
                    value={tagSearchTerm}
                    onChange={(e) => setTagSearchTerm(e.target.value)}
                    className="h-8 border-none focus-visible:ring-0 focus-visible:ring-offset-0"
                  />
                </div>
              </div>

              <div className="max-h-[200px] overflow-y-auto p-2">
                {filteredTags.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-2 px-2">
                    {t("no_tags_found")}.
                  </p>
                ) : (
                  filteredTags.map((tag) => {
                    const isSelected = field.value.includes(tag.name);
                    return (
                      <div
                        key={tag.id}
                        className="flex items-center space-x-2 py-1.5 px-2 hover:bg-muted rounded-sm cursor-pointer"
                        onClick={(e) => {
                          e.preventDefault();
                          const newTags = isSelected
                            ? field.value.filter((t: string) => t !== tag.name)
                            : [...field.value, tag.name];
                          field.onChange(newTags);
                        }}
                      >
                        <Checkbox
                          id={`tag-${tag.id}`}
                          checked={isSelected}
                          onCheckedChange={(checked) => {
                            const newTags = checked
                              ? [...field.value, tag.name]
                              : field.value.filter(
                                  (t: string) => t !== tag.name
                                );
                            field.onChange(newTags);
                          }}
                          onClick={(e) => e.stopPropagation()}
                        />
                        <label
                          htmlFor={`tag-${tag.id}`}
                          className="text-sm cursor-pointer flex-1"
                        >
                          {tag.name}
                        </label>
                      </div>
                    );
                  })
                )}
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
