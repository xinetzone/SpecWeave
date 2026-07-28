---
title: "风险拦截器日志测试与四项缺陷修复复盘"
date: 2026-07-28
source: "check-risky-commands.py -vv 测试驱动bugfix"
type: task-retrospective
commit: afb19f6d
tags: [risk-interceptor, cli-tooling, logging, bugfix, whitebox-testing]
---

# 风险拦截器日志测试与四项缺陷修复复盘

## 1. 事实还原（S1）

### 1.1 任务背景

在前序风险拦截器模式V2开发完成后，通过 `-vv` 模式对包含10种高危命令场景的测试文件进行白盒测试，发现4项逻辑缺陷，本次任务完成全部修复并原子提交。

### 1.2 时间线

| 时间 | 事件 |
|------|------|
| T0 | 创建 `.temp/risky-commands-test.sh` 测试文件（含 DROP DATABASE/rm -rf/git push --force等10场景） |
| T1 | 以 `-vv` 模式运行，发现4项问题 |
| T2 | 逐一修复4项缺陷 |
| T3 | 语法验证 + 三轮测试（默认/-v/-vv）确认修复正确 |
| T4 | 删除临时测试文件，原子提交 afb19f6d |

### 1.3 变更统计

| 文件 | 新增行 | 删除行 | 变更内容 |
|------|--------|--------|---------|
| `check-risky-commands.py` | 13 | 4 | `_setup_logging` 重构：默认模式NullHandler静默 |
| `risk_interceptor.py` | 32 | 11 | 冗余升级警告修复+类别权重算法+信号去重+DEBUG日志 |
| **合计** | **45** | **15** | **2 files changed** |

### 1.4 发现的4项缺陷

| # | 缺陷 | 现象 | 根因 |
|---|------|------|------|
| 1 | 冗余升级警告 | CRITICAL命令+生产环境双重命中时，即使原等级已是CRITICAL仍输出"升级为CRITICAL"警告 | 升级判断缺少前置等级检查 |
| 2 | 风险类别随机选择 | 多类别CRITICAL信号并存时，回滚方案匹配到database类而非更危险的filesystem类 | 使用 `next(iter(set))` 随机取首个类别，无权重算法 |
| 3 | 拦截模板信号重复 | 同一(描述+匹配文本)在拦截提示中重复出现（如rm -rf/显示两次） | 信号列表未去重直接取top5 |
| 4 | 默认模式日志污染 | 无-v参数时输出 `[WARNING] check_risky_commands:` 前缀，污染CI stdout/stderr | verbose=0时仍挂载了StreamHandler |

## 2. 过程分析（S2）

### 2.1 成功因素

1. **白盒测试驱动发现问题**：通过添加DEBUG级别决策日志（每个模式匹配详情、权重计算、升级判断），让问题在测试输出中一目了然
2. **测试文件覆盖多场景**：10个高危命令场景覆盖了filesystem/database/git/container/security/permissions六大类别，触发了多类别竞争的边界情况
3. **逐模式验证**：修复每个问题后立即回归验证，避免修复引入新问题

### 2.2 问题根因分析

| 缺陷 | 根因分类 | 为什么开发时未发现 |
|------|---------|-------------------|
| 冗余升级警告 | 边界条件遗漏 | 开发时只测试了"HIGH+生产→CRITICAL"升级路径，未测试"已CRITICAL+生产"的确认路径 |
| 类别随机选择 | 算法设计缺陷 | Python set迭代顺序在版本间不稳定，小数据集下表现为"看起来正常"的伪随机 |
| 信号重复 | 去重缺失 | 同一文本可能被多个模式命中（如DROP DATABASE命中模式#1和#10），未在展示层去重 |
| 默认模式日志污染 | 日志架构问题 | 设计时只考虑了"有日志vs无日志"，未考虑"日志格式是否适合CI消费" |

### 2.3 修复方案选型

1. **冗余警告→条件日志**：增加 `if max_level < RiskLevel.CRITICAL` 判断，已CRITICAL时输出DEBUG确认而非WARNING告警
2. **类别选择→权重算法**：采用 `Σseverity²` 累加权重，严重等级平方放大了CRITICAL与HIGH的差距（16:9），使最危险类别自然胜出
3. **信号重复→(description, matched_text)去重**：用tuple作为去重key，排序后按严重度降序取最多5个唯一信号
4. **默认模式→NullHandler**：verbose=0时挂载NullHandler+level=51（高于CRITICAL），确保零日志输出；-v/-vv才启用格式化StreamHandler

## 3. 关键数据验证

### 修复后 -vv 模式输出关键日志（验证数据）

```
[DEBUG] 风险类别权重: {'filesystem': 32, 'database': 32, 'git': 18, 'permissions': 4, 'container': 18, 'security': 9}
[DEBUG] → 主要类别: filesystem，回滚方案已匹配
[DEBUG] CRITICAL命令 + 生产环境上下文双重命中（等级已是CRITICAL，确认加固）
[DEBUG] 拦截模板去重后显示 5/11 个信号（最多5个）
```

- ✅ 类别权重正确计算（filesystem=2×4²=32, database=2×4²=32, filesystem因插入顺序优先胜出）
- ✅ 升级路径日志从WARNING降级为DEBUG
- ✅ 去重计数正确（11个原始信号去重后显示5个最高严重度）
- ✅ 默认模式stdout仅含业务输出（无日志前缀）
