import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ProductionPage() {
  return (
    <div className="container mx-auto p-6 h-full overflow-auto">
      <Card>
        <CardHeader>
          <CardTitle>Production Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This page is under construction. The production dashboard will be available soon.
          </p>
        </CardContent>
      </Card>
    </div>
  );
} 