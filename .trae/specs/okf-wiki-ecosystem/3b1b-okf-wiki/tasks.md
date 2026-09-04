# 3Blue1Brown 生态 OKF Wiki 教程生成 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: manim 知识包 R 阶段 - 源码事实采集
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 按模块阅读 `external/dao/action/3b1b/manim/manimlib/` 核心源码
  - 重点模块：animation/、camera/、mobject/、renderer/、scene/、shaders/、utils/、config.py、constants.py、__init__.py
  - 提取编号事实 F-001~F-xxx，写入 `doc/bundles/viz/3b1b/manim/spec/facts.md`
  - 事实要求：零推测，只记录"代码中有什么"（类名、方法签名、继承关系、字段、常量、数据流）
  - 识别核心类：Scene、Mobject、Animation、Camera、Renderer、VMobject、Group 等
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: facts.md 中每条事实包含源码路径引用
  - `programmatic` TR-1.2: 事实中无"用于"/"目的是"/"设计为"等推断词
  - `human-judgement` TR-1.3: 核心模块覆盖完整（animation/camera/mobject/renderer/scene/config）
- **Notes**: 使用 general_purpose_task 委派子代理执行，分批阅读（每批 2-3 个模块）

## [x] Task 2: manim 知识包 I 阶段 - 架构洞察与知识结构设计
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 facts.md，提炼 3-5 个核心架构洞察（陈述+证据+反常识+行动四元组）
  - 设计知识地图：概念文档分组与学习路径（基础→核心→高级）
  - 确定每个概念文档覆盖哪些 F-xxx 事实
  - 写入 `doc/bundles/viz/3b1b/manim/spec/insights.md`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-2.1: 每个洞察包含陈述/证据/反常识/行动四要素
  - `human-judgement` TR-2.2: 知识地图有清晰的学习路径（基础→核心→高级）
- **Notes**: 洞察示例：Mobject 树形组合结构、Animation 时间映射机制、Scene 播放循环、GPU 渲染管线设计

## [x] Task 3: manim 知识包 E 阶段 - 信源登记与文档生成
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建目录结构：`doc/bundles/viz/3b1b/manim/` 下 concepts/、examples/、references/、spec/
  - **信源先行**：先生成 references/ 下的信源登记文档（每个核心模块一个 .md，含源码路径索引）
  - 分批生成 concepts/ 概念文档（每批≤5个），按学习路径排序：
    - 00-overall-architecture.md（整体架构）
    - 01-mobject-system.md（Mobject 对象体系）
    - 02-animation-system.md（Animation 动画机制）
    - 03-scene-lifecycle.md（Scene 场景生命周期）
    - 04-camera-and-renderer.md（相机与渲染管线）
    - 05-configuration.md（配置系统）
    - 06-utilities.md（工具函数与常量）
  - 生成 examples/ 示例文档（2-3个：简单场景示例、自定义动画、LaTeX 数学渲染）
  - **最后生成**：各级 index.md（concepts/index.md、examples/index.md、references/index.md 无 frontmatter；根 index.md 含 okf_version）
  - 生成 log.md 变更日志
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-3.1: references/ 文件先于 concepts/ 生成（检查 git log 时间戳或文件内容中的 sources 引用有效性）
  - `human-judgement` TR-3.2: 概念文档按学习路径排列，从基础到高级
  - `human-judgement` TR-3.3: 每个概念文档 frontmatter 完整（type/title/description/tags/generated/verified/status/stale_after/sources）
  - `programmatic` TR-3.4: 子目录 index.md 不含 frontmatter，根 index.md 含 okf_version: "0.2"
- **Notes**: 分批委派子代理生成，每批≤5个文档防止上下文过载；交叉链接使用 `/` 开头 bundle-relative 路径

