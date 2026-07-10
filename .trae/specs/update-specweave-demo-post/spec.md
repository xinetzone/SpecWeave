# 创建 SpecWeave 最新版 Demo 帖（daoyi 账号） Spec

## Why
SpecWeave 初赛 Demo 帖（topic/44601，flexloop 账号）于 6 月 25 日发布，数据已严重过时（34 模式/23 脚本/142 对话/41 报告 vs 当前 237+ 模式/155+ 脚本/1,256 提交/140+ 报告/59 Wiki/15 Skills）。基于第一性原理——不编辑旧帖，而是以 daoyi 账号发布全新 Demo 帖至初赛专区，用最新数据全面展示项目当前状态。

## What Changes
- **不编辑** topic/44601 旧帖
- 以 **daoyi 账号**在初赛专区（40-category）**创建新帖**
- 新帖使用最新项目数据（截至 2026-07-10，1,256 次提交）
- 新增技术创新点：四层质量防御体系、L3 模式成熟度标准化、规范自举性驱动演化
- 新增 15 个 Skills（L0/L1/L2 三层架构）、59 个 Wiki（8 大主题）
- 新增 5+ 外部验证项目展示
- 更新行业对标表格
- 更新 HTML 附件（如需要）

## Impact
- Affected specs: 更新本 spec（从编辑旧帖改为创建新帖）
- Affected code: 无代码变更
- Affected docs: 生成新 Demo 帖草稿文件

## ADDED Requirements
### Requirement: 新帖创建
Demo 帖 SHALL 以 daoyi 账号在初赛专区（https://forum.trae.cn/c/38-category/40-category/40）创建全新帖子，而非编辑旧帖 topic/44601。

#### Scenario: 创建新帖
- **WHEN** 帖子内容准备就绪
- **THEN** 在初赛专区创建新帖
- **AND** 发布账号为 daoyi

### Requirement: Demo 帖数据刷新
Demo 帖 SHALL 将所有量化数据设为截至 2026-07-10 的最新值（1,256 提交/237+ 模式/140+ 报告/59 Wiki/15 Skills/155+ 脚本/5+ 外部验证）。

#### Scenario: 数据一致性校验
- **WHEN** Demo 帖内容生成后
- **THEN** 所有数字与 `docs/project-highlights.md` 一致
- **AND** 与 `git rev-list --count HEAD` 结果匹配

### Requirement: 新增技术创新点展示
Demo 帖 SHALL 展示四层质量防御体系（L0-L3）、L3 模式成熟度标准化（5 个 L3 模式）、规范自举性驱动演化。

### Requirement: 新增知识体系展示
Demo 帖 SHALL 展示 15 个 Skills（L0/L1/L2 三层架构）和 59 个 Wiki 教程（8 大主题分类）。

### Requirement: 新增外部验证
Demo 帖 SHALL 展示 5+ 外部验证项目（竹简悟道/论坛自动化/Tuya IoT/Home Assistant/火山引擎系列）。

### Requirement: 使用论坛自动化脚本发布
Demo 帖 SHALL 使用 forum-posting Skill 或 forum-bot.py 以 daoyi 账号发布。

#### Scenario: 自动化发布
- **WHEN** Demo 帖内容准备就绪
- **THEN** 使用 forum-posting Skill 以 daoyi 账号在初赛专区创建新帖
- **AND** 发布后验证帖子内容可见且格式正确