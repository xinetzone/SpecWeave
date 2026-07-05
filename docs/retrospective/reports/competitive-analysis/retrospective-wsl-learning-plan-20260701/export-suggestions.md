---
id: "retrospective-wsl-learning-plan-20260701-export"
title: "导出建议"
source: "docs/knowledge/learning/08-systems-infrastructure/wsl-learning-plan.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-wsl-learning-plan-20260701/export-suggestions.toml"
---
# 导出建议

## 一、知识沉淀建议

### 建议 1：将"三源三角验证法"提升为通用学习方法论

**当前状态**：[triangular-source-verification.md](../../../patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md) 位于 `retrospective-knowledge` 分类，L2 成熟度。

**改进建议**：
- 提升至 L3 成熟度（本次为第二次实证验证，方法论稳定）
- 考虑从 `retrospective-knowledge` 提升至更通用的分类（如 `tools-automation` 或新建 `learning-methodology` 分类），使其适用于所有"基于第三方仓库 + 在线文档"的学习任务
- 在 [docs/knowledge/README.md](../../../../knowledge/README.md) 的使用指南中，明确推荐"学习任何外部技术时，必须采集源码 + 开发者文档 + 用户文档三源"

**优先级**：高
**责任方**：reviewer 审核模式升级，orchestrator 决定分类调整

### 建议 2：新增 `preview-api-learning-strategy.md` 模式

**内容要点**：
- preview API 文档完整度梯度规律（示例 > 错误码 > 清单 > 教程）
- 学习策略：优先抓端到端示例与错误码表，从示例逆向提取 API 用法
- 适用场景：任何 preview/beta 阶段 API 的学习任务

**建议位置**：`docs/retrospective/patterns/methodology-patterns/tools-automation/preview-api-learning-strategy.md`

**优先级**：中
**责任方**：developer 起草，reviewer 审核

### 建议 3：新增 `container-cli-conventions.md` 最佳实践

**内容要点**：
- 类 Docker CLI 的通用命令惯例（`ls`/`ps`/`rm`/`inspect`/`prune` 短形态）
- 常见标志（`--rm`/`-it`/`-d`/`-p`/`-v`/`--name`）
- 适用工具：Docker / Podman / nerdctl / ctr / wslc 等

**建议位置**：`docs/knowledge/best-practices/container-cli-conventions.md`

**优先级**：中
**责任方**：developer 起草

### 建议 4：新增 `channel-separation-by-responsibility.md` 架构模式

**内容要点**：
- 跨边界通信系统应按职责（命令/通知/数据/控制）分离通道
- WSL2 的 hvsocket 多通道拓扑作为产业级案例
- SpecWeave 协议设计的本地化映射

**建议位置**：`docs/retrospective/patterns/architecture-patterns/channel-separation-by-responsibility.md`

**优先级**：中
**责任方**：architect 起草，reviewer 审核

## 二、流程改进建议

### 建议 5：在 atomic-commit-cmd Skill 中加入 PowerShell heredoc 预防提示

**当前问题**：本次提交首次尝试使用 bash heredoc 语法失败，浪费一次工具调用。项目已有教训记录（[windows-powershell-heredoc.md](../../../../knowledge/operations/windows-powershell-heredoc.md)），但未内化为 Skill 的预防性提示。

**改进建议**：
- 在 [atomic-commit-cmd SKILL.md](../../../../../.agents/skills/atomic-commit-cmd/SKILL.md) 的"安全检查清单"中新增一条：
  > - [ ] PowerShell 环境下禁止使用 heredoc 语法，直接使用 here-string `@'...'@`
- 或在"快速开始"步骤 5 中明确：
  > 执行提交时，PowerShell 环境使用 here-string `@'...'@` 传递多行提交信息，禁止 bash heredoc `$(cat <<'EOF'...EOF)`

**优先级**：高
**责任方**：developer 修改 Skill

### 建议 6：建立"学习计划归档"标准 SOP

