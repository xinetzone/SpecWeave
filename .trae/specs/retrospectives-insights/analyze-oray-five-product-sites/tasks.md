---
id: "analyze-oray-five-product-sites-tasks"
title: "贝锐五大产品线分析 - 实施计划"
source: "/spec"
date: "2026-07-06"
---

# 贝锐五大产品线官网系统性学习与深度洞察 - The Implementation Plan

## [x] Task 1: 目录创建与准备工作
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 docs/knowledge/learning/07-vendor-product-learning/ 下创建 oray/ 子目录
  - 在 oray/ 下创建 retrospective-oray-comprehensive-analysis-YYYYMMDD/ 复盘目录（日期使用实际执行日期）
  - 读取向日葵复盘目录结构作为参考模板
  - 读取向日葵综合分析 Wiki 的完整章节结构作为参考
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-1.1: oray/ 目录及复盘子目录存在
  - `human-judgement` TR-1.2: 已参考向日葵 Wiki 和复盘文档格式
- **Notes**: 确保目录命名符合 kebab-case 规范

## [ ] Task 2: 贝锐集团官网（www.oray.com）内容提取与分析
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 web-extraction-report skill 提取 https://www.oray.com/ 内容
  - 重点提取：公司介绍、发展历程、产品矩阵、客户案例、资质荣誉、AI战略、品牌定位
  - 整理集团层面的战略定位、五大产品协同逻辑、20周年相关内容
  - 形成独立的单产品（集团层面）分析摘要
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 网页内容成功提取，包含核心板块信息
  - `human-judgement` TR-2.2: 集团战略定位清晰，产品矩阵与协同逻辑明确

## [ ] Task 3: 蒲公英智能组网（pgy.oray.com）内容提取与分析
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 web-extraction-report skill 提取 https://pgy.oray.com/ 内容
  - 重点提取：产品定位、核心功能、SD-WAN技术、硬件产品（路由器等）、版本/价格矩阵、应用场景、客户案例、技术优势
  - 分析蒲公英与其他产品（向日葵/花生壳）的协同点
  - 形成蒲公英独立分析摘要
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 网页内容成功提取，包含功能/价格/场景/技术信息
  - `human-judgement` TR-3.2: 产品定位准确，技术特性分析到位，与其他产品协同点明确

## [ ] Task 4: 花生壳内网穿透（hsk.oray.com）内容提取与分析
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 web-extraction-report skill 提取 https://hsk.oray.com/ 内容
  - 重点提取：产品定位（DDNS/内网穿透）、核心功能、硬件产品（花生棒等）、版本/价格矩阵、应用场景、技术优势
  - 分析花生壳作为"访问层"产品的战略地位
  - 形成花生壳独立分析摘要
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: 网页内容成功提取，包含功能/价格/场景/技术信息
  - `human-judgement` TR-4.2: 产品定位准确，"能访问"这一基础能力的价值分析到位

## [ ] Task 5: 洋葱头企业管理（yct.oray.com）内容提取与分析
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 web-extraction-report skill 提取 https://yct.oray.com/ 内容
  - 如官网信息不足，补充从贝锐集团官网等其他页面提取的洋葱头相关内容
  - 重点提取：产品定位（企业应用管理/身份管理/权限管控）、核心功能、应用场景、企业级特性、与向日葵的协同
  - 形成洋葱头独立分析摘要（如信息有限需注明）
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-5.1: 网页内容提取完成，信息不足时有补充说明
  - `human-judgement` TR-5.2: 洋葱头作为"管理层"产品的定位与价值分析清晰

## [ ] Task 6: 向日葵远程控制（sunlogin.oray.com）补充提取与整合
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 向日葵已有深度分析 Wiki，本次仅需从集团协同视角补充提取官网最新内容
  - 重点关注：与其他四大产品的交叉引用、集团统一活动/促销、AI能力最新进展
  - 整合已有分析成果，不需要重新做全面分析
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `human-judgement` TR-6.1: 向日葵内容与已有 Wiki 整合，突出集团视角的新内容

