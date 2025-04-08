import type {
  SystemIntegrationData,
  SyncWorkflow,
  SyncJob,
  SyncJobStatus,
  WorkflowLogRow,
  TriggerWorkflowPayload,
} from "@/types/settings/api";
import { API_URL } from "@/lib/config";
import { authService } from "@/lib/auth/authService";

// --- Helper Function --- 

export async function createSyncWorkflow(workflow: Omit<SyncWorkflow, "id" | "last_job_status" | "last_run_time">): Promise<SyncWorkflow> {
  const token = await authService.getToken();
  const endpoint = `/api/sync/system-integrations/workflows/`; 

  const response = await fetch(API_URL + endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(workflow),
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(`Failed to create workflow: ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as SyncWorkflow;
}

function mapSyncJobToLogRow(job: SyncJob): WorkflowLogRow {
  const levelMap: Record<SyncJobStatus, WorkflowLogRow["level"]> = {
    PENDING: "info",
    STARTED: "info",
    SUCCESS: "success",
    FAILURE: "error",
    RETRY: "warning",
  };

  const timestampStr = job.completed_at || job.started_at || job.created_at;
  const timestamp = timestampStr ? new Date(timestampStr).toLocaleString() : new Date().toLocaleString(); // Format timestamp
  const level = levelMap[job.status] || "info";
  // Add Job ID to the message
  let message = `Job #${job.id} for '${job.workflow_name}' ${job.status.toLowerCase()}`; 
  if (job.status === "FAILURE") {
      message += job.log_output ? `: ${job.log_output.split('\n')[0]}` : '';
  }

  return {
    id: job.id,
    timestamp: timestamp, // Use formatted timestamp
    level: level,
    message: message,
    details: job.log_output || undefined,
  };
}

// --- API Functions (Using Standard Pattern) ---

/**
 * Fetches the combined system integration data (connections and their workflows).
 */

const mockSystemIntegrationData: SystemIntegrationData = {
  legacy_erp: {
    enabled: true,
    workflows: [
      {
        id: 1,
        name: "Customer Sync",
        slug: "customer_sync",
        description: "Synchronizes customer data from the legacy ERP.",
        external_connection_name: "legacy_erp",
        command_template: "sync_customer_data",
        parameters: { debug: "boolean", force_update: "boolean" },
        environment_variables: {},
        last_job_status: "STARTED",
        last_run_time: "2025-04-05T12:00:00Z",
      },
      {
        id: 2,
        name: "Employee Sync",
        slug: "employee_sync",
        description: "Synchronizes employee data from the legacy ERP.",
        external_connection_name: "legacy_erp",
        command_template: "sync_employee_data",
        parameters: { debug: "boolean", force_update: "boolean" },
        environment_variables: {},
        last_job_status: "SUCCESS",
        last_run_time: "2025-04-05T12:00:00Z",
      },
    ],
  },

  images_cms: {
    enabled: true,
    workflows: [
      {
        id: 3,
        name: "Product Images Sync",
        slug: "product_images_sync",
        description: "Synchronizes product images from the external CMS.",
        external_connection_name: "images_cms",
        command_template: "sync_product_images",
        parameters: { debug: "boolean", force: "boolean", download: "boolean" },
        environment_variables: {},
        last_job_status: null,
        last_run_time: null,
      },
    ],
  },

  currency_api: {
    enabled: true,
    workflows: [
      {
        id: 4,
        name: "FX Sync",
        slug: "fx_sync",
        description: "Synchronizes currency exchange rates from the Frankfurter API.",
        external_connection_name: "currency_api",
        command_template: "sync_currency_rates",
        parameters: { debug: "boolean", force_update: "boolean" },
        environment_variables: {
          API_BASE_URL: "https://api.frankfurter.app",
        },
        last_job_status: null,
        last_run_time: null,
      },
    ],
  },
};

export async function fetchSystemIntegrationData(
  signal?: AbortSignal,
): Promise<SystemIntegrationData> {
  const token = await authService.getToken();
  // Ensure the endpoint starts with /api/
  const endpoint = `/api/sync/system-integrations/`; 

  const response = await fetch(API_URL + endpoint, {
    headers: {
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    signal: signal,
  });
  
  console.log("RESPONSE", response)
  return mockSystemIntegrationData
}

/**
 * Updates the enabled status of an external connection.
 * Returns the updated integration data.
 */
export async function updateConnectionStatus(
  connectionName: string,
  enabled: boolean,
): Promise<SystemIntegrationData> {
  const token = await authService.getToken();
  // Ensure the endpoint starts with /api/
  const endpoint = `/api/external-api/connections/${connectionName}/`; 

  const response = await fetch(API_URL + endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify({ enabled }),
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(
      `Failed to update connection status: ${response.status} ${response.statusText}`,
    );
  }
  return (await response.json()) as SystemIntegrationData;
}

/**
 * Fetches the most recent job runs for a specific workflow.
 * Maps SyncJob data to WorkflowLogRow format for easier display.
 */
export async function fetchWorkflowLogs(
  workflowSlug: string,
): Promise<WorkflowLogRow[]> {
  const token = await authService.getToken();
  // Ensure the endpoint starts with /api/
  const endpoint = `/api/sync/workflows/${workflowSlug}/recent-jobs/`; 

  const response = await fetch(API_URL + endpoint, {
    headers: {
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(
      `Failed to fetch workflow logs: ${response.status} ${response.statusText}`,
    );
  }
  const jobs = (await response.json()) as SyncJob[];
  return jobs.map(mapSyncJobToLogRow);
}

/**
 * Triggers a new run for a specific workflow.
 */
export async function triggerWorkflowRun(
  workflowSlug: string,
  payload: TriggerWorkflowPayload,
): Promise<SyncJob> {
  const token = await authService.getToken();
  // Ensure the endpoint starts with /api/
  const endpoint = `/api/sync/workflows/${workflowSlug}/trigger/`; 

  const response = await fetch(API_URL + endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(
      `Failed to trigger workflow run: ${response.status} ${response.statusText}`,
    );
  }
  return (await response.json()) as SyncJob;
}
