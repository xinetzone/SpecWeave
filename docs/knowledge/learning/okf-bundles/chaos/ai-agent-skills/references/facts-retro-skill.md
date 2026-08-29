# retro-skill 事实清单

> R阶段事实采集。源码路径：d:\AI\.chaos\libs\tests\retro-skill\
> 采集日期：2026-08-23

## 项目概述

- F-001: retro-skill 是一个 LLM 驱动的会话复盘技能，用于在 Claude Code 会话结束后检测摩擦点并将学习成果路由到七个目标位置 — 源码：`README.md:3`
- F-002: 单次扫描最多返回 10 条可操作建议，按目标位置分组，每条包含 Why 和 How-to-apply — 源码：`README.md:33`
- F-003: 项目采用双许可证：代码 MIT，内容 CC-BY-SA-4.0 — 源码：`README.md:254`
- F-004: 由 Netresearch DTT GmbH 维护 — 源码：`README.md:256`

## SKILL.md 结构

- F-005: SKILL.md frontmatter 包含 name、description、license、compatibility、metadata（author/version/repository）、allowed-tools 字段 — 源码：`skills/retro/SKILL.md:1-11`
- F-006: 技能名称为 `retro`，版本为 `1.6.0` — 源码：`skills/retro/SKILL.md:2,8`
- F-007: allowed-tools 声明了 Bash(python3:*)、Bash(gh:*)、Bash(glab:*)、Bash(git:*)、Bash(find:*)、Bash(grep:*)、Bash(jq:*)、Read、Write、Edit、Glob、Grep、Task — 源码：`skills/retro/SKILL.md:10`
- F-008: SKILL.md 定义了六种模式：Sweep、Spotlight、Outcome、Audit、Promote、Auto — 源码：`skills/retro/SKILL.md:26-35`
- F-009: 核心原则是"No silent writes"——每次物化都需要逐提案审批 — 源码：`skills/retro/SKILL.md:19-20`
- F-010: SKILL.md 的 References 表引用了 8 个参考文档：friction-catalog、destination-taxonomy、classification-heuristic、skill-discovery、patch-workflow、eval-integration、promote-mode、workflow — 源码：`skills/retro/SKILL.md:70-79`

## 五种运行模式

- F-011: Sweep 模式（`/retro`）分析整个当前会话，Token 成本最高 — 源码：`skills/retro/references/workflow.md:7-21`
- F-012: Spotlight 模式（`/retro "<problem>"`）聚焦单个问题，Token 成本低 — 源码：`skills/retro/references/workflow.md:23-39`
- F-013: Outcome 模式（`/retro outcome`）事后复盘过去会话的输出结果，需等待 24 小时以上运行 — 源码：`skills/retro/references/workflow.md:41-57`
- F-014: Audit 模式（`/retro audit`）跨会话架构审查，检测架构漂移和约定侵蚀 — 源码：`skills/retro/references/workflow.md:59-85`
- F-015: Promote 模式（`/retro promote`）清点已写入的本地记忆库存并将其向上迁移 — 源码：`skills/retro/references/workflow.md:87-101`
- F-016: Auto 模式通过可选的 SessionEnd 钩子触发，默认关闭，仅打印提醒 — 源码：`skills/retro/references/workflow.md:103-114`

## 七个目标位置（Seven Destinations）

- F-017: 七个目标位置分别为 canonical-source、personal-rule、project-rule、skill-update、new-skill、checkpoint、harness-artefact — 源码：`README.md:117-125`
- F-018: canonical-source 用于事实的规范所有者在代理系统之外的场景（上游文档、代码、模式） — 源码：`README.md:119`
- F-019: personal-rule 将规则追加到 `~/.claude/CLAUDE.md`（旧名 user-memory 仍作为输入别名有效） — 源码：`README.md:120,127`
- F-020: skill-update 对技能的源仓库开 PR，绝不修改插件缓存 — 源码：`README.md:122`
- F-021: checkpoint 向目标技能的 checkpoints.yaml 添加 YAML 条目 — 源码：`README.md:124`
- F-022: harness-artefact 通过 agent-harness 引导钩子/CI/模板 — 源码：`README.md:125`

