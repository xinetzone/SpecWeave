---
id: "okf-wiki-usage-patterns"
title: "03 使用模式与最佳实践"
version: "1.0"
source: "okf.md spec + 实践经验总结"
type: "Wiki Tutorial"
description: "OKF三种典型使用场景、扩展字段最佳实践、自动化脚本、Git工作流结合"
tags: ["OKF", "使用场景", "最佳实践", "自动化", "Git工作流"]
category: "learning"
date: "2026-08-05"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "覆盖数据目录、Agent知识库、团队Runbook三种典型场景，详解扩展字段、链接设计、渐进式文档化、自动化脚本、Git集成等最佳实践"
last_verified: "2026-08-05"
wiki_version: "1.0"
okf_version_target: "v0.2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/03-usage-patterns.toml"
---

# 03 使用模式与最佳实践

## 3.1 三种典型使用场景

OKF是通用格式，实践中形成了三种典型模式。

### 3.1.1 场景1：数据目录（Data Catalog）

**适用**：数据团队文档化表、指标、字段、Pipeline、BI仪表盘。

**目录结构**：按业务领域分目录（`sales/`、`product/`、`infra/`）。

**典型type**：`BigQuery Table`、`Metric`、`dbt Model`、`Kafka Topic`、`Dashboard`

**核心字段**：`resource`指向实际资源链接，`timestamp`保持更新，`stale_after`标记新鲜度。

**示例**：DAU日活指标（约18行）
```markdown
---
title: "Daily Active Users (DAU)"
type: "Metric"
owner: data-team@company.com
resource: "https://bi.company.com/dashboards/dau"
timestamp: 2026-08-01
stale_after: P7D
tags: ["growth", "core-metric"]
---

# DAU 日活用户

## 定义
过去24小时内至少产生一次有效事件的去重用户数。

## 计算逻辑
`SELECT COUNT(DISTINCT user_id) FROM events WHERE ... AND event_type != 'test'`

## 相关
- [MAU](./mau.md) | [events表](../product/events.md)
```

**适用边界**：专业数据目录工具（dbt docs/DataHub）的轻量补充或上层入口索引。

---

### 3.1.2 场景2：Agent配套知识库（Agent Knowledge）

**适用**：为AI Agent提供工具文档、API说明、领域知识、操作规范。本Wiki Quickstart采用此场景。

**目录结构**：`tools/`、`concepts/`、`playbooks/`、`policies/`。

**典型type**：`Tool`、`API Endpoint`、`Concept`、`Playbook`、`Policy`

**核心字段**：`verified`标记人类审核状态，`confidence`标记可信度，`sources`带来源引用。

**示例**：Jira创建工单API（约17行）
```markdown
---
title: "创建Jira工单"
type: "API Endpoint"
method: "POST"
endpoint: "/rest/api/3/issue"
verified: true
confidence: high
sources: ["https://developer.atlassian.com/..."]
tags: ["jira", "ticket"]
---

# 创建Jira工单

## 参数
- `project.key` (string, required): 项目Key，如 "PLAT"
- `summary` (string, required): 工单标题
- `issuetype.name` (string, required): "Bug" / "Task"

## 示例
`jira.create_issue(project={"key":"PLAT"}, summary="生产500错误", issuetype={"name":"Bug"})`
```

**适用边界**：Agent需要结构化、可机器读取的知识时，特别适合有明确Schema的工具类文档。

---

### 3.1.3 场景3：团队运维Runbook（Playbook）

**适用**：SRE/运维团队记录故障处理流程、操作手册、应急响应。

**目录结构**：按服务分目录（`services/payment-service/`）或按故障类型分（`incidents/`）。

**典型type**：`Playbook`、`Runbook`、`On-Call Guide`、`Escalation Policy`

**核心字段**：`owner`标记负责人，`last_tested`标记上次演练时间，`severity`标记故障等级。步骤要**极度具体**。

**示例**：服务重启Playbook（约18行）
```markdown
---
title: "Payment Service 紧急重启"
type: "Playbook"
owner: sre-oncall@company.com
severity: critical
last_tested: 2026-07-15
estimated_minutes: 10
tags: ["payment", "restart"]
---

# Payment Service 紧急重启

## 前置检查
1. 确认需重启（查Grafana）2. #incidents频道通知

## 重启步骤
1. `kubectl ctx prod-use1`
2. `kubectl rollout restart deployment/payment-service`
3. `kubectl rollout status deployment/payment-service`
4. 等2分钟确认错误率恢复

## 回滚：`kubectl rollout undo deployment/payment-service`
## 升级：10分钟未恢复 → 打@sre-lead电话
```

**适用边界**：需要SOP落地为可执行、可演练、可追溯文档时，比Confluence更适合版本控制和CI。

---

## 3.2 Frontmatter扩展字段最佳实践

OKF鼓励按需扩展，常用推荐字段：

