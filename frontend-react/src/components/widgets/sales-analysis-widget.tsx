"use client";

import { useState, useEffect } from "react";
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
import { Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import axios from 'axios';

interface SalesData {
  date: string;
  daily: number;
  cumulative: number;
}

interface MonthInfo {
  start_date: string;
  end_date: string;
  name: string;
}

interface SalesAnalysisData {
  current_month: MonthInfo;
  data: SalesData[];
}

export function SalesAnalysisWidget() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SalesAnalysisData | null>(null);
  const [showValues, setShowValues] = useState(false);

  useEffect(() => {
    const fetchSalesData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await axios.get('/api/business/sales/records/monthly_analysis/');
        setData(response.data);
      } catch (err) {
        console.error('Error fetching sales data:', err);
        setError('Failed to load sales data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSalesData();
  }, []);

  const toggleValueVisibility = () => {
    setShowValues(prev => !prev);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.getDate().toString();
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2
    }).format(value);
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-popover shadow-md rounded-md p-2 border border-border text-popover-foreground">
          <p className="font-medium">{new Date(data.date).toLocaleDateString('de-DE')}</p>
          <p>Tagesumsatz: {formatCurrency(data.daily)}</p>
          <p>Kumuliert: {formatCurrency(data.cumulative)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-full">
      <Card className="w-full h-full">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle>Verkaufsanalyse</CardTitle>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={toggleValueVisibility}
              className="h-8 w-8"
            >
              {showValues ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
            </Button>
          </div>
          {data && (
            <p className="text-sm text-muted-foreground">{data.current_month.name}</p>
          )}
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="w-full h-[200px] flex items-center justify-center">
              <Skeleton className="w-full h-full" />
            </div>
          ) : error ? (
            <div className="w-full h-[200px] flex items-center justify-center text-muted-foreground">
              <p>{error}</p>
            </div>
          ) : data && data.data.length > 0 ? (
            <div className="w-full h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={data.data}
                  margin={{ top: 5, right: 5, left: showValues ? 40 : 5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" strokeOpacity={0.5} />
                  <XAxis
                    dataKey="date"
                    tickFormatter={formatDate}
                    stroke="var(--muted-foreground)"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    domain={[0, 'auto']}
                    tickFormatter={(value) => showValues ? formatCurrency(value) : ''}
                    stroke="var(--muted-foreground)"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    width={showValues ? 80 : 0}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: "12px", color: 'var(--muted-foreground)' }} />
                  <Line
                    type="monotone"
                    dataKey="cumulative"
                    name="Kumulierter Umsatz"
                    stroke="var(--primary)"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 6, fill: 'var(--primary)' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="w-full h-[200px] flex items-center justify-center text-muted-foreground">
              <p>Keine Daten für diesen Monat verfügbar</p>
            </div>
          )}
        </CardContent>
        <CardFooter className="pt-1 text-xs text-muted-foreground">
          <p>Nur Rechnungen (INVOICE) werden berücksichtigt</p>
        </CardFooter>
      </Card>
    </div>
  );
}

export default SalesAnalysisWidget; 