## 流水线架构（分层 Schicht A/B/C/D/E）

- F-023: 流水线分为 10 个阶段：机械预检→LLM 增强→跨会话增强→分类→技能发现→评估咨询→提案生成→审批→物化→报告 — 源码：`README.md:133-142`
- F-024: Schicht A（机械预检）由 detect-mechanical.py 实现，检测 18 个确定性信号（A1-A18），不做分类 — 源码：`README.md:133`
- F-025: Schicht B（LLM 增强）添加 14 个推断信号并过滤 A 层误报 — 源码：`README.md:134`
- F-026: Schicht C（跨会话增强，可选）由 scan-cross-session.py 实现，检测 5 个信号 — 源码：`README.md:135`
- F-027: 分类阶段按"权威优先"原则映射到七个目标位置 — 源码：`README.md:136`
- F-028: 效率目标：每次 /retro 仅 1 次 LLM 传递，detect-mechanical.py 仅调用 1 次，技能发现工具调用 ≤5 — 源码：`skills/retro/references/workflow.md:238-240`

## 分类启发式（classification-heuristic.md）

- F-029: 分类使用三个轴：Axis 0 权威性（谁拥有这个真相）、Axis 1 可执行性（门控优先于句子）、Axis 2 覆盖面（最广泛的有用目标） — 源码：`skills/retro/references/classification-heuristic.md:62-66`
- F-030: Axis 0 规定技能仅作为代理行为和自身流程的规范来源；外部事实路由到 canonical-source — 源码：`skills/retro/references/classification-heuristic.md:81-86`
- F-031: Axis 1 分三层：机械门控（最强）→LLM 审查→散文指令（最弱） — 源码：`skills/retro/references/classification-heuristic.md:123-133`
- F-032: Axis 2 升级顺序为 skill-update/new-skill → project-rule → personal-rule，禁止项目本地记忆 — 源码：`skills/retro/references/classification-heuristic.md:211-224`
- F-033: 严重性分级：critical（反复发生/上游失败/用户可见 bug）、important（用户纠正/违规/可复用学习）、nice-to-have — 源码：`skills/retro/references/classification-heuristic.md:284-286`
- F-034: 指令修剪是有效的 skill-update——移除过时、过宽、重复或矛盾的指令 — 源码：`skills/retro/references/classification-heuristic.md:231-259`

## checkpoints.yaml 质量门控

- F-035: checkpoints.yaml 版本为 1，skill_id 为 retro — 源码：`skills/retro/checkpoints.yaml:1-2`
- F-036: 前置条件检查 python3 可用（`python3 --version`） — 源码：`skills/retro/checkpoints.yaml:4-7`
- F-037: RT-01 至 RT-05 验证 SKILL.md、commands/retro.md、detect-mechanical.py 存在且 Python 语法有效 — 源码：`skills/retro/checkpoints.yaml:9-38`
- F-038: RT-07 运行单元测试套件（`python3 -m unittest discover -s tests -q`） — 源码：`skills/retro/checkpoints.yaml:40-44`
- F-039: RT-10 和 RT-11 验证核心参考文档和工作流参考文档存在 — 源码：`skills/retro/checkpoints.yaml:52-62`
- F-040: RT-40 至 RT-42 验证评估验证器脚本存在、语法有效、且评估场景 ≥5 个且格式良好 — 源码：`skills/retro/checkpoints.yaml:82-98`

## detect-mechanical.py 脚本

