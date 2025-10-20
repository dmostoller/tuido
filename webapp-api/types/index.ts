// Re-export Zod-inferred types from schemas
export type {
  Subtask,
  Priority,
  Task,
  Project,
  Note,
  SyncData,
} from "@/lib/schemas";

// User data structure stored in Redis
export interface UserData {
  email: string;
  name?: string;
  image?: string;
  apiToken: string;
  createdAt: string;
  lastSync?: string;
}

// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Sync status response
export interface SyncStatus {
  lastSync?: string;
  syncCount?: number;
  dataSize?: number;
}

// Token regeneration response
export interface TokenResponse {
  apiToken: string;
  message: string;
}
