# lineline

Linear task/schedule management with **Timeline** and **Pipeline**.

## Install

```bash
npm install lineline
```

## Usage

### Library

```typescript
import { Lineline } from 'lineline';

const ll = new Lineline();

// Listen to all events
ll.on('*', (event, data) => console.log(event, data.line.name));

// Create a timeline
const tl = ll.create({ kind: 'timeline', name: '学日语', endless: true });
ll.addEntry(tl.id, '完成了第一课');

// Create a pipeline from template
const pl = ll.createFromTemplate('blog-publish', '发博客');
ll.advanceStage(pl.id); // Draft → Review
```

### CLI

```bash
lineline create timeline "学日语" --endless
lineline entry <id> "完成了第一课"
lineline create pipeline "发博客" --template blog-publish
lineline advance <id>
lineline list
lineline show <id>
```
