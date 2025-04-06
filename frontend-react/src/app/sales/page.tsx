import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import SalesAnalysisWidget from "@/components/widgets/sales-analysis-widget";
import SalesRecordsTable from "@/components/widgets/sales-records-table";

export default function SalesPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Sales Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <SalesAnalysisWidget />
        </CardContent>
      </Card>

      <SalesRecordsTable />
    </div>
  );
} 