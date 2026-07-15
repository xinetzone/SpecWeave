---
title: "Bug修复1+N+1 Checklist模板"
id: "bug-fix-checklist"
source: "retrospective:retrospective-conflict-resolution-mechanism-20260708"
x-toml-ref: "../../.meta/toml/.agents/templates/bug-fix-1n1-checklist-template.toml"
type: "checklist-template"
maturity_level: "L2"
created_date: "2026-07-08"
tags: [bug-fix, checklist, code-review, commit-conventions]
trigger_conditions:
  - 修复任何Bug后执行提交前
  - 代码审查发现问题后修复
  - 任何fix类型提交前
validation_count: 1
reuse_count: 0
---
# Bug修复"1+N+1" Checklist

> **来源**：从[多智能体冲突解决机制复盘](../docs/retrospective/reports/task-reports/retrospective-conflict-resolution-mechanism-20260708/retrospective-report.md)中萃取。核心原则：每个Bug修复必须包含1个代码修复+N个预防测试+1个规范Commit，确保修复即闭环，防止同类问题再次引入。

---

## 修复前

- [ ] 已复现Bug并记录复现步骤
- [ ] 已定位根因（找到根本原因，而非仅修复症状）
- [ ] 已评估影响范围（哪些模块/场景/用户受影响）
- [ ] 已确认修复方案（如有多种方案，选择最小变更的）

---

## 1. 代码修复

- [ ] 修复代码已编写，逻辑正确
- [ ] 修复遵循最小变更原则（不做与本Bug无关的重构）
- [ ] 修复不引入新的Bug（已做回归风险评估）
- [ ] 并发场景：已检查锁超时、幂等性、防御性拷贝（参考六维检查法）
- [ ] 边界场景：已验证N=0/1/2/3等关键边界值
- [ ] 可配置性：硬编码的规则/阈值/关键词已支持构造函数注入

---

## N. 预防测试（N≥1）

- [ ] **回归测试**：至少1个测试用例直接复现本次Bug（修复前失败，修复后通过）
- [ ] **边界测试**：同类问题的边界场景（如修了N=2的bug，加N=0/1/3/5的测试）
- [ ] **异常路径测试**：覆盖错误输入、超时、重复调用、并发冲突等异常场景
- [ ] **防御性测试**：验证外部修改传入参数不会影响内部状态（如适用）
- [ ] 所有新增+原有测试通过，无回归失败

---

## 1. 规范Commit

### Commit格式检查

- [ ] Commit type正确：使用`fix(scope):`（纯修复）；如果同时包含功能增强则用`feat(scope):`
- [ ] Scope准确：对应修改的模块名（如`collaboration`、`links`、`scripts`）
- [ ] Subject为中文，说明"为什么需要修复"而非"改了什么"，不超过72字符
- [ ] 预防标记：Commit subject末尾添加`[prevent: ...]`标记（见下方标记规则）
- [ ] Body详细说明：问题根因、修复方案、预防测试、影响范围
- [ ] 单一职责：本commit只包含这一个Bug的修复和预防，不混入其他无关变更

### 预防标记规则

| 标记 | 使用场景 |
|------|---------|
| `[prevent: test-case]` | 通过新增单元测试预防回归（最常用） |
| `[prevent: architecture]` | 通过架构调整/防御性编程从根源消除问题 |
| `[prevent: rule-update]` | 通过更新规则/规范/Checklist预防人为错误 |
| `[prevent: doc]` | 通过文档补充说明防止误用 |
| 组合使用 | 如`[prevent: test-case, architecture]`表示多种预防措施 |

### Commit Message模板

```
fix(<scope>): <修复简述——一句话说明根因> [prevent: <type>]

- 问题根因：<一句话说明Bug的根本原因>
- 修复方案：<一句话说明如何修复的>
- 预防测试：<N>个新增测试覆盖<回归/边界/异常>场景
- 影响范围：<哪些模块/功能受影响>
```

### Commit Message示例

```
fix(collaboration): 修复冲突解决机制死锁风险与逻辑缺陷 [prevent: test-case, architecture]

- 死锁预防：资源锁增加超时机制（默认300秒，可配置），防止持有者崩溃导致永久死锁
- 活锁预防：rejected_by列表自动去重，防止重复拒绝绕过升级机制
- 逻辑修复：负载均衡覆盖所有候选agent，资源优先级调度正确排序
- 并发安全：传入可变参数做防御性deepcopy防止竞态
- 测试覆盖：新增13个测试用例，总计39个全通过
```

---

## 修复后验证

- [ ] 本地验证通过：所有单元测试通过
- [ ] 代码风格检查通过（lint/type check）
- [ ] 如有必要，已更新相关文档
- [ ] 已在提交信息中正确标记预防措施类型
- [ ] 可用`git fixlog`或`git prevent <type>`验证标记可被检索

---

## 辅助工具

配置以下git alias便于日常使用：

```bash
# 列出所有带预防标记的fix提交
git config --global alias.fixlog "log --oneline --grep=\"[prevent:\" --fixed-strings"

# 按预防类型筛选（如 git prevent test-case）
git config --global alias.prevent "!f() { if [ -n \"$1\" ]; then git log --oneline --grep=\"prevent: $1\" --fixed-strings; else git log --oneline --grep=\"[prevent:\" --fixed-strings; fi; }; f"
```
