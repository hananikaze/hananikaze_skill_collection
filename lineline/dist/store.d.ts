import type { Line } from './types.js';
export declare class Store {
    private dir;
    constructor(dataDir: string);
    save(line: Line): void;
    load(id: string): Line | undefined;
    remove(id: string): boolean;
    loadAll(): Line[];
}
