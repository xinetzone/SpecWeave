---
id: seven-concepts-prompt-engineering-wiki-spec
title: "七概念驱动的GPT-5.6时代Prompt Engineering Wiki教程 PRD"
category: retrospectives-insights
date: "2026-07-13"
version: "1.0"
status: draft
---

# 七概念驱动的GPT-5.6时代Prompt Engineering Wiki教程 - Product Requirement Document

## Overview
- **Summary**: 创建一份系统整合七概念方法论（R-I-E-C-A-F-V）与OpenAI最新Prompting指南（GPT-5.6时代新范式）的结构化Wiki教程。教程采用原子化Wiki格式，包含目录导航、概念解释、实践案例、应用场景分析、Before/After对照及常见问题解答，覆盖从入门到精通的完整学习路径。
- **Purpose**: 
  1. 将SpecWeave七概念方法论与GPT-5.6时代Prompt Engineering最佳实践深度整合
  2. 解决"模型能力升级但Prompt写法未跟上"的行业痛点
  3. 提供可操作、可验证、可复用的Prompt Engineering知识体系
  4. 为不同知识水平的读者提供分层学习路径
- **Target Users**: 
  - AI应用开发者与Prompt工程师
  - 使用Codex/Cursor等AI编程工具的软件工程师
  - 需要与LLM高效协作的知识工作者
  - SpecWeave方法论实践者与学习者

## Goals
- **G1**: 建立七概念与Prompt Engineering的映射关系，将R-I-E-C-A-F-V方法论转化为Prompt编写的可操作框架
- **G2**: 完整整合两篇OpenAI官方指南的核心内容（Goal-Context-Output-Boundaries四要素、GPT-5.6新范式、6组Before/After对照）
- **G3**: 提供10+个覆盖Chat/Work/Codex三大场景的实战案例与模板
- **G4**: 构建分层学习路径（入门→进阶→专家），适配不同知识水平读者
- **G5**: 包含Prompt质量自检清单、反模式识别、常见问题解答
- **G6**: 遵循SpecWeave Wiki编写规范，采用原子化文件结构与标准化frontmatter
- **G7**: 更新上级目录索引（02-agent-engineering-methodology/README.md），确保文档可发现

## Non-Goals (Out of Scope)
- 不覆盖GPT-4/4o时代的旧版Prompt技巧（如思维链CoT、Few-shot等传统方法，仅在对比时提及）
- 不开发Prompt Engineering自动化工具或代码库
- 不涉及特定垂直领域（如医疗/法律）的专业Prompt模板
- 不包含RAG、Agent框架等上下文工程（Context Engineering）内容（属于后续Harness Engineering范畴）
- 不翻译全文（保留关键英文术语，采用中英对照解释专业概念）

## Background & Context
- **七概念方法论**: SpecWeave项目沉淀的R-I-E-C-A-F-V七概念体系（复盘R、洞察I、萃取E、原子提交C、原子化A、第一性原理F、对抗性审查V），经1258+次提交实战验证，成熟度L2.8
- **网页资源1**: OpenAI官方Prompting指南（Eric Provencher著，Codex DX负责人），提出Goal-Context-Output-Boundaries四要素框架，覆盖Chat/Work/Codex三大场景
- **网页资源2**: GPT-5.6时代新Prompt写法指南，核心观点"少教模型怎么思考，多告诉它你要什么"，提供6组Before/After对照，测试数据显示Eval提升10-15%、Token减少41-66%、成本降低33-67%
- **Wiki规范**: 现有adversarial-review-wiki等成熟Wiki采用原子化文件结构（README.md + 00-overview.md + 01-xx.md + ...），包含YAML frontmatter、分层阅读路径、可信度评级、文档导航表
- **放置位置**: `docs/knowledge/learning/02-agent-engineering-methodology/` 目录下新建子目录 `seven-concepts-prompt-wiki/`

## Functional Requirements
- **FR-1**: 文档结构
  - FR-1.1: 包含README.md索引入页，提供完整文档导航、主题概述、分层阅读路径
  - FR-1.2: 包含00-overview.md概述页，介绍教程定位、学习目标、适用人群、资料可信度说明
  - FR-1.3: 包含01-12共12个原子化章节文件，每个文件聚焦单一主题
  - FR-1.4: 包含13-quick-reference.md速查表，提供核心框架、检查清单、模板快速查阅
  - FR-1.5: 每个文件包含标准化YAML frontmatter（id/title/category/date/version/status）

