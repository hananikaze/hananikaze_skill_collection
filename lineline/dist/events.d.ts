import type { LineEvent, EventCallback } from './types.js';
export declare class EventBus {
    private listeners;
    on(event: LineEvent | '*', callback: EventCallback): () => void;
    emit(event: LineEvent, data: {
        line: any;
        [key: string]: any;
    }): Promise<void>;
}
