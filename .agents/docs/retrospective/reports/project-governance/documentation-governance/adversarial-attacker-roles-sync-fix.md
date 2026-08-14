---
title: 对抗审查攻击者角色文档-代码不一致修复说明
date: 2026-07-28
type: bugfix
severity: medium
source: 一致性检查发现
status: 已完成（命令文档+wiki知识库全量同步）
commit: 20d79b8c
---

# 对抗审查攻击者角色文档-代码不一致修复说明

## 问题描述

对抗性审查命令文档（`adversarial-review.md`）中定义的攻击者角色列表与代码实现（`knowledge_adversarial.py`）中的 `ATTACKER_PROFILES` 不一致：

| 维度 | 文档（修复前） | 代码（SSOT） | 差异 |
|------|---------------|-------------|------|
| 角色数量 | 4个 | 5个 | 缺失1个 |
| 角色列表 | security/performance/boundary/timing | security/boundary/integrity/timing/fuzzer | ①performance不存在于代码；②缺失integrity和fuzzer |
| 性能攻击者 | 有🟡性能攻击者 | 无对应profile | 资源耗尽/并发归入timing，大输入归入fuzzer |
| 完整性攻击者 | 无 | 有🟠integrity | 校验和/元数据/Git历史攻击 |
| 模糊测试者 | 无 | 有🟣fuzzer | 随机/半随机异常输入 |

**根因**：代码在演化过程中将原来的"performance"角色重构拆分为"integrity"和"fuzzer"两个更细分的角色，同时将资源耗尽/大并发场景归入timing的攻击向量，但命令文档未同步更新。

## 修复内容

### 已修复（命令文档 adversarial-review.md）

共修改9处，文件：[adversarial-review.md](../commands/adversarial-review.md)

| 位置 | 修改内容 |
|------|---------|
| L27 场景速查表 | "安全/性能/边界/时序四个"→"安全/边界/完整性/时序/模糊测试五个" |
| L40 scope参数 | `performance`→`integrity`，新增`fuzzer`选项 |
| L42 attacker_roles参数 | `security/performance/boundary/timing`（四个）→`security/boundary/integrity/timing/fuzzer`（五个） |
| L82 核心原则 | "安全/性能/边界/时序"→"安全/边界/完整性/时序/模糊测试" |
| L182 步骤2标题 | "四大攻击者Agent"→"五大攻击者Agent" |
| L186-192 角色表 | 替换🟡性能攻击行为🟠完整性攻击者，新增🟣模糊测试者行；全部角色的攻击目标/攻击思路对齐代码中focus/attack_vectors定义 |
| L209 步骤4 | "四个攻击者"→"五个攻击者"；关联问题例子从"性能攻击者触发OOM"改为"模糊测试者的极端输入触发崩溃" |
| L249 验收标准 | "四大攻击者角色"→"五大攻击者角色" |
| L262 元审查 | "四大攻击者流程"→"五大攻击者流程" |

### 未修复（wiki知识库，待同步）

wiki知识库 [adversarial-review-wiki/](../docs/knowledge/learning/02-agent-engineering-methodology/adversarial-review-wiki/) 下共10个文件、40+处引用仍使用旧的"四大攻击者（安全/性能/边界/时序）"定义：

| 文件 | 旧引用数 | 说明 |
|------|---------|------|
| `01-core-concepts.md` | 3处 | 3.2.2角色定义章节 |
| `02-philosophy-origins.md` | 1处 | 红队思想借鉴描述 |
| `03-methodology-framework.md` | 5处 | 3.2角色详解、流程步骤表、架构模式引用 |
| `04-cognitive-biases-defense.md` | 4处 | 多视角对抗机制描述 |
| `05-checklists-templates.md` | 6处 | 3.1检查清单章节、Prompt模板、变更日志 |
| `08-practice-cases.md` | 7处 | AIHOT实战案例中"性能攻击者发现OOM"等历史记录 |
| `11-glossary.md` | 5处 | 安全/性能/边界/时序四个术语条目 |
| `12-resources.md` | 1处 | 资源索引描述 |
| `13-quick-reference.md` | 3处 | 快速参考流程、角色速查表 |
| `knowledge-graph-config.toml` | 2处 | 知识图谱节点配置 |
| `knowledge-graph.html` | 2处 | 生成的HTML图谱 |

**注意**：wiki中的实战案例（如AIHOT OOM案例）是历史记录，"性能攻击者发现"是当时实际使用的角色，不应机械替换为新角色名，需在更新时保留历史准确性（可加注释说明角色已演进）。

## wiki知识库同步完成（2026-07-28，commit 20d79b8c）

采用**版本涟漪Grep清扫模式+四分类处理策略**完成全量同步：

| 处理策略 | 文件数/引用数 | 说明 |
|---------|-------------|------|
| 🔧 机械替换(auto_replace) | 7文件/~20处 | 扫描脚本`--apply`模式批量替换：四大→五大、描述性文本更新 |
| 🏗️ 结构性调整(structural) | 5文件/11处 | 手动更新：角色定义表、检查清单、术语表、速查表、对比表 |
| 👀 历史保留(manual_review) | 1文件/10处 | AIHOT实战案例原文保留，文件头部添加"📜 角色演变注记（v1.0→v1.1）" |
| ⏭️ 跳过(skip) | 2生成产物 | knowledge-graph.html将随图谱重新生成，_scan_report.md自动清理 |

**验证结果**：
- 链接检查：111个本地引用全部通过
- 残留扫描：10处旧引用全部集中在08-practice-cases.md实战案例历史记录中（预期保留）
- 新增工具：[scan-adversarial-wiki.py](../../../../../scripts/scan-adversarial-wiki.py) 可复用扫描脚本

**模式沉淀**：本次案例将`version-ripple-grep-sweep`模式从L1升级为L2（validation_count=2），新增"内容四分类法"核心策略。

## 代码SSOT确认

代码定义位置：[knowledge_adversarial.py](../../../../../scripts/lib/knowledge_adversarial.py#L49-L115)

```python
ATTACKER_PROFILES: dict[str, AttackerProfile] = {
    "security":   # 安全攻击者：加密边界、密钥管理、认证绕过
    "boundary":   # 边界攻击者：路径遍历、文件大小、格式畸形
    "integrity":  # 完整性攻击者：校验和篡改、元数据污染、Git历史攻击
    "timing":     # 时序攻击者：并发冲突、超时、竞态条件
    "fuzzer":     # 模糊测试者：随机/半随机异常输入、边界值
}
```

## 验证方式

1. `python .agents/scripts/load-adversarial-addendum.py --check` — 补充文件完整性检查
2. `python .agents/scripts/check-links.py --path .agents/commands/adversarial-review.md` — 链接有效性检查
3. 文档内grep确认无遗漏"performance"/"四大攻击者"引用（wiki描述部分除外）

## 预防措施

此类文档-代码不一致的根因是：代码重构后未同步更新命令文档。建议：
- 后续修改 `ATTACKER_PROFILES` 时，同步检查 `adversarial-review.md` 的角色表和参数说明
- 考虑在CI中加入文档-代码一致性校验（如提取代码中的profile id列表与文档参数表做diff）