## [/] Task 4: manim 知识包 V 阶段 - 独立验证与修复
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 结构检查：目录结构完整、frontmatter 字段齐全、无孤立文件
  - **Grep API 验证**：对文档中引用的每个类名（Scene/Mobject/Animation/VMobject/Camera 等）和关键方法，在 manimlib/ 中验证存在性
  - 代码示例检查：示例代码中的 API 调用与 facts.md 中记录的签名一致
  - 链接检查：内部交叉链接无断裂
  - Index 完整性检查：toctree 包含所有子文档，无遗漏
  - 运行 `invoke gates.toctrees` 和 `invoke gates.utf8` 在 awesome-okf-xs 目录
  - 修复发现的所有问题
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: Grep 验证至少 15 个核心类名/方法名在源码中存在
  - `programmatic` TR-4.2: `invoke gates.toctrees` 在 projects/awesome-okf-xs/ 下运行通过（针对 manim bundle）
  - `programmatic` TR-4.3: `invoke gates.utf8` 运行通过
  - `human-judgement` TR-4.4: 代码示例逻辑正确，可作为入门参考
- **Notes**: Grep 验证是强制质量门，不可跳过；使用独立子代理进行黑盒验证

## [x] Task 5: videos 知识包 R→I→E→V 全流程
- **Priority**: medium
- **Depends On**: Task 4（manim 完成后便于理解 videos 的代码模式）
- **Description**:
  - R 阶段：分析 videos/ 目录结构（按年份 _2015/_2016/_2017/_2018/），识别典型项目结构（如 eola/线性代数本质、eoc/微积分本质、nn/神经网络系列），提取自定义组件和通用模式事实，写入 spec/facts.md
  - I 阶段：提炼场景组织模式、checkpoint_paste 交互式工作流、PiCreature 角色系统、数学可视化实践模式洞察
  - E 阶段：生成 references/（核心扩展文件信源）、concepts/（场景结构、交互式工作流、自定义组件、年度项目组织）、examples/（选取 1-2 个代表性视频场景拆解，如 eola/chapter1.py 或 nn/part1.py）、index.md、log.md
  - V 阶段：Grep 验证关键类/函数引用（InteractiveScene、checkpoint_paste、PiCreature 等）、结构检查、质量门验证
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: spec/facts.md 存在，无推断性表述
  - `programmatic` TR-5.2: 文档中引用的关键类/函数在 videos/ 源码中可 Grep 到
  - `programmatic` TR-5.3: `invoke gates.toctrees` 和 `invoke gates.utf8` 通过
  - `human-judgement` TR-5.4: 清晰标注老版本代码与当前 ManimGL 的兼容性注意事项
- **Notes**: videos 代码较老（2015-2018），重点提炼通用模式而非逐文件讲解；目录名 `videos`（与源码目录名一致，简单单词无需 kebab-case 转换）

## [x] Task 6: caption-ops 知识包 R→I→E→V 全流程
- **Priority**: medium
- **Depends On**: Task 1（可并行，但 manim 完成后更了解 3b1b 生态）
- **Description**:
  - R 阶段：分析 caption_ops/ 下核心 Python 脚本（transcribe_video.py、translate.py、gpt_translate.py、srt_ops.py、retime_srt.py、download.py、upload.py、helpers.py、sentence_timings.py、scripts/ 目录下工具），提取脚本功能、调用关系、数据流事实
  - I 阶段：提炼字幕处理管线洞察（音频下载→转录→翻译→时间轴调整→上传）、SRT 操作模式洞察
  - E 阶段：生成 references/（核心脚本信源）、concepts/（字幕处理管线概览、SRT 操作、转录与翻译、批量同步工作流）、examples/（典型使用流程）、index.md、log.md
  - V 阶段：Grep 验证关键函数名、结构检查、质量门验证
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: spec/facts.md 记录至少 10 个核心脚本的功能与主要函数
  - `programmatic` TR-6.2: 关键函数名在 caption_ops/ 中可 Grep 到
  - `programmatic` TR-6.3: `invoke gates.toctrees` 和 `invoke gates.utf8` 通过
- **Notes**: 目录名使用 kebab-case `caption-ops`（Python 包名 `caption_ops` 转为目录名时用连字符）