- **FR-2**: 七概念与Prompt Engineering整合
  - FR-2.1: 建立R-I-E-C-A-F-V到Prompt编写各环节的映射关系（如F第一性原理→目标定义，V对抗性审查→Prompt自检）
  - FR-2.2: 用七概念五层模型（感知→认知→验证→执行→沉淀）解释Prompt编写的认知过程
  - FR-2.3: 提供七概念驱动的Prompt编写工作流（从目标定义到对抗验证的完整闭环）

- **FR-3**: GPT-5.6新范式核心内容
  - FR-3.1: 完整阐述"明确目标而非规定过程"的核心理念，包含OpenAI测试数据（Eval+10-15%、Token-41-66%、成本-33-67%）
  - FR-3.2: 详细解释Goal-Context-Output-Boundaries四要素框架，每个要素配定义、示例、使用要点
  - FR-3.3: 提供应删除的5类冗余内容（无法验证形容词、重复规则、不必要思考流程、无效专家角色、用不上的工具）
  - FR-3.4: 包含6组Before/After完整对照（内容分析、代码生成、翻译、研究分析、Agent工具调用、日常任务）

- **FR-4**: 三大场景实战指南
  - FR-4.1: Chat场景：理解话题、起草文字、比较选项、实用计划等日常用法
  - FR-4.2: Work场景：源材料转成品、决策调研、协调发布等复杂任务
  - FR-4.3: Codex场景：代码库理解、Bug修复、测试编写、截图转原型、UI迭代、重构规划、代码审查、文档更新等8大开发工作流
  - FR-4.4: Steer与Queue机制说明（Codex工作时转向vs排队）

- **FR-5**: 实践工具与模板
  - FR-5.1: Prompt五问自检清单（目标是否清晰？完成标准是否明确？哪些不能猜？哪些不能越界？何时该停止？）
  - FR-5.2: 不同任务复杂度的Prompt长度指南（简单/普通/复杂/Agent编码四级）
  - FR-5.3: 5类反模式识别与修正方案
  - FR-5.4: 可直接复用的Prompt模板库（研究分析、Agent编码、Bug修复等）

- **FR-6**: 辅助内容
  - FR-6.1: 核心术语表（中英文对照、关键概念定义）
  - FR-6.2: 常见问题FAQ（10+个高频问题与解答）
  - FR-6.3: 延伸阅读与资源索引（相关Wiki、官方文档链接）
  - FR-6.4: 可信度评级说明与来源验证

- **FR-7**: 导航与索引更新
  - FR-7.1: 更新02-agent-engineering-methodology/README.md，在子Wiki索引表中添加本教程条目
  - FR-7.2: 在快速导航表中添加Prompt Engineering场景分组
  - FR-7.3: 在推荐学习路径中整合本教程

## Non-Functional Requirements
- **NFR-1**: 可读性
  - NFR-1.1: 语言通俗易懂，关键技术术语保留英文并附中文解释
  - NFR-1.2: 逻辑连贯，章节间有明确的递进关系
  - NFR-1.3: 每个概念配至少1个具体示例，避免纯理论阐述
- **NFR-2**: 可操作性
  - NFR-2.1: 所有Before/After示例可直接复制使用
  - NFR-2.2: 检查清单可打印，采用yes/no判定格式
  - NFR-2.3: 模板包含占位符与填写说明
- **NFR-3**: 规范性
  - NFR-3.1: 遵循SpecWeave Markdown规范（相对路径引用、无file:///绝对路径、标准frontmatter）
  - NFR-3.2: 每个文件≤500行，单一职责
  - NFR-3.3: Mermaid图表遵循安全编码六规则
- **NFR-4**: 可信度
  - NFR-4.1: 关键数据与观点标注来源（OpenAI官方文档/微信文章）
  - NFR-4.2: 区分官方推荐 vs 文章作者解读 vs 七概念整合观点
  - NFR-4.3: 七概念映射关系明确标注为SpecWeave方法论整合，非OpenAI官方内容

