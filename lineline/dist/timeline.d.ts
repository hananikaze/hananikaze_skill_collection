import type { Timeline, TimelineEntry } from './types.js';
export declare function createTimeline(name: string, endless: boolean, tags?: string[], metadata?: Record<string, any>): Timeline;
export declare function addEntry(tl: Timeline, event: string, data?: Record<string, any>): TimelineEntry;
export declare function removeEntry(tl: Timeline, entryId: string): TimelineEntry;
