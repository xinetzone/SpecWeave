---
name: docgen-cmd
version: 1.0.0
description: "当用户提到'生成导航'、'更新导航'、'更新看板'、'刷新看板'、'生成文档索引'、'docgen'、'更新README'、'应用清单'、'文档生成'时，必须使用此技能。提供文档导航表与执行看板自动生成能力：扫描文档目录生成导航表、扫描.trae/specs/生成进度看板、生成apps/应用清单索引。不要手动编辑导航表或看板区域——它们由标记包裹，本Skill会自动更新标记区域内的内容，手动编辑会被下次生成覆盖。"
argument-hint: "<nav|dashboard|apps|all> [--path <dir>]"
user-invocable: true
paths:
  - ".agents/scripts/docgen.py"
  - "README.md"
  - "docs/README.md"
  - "apps/README.md"
---

# DocGen 文档导航与看板生成 Skill

> ⚠️ **本Skill是脚本命令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心命令+安全清单）
> - L2：脚本源码 [docgen.py](../../scripts/docgen.py)（完整实现）

## 1. Skill ID
`docgen-cmd`

## 2. 功能描述

文档索引与看板自动生成工具，提供四个子命令，覆盖三类文档生成场景：

| 子命令 | 功能 | 更新目标 |
|--------|------|---------|
| **nav** | ⭐ 扫描文档目录生成导航表 | README.md、docs/README.md 中 `<!-- nav-start -->`/`<!-- nav-end -->` 标记区域 |
| **dashboard** | ⭐ 扫描 .trae/specs/ 生成进度看板 | 根 README.md 中看板区域 |
| **apps** | 生成 apps/ 应用清单索引 | apps/README.md 中应用清单区域 |
| **all** | 依次执行 nav → dashboard → apps | 以上全部 |

**幂等性与预览机制**：docgen 是幂等操作（多次运行结果相同），且仅更新标记区域（标记外人工内容不受影响）。推荐的预览/回滚流程：
1. 执行前先 `git commit` 或 `git stash` 保存当前状态
2. 执行 docgen 子命令
3. 用 `git diff` 查看生成结果
4. 如不满意，`git checkout .` 回滚到之前状态

> **为什么用本Skill而非手动编辑导航表？** 手动维护导航表和看板有三个问题：一是容易遗漏新增文档，导致导航不全；二是格式不统一，表格对齐、描述截断容易出错；三是看板进度需要统计每个Spec的任务完成状态，人工统计既慢又不准。本Skill自动扫描frontmatter提取标题/描述/状态，保证导航和看板始终与实际文件同步。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "生成导航"、"更新导航"、"刷新导航表"、"文档索引"
- "更新看板"、"刷新看板"、"进度看板"、"Spec看板"
- "生成文档"、"docgen"、"更新README导航"
- "应用清单"、"apps索引"
- 新增/删除/重命名文档后
- 提到 `docgen.py`、`generate-nav.py`、`generate-dashboard.py` 脚本

> **关于触发**：导航表和看板都用HTML注释标记包裹（如 `<!-- nav-start -->`/`<!-- nav-end -->`），**标记区域内的内容会被脚本完全覆盖**——不要手动编辑标记区域内的表格，否则下次生成会丢失。如果需要添加说明，放在标记区域外面。

## 4. 方案选择决策树

```
需要更新文档索引/看板？
├─ 新增/删除/重命名了 docs/ 下的文档？ → nav（更新导航表，第5.1节）
├─ Spec 状态变更（完成任务/新增Spec）？ → dashboard（刷新进度看板，第5.2节）
├─ apps/ 目录新增了应用？ → apps（更新应用清单，第5.3节）
├─ 原子化收尾/发布前全量更新？ → all（依次执行全部，第5.4节）
└─ 文件移动/原子化拆分后需要完整收尾？ → 优先使用 atomization-finalize-cmd（内部调用nav+dashboard+链接修复）
```

**与其他Skill的关系**：
- 原子化收尾后通常由 `atomization-finalize-cmd` 自动调用本Skill
- 只需要单独更新导航或看板时直接使用本Skill

> **为什么all的执行顺序是nav→dashboard→apps？** nav和dashboard都可能修改根README.md，nav更新导航表区域（文件中靠前位置），dashboard更新看板区域（靠后位置），顺序执行不会相互覆盖；apps操作独立文件apps/README.md，放在最后不影响。这和装修顺序同理——先处理公共区域再处理独立房间。

## 5. 核心命令（快速开始）

脚本路径：[docgen.py](../../scripts/docgen.py)

> **注意**：`generate-nav.py` 和 `generate-dashboard.py` 是向后兼容包装器，实际功能都在 docgen.py 中，新代码直接使用 docgen.py。

### 5.1 更新文档导航表（nav）

```bash
cd d:\spaces\SpecWeave

# 生成/更新导航表（扫描docs/和根目录.md，更新README.md和docs/README.md）
python .agents/scripts/docgen.py nav
```