## Constraints
- **Technical**: 
  - 纯Markdown格式，使用MyST语法特性
  - Mermaid图表用于可视化框架与流程
  - 遵循现有Wiki原子化结构
- **Business**: 
  - 内容必须基于提供的两个网页资源与七概念理论，不得编造未经验证的"最佳实践"
  - 开源内容，无版权限制
- **Dependencies**:
  - 依赖现有七概念方法论文档（seven-concepts-quick-reference.md等）
  - 依赖02-agent-engineering-methodology/README.md现有结构

## Assumptions
- 读者具备基本的LLM使用经验，知道什么是Prompt
- 目标读者使用GPT-5.6/Claude 3.5+/同等能力水平的模型（旧模型可能不完全适用新范式）
- Wiki放置路径已确定为 `docs/knowledge/learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/`
- 两个微信公众号文章为公开可访问内容，无访问权限问题

## Acceptance Criteria

### AC-1: 文档结构完整性
- **Given**: Wiki教程创建完成
- **When**: 检查目标目录文件列表
- **Then**: 必须包含README.md、00-overview.md、01-12章节目录、13-quick-reference.md共15个文件
- **Verification**: `programmatic`
- **Notes**: 文件命名遵循两位数字前缀+英文kebab-case格式

### AC-2: Frontmatter规范性
- **Given**: 所有Markdown文件创建完成
- **When**: 检查每个文件的YAML frontmatter
- **Then**: 每个文件必须包含id、title、category、date、version、status六个必填字段，格式正确
- **Verification**: `programmatic`

### AC-3: 七概念映射准确性
- **Given**: 阅读02章七概念整合部分
- **When**: 对照七概念方法论原文
- **Then**: R-I-E-C-A-F-V每个概念必须正确映射到Prompt编写环节，不得歪曲七概念原意
- **Verification**: `human-judgment`

### AC-4: 网页内容整合完整性
- **Given**: Wiki教程创建完成
- **When**: 对照两个微信公众号原文
- **Then**: Goal-Context-Output-Boundaries四要素、6组Before/After、5类应删除内容、5问自检清单、三大场景指南必须完整覆盖，不得遗漏核心内容
- **Verification**: `human-judgment`

### AC-5: 示例可操作性
- **Given**: 所有Before/After示例
- **When**: 读者复制"新写法"示例直接使用
- **Then**: 示例必须是完整可运行的Prompt，包含必要上下文，占位符明确标注
- **Verification**: `human-judgment`

### AC-6: 反模式与检查清单
- **Given**: 检查清单章节
- **When**: 逐项检查
- **Then**: 必须包含5个以上可yes/no判定的检查项，5类以上反模式配识别特征与修正方案
- **Verification**: `human-judgment`

### AC-7: 链接有效性
- **Given**: Wiki所有内容完成
- **When**: 运行链接检查脚本 `python .agents/scripts/check-links.py --path docs/knowledge/learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/`
- **Then**: 无断链，无file:///绝对路径，所有内部相对路径正确
- **Verification**: `programmatic`

### AC-8: 导航更新
- **Given**: 上级目录README更新完成
- **When**: 阅读02-agent-engineering-methodology/README.md
- **Then**: 子Wiki索引表必须包含本教程条目，快速导航和学习路径中必须有对应入口
- **Verification**: `human-judgment`

### AC-9: 分层阅读路径
- **Given**: README.md索引入页
- **When**: 阅读"分层次阅读路径"章节
- **Then**: 必须提供至少3条针对不同读者（入门/开发者/研究者）的阅读路径，每条路径有明确目标与步骤
- **Verification**: `human-judgment`

### AC-10: 术语表与FAQ
- **Given**: 术语表和FAQ章节
- **When**: 检查内容
- **Then**: 术语表至少包含15个核心术语，FAQ至少包含10个问题与解答
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要添加Codex CLI/IDE/Codex Cloud三种载体的差异化说明？（第一篇文章有提及，第二篇未强调）
- [ ] 是否需要添加与现有Karpathy四条准则、对抗性审查Wiki的交叉引用说明？
- [ ] 七概念映射部分深度如何把握？是简要对照表还是完整工作流说明？
