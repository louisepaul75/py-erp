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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { instance as api } from "@/lib/api";

interface SalesData {
  date: string;
  daily: number | null;
  cumulative: number | null;
  cumulative_prev_year?: number | null;
  cumulative_avg_5_years?: number | null;
  year?: number;
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

// Define a type guard for MonthInfo
function isMonthInfo(period: any): period is MonthInfo {
  return period && typeof period === 'object' && 'month' in period && 'year' in period && 'name' in period;
}

// Define a type guard for Annual Navigation
function isAnnualNavigation(nav: any): nav is { prev_year: number; next_year: number; is_current: boolean } {
  return nav && typeof nav === 'object' && 'prev_year' in nav && 'next_year' in nav && 'is_current' in nav;
}

// Define a type guard for Monthly Navigation
function isMonthlyNavigation(nav: any): nav is NavigationInfo {
    return nav && typeof nav === 'object' && 'prev_month' in nav && 'next_month' in nav && 'prev_year' in nav && 'next_year' in nav && 'is_current' in nav;
}

interface SalesAnalysisData {
  // Use a more generic type for the period, check structure with type guard
  selected_period: MonthInfo | { year: number }; 
  // Use a more generic type for navigation, check structure with type guard
  navigation: NavigationInfo | { prev_year: number; next_year: number; is_current: boolean }; 
  data: SalesData[];
}

type AnalysisMode = "monthly" | "annual";

export function SalesAnalysisWidget() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SalesAnalysisData | null>(null);
  const [showValues, setShowValues] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState<number>(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [mode, setMode] = useState<AnalysisMode>("monthly");

  const fetchSalesData = async (currentMode: AnalysisMode, month: number, year: number) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const endpointUrl = currentMode === 'monthly' 
        ? 'sales/records/monthly_analysis/' 
        : 'sales/records/annual_analysis/';
      
      console.log(`Fetching from ${API_URL}/${endpointUrl}`);
      
      const searchParams: Record<string, number> = {};
      if (currentMode === 'monthly') {
        searchParams.month = month;
        searchParams.year = year;
      } else {
        searchParams.year = year;
      }

      const response: SalesAnalysisData = await api.get(endpointUrl, {
        searchParams: searchParams
      }).json();
      
      setData(response);
      
      // Safely update state based on the actual response structure
      if (response.selected_period) {
        if (isMonthInfo(response.selected_period)) {
          // It's monthly data, update both month and year
          setSelectedMonth(response.selected_period.month);
          setSelectedYear(response.selected_period.year);
        } else if ('year' in response.selected_period) {
          // Assume it's annual data (or at least has a year), update year only
          setSelectedYear(response.selected_period.year);
        }
      }

    } catch (err: any) {
      console.error('Error fetching sales data:', err);
      const errorMessage = err.response?.data?.error || 'Failed to load sales data. Please try again later.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSalesData(mode, selectedMonth, selectedYear);
  }, [selectedMonth, selectedYear, mode]);

  const toggleValueVisibility = () => {
    setShowValues(prev => !prev);
  };

  const handlePrevious = () => {
    if (!data?.navigation) return;
    
    // Use type guards for navigation
    if (mode === 'monthly' && isMonthlyNavigation(data.navigation)) {
      setSelectedMonth(data.navigation.prev_month);
      setSelectedYear(data.navigation.prev_year);
    } else if (mode === 'annual' && isAnnualNavigation(data.navigation)) {
      setSelectedYear(data.navigation.prev_year);
    } else if (mode === 'annual' && isMonthlyNavigation(data.navigation)) { 
      // Fallback if annual API still returns monthly nav structure
      setSelectedYear(data.navigation.prev_year);
    }
  };

  const handleNext = () => {
    if (!data?.navigation) return;
    
    // Use type guards for navigation
    if (mode === 'monthly' && isMonthlyNavigation(data.navigation)) {
      if (data.navigation.is_current) return; 
      setSelectedMonth(data.navigation.next_month);
      setSelectedYear(data.navigation.next_year);
    } else if (mode === 'annual' && isAnnualNavigation(data.navigation)) {
      if (data.navigation.is_current) return; 
      setSelectedYear(data.navigation.next_year);
    } else if (mode === 'annual' && isMonthlyNavigation(data.navigation)) { 
      // Fallback if annual API still returns monthly nav structure
       if (data.navigation.is_current) return; 
      setSelectedYear(data.navigation.next_year);
    }
  };

  const goToCurrent = () => {
    const currentDate = new Date();
    setMode('monthly');
    setSelectedMonth(currentDate.getMonth() + 1);
    setSelectedYear(currentDate.getFullYear());
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    if (mode === 'annual') {
      return date.toLocaleDateString('de-DE', { month: 'short' });
    }
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
      const data = payload[0].payload as SalesData;
      const currentYearLabel = data.year || selectedYear;
      const prevYearLabel = currentYearLabel - 1;
      const fiveYearAvgLabel = `${currentYearLabel-5}-${currentYearLabel-1}`;

      return (
        <div className="bg-popover shadow-md rounded-md p-2 border border-border text-popover-foreground text-xs">
          <p className="font-medium mb-1">{new Date(data.date).toLocaleDateString('de-DE')}</p>
          {data.daily !== null && <p>Tagesumsatz: {formatCurrency(data.daily)}</p>}
          {data.cumulative !== null && 
            <p className="flex items-center">
              <span className="inline-block w-2 h-2 rounded-full mr-1.5" style={{ backgroundColor: 'var(--primary)' }}></span>
              Kumuliert ({currentYearLabel}): {formatCurrency(data.cumulative)}
            </p>
          }
          {data.cumulative_prev_year !== null && data.cumulative_prev_year !== undefined && 
            <p className="flex items-center">
              <span className="inline-block w-2 h-2 rounded-full mr-1.5" style={{ backgroundColor: 'var(--muted-foreground)' }}></span>
              Kumuliert ({prevYearLabel}): {formatCurrency(data.cumulative_prev_year)}
            </p>
          }
          {data.cumulative_avg_5_years !== null && data.cumulative_avg_5_years !== undefined && 
            <p className="flex items-center">
               <span className="inline-block w-2 h-2 rounded-full mr-1.5" style={{ backgroundColor: 'var(--muted-foreground)' }}></span>
              5J. Ø Kumuliert: {formatCurrency(data.cumulative_avg_5_years)}
            </p>
          }
        </div>
      );
    }
    return null;
  };

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

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  return (
    <div className="w-full h-full">
      <Card className="w-full h-full">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <CardTitle>Verkaufsanalyse ({mode === 'monthly' ? 'Monatlich' : 'Jährlich'})</CardTitle>
            <div className="flex items-center gap-2">
              <ToggleGroup 
                type="single" 
                defaultValue="monthly" 
                value={mode} 
                onValueChange={(value: AnalysisMode) => {
                  if (value) setMode(value);
                }}
                className="h-8"
                disabled={isLoading}
              >
                <ToggleGroupItem value="monthly" aria-label="Monatlich" className="h-full px-2 text-xs">Monat</ToggleGroupItem>
                <ToggleGroupItem value="annual" aria-label="Jährlich" className="h-full px-2 text-xs">Jahr</ToggleGroupItem>
              </ToggleGroup>
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={toggleValueVisibility}
                className="h-8 w-8"
              >
                {showValues ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
              </Button>
            </div>
          </div>
          <div className="flex items-center justify-between mt-1">
            <div className="flex items-center space-x-1">
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={handlePrevious}
                disabled={isLoading}
                className="h-7 w-7"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <div className="flex items-center space-x-1">
                {mode === 'monthly' && (
                  <Select
                    value={selectedMonth.toString()}
                    onValueChange={(value: string) => setSelectedMonth(parseInt(value))}
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
                )}
                
                <Select
                  value={selectedYear.toString()}
                  onValueChange={(value: string) => setSelectedYear(parseInt(value))}
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
                onClick={handleNext}
                disabled={isLoading || (data?.navigation && data.navigation.is_current)}
                className="h-7 w-7"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
              
              {!data?.navigation?.is_current && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={goToCurrent}
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
          ) : data && data.data.length > 0 && data.data.some(item => (item.daily ?? 0) > 0 || (item.cumulative ?? 0) > 0) ? (
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
                    name={`Kumuliert (${selectedYear})`}
                    stroke="var(--primary)"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 6, fill: 'var(--primary)' }}
                    connectNulls={true}
                  />
                  <Line
                    type="monotone"
                    dataKey="cumulative_prev_year"
                    name={`Kumuliert (${selectedYear - 1})`}
                    stroke="var(--muted-foreground)"
                    strokeWidth={1.5}
                    dot={false}
                    activeDot={{ r: 5, fill: 'var(--muted-foreground)' }}
                    connectNulls={true}
                  />
                  <Line
                    type="monotone"
                    dataKey="cumulative_avg_5_years"
                    name="5J. Ø Kumuliert"
                    stroke="var(--muted-foreground)"
                    strokeWidth={1.5}
                    strokeDasharray="8 4"
                    dot={false}
                    activeDot={{ r: 5, fill: 'var(--muted-foreground)' }}
                    connectNulls={true}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="w-full h-[200px] flex flex-col items-center justify-center text-muted-foreground">
              <p>Keine Daten für {
                mode === 'monthly'
                  ? (data?.selected_period && isMonthInfo(data.selected_period) ? data.selected_period.name : `Monat ${selectedMonth}/${selectedYear}`)
                  : (data?.selected_period && 'year' in data.selected_period ? data.selected_period.year : selectedYear)
              } verfügbar</p>
              {/* Adjust condition for helper text if needed */}
              {mode === 'monthly' && data?.navigation && isMonthlyNavigation(data.navigation) && data.navigation.is_current && (
                <p className="text-xs mt-2">Möglicherweise befinden wir uns am Anfang des Monats</p>
              )}
               {mode === 'annual' && data?.navigation && (isAnnualNavigation(data.navigation) || isMonthlyNavigation(data.navigation)) && data.navigation.is_current && (
                <p className="text-xs mt-2">Möglicherweise befinden wir uns am Anfang des Jahres</p>
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