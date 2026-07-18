---
name: link-check-cmd
version: 1.2.0
description: "当用户提到'链接检查'、'检查链接'、'断链'、'链接修复'、'fix links'、'check links'、'验证链接'、'死链'、'链接有效性'、'提交前检查'时，必须使用此技能。提供Markdown链接有效性检查与自动修复能力：本地文件引用验证、外部URL可达性检测、file:///绝对路径转相对路径、相对路径层级自动校正。不要手动查找断链——本Skill封装了缓存机制、并发检测、自动修复和dry-run预览，是提交前质量门禁的核心工具。"
argument-hint: "[路径] [--fix] [--check-external] [--dry-run]"
user-invocable: true
paths:
  - ".agents/scripts/check-links.py"
  - ".agents/scripts/lib/link_fixer.py"
title: "Link Check 链接检查与修复 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/link-check-cmd/SKILL.toml"
---
# Link Check 链接检查与修复 Skill

> ⚠️ **本Skill是脚本命令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心命令+安全清单）
> - L2：脚本源码 [check-links.py](../../scripts/check-links.py) + [link_fixer/](../../scripts/lib/link_fixer/README.md)（完整实现）

## 1. Skill ID
`link-check-cmd`

## 2. 功能描述

提供Markdown链接有效性检查与自动修复能力，支持两类链接、两种模式：

| 模式 | 推荐场景 | 优势 |
|------|---------|------|
| **检查模式（默认）** | ⭐ 提交前质量门禁、文档重构后验证 | 快速扫描，零风险，输出问题清单 |
| **修复模式（--fix）** | ⭐ 文件移动/目录重构后断链修复 | 自动修复可修复问题，预览机制防误操作 |
| **外部链接检查（--check-external）** | ⭐ 发布前完整验证、定期巡检 | HEAD请求+GET回退，7天缓存避免重复请求 |

核心功能：本地文件引用存在性检查 → 外部URL可达性检测 → 自动修复可修复断链（绝对路径转相对、层级校正、斜杠补全）→ 输出结构化报告。

> **为什么用本Skill而非手动查找？** 手动检查链接效率极低且容易遗漏——一个中型文档库可能有数百个链接，人工逐一点击不现实；外部链接检查有网络开销和频率限制问题。本Skill封装了并发检测、7天缓存、自动修复等机制，检查效率提升数十倍，且修复逻辑经过多轮验证（目录迁移场景是高频重灾区）。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "链接检查"、"检查链接"、"验证链接"、"断链检查"、"死链检测"
- "链接修复"、"修复链接"、"fix links"、"repair links"、"自动修复断链"
- "提交前检查"、"PR检查"、"质量门禁"
- 文件移动、目录重构、原子化拆分后需要验证链接
- 提到 `check-links.py` 脚本

> **关于触发**：即使没有明确说"用link-check命令"，只要涉及Markdown文档链接的有效性验证或修复，就应该使用本Skill。链接问题是文档重构后最高频的遗留问题，不要等到用户抱怨"点不开"才想起来检查。

## 4. 方案选择决策树

```
需要检查/修复链接？
├─ 只是想看看有没有断链（不修改文件）？ → 检查模式（默认，第5.1节）
├─ 文件移动/重构后需要自动修复？ → 修复模式（先--dry-run预览，再--fix执行，第5.2节）
├─ 需要验证外部URL也能访问？ → 检查模式 + --check-external（第5.3节）
└─ 原子化拆分后的完整收尾？ → 优先使用 atomization-finalize-cmd（它内部会调用链接修复）
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `lnk-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=link-check | step=S0 | event=CMD_START | session=lnk-... | msg=开始链接检查：<简述> | ctx={"target_path":"...","check_external":false}
```

> **为什么决策前必须记录日志？** 链接检查可能误判（如动态生成链接），CMD_START记录检查路径和是否检查外链便于排查误报。

**写操作（--fix）原则**：必须先用 `--dry-run` 预览修复内容，确认无误再正式执行。

> **为什么dry-run是修复模式的强制前置步骤？** 自动修复虽然经过验证，但路径解析有边界情况（如特殊字符文件名、符号链接、跨盘符引用），直接执行可能"修复"成错误路径导致更多断链。dry-run在完全不修改文件的情况下展示所有将要执行的修改，是成本最低的防误操作手段。

## 5. 核心命令（快速开始）

脚本路径：[check-links.py](../../scripts/check-links.py)

### 5.1 检查模式（默认，零风险）

```bash
cd d:\spaces\SpecWeave

# 检查整个项目的本地链接
python .agents/scripts/check-links.py

# 只检查指定目录
python .agents/scripts/check-links.py --path docs/

# 检查单个文件
python .agents/scripts/check-links.py --path README.md

# 批量检查多个目录（--paths，自动去重，与 --path 互斥）
python .agents/scripts/check-links.py --paths .agents/skills .agents/commands docs/task-summaries
```

### 5.2 修复模式（先预览！）

```bash
# 预览将要修复的内容（不修改文件，强烈推荐先执行）
python .agents/scripts/check-links.py --fix --dry-run

# 确认无误后执行修复
python .agents/scripts/check-links.py --fix

# 只修复指定目录
python .agents/scripts/check-links.py --path docs/ --fix --dry-run
python .agents/scripts/check-links.py --path docs/ --fix
```

### 5.3 外部链接检查

```bash
# 本地 + 外部链接完整检查（外部链接有7天缓存）
python .agents/scripts/check-links.py --check-external