| 字段名 | 类型 | 用途 | 示例值 |
|--------|------|------|--------|
| `owner` | string | 负责人/团队邮箱 | `data-team@company.com` |
| `freshness_sla` | string | 新鲜度SLA | `30m`、`24h`、`7d` |
| `confidence` | enum | 可信度等级 | `high`/`medium`/`low` |
| `last_tested` | date | 上次测试/演练时间 | `2026-07-15` |
| `severity` | enum | 严重等级（Playbook用） | `critical`/`high`/`medium`/`low` |
| `version` | SemVer | 概念本身版本 | `1.2.0` |
| `deprecated` | boolean | 是否废弃 | `true` |
| `replaced_by` | path | 替代文件链接 | `/concepts/new-auth.md` |
| `permissions` | enum | 访问权限 | `internal`/`confidential`/`public` |

**设计原则**：只加你真正需要的字段，不要预加"可能有用"的字段。新增字段前先想清楚：谁消费？用来做什么决策？答不上来就不要加。

---

## 3.3 链接设计最佳实践

- **优先Bundle绝对链接**（`/path/to/file.md`）：文件移动时链接不失效
- **相对链接仅用于**：同一目录下紧密关联文件间，跨目录一律绝对路径
- **链接文字要有意义**：✅ `详见[客户表](/tables/customers.md)` ❌ `见[这里](/tables/customers.md)`
- **断链是特性**：规划阶段先写链接后补文档，鼓励增量式文档化
- **不要过度双向链接**：只在确实有关系时加链接，避免链接农场

---

## 3.4 渐进式文档化策略

OKF支持增量式文档化，不需要"一次写完"，五个成熟度阶段：

| 阶段 | 状态 | 内容要求 | Agent可用性 |
|------|------|----------|-------------|
| 0 | 占位 | index.md列出，或只有frontmatter空文件 | 知道标题和tags |
| 1 | 骨架 | 标题+主要章节标题，正文TODO | 知道大概结构 |
| 2 | 核心内容 | 关键信息、定义、Schema | 可使用核心信息 |
| 3 | 完善 | 示例、引用、交叉链接、边界情况 | 高置信度使用 |
| 4 | 验证 | `verified: true`，人类审核 | 生产可依赖 |

**实践建议**：从阶段0开始占位，不要因追求完美而拖延开始。Agent从阶段2开始就能使用部分信息，比没文档强100倍。

---

## 3.5 Index自动化脚本

简洁Python脚本（约25行），跨平台零依赖：

```python
#!/usr/bin/env python3
import re, glob
from pathlib import Path

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

def parse_fm(path):
    m = FM_RE.match(Path(path).read_text(encoding="utf-8"))
    if not m: return {}
    return dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)

def main():
    entries = []
    for md in glob.glob("**/*.md", recursive=True):
        p = Path(md)
        if p.name in ("index.md", "log.md"): continue
        fm = parse_fm(p)
        title = fm.get("title", p.stem).strip().strip('"')
        desc = fm.get("description", "").strip().strip('"')
        entries.append(f"- [{title}](./{md}) — {desc}")
    entries.sort()
    Path("index.md").write_text(
        "# Knowledge Index\n\n_自动生成，勿手动编辑_\n\n" + "\n".join(entries) + "\n",
        encoding="utf-8"
    )
    print(f"Generated index.md with {len(entries)} entries")

if __name__ == "__main__":
    main()
```

**用法**：保存为`scripts/generate_index.py`，cd到Bundle根目录后运行`python scripts/generate_index.py`。建议加入pre-commit hook。

---

## 3.6 与Git工作流结合

OKF纯文本特性天生适配Git工作流：

- **分支策略**：知识更新用feature branch（如`knowledge/add-payment-runbook`），提PR，重要知识需至少1人review
- **知识评审**：像代码评审一样审知识——准确性、完整性、链接有效性、格式规范
- **Git能力复用**：`git diff`看清变更、`git blame`找作者、`git log`看演进、`git revert`回滚
- **CI检查**：frontmatter校验、断链检测、废弃字段检查、index同步检查

---

## 3.7 SemVer版本管理建议

Bundle用SemVer（MAJOR.MINOR.PATCH）：

| 层级 | 变更类型 | 示例 |
|------|----------|------|
| **MAJOR** | 不兼容结构变更 | 删除/重命名Concept、改type含义、删必填字段 |
| **MINOR** | 向后兼容新增 | 新增Concept、新增可选字段、补充内容 |
| **PATCH** | 小幅修复 | 错别字、链接修复、内容微调 |

版本记录在根`index.md`或`log.md`（CHANGELOG）中。消费端根据版本决定索引策略：PATCH静默更新，MINOR增量索引，MAJOR全量重索引。

---

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [02 5分钟快速入门](./02-quickstart.md) | [README](./README.md) | [04 局限性与方案对比](./04-limitations-and-comparison.md) |
