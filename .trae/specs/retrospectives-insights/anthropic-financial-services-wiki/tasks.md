# Anthropic Financial Services 金融Agent仓库 Wiki教程 - The Implementation Plan

## [x] Task 0: L1-L3 前置准备（已完成）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - L1：使用defuddle提取原始网页内容，去噪后保存到.temp/
  - L2：通读并标记核心观点，识别关键概念和术语
  - L3：完成spec.md，明确原子化决策（保持单文件）
- **Acceptance Criteria Addressed**: AC-1（内容完整性基础）
- **Test Requirements**:
  - `human-judgement` TR-0.1: 网页内容提取完整，无广告/导航/评论区噪音
  - `human-judgement` TR-0.2: 已识别核心观点：四层架构、10大模块、模板定位、人工审核
- **Notes**: L1-L3已在Spec阶段完成

## [ ] Task 1: L4 创建Wiki文档骨架与frontmatter
- **Priority**: high
- **Depends On**: Task 0
- **Description**: 
  - 创建文件 `docs/knowledge/learning/anthropic-financial-services-wiki.md`
  - 添加正确的YAML frontmatter（---分隔），包含title/source/date/tags字段
  - 以现有Wiki文档格式为准（参考declarative-partial-updates-wiki.md）
  - 添加一级标题和原文引用区块
  - 添加目录导航（11个章节锚点链接）
- **Acceptance Criteria Addressed**: AC-2（格式规范）
- **Test Requirements**:
  - `programmatic` TR-1.1: frontmatter使用---分隔，字段完整（title/source/date/tags）
  - `human-judgement` TR-1.2: 目录导航完整，锚点链接格式正确
  - `programmatic` TR-1.3: 文件名为kebab-case纯英文：anthropic-financial-services-wiki.md
- **Notes**: 按"格式一致性优先原则"，先创建基础骨架再填充内容

## [ ] Task 2: 填充概述、架构、功能模块章节（第一至三章）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 第一章：项目概述与背景（GitHub 3.2万Star、Anthropic官方、四大垂直领域）
  - 第二章：核心定位与四层架构（Agent/Skill/Slash Command/MCP Connector详解）
  - 第三章：十大核心功能模块详解（每个模块的价值、适用场景、关键细节）
  - 对金融术语进行括号注释解释（DCF/LBO/comps/KYC/GL等）
- **Acceptance Criteria Addressed**: AC-1（内容完整性）、AC-4（局限性客观）
- **Test Requirements**:
  - `human-judgement` TR-2.1: 四层架构解释清晰，每层的作用和关系明确
  - `human-judgement` TR-2.2: 10大功能模块无遗漏，每个模块有独立小节
  - `human-judgement` TR-2.3: 金融术语有通俗易懂的解释
  - `human-judgement` TR-2.4: /debug-model的价值（查硬编码/错链/假平）有具体示例说明
- **Notes**: Pitch Agent的"流水线而非写作文"观点、/debug-model的具体错误示例是重点亮点

## [ ] Task 3: 填充快速上手、源码结构、定制化章节（第四至六章）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 第四章：快速上手指南（插件市场添加、核心插件安装、顺序建议、避坑提示）
  - 第五章：源码结构与学习路径（按学习目的推荐目录：agent-plugins/vertical-plugins/managed-agent-cookbooks/MCP配置）
  - 第六章：企业定制化方法（5种方式：换数据连接器、加公司上下文、用自己的模板、调整代理范围、加自定义工作流）
  - 所有安装命令使用代码块，可直接复制
- **Acceptance Criteria Addressed**: AC-3（快速上手可复现）
- **Test Requirements**:
  - `human-judgement` TR-3.1: 安装命令语法正确，使用bash代码块
  - `human-judgement` TR-3.2: 插件安装顺序建议明确（先financial-analysis再加垂直插件）
  - `human-judgement` TR-3.3: 避坑提示清晰（不要全装、MCP连接器不是免费数据）
  - `human-judgement` TR-3.4: 5种定制化方法每种都有具体操作说明
