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
├── skill-manager/                # meta-skill (直接在集合 repo 中，非 submodule)
├── budget-travel/                # submodule → hananikaze/budget-travel
├── paper-reader/                 # submodule → hananikaze/paper-reader
├── lineline/                     # submodule → hananikaze/lineline
└── <new-skill>/                  # each skill = one submodule
```

## Operations

### List Installed Skills
查看 git submodule 状态，获取各 skill 的提交哈希和名称。也可读取各 skill 的 SKILL.md 获取描述。

### Add a New Skill (from existing repo)
在集合目录中通过 git submodule 添加目标 repo，提交并推送集合 repo。

### Create & Add a Brand New Skill
1. 在临时目录中编写 skill 代码和 SKILL.md
2. 在 GitHub 上为 `hananikaze` 创建同名公开 repo，推送代码
3. 在集合 repo 中将新 repo 作为 submodule 添加，提交并推送
4. 如有 npm 依赖，进入 skill 目录安装依赖

### Remove a Skill
通过 git submodule 的标准流程取消注册、移除目录和模块缓存，提交推送。如需彻底删除，可同时删除 GitHub repo。

### Update a Skill (pull latest)
进入目标 skill 目录拉取最新代码，回到集合目录更新 submodule 引用，提交推送。

### Update All Skills
使用 git submodule 的远程更新功能批量拉取所有 skill 的最新版本，提交推送。

### Push Changes Within a Skill
修改 skill 代码后需要两级推送：
1. 先在 skill 目录内提交并推送到 skill 自己的 repo
2. 再回到集合目录更新 submodule 引用，提交推送集合 repo

### Check Collection Status
查看所有 submodule 状态和集合 repo 的未提交变更。可遍历各 skill 查看内部状态。

## Important Rules

1. **Every skill = a submodule**。不要将 skill 代码直接提交到集合 repo（skill-manager 自身除外，它是 meta-skill）。
2. **Two-level push**：skill 内部变更需先推 skill repo，再更新集合 ref。
3. **npm 依赖**：添加含 package.json 的 skill 后，需进入目录安装依赖。
4. **SKILL.md 必须存在**：每个 skill 根目录必须有 SKILL.md，OpenClaw 才能发现它。
5. **Git 邮箱隐私**：GitHub 启用了邮箱隐私，新 repo 中使用 noreply 邮箱提交。
