import { z } from "zod";

/**
 * Zod schemas matching the TUI Python data models
 * These schemas validate sync data from the desktop todo-tui app
 */

// Subtask within a task
export const SubtaskSchema = z.object({
  id: z.string(),
  title: z.string(),
  completed: z.boolean(),
});

// Priority levels matching TUI
export const PrioritySchema = z.enum(["high", "medium", "low", "none"]);

// Task/Todo item with full TUI features
export const TaskSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().default(""),
  notes: z.string().default(""),
  completed: z.boolean(),
  created_at: z.string(), // ISO timestamp
  completed_at: z.string().nullable().optional(),
  subtasks: z.array(SubtaskSchema).default([]),
  project_id: z.string().default(""),
  priority: PrioritySchema.default("none"),
});

// Project that contains tasks
export const ProjectSchema = z.object({
  id: z.string(),
  name: z.string(),
  created_at: z.string(), // ISO timestamp
});

// Note in the scratchpad
export const NoteSchema = z.object({
  id: z.string(),
  title: z.string().default("Untitled Note"),
  content: z.string().default(""),
  created_at: z.string(), // ISO timestamp
  updated_at: z.string(), // ISO timestamp
});

// Sync data structure from TUI
export const SyncDataSchema = z.object({
  timestamp: z.string(), // ISO timestamp
  projects: z.array(ProjectSchema),
  tasks: z.record(z.string(), z.array(TaskSchema)), // Map of project_id -> tasks[]
  notes: z.array(NoteSchema),
});

// Type exports inferred from Zod schemas
export type Subtask = z.infer<typeof SubtaskSchema>;
export type Priority = z.infer<typeof PrioritySchema>;
export type Task = z.infer<typeof TaskSchema>;
export type Project = z.infer<typeof ProjectSchema>;
export type Note = z.infer<typeof NoteSchema>;
export type SyncData = z.infer<typeof SyncDataSchema>;
