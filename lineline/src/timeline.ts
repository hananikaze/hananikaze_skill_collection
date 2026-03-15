import crypto from 'node:crypto';
import type { Timeline, TimelineEntry } from './types.js';

export function createTimeline(name: string, endless: boolean, tags?: string[], metadata?: Record<string, any>): Timeline {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(), kind: 'timeline', name, status: 'active',
    endless, entries: [], tags, metadata, createdAt: now, updatedAt: now,
  };
}

export function addEntry(tl: Timeline, event: string, data?: Record<string, any>): TimelineEntry {
  const entry: TimelineEntry = { id: crypto.randomUUID(), ts: new Date().toISOString(), event, data };
  tl.entries.push(entry);
  tl.updatedAt = new Date().toISOString();
  return entry;
}

export function removeEntry(tl: Timeline, entryId: string): TimelineEntry {
  const idx = tl.entries.findIndex(e => e.id === entryId);
  if (idx === -1) throw new Error(`Entry ${entryId} not found`);
  const [removed] = tl.entries.splice(idx, 1);
  tl.updatedAt = new Date().toISOString();
  return removed;
}
