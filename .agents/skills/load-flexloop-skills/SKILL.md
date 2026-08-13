---
name: load-flexloop-skills
description: 自动装载/扫描 flexloop chaos 技能目录，生成技能注册表索引。触发词："装载flexloop技能"、"扫描技能目录"、"加载技能"、"skill auto loader"、"skill registry"、"技能索引"、"加载flexloop技能"、"扫描flexloop技能"、"注册技能"
version: "0.1.0"
argument-hint: "[--extra-dir DIR]... [--mode strict|relaxed] [--force] [--no-cache] [--output FILE] [--format json|markdown|both] [--verbose]"
user-invocable: true
paths:
  - scripts/cli.py
---

# FlexLoop 技能装载器 Skill

> ⚠️ **本Skill是脚本命令门面（L1索引层）**，遵循渐进式披露三层架构：
> - L0：.agents/ONBOARDING.md（入口速查）
> - L1：本文件（触发词+核心步骤+参数说明+安全清单）
> - L2：scripts/ 目录下各模块源码（完整实现）

## 1. Skill ID

`load-flexloop-skills`

## 2. 功能描述（Overview）

自动扫描项目中的 SKILL.md 技能文件，解析 frontmatter 元数据，验证技能文档完整性，并生成结构化的技能注册表索引。

**默认扫描路径**：
- `vendor/flexloop/apps/chaos/.agents/skills/` — flexloop chaos 内置技能（标记为 vendor 来源）
- `.agents/skills/` — 项目本地自定义技能（标记为 local 来源）

**核心能力**：
- YAML/TOML frontmatter 自动解析与验证
- strict/relaxed 双验证模式（strict 检查推荐章节完整性）
- 增量缓存机制（避免重复解析未变更文件）
- 技能名称冲突检测
- JSON + Markdown 双格式报告输出
- 自动向上查找项目根目录（通过 AGENTS.md 定位）

> **为什么用本Skill？** 手动维护技能注册表容易遗漏新增技能、frontmatter 格式错误难以及时发现、技能名称冲突会导致调用歧义。本工具一键全量扫描，自动验证元数据完整性，生成统一索引，确保技能目录始终处于可发现、可审计状态。

## 3. 何时使用（When to Use）

当用户提到以下任何内容时触发本技能：

- **装载相关**："装载flexloop技能"、"加载技能"、"加载flexloop技能"、"注册技能"
- **扫描相关**："扫描技能目录"、"扫描flexloop技能"、"扫描SKILL.md"
- **索引相关**："技能索引"、"skill registry"、"skill auto loader"、"技能注册表"
- **新增技能后**：创建新的 SKILL.md 后验证格式正确性
- **技能排查**：检查技能是否被正确发现、frontmatter 是否完整
- **生成报告**：需要 JSON 或 Markdown 格式的技能清单

## 4. 快速开始（Quick Start）

### 4.1 默认用法（推荐）

在项目根目录执行，使用 strict 模式全量扫描，同时输出 JSON 和 Markdown 报告到默认目录：

```bash
cd d:\spaces\SpecWeave
python .agents/skills/load-flexloop-skills/scripts/cli.py
```

### 4.2 示例输出

```
============================================================
扫描完成
============================================================
  扫描目录:
    - vendor/flexloop/apps/chaos/.agents/skills/
    - .agents/skills/

  技能总数: 28
  OK:        26
  Warning:   2
  Error:     0
  Conflicts: 0
============================================================

生成的报告文件:
  - d:\spaces\SpecWeave\.agents\skills\load-flexloop-skills\reports\skill-registry.json
  - d:\spaces\SpecWeave\.agents\skills\load-flexloop-skills\reports\skill-registry.md
```

- **OK**：frontmatter 完整，strict 模式下推荐章节齐全
- **Warning**：frontmatter 必填字段存在但缺少推荐章节（strict 模式）
- **Error**：缺少 name 字段或 frontmatter 解析失败
- **Conflicts**：存在同名技能（多个 SKILL.md 使用相同 name）

### 4.3 仅输出 JSON 到指定文件

```bash
python .agents/skills/load-flexloop-skills/scripts/cli.py --format json --output ./skills.json
```

### 4.4 添加额外扫描目录

```bash
python .agents/skills/load-flexloop-skills/scripts/cli.py --extra-dir ./my-custom-skills --extra-dir ./experimental/skills
```

### 4.5 禁用缓存强制全量扫描

```bash
python .agents/skills/load-flexloop-skills/scripts/cli.py --force --verbose
```

## 5. 参数说明（Parameters）

