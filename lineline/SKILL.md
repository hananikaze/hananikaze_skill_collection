---
name: lineline
description: >
  Linear task/schedule management system with two line types: Timeline (append-only event log for open-ended schedules) and Pipeline (linear stage-based workflow with templates). All mutations emit events with callback support.
  Use when: managing tasks as linear flows, creating pipelines from templates, tracking progress through stages, recording timeline events, or when another skill needs workflow tracking.
  Triggers: "创建流水线", "pipeline", "timeline", "任务流", "进度管理", "lineline", "advance", "打卡".
---

# Lineline — Linear Task Management

A linear task/schedule management system. Two line types:
- **Timeline**: append-only event log, no fixed stages, can be endless
- **Pipeline**: linear stage-based workflow, created from templates or ad-hoc, terminates on completion

## CLI Reference

The CLI is at: `~/.openclaw/my-skills/lineline/dist/cli.js`

Run with: `node ~/.openclaw/my-skills/lineline/dist/cli.js <command>`

### Commands

```bash
# Create
create timeline <name> [--endless]
create pipeline <name> --template <template-name>
create pipeline <name>   # ad-hoc, requires --stages via programmatic API

# List & Show
list [--kind timeline|pipeline] [--status active|paused|archived|done]
show <id>
templates

# Timeline Operations
entry <timeline-id> "<event description>"

# Pipeline Operations
advance <pipeline-id>                        # move to next stage
complete <pipeline-id> [--stage <stage-id>]  # complete current/specific stage
skip <pipeline-id> [--stage <stage-id>]      # skip current/specific stage
add-stage <pipeline-id> "<name>" [--after <stage-id>]

# Lifecycle
pause <id>
resume <id>
archive <id>
delete <id>
```

### ID Matching
IDs can be abbreviated — use the first 8 characters (e.g., `735704cf`).

## Built-in Templates

Templates are YAML files in `~/.openclaw/my-skills/lineline/templates/`:

- **blog-publish**: Draft → Review → Edit → Publish → Promote
- **budget-travel**: 调研与路线规划 → 旅行打卡 → 游记与总结

## Programmatic Usage (TypeScript/JS)

```typescript
import { Lineline } from './dist/index.js';

const ll = new Lineline({ dataDir: '~/.openclaw/my-skills/lineline/data' });

// Register callbacks on ANY event
ll.on('pipeline:stageCompleted', (event, { line, stage }) => {
  console.log(`Stage ${stage.name} completed in ${line.name}`);
});

ll.on('*', (event, data) => {
  console.log(`Event: ${event}`);
});

// Create & operate
const p = ll.createFromTemplate('budget-travel', '长沙穷游');
ll.advanceStage(p.id);
```

## Events

All mutations emit events. Register with `on(event, callback)`:

| Event | Trigger |
|---|---|
| `line:created` | Any line created |
| `line:deleted` | Any line deleted |
| `line:statusChanged` | pause/resume/archive |
| `timeline:entryAdded` | New timeline entry |
| `timeline:entryRemoved` | Timeline entry removed |
| `pipeline:stageActivated` | Stage becomes active |
| `pipeline:stageCompleted` | Stage marked done |
| `pipeline:stageSkipped` | Stage skipped |
| `pipeline:stageAdded` | New stage inserted |
| `pipeline:stageRemoved` | Stage removed |
| `pipeline:completed` | All stages done, pipeline complete |
| `line:metadataChanged` | Metadata updated |
| `line:tagged` | Tags changed |
| `*` | Wildcard — catches all events |

## Workflow Patterns

### Travel Pipeline (with budget-travel skill)
```bash
node ~/.openclaw/my-skills/lineline/dist/cli.js create pipeline "西安穷游" --template budget-travel
# → 调研与路线规划 (active) → 旅行打卡 → 游记与总结
```

### Custom Pipeline
```bash
node ~/.openclaw/my-skills/lineline/dist/cli.js create pipeline "搬家计划" --template custom
# Or add stages dynamically:
node ~/.openclaw/my-skills/lineline/dist/cli.js add-stage <id> "找房子"
node ~/.openclaw/my-skills/lineline/dist/cli.js add-stage <id> "打包行李"
node ~/.openclaw/my-skills/lineline/dist/cli.js add-stage <id> "搬运"
```

### Endless Timeline
```bash
node ~/.openclaw/my-skills/lineline/dist/cli.js create timeline "读书笔记" --endless
node ~/.openclaw/my-skills/lineline/dist/cli.js entry <id> "读完《三体》第一部"
node ~/.openclaw/my-skills/lineline/dist/cli.js entry <id> "开始《三体》第二部"
```

## Data Storage

Each line is stored as a YAML file in `~/.openclaw/my-skills/lineline/data/<id>.yaml`. Human-readable and editable.
