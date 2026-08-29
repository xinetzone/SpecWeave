---
type: Concept
title: Retro Skill 自省与演进模式
description: retro-skill v1.6.0 的六种复盘模式、五层流水线、21个机械信号检测、七目标路由分类法与No silent writes安全原则
tags: [agent-skills, retro, introspection, friction-detection, mechanical-signals, classification]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: retro-skill-source
    resource: "/references/retro-skill-source.md"
    title: retro-skill 源码
---

# Retro Skill 自省与演进模式

retro-skill（v1.6.0）是一个 LLM 驱动的会话复盘技能，它让 AI 在工作结束后审查自己的工作过程，检测摩擦点（friction），并将学习成果路由到正确的位置。其核心设计哲学是"机械优先、LLM 兜底、人工审批物化"，通过 21 个确定性信号、五层流水线和七目标分类法，实现了 AI 代理的自省与持续演进。

## 核心理念：No Silent Writes

retro-skill 的第一原则是 **"No silent writes"**——每次物化（将学习成果写入文件/创建 PR/修改配置）都需要逐提案人工审批。AI 可以自动检测问题、分析原因、生成改进提案，但不能自动执行任何持久化修改。这一原则贯穿所有模式和流水线阶段。

安全边界还包括：
- 补丁始终指向源仓库，绝不指向 `~/.claude/plugins/cache/`
- 禁止自动合并、机器人署名、`--no-verify`
- PR 使用 Conventional Commits 并需要 DCO 签名（`git commit -s`）
- 每个私有仓库目标需要逐仓库确认

## 六种运行模式

| 模式 | 触发 | 分析范围 | Token 成本 | 等待要求 |
|------|------|---------|-----------|---------|
| **Sweep** | `/retro` | 整个当前会话 | 最高 | 无 |
| **Spotlight** | `/retro "<problem>"` | 单个问题 | 低 | 无 |
| **Outcome** | `/retro outcome` | 过去会话的输出结果 | 中 | 24 小时以上 |
| **Audit** | `/retro audit` | 跨会话架构审查 | 高 | 多个会话 |
| **Promote** | `/retro promote` | 本地记忆库存 | 中 | 无 |
| **Auto** | SessionEnd 钩子 | 仅打印提醒 | 最低 | 会话 >1000 字 |

### Sweep vs Spotlight

- **Sweep** 分析完整会话记录，检测所有类型的摩擦信号，适合会话结束后的全面复盘
- **Spotlight` 聚焦用户指定的单个问题，Token 成本低，适合针对特定困难点快速获取改进建议

### Outcome（事后复盘）

Outcome 模式需要等待 24 小时以上运行，因为它检测的是 Schicht D 信号（D1-D12），包括：
- 失败的结果
- 持久成功的结果
- 被取代的临时副本

时间延迟让 AI 能区分"看起来成功"和"真正成功"。

### Audit（架构审查）

跨会话检测架构漂移和约定侵蚀，不局限于单次会话的摩擦，而是识别反复出现的系统性问题。

### Promote（记忆迁移）

清点已写入的本地记忆库存（memory/ 目录）并将其向上迁移到更广泛的目标位置（从个人规则到项目规则到技能更新）。此模式使用 `scan-memory-inventory.py` 替代标准流水线的阶段 1。

### Auto（自动提醒）

通过 `hooks/session-end.json` 在会话结束时触发。默认关闭，即使启用也仅对超过 1000 字的会话打印提醒——**不自动执行复盘**，遵守 No silent writes。

## 五层流水线（Schicht A-E）

retro-skill 的复盘流水线分为 10 个阶段，按数据源和处理方式分为五层：

```text
阶段 1：机械预检（Schicht A）
  └── detect-mechanical.py 检测 21 个确定性信号
阶段 2：LLM 增强（Schicht B）
  └── 添加 14 个推断信号，过滤 A 层误报
阶段 2b：跨会话增强（Schicht C，可选）
  └── scan-cross-session.py 检测 5 个跨会话信号
阶段 3：分类
  └── 按三轴启发式路由到七个目标位置
阶段 4：技能发现
  └── 发现已安装和可用技能（必须在分类前运行）
阶段 5：评估咨询（Schicht E）
  └── 评估验证器集成
阶段 6：提案生成
  └── 生成具体改进提案
阶段 7：审批
  └── 逐提案人工审批
阶段 8：物化
  └── 将批准的提案写入目标位置
阶段 9：报告
  └── 输出复盘报告
