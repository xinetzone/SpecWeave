---
type: tasks
title: "自动赚钱系统文章转 OKF Wiki 任务队列"
source: "spec.md"
status: completed
---

# 实施任务

## Task 1: 完成公开内容与事实登记

Status: completed
Priority: high

### Test Requirements

- `rule`: 原文正文、标题、作者和发布日期已记录，F-001 至 F-017 连续且可回溯。
- `rule`: 作者观点、作者建议、原文示例与客观元信息已分层。

### Completion Evidence

- 证据：[facts.md](facts.md)
- 证据：bundle `references/article-source.md`
- 结果：通过 G1；未将建议阈值升级为市场事实。

## Task 2: 按操作可复现性两问确定 bundle 骨架

Status: completed
Priority: high

### Test Requirements

- `rule`: 文章未提供版本、安装、代码、输入输出和完整实测流程时，不创建 `examples/`。
- `rubric`: 结构与内容性质匹配，评分 2/2；商业分析/战略资讯采用 `index + concepts + references + log`。

### Completion Evidence

- 证据：`spec.md` 的“骨架判定”和 bundle 根索引性质声明。
- 结果：通过；bundle 未创建 `examples/`。

## Task 3: 生成三层知识内容与信源核验

Status: completed
Priority: high

### Test Requirements

- `rule`: 三篇 concepts 文档均回指 F 编号，并区分原文观点与非官方工程化重述。
- `rule`: 核验报告明确日期、数字、口径和引文四类边界。
- `rubric`: 内容可迁移性评分 2/2；至少给出触发条件、核心步骤、反模式和迁移验证。

### Completion Evidence

- 证据：bundle `concepts/00-three-directions.md`
- 证据：bundle `concepts/01-system-layers-and-automation.md`
- 证据：bundle `concepts/02-validation-and-boundaries.md`
- 证据：bundle `references/verification.md`
- 结果：通过 G2/G3；核心声明为作者单源观察，bundle 保持 `flagged`。

## Task 4: 完成导航与质量门收尾

Status: completed
Priority: medium

### Test Requirements

- `rule`: 根索引、概念索引、信源索引和父级分组索引均包含可达的 toctree 条目。
- `rule`: 新增与修改 Markdown 文件通过 UTF-8、相对链接、F 编号集合和敏感路径手动等效检查。

### Completion Evidence

- 证据：bundle `index.md`、`concepts/index.md`、`references/index.md`
- 证据：父级 `sheke/industry/index.md`
- 结果：通过；未执行 `invoke gates.*`，因此不宣称自动 gates 通过。

## Task 5: Git 交付边界

Status: completed
Priority: low

### Test Requirements

- `rule`: 未经用户明确请求，不执行 Git commit 或 push。

### Completion Evidence

- 证据：bundle `log.md`
- 结果：未提交、未推送。