**当前状态**：本次归档流程（`.temp/` → `docs/knowledge/learning/`）是手动判断的，依赖对现有条目的对照。

**改进建议**：将本次流程沉淀为标准 SOP，纳入 [docs/knowledge/best-practices/](../../../../knowledge/best-practices/)：
- 文件名：`learning-plan-archiving-sop.md`
- 核心步骤：
  1. 读取 `docs/knowledge/learning/` 现有条目，确定命名风格
  2. 复制 `template.md` frontmatter 结构
  3. 写入 `docs/knowledge/learning/{技术名}-learning-plan.md`
  4. 删除 `.temp/` 中的临时文件
  5. 运行 `python generate_index.py` 刷新索引
  6. 原子提交（显式指定文件，禁止 `git add .`）

**优先级**：中
**责任方**：developer 起草

### 建议 7：WebFetch 抓取策略沉淀

**当前状态**：本次任务采用 5 层并行 WebFetch 策略，效果良好但未文档化。

**改进建议**：在 [docs/knowledge/operations/](../../../../knowledge/operations/) 新增 `webfetch-crawling-strategy.md`：
- 分层并行抓取原则（入口页 → 子页面首页 → 细节页）
- 空模板页识别与降级策略
- 从端到端示例逆向提取 API 用法的方法

**优先级**：低
**责任方**：developer 起草

## 三、行动计划

| 行动项 ID | 行动项 | 优先级 | 责任方 | 验收标准 | 截止 |
|-----------|--------|--------|--------|----------|------|
| ACT-001 | 提交整合后的 WSL 学习计划报告 | 高 | developer | commit 成功，工作树干净 | 本次会话 |
| ACT-002 | 在 atomic-commit-cmd Skill 加入 heredoc 预防提示 | 高 | developer | SKILL.md 安全清单新增一条 | 下次提交前 |
| ACT-003 | 将 triangular-source-verification 提升至 L3 | 高 | reviewer | 模式文件更新成熟度标签 | 一周内 |
| ACT-004 | 新增 preview-api-learning-strategy 模式 | 中 | developer | 模式文件入库，索引更新 | 一周内 |
| ACT-005 | 新增 container-cli-conventions 最佳实践 | 中 | developer | 文件入库，索引更新 | 一周内 |
| ACT-006 | 新增 channel-separation-by-responsibility 架构模式 | 中 | architect | 模式文件入库，索引更新 | 两周内 |
| ACT-007 | 新增 learning-plan-archiving-sop | 中 | developer | SOP 文件入库 | 两周内 |
| ACT-008 | 补充抓取 wsl.dev 的 C#/C++ API 子页面 | 低 | developer | WSL 学习计划报告补充完整 API 清单 | 下次学习时 |
| ACT-009 | 新增 webfetch-crawling-strategy 操作指南 | 低 | developer | 文件入库，索引更新 | 两周内 |

## 四、未入库的观察

以下观察未形成正式洞察，但值得记录：

1. **MkDocs Material 站点的空模板页特征**：返回内容仅含 `Made with Material for MkDocs` 页脚时，通常为占位页或 JS 动态渲染页，WebFetch 无法获取。可作为后续 WebFetch 抓取的快速判别信号。

2. **wsl.dev 与 learn.microsoft.com 的分工**：wsl.dev 面向开发者（架构、API、构建），learn.microsoft.com 面向用户（安装、配置、CLI 用法）。这种"开发者文档独立站点 + 用户文档官方门户"的分工模式值得借鉴。

3. **NuGet 包名与命名空间一致性**：`Microsoft.WSL.Containers` NuGet 包对应 `Microsoft.WSL.Containers` 命名空间，这种一致性简化了记忆与使用。SpecWeave 在设计 SDK 时可参照此惯例。

4. **preview 阶段的明确标注**：WSL Container API 在 wsl.dev 每个页面顶部都明确标注 "PREVIEW NOTICE"，并说明"可能有不兼容变更"。这种透明的 maturity 标注值得 SpecWeave 在 capability 注册中心借鉴。
