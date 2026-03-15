import fs from 'node:fs';
import path from 'node:path';
import YAML from 'yaml';
export class Store {
    dir;
    constructor(dataDir) {
        this.dir = dataDir;
        fs.mkdirSync(this.dir, { recursive: true });
    }
    save(line) {
        fs.writeFileSync(path.join(this.dir, `${line.id}.yaml`), YAML.stringify(line), 'utf-8');
    }
    load(id) {
        const p = path.join(this.dir, `${id}.yaml`);
        if (!fs.existsSync(p))
            return undefined;
        return YAML.parse(fs.readFileSync(p, 'utf-8'));
    }
    remove(id) {
        const p = path.join(this.dir, `${id}.yaml`);
        if (!fs.existsSync(p))
            return false;
        fs.unlinkSync(p);
        return true;
    }
    loadAll() {
        if (!fs.existsSync(this.dir))
            return [];
        return fs.readdirSync(this.dir)
            .filter(f => f.endsWith('.yaml'))
            .map(f => YAML.parse(fs.readFileSync(path.join(this.dir, f), 'utf-8')));
    }
}