导航表自动从frontmatter或文件内容提取：
- **标题**：Markdown第一个H1标题，无标题则用文件名
- **描述**：frontmatter中的`description`字段，或正文前60字符摘要
- **链接**：自动计算相对路径

### 5.2 刷新Spec进度看板（dashboard）

```bash
# 生成/更新 Spec 执行进度看板（扫描.trae/specs/下所有主题和Spec）
python .agents/scripts/docgen.py dashboard
```

看板自动统计：
- 每个主题下的Spec总数、已完成数、进行中、待开始
- 每个Spec的任务完成进度（解析tasks.md中的复选框）
- 整体进度百分比

### 5.3 更新应用清单（apps）

```bash
# 生成/更新 apps/README.md 应用清单
python .agents/scripts/docgen.py apps
```

### 5.4 一键全量更新（all）

```bash
# 依次执行 nav → dashboard → apps（原子化收尾/发布前推荐）
python .agents/scripts/docgen.py all
```

> 完整参数说明见脚本源码 `--help` 输出；所有子命令支持 `--path <dir>` 指定项目根目录（默认自动解析）。

## 6. 标记区域说明

脚本通过HTML注释标记定位要更新的区域，**标记区域内的内容会被完全覆盖**：

| 目标文件 | 标记对 | 区域内容 |
|---------|--------|---------|
| README.md | `<!-- nav-start -->` / `<!-- nav-end -->` | 文档导航表 |
| docs/README.md | `<!-- nav-start -->` / `<!-- nav-end -->` | 文档导航表 |
| README.md | 看板区域标记 | Spec执行进度看板 |
| apps/README.md | `<!-- APPS_TABLE_START -->` / `<!-- APPS_TABLE_END -->` | 应用清单表 |

> **为什么使用标记区域而非全文件重写？** 全文件重写风险高——README.md中有人工维护的项目介绍、核心优势、架构说明等内容，自动生成只应覆盖"机器可生成"的部分（导航表、看板），保留人工编写的内容。标记区域机制实现了"人机分区编辑"：标记外是人写的，标记内是机器生成的，互不干扰。

## 7. 安全检查清单（执行前确认）

- [ ] 明确需要更新哪个部分（nav/dashboard/apps/all），不要盲目执行all
- [ ] **Git工作区已提交或有备份**（执行前git commit/stash，可用git diff预览变更、git checkout回滚）
- [ ] 新增的Markdown文件包含规范的frontmatter（id、title、description等）或H1标题
- [ ] Spec文件（spec.md）包含正确的status字段和tasks.md
- [ ] **没有手动编辑过标记区域内的内容**（如有手动修改，先移到标记外）
- [ ] 执行后检查更新结果，确认导航表链接正确、看板进度符合预期
- [ ] 如配合链接修复，先执行链接修复再生成导航（避免导航表引用断链）

## 8. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| "未找到标记"警告 | 目标文件中缺少对应HTML注释标记 | 检查README.md中是否有 `<!-- nav-start -->` 标记；需要的话手动添加标记对 |
| 导航表中缺少某个文档 | 文档不在扫描目录内，或frontmatter/标题格式有问题 | 检查constants.py中的SCAN_DIRS配置；确认文档有H1标题或frontmatter title |
| 看板进度显示100%但实际未完成 | Spec的status字段为completed但tasks有未完成项，或反之 | 检查spec.md的frontmatter status字段，或tasks.md的复选框格式 |
| 应用清单为空 | apps/目录不存在或为空，或缺少README.md | 确认apps/目录存在且包含应用子目录；apps/README.md需存在并包含标记 |
| 描述显示为文件名 | 文档缺少frontmatter description且无法从正文提取摘要 | 给文档添加规范的TOML frontmatter（id、type、title、description等） |

> 脚本输出会显示"找到 N 个文档"/"找到 N 个主题，M 个 Spec"，如果数量与预期不符，说明扫描范围或文件格式有问题。

## 9. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 脚本源码（完整参数） | L2 | [docgen.py](../../scripts/docgen.py) | 需要理解扫描逻辑、添加新的生成目标时 |
| 原子化收尾Skill | L1 | [atomization-finalize-cmd](../atomization-finalize-cmd/SKILL.md) | 文件移动/拆分后的完整收尾（含链接修复） |
| 链接检查Skill | L1 | [link-check-cmd](../link-check-cmd/SKILL.md) | 生成导航前先确认链接有效 |
| 共享工具库 | L2 | [scripts/lib/markdown.py](../../scripts/lib/markdown.py) | 理解标题/描述提取逻辑 |
| 扫描配置 | L2 | [scripts/constants.py](../../scripts/constants.py) | SCAN_DIRS、TARGETS、MANUAL_DESCRIPTIONS等配置 |

## 10. Changelog

- **v1.0.0** (2026-06-30): 初始版本，基于docgen.py脚本封装为命令门面Skill，整合了原generate-nav.py和generate-dashboard.py的功能，遵循五要素模型和渐进式披露三层架构。
