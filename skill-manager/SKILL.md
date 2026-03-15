---
name: skill-manager
description: >
  Manage the my-skills collection at ~/.openclaw/my-skills (repo: hananikaze/hananikaze_skill_collection).
  Each skill is a git submodule under hananikaze/<skill-name>.
  Use when: adding, removing, updating skills, or syncing with GitHub.
  Triggers: "添加skill", "删除skill", "更新skill", "skill管理", "add skill", "remove skill", "管理技能".
---

# Skill Manager

集合目录: `~/.openclaw/my-skills/` → `hananikaze/hananikaze_skill_collection`

## 核心规则

- **每个 skill = 一个 git submodule**，独立 repo `hananikaze/<name>`
- skill-manager 自身是例外，直接存在于集合 repo 中
- 每个 skill 根目录必须有 SKILL.md
- 修改 skill 后需两级推送：先推 skill repo，再更新集合 repo 的 submodule 引用
- GitHub 邮箱隐私已开启，新 repo 用 noreply 邮箱提交

## 操作

| 操作 | 说明 |
|---|---|
| 新建 skill | 本地编写 → 创建 GitHub repo → 作为 submodule 添加到集合 |
| 添加已有 skill | 将已有 repo 作为 submodule 添加 |
| 移除 skill | 标准 submodule 移除流程 |
| 更新 skill | 进入 skill 目录拉取最新，更新集合引用 |
| 查看状态 | 查看 submodule 状态 |
