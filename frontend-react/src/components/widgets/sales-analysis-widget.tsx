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
import { Eye, EyeOff, ChevronLeft, ChevronRight, CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import axios from 'axios';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { instance as api } from "@/lib/api";

interface SalesData {
  date: string;
  daily: number;
  cumulative: number;
}

interface MonthInfo {
  start_date: string;
  end_date: string;
  name: string;
  month: number;
  year: number;
}

interface NavigationInfo {
  prev_month: number;
  prev_year: number;
  next_month: number;
  next_year: number;
  is_current: boolean;
}

interface SalesAnalysisData {
  selected_month: MonthInfo;
  navigation: NavigationInfo;
  data: SalesData[];
}

export function SalesAnalysisWidget() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SalesAnalysisData | null>(null);
  const [showValues, setShowValues] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());

  const fetchSalesData = async (month: number, year: number) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await api.get('api/v1/sales/records/monthly_analysis/', {
        searchParams: { month, year }
      }).json();
      
      setData(response);
    } catch (err: any) {
      console.error('Error fetching sales data:', err);
      const errorMessage = err.response?.data?.error || 'Failed to load sales data. Please try again later.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSalesData(selectedMonth, selectedYear);
  }, [selectedMonth, selectedYear]);

  const toggleValueVisibility = () => {
    setShowValues(prev => !prev);
  };

  const handlePreviousMonth = () => {
    if (data?.navigation) {
      setSelectedMonth(data.navigation.prev_month);
      setSelectedYear(data.navigation.prev_year);
    }
  };

  const handleNextMonth = () => {
    if (data?.navigation) {
      setSelectedMonth(data.navigation.next_month);
      setSelectedYear(data.navigation.next_year);
    }
  };

  const goToCurrentMonth = () => {
    const currentDate = new Date();
    setSelectedMonth(currentDate.getMonth() + 1);
    setSelectedYear(currentDate.getFullYear());
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

  // Generate months for selector
  const months = [
    { value: 1, label: 'Januar' },
    { value: 2, label: 'Februar' },
    { value: 3, label: 'März' },
    { value: 4, label: 'April' },
    { value: 5, label: 'Mai' },
    { value: 6, label: 'Juni' },
    { value: 7, label: 'Juli' },
    { value: 8, label: 'August' },
    { value: 9, label: 'September' },
    { value: 10, label: 'Oktober' },
    { value: 11, label: 'November' },
    { value: 12, label: 'Dezember' },
  ];

  // Generate years (current year and 5 years back)
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

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
          <div className="flex items-center justify-between mt-1">
            <div className="flex items-center space-x-1">
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={handlePreviousMonth}
                disabled={isLoading}
                className="h-7 w-7"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <div className="flex items-center space-x-1">
                <Select
                  value={selectedMonth.toString()}
                  onValueChange={(value) => setSelectedMonth(parseInt(value))}
                  disabled={isLoading}
                >
                  <SelectTrigger className="h-7 px-2 text-xs w-[85px]">
                    <SelectValue placeholder="Monat" />
                  </SelectTrigger>
                  <SelectContent>
                    {months.map((month) => (
                      <SelectItem key={month.value} value={month.value.toString()}>
                        {month.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Select
                  value={selectedYear.toString()}
                  onValueChange={(value) => setSelectedYear(parseInt(value))}
                  disabled={isLoading}
                >
                  <SelectTrigger className="h-7 px-2 text-xs w-[70px]">
                    <SelectValue placeholder="Jahr" />
                  </SelectTrigger>
                  <SelectContent>
                    {years.map((year) => (
                      <SelectItem key={year} value={year.toString()}>
                        {year}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={handleNextMonth}
                disabled={isLoading || (data?.navigation && data.navigation.is_current)}
                className="h-7 w-7"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
              
              {!data?.navigation?.is_current && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={goToCurrentMonth}
                  disabled={isLoading}
                  className="h-7 text-xs"
                >
                  <CalendarIcon className="mr-1 h-3 w-3" />
                  Aktuell
                </Button>
              )}
            </div>
          </div>
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
          ) : data && data.data.length > 0 && data.data.some(item => item.daily > 0 || item.cumulative > 0) ? (
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
            <div className="w-full h-[200px] flex flex-col items-center justify-center text-muted-foreground">
              <p>Keine Daten für {data?.selected_month.name || ""} verfügbar</p>
              {selectedMonth === new Date().getMonth() + 1 && selectedYear === new Date().getFullYear() && (
                <p className="text-xs mt-2">Möglicherweise befinden wir uns am Anfang des Monats</p>
              )}
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