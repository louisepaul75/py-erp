import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileText, Users, Receipt, Package } from 'lucide-react'; // Assuming lucide-react for icons

export default function SalesDashboardPage() {
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
            {/* Document Status Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Dokumentenstatus</CardTitle>
                <p className="text-sm text-muted-foreground">Verteilung der Dokumente nach Status</p>
              </CardHeader>
              <CardContent>
                {/* Placeholder for Pie Chart */}
                <div className="flex items-center justify-center h-60 bg-secondary rounded-md">
                  <p className="text-muted-foreground">Pie Chart Placeholder</p>
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
                {/* Placeholder for Activity List */}
                <div className="space-y-4">
                  <p className="text-muted-foreground">Activity List Placeholder</p>
                  {/* Example item structure */}
                  {/* <div className="flex items-center">
                    <div className="ml-4 space-y-1">
                      <p className="text-sm font-medium leading-none">Acme Corporation placed a new order</p>
                      <p className="text-sm text-muted-foreground">Order #ORD-2023-001 for €1,488.68</p>
                      <p className="text-xs text-muted-foreground">15.06.2023</p>
                    </div>
                  </div> */}
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
              <div className="flex items-center justify-center h-60 bg-secondary rounded-md">
                <p className="text-muted-foreground">Bar Chart Placeholder</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Placeholder Content for other tabs */}
        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <CardTitle>Dokumente</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Inhalt für Dokumente...</p>
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