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
  
  