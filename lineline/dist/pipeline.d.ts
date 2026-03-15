import type { Pipeline, PipelineStage } from './types.js';
export declare function createPipeline(name: string, stages: {
    name: string;
    data?: Record<string, any>;
}[], template?: string, tags?: string[], metadata?: Record<string, any>): Pipeline;
export declare function completeStage(pl: Pipeline, stageId?: string): PipelineStage;
export declare function skipStage(pl: Pipeline, stageId?: string): PipelineStage;
export declare function advanceStage(pl: Pipeline): PipelineStage;
export declare function addStage(pl: Pipeline, name: string, after?: string): PipelineStage;
export declare function removeStage(pl: Pipeline, stageId: string): PipelineStage;
export declare function isComplete(pl: Pipeline): boolean;