## [x] Task 7: 3blue1brown-com 知识包 R→I→E→V 全流程
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - R 阶段：分析 3Blue1Brown.com/ 的 app/ 目录结构（api/components/data/pages/util）、package.json、react-router.config.ts、vite.config.ts、核心组件（Header/Footer/Nav/MathJax/YouTube/Vimeo/Figure 等）、MDX 配置、Tailwind 使用模式，提取事实
  - I 阶段：提炼 React Router v7 框架模式洞察、MDX+MathJax 数学内容处理洞察、组件库组织模式洞察
  - E 阶段：生成 references/（核心配置与组件信源）、concepts/（项目架构与技术栈、路由与页面系统、通用组件库、MDX 数学内容处理、样式与设计系统）、examples/（典型页面结构如 lessons/lessons.ts）、index.md、log.md
  - V 阶段：Grep 验证关键组件/函数名、结构检查、质量门验证
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: spec/facts.md 覆盖 app/components/ 中至少 15 个核心组件
  - `programmatic` TR-7.2: 关键组件名在 app/components/ 中可 Grep 到
  - `programmatic` TR-7.3: `invoke gates.toctrees` 和 `invoke gates.utf8` 通过
  - `human-judgement` TR-7.4: 准确描述 React Router v7 框架模式（与 SPA 的区别、预渲染等）
- **Notes**: 目录名使用 kebab-case `3blue1brown-com`；此为 TypeScript/React 项目，Grep 验证时注意 .tsx/.ts 文件扩展名

## [x] Task 8: 创建 viz/ 技术域与 3b1b/ 分组索引
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6, Task 7（所有知识包生成后统一创建索引）
- **Description**:
  - 创建 `doc/bundles/viz/index.md`：作为"数学可视化与创意编程"技术域入口，包含域说明、分组导航、toctree 引用 3b1b/index，更新 mermaid 生态关系图（添加 viz 与 data/document 的关联）
  - 创建 `doc/bundles/viz/3b1b/index.md`：作为 3Blue1Brown 生态分组入口，包含 4 个知识包导航（manim/videos/caption-ops/3blue1brown-com）、生态关系说明、toctree
  - 更新 `doc/bundles/index.md`：
    - 在十域导航中添加 viz 域为第十一域
    - 更新 mermaid 生态关系概览图，添加 viz 节点及其与 data/pydata（matplotlib）、document/katex 的关联
    - 更新推荐入门路径图
    - 更新 toctree 添加 viz/index
    - 更新统计数字（total_bundles、groups、domains）
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: `doc/bundles/viz/index.md` 存在且包含有效的 toctree
  - `programmatic` TR-8.2: `doc/bundles/viz/3b1b/index.md` 存在且包含 4 个知识包的 toctree
  - `programmatic` TR-8.3: `doc/bundles/index.md` 已更新，mermaid 图包含 viz
  - `programmatic` TR-8.4: 在 awesome-okf-xs 根目录运行 `invoke gates.toctrees` 完全通过，零断链、零孤立
  - `programmatic` TR-8.5: `invoke gates.utf8` 完全通过
  - `human-judgement` TR-8.6: viz 域描述清晰，与现有域分类逻辑一致
- **Notes**: 索引文件必须在所有知识包完成后最后生成/更新，确保 toctree 不遗漏

## [x] Task 9: 最终验证与构建测试
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 在 `projects/awesome-okf-xs/` 目录下运行完整质量门：`invoke gates.all`
  - 尝试构建 HTML 文档：`invoke build`（如环境已安装依赖）
  - 检查所有 4 个知识包的根 index.md 包含 okf_version: "0.2"
  - 检查所有 frontmatter 中 sources 字段指向有效的 references/ 文档
  - 检查交叉链接使用 `/` 开头路径，无 `../` 相对路径
  - 检查所有文件 UTF-8 编码无 BOM
  - 输出最终验证报告
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: `invoke gates.all` 完全通过（toctrees + utf8）
  - `programmatic` TR-9.2: 所有知识包 index.md 的 toctree 引用的文件均存在
  - `human-judgement` TR-9.3: 文档整体阅读流畅，中文表达自然，技术术语准确
- **Notes**: 如 `invoke build` 因依赖缺失失败，至少确保 gates.all 通过即可
