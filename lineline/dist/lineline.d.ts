import type { Line, Timeline, Pipeline, TimelineEntry, PipelineStage, PipelineTemplate, CreateTimelineConfig, CreatePipelineConfig, LineEvent, EventCallback } from './types.js';
export declare class Lineline {
    private store;
    private bus;
    private templates;
    constructor(options?: {
        dataDir?: string;
    });
    private loadBuiltinTemplates;
    on(event: LineEvent | '*', callback: EventCallback): () => void;
    create(config: CreateTimelineConfig | CreatePipelineConfig): Timeline | Pipeline;
    get(id: string): Line | undefined;
    list(filter?: {
        kind?: string;
        status?: string;
        tags?: string[];
    }): Line[];
    delete(id: string): void;
    private setStatus;
    pause(id: string): void;
    resume(id: string): void;
    archive(id: string): void;
    addEntry(timelineId: string, event: string, data?: Record<string, any>): TimelineEntry;
    removeEntry(timelineId: string, entryId: string): void;
    advanceStage(pipelineId: string): PipelineStage;
    completeStage(pipelineId: string, stageId?: string): void;
    skipStage(pipelineId: string, stageId?: string): void;
    addStage(pipelineId: string, stage: {
        name: string;
        after?: string;
    }): PipelineStage;
    removeStage(pipelineId: string, stageId: string): void;
    registerTemplate(name: string, template: PipelineTemplate): void;
    createFromTemplate(templateName: string, name: string): Pipeline;
    listTemplates(): PipelineTemplate[];
}
