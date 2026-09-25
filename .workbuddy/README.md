# .workbuddy — WorkBuddy 本地识别配置

本目录用于让 WorkBuddy 正确识别 SpecWeave 的 `.agents/` 资产。

## 结构

| 路径 | 类型 | 说明 |
|---|---|---|
| `skills/` | 目录联接 (Junction) | 指向 `D:\spaces\SpecWeave\.agents\skills`，使 WorkBuddy 按项目级技能规范（`{workspace}/.workbuddy/skills/<name>/SKILL.md`）加载全部 160 个技能 |
| `memory/` | 普通目录 | WorkBuddy 工作区记忆（日志与长期笔记），由 WorkBuddy 自动维护 |

## 注意事项

- `skills/` 是**本地目录联接**，不纳入版本控制（已在 `.gitignore` 排除）。克隆仓库后需在新机器上重建：
  ```powershell
  New-Item -ItemType Junction -Path "<repo>\.workbuddy\skills" -Target "<repo>\.agents\skills"
  ```
- 由于是指向 `.agents/skills` 的联接，在 `.agents/skills/` 中新增/修改技能会**自动**被 WorkBuddy 识别，无需同步。
- 反之，通过 WorkBuddy 安装的项目级技能也会落入 `.agents/skills/`，提交前请注意甄别。
- 技能的唯一权威源仍为 `.agents/skills/`，请勿直接删除本目录下的 `skills` 联接后再新建同名普通目录，以免造成双源分叉。
- 根目录 `AGENTS.md` 已被 WorkBuddy 作为项目指导自动注入，无需额外配置。
