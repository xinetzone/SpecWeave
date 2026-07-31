---
title: 代码优化指南集
date: 2026-07-31
type: guides-index
tags:
  - 指南
  - 代码优化
  - 索引
---

# 代码优化指南集

> 本目录存放代码优化相关的通用指南、参考材料、Checklist和培训文档。具体的里程碑复盘报告请见 [reports/code-optimization/](../../reports/code-optimization/README.md)。

---

## 📚 文档导航

### 入门学习

| 文档 | 类型 | 适合人群 | 阅读时间 |
|------|------|---------|---------|
| [optimization-beginner-guide.md](optimization-beginner-guide.md) | 📖 入门指南 | 新成员 | 15分钟 |
| [optimization-anti-patterns-checklist.md](optimization-anti-patterns-checklist.md) | 📋 可打印Checklist | 所有人 | 2分钟（过一遍） |
| [optimization-assessment-quiz.md](optimization-assessment-quiz.md) | 📝 考核测试题 | 学完入门指南后 | 30分钟 |

### 策略参考

| 文档 | 类型 | 用途 |
|------|------|------|
| [optimization-strategy-comparison.md](optimization-strategy-comparison.md) | 📊 策略对比表 | 选择优化策略时参考 |
| [methodology-validation-summary.md](methodology-validation-summary.md) | ✅ 方法论验证 | 了解七概念质量门在优化中的实际效果 |

### 可复用模式

| 模式 | 类型 | 用途 |
|------|------|------|
| [phased-incremental-optimization](../../patterns/methodology-patterns/governance-strategy/phased-incremental-optimization.md) | 方法论模式 | 分层渐进优化策略完整规范 |
| [ffi-intrusive-refcount-zerocopy](../../patterns/code-patterns/ffi-intrusive-refcount-zerocopy.md) | 代码模式 | 侵入式引用计数零拷贝 |
| [const-cow-trigger](../../patterns/code-patterns/const-cow-trigger.md) | 代码模式 | const/non-const重载驱动的COW |
| [preflight-checks-script](../../patterns/code-patterns/preflight-checks-script.md) | 代码模式 | 构建环境预检脚本 |
| [platform-aware-dependency-detect](../../patterns/code-patterns/platform-aware-dependency-detect.md) | 代码模式 | 跨平台CMake依赖检测 |

### 实战案例

| 案例 | 位置 |
|------|------|
| Split层零拷贝+COW优化里程碑 | [retrospective-split-zerocopy-cow-milestone-20260731](../../reports/code-optimization/retrospective-split-zerocopy-cow-milestone-20260731/README.md) |

---

## 🎯 新成员学习路径推荐

```
Step 1: 读入门指南（15分钟）
    ↓
Step 2: 对照Checklist过一遍（2分钟）
    ↓
Step 3: 做测试题自测（30分钟），≥80分通过
    ↓
Step 4: 看策略对比表，了解何时用什么策略
    ↓
Step 5: 参考真实案例，阅读完整里程碑复盘
    ↓
Step 6: 实际做优化时，对照Checklist和模式文档
```

---

## Changelog

<!-- changelog -->
- 2026-07-31 | feat | 初始版本，从reports/code-optimization/迁移通用指南到guides/目录
