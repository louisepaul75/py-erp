// Types for System Integration Settings

// Represents a single data synchronization workflow defined in the backend
export interface SyncWorkflow {
  id: number; // Assuming integer ID from Django model
  name: string;
  slug: string;
  description: string | null;
  external_connection_name: string | null; // Link to connection key
  command_template: string;
  parameters: Record<string, any>; // Definition of expected parameters (e.g., {"debug": "boolean"})
  environment_variables: Record<string, string>;
  last_job_status: SyncJobStatus | null; // Get status from the last job
  last_run_time: string | null; // ISO 8601 timestamp
}

// Represents the status of a SyncJob
export type SyncJobStatus =
  | "PENDING"
  | "STARTED"
  | "SUCCESS"
  | "FAILURE"
  | "RETRY";

// Represents a single execution instance of a SyncWorkflow
export interface SyncJob {
  id: number; // Assuming integer ID
  workflow: number; // ID of the related SyncWorkflow
  workflow_name: string;
  task_id: string | null; // Celery task ID
  status: SyncJobStatus;
  parameters: Record<string, any>; // Parameters used for this run
  created_at: string; // ISO 8601 timestamp
  started_at: string | null; // ISO 8601 timestamp
  completed_at: string | null; // ISO 8601 timestamp
  log_output: string;
}

// Structure for the combined data fetched for the system integrations view
export type SystemIntegrationData = Record<
  string, // Connection name (e.g., 'legacy_erp', 'images_cms')
  {
    enabled: boolean; // Whether the connection is enabled
    workflows: SyncWorkflow[]; // List of workflows associated with this connection
  }
>;

// Type for simplified log entries derived from SyncJob for display
export interface WorkflowLogRow {
  id: string | number; // Use job id or task id
  timestamp: string; // completed_at or created_at
  level: "info" | "warning" | "error" | "success"; // Map from job status
  message: string; // Summary message based on status/log
  details?: string; // Can use job.log_output
}

// Structure for triggering a workflow run
export interface TriggerWorkflowPayload {
  parameters: Record<string, any>;
}

export interface ApiEndpoint {
    id: string
    name: string
    url: string
    status: "active" | "error" | "pending"
    lastSync: string
  }
  
  export interface LogEntry {
    id: string
    timestamp: string
    level: "info" | "warning" | "error" | "success"
    message: string
    details?: any
  }
  
  export interface ChangeEntry {
    id: string
    timestamp: string
    type: "added" | "removed" | "modified"
    entity: string
    description: string
    details?: any
  }
  
  export interface Automation {
    id: string
    name: string
    description: string
    status: "running" | "stopped" | "scheduled" | "failed"
    schedule: string
    lastRun: string
  }
  
  