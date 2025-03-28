"use client";

import { useState } from "react";
import { useCurrencyContext } from "./currency-provider";
import { useCurrencies } from "@/hooks/use-currencies";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  PlusCircle,
  Search,
  RefreshCw,
  Edit,
  Trash2,
  LineChart,
} from "lucide-react";
import CurrencyForm from "./currency-form";
import DeleteCurrencyDialog from "./delete-currency-dialog";
import CurrencyHistoryChart from "./currency-history-chart";
import type { Currency } from "@/types/settings/currency";
import useAppTranslation from "@/hooks/useTranslationWrapper";

export default function CurrencyList() {
  const { data: currencies = [], isLoading, refetch } = useCurrencies();
  const { setSelectedCurrency, setIsAddingCurrency } = useCurrencyContext();
  const [searchTerm, setSearchTerm] = useState("");
  const [currencyToDelete, setCurrencyToDelete] = useState<Currency | null>(
    null
  );
  const [selectedHistoryCurrency, setSelectedHistoryCurrency] =
    useState<Currency | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const { t } = useAppTranslation("settings_currency");

  const filteredCurrencies = currencies.filter(
    (currency) =>
      currency.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      currency.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddCurrency = () => {
    setSelectedCurrency(null);
    setIsAddingCurrency(true);
  };

  const handleEditCurrency = (currency: Currency) => {
    setSelectedCurrency(currency);
    setIsAddingCurrency(true);
  };

  const handleShowHistory = (currency: Currency) => {
    setSelectedHistoryCurrency(currency);
    setShowHistory(true);
  };

  return (
    <div className="space-y-4">
      <div className="bg-muted/50 p-3 rounded-md flex items-center text-sm">
        <div className="mr-2 rounded-full bg-primary/10 p-1">
          <RefreshCw className="h-4 w-4 text-primary" />
        </div>
        <p>
        {t("all_exchange_rates_refer_to_base_currency")}{" "}
          <strong>Euro (EUR)</strong>
        </p>
      </div>

      <div className="flex flex-col sm:flex-row justify-between gap-4">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={t("search_currency_placeholder")}
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={showHistory ? "outline" : "default"}
            onClick={() => setShowHistory(false)}
          >
            {t("currencies")}
          </Button>
          <Button
            variant={showHistory ? "default" : "outline"}
            onClick={() => setShowHistory(true)}
            disabled={!selectedHistoryCurrency}
          >
            <LineChart className="mr-2 h-4 w-4" />
            {t("trend_analysis")}
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => refetch()}
            disabled={isLoading}
            title={t("refresh")}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button onClick={handleAddCurrency}>
            <PlusCircle className="mr-2 h-4 w-4" />
            {t("add_new_currency")}
          </Button>
        </div>
      </div>

      {showHistory ? (
        <CurrencyHistoryChart currency={selectedHistoryCurrency} />
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">{t("code")}</TableHead>
                <TableHead>{t("currency_name")}</TableHead>
                <TableHead className="text-right">
                {t("real_time_rate")} (EUR)
                </TableHead>
                <TableHead className="text-right">
                {t("calculation_rate")} (EUR)
                </TableHead>
                <TableHead className="text-right">
                {t("last_updated")}
                </TableHead>
                <TableHead className="w-[140px] text-right">{t("actions")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center">
                  {t("loading_data")}
                  </TableCell>
                </TableRow>
              ) : filteredCurrencies.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center">
                    {t("no_currencies_found")}
                  </TableCell>
                </TableRow>
              ) : (
                filteredCurrencies.map((currency) => (
                  <TableRow key={currency.id}>
                    <TableCell className="font-medium">
                      {currency.code}
                    </TableCell>
                    <TableCell>{currency.name}</TableCell>
                    <TableCell className="text-right">
                      {currency.realTimeRate.toFixed(4)}
                    </TableCell>
                    <TableCell className="text-right">
                      {currency.calculationRate.toFixed(4)}
                    </TableCell>
                    <TableCell className="text-right">
                      {new Date(currency.lastUpdated).toLocaleString("de-DE", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleShowHistory(currency)}
                          title={t("trend_analysis")}
                        >
                          <LineChart className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEditCurrency(currency)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setCurrencyToDelete(currency)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      )}

      <CurrencyForm />
      <DeleteCurrencyDialog
        currency={currencyToDelete}
        open={!!currencyToDelete}
        onOpenChange={() => setCurrencyToDelete(null)}
      />
    </div>
  );
}
