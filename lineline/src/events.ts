import type { LineEvent, EventCallback } from './types.js';

export class EventBus {
  private listeners = new Map<string, Set<EventCallback>>();

  on(event: LineEvent | '*', callback: EventCallback): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
    return () => { this.listeners.get(event)?.delete(callback); };
  }

  async emit(event: LineEvent, data: { line: any; [key: string]: any }): Promise<void> {
    const specific = this.listeners.get(event);
    const wildcard = this.listeners.get('*');
    if (specific) for (const cb of specific) await cb(event, data);
    if (wildcard) for (const cb of wildcard) await cb(event, data);
  }
}