| 参数 | 短名 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--project-root` | `-r` | Path | 自动检测 | 项目根目录路径，默认向上查找包含 AGENTS.md 的目录 |
| `--extra-dir` | `-d` | list[str] | 无 | 额外扫描目录（相对于 project_root），可多次指定 |
| `--mode` | `-m` | choice | `strict` | 验证模式：`strict` 检查推荐章节完整性，`relaxed` 仅检查必填字段 |
| `--no-cache` | — | flag | `false` | 禁用增量缓存，全量重新扫描 |
| `--force` | `-f` | flag | `false` | 强制全量重新扫描（相当于 `--no-cache`） |
| `--output` | `-o` | Path | 默认目录 | 输出文件路径；不指定则输出到默认 reports/ 目录 |
| `--format` | `-fmt` | choice | `both` | 输出格式：`json`/`markdown`/`both`；指定 `--output` 时以文件后缀为准 |
| `--verbose` | `-v` | flag | `false` | 打印详细扫描日志 |
| `--version` | — | flag | — | 打印版本号并退出 |

## 6. 依赖（Dependencies）

### 6.1 运行环境

- **Python**：3.10 或更高版本
- **标准库**：pathlib、dataclasses、enum、json、hashlib（缓存用）

### 6.2 可选依赖

- **typer**：提供更友好的 CLI 体验（自动补全、彩色帮助）。如未安装，自动回退到 argparse
- **click**：typer 的依赖，用于 Choice 类型支持

安装可选依赖：
```bash
pip install typer click
```

> 注意：typer 不是必须的，脚本会在无 typer 时自动使用 argparse，功能完全一致。

### 6.3 项目内部依赖

- `.agents/scripts/lib/frontmatter.py`：frontmatter 解析工具（项目共享库）

## 7. 输出格式（Output）

### 7.1 JSON 报告结构

默认输出位置：`.agents/skills/load-flexloop-skills/reports/skill-registry.json`

```json
{
  "scan_time": "2026-08-07T10:30:00.123456",
  "scan_dirs": [
    "vendor/flexloop/apps/chaos/.agents/skills/",
    ".agents/skills/"
  ],
  "skills": [
    {
      "name": "load-flexloop-skills",
      "skill_path": ".agents/skills/load-flexloop-skills/SKILL.md",
      "source": "local",
      "description": "自动装载/扫描 flexloop chaos 技能目录...",
      "version": "0.1.0",
      "status": "ok",
      "issues": [],
      "raw_metadata": {
        "argument-hint": "[--extra-dir DIR]...",
        "user-invocable": true,
        "paths": ["scripts/cli.py"]
      }
    }
  ],
  "errors": [],
  "conflicts": []
}
```

字段说明：
- `status`：`ok`（正常）/`warning`（缺少推荐章节）/`error`（必填字段缺失）
- `source`：`vendor`（来自 flexloop）/`local`（项目本地或额外目录）
- `issues`：strict 模式下发现的问题列表
- `conflicts`：同名技能冲突详情

### 7.2 Markdown 报告结构

默认输出位置：`.agents/skills/load-flexloop-skills/reports/skill-registry.md`

包含：
- 扫描统计摘要（总数、OK/Warning/Error/Conflict 数量）
- 技能清单表格（名称、版本、来源、状态、路径）
- 错误详情表（如有）
- 名称冲突列表（如有）

## 8. 部署/安装（Deployment）

本技能为文档+脚本型技能，无需额外安装步骤：

1. **目录结构**：
   ```
   .agents/skills/load-flexloop-skills/
   ├── SKILL.md          # 本文件（技能门面）
   ├── scripts/
   │   ├── cli.py        # CLI 入口
   │   ├── parser.py     # frontmatter 解析与验证
   │   ├── discovery.py  # 技能文件发现
   │   ├── cache.py      # 增量缓存
   │   ├── models.py     # 数据模型
   │   ├── report.py     # 报告生成
   │   └── __init__.py
   └── reports/          # 输出目录（自动创建）
       ├── skill-registry.json
       └── skill-registry.md
   ```

2. **验证安装**：执行 `python .agents/skills/load-flexloop-skills/scripts/cli.py --version`，应输出版本号。

3. **缓存位置**：扫描缓存存储在系统临时目录，基于文件内容 hash 实现增量扫描。

## 9. 错误处理（Error Handling）

### 9.1 Exit Code

| Exit Code | 含义 |
|-----------|------|
| 0 | 扫描完成，无错误（允许有 Warning） |
| 1 | 扫描完成，但存在 Error 级问题（缺少 name、解析失败等） |
| 2 | 项目根目录不存在 |

### 9.2 错误类型与处理

| 错误类型 | 原因 | 建议处理方式 |
|---------|------|-------------|
| `missing_frontmatter` | SKILL.md 缺少 YAML frontmatter（--- 包裹） | 在文件开头添加正确格式的 frontmatter |
| `missing_name` | frontmatter 中缺少 name 字段或为空 | 添加 `name: skill-name` 字段 |
| `parse_error` | frontmatter YAML 语法错误 | 检查 YAML 缩进、冒号后空格、引号配对 |
| `unicode_decode_error` | 文件编码不是 UTF-8 | 将文件转换为 UTF-8 编码保存 |
| `io_error` | 文件读取失败 | 检查文件权限、路径是否正确 |

### 9.3 常见问题

**Q: 新创建的技能没有出现在扫描结果中？**
- 确认文件名为 `SKILL.md`（全大写，注意是两个 L）
- 确认文件位于 `.agents/skills/` 或 vendor 技能目录下
- 检查目录名是否在 `.validate-skip` 跳过列表中
- 使用 `--force --verbose` 强制全量扫描并查看详细日志

**Q: strict 模式下显示 Warning"缺少推荐章节"？**
- 确保正文中包含以下关键词对应的章节：
  - "输入"/"参数"、"依赖"、"部署"/"安装"、"错误"、"版本记录"/"变更"
- 关键词大小写不敏感，章节标题或正文中出现即可
- 如暂时不需要完整文档，可使用 `--mode relaxed` 跳过此检查

**Q: 提示名称冲突？**
- 两个不同的 SKILL.md 使用了相同的 `name` 字段
- 修改其中一个技能的 name 确保唯一

**Q: typer 未安装有什么影响？**
- 自动回退到 argparse，功能完全一致
- 仅缺少 typer 提供的彩色帮助和自动补全
- 可正常使用所有参数

## 10. 版本记录（Changelog）

- **v0.1.0** (2026-08-07): 初始版本，实现 SKILL.md 技能门面。包含 CLI 完整功能：双目录自动扫描（vendor/local）、YAML/TOML frontmatter 解析、strict/relaxed 双验证模式、增量缓存、名称冲突检测、JSON+Markdown 双格式报告输出。
