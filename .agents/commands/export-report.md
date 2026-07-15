---
id: "export-report"
title: "导出报告指令集"
source: "AGENTS.md#导出报告指令"
x-toml-ref: "../../.meta/toml/.agents/commands/export-report.toml"
---
# 导出报告指令集

## 触发条件

- 复盘报告生成完成
- 洞察分析完成
- 任务执行结束需要总结
- 用户请求导出特定报告
- 周期性报告生成触发

## 输入规范

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| report_type | string | 是 | 报告类型：`retrospective`/`insight`/`summary`/`custom` |
| source_path | string | 是 | 源报告文件路径 |
| formats | list | 否 | 导出格式：`md`/`pdf`/`docx`/`json`，默认 `["md"]` |
| output_dir | string | 否 | 输出目录，默认 `docs/reports/` |
| include_attachments | boolean | 否 | 是否包含附件，默认 `true` |
| compress | boolean | 否 | 是否压缩打包，默认 `false` |

## RACI责任分配矩阵

**RACI模型说明**：
- **R** = 负责执行（Responsible）：实际完成工作的角色
- **A** = 最终审批（Accountable）：对结果负最终责任，拥有最终决策权，每项活动有且仅有一个A
- **C** = 需咨询（Consulted）：决策前需征求意见、提供专业输入的角色，双向沟通
- **I** = 需知会（Informed）：决策后需告知进展与结果的角色，单向沟通

| 导出报告核心活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 触发导出与参数确认 | **R/A** | I | C | I | I | I |
| 源报告验证（步骤1） | R | I | C | **A** | I | I |
| 导出内容准备（步骤2） | **R/A** | I | C | I | I | I |
| 格式转换（步骤3：PDF/DOCX/JSON） | I | I | **R** | **A** | I | I |
| 导出文件生成（步骤4） | I | I | **R** | **A** | I | I |
| 归档与索引更新（步骤5） | **R/A** | I | C | I | I | I |
| 通知与交付（步骤6） | **R/A** | I | I | I | I | I |
| 导出质量验收 | C | I | C | **R/A** | I | I |
| 含敏感信息报告导出审批 | C | C | I | R | I | **A** |

### 审批权限边界

- **常规报告导出**：orchestrator确认导出参数，reviewer验证源报告合法性
- **格式转换与文件生成**：developer负责执行，reviewer验收输出质量
- **含L3/L4敏感信息报告**：co-founder审批，reviewer执行脱敏审计
- **敏感信息脱敏**：developer执行脱敏操作，reviewer审计脱敏效果
- **导出工具链异常**：architect参与技术方案评估，orchestrator协调资源

## 执行步骤

### 步骤 1：验证源报告

- 检查源报告文件是否存在
- 验证报告格式是否符合规范
- 检查 frontmatter 是否完整
- 确认报告内容不为空

### 步骤 2：准备导出内容

- 提取报告元数据（标题、日期、作者等）
- 整理报告正文内容
- 收集关联附件与图表
- 生成报告目录与索引

### 步骤 3：格式转换

- Markdown 格式：直接复制源文件
- PDF 格式：使用模板渲染并生成 PDF
- DOCX 格式：转换为 Word 文档格式
- JSON 格式：提取结构化数据

### 步骤 4：生成导出文件

- 创建输出目录（如不存在）
- 按格式生成导出文件
- 命名规范：`<报告类型>-<日期>-<版本>.扩展名`
- 添加导出时间戳与版本信息

### 步骤 5：归档与索引

- 将导出文件归档至指定目录
- 更新报告索引表
- 添加到知识资产库
- 记录导出历史

### 步骤 6：通知与交付

- 通知相关角色报告已导出
- 提供下载链接（如适用）
- 同步至自我管理模块
- 更新系统状态

## 输出规范

| 产出物 | 格式 | 存储位置 |
|--------|------|---------|
| Markdown 报告 | `.md` | 指定输出目录 |
| PDF 报告 | `.pdf` | 指定输出目录 |
| DOCX 报告 | `.docx` | 指定输出目录 |
| JSON 数据 | `.json` | 指定输出目录 |
| 导出清单 | `.txt` | 指定输出目录 |

## 质量验收

- 导出文件格式正确，可正常打开
- 文件内容与源报告一致，无丢失或损坏
- 文件名符合命名规范，包含时间戳
- 文件已归档至指定目录
- 索引表已更新，链接有效

## 约束条件

- 仅导出已完成的报告，不处理草稿状态
- PDF/DOCX 导出依赖外部工具链（如 pandoc）
- 大文件导出需考虑性能与存储空间限制
- 敏感信息需在导出前进行脱敏处理

## 关联资源

- [自我复盘模块](../modules/self-retrospective.md)
- [自我洞察模块](../modules/self-insight.md)
- [报告模板](../docs/retrospective/templates/)