"use client";

import { useDeleteCurrency } from "@/hooks/use-currencies";
import type { Currency } from "@/types/settings/currency";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "@/hooks/use-toast";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface DeleteCurrencyDialogProps {
  currency: Currency | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function DeleteCurrencyDialog({
  currency,
  open,
  onOpenChange,
}: DeleteCurrencyDialogProps) {
  const deleteCurrency = useDeleteCurrency();
  const { t } = useAppTranslation("settings_currency");
  const handleDelete = async () => {
    if (!currency) return;

    try {
      await deleteCurrency.mutateAsync(currency.id);
      toast({
        title: t("currency_deleted"),
        description: `${currency.name} (${currency.code}) ${t("was_successfully_deleted")}`,
      });
      onOpenChange(false);
    } catch (error) {
      toast({
        title:  t("error"),
        description: t("delete_currency_error"),
        variant: "destructive",
      });
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{t("delete_currency")}</AlertDialogTitle>
          <AlertDialogDescription>
          {t("delete_currency_description")} {" "}
            <strong>
              {currency?.name} ({currency?.code})
            </strong>{" "}
            {t("delete_confirm")}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{t("cancel")}</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {deleteCurrency.isPending ? t("deleting") : t("delete")}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
