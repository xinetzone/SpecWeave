# text-to-cad 项目学习与 Wiki 教程文档 - 实施计划

## [x] Task 1: 创建Wiki教程文档基础框架与目录导航
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在docs/knowledge/learning/目录下创建text-to-cad-wiki.md文件
  - 添加符合规范的TOML frontmatter（title/source/date/tags）
  - 创建完整的目录导航系统，包含所有章节的锚点链接
  - 添加原文参考和GitHub项目链接的开头引用
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-9]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于正确路径docs/knowledge/learning/text-to-cad-wiki.md
  - `programmatic` TR-1.2: frontmatter包含所有必填字段（title/source/date/tags）
  - `human-judgement` TR-1.3: 目录导航结构完整，所有章节链接可跳转
  - `programmatic` TR-1.4: 包含原文URL和GitHub项目URL
- **Notes**: 参考the-agency-project-wiki.md的文档结构和格式

## [x] Task 2: 编写项目概述与核心价值章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 介绍传统AI CAD设计的三个痛点：STL网格不可编辑、STEP格式需重建几何体、URDF手动编写易出错
  - 引出text-to-cad项目：面向Agent的CAD技能库，7400+ GitHub stars
  - 用一句话概括核心价值：用AI写可编辑的CAD源代码，导出STEP/URDF等工程文件
  - 设计演示场景引入（机器人底盘设计示例）
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 清晰阐述3个传统CAD痛点
  - `human-judgement` TR-2.2: 准确介绍项目定位和star数量
  - `human-judgement` TR-2.3: 核心价值概括准确易懂
  - `human-judgement` TR-2.4: 适当引用原文内容

## [x] Task 3: 编写5大核心功能详解章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 功能1：参数化CAD源码生成 - Build123d Python源码、@cad[feature_name]标记、可直接修改参数、STEP导出可导入SolidWorks编辑
  - 功能2：机器人描述文件自动生成 - URDF XML自动生成、links/joints/limits自动写入、关节限位/坐标系/惯性参数合法性校验、配合CAD Viewer本地查看
  - 功能3：标准件库内置 - step.parts catalog提供螺丝/轴承/电机等标准件、使用可实际购买的标准件、避免"设计好但买不到螺丝"问题
  - 功能4：本地浏览器预览器 - WebGL渲染、浏览器原生运行无需专业CAD软件、支持STEP/STL/URDF、轨道旋转/组件树浏览、手机端查看、@cad引用复制、正交/透视投影、GLSL光线步进（试验性）
  - 功能5：DXF工程图和G-code切片 - 3D几何投影生成2D DXF（激光切割/钣金）、自动生成钣金展开/垫片/切割布局、切片器CLI生成G-code、对接Bambu Labs打印机、SendCutSend下单前文件检查
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 5个功能每个都有详细说明
  - `human-judgement` TR-3.2: 每个功能说明包含技术原理和应用价值
  - `human-judgement` TR-3.3: 技术术语解释准确
  - `human-judgement` TR-3.4: 使用表格或列表清晰组织内容

## [x] Task 4: 编写安装配置指南章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - Skills CLI安装命令：npx skills install earthtojake/text-to-cad
  - Claude Code插件安装：claude plugin marketplace add和claude plugin install命令
  - Python CAD环境配置：Python 3.11 venv创建、pip安装requirements-cad.txt
  - Viewer前端启动：npm install和npm run dev命令、访问http://localhost:4178
  - 各步骤说明清晰，命令可直接复制执行
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 4个安装部分完整
  - `programmatic` TR-4.2: 所有命令代码块格式正确
  - `human-judgement` TR-4.3: 步骤说明清晰易懂
  - `human-judgement` TR-4.4: 包含必要的注意事项

