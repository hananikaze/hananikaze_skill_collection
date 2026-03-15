export interface Line {
    id: string;
    kind: 'timeline' | 'pipeline';
    name: string;
    status: 'active' | 'paused' | 'archived' | 'done';
    tags?: string[];
    createdAt: string;
    updatedAt: string;
    metadata?: Record<string, any>;
}
export interface Timeline extends Line {
    kind: 'timeline';
    endless: boolean;
    entries: TimelineEntry[];
}
export interface TimelineEntry {
    id: string;
    ts: string;
    event: string;
    data?: Record<string, any>;
}
export interface Pipeline extends Line {
    kind: 'pipeline';
    template?: string;
    currentStageId: string;
    stages: PipelineStage[];
}
export interface PipelineStage {
    id: string;
    name: string;
    status: 'pending' | 'active' | 'done' | 'skipped';
    enteredAt?: string;
    completedAt?: string;
    data?: Record<string, any>;
}
export interface PipelineTemplate {
    name: string;
    description?: string;
    stages: {
        name: string;
        data?: Record<string, any>;
    }[];
}
export type LineEvent = 'line:created' | 'line:deleted' | 'line:statusChanged' | 'timeline:entryAdded' | 'timeline:entryRemoved' | 'pipeline:stageAdded' | 'pipeline:stageRemoved' | 'pipeline:stageActivated' | 'pipeline:stageCompleted' | 'pipeline:stageSkipped' | 'pipeline:completed' | 'line:metadataChanged' | 'line:tagged';
export type EventCallback = (event: LineEvent, data: {
    line: Line;
    [key: string]: any;
}) => void | Promise<void>;
export interface CreateTimelineConfig {
    kind: 'timeline';
    name: string;
    endless?: boolean;
    tags?: string[];
    metadata?: Record<string, any>;
}
export interface CreatePipelineConfig {
    kind: 'pipeline';
    name: string;
    stages: {
        name: string;
        data?: Record<string, any>;
    }[];
    template?: string;
    tags?: string[];
    metadata?: Record<string, any>;
}
