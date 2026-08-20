# Tasks

## 任务总览

本 spec 共 10 个文档创建任务 + 1 个质量验证任务，按章节顺序编排。

- [x] Task 1: 创建 `00-overview.md` 教程总览与导航索引
- [x] Task 2: 创建 `01-repository-structure.md` 仓库整体架构
- [x] Task 3: 创建 `02-workflows-deep-dive.md` GitHub Actions 工作流详解
- [x] Task 4: 创建 `03-issue-templates.md` Issue 模板详解
- [x] Task 5: 创建 `04-community-files.md` 社区健康文件详解
- [x] Task 6: 创建 `05-infrastructure-sync-model.md` 中央同步模型
- [x] Task 7: 创建 `06-issue-sorting-labeling.md` Issue Sorting 与标签体系
- [x] Task 8: 创建 `07-operations-guide.md` 常见操作指南
- [x] Task 9: 创建 `08-best-practices.md` 最佳实践与注意事项
- [x] Task 10: 创建 `09-resources.md` 术语表与参考资料
- [x] Task 11: 创建 `README.md` 并统一质量验证（文件大小、链接、frontmatter、导航）

---

## 任务详细分解

### Task 1: 创建 `00-overview.md` 教程总览与导航索引
- [ ] Step 1.1: 在 `.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/` 目录下创建 `00-overview.md`
- [ ] Step 1.2: 编写 YAML frontmatter（id/title/x-toml-ref/source/category/tags/date/status/author/summary）
- [ ] Step 1.3: 编写教程引言，简述 conda `.github` 元仓库的价值与学习意义
- [ ] Step 1.4: 绘制 Mermaid 概念定位图（组织级元仓库在 GitHub 组织治理栈中的位置）
- [ ] Step 1.5: 编写 10 章导航表（章节号 + 标题 + 简要内容描述 + 文件链接）
- [ ] Step 1.6: 编写目标读者说明与阅读路径建议
- [ ] Step 1.7: 关联 08 主题下其他 wiki（git-advanced-wiki、git-baidu-sync）
- **验证**: 文件 < 300 行；frontmatter 完整；含 Mermaid 图；导航链接相对路径

### Task 2: 创建 `01-repository-structure.md` 仓库整体架构
- [ ] Step 2.1: 创建文件并编写 frontmatter
- [ ] Step 2.2: 编写完整目录树（根级 + `.github/` 各子目录），基于本地仓库实际结构
- [ ] Step 2.3: 编写每个文件/目录的作用说明表
- [ ] Step 2.4: 对比组织级 `.github` 元仓库与普通仓库 `.github/` 目录的区别
- [ ] Step 2.5: 说明本仓库在 conda/infrastructure 同步体系中的角色定位
- [ ] Step 2.6: 添加底部双向导航
- **验证**: 文件 < 300 行；目录树与本地仓库一致；含对比表格

### Task 3: 创建 `02-workflows-deep-dive.md` GitHub Actions 工作流详解
- [ ] Step 3.1: 创建文件并编写 frontmatter
- [ ] Step 3.2: 编写 `cla.yml` 详解（触发事件/权限/步骤/配置语义/使用场景）
- [ ] Step 3.3: 编写 `issues.yml` 详解
- [ ] Step 3.4: 编写 `labels.yml` 详解
- [ ] Step 3.5: 编写 `lock.yml` 详解
- [ ] Step 3.6: 编写 `project.yml` 详解
- [ ] Step 3.7: 编写 `stale.yml` 详解
- [ ] Step 3.8: 编写 `update.yml` 详解
- [ ] Step 3.9: 编写跨工作流共性配置模式（concurrency/permissions/pull_request_target/版本锁定/ubuntu-slim）
- [ ] Step 3.10: 添加底部双向导航
- **验证**: 文件 < 300 行；覆盖全部 7 个工作流；配置项与本地仓库一致

### Task 4: 创建 `03-issue-templates.md` Issue 模板详解
- [ ] Step 4.1: 创建文件并编写 frontmatter
- [ ] Step 4.2: 编写 `0_bug.yml` 详解（字段/block 类型/validations）
- [ ] Step 4.3: 编写 `1_feature.yml` 详解
- [ ] Step 4.4: 编写 `2_documentation.yml` 详解
- [ ] Step 4.5: 编写 `epic.yml` 详解（What/Why/User impact/Goals/Tasks/blocked_by/blocks）
- [ ] Step 4.6: 说明模板如何与 Issue Sorting 标签联动、单一来源原则
- [ ] Step 4.7: 添加底部双向导航
- **验证**: 文件 < 300 行；覆盖 4 个模板；字段语义解析准确