```

效率目标：每次 /retro 仅 1 次 LLM 传递，detect-mechanical.py 仅调用 1 次，技能发现工具调用 ≤5。

## 21 个机械信号（Schicht A）

`detect-mechanical.py` 实现了 21 个通过 `SIGNAL_FUNCS` 字典注册的确定性信号检测函数。这些信号不依赖 LLM，使用正则、shell 解析和状态跟踪。

### 信号分组

| 分组 | 信号 ID | 检测内容 |
|------|---------|---------|
| 工具问题 | A1, A2, A3, A10, A16, A17 | 工具错误、重试簇、冗余输出、技能提醒未调用、过时工具、上游失败 |
| 用户纠正 | A6 | 纠正短语（支持英语和德语，含行首纠正词和强纠正短语） |
| 重复低效 | A7, A8, A9, A12, A18, A19, A20 | 提示词重复、序列重复、重复读文件、权限重审批、重复命令、等待循环 |
| 工具误用 | A11 | grep/sed/awk 操作 JSON/YAML，cat/head/tail 代替 Read |
| 流程违规 | A14, A15 | 在 main/master 上提交、机器人署名 |
| 任务匹配 | A4, A5, A13 | 工具数与任务不匹配、可并行串行化、跳过验证 |
| 规则违反 | C6 | 已写规则被反复违反 ≥3 次，建议机械门控 |

### 关键信号实现

**A1（工具错误）**：信任 harness 的 `is_error` 标志；文本回退使用 `A1_ERROR_MARKER` 和 `A1_BENIGN` 正则排除良性输出。

**A6（用户纠正）**：支持英语和德语双语检测，包括行首纠正词和强纠正短语。

**A11（工具误用）**：检测两类反模式：
1. 用 grep/sed/awk 操作结构化文件（JSON/YAML）——应使用专门的 JSON/YAML 工具
2. 用 cat/head/tail 读取文件——应使用 Read 工具

**A14（主分支工作）**：通过跟踪分支状态检测在 main/master 上的提交/推送。使用 `git_segments()` 解析 git 命令，避免误匹配数据中的字符串。

**A18（权限重审批）**：检测同一 Bash 命令前缀出现 ≥3 次且间隔分散的情况，提示用户可预授权。

**A19（重复探测）**：检测重复命令形状 ≥8 次，提示将重复操作包装为脚本。

**A20（等待循环低效）**：检测等待所有检查完成而非等待第一个可操作事件的低效模式。

**C6（规则存在但被违反）**：检测已写规则被反复违反 ≥3 次，建议机械门控而非另一条散文规则。

### Shell 解析基础设施

信号检测依赖两个关键的命令解析函数：

- `split_segments(cmd)`：引用感知的 shell 分割，正确处理引号和转义
- `peel_to_program(toks)`：去除包装器（如 `sudo`、`time`、`nohup`），提取核心命令
- `git_segments(cmd)`：专门解析 git 命令的子命令和参数
- `command_shapes(cmd)` / `shape_of(name, inp)`：生成命令形状（去除具体参数后的模式）

### CLI 接口

```bash
# 分析会话记录
python detect-mechanical.py --transcript-file session.jsonl

# 指定输出格式
python detect-mechanical.py --transcript-file session.jsonl --output-format text

