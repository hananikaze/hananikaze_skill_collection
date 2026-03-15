import path from 'node:path';
import fs from 'node:fs';
import YAML from 'yaml';
import { EventBus } from './events.js';
import { Store } from './store.js';
import * as tl from './timeline.js';
import * as pl from './pipeline.js';
export class Lineline {
    store;
    bus = new EventBus();
    templates = new Map();
    constructor(options) {
        const dataDir = options?.dataDir ?? path.join(process.env.HOME ?? '.', '.lineline', 'data');
        this.store = new Store(dataDir);
        this.loadBuiltinTemplates();
    }
    loadBuiltinTemplates() {
        const tplDir = path.resolve(new URL('.', import.meta.url).pathname, '..', 'templates');
        if (!fs.existsSync(tplDir))
            return;
        for (const f of fs.readdirSync(tplDir).filter(f => f.endsWith('.yaml'))) {
            try {
                const t = YAML.parse(fs.readFileSync(path.join(tplDir, f), 'utf-8'));
                if (t.name)
                    this.templates.set(t.name, t);
            }
            catch { /* skip invalid */ }
        }
    }
    on(event, callback) {
        return this.bus.on(event, callback);
    }
    create(config) {
        let line;
        if (config.kind === 'timeline') {
            line = tl.createTimeline(config.name, config.endless ?? false, config.tags, config.metadata);
        }
        else {
            line = pl.createPipeline(config.name, config.stages, config.template, config.tags, config.metadata);
        }
        this.store.save(line);
        this.bus.emit('line:created', { line });
        return line;
    }
    get(id) {
        return this.store.load(id);
    }
    list(filter) {
        let lines = this.store.loadAll();
        if (filter?.kind)
            lines = lines.filter(l => l.kind === filter.kind);
        if (filter?.status)
            lines = lines.filter(l => l.status === filter.status);
        if (filter?.tags?.length)
            lines = lines.filter(l => filter.tags.some(t => l.tags?.includes(t)));
        return lines;
    }
    delete(id) {
        const line = this.store.load(id);
        if (!line)
            throw new Error(`Line ${id} not found`);
        this.store.remove(id);
        this.bus.emit('line:deleted', { line });
    }
    setStatus(id, status) {
        const line = this.store.load(id);
        if (!line)
            throw new Error(`Line ${id} not found`);
        const old = line.status;
        line.status = status;
        line.updatedAt = new Date().toISOString();
        this.store.save(line);
        this.bus.emit('line:statusChanged', { line, oldStatus: old, newStatus: status });
    }
    pause(id) { this.setStatus(id, 'paused'); }
    resume(id) { this.setStatus(id, 'active'); }
    archive(id) { this.setStatus(id, 'archived'); }
    // ── Timeline ops ──
    addEntry(timelineId, event, data) {
        const line = this.store.load(timelineId);
        if (!line || line.kind !== 'timeline')
            throw new Error('Timeline not found');
        const entry = tl.addEntry(line, event, data);
        this.store.save(line);
        this.bus.emit('timeline:entryAdded', { line, entry });
        return entry;
    }
    removeEntry(timelineId, entryId) {
        const line = this.store.load(timelineId);
        if (!line || line.kind !== 'timeline')
            throw new Error('Timeline not found');
        const entry = tl.removeEntry(line, entryId);
        this.store.save(line);
        this.bus.emit('timeline:entryRemoved', { line, entry });
    }
    // ── Pipeline ops ──
    advanceStage(pipelineId) {
        const line = this.store.load(pipelineId);
        if (!line || line.kind !== 'pipeline')
            throw new Error('Pipeline not found');
        if (line.status === 'done')
            throw new Error('Pipeline already completed');
        const prev = line.stages.find(s => s.id === line.currentStageId);
        const next = pl.advanceStage(line);
        this.store.save(line);
        this.bus.emit('pipeline:stageCompleted', { line, stage: prev });
        this.bus.emit('pipeline:stageActivated', { line, stage: next });
        return next;
    }
    completeStage(pipelineId, stageId) {
        const line = this.store.load(pipelineId);
        if (!line || line.kind !== 'pipeline')
            throw new Error('Pipeline not found');
        const stage = pl.completeStage(line, stageId);
        if (pl.isComplete(line)) {
            line.status = 'done';
            this.store.save(line);
            this.bus.emit('pipeline:stageCompleted', { line, stage });
            this.bus.emit('pipeline:completed', { line });
        }
        else {
            this.store.save(line);
            this.bus.emit('pipeline:stageCompleted', { line, stage });
        }
    }
    skipStage(pipelineId, stageId) {
        const line = this.store.load(pipelineId);
        if (!line || line.kind !== 'pipeline')
            throw new Error('Pipeline not found');
        const stage = pl.skipStage(line, stageId);
        if (pl.isComplete(line)) {
            line.status = 'done';
            this.store.save(line);
            this.bus.emit('pipeline:stageSkipped', { line, stage });
            this.bus.emit('pipeline:completed', { line });
        }
        else {
            this.store.save(line);
            this.bus.emit('pipeline:stageSkipped', { line, stage });
        }
    }
    addStage(pipelineId, stage) {
        const line = this.store.load(pipelineId);
        if (!line || line.kind !== 'pipeline')
            throw new Error('Pipeline not found');
        const s = pl.addStage(line, stage.name, stage.after);
        this.store.save(line);
        this.bus.emit('pipeline:stageAdded', { line, stage: s });
        return s;
    }
    removeStage(pipelineId, stageId) {
        const line = this.store.load(pipelineId);
        if (!line || line.kind !== 'pipeline')
            throw new Error('Pipeline not found');
        const s = pl.removeStage(line, stageId);
        this.store.save(line);
        this.bus.emit('pipeline:stageRemoved', { line, stage: s });
    }
    // ── Templates ──
    registerTemplate(name, template) {
        this.templates.set(name, template);
    }
    createFromTemplate(templateName, name) {
        const tpl = this.templates.get(templateName);
        if (!tpl)
            throw new Error(`Template "${templateName}" not found`);
        return this.create({ kind: 'pipeline', name, stages: tpl.stages, template: templateName });
    }
    listTemplates() {
        return [...this.templates.values()];
    }
}
