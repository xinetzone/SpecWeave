# MopMonk 安全 Agent 系统 Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 基于微信公众号文章《中国AI扫地僧杀入全球前七！MopMonk紧咬OpenAI，无人知其真身》，创建一份结构清晰、内容全面的Wiki技术教程，系统介绍MopMonk安全多Agent系统的核心概念、技术架构和关键洞察，帮助读者理解AI安全Agent领域的最新进展。
- **Purpose**: 将新闻报道转化为系统化的技术学习资料，帮助AI安全研究者、Agent开发者和技术爱好者理解MopMonk的技术路线（结构化记忆+多Agent并行+基座模型耦合），以及CyberGym基准测试的意义，为AI安全Agent开发提供参考。
- **Target Users**: AI安全研究人员、大模型应用开发者、Agent系统架构师、网络安全从业者、对AI前沿技术感兴趣的技术学习者。

## Goals
- 系统梳理MopMonk（扫地僧）安全Agent的核心技术架构与创新点
- 解释CyberGym基准测试的设计理念、评估维度与行业意义
- 阐明Harness（协调层）在Agent系统中的关键作用与价值
- 提供结构化的学习路径，帮助不同技术水平的读者理解内容
- 整理相关资源链接，方便读者深入研究
- 准确反映原网页信息，不添加未经证实的内容

## Non-Goals (Out of Scope)
- 不提供MopMonk系统的完整复现指南（官方未开源完整代码）
- 不猜测或证实MopMonk团队的真实身份
- 不进行其他AI安全Agent系统的横向对比评测
- 不涉及具体漏洞挖掘技术的实操教学
- 不创建交互式演示或代码示例

## Background & Context
- MopMonk（扫地僧）是2026年7月前后横空出世的神秘中国AI安全团队，以73.1%的成功率位列CyberGym全球第七、中国第一
- CyberGym是UC Berkeley团队打造的AI网络安全能力评估基准，论文入选ICLR 2026，包含1507个真实漏洞实例、188个开源项目，体量是NYU CTF的7.5倍
- MopMonk基于MiniMax M3（上海公司开源模型）构建，核心创新在于为漏洞挖掘量身定制的Harness层，包含结构化漏洞记忆、记忆驱动挖掘、多Agent并行探索三大核心技术
- 文章揭示了AI竞争从"堆参数"转向"拼Agent执行力"的行业趋势

## Functional Requirements
- **FR-1**: 教程必须包含清晰的目录导航系统，方便读者快速定位内容
- **FR-2**: 提供教程概述与学习目标，明确读者预期收获和前置知识要求
- **FR-3**: 系统解析核心概念，包括但不限于：CyberGym基准、Harness协调层、PoC（概念验证）、结构化漏洞记忆、多Agent并行探索、MiniMax M3基座
- **FR-4**: 提供步骤式内容导读指南，按技术深度分层组织（入门→进阶→深入）
- **FR-5**: 包含常见问题解答（FAQ）章节，解答读者可能产生的疑问
- **FR-6**: 整理并提供相关资源链接（论文、GitHub仓库、相关基准）
- **FR-7**: 所有技术表述必须准确反映原文内容，关键数据必须与原文一致
- **FR-8**: 语言通俗易懂，对专业术语提供必要的解释说明

## Non-Functional Requirements
- **NFR-1**: 文档结构清晰，使用Markdown标准格式，层级分明
- **NFR-2**: 适合不同技术水平的读者阅读：入门读者能理解基本概念，进阶读者能把握技术架构
- **NFR-3**: 关键术语首次出现时提供简明解释
- **NFR-4**: 派生产物在TOML frontmatter中携带source字段标注来源
- **NFR-5**: 文件命名遵循kebab-case规范，使用纯英文

## Constraints
- **Technical**: 使用标准Markdown格式；遵循项目文档命名规范；存放在docs/knowledge/learning/目录下
- **Business**: 教程内容必须基于原文章，不得编造未提及的技术细节；尊重原作者知识产权
- **Dependencies**: 原文章内容、GitHub公开技术报告、CyberGym论文链接

## Assumptions
- 原文章内容准确可信，技术数据真实可靠
- MopMonk GitHub仓库（https://github.com/MopMonkAI/MopMonkAgent）是官方公开资源
- 读者具备基础的AI/大模型概念，了解Agent基本含义
- 教程将作为技术知识库资料归档，供后续查阅参考

## Acceptance Criteria

### AC-1: 文档结构完整性
- **Given**: Wiki教程已创建完成
- **When**: 审阅文档结构
- **Then**: 包含以下所有必需章节：教程概述与学习目标、目录导航、核心概念解析、步骤式导读指南、常见问题解答、相关资源链接
- **Verification**: `human-judgment`
- **Notes**: 章节顺序应符合学习逻辑，从易到难

### AC-2: 核心概念准确解析
- **Given**: Wiki教程核心概念章节
- **When**: 对照原文检查技术表述
- **Then**: CyberGym、Harness、结构化漏洞记忆、三大核心技术等关键概念的解释与原文一致；关键数据（73.1%成功率、1507个漏洞、188个项目、SWE-Bench Pro 59.0%等）准确无误
- **Verification**: `human-judgment`

### AC-3: 内容通俗易懂
- **Given**: 完整Wiki教程
- **When**: 非AI安全专业的技术读者阅读
- **Then**: 能够理解MopMonk的核心创新点和行业意义，专业术语有解释说明
- **Verification**: `human-judgment`

### AC-4: 资源链接有效性
- **Given**: 相关资源链接章节
- **When**: 检查所有提供的URL
- **Then**: CyberGym论文链接、MopMonk GitHub链接正确完整；链接格式规范
- **Verification**: `programmatic`

### AC-5: 格式规范符合要求
- **Given**: 已创建的Wiki教程文件
- **When**: 检查文件格式和命名
- **Then**: 文件使用标准Markdown格式；文件名遵循kebab-case纯英文；包含正确的TOML frontmatter（含source字段）；存放路径正确（docs/knowledge/learning/）
- **Verification**: `programmatic` + `human-judgment`

### AC-6: FAQ覆盖常见疑问
- **Given**: FAQ章节
- **When**: 审阅FAQ内容
- **Then**: 至少包含5个常见问题及解答，覆盖身份之谜、技术原理、与传统方法区别、学习路径、行业影响等方面
- **Verification**: `human-judgment`

## Open Questions
- [ ] 教程最终的文件命名应如何确定？（建议：mopmonk-security-agent-wiki.md）
- [ ] 是否需要添加Mermaid图表来可视化MopMonk技术架构？
- [ ] 步骤式操作指南是指学习导读步骤，还是读者需要实操的技术步骤？（原文没有具体操作教程，建议按分层学习导读设计）
