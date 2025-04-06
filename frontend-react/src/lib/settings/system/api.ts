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
export async function fetchSystemIntegrationData(
  signal?: AbortSignal,
): Promise<SystemIntegrationData> {
  const token = await authService.getToken();
  const endpoint = `/sync/system-integrations/`;

  const response = await fetch(API_URL + endpoint, {
    headers: {
      Accept: "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    },
    signal: signal,
  });

  if (!response.ok) {
    console.error("API Error:", response.status, await response.text());
    throw new Error(
      `Failed to fetch system integrations: ${response.status} ${response.statusText}`,
    );
  }
  return (await response.json()) as SystemIntegrationData;
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
  const endpoint = `/external-api/connections/${connectionName}/`;

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
  const endpoint = `/sync/workflows/${workflowSlug}/recent-jobs/`;

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
  const endpoint = `/sync/workflows/${workflowSlug}/trigger/`;

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
