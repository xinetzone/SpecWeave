---
id: "okf-open-knowledge-format-wiki-tasks"
title: "OKF开放知识格式Wiki教程任务分解"
source: "seven-concepts knowledge-scenario: okf-wiki"
date: "2026-08-05"
---

# OKF开放知识格式Wiki教程 - The Implementation Plan

## [x] Task 1: 内容准备与格式确认
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 补充获取剩余2篇知乎文章完整内容（URL2: 2051665837967380596, URL3: 2050505404975788824）
  - 尝试获取GitHub GoogleCloudPlatform/knowledge-catalog仓库OKF目录内容
  - 读取2-3个现有原子化wiki样例（volcengine-agentkit-wiki、agent-communication-protocols）的完整frontmatter和格式
  - 确认目标输出目录`d:\AI\.agents\docs\knowledge\learning\01-agent-protocols-interfaces\okf-wiki\`不存在或为空
  - 创建输出目录
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 输出目录`okf-wiki/`创建成功
  - `human-judgement` TR-1.2: 确认现有wiki的frontmatter字段、标题层级、链接格式规范
  - `human-judgement` TR-1.3: 所有来源资料（官网+GitHub+3篇知乎）收集完毕
- **Notes**: 使用集成浏览器获取知乎内容；GitHub可尝试raw.githubusercontent.com获取

## [x] Task 2: 创建00-overview.md教程总览
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建概述章节，包含：
    - OKF是什么（一句话定义+核心定位"AI时代的HTML"）
    - 背景与动机（知识碎片化、平台锁定、Agent知识层缺失问题）
    - 学习目标（3-5条）
    - 前置知识要求
    - 章节导航表（8个章节+预计阅读时间+适合人群）
    - 三条阅读路径（快速上手/深度开发/架构决策）
    - ⚠️ V0.1早期版本警示（放在导航前显著位置）
    - Mermaid图：Agent四层架构定位图（模型→MCP→Skills→OKF知识层）
    - Mermaid图：OKF Bundle结构示意图
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5, AC-6, AC-7, AC-11
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件创建成功，frontmatter字段完整
  - `human-judgement` TR-2.2: 导航表包含所有章节，阅读时间合理
  - `human-judgement` TR-2.3: V0.1警示位置显著，表述清晰
  - `human-judgement` TR-2.4: Mermaid图表语法正确，信息表达清晰
  - `human-judgement` TR-2.5: 学习目标明确可衡量

## [x] Task 3: 创建01-core-concepts.md核心概念
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建核心概念章节，包含：
    - 三大设计原则深度解读（每个原则配解释+设计权衡+为什么）
    - 术语对照表（Bundle/Concept/Concept ID/Frontmatter/Body/Link/Citation）
    - Bundle目录结构规范（保留文件名index.md/log.md说明）
    - Concept文件结构（frontmatter必填/推荐字段详解+扩展字段机制）
    - Body编写规范（推荐标题：Schema/Examples/Citations）
    - 跨链接规则（绝对链接/相对链接/断链是特性不是bug）
    - Index Files规范与自动化脚本示例
    - Log Files规范与git log区别
    - Citations引用规范（为什么对Agent重要）
    - 三个完整代码示例（BigQuery Table / Playbook / Metric）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-11
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件创建成功，frontmatter正确
  - `human-judgement` TR-3.2: 三大设计原则解释清晰，有权衡分析
  - `human-judgement` TR-3.3: 所有术语有明确定义
  - `human-judgement` TR-3.4: 三个代码示例完整可参考
  - `human-judgement` TR-3.5: frontmatter字段说明准确完整（必填/推荐/扩展）

## [x] Task 4: 创建02-quickstart.md快速入门
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 创建快速入门章节（OKF零安装，直接实操）：
    - 什么是Bundle（10秒快速解释）
    - 最终目录结构展示
    - Step 1: 创建目录
    - Step 2: 创建第一个Concept（选择AI Agent场景示例，如Agent常用工具文档）
    - Step 3: 创建第二个Concept（交叉链接示例）
    - Step 4: 创建第三个Concept
    - Step 5: 创建index.md
    - Step 6: 创建log.md
    - 快速验证三规则检查清单
    - 你刚刚构建了什么（知识图谱）说明
    - 下一步建议
  - 说明：OKF不需要"安装"，零依赖，所以章节命名为quickstart而非installation
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件创建成功，frontmatter正确
  - `human-judgement` TR-4.2: 6个步骤清晰，每个步骤有完整代码块可复制
  - `human-judgement` TR-4.3: 示例场景贴合AI Agent开发者（而非纯SaaS指标）
  - `human-judgement` TR-4.4: 三规则验证清单明确可检查
  - `human-judgement` TR-4.5: 按步骤操作可在5分钟内完成完整Bundle

## [x] Task 5: 创建03-usage-patterns.md使用模式与最佳实践
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 创建使用模式章节，包含：
    - 三种典型使用场景（数据目录/Agent知识库/团队Playbook）
    - 场景1：数据目录（表/指标/字段文档化示例）
    - 场景2：Agent Skills配套知识（工具说明/API文档/使用示例）
    - 场景3：团队运维Playbook（故障处理/Runbook）
    - frontmatter扩展字段最佳实践（owner/freshness_sla/confidence等）
    - 链接设计最佳实践（什么时候用绝对/相对链接）
    - 渐进式文档化策略（先引用后填充，断链是特性）
    - index.md自动化脚本（Python版+Shell版）
    - 与Git工作流结合（分支/PR/Code Review知识变更）
    - SemVer版本管理建议
- **Acceptance Criteria Addressed**: AC-2, AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件创建成功，frontmatter正确
  - `human-judgement` TR-5.2: 三个场景各有具体示例和适用边界
  - `human-judgement` TR-5.3: 自动化脚本可运行
  - `human-judgement` TR-5.4: 最佳实践可落地操作

## [x] Task 6: 创建04-limitations-and-comparison.md局限性与对比
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 创建局限性与对比章节，包含：
    - ⚠️ V0.1版本状态警示（发布仅2个月/2026年6月发布/Draft状态）
    - 已知局限性（不做什么/Non-Goals深度解读）
    - Google产品历史风险提示（Reader/Knork/Inbox等前车之鉴）
    - 生态成熟度评估（工具链/社区/案例现状）
    - 不适用场景（什么时候不该用OKF）
    - 对比表格：OKF vs 8种替代方案
      - OKF vs 纯Markdown无结构
      - OKF vs Notion/Confluence（闭源Wiki）
      - OKF vs Obsidian（个人知识管理）
      - OKF vs 专有向量库RAG（仅切块无元数据）
      - OKF vs 知识图谱/本体（复杂RDF/OWL）
      - OKF vs OpenAPI/Swagger（API规范）
      - OKF vs Protobuf/Avro（数据序列化）
      - OKF vs dbt docs（数据文档）
    - 选型决策树（什么时候选OKF/什么时候选别的）
- **Acceptance Criteria Addressed**: AC-2, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件创建成功，frontmatter正确
  - `human-judgement` TR-6.2: V0.1风险提示充分醒目，不回避问题
  - `human-judgement` TR-6.3: 8种方案对比客观，各有优缺点
  - `human-judgement` TR-6.4: 决策树清晰可指导选型

## [x] Task 7: 创建05-architecture-and-integration.md架构定位与Agent集成
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 创建架构与集成章节，包含：
    - Agent四层架构详解（模型层/MCP连接层/Skills程序层/OKF知识层）
    - Mermaid图：四层架构依赖关系图
    - 为什么知识层要独立（不商品化的企业护城河）
    - OKF与MCP的关系（互补而非竞争）
    - OKF与Skills的关系（Skills是程序，OKF是知识）
    - Agent如何消费OKF Bundle（读取index→类型路由→章节检索）
    - 生产者-消费者解耦架构（人写/Agent生成/Agent消费/可视化浏览）
    - Mermaid图：知识生产消费流程图
    - 企业落地四阶段路径：
      - 阶段1：试点（新文档开始用OKF格式）
      - 阶段2：单领域（选一个业务域全面采用）
      - 阶段3：Agent集成（Agent优先访问OKF知识）
      - 阶段4：治理（建立审核/验证/更新流程）
    - 与SpecWeave现有知识库的结合思考
- **Acceptance Criteria Addressed**: AC-2, AC-6, AC-9, AC-11
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件创建成功，frontmatter正确
  - `human-judgement` TR-7.2: 四层架构解释清晰，OKF定位准确
  - `human-judgement` TR-7.3: OKF与MCP/Skills关系阐述清楚
  - `human-judgement` TR-7.4: 四阶段落地路径具体可执行
  - `human-judgement` TR-7.5: 两个Mermaid图表语法正确有信息量

## [x] Task 8: 创建06-faq-and-best-practices.md FAQ与最佳实践
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 创建FAQ章节，包含10-12个常见问题：
    - Q1: OKF和Obsidian有什么区别？我直接用Obsidian不行吗？
    - Q2: 为什么不用JSON Schema/Protobuf来定义知识结构？
    - Q3: OKF需要数据库吗？怎么和向量检索结合？
    - Q4: type字段可以随便写吗？会不会乱？
    - Q5: 现有Markdown文档怎么迁移到OKF？
    - Q6: 企业内多团队使用如何统一type命名？
    - Q7: OKF有没有官方验证工具？
    - Q8: OKF支持多语言吗？
    - Q9: 大文件要不要拆分？拆分原则是什么？
    - Q10: OKF未来会收费吗？会被Google锁定吗？
    - Q11: 图片/二进制资源怎么处理？
    - Q12: 如何处理权限/敏感信息？
  - 8条最佳实践（来自spec和实践经验）
  - 生产上线检查清单（10项）
- **Acceptance Criteria Addressed**: AC-2, AC-10
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件创建成功，frontmatter正确
  - `human-judgement` TR-8.2: 至少10个FAQ，问题真实有代表性
  - `human-judgement` TR-8.3: 答案简明准确，有可操作性
  - `human-judgement` TR-8.4: 最佳实践和检查清单实用

## [x] Task 9: 创建07-resources-and-glossary.md资源与术语表
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - 创建资源与术语表章节：
    - 完整术语表（20+术语，带定义）
    - 官方资源链接：
      - 官网 okf.md
      - 官方spec页面
      - quickstart页面
      - validator工具
      - skill安装页面
      - GitHub仓库链接
    - 知乎深度分析文章链接（3篇）
    - 相关标准链接（Markdown/YAML/OpenAPI等）
    - 本项目相关wiki交叉引用：
      - agent-skills-wiki
      - agent-communication-protocols
      - mcp相关wiki
      - seven-concepts相关wiki
    - 延伸阅读建议
- **Acceptance Criteria Addressed**: AC-2, AC-10
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件创建成功，frontmatter正确
  - `human-judgement` TR-9.2: 术语表20+术语，定义准确
  - `human-judgement` TR-9.3: 所有来源链接完整（官网+GitHub+3篇知乎）
  - `human-judgement` TR-9.4: 交叉引用路径正确

## [x] Task 10: 创建README.md入口与目录索引更新
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 创建okf-wiki/README.md入口文件
  - 更新父目录README/索引：
    - 检查`01-agent-protocols-interfaces/README.md`
    - 添加okf-wiki条目
    - 确保导航可见
  - 检查并更新必要的分类索引
- **Acceptance Criteria Addressed**: AC-1, AC-12
- **Test Requirements**:
  - `programmatic` TR-10.1: README.md创建成功
  - `human-judgement` TR-10.2: README包含wiki简介、章节导航
  - `human-judgement` TR-10.3: 父目录索引已更新，可发现新wiki

## [x] Task 11: 全局链接检查与格式校验
- **Priority**: high
- **Depends On**: Task 10
- **Description**: 
  - 运行链接检查，验证所有文件间相对链接正确
  - 统一检查所有文件frontmatter格式一致性
  - 检查三级标题编号是否为x.y格式（无x.0）
  - 检查所有代码块语法标记正确
  - 检查Mermaid图表语法
  - 通读全文，检查术语一致性、语言风格统一
  - 修复发现的问题
- **Acceptance Criteria Addressed**: AC-2, AC-11, AC-12
- **Test Requirements**:
  - `programmatic` TR-11.1: 所有内部相对链接指向文件存在
  - `human-judgement` TR-11.2: frontmatter字段在所有文件中保持一致
  - `human-judgement` TR-11.3: 三级标题编号正确
  - `human-judgement` TR-11.4: 通读后无明显错别字、术语不一致
