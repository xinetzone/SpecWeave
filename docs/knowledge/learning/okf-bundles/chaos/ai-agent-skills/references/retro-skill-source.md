---
type: Reference
title: retro-skill 源码
description: Retro Skill v1.6.0 源码登记，含六种模式、五层流水线、21机械信号、七目标路由与8个脚本
tags: [agent-skills, retro, source, reference, introspection, plugin]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts-retro-skill
    resource: "/references/facts-retro-skill.md"
    title: retro-skill 事实清单
---

# retro-skill 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 项目名 | retro-skill |
| 版本 | 1.6.0 |
| 作者 | Netresearch DTT GmbH |
| 许可证 | 代码 MIT，内容 CC-BY-SA-4.0（双许可证） |
| 源码路径 | `d:\AI\.chaos\libs\tests\retro-skill\` |
| 技能名称 | `retro` |
| 定位 | LLM 驱动的会话复盘技能，检测摩擦点并将学习成果路由到七个目标位置 |

## 插件结构

```text
retro-skill/
├── plugin.json                     # 插件元数据
├── commands/
│   └── retro.md                    # /retro 命令定义（10 阶段流程）
├── hooks/
│   └── session-end.json            # 可选的 SessionEnd 自动触发钩子
└── skills/retro/
    ├── SKILL.md                    # 技能主入口
    ├── checkpoints.yaml            # 质量门控（RT-01 至 RT-42）
    ├── references/                 # 9 个参考文档
    ├── scripts/                    # 8 个脚本
    └── evals/                      # 15 个评估场景
```

## SKILL.md frontmatter

```yaml
---
name: retro
description: [...]
license: MIT
compatibility: [...]
metadata:
  author: Netresearch DTT GmbH
  version: 1.6.0
  repository: https://github.com/...