## [ ] Task 7: 五大产品横向对比分析
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 构建至少10个维度的对比矩阵（战略定位、技术核心、产品形态、目标用户、定价策略、商业模式、硬件生态、AI能力、协同角色、成熟度、典型场景等）
  - 分析差异化定位：为什么需要五个独立产品而不是一个大而全的产品
  - 识别共性特征：跨产品线的设计一致性
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgement` TR-7.1: 对比维度≥10个，矩阵清晰，差异化分析到位
  - `human-judgement` TR-7.2: 共性特征提炼准确

## [ ] Task 8: 产品协同生态与统一范式提炼
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 绘制五大产品协同关系图（使用 Mermaid flowchart）
  - 阐述"能访问（花生壳）→能操作（向日葵）→能组网（蒲公英）→可管理（洋葱头）→AI执行（OrayClaw）"完整闭环
  - 提炼业务模式范式：三层变现漏斗（免费引流→付费增值→硬件/企业级变现）
  - 提炼技术架构范式：硬件端+App端+云端三层架构、本地能力保底+云端增强设计原则
  - 提炼 UX/官网设计范式：B端/C端差异化呈现、信任建立要素、转化路径设计
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `human-judgement` TR-8.1: Mermaid 协同关系图逻辑清晰，闭环完整
  - `human-judgement` TR-8.2: 至少提炼2个业务模式范式和2个技术架构范式，有具体案例支撑
  - `human-judgement` TR-8.3: UX 设计要素分析到位

## [ ] Task 9: 核心洞察萃取
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 产品级洞察：每个产品的独特成功要素与启示
  - 模式级洞察：贝锐20年演进的底层逻辑、多产品矩阵管理方法论
  - 跨领域可复用洞察：对 AI Agent、IoT、SaaS、软硬结合产品的借鉴意义
  - 总计不少于10条核心洞察
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-9.1: 洞察分三个层次，总计≥10条
  - `human-judgement` TR-9.2: 每条洞察有具体分析支撑，不是空泛结论

## [ ] Task 10: 综合分析 Wiki 报告撰写
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 参考向日葵综合分析 Wiki 的12章节结构，撰写贝锐五大产品线综合分析 Wiki
  - 章节建议：
    1. 报告概述与学习目标
    2. 贝锐20年发展与集团战略定位
    3. 五大产品矩阵全景（含各产品独立介绍）
    4. 五大产品横向对比分析
    5. 产品协同生态与闭环逻辑
    6. 统一业务模式深度拆解
    7. 跨产品线技术架构范式
    8. 官网 UX 与转化路径设计分析
    9. 市场策略与客户成功体系
    10. AI 战略与 OrayClaw 生态
    11. 核心洞察与跨领域启示
    12. FAQ 与资源链接
  - 文件命名：oray-comprehensive-analysis-wiki.md
  - 存放路径：docs/knowledge/learning/07-vendor-product-learning/oray/
  - 总字数≥8000字
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-10.1: 章节结构完整（≥12章），逻辑清晰
  - `programmatic` TR-10.2: 文件存在于正确路径，命名符合规范
  - `human-judgement` TR-10.3: 内容充实，总字数≥8000字，有数据/案例支撑
  - `programmatic` TR-10.4: YAML frontmatter 完整（title/source/date/tags）

## [ ] Task 11: 复盘文档四件套生成
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 参考向日葵复盘目录格式，生成四件套：
    1. README.md - 复盘目录索引
    2. execution-retrospective.md - 执行过程复盘（阶段划分、时间线、量化结果、经验总结）
    3. insight-extraction.md - 洞察萃取（方法论、模式、可复用经验）
    4. export-suggestions.md - 导出建议（知识复用指南、关联文档索引）
  - 复盘文档放在 oray/retrospective-oray-comprehensive-analysis-YYYYMMDD/ 目录下
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-11.1: 四个文件均存在，路径正确
  - `human-judgement` TR-11.2: 执行复盘包含阶段、时间线、量化结果、经验
  - `human-judgement` TR-11.3: 洞察萃取区分层次，有具体内容

## [ ] Task 12: 产品索引更新与规范验证
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 更新 sunlogin-product-series-index.md（或创建新的 oray 集团索引，根据实际情况决定），添加贝锐全产品线分析成果入口
  - 运行文件名规范检查脚本：python .agents/scripts/check-filename-convention.py
  - 运行链接有效性检查脚本：python .agents/scripts/check-links.py docs/knowledge/learning/07-vendor-product-learning/oray/
  - 如创建新索引文件，确保命名符合 kebab-case 规范
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-12.1: 索引文档更新完成
  - `programmatic` TR-12.2: 文件名规范检查通过
  - `programmatic` TR-12.3: 链接有效性检查通过
  - `programmatic` TR-12.4: frontmatter 格式验证通过