- F-041: detect-mechanical.py 是 Schicht A 机械摩擦检测器，读取 JSONL 会话记录并输出 JSON 格式的候选发现 — 源码：`skills/retro/scripts/detect-mechanical.py:1-6`
- F-042: 实现了 A1-A20 和 C6 共 21 个信号检测函数，通过 SIGNAL_FUNCS 字典注册 — 源码：`skills/retro/scripts/detect-mechanical.py:1453-1475`
- F-043: A1 检测工具错误，信任 harness is_error 标志，文本回退使用 A1_ERROR_MARKER 和 A1_BENIGN 正则排除良性输出 — 源码：`skills/retro/scripts/detect-mechanical.py:705-723`
- F-044: A6 检测用户纠正短语，支持英语和德语，包括行首纠正词和强纠正短语 — 源码：`skills/retro/scripts/detect-mechanical.py:48-65,765-795`
- F-045: A11 检测结构化文件上的工具误用（grep/sed/awk 操作 json/yaml 等）和 cat/head/tail 代替 Read — 源码：`skills/retro/scripts/detect-mechanical.py:1166-1246`
- F-046: A14 通过跟踪分支状态检测在 main/master 上的提交/推送，使用 git_segments() 避免误匹配数据中的字符串 — 源码：`skills/retro/scripts/detect-mechanical.py:938-990`
- F-047: A18 检测同一 Bash 命令前缀出现 ≥3 次且间隔分散的权限重新审批候选 — 源码：`skills/retro/scripts/detect-mechanical.py:1289-1332`
- F-048: A19 检测重复命令形状（≥8 次），提示包装为脚本 — 源码：`skills/retro/scripts/detect-mechanical.py:1335-1371`
- F-049: A20 检测等待循环低效——等待所有检查完成而非第一个可操作事件 — 源码：`skills/retro/scripts/detect-mechanical.py:1374-1413`
- F-050: C6 检测已写规则被反复违反（≥3 次），建议机械门控而非另一条散文规则 — 源码：`skills/retro/scripts/detect-mechanical.py:1416-1450`
- F-051: 命令形状分析通过 split_segments() 实现引用感知的 shell 分割，peel_to_program() 去除包装器 — 源码：`skills/retro/scripts/detect-mechanical.py:430-520,571-589`
- F-052: 脚本支持 --transcript-file（必需）、--output-format（json/text）、--signals（逗号分隔信号 ID）参数 — 源码：`skills/retro/scripts/detect-mechanical.py:1478-1487`

## scan-cross-session.py 脚本

- F-053: scan-cross-session.py 是 Schicht C 跨会话数据源，扫描 JSONL 文件查找相似摩擦模式 — 源码：`skills/retro/scripts/scan-cross-session.py:1-6`
- F-054: 支持两种模式：--pattern 搜索关键词/短语，--user-correction-summary 汇总纠正模式 — 源码：`skills/retro/scripts/scan-cross-session.py:9-10`
- F-055: session_files() 函数返回最近 N 天内的 (jsonl_path, project_slug) 列表 — 源码：`skills/retro/scripts/scan-cross-session.py:30-50`
- F-056: extract_user_texts() 从 JSONL 中提取 type=user 的文本内容 — 源码：`skills/retro/scripts/scan-cross-session.py:53-77`
- F-057: cmd_pattern() 按项目分组匹配项，每个会话最多记录一次命中 — 源码：`skills/retro/scripts/scan-cross-session.py:80-105`
- F-058: cmd_correction_summary() 使用 CORRECTION_PATTERNS 正则检测纠正短语，输出跨项目和各项目前 5 条 — 源码：`skills/retro/scripts/scan-cross-session.py:108-138`

## scan-memory-inventory.py 脚本