allowed-tools:
  - Bash(python3:*)
  - Bash(gh:*)
  - Bash(glab:*)
  - Bash(git:*)
  - Bash(find:*)
  - Bash(grep:*)
  - Bash(jq:*)
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Task
---
```

## 六种运行模式

| 模式 | 触发方式 | 用途 | Token 成本 |
|------|---------|------|-----------|
| Sweep | `/retro` | 分析整个当前会话 | 最高 |
| Spotlight | `/retro "<problem>"` | 聚焦单个问题 | 低 |
| Outcome | `/retro outcome` | 事后复盘过去会话输出（需等待 24 小时以上） | 中 |
| Audit | `/retro audit` | 跨会话架构审查，检测架构漂移和约定侵蚀 | 高 |
| Promote | `/retro promote` | 清点本地记忆库存并向上迁移 | 中 |
| Auto | SessionEnd 钩子 | 自动触发（默认关闭，仅打印提醒，仅 >1000 字会话） | 最低 |

## 七个目标位置

| 目标 | 用途 |
|------|------|
| `canonical-source` | 事实的规范所有者在代理系统之外（上游文档、代码、模式） |
| `personal-rule` | 规则追加到 `~/.claude/CLAUDE.md`（旧名 user-memory 仍作别名有效） |
| `project-rule` | 项目级规则 |
| `skill-update` | 对技能的源仓库开 PR，绝不修改插件缓存 |
| `new-skill` | 建议创建新技能 |
| `checkpoint` | 向目标技能的 checkpoints.yaml 添加 YAML 条目 |
| `harness-artefact` | 通过 agent-harness 引导钩子/CI/模板 |

## 五层流水线（Schicht A-E）

10 个阶段：机械预检 → LLM 增强 → 跨会话增强 → 分类 → 技能发现 → 评估咨询 → 提案生成 → 审批 → 物化 → 报告。

| 层级 | 实现 | 信号数 | 说明 |
|------|------|--------|------|
| Schicht A | `detect-mechanical.py` | A1-A20 + C6 = 21 | 确定性信号，不做分类，不依赖 LLM |
| Schicht B | LLM 增强 | 14 个推断信号 | 过滤 A 层误报 |
| Schicht C | `scan-cross-session.py` | 5 个信号 | 跨会话模式检测（可选） |
| Schicht D | Outcome 模式 | D1-D12 | 失败、持久成功、取代的临时副本 |
| Schicht E | 评估咨询 | — | 评估验证器集成 |

效率目标：每次 /retro 仅 1 次 LLM 传递，detect-mechanical.py 仅调用 1 次，技能发现工具调用 ≤5。

## detect-mechanical.py 信号函数

通过 `SIGNAL_FUNCS` 字典注册的 21 个信号：

| 信号 ID | 函数 | 检测内容 |
|---------|------|---------|
| A1 | `signal_tool_errors` | 工具错误（信任 harness is_error 标志） |
| A2 | `signal_retry_clusters` | 重试簇 |
| A3 | `signal_verbose_results` | 冗余输出 |
| A4 | `signal_tool_count_vs_task` | 工具调用数与任务不匹配 |
| A5 | `signal_sequential_parallelizable` | 可并行的串行调用 |
| A6 | `signal_user_corrections` | 用户纠正短语（英语/德语） |
| A7 | `signal_prompt_repetition` | 提示词重复 |
| A8 | `signal_prompt_sequence_repetition` | 提示词序列重复 |
| A9 | `signal_tool_sequence_repetition` | 工具序列重复 |
| A10 | `signal_skill_reminder_vs_invoke` | 技能提醒与实际调用不符 |
| A11 | `signal_wrong_tool_choice` | 结构化文件工具误用（grep/sed/awk 操作 json/yaml，cat/head/tail 代替 Read） |
| A12 | `signal_reread_same_file` | 重复读取同一文件 |
| A13 | `signal_skipped_verification` | 跳过验证 |
| A14 | `signal_main_branch_work` | 在 main/master 上提交/推送（通过 git_segments() 避免误匹配） |
| A15 | `signal_bot_attribution` | 机器人署名 |
| A16 | `signal_outdated_tool` | 过时工具调用 |
| A17 | `signal_upstream_failure` | 上游失败 |
| A18 | `signal_permission_reapproval` | 同命令前缀 ≥3 次权限重审批 |
| A19 | `signal_repeated_probe` | 重复命令形状 ≥8 次，提示包装为脚本 |
| A20 | `signal_wait_loop_inefficiency` | 等待循环低效 |
| C6 | `signal_rule_exists_but_violated` | 已写规则被反复违反 ≥3 次，建议机械门控 |

关键辅助函数：`split_segments()`（引用感知 shell 分割）、`peel_to_program()`（去除包装器）、`git_segments()`（git 命令解析）、`command_shapes()`、`shape_of()`、`shape_histogram()`、`load_jsonl()`、`extract_user_texts()`、`extract_assistant_texts()`、`extract_tool_uses()`。

CLI 参数：`--transcript-file`（必需）、`--output-format`（json/text）、`--signals`（逗号分隔信号 ID）。

## 其他脚本（scripts/）

| 脚本 | 职责 |
|------|------|
| `scan-cross-session.py` | Schicht C 跨会话数据源，支持 --pattern 和 --user-correction-summary 模式；含 `session_files()`、`extract_user_texts()`、`cmd_pattern()`、`cmd_correction_summary()` |
| `scan-memory-inventory.py` | Promote 模式前端，扫描本地记忆库存；含 `_parse_frontmatter()`（无 pyyaml 依赖）、drain 子命令（移动到 .promoted/ 墓碑目录，从不删除） |
| `find-installed-skills.sh` | 发现已安装技能 |
| `find-org-skills.py` | 发现组织技能 |
| `check-upstream-sources.py` | 检查上游来源 |
| `materialize-pr.sh` | 物化 PR（补丁工作流） |
| `validate-evals.py` | 验证评估场景（≥5 个且格式良好） |

## references/ 目录（9 篇）

friction-catalog、destination-taxonomy、classification-heuristic、skill-discovery、patch-workflow、eval-integration、promote-mode、workflow、project-harness-inspection。

## 分类启发式（三轴）

- **Axis 0 权威性**：谁拥有这个真相。技能仅作为代理行为和自身流程的规范来源；外部事实路由到 canonical-source。
- **Axis 1 可执行性**：机械门控（最强）→ LLM 审查 → 散文指令（最弱）。
- **Axis 2 覆盖面**：升级顺序为 skill-update/new-skill → project-rule → personal-rule，禁止项目本地记忆。

严重性分级：critical（反复发生/上游失败/用户可见 bug）、important（用户纠正/违规/可复用学习）、nice-to-have。

## checkpoints.yaml 质量门控

| 检查点 | 验证内容 |
|--------|---------|
| 前置条件 | python3 可用（`python3 --version`） |
| RT-01~RT-05 | SKILL.md、commands/retro.md、detect-mechanical.py 存在且 Python 语法有效 |
| RT-07 | 单元测试套件（`python3 -m unittest discover -s tests -q`） |
| RT-10~RT-11 | 核心参考文档和工作流参考文档存在 |
| RT-40~RT-42 | 评估验证器脚本存在、语法有效、评估场景 ≥5 个且格式良好 |

## 安全与边界

- 补丁始终指向源仓库，绝不指向 `~/.claude/plugins/cache/`
- 禁止自动合并、机器人署名、--no-verify、修补缓存、硬编码静态技能列表
- PR 使用 Conventional Commits 并需要 DCO 签名（`git commit -s`）
- 每个私有仓库目标需要逐仓库确认
- 核心原则："No silent writes"——每次物化都需要逐提案审批