# 修复模式 + 外部链接检查
python .agents/scripts/check-links.py --fix --check-external --dry-run
python .agents/scripts/check-links.py --fix --check-external
```

### 5.4 文件重命名映射

```bash
# 文件重命名后修复链接（旧名→新名）
python .agents/scripts/check-links.py --fix --rename old-name.md new-name.md
```

> 完整参数表见脚本源码 `--help` 输出；公共参数定义在 [lib/cli.py](../../scripts/lib/cli.py)。

## 6. 自动修复能力范围

`--fix` 模式可以自动修复以下问题：

| 修复类型 | 说明 | 示例 | 幂等性 |
|---------|------|------|--------|
| 绝对路径转换 | `file:///` 本地绝对路径 → 相对路径 | `file:///d:/spaces/.../doc.md` → `../doc.md` | 已修复的不会重复修改 |
| 层级校正 | 文件移动后 `../` 层数错误 | `../../doc.md` → `../doc.md`（上移一层目录后） | 路径正确后不再改动 |
| 斜杠补全 | 目录链接尾部缺少 `/` | `./docs` → `./docs/` | 幂等 |
| 文件名映射 | 配合 `--rename` 更新重命名文件引用 | `old.md` → `new.md` | 配合rename参数一次性完成 |

**无法自动修复**的问题会明确列出，需要人工处理：
- 目标文件确实不存在（已删除/未创建）
- 跨盘符引用（Windows环境无可靠相对路径）
- 锚点（`#anchor`）不存在
- 外部URL返回4xx/5xx

## 7. 安全检查清单（执行修复前逐项确认）

- [ ] 已理解修复范围（本地链接/外部链接/指定目录）
- [ ] **修复前已执行 `--dry-run` 预览**（检查预览结果无异常）
- [ ] 预览中显示的修复数量符合预期（文件移动后数量应与移动范围匹配）
- [ ] 没有"无法自动修复"的关键路径问题（如有，先人工处理再执行）
- [ ] Git工作区已提交或有备份（防止意外修改可回滚）
- [ ] 修复后重新运行检查模式确认零问题
- [ ] 外部链接检查确认网络连通（避免误判）

> **为什么外部链接需要7天缓存而非实时检查？** 外部链接检查需要发起HTTP请求，实时检查数百个外链会：1) 因频率限制被目标网站封禁IP；2) 单次检查耗时过长（30秒→5分钟）；3) 网络波动导致临时不可达的链接被误判为断链。7天缓存平衡了"结果新鲜度"和"检查效率/稳定性"——如果一个链接7天前还能访问，大概率现在也能访问；如确需最新结果可手动删除缓存文件强制刷新。

## 8. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| 大量"文件不存在"误报 | 排除目录未配置 | 使用 `--exclude` 添加排除目录 |
| 外部链接全部超时 | 网络代理/防火墙问题 | 检查网络设置，或跳过 `--check-external` |
| 修复后仍有断链 | 存在无法自动修复的问题 | 查看报告中标注的"需人工处理"项 |
| 相对路径被改"错" | 跨盘符/符号链接边界 | 人工校正，提交issue给脚本维护者 |
| 缓存导致旧结果 | 外部链接缓存7天 | 删除 `.agents/cache/external-links-cache.json` 强制刷新 |

> 加 `-v` 或 `--verbose` 参数获取详细日志；调试问题加 `--debug`。

## 9. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **外部URL超时**：外部链接有7天缓存机制避免重复请求，但首次检查（缓存未命中时）可能因网络延迟导致检查较慢，这不是bug而是设计取舍——耐心等待即可，后续检查会直接读取缓存。
- **file:///路径必须转相对路径**：自动修复功能会将 `file:///` 开头的绝对路径转换为相对路径，但Windows盘符（如 `D:`、`C:`）有特殊处理逻辑——跨盘符引用无法可靠转换为相对路径，会被标记为"需人工处理"而非强行转换出错。
- **相对路径层级计算**：文件移动后 `../` 层数计算依赖于源文件和目标文件的目录深度差，移动文件到子目录时 `../` 层数增加，移动到上级目录时层数减少——这是最常见的断链来源，务必在文件移动后运行 `--fix` 修复。
- **--check-external需要网络**：外部链接检查模式需要发起HTTP请求，离线环境或防火墙限制下会全部超时，此时应跳过 `--check-external` 参数，仅检查本地链接。
- **Markdown链接格式变体**：自动识别标准 `[text](url)` 和尖括号包裹的 `<http://example.com>` 格式，但不识别裸URL（即纯文本的 `http://example.com` 未被任何Markdown链接语法包裹），裸URL不会被检查。

## 10. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 脚本源码（完整参数） | L2 | [check-links.py](../../scripts/check-links.py) | 需要高级参数时 |
| 链接修复核心逻辑 | L2 | [link_fixer/](../../scripts/lib/link_fixer/README.md) | 理解修复算法、排查修复异常 |
| 公共CLI参数 | L2 | [lib/cli.py](../../scripts/lib/cli.py) | 通用参数（--path、--verbose、--exclude等） |
| 原子化收尾（含链接修复） | L1 | [atomization-finalize-cmd](../atomization-finalize-cmd/SKILL.md) | 原子化拆分后的一键收尾 |

## 11. Changelog

- **v1.2.0** (2026-07-06): check-links.py 新增 --paths 多目录批量扫描参数（nargs="+"，与 --path 互斥），支持自动去重和 file_root_map 文件归属跟踪。解决批量原子提交后需扫描多个变更目录时必须用 PowerShell 循环的问题。基于 P0-1 批量提交复盘萃取。
- **v1.1.0** (2026-07-01): 在§4决策树后添加S0 CMD_START强制日志规范，记录触发时的输入参数（target_path/check_external）便于排查误报问题；补充第3个Why解释（外部链接7天缓存的设计原因）。
- **v1.0.0** (2026-06-30): 初始版本，基于check-links.py脚本封装为命令门面Skill，遵循五要素模型和渐进式披露三层架构。
