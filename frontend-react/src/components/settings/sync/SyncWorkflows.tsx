import React, { useState, useEffect } from 'react';
import { instance as api } from '@/lib/api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";

interface Workflow {
  slug: string;
  name: string;
  description: string;
  parameters: { [key: string]: { type: string; flag: string; label: string } };
  // Add other fields as needed, e.g., last run status/time
}

// Define interface for the paginated API response
interface PaginatedWorkflowsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Workflow[];
}

const SyncWorkflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWorkflows = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await api.get('sync/workflows/').json<PaginatedWorkflowsResponse>();
        setWorkflows(response.results || []);
      } catch (error) {
        console.error('Failed to fetch workflows:', error);
        setError('Failed to load sync workflows. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchWorkflows();
  }, []); // Empty dependency array means this runs once on mount

  if (loading) {
    return <div>Loading workflows...</div>; // Replace with a proper spinner/skeleton loader later
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Data Synchronization Workflows</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Workflow Name</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Parameters</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {workflows.map((workflow) => (
              <TableRow key={workflow.slug}>
                <TableCell>{workflow.name}</TableCell>
                <TableCell>{workflow.description || '-'}</TableCell>
                <TableCell>
                  {/* Parameter inputs - Basic checkboxes for now */}
                  {Object.entries(workflow.parameters).map(([key, param]) => (
                    param.type === 'boolean' && (
                      <div key={key} className="flex items-center space-x-2 mb-1">
                        <Checkbox id={`${workflow.slug}-${key}`} />
                        <label
                          htmlFor={`${workflow.slug}-${key}`}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          {param.label || key}
                        </label>
                      </div>
                    )
                    // Add inputs for other parameter types here later
                  ))}
                </TableCell>
                <TableCell>
                  <Button variant="outline" size="sm" className="mr-2">Run</Button>
                  <Button variant="ghost" size="sm">Logs</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};

export default SyncWorkflows; 