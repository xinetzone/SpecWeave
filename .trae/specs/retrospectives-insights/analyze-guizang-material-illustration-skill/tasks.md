# 歸藏材质插画 Skill 开源文章深度洞察分析 - The Implementation Plan

## [x] Task 1: 保存原始文章内容并清理格式
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 将浏览器提取的完整文章文本保存为 article-content.md
  - 保留关键元信息：标题、作者、发布时间、来源URL、GitHub地址、安装命令
  - 清理微信页面的互动元素残留（赞、分享、在看、留言等按钮文字）
  - 保持正文段落结构完整
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: article-content.md文件存在于spec目录下
  - `programmatic` TR-1.2: 文件包含标题、作者、发布时间、GitHub地址、安装命令
  - `human-judgement` TR-1.3: 正文内容完整无缺失，无明显的微信互动按钮文字残留
- **Notes**: 直接使用browser_evaluate提取的innerText内容进行保存

## [x] Task 2: 提炼核心问题与价值主张
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 分析文章开篇背景和"它解决什么问题"章节
  - 识别当前AI配图的两大痛点（截图堆砌vs无意义装饰图）
  - 提炼Skill的核心价值：把概念/流程/数据变成带中文标签的解释图
  - 明确Skill的定位：只负责中心图，不做完整卡片排版或PPT设计
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: 准确识别出2个以上配图痛点
  - `human-judgement` TR-2.2: 价值主张表述清晰，与原文一致
  - `human-judgement` TR-2.3: 定位边界（做什么/不做什么）分析准确
- **Notes**: 重点关注"解释图"vs"装饰图"的本质区别

## [x] Task 3: 萃取5大技术模块实现细节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 详细分析5个技术模块：
    1. 场景适配与统一视觉风格（4类场景+视觉语言体系）
    2. 冷门概念与Logo参考检索（判断逻辑+参考提取+风格统一）
    3. 图内中文标签生成（反模式纠正+标签规范）
    4. 图表语义重绘（vs截图换皮的方案对比）
    5. 反模式纠正与交付前QA审核（5类常见坑+检查清单）
  - 每个模块按"遇到的问题→解决方案→实现细节→效果"结构整理
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: 5个技术模块全部覆盖无遗漏
  - `human-judgement` TR-3.2: 每个模块包含问题、方案、细节三层信息
  - `human-judgement` TR-3.3: 技术细节萃取准确，不曲解原文意思
- **Notes**: 视觉风格部分重点关注"IKB蓝"、"白底工作室光线"、"克制3D材质"等设计关键词

## [x] Task 4: 总结Skill产品化工程方法论
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 基于文章中"从随手写的提示词到正式Skill"的过程描述
  - 提炼从"能跑的提示词"到"别人也能稳定出好图的Skill"的转化路径
  - 总结≥6个关键工程化环节
  - 分析每个环节解决的具体问题
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 提炼出≥6个工程化环节
  - `human-judgement` TR-4.2: 方法论具备可迁移性，不限于图像生成领域
  - `human-judgement` TR-4.3: 每个环节有具体做法描述，而非空泛概念
- **Notes**: 重点关注"提示词工程"到"产品工程"的思维转变

## [x] Task 5: 梳理适用场景与能力边界
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 整理7类适用场景（文章配图、工作汇报、产品机制、数据图表、教学材料、人文配图、社交卡片/PPT主视觉）
  - 整理5类不适用场景（小红书完整排版、PPT结构设计、真实摄影修图、人像写真、长文海报排版）
  - 分析作者"明确说不"的定位哲学
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: 7类适用场景完整列出
  - `programmatic` TR-5.2: 5类不适用场景完整列出
  - `human-judgement` TR-5.3: 对"单一职责"定位哲学的分析到位
- **Notes**: 这是歸藏文章的一贯特点——明确能力边界，值得重点分析

## [x] Task 6: 分析文章结构与内容组织特点
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 梳理文章整体结构脉络（背景→问题→方案分模块→边界→使用→感悟）
  - 分析配图策略（每个技术点配示例图）
  - 总结信息呈现的特点（问题导向、先讲坑再讲方案、明确边界）
  - 对比同类技术文章的写作风格
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 文章结构脉络梳理清晰
  - `human-judgement` TR-6.2: 总结≥3点内容组织特点
  - `human-judgement` TR-6.3: 对写作风格的分析客观准确
- **Notes**: 作者本身是内容创作高手，文章结构本身就是学习对象

## [x] Task 7: 批判性分析与启示提炼
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 识别文章的亮点（≥3个）：工程化思路、边界意识、QA环节设计等
  - 识别潜在局限性/待验证点（≥3个）：仅在GPT-Image 2.0测试、冷门概念检索准确性、标签准确率数据等
  - 提炼对Skill开发的可行动启示（≥5条）：如统一视觉语言的重要性、反模式防范机制、交付前QA、语义抽取vs表面美化等
  - 结合SpecWeave项目思考可借鉴之处
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-7.1: ≥3个亮点识别
  - `programmatic` TR-7.2: ≥3个局限性/待验证点识别
  - `programmatic` TR-7.3: ≥5条可行动启示
  - `human-judgement` TR-7.4: 启示具备实际指导意义，不牵强附会
- **Notes**: 启示部分要结合我们自己做Skill和规范的实际经验

## [x] Task 8: 生成最终洞察分析报告
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 将以上所有分析结果整合为结构化的analysis-report.md
  - 报告包含：执行摘要、文章基本信息、核心问题与价值、技术实现详解、工程化方法论、场景与边界、文章结构分析、批判性思考、可行动启示、总结
  - 确保YAML frontmatter完整规范
  - 所有内部引用使用相对路径
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-8.1: analysis-report.md文件存在
  - `programmatic` TR-8.2: YAML frontmatter包含id、title、date、type、source、theme字段
  - `human-judgement` TR-8.3: 报告结构完整，逻辑流畅，可读性强
  - `human-judgement` TR-8.4: 所有分析结论有原文依据支撑
- **Notes**: 参考同类分析报告的结构和深度
