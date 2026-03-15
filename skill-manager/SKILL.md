---
name: skill-manager
description: >
  Manage the my-skills collection: list installed skills, add new skills as git submodules,
  remove skills, update skills, check status, and push changes to the collection repo.
  The skill collection lives at ~/.openclaw/my-skills (repo: hananikaze/hananikaze_skill_collection)
  with each skill as a git submodule pointing to its own repo under hananikaze/*.
  Use when: adding/removing/updating skills, checking skill status, syncing with GitHub,
  creating new skill repos, or managing the skill collection.
  Triggers: "添加skill", "删除skill", "更新skill", "skill列表", "skill管理",
  "add skill", "remove skill", "update skill", "skill status", "管理技能".
---

# Skill Manager — my-skills Collection Management

Manages the skill collection at `~/.openclaw/my-skills/` (GitHub: `hananikaze/hananikaze_skill_collection`).

Each skill is a **git submodule** with its own repo under `hananikaze/<skill-name>`.

## Collection Structure

```
~/.openclaw/my-skills/           # hananikaze/hananikaze_skill_collection
├── .gitmodules                   # submodule registry
├── budget-travel/                # submodule → hananikaze/budget-travel
├── paper-reader/                 # submodule → hananikaze/paper-reader
├── lineline/                     # submodule → hananikaze/lineline
└── <new-skill>/                  # each skill = one submodule
```

## Operations

### List Installed Skills

```bash
cd ~/.openclaw/my-skills && git submodule status
```

Also check each skill's SKILL.md for description.

### Add a New Skill (from existing repo)

```bash
cd ~/.openclaw/my-skills
git submodule add git@github.com:hananikaze/<skill-name>.git <skill-name>
git commit -m "feat: add <skill-name> skill"
git push
```

### Create & Add a Brand New Skill

1. Create the skill directory with code/SKILL.md locally (e.g., in `/tmp/<skill-name>`)
2. Create GitHub repo:
   ```bash
   gh repo create hananikaze/<skill-name> --public --description "<description>" --source /tmp/<skill-name> --push
   ```
3. Add as submodule:
   ```bash
   cd ~/.openclaw/my-skills
   git submodule add git@github.com:hananikaze/<skill-name>.git <skill-name>
   git commit -m "feat: add <skill-name> skill"
   git push
   ```
4. If the skill has npm dependencies, run `cd <skill-name> && npm install`

### Remove a Skill

```bash
cd ~/.openclaw/my-skills
git submodule deinit -f <skill-name>
git rm -f <skill-name>
rm -rf .git/modules/<skill-name>
git commit -m "feat: remove <skill-name> skill"
git push
```

Optionally delete the GitHub repo: `gh repo delete hananikaze/<skill-name> --yes`

### Update a Skill (pull latest from its repo)

```bash
cd ~/.openclaw/my-skills/<skill-name>
git pull origin main
cd ..
git add <skill-name>
git commit -m "chore: update <skill-name> to latest"
git push
```

### Update All Skills

```bash
cd ~/.openclaw/my-skills
git submodule update --remote --merge
git add -A
git commit -m "chore: update all skills to latest"
git push
```

### Push Changes Within a Skill

When modifying a skill's code:

```bash
# 1. Commit & push inside the skill repo
cd ~/.openclaw/my-skills/<skill-name>
git add -A && git commit -m "<message>" && git push

# 2. Update the submodule reference in the collection
cd ~/.openclaw/my-skills
git add <skill-name>
git commit -m "chore: update <skill-name> ref"
git push
```

### Check Collection Status

```bash
cd ~/.openclaw/my-skills
git submodule status          # show all submodules + commit hashes
git status                    # show uncommitted changes
git submodule foreach 'git status'  # status inside each skill
```

## Git Config Note

GitHub email privacy is enabled for `hananikaze`. When committing in new repos, use:

```bash
git config user.email "hananikaze@users.noreply.github.com"
```

## Important Rules

1. **Every skill = a submodule**. Never commit skill code directly into the collection repo.
2. **Two-level push**: changes inside a skill need to be pushed in the skill repo first, then the submodule ref updated in the collection repo.
3. **npm dependencies**: after cloning/adding a skill with package.json, run `npm install` inside it.
4. **SKILL.md required**: every skill must have a SKILL.md at its root for OpenClaw to discover it.