## [x] Task 5: 编写完整使用流程演示章节
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 以机器人底盘设计为例演示完整工作流
  - 步骤1：自然语言描述需求（"生成一个矩形底座，有四个安装孔和两个电机支架"）
  - 步骤2：AI自动编写Build123d Python源码（每个几何特征用代码定义：孔位、支架大小、底座厚度）
  - 步骤3：自动导出STEP文件（可直接导入SolidWorks编辑）
  - 步骤4：生成URDF机器人描述（links/joints/坐标系写入XML，ROS MoveIt2可直接加载）
  - 强调整个过程只需要一句话，后续工作全部自动化完成
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 工作流步骤完整（从自然语言到制造文件）
  - `human-judgement` TR-5.2: 以机器人底盘为示例贯穿始终
  - `human-judgement` TR-5.3: 清晰展示"自然语言→CAD→机器人描述→制造文件"链路价值
  - `human-judgement` TR-5.4: 适当引用原文描述

## [x] Task 6: 编写局限性与边界说明章节
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 客观说明Implicit CAD还是试验性功能，不完善
  - Viewer开发需要Node环境，对纯Python用户有门槛
  - Git LFS资产默认不拉取，需手动执行git lfs pull命令
  - 没有中文文档，README和SKILL.md都是英文
  - 没有对复杂装配体生成效果进行验证，目前只做了单个零件的benchmark
  - OpenCascade和step.parts库的商业许可证需自行查阅
  - 适用场景说明：需要工程级可编辑模型时使用，只需要漂亮3D图则没必要
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 列出至少6个局限性
  - `human-judgement` TR-6.2: 表述客观中立，不夸大不贬低
  - `human-judgement` TR-6.3: 包含适用场景和不适用场景说明

## [x] Task 7: 编写核心价值总结与展望章节
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 总结text-to-cad的设计思路正确性：让AI生成CAD源码而非黑盒模型
  - 阐述参数化修改的价值：改孔位不需要重画整个零件
  - 强调代码化的优势：尺寸、基准、装配关系都在代码里，一目了然
  - 重申最大价值：打通"自然语言→CAD→机器人描述→制造文件"全链路
  - 开源协议说明：MIT协议开放
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 核心价值总结到位
  - `human-judgement` TR-7.2: 与开头痛点形成呼应
  - `human-judgement` TR-7.3: 语言精炼有洞察力

## [x] Task 8: 编写FAQ常见问题解答章节
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 整理常见问题并提供解答，如：
    - Q: text-to-cad适合什么场景使用？
    - Q: 生成的STEP文件真的可以在SolidWorks中编辑吗？
    - Q: 必须使用Claude Code吗？支持其他AI编程工具吗？
    - Q: 标准件库包含哪些类型的零件？
    - Q: 没有Python基础可以使用吗？
    - Q: 生成的模型可以直接用于3D打印吗？
    - Q: 项目还在积极维护吗？
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 至少包含7个FAQ问题
  - `human-judgement` TR-8.2: 问题具有实际参考价值
  - `human-judgement` TR-8.3: 解答清晰准确

## [x] Task 9: 编写相关资源链接章节
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - GitHub项目地址：https://github.com/earthtojake/text-to-cad
  - 原文链接：微信公众号文章URL
  - Build123d相关资源（如适用）
  - 相关CAD/机器人技术资源
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-9.1: GitHub链接正确
  - `programmatic` TR-9.2: 原文链接正确
  - `human-judgement` TR-9.3: 资源分类清晰

## [x] Task 10: 更新知识库索引README.md
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 在docs/knowledge/README.md的learning分类表格中新增text-to-cad教程条目
  - 条目包含：标题、摘要、日期（2026-07-04）、标签（text-to-cad、cad、ai-agent、build123d、step、urdf、3d-printing、robotics）
  - 遵循现有索引格式，保持表格结构一致
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-10.1: README.md中learning分类新增了条目
  - `human-judgement` TR-10.2: 摘要准确概括教程内容
  - `human-judgement` TR-10.3: 标签设置合理
  - `programmatic` TR-10.4: 表格格式保持一致
