"use client"; // Make it a client component

import { useState, useEffect } from "react"; // Import hooks
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileText, Users, Receipt, Package } from 'lucide-react'; // Assuming lucide-react for icons
import { SalesAnalysisWidget } from "@/components/widgets/sales-analysis-widget";
import { instance as api } from "@/lib/api"; // Import API instance
import { Skeleton } from "@/components/ui/skeleton"; // Import Skeleton for loading
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"; // Import Alert for errors
import { format } from 'date-fns'; // For date formatting
import SalesRecordsTable from "@/components/widgets/sales-records-table";

// Basic interface for recent activity data
interface RecentActivity {
  id: number;
  record_number: string;
  record_date: string;
  customer?: { name: string }; // Assuming customer is nested
  total_amount: number;
  record_type: string;
  payment_status: string; // Add payment status here too for counting
}

// Interface for status counts
interface StatusCounts {
  PENDING: number;
  PAID: number;
  OVERDUE: number;
  CANCELLED: number;
  [key: string]: number; // Index signature for dynamic access
}

// Interface for summary counts
interface SummaryCounts {
  customers: number | null;
  documents: number | null; // Total sales records
  orders: number | null; // Specific type TBD
  invoices: number | null; // Specific type 'INVOICE'
}

export default function SalesDashboardPage() {
  // State for recent activities
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [isLoadingActivities, setIsLoadingActivities] = useState(true);
  const [errorActivities, setErrorActivities] = useState<string | null>(null);

  // State for document status counts
  const [statusCounts, setStatusCounts] = useState<StatusCounts | null>(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(true);
  const [errorStatus, setErrorStatus] = useState<string | null>(null);

  // State for summary counts
  const [summaryCounts, setSummaryCounts] = useState<SummaryCounts>({ customers: null, documents: null, orders: null, invoices: null });
  const [isLoadingSummary, setIsLoadingSummary] = useState(true);
  const [errorSummary, setErrorSummary] = useState<string | null>(null);

  // Fetch recent activities
  useEffect(() => {
    const fetchActivities = async () => {
      setIsLoadingActivities(true);
      setErrorActivities(null);
      try {
        // Fetch the 5 most recent sales records
        // Explicitly type the expected response structure if paginated
        const responseData = await api.get("v1/sales/records/?limit=5").json<{ results: RecentActivity[] } | RecentActivity[]>();

        // Check if it's paginated or a simple array
         if (responseData && 'results' in responseData && Array.isArray(responseData.results)) {
             setActivities(responseData.results);
         } else if (Array.isArray(responseData)) { // Handle non-paginated results (though limit implies pagination)
             setActivities(responseData);
         } else {
             console.error("Unexpected response structure for activities:", responseData);
             throw new Error("Received unexpected data structure for recent activities.");
         }
      } catch (err: any) {
        console.error("Error fetching recent activities:", err);
        let detail = "Failed to load recent activities.";
        // Attempt to get detail from Ky http errors
        if (err.response) {
            try {
                const errorBody = await err.response.json();
                detail = errorBody?.detail || JSON.stringify(errorBody) || detail;
            } catch (parseErr) {
                 detail = err.message || detail; // Fallback to general message
            }
        } else {
            detail = err.message || detail;
        }
        setErrorActivities(detail);
      } finally {
        setIsLoadingActivities(false);
      }
    };

    fetchActivities();
  }, []);

  // Fetch and calculate document status counts
  useEffect(() => {
    const fetchAndCountStatus = async () => {
      setIsLoadingStatus(true);
      setErrorStatus(null);
      try {
        // Fetch all sales records (potential performance issue if very large)
        // Assuming the API returns { results: [...] } or just [...] 
        const responseData = await api.get("v1/sales/records/").json<{ results: RecentActivity[] } | RecentActivity[]>();
        
        const records = (responseData && 'results' in responseData) ? responseData.results : responseData;
        
        if (!Array.isArray(records)) {
            console.error("Unexpected response structure for status counts:", records);
            throw new Error("Received unexpected data structure for status counts.");
        }

        // Initialize counts
        const counts: StatusCounts = { PENDING: 0, PAID: 0, OVERDUE: 0, CANCELLED: 0 };

        // Count records by payment_status
        records.forEach(record => {
          if (record.payment_status && counts.hasOwnProperty(record.payment_status)) {
            counts[record.payment_status]++;
          }
        });

        setStatusCounts(counts);
      } catch (err: any) {
        console.error("Error fetching or counting document status:", err);
         let detail = "Failed to load document status data.";
         if (err.response) {
             try {
                 const errorBody = await err.response.json();
                 detail = errorBody?.detail || JSON.stringify(errorBody) || detail;
             } catch (parseErr) {
                  detail = err.message || detail;
             }
         } else {
             detail = err.message || detail;
         }
        setErrorStatus(detail);
      } finally {
        setIsLoadingStatus(false);
      }
    };

    fetchAndCountStatus();
  }, []);

  // Fetch summary counts
  useEffect(() => {
    const fetchSummaryCounts = async () => {
      setIsLoadingSummary(true);
      setErrorSummary(null);
      try {
        // Fetch total customer count
        const customerRes = await api.get("v1/sales/customers/?limit=1").json<{ count: number }>();
        const customerCount = customerRes?.count ?? null;

        // Fetch total document (sales record) count
        const docRes = await api.get("v1/sales/records/?limit=1").json<{ count: number }>();
        const documentCount = docRes?.count ?? null;

        // Fetch invoice count
        const invoiceRes = await api.get("v1/sales/records/?record_type=INVOICE&limit=1").json<{ count: number }>();
        const invoiceCount = invoiceRes?.count ?? null;
        
        // Fetch order count (assuming ORDER_CONFIRMATION type - adjust if needed)
        const orderRes = await api.get("v1/sales/records/?record_type=ORDER_CONFIRMATION&limit=1").json<{ count: number }>();
        const orderCount = orderRes?.count ?? null;

        setSummaryCounts({
          customers: customerCount,
          documents: documentCount,
          invoices: invoiceCount,
          orders: orderCount
        });

      } catch (err: any) {
        console.error("Error fetching summary counts:", err);
         let detail = "Failed to load summary data.";
         if (err.response) {
             try {
                 const errorBody = await err.response.json();
                 detail = errorBody?.detail || JSON.stringify(errorBody) || detail;
             } catch (parseErr) {
                  detail = err.message || detail;
             }
         } else {
             detail = err.message || detail;
         }
        setErrorSummary(detail);
      } finally {
        setIsLoadingSummary(false);
      }
    };
    fetchSummaryCounts();
  }, []);

  // Helper to format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value);
  };

  // Helper to render summary count or skeleton/error
  const renderSummaryCount = (count: number | null) => {
    if (isLoadingSummary) return <Skeleton className="h-6 w-12 mt-1" />;
    if (errorSummary) return <span className="text-xs text-destructive">Error</span>; // Simple error indicator
    if (count === null) return <span className="text-muted-foreground">-</span>;
    return <div className="text-2xl font-bold">{count}</div>;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Willkommen in Ihrem Kunden- und Auftragsverwaltungssystem</p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Dokumente</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              Alle Dokumente verwalten
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Aufträge</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              Aufträge verwalten
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rechnungen</CardTitle>
            <Receipt className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              Rechnungen verwalten
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Kunden</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              Kundendaten verwalten
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs & Content Sections */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Übersicht</TabsTrigger>
          <TabsTrigger value="documents">Dokumente</TabsTrigger>
          <TabsTrigger value="customers">Kunden</TabsTrigger>
          <TabsTrigger value="top-customers">Top-Kunden</TabsTrigger>
        </TabsList>

        {/* Overview Tab Content */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Document Status Card */}
            <Card>
              <CardHeader>
                <CardTitle>Dokumentenstatus</CardTitle>
                <p className="text-sm text-muted-foreground">Verteilung der Dokumente nach Zahlungsstatus</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {isLoadingStatus ? (
                    <>
                      <Skeleton className="h-6 w-3/4" />
                      <Skeleton className="h-6 w-2/4" />
                      <Skeleton className="h-6 w-3/5" />
                      <Skeleton className="h-6 w-1/2" />
                    </>
                  ) : errorStatus ? (
                    <Alert variant="destructive">
                      <AlertTitle>Error</AlertTitle>
                      <AlertDescription>{errorStatus}</AlertDescription>
                    </Alert>
                  ) : statusCounts ? (
                    Object.entries(statusCounts).map(([status, count]) => (
                      <div key={status} className="flex justify-between items-center text-sm">
                        <span className="capitalize text-muted-foreground">{status.toLowerCase().replace('_', ' ')}</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">Keine Statusdaten verfügbar.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Recent Activities */}
            <Card>
              <CardHeader>
                <CardTitle>Aktuelle Aktivitäten</CardTitle>
                 <p className="text-sm text-muted-foreground">Die neuesten Kundenaktivitäten</p>
              </CardHeader>
              <CardContent>
                {/* Placeholder for Activity List - Replaced below */}
                <div className="space-y-4">
                  {isLoadingActivities ? (
                    <div className="space-y-3">
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-10 w-full" />
                      <Skeleton className="h-10 w-full" />
                    </div>
                  ) : errorActivities ? (
                    <Alert variant="destructive">
                      <AlertTitle>Error</AlertTitle>
                      <AlertDescription>{errorActivities}</AlertDescription>
                    </Alert>
                  ) : activities.length > 0 ? (
                    activities.map((activity) => (
                      <div key={activity.id} className="flex items-center border-b pb-2 mb-2 last:border-b-0 last:pb-0 last:mb-0">
                         {/* Basic activity item structure */}
                        <div className="ml-4 space-y-1 flex-grow">
                          <p className="text-sm font-medium leading-none">
                            {activity.record_type}: {activity.record_number}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {activity.customer?.name ?? 'Unknown Customer'} - {formatCurrency(activity.total_amount)}
                          </p>
                           <p className="text-xs text-muted-foreground">
                            {format(new Date(activity.record_date), 'dd.MM.yyyy')}
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                     <p className="text-sm text-muted-foreground">Keine aktuellen Aktivitäten gefunden.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sales Development Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Umsatzentwicklung</CardTitle>
              <p className="text-sm text-muted-foreground">Umsatz der letzten 6 Monate</p>
            </CardHeader>
            <CardContent>
              {/* Placeholder for Bar Chart */}
              {/* <div className="flex items-center justify-center h-60 bg-secondary rounded-md">
                <p className="text-muted-foreground">Bar Chart Placeholder</p>
              </div> */}
              {/* Use the actual widget */}
              <SalesAnalysisWidget />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Placeholder Content for other tabs */}
        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <CardTitle>Dokumente</CardTitle>
               {/* Optional: Add description or filter controls here later */}
            </CardHeader>
            <CardContent>
              {/* Replace placeholder with the table component */}
              {/* <p>Inhalt für Dokumente...</p> */}
              <SalesRecordsTable />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="customers">
           <Card>
            <CardHeader>
              <CardTitle>Kunden</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Inhalt für Kunden...</p>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="top-customers">
           <Card>
            <CardHeader>
              <CardTitle>Top-Kunden</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Inhalt für Top-Kunden...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 