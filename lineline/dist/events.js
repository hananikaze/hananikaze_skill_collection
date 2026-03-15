export class EventBus {
    listeners = new Map();
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
        return () => { this.listeners.get(event)?.delete(callback); };
    }
    async emit(event, data) {
        const specific = this.listeners.get(event);
        const wildcard = this.listeners.get('*');
        if (specific)
            for (const cb of specific)
                await cb(event, data);
        if (wildcard)
            for (const cb of wildcard)
                await cb(event, data);
    }
}