# 仅运行特定信号
python detect-mechanical.py --transcript-file session.jsonl --signals A1,A6,A14
```

## 七个目标位置

分类阶段将每个发现路由到七个目标位置之一：

| 目标 | 用途 | 物化方式 |
|------|------|---------|
| `canonical-source` | 事实的规范所有者在代理系统之外（上游文档、代码） | 指向外部，不直接修改 |
| `personal-rule` | 个人行为规则 | 追加到 `~/.claude/CLAUDE.md`（旧名 user-memory 仍作别名） |
| `project-rule` | 项目级规则 | 项目配置文件 |
| `skill-update` | 技能指令改进 | 对技能源仓库开 PR |
| `new-skill` | 需要新技能 | 创建新技能提案 |
| `checkpoint` | 质量门控改进 | 向目标技能的 checkpoints.yaml 添加条目 |
| `harness-artefact` | 工具链改进 | 通过 agent-harness 引导钩子/CI/模板 |

## 三轴分类启发式

分类使用三个正交轴确定最佳目标位置：

### Axis 0：权威性（谁拥有这个真相）

- 技能仅作为**代理行为和自身流程**的规范来源
- 外部事实（API 文档、业务规则）路由到 `canonical-source`
- 这防止了技能越权声明外部真相的所有权

### Axis 1：可执行性（门控优先于句子）

三层执行力，从强到弱：
1. **机械门控**（最强）：checkpoints.yaml、pre-commit hooks、CI 检查
2. **LLM 审查**：技能指令中的条件判断
3. **散文指令**（最弱）：文档中的建议性文字

当一条规则被反复违反（C6 信号），应升级到更强的门控层，而非添加更多散文。

### Axis 2：覆盖面（最广泛的有用目标）

升级顺序（从窄到宽）：
```text
skill-update / new-skill → project-rule → personal-rule
```

- 可复用的学习应进入技能（所有用户受益）
- 项目特定的约定进入项目规则
- 个人偏好进入个人规则
- **禁止项目本地记忆**（避免知识被困在单个项目中）

### 严重性分级

| 级别 | 判定条件 |
|------|---------|
| critical | 反复发生、上游失败、用户可见 bug |
| important | 用户纠正、违规、可复用学习 |
| nice-to-have | 改进建议但非紧急 |

### 指令修剪

移除过时、过宽、重复或矛盾的指令被视为有效的 skill-update。这意味着 retro-skill 不仅建议添加规则，还建议删除无效规则。

## Promote 模式与记忆库存

`scan-memory-inventory.py` 是 Promote 模式的前端，扫描本地记忆库存而非会话记录：

- 默认扫描所有项目 slug 下的 `memory/` 目录（不仅限当前项目）
- 每个发现携带 C3（memory_drift）信号和 `content_sha256`（幂等键和排空竞争检查）
- `--include-flagged-locations` 检测已弃用的项目本地规则存储（CLAUDE.md、docs/feedback/），发出 B8 信号
- `--include-global-rules` 扫描全局规则文件的 `## ` 节，发出 C2 跨项目模式信号

### drain 子命令

将源文件移动到 `.promoted/` 墓碑目录（**从不删除**），并修剪 MEMORY.md 索引：
- 验证路径必须在 `<memory-root>/<slug>/memory/` 内
- 支持 `--expect-sha256` 竞争检查（防止迁移期间文件被修改）
- 使用 `_parse_frontmatter()` —— 无 pyyaml 依赖的自研 YAML frontmatter 解析器

## checkpoints.yaml 质量门控

| 检查点 | 验证内容 |
|--------|---------|
| 前置 | `python3 --version` 可用 |
| RT-01~RT-05 | SKILL.md、commands/retro.md、detect-mechanical.py 存在且 Python 语法有效 |
| RT-07 | 单元测试通过（`python3 -m unittest discover -s tests -q`） |
| RT-10~RT-11 | 核心参考文档和工作流文档存在 |
| RT-40~RT-42 | 评估验证器存在、语法有效、评估场景 ≥5 个且格式良好 |

## 脚本清单

| 脚本 | 职责 |
|------|------|
| `detect-mechanical.py` | Schicht A 机械信号检测（21 个信号） |
| `scan-cross-session.py` | Schicht C 跨会话模式检测（--pattern / --user-correction-summary） |
| `scan-memory-inventory.py` | Promote 模式前端，记忆库存扫描和 drain |
| `find-installed-skills.sh` | 发现已安装技能 |
| `find-org-skills.py` | 发现组织技能 |
| `check-upstream-sources.py` | 上游来源检查 |
| `materialize-pr.sh` | 物化 PR（补丁工作流） |
| `validate-evals.py` | 验证评估场景格式和数量 |

## 设计启示

1. **机械优先**：用确定性规则覆盖可量化的摩擦信号，LLM 仅处理模糊判断——可预测、低成本、可审计。
2. **提案与执行分离**：AI 生成提案，人类审批物化——"No silent writes"是自动化安全的底线。
3. **知识路由有层级**：学习成果应路由到最广泛有用的位置（技能 > 项目 > 个人），避免知识孤岛。
4. **门控强于散文**：反复违反的规则需要机械门控（CI/hook），而非更多文档。
5. **信号有 ID 和函数名**：每个信号可独立选择、测试和追踪，注册字典模式便于扩展。

## 相关概念

- [插件架构（plugin.json/hooks/commands）](/concepts/05-plugin-architecture.md)
- [Skill 脚本工具模式](/concepts/10-skill-tooling-scripts.md)
- [多工具兼容与集成模式](/concepts/11-integration-patterns.md)
