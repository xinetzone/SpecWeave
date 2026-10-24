# 登记面精确格式模板

本文件给出四个登记面 + 用户级联接的逐字格式，全部取自 2026-10-23 磁盘实测样例（`skill-quality-gate-remediation` 入库，CHANGELOG v1.31）。占位符用 `<name>` 表示新 Skill 目录名。

## 目录

1. [.agents/skills/README.md](#1-agentsskillsreadmemd)
2. [.agents/capability-registry/02-skills.md](#2-agentscapability-registry02-skillsmd)
3. [.agents/skills/CHANGELOG.md](#3-agentskillschangelogmd)
4. [.meta/toml 镜像](#4-metatoml-镜像)
5. [验收命令逐字签名](#5-验收命令逐字签名)
6. [用户级联接](#6-用户级联接)

## 1. `.agents/skills/README.md`

- 分类标题带计数：`### 完整Skill（14个）`、`### 命令集门面（11个）`，表头数字必须等于表体行数。
- 完整Skill 表列：`| Skill名称 | 类型 | 功能描述 | 核心触发词 | SKILL.md路径 |`
- 行内路径相对 `.agents/skills/`：`[<name>/SKILL.md](<name>/SKILL.md)`
- 实测行（v1.31 入库时新增）：

```markdown
| skill-quality-gate-remediation | 完整Skill（v1.0.0，L1） | 技能质量门（check-skill-quality.py）修复闭环：取基线 → 按 error→warn 定位 → … | 质量门没过、check-skill-quality 报错、Skill 只有 65 分、… | [skill-quality-gate-remediation/SKILL.md](skill-quality-gate-remediation/SKILL.md) |
```

## 2. `.agents/capability-registry/02-skills.md`

- 分类计数与 README 独立（同一「完整Skill」分类此处实测为 12 个，README 为 14 个——收录范围不同，各自对齐自身行数即可，禁止互相「拉平」）。
- 表列：`| Skill名 | 触发词 | 方案数 | 版本 | 路径 |`
- 行内路径相对 `.agents/capability-registry/`：`[skills/<name>/SKILL.md](../skills/<name>/SKILL.md)`
- 触发词用中文引号加顿号分隔：`"质量门没过"、"check-skill-quality 报错"、…`
- 方案数格式：`1（流程一句话摘要；含 N 项映射表；L1）`

## 3. `.agents/skills/CHANGELOG.md`

- frontmatter 含 `id/date/type/source/title`；正文条目倒序，最新在最上。
- 取号必须实跑：`grep -m1 '^- \*\*v' .agents/skills/CHANGELOG.md` → 当前最大号 +1。
- 条目模板（要素顺序参照 v1.31 实测条目）：

```markdown
- **v<N>** (YYYY-MM-DD): 新增<分类> Skill <name>（<分类> X→X+1，v1.0.0，L1 单案例验证）。封装<来源会话/案例>为<流程一句话>：S0 <步骤> → S1 → … 。判据逐条对照当前源码核实（<文件与行号>）。验证：check-skill-quality 100/100（34 项全 PASS，…）；同步登记 README.md（<分类> X→X+1）、capability-registry/02-skills.md（Y→Y+1）、.meta/toml 镜像；用户级 `~/.qoder/skills/<name>` 以目录联接指向主权区权威副本，零内容复制。与 <相邻技能> 建立边界路由，本技能只管「<定位>」。
```

- 若顺带修正了 HEAD 计数漂移，必须在条目中显式写出 old→new 与实测行数，参照 v1.30 实测句式：`顺带修正既有计数漂移：README 完整 Skill 表头 11→13（原有 12 行）、registry 表头 9→11（原有 10 行）`。

## 4. `.meta/toml` 镜像

路径：`<仓根>/.meta/toml/.agents/skills/<name>/SKILL.toml`（注意 `.meta` 在仓库根，不在 `.agents` 下）。实测格式（5 字段，无 frontmatter 围栏）：

```toml
id = "skill"
title = "技能质量门修复闭环 Skill"
category = "skills/skill-quality-gate-remediation"
date = "2026-10-23"
version = "1.0"
```

- `category` 固定 `skills/<name>`；`version` 用两段（`1.0`），与 SKILL.md frontmatter 的三段（`1.0.0`）不同，照镜像既有惯例写。

## 5. 验收命令逐字签名

```bash
# 质量门（在仓根执行；--path 支持仓外目录，见 lib/cli.py 的 --path 定义）
python .agents/scripts/check-skill-quality.py --path .agents/skills/<name> --verbose
python .agents/scripts/check-skill-quality.py --path .agents/skills/<name> --score --threshold 100

# 链接门（登记面+技能目录全集；--paths 可多目录，--check-frontmatter-paths 校验 source/x-toml-ref 等）
python .agents/scripts/check-links.py --paths .agents/skills .agents/capability-registry --check-frontmatter-paths
```

断链典型形态与处置：

| 失败形态 | 处置 |
|---|---|
| 链接指向目录（如 `.meta/toml/.agents/skills/`） | 改指具体源文件（如对应 `SKILL.md`） |
| `file:///` 绝对路径 | 改相对路径 |
| frontmatter `source`/`x-toml-ref` 指向不存在路径 | 修正为目标真实位置 |

## 6. 用户级联接

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.qoder\skills\<name>" `
  -Target "<仓库根>\.agents\skills\<name>"
```

- 前置：用户级路径不存在，或仅存在空目录树（用 `rmdir` 删除，非空即失败）。
- 禁止：`cmd /c mklink /J`（中文环境乱码失败）、任何形式的复制。
- 验证：`ls -la ~/.qoder/skills/ | grep "<name>"` 应显示为链接（`l` 前缀）指向主权区；再经用户级路径回读 `SKILL.md` 首行比对内容。
