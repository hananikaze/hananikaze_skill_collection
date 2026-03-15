#!/usr/bin/env node
import { Lineline } from './lineline.js';
import type { Pipeline, Timeline } from './types.js';

const args = process.argv.slice(2);
const cmd = args[0];

function flag(name: string): string | undefined {
  const i = args.indexOf(`--${name}`);
  if (i === -1 || i + 1 >= args.length) return undefined;
  return args[i + 1];
}

function hasFlag(name: string): boolean {
  return args.includes(`--${name}`);
}

function positional(index: number): string | undefined {
  // skip flags
  let pos = 0;
  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith('--')) { i++; continue; }
    if (pos === index) return args[i];
    pos++;
  }
  return undefined;
}

const ll = new Lineline();

function short(id: string): string { return id.slice(0, 8); }

function printLine(line: any): void {
  console.log(`[${line.kind}] ${line.name}  (${short(line.id)})  status=${line.status}`);
  if (line.kind === 'timeline') {
    const tl = line as Timeline;
    console.log(`  endless: ${tl.endless}  entries: ${tl.entries.length}`);
    for (const e of tl.entries.slice(-10)) {
      console.log(`    ${e.ts.slice(0, 16)} ${e.event}  (${short(e.id)})`);
    }
  } else {
    const pl = line as Pipeline;
    if (pl.template) console.log(`  template: ${pl.template}`);
    for (const s of pl.stages) {
      const marker = s.id === pl.currentStageId ? '>' : ' ';
      console.log(`  ${marker} [${s.status.padEnd(7)}] ${s.name}  (${short(s.id)})`);
    }
  }
}

function findLine(partial: string): string {
  // try exact, then prefix match
  const line = ll.get(partial);
  if (line) return partial;
  const all = ll.list();
  const matches = all.filter(l => l.id.startsWith(partial));
  if (matches.length === 1) return matches[0].id;
  if (matches.length > 1) { console.error(`Ambiguous ID prefix: ${partial}`); process.exit(1); }
  console.error(`Line not found: ${partial}`); process.exit(1);
}

try {
  switch (cmd) {
    case 'create': {
      const kind = positional(0);
      const name = positional(1);
      if (!kind || !name) { console.error('Usage: lineline create <timeline|pipeline> <name>'); process.exit(1); }
      if (kind === 'timeline') {
        const line = ll.create({ kind: 'timeline', name, endless: hasFlag('endless') });
        console.log(`Created timeline: ${short(line.id)}  "${name}"`);
      } else if (kind === 'pipeline') {
        const tpl = flag('template');
        if (tpl) {
          const line = ll.createFromTemplate(tpl, name);
          console.log(`Created pipeline from template "${tpl}": ${short(line.id)}  "${name}"`);
        } else {
          console.error('Pipeline creation requires --template or use the library API for ad-hoc stages');
          process.exit(1);
        }
      } else {
        console.error(`Unknown kind: ${kind}`);
        process.exit(1);
      }
      break;
    }
    case 'list': {
      const lines = ll.list({ kind: flag('kind'), status: flag('status') });
      if (lines.length === 0) { console.log('No lines found.'); break; }
      for (const l of lines) {
        console.log(`${short(l.id)}  [${l.kind}]  ${l.name}  (${l.status})`);
      }
      break;
    }
    case 'show': {
      const id = findLine(positional(0) ?? '');
      const line = ll.get(id)!;
      printLine(line);
      break;
    }
    case 'entry': {
      const id = findLine(positional(0) ?? '');
      const event = positional(1);
      if (!event) { console.error('Usage: lineline entry <timeline-id> <event>'); process.exit(1); }
      const entry = ll.addEntry(id, event);
      console.log(`Added entry ${short(entry.id)}: ${event}`);
      break;
    }
    case 'advance': {
      const id = findLine(positional(0) ?? '');
      const stage = ll.advanceStage(id);
      console.log(`Advanced to stage: ${stage.name} (${short(stage.id)})`);
      break;
    }
    case 'complete': {
      const id = findLine(positional(0) ?? '');
      ll.completeStage(id, flag('stage'));
      console.log('Stage completed.');
      break;
    }
    case 'skip': {
      const id = findLine(positional(0) ?? '');
      ll.skipStage(id, flag('stage'));
      console.log('Stage skipped.');
      break;
    }
    case 'add-stage': {
      const id = findLine(positional(0) ?? '');
      const name = positional(1);
      if (!name) { console.error('Usage: lineline add-stage <pipeline-id> <name> [--after <stage-id>]'); process.exit(1); }
      const stage = ll.addStage(id, { name, after: flag('after') });
      console.log(`Added stage: ${stage.name} (${short(stage.id)})`);
      break;
    }
    case 'pause': { const id = findLine(positional(0) ?? ''); ll.pause(id); console.log('Paused.'); break; }
    case 'resume': { const id = findLine(positional(0) ?? ''); ll.resume(id); console.log('Resumed.'); break; }
    case 'archive': { const id = findLine(positional(0) ?? ''); ll.archive(id); console.log('Archived.'); break; }
    case 'delete': { const id = findLine(positional(0) ?? ''); ll.delete(id); console.log('Deleted.'); break; }
    case 'templates': {
      const tpls = ll.listTemplates();
      if (tpls.length === 0) { console.log('No templates.'); break; }
      for (const t of tpls) {
        console.log(`${t.name}${t.description ? ' - ' + t.description : ''}`);
        for (const s of t.stages) console.log(`  • ${s.name}`);
      }
      break;
    }
    default:
      console.log(`lineline - linear task/schedule management

Commands:
  create timeline <name> [--endless]
  create pipeline <name> --template <tpl>
  list [--kind timeline|pipeline] [--status active|paused|archived|done]
  show <id>
  entry <timeline-id> <event>
  advance <pipeline-id>
  complete <pipeline-id> [--stage <stage-id>]
  skip <pipeline-id> [--stage <stage-id>]
  add-stage <pipeline-id> <name> [--after <stage-id>]
  pause|resume|archive|delete <id>
  templates`);
  }
} catch (e: any) {
  console.error(`Error: ${e.message}`);
  process.exit(1);
}