### Task 5: 创建 `04-community-files.md` 社区健康文件详解
- [ ] Step 5.1: 创建文件并编写 frontmatter
- [ ] Step 5.2: 编写 `CODE_OF_CONDUCT.md` 用途说明
- [ ] Step 5.3: 编写 `HOW_WE_USE_GITHUB.md` 详解（Issue Sorting 定义/标签约定/代码评审/合并规范）
- [ ] Step 5.4: 编写 `profile/README.md` 详解（conda/conda-incubator/conda-archive 三组织架构）
- [ ] Step 5.5: 编写 `.gitignore` 说明（Python 模板来源）
- [ ] Step 5.6: 添加底部双向导航
- **验证**: 文件 < 300 行；内容与本地仓库一致

### Task 6: 创建 `05-infrastructure-sync-model.md` 中央同步模型
- [ ] Step 6.1: 创建文件并编写 frontmatter
- [ ] Step 6.2: 解析 `template-files/config.yml` 完整映射清单（必选/可选、src/dst、with.placeholder）
- [ ] Step 6.3: 说明 `conda/infrastructure` 中央仓库的角色
- [ ] Step 6.4: 说明同步触发方式（update.yml 每周拉取 + 中央 sync.yml 推送）
- [ ] Step 6.5: 对 `external/libs` 镜像仓库的维护启示
- [ ] Step 6.6: 添加底部双向导航
- **验证**: 文件 < 300 行；映射清单与本地 config.yml 一致

### Task 7: 创建 `06-issue-sorting-labeling.md` Issue Sorting 与标签体系
- [ ] Step 7.1: 创建文件并编写 frontmatter
- [ ] Step 7.2: 编写 Issue Sorting 概念、目的与四种优先级分类
- [ ] Step 7.3: 编写标签体系语法与互斥/并发规则（type/source/severity）
- [ ] Step 7.4: 绘制 Roadmap Board 流转 Mermaid 流程图
- [ ] Step 7.5: 编写常见回复模板（Duplicate/Anaconda/Off-topic）
- [ ] Step 7.6: 添加底部双向导航
- **验证**: 文件 < 300 行；含 Mermaid 图；标签约定准确

### Task 8: 创建 `07-operations-guide.md` 常见操作指南
- [ ] Step 8.1: 创建文件并编写 frontmatter
- [ ] Step 8.2: 编写"配置修改"场景（工作流触发/权限/参数、标签、模板修改，含 YAML 示例）
- [ ] Step 8.3: 编写"功能扩展"场景（新增工作流/标签类别/模板字段，含示例与验证方式）
- [ ] Step 8.4: 编写"问题排查"场景（工作流不触发原因、Action 版本更新与 SHA 锁定、dry-run/debug-only、gh CLI 手动触发）
- [ ] Step 8.5: 添加底部双向导航
- **验证**: 文件 < 300 行；三个场景步骤完整、示例可复制

### Task 9: 创建 `08-best-practices.md` 最佳实践与注意事项
- [ ] Step 9.1: 创建文件并编写 frontmatter
- [ ] Step 9.2: 编写可迁移治理模式（单一来源/模板标签分离/Action 版本锁定/最小权限）
- [ ] Step 9.3: 编写安全最佳实践（pull_request_target 风险与缓解、密钥最小授权）
- [ ] Step 9.4: 编写 ≥3 个反模式
- [ ] Step 9.5: 编写检验标准清单
- [ ] Step 9.6: 添加底部双向导航
- **验证**: 文件 < 300 行；含 ≥3 个反模式；含检验标准

### Task 10: 创建 `09-resources.md` 术语表与参考资料
- [ ] Step 10.1: 创建文件并编写 frontmatter
- [ ] Step 10.2: 编写术语表（≥15 条）
- [ ] Step 10.3: 编写权威参考资料链接清单
- [ ] Step 10.4: 编写按难度分级的扩展阅读建议
- [ ] Step 10.5: 添加底部双向导航
- **验证**: 文件 < 300 行；术语表 ≥15 条；含权威资料链接

### Task 11: 创建 `README.md` 并统一质量验证
- [ ] Step 11.1: 创建 `README.md`（教程入口、章节列表、一句话说明）
- [ ] Step 11.2: 所有原子文档 < 300 行（max/min 统计）
- [ ] Step 11.3: 链接检查全部通过（无断链、无 file:/// 绝对路径）
- [ ] Step 11.4: 所有文件 frontmatter 包含 `source: "spec:create-conda-dev-github-wiki-tutorial"` 与 `category: "learning"`
- [ ] Step 11.5: 01-08 文件底部三向导航完整且正确
- [ ] Step 11.6: 配置引用抽样核对（工作流名/Action 名/参数与本地仓库一致）
- [ ] Step 11.7: 修复验证中发现的所有问题
- **验证**: 全部检查项通过

---

# Task Dependencies

- 执行顺序：阶段一 Task 1（overview 定调）→ 阶段二 Task 2-10 并行（各章节独立）→ 阶段三 Task 11 质量验证与修复
- Task 2-10 相互独立，可并行执行
- Task 11 依赖 Task 1-10 全部完成
- 所有章节内容必须以本地仓库 `external/libs/conda-dev/.github` 文件为事实来源
