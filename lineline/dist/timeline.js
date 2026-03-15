import crypto from 'node:crypto';
export function createTimeline(name, endless, tags, metadata) {
    const now = new Date().toISOString();
    return {
        id: crypto.randomUUID(), kind: 'timeline', name, status: 'active',
        endless, entries: [], tags, metadata, createdAt: now, updatedAt: now,
    };
}
export function addEntry(tl, event, data) {
    const entry = { id: crypto.randomUUID(), ts: new Date().toISOString(), event, data };
    tl.entries.push(entry);
    tl.updatedAt = new Date().toISOString();
    return entry;
}
export function removeEntry(tl, entryId) {
    const idx = tl.entries.findIndex(e => e.id === entryId);
    if (idx === -1)
        throw new Error(`Entry ${entryId} not found`);
    const [removed] = tl.entries.splice(idx, 1);
    tl.updatedAt = new Date().toISOString();
    return removed;
}
