# 🔄 复盘与模式库

本目录汇集 SpecWeave 项目**自身演进过程中的复盘报告与可复用模式沉淀**。通过七概念方法论（R-I-E-C-A-F-V）编排，将实践经验提炼为经过质量门验证的可迁移模式。

与 [知识库](../knowledge/index.md)（外部知识学习成果）互补：知识库是"向外学"，复盘模式库是"向内求"。

## 📂 内容板块

```{toctree}
:maxdepth: 2
:caption: 复盘与模式
:hidden:

patterns/methodology-patterns/README
reports/milestone/README
```

| 板块 | 说明 | 入门推荐 |
|------|------|---------|
| **[方法论模式库](patterns/methodology-patterns/README.md)** | 经过 G1-G4 质量门与 V 对抗审查的可复用方法论模式（15+ 个模式，含知识编译、双引擎架构、三层修复闭环等） | [知识编译模式](patterns/methodology-patterns/knowledge-compilation.md) — 将10个源文件深度编译为~4800token自包含参考 |
| **里程碑复盘** | 项目重要里程碑节点的系统性复盘报告（知识 scaling、Loop Engineering、Harness Wiki 生成等） | [SpecWeave 知识 scaling 里程碑](reports/milestone/specweave-knowledge-scaling-milestone-20260801.md) |
| **对抗审查报告** | 重要产出的对抗审查记录，证伪加固过程留痕 | [Headroom Wiki 对抗审查](reports/adversarial-review/adversarial-review-analyze-wechat-article-3dnk-20260803.md) |
| **竞争分析** | 外部工具/平台的竞争性分析与对比研究 | [Headroom 上下文压缩分析](reports/competitive-analysis/retrospective-headroom-wiki-20260803/README.md) |

## 🎯 如何使用

- **想找可复用的方法论？** 直接浏览 [方法论模式库](patterns/methodology-patterns/README.md)，按"触发场景"列选择适合的模式
- **想了解项目演进历程？** 阅读 [里程碑复盘](reports/milestone/README.md) 系列报告
- **想学习如何做复盘？** 参考任意一份里程碑报告的结构（事实→洞察→模式→行动）
- **想贡献新模式？** 遵循模式入库流程：R（复盘采集）→ I（洞察提炼）→ E（模式萃取）→ V（对抗审查）→ 入库

## 模式成熟度

| 等级 | 名称 | 标准 |
|------|------|------|
| L1-draft | 假设性模式 | 单案例，待验证 |
| L1.5 | 同谱系双案例 | 同一方法论谱系两个独立实现互为验证 |
| L2-validated | 已验证模式 | ≥2 独立案例，已在本项目验证 |
| L3-mature | 成熟模式 | 跨项目验证，有明确边界条件 |
| L4-optimized | 优化模式 | 经过对抗审查，工具化/自动化支持 |

## 接入约定

> 新增复盘或模式时：
>
> 1. 复盘报告放入 `reports/` 对应子目录（milestone/knowledge/adversarial-review/competitive-analysis）；
> 2. 可复用模式放入 `patterns/methodology-patterns/` 并更新模式库索引；
> 3. 重要内容在本页表格中追加条目以便发现。
