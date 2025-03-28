"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useCurrencyHistory } from "@/hooks/use-currency-history";
import type { TimeRange } from "@/types/settings/currency-history";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import type { Currency } from "@/types/settings/currency";
import useAppTranslation from "@/hooks/useTranslationWrapper";

interface CurrencyHistoryChartProps {
  currency: Currency | null;
}

export default function CurrencyHistoryChart({
  currency,
}: CurrencyHistoryChartProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>("month");

  const { t } = useAppTranslation("settings_currency");

  const { data, isLoading } = useCurrencyHistory(
    currency?.id,
    currency?.code,
    timeRange,
    currency?.realTimeRate
  );

  if (!currency) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("historical_exchange_rates")}</CardTitle>
          <CardDescription>{t("select_currency_for_history")}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);

    switch (timeRange) {
      case "day":
        return date.toLocaleTimeString("de-DE", {
          hour: "2-digit",
          minute: "2-digit",
        });
      case "week":
        return date.toLocaleDateString("de-DE", { weekday: "short" });
      case "month":
        return date.toLocaleDateString("de-DE", { day: "2-digit" });
      case "quarter":
        return date.toLocaleDateString("de-DE", {
          day: "2-digit",
          month: "2-digit",
        });
      case "year":
        return date.toLocaleDateString("de-DE", { month: "short" });
      default:
        return date.toLocaleDateString("de-DE");
    }
  };

  const formatTooltipDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: timeRange === "day" ? "2-digit" : undefined,
      minute: timeRange === "day" ? "2-digit" : undefined,
    });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-md shadow-md p-2 text-sm">
          <p className="font-medium">
            {formatTooltipDate(payload[0].payload.date)}
          </p>
          <p className="text-primary">
            {t("rate")}: {payload[0].value.toFixed(4)} EUR
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <CardTitle>
              {t("historical_exchange_rates")}: {currency.name} ({currency.code})
            </CardTitle>
            <CardDescription>
              {t("exchange_rate_to_euro")} (EUR)
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant={timeRange === "day" ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange("day")}
            >
              {t("day")}
            </Button>
            <Button
              variant={timeRange === "week" ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange("week")}
            >
              {t("week")}
            </Button>
            <Button
              variant={timeRange === "month" ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange("month")}
            >
              {t("month")}
            </Button>
            <Button
              variant={timeRange === "quarter" ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange("quarter")}
            >
              {t("quarter")}
            </Button>
            <Button
              variant={timeRange === "year" ? "default" : "outline"}
              size="sm"
              onClick={() => setTimeRange("year")}
            >
              {t("year")}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="w-full h-[300px] flex items-center justify-center">
            <Skeleton className="w-full h-full" />
          </div>
        ) : (
          <Tabs defaultValue="chart">
            <TabsList className="mb-4">
              <TabsTrigger value="chart">{t("chart")}</TabsTrigger>
              <TabsTrigger value="table">{t("table")}</TabsTrigger>
            </TabsList>
            <TabsContent value="chart">
              <div className="w-full h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={data?.history}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={formatDate}
                      minTickGap={30}
                    />
                    <YAxis
                      domain={["auto", "auto"]}
                      tickFormatter={(value) => value.toFixed(4)}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="rate"
                      name={`${currency.code}/EUR Kurs`}
                      stroke="#3b82f6"
                      activeDot={{ r: 8 }}
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </TabsContent>
            <TabsContent value="table">
              <div className="border rounded-md max-h-[300px] overflow-auto">
                <table className="w-full">
                  <thead className="sticky top-0 bg-background">
                    <tr className="border-b">
                      <th className="text-left p-2">{t("date")}</th>
                      <th className="text-right p-2">{t("rate")} (EUR)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data?.history.map((point, index) => (
                      <tr key={index} className="border-b">
                        <td className="p-2">{formatTooltipDate(point.date)}</td>
                        <td className="text-right p-2">
                          {point.rate.toFixed(4)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
}
