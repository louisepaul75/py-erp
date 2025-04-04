import type {
  SystemIntegrationData,
  SyncWorkflow,
  SyncJob,
  SyncJobStatus,
  WorkflowLogRow,
  TriggerWorkflowPayload,
} from "@/types/settings/api";

// --- Base API Configuration ---
// TODO: Replace with your actual API base URL if different
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

// Helper function for API requests (replace with your project's actual API client if available)
async function apiFetch<T>(url: string, options: RequestInit = {}): Promise<T> {
  const defaultOptions: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      // TODO: Add authentication headers (e.g., Authorization: `Bearer ${token}`)
      // TODO: Add CSRF token header if using Django sessions/CSRF protection
    },
  };

  const mergedOptions: RequestInit = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, mergedOptions);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }
      console.error("API Error:", response.status, errorData);
      throw new Error(
        errorData?.detail ||
          errorData?.error ||
          errorData?.message ||
          `HTTP error ${response.status}`,
      );
    }

    // Handle responses with no content (e.g., 204)
    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  } catch (error) {
    console.error("Fetch failed:", error);
    // Re-throw the error so components can handle it (e.g., show error messages)
    throw error;
  }
}

// --- API Functions ---

/**
 * Fetches the combined system integration data (connections and their workflows).
 */
export async function fetchSystemIntegrationData(): Promise<SystemIntegrationData> {
  return apiFetch<SystemIntegrationData>("/sync/system-integrations/");
}

/**
 * Updates the enabled status of an external connection.
 * Returns the updated integration data.
 */
export async function updateConnectionStatus(
  connectionName: string,
  enabled: boolean,
): Promise<SystemIntegrationData> {
  return apiFetch<SystemIntegrationData>(
    `/external-api/connections/${connectionName}/`,
    {
      method: "POST",
      body: JSON.stringify({ enabled }),
    },
  );
}

/**
 * Fetches the most recent job runs for a specific workflow.
 * Maps SyncJob data to WorkflowLogRow format for easier display.
 */
export async function fetchWorkflowLogs(
  workflowSlug: string,
): Promise<WorkflowLogRow[]> {
  const jobs = await apiFetch<SyncJob[]>(
    `/sync/workflows/${workflowSlug}/recent-jobs/`,
  );

  // Map SyncJob[] to WorkflowLogRow[]
  return jobs.map(mapSyncJobToLogRow);
}

/**
 * Triggers a new run for a specific workflow.
 */
export async function triggerWorkflowRun(
  workflowSlug: string,
  payload: TriggerWorkflowPayload,
): Promise<SyncJob> {
  return apiFetch<SyncJob>(`/sync/workflows/${workflowSlug}/trigger/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// --- Helper Functions ---

/**
 * Maps a SyncJob object from the backend to a simplified WorkflowLogRow for display.
 */
function mapSyncJobToLogRow(job: SyncJob): WorkflowLogRow {
  const levelMap: Record<SyncJobStatus, WorkflowLogRow["level"]> = {
    PENDING: "info",
    STARTED: "info",
    SUCCESS: "success",
    FAILURE: "error",
    RETRY: "warning",
  };

  let message = `Job ${job.status.toLowerCase()}`;
  if (job.status === "SUCCESS") {
    message = "Workflow run completed successfully";
  } else if (job.status === "FAILURE") {
    message = "Workflow run failed";
    // Optionally parse log_output for a more specific error message
    // Example: const errorLine = job.log_output.split('\n').find(line => line.toLowerCase().includes('error'));
    // if (errorLine) message = errorLine;
  }

  return {
    id: job.task_id || job.id,
    timestamp: job.completed_at || job.created_at, // Prefer completed time
    level: levelMap[job.status] || "info",
    message: message,
    details: job.log_output,
  };
}
