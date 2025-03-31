"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
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
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { ArticleStatus } from "@/types/mold/article";
import useAppTranslation from "@/hooks/useTranslationWrapper";

/**
 * Schema for article form validation
 */
export const articleFormSchema = z
  .object({
    oldArticleNumber: z.string().optional(),
    newArticleNumber: z.string().optional(),
    description: z.string().optional(),
    frequency: z.coerce.number().int().min(1, "Frequency must be at least 1"),
    status: z.nativeEnum(ArticleStatus),
  })
  .refine((data) => data.oldArticleNumber || data.newArticleNumber, {
    message: "Either old or new article number must be provided",
    path: ["oldArticleNumber"],
  });

/**
 * Type for the article form values
 */
export type ArticleFormValues = z.infer<typeof articleFormSchema>;

/**
 * Props for the ArticleFormDialog component
 */
interface ArticleFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: ArticleFormValues) => void;
  defaultValues?: ArticleFormValues;
}

/**
 * Dialog for adding or editing an article
 */
export function ArticleFormDialog({
  open,
  onOpenChange,
  onSubmit,
  defaultValues,
}: ArticleFormDialogProps) {
  const { t } = useAppTranslation("mold");

  // Initialize article form
  const form = useForm<ArticleFormValues>({
    resolver: zodResolver(articleFormSchema),
    defaultValues: defaultValues || {
      oldArticleNumber: "",
      newArticleNumber: "",
      description: "",
      frequency: 1,
      status: ArticleStatus.ACTIVE,
    },
  });

  const handleSubmit = (data: ArticleFormValues) => {
    onSubmit(data);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("article_form_title")}</DialogTitle>
          <DialogDescription>{t("article_form_description")}</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-4 py-4"
          >
            <FormField
              control={form.control}
              name="oldArticleNumber"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("old_article_number")}</FormLabel>
                  <FormControl>
                    <Input
                      placeholder={t("old_article_placeholder")}
                      {...field}
                      readOnly
                      className="bg-muted cursor-not-allowed"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="newArticleNumber"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("new_article_number")}</FormLabel>
                  <FormControl>
                    <Input
                      placeholder={t("new_article_placeholder")}
                      {...field}
                      readOnly
                      className="bg-muted cursor-not-allowed"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("article_description")}</FormLabel>
                  <FormControl>
                    <Input
                      placeholder={t("article_description_placeholder")}
                      {...field}
                      readOnly
                      className="bg-muted cursor-not-allowed"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="frequency"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("frequency")}</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min="1"
                      placeholder={t("frequency_placeholder")}
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    {t("frequency_description")}
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("status")}</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    value={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder={t("select_status")} />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value={ArticleStatus.ACTIVE}>
                        {t("status_active")}
                      </SelectItem>
                      <SelectItem value={ArticleStatus.INACTIVE}>
                        {t("status_inactive")}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter className="pt-4">
              <Button
                variant="outline"
                type="button"
                onClick={() => onOpenChange(false)}
              >
                {t("cancel_button")}
              </Button>
              <Button type="submit">{t("add_article_button")}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