- F-059: scan-memory-inventory.py 是 /retro promote 模式的前端，扫描本地记忆库存文件而非会话记录 — 源码：`skills/retro/scripts/scan-memory-inventory.py:1-12`
- F-060: 默认扫描所有项目 slug 下的 memory/ 目录，不仅限当前项目 — 源码：`skills/retro/scripts/scan-memory-inventory.py:20-21,60-77`
- F-061: 每个发现携带 C3（memory_drift）信号、content_sha256（幂等键和排空竞争检查） — 源码：`skills/retro/scripts/scan-memory-inventory.py:14-18,153-166`
- F-062: 支持 --include-flagged-locations 检测已弃用的项目本地规则存储（CLAUDE.md、docs/feedback/），发出 B8 信号 — 源码：`skills/retro/scripts/scan-memory-inventory.py:169-200`
- F-063: 支持 --include-global-rules 扫描全局规则文件的 `## ` 节，发出 C2 跨项目模式信号 — 源码：`skills/retro/scripts/scan-memory-inventory.py:203-263`
- F-064: drain 子命令将源文件移动到 .promoted/ 墓碑目录（从不删除），并修剪 MEMORY.md 索引 — 源码：`skills/retro/scripts/scan-memory-inventory.py:360-440`
- F-065: drain 验证路径必须在 <memory-root>/<slug>/memory/ 内，并支持 --expect-sha256 竞争检查 — 源码：`skills/retro/scripts/scan-memory-inventory.py:370-392`
- F-066: _parse_frontmatter() 是无依赖的 YAML frontmatter 解析器（不使用 pyyaml） — 源码：`skills/retro/scripts/scan-memory-inventory.py:80-113`

## commands/retro.md 命令定义

- F-067: /retro 命令 frontmatter 仅包含 description 字段 — 源码：`commands/retro.md:1-3`
- F-068: 命令定义了 10 个阶段的详细执行流程，从机械预检到报告 — 源码：`commands/retro.md:30-199`
- F-069: 阶段 5（技能发现）必须在分类之前运行，发现所有已安装和可用的技能 — 源码：`commands/retro.md:106-135`
- F-070: 阶段 7 要求技能更新提案包含 Skill instruction delta（当前指令、建议编辑、边界说明） — 源码：`commands/retro.md:157-162`
- F-071: 阶段 8 拒绝的技能更新编辑记录到 `~/.claude/retro/rejected-edits.md` 以避免重复提议 — 源码：`commands/retro.md:175-177`
- F-072: Outcome 模式检测 Schicht D 信号 D1-D12，包括失败、持久成功和取代的临时副本 — 源码：`commands/retro.md:217-244`
- F-073: Promote 模式替换阶段 1 为 scan-memory-inventory.py，跳过阶段 2/2b/3/3b/3c，阶段 9 增加"物化后排空"步骤 — 源码：`commands/retro.md:260-294`

## 安全与边界

- F-074: 补丁始终指向源仓库，绝不指向 `~/.claude/plugins/cache/` — 源码：`README.md:149`
- F-075: 禁止自动合并、机器人署名、--no-verify、修补缓存、硬编码静态技能列表 — 源码：`README.md:151`
- F-076: PR 使用 Conventional Commits 并需要 DCO 签名（`git commit -s`），无签名 PR 被阻止 — 源码：`README.md:141`
- F-077: 每个私有仓库目标需要逐仓库确认 — 源码：`skills/retro/SKILL.md:62`

## 仓库结构

- F-078: skills/retro/ 是自包含技能子树，包含 SKILL.md、checkpoints.yaml、references/（7 个参考文档）、evals/、scripts/ — 源码：`README.md:197-216`
- F-079: references/ 目录包含 friction-catalog.md、destination-taxonomy.md、classification-heuristic.md、skill-discovery.md、patch-workflow.md、eval-integration.md、workflow.md — 源码：`README.md:202-208`
- F-080: scripts/ 目录包含 detect-mechanical.py、find-installed-skills.sh、scan-cross-session.py、validate-evals.py — 源码：`README.md:213-216`
- F-081: hooks/session-end.json 是可选的自动触发钩子，默认关闭，仅对超过 1000 字的会话打印提醒 — 源码：`README.md:166-170`