- **Notes**: 特别强调"不要一上来全装"和"MCP是企业路线图不是白嫖数据包"两个避坑点

## [ ] Task 4: 填充法律免责、评估、见解章节（第七至九章）
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 第七章：法律免责与人工审核（突出draft定位、人工签字责任、合规要求，引用Anthropic官方免责原文）
  - 第八章：内容三维评估（准确性/权威性/实用性各维度评分和理由）
  - 第九章：个人见解与行业启示（垂直行业Agent的正确落地路径：模板+定制+人工审核，聊天只是入口不是工作流）
- **Acceptance Criteria Addressed**: AC-4（局限性客观）、AC-5（法律免责突出）
- **Test Requirements**:
  - `human-judgement` TR-4.1: 法律免责声明位置显眼，内容完整（不构成投资/法律/税务建议）
  - `human-judgement` TR-4.2: 明确强调"所有输出必须人工审核，你才是负责人"
  - `human-judgement` TR-4.3: 三维评估客观中立，有评分有理由
  - `human-judgement` TR-4.4: 个人见解有深度，不只是复述原文
- **Notes**: 法律免责章节必须严肃认真，不能一笔带过

## [ ] Task 5: 填充FAQ、资源链接并更新知识库索引（第十至十一章）
- **Priority**: medium
- **Depends On**: Task 4
- **Description**: 
  - 第十章：常见问题FAQ（8个问题，如"个人开发者能用吗"、"需要付费数据源吗"、"能直接给投资建议吗"等）
  - 第十一章：相关资源链接（GitHub仓库、相关Wiki教程）
  - 更新 `docs/knowledge/README.md`，在learning分类下添加本Wiki条目
- **Acceptance Criteria Addressed**: AC-1（内容完整性）、AC-6（资源链接有效）
- **Test Requirements**:
  - `human-judgement` TR-5.1: FAQ覆盖8个以上读者最可能问的问题
  - `programmatic` TR-5.2: GitHub仓库链接正确：https://github.com/anthropics/financial-services
  - `human-judgement` TR-5.3: 知识库索引已更新，条目格式与现有条目一致
- **Notes**: FAQ需站在读者角度思考真实疑问

## [ ] Task 6: 元数据补全与格式验证
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 运行fix-x-toml-ref.py自动添加x-toml-ref字段并创建TOML文件
  - 运行check-filename-convention.py验证文件名规范
  - 运行check-links.py验证链接有效性
  - 通读全文检查逻辑连贯性和术语一致性
  - 检查"子代理产出验收5点检查"
- **Acceptance Criteria Addressed**: AC-2（格式规范）、AC-6（资源链接有效）
- **Test Requirements**:
  - `programmatic` TR-6.1: fix-x-toml-ref.py执行成功，x-toml-ref路径正确
  - `programmatic` TR-6.2: check-filename-convention.py通过，无文件名违规
  - `programmatic` TR-6.3: check-links.py通过，无断链
  - `human-judgement` TR-6.4: 子代理验收5点全部通过（YAML分隔符/x-toml-ref/标题层级/文件名/source溯源）
- **Notes**: 使用自动化工具而非手动计算路径

## [ ] Task 7: 原子提交
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 原子提交，格式：docs(knowledge): 新增Anthropic Financial Services金融Agent仓库学习Wiki教程
  - 提交包含：新Wiki文件 + README.md索引更新
  - 不包含临时文件（.temp/目录下的内容不提交）
- **Acceptance Criteria Addressed**: 全部AC
- **Test Requirements**:
  - `programmatic` TR-7.1: git status确认只有预期文件被修改
  - `human-judgement` TR-7.2: commit message符合Conventional Commits规范
  - `human-judgement` TR-7.3: 单次提交单一职责，无无关文件混入
- **Notes**: 单一职责提交，不与其他改动混提
