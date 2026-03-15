import crypto from 'node:crypto';
import type { Pipeline, PipelineStage } from './types.js';

export function createPipeline(name: string, stages: { name: string; data?: Record<string, any> }[], template?: string, tags?: string[], metadata?: Record<string, any>): Pipeline {
  if (stages.length === 0) throw new Error('Pipeline must have at least one stage');
  const now = new Date().toISOString();
  const pipelineStages: PipelineStage[] = stages.map((s, i) => ({
    id: crypto.randomUUID(), name: s.name, status: i === 0 ? 'active' as const : 'pending' as const,
    enteredAt: i === 0 ? now : undefined, data: s.data,
  }));
  return {
    id: crypto.randomUUID(), kind: 'pipeline', name, status: 'active',
    template, currentStageId: pipelineStages[0].id, stages: pipelineStages,
    tags, metadata, createdAt: now, updatedAt: now,
  };
}

export function completeStage(pl: Pipeline, stageId?: string): PipelineStage {
  const stage = stageId ? pl.stages.find(s => s.id === stageId) : pl.stages.find(s => s.id === pl.currentStageId);
  if (!stage) throw new Error('Stage not found');
  if (stage.status === 'done') throw new Error('Stage already completed');
  if (stage.status === 'skipped') throw new Error('Stage was skipped');
  stage.status = 'done';
  stage.completedAt = new Date().toISOString();
  pl.updatedAt = new Date().toISOString();
  return stage;
}

export function skipStage(pl: Pipeline, stageId?: string): PipelineStage {
  const stage = stageId ? pl.stages.find(s => s.id === stageId) : pl.stages.find(s => s.id === pl.currentStageId);
  if (!stage) throw new Error('Stage not found');
  if (stage.status === 'done') throw new Error('Stage already completed');
  stage.status = 'skipped';
  stage.completedAt = new Date().toISOString();
  pl.updatedAt = new Date().toISOString();
  return stage;
}

export function advanceStage(pl: Pipeline): PipelineStage {
  const currentIdx = pl.stages.findIndex(s => s.id === pl.currentStageId);
  if (currentIdx === -1) throw new Error('Current stage not found');
  const current = pl.stages[currentIdx];
  if (current.status === 'active') {
    current.status = 'done';
    current.completedAt = new Date().toISOString();
  }
  const nextIdx = currentIdx + 1;
  if (nextIdx >= pl.stages.length) throw new Error('No more stages — pipeline is complete');
  const next = pl.stages[nextIdx];
  next.status = 'active';
  next.enteredAt = new Date().toISOString();
  pl.currentStageId = next.id;
  pl.updatedAt = new Date().toISOString();
  return next;
}

export function addStage(pl: Pipeline, name: string, after?: string): PipelineStage {
  const stage: PipelineStage = { id: crypto.randomUUID(), name, status: 'pending' };
  if (after) {
    const idx = pl.stages.findIndex(s => s.id === after);
    if (idx === -1) throw new Error(`Stage ${after} not found`);
    pl.stages.splice(idx + 1, 0, stage);
  } else {
    pl.stages.push(stage);
  }
  pl.updatedAt = new Date().toISOString();
  return stage;
}

export function removeStage(pl: Pipeline, stageId: string): PipelineStage {
  const idx = pl.stages.findIndex(s => s.id === stageId);
  if (idx === -1) throw new Error(`Stage ${stageId} not found`);
  if (pl.currentStageId === stageId) throw new Error('Cannot remove active stage');
  const [removed] = pl.stages.splice(idx, 1);
  pl.updatedAt = new Date().toISOString();
  return removed;
}

export function isComplete(pl: Pipeline): boolean {
  return pl.stages.every(s => s.status === 'done' || s.status === 'skipped');
}
