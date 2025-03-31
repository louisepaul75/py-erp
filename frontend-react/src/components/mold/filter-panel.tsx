"use client";

import type React from "react";

import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import type { Technology } from "@/types/mold/technology";
import type { Alloy } from "@/types/mold/alloy";
import type { Tag } from "@/types/mold/tag";
import type { MoldSize } from "@/types/mold/mold-size";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Props for the FilterPanel component
 */
interface FilterPanelProps {
  technologies: Technology[];
  alloys: Alloy[];
  tags: Tag[];
  moldSizes: MoldSize[];
  filters: {
    technology: string[];
    alloy: string[];
    tags: string[];
    moldSize: string[];
    isActive: boolean | null | "mixed";
  };
  setFilters: React.Dispatch<
    React.SetStateAction<{
      technology: string[];
      alloy: string[];
      tags: string[];
      moldSize: string[];
      isActive: boolean | null | "mixed";
    }>
  >;
}

/**
 * FilterPanel component provides filtering options for the mold table
 * Uses checkboxes to allow multiple selections
 */
export default function FilterPanel({
  technologies,
  alloys,
  tags,
  moldSizes,
  filters,
  setFilters,
}: FilterPanelProps) {
  /**
   * Handle technology checkbox change
   */
  const handleTechnologyChange = (techName: string, checked: boolean) => {
    if (checked) {
      setFilters({
        ...filters,
        technology: [...filters.technology, techName],
      });
    } else {
      setFilters({
        ...filters,
        technology: filters.technology.filter((t) => t !== techName),
      });
    }
  };

  const { t } = useAppTranslation("mold");

  /**
   * Handle alloy checkbox change
   */
  const handleAlloyChange = (alloyName: string, checked: boolean) => {
    if (checked) {
      setFilters({
        ...filters,
        alloy: [...filters.alloy, alloyName],
      });
    } else {
      setFilters({
        ...filters,
        alloy: filters.alloy.filter((a) => a !== alloyName),
      });
    }
  };

  /**
   * Handle tag checkbox change
   */
  const handleTagChange = (tagName: string, checked: boolean) => {
    if (checked) {
      setFilters({
        ...filters,
        tags: [...filters.tags, tagName],
      });
    } else {
      setFilters({
        ...filters,
        tags: filters.tags.filter((t) => t !== tagName),
      });
    }
  };

  /**
   * Handle mold size checkbox change
   */
  const handleMoldSizeChange = (sizeName: string, checked: boolean) => {
    if (checked) {
      setFilters({
        ...filters,
        moldSize: [...filters.moldSize, sizeName],
      });
    } else {
      setFilters({
        ...filters,
        moldSize: filters.moldSize.filter((s) => s !== sizeName),
      });
    }
  };

  /**
   * Handle activity status change
   */
  const handleActivityChange = (value: string) => {
    setFilters({
      ...filters,
      isActive:
        value === "all"
          ? null
          : value === "active"
          ? true
          : value === "inactive"
          ? false
          : "mixed",
    });
  };

  return (
    <div className="space-y-6">
      {/* Technology Filters */}
      <div className="space-y-3">
        <h3 className="font-medium text-sm">{t("technology_heading")}</h3>
        <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
          {technologies.map((tech) => (
            <div key={tech.id} className="flex items-center space-x-2">
              <Checkbox
                id={`tech-${tech.id}`}
                checked={filters.technology.includes(tech.name)}
                onCheckedChange={(checked) =>
                  handleTechnologyChange(tech.name, checked === true)
                }
              />
              <Label
                htmlFor={`tech-${tech.id}`}
                className="text-sm font-normal cursor-pointer"
              >
                {tech.name}
              </Label>
            </div>
          ))}
          {technologies.length === 0 && (
            <p className="text-sm text-muted-foreground">
              {t("no_technologies")}
            </p>
          )}
        </div>
      </div>

      {/* Alloy Filters */}
      <div className="space-y-3">
        <h3 className="font-medium text-sm">{t("alloy_heading")}</h3>
        <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
          {alloys.map((alloy) => (
            <div key={alloy.id} className="flex items-center space-x-2">
              <Checkbox
                id={`alloy-${alloy.id}`}
                checked={filters.alloy.includes(alloy.name)}
                onCheckedChange={(checked) =>
                  handleAlloyChange(alloy.name, checked === true)
                }
              />
              <Label
                htmlFor={`alloy-${alloy.id}`}
                className="text-sm font-normal cursor-pointer"
              >
                {alloy.name}
              </Label>
            </div>
          ))}
          {alloys.length === 0 && (
            <p className="text-sm text-muted-foreground">{t("no_alloys")}</p>
          )}
        </div>
      </div>

      {/* Mold Size Filters */}
      <div className="space-y-3">
        <h3 className="font-medium text-sm">{t("mold_size_heading")}</h3>
        <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
          {moldSizes.map((size) => (
            <div key={size.id} className="flex items-center space-x-2">
              <Checkbox
                id={`size-${size.id}`}
                checked={filters.moldSize.includes(size.name)}
                onCheckedChange={(checked) =>
                  handleMoldSizeChange(size.name, checked === true)
                }
              />
              <Label
                htmlFor={`size-${size.id}`}
                className="text-sm font-normal cursor-pointer"
              >
                {size.name}
              </Label>
            </div>
          ))}
          {moldSizes.length === 0 && (
            <p className="text-sm text-muted-foreground">
              {t("no_mold_sizes")}
            </p>
          )}
        </div>
      </div>

      {/* Tags Filters */}
      <div className="space-y-3">
        <h3 className="font-medium text-sm">{t("tags_heading")}</h3>
        <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
          {tags.map((tag) => (
            <div key={tag.id} className="flex items-center space-x-2">
              <Checkbox
                id={`tag-${tag.id}`}
                checked={filters.tags.includes(tag.name)}
                onCheckedChange={(checked) =>
                  handleTagChange(tag.name, checked === true)
                }
              />
              <Label
                htmlFor={`tag-${tag.id}`}
                className="text-sm font-normal cursor-pointer"
              >
                {tag.name}
              </Label>
            </div>
          ))}
          {tags.length === 0 && (
            <p className="text-sm text-muted-foreground">{t("no_tags")}</p>
          )}
        </div>
      </div>

      {/* Activity Status Filters */}
      <div className="space-y-3">
        <h3 className="font-medium text-sm">{t("activity_status_heading")}</h3>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="status-all"
              checked={filters.isActive === null}
              onCheckedChange={(checked) => {
                if (checked) handleActivityChange("all");
              }}
            />
            <Label
              htmlFor="status-all"
              className="text-sm font-normal cursor-pointer"
            >
              {t("activity_status_all")}
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="status-active"
              checked={filters.isActive === true}
              onCheckedChange={(checked) => {
                if (checked) handleActivityChange("active");
              }}
            />
            <Label
              htmlFor="status-active"
              className="text-sm font-normal cursor-pointer"
            >
              {t("activity_status_active")}
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="status-inactive"
              checked={filters.isActive === false}
              onCheckedChange={(checked) => {
                if (checked) handleActivityChange("inactive");
              }}
            />
            <Label
              htmlFor="status-inactive"
              className="text-sm font-normal cursor-pointer"
            >
              {t("activity_status_inactive")}
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="status-mixed"
              checked={filters.isActive === "mixed"}
              onCheckedChange={(checked) => {
                if (checked) handleActivityChange("mixed");
              }}
            />
            <Label
              htmlFor="status-mixed"
              className="text-sm font-normal cursor-pointer"
            >
              {t("activity_status_mixed")}
            </Label>
          </div>
        </div>
      </div>
    </div>
  );
}
