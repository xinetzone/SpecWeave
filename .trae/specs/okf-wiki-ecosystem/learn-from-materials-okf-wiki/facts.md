# Facts：learn-from-materials

> 主信源：微信公众号"GitHubDaily"，2026-11-03 15:35 发布《一个神级学习 Skill，开源了！》
> URL：https://mp.weixin.qq.com/s/MUvHmFc4ItWfN57tuNjZkQ
> 权威信源：GitHub 仓库 `dmoshehun-prog/learn-from-materials`（API 元数据 + README.md/README_CN.md 双份）
> P0核验：10项（9项 ✅ 通过 + 1项 ⚠️ 口径差异已双源并列）

## 元信息与信源（F-001~F-003）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-001 | 原文标题《一个神级学习 Skill，开源了！》，公众号 GitHubDaily，2026-11-03 15:35 发布 | — |
| F-002 | 文章主线实体为一个开源学习 Skill：`learn-from-materials`，GitHub 作者 `dmoshehun-prog` | ✅ 仓库存在 |
| F-003 | 文章标签：#豆包工作 #豆包办公 #豆包教程 #豆包AI办公 #开源工具 #AI阅读 #效率工具 | — |

## 项目与仓库（F-004~F-009）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-004 | 仓库 `dmoshehun-prog/learn-from-materials` 真实存在、public、非 fork | ✅ GitHub API（id 1361079582） |
| F-005 | 仓库一句话定位："Turn PDFs, books and papers into interactive learning webpages｜将复杂材料转化为可追溯、可测验、可做笔记的学习网页" | ✅ API description 逐字 |
| F-006 | 许可证 MIT License | ✅ API license.spdx_id = MIT |
| F-007 | 实现语言为 Python | ✅ API language = Python |
| F-008 | 仓库创建于 2026-09-08T07:48:21Z；核验时点 star 1280 / fork 121（时点快照，非稳定值） | ✅ GitHub API 时点快照 |
| F-009 | 仓库 topics 含 agent-skills、ai-agent、book、claude-code、codex、education、knowledge-base、learning、markdown、workbuddy | ✅ GitHub API |

## 能力与支持格式（F-010~F-016）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-010 | 原文称：它可以把 PDF、EPUB、Word、PPT 等文件的内容，变成一个可交互的学习网页 | ✅ 官方 README 一致，且支持面更宽 |
| F-011 | 官方支持格式清单：PDF、EPUB、MOBI/AZW/AZW3、DOCX、PPTX/PPTM、HTML、Markdown、TXT、RTF 与多材料集合 | ✅ README EN/CN 双份一致（原文未覆盖 MOBI/AZW/HTML/TXT/RTF） |
| F-012 | 当前版本 1.1.0 | ✅ 官方 badge `version-1.1.0` + "1.1.0" 章节 |
| F-013 | 基于开放 Agent Skills 规范构建的跨 Agent 学习 Skill | ✅ README 首段 |
| F-014 | 提供两种学习深度："快速了解"（Quick Overview）与"系统学习"（Systematic Study） | ✅ README「两种学习深度」小节 |
| F-015 | 系统学习逐块读到材料末尾并审计方法候选项去向；明确"卡片数量不作为完成证明" | ✅ README |
| F-016 | 生成三类同源产出：可追溯的 `.learnkb/` 知识库、交互式单文件 HTML、同源 Markdown | ✅ README |

## 输出与交互（F-017~F-022）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-017 | 生成六类页面板块：核心框架、内容导学、术语大全、行动规则、动态自检、本地笔记 | ✅ README |
| F-018 | 原文：首页先看报告的内容框架，进入「内容导学」后可按章节阅读整理好的观点 | ✅ 与 README「内容导学」板块一致 |
| F-019 | 原文：导学里保留了报告正文页码和 PDF 页序，可照页码翻回原报告 | ✅ README：为 PDF 页码/PPT 幻灯片/EPUB 章节建立细粒度来源映射 |
| F-020 | 原文：不熟悉的词可到「术语大全」翻看解释，报告里的用法也放在一起 | ✅ 与 README「术语大全」板块一致 |
| F-021 | 对内容做四类区分：材料依据、材料未覆盖、模型补充、外部核验 | ✅ README（原文表述为"区分报告内容与模型补充"，为其中两类） |
| F-022 | 三套阅读主题：海盐云纱（Sea Salt）、黑白水墨（Ink Wash）、竹月清（Bamboo Moon），动效可关闭 | ✅ README EN/CN 双份 |

## 实操三步与实测（F-023~F-028）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-023 | 第一步：在「豆包工作」新建工作任务、选好存放报告的本地文件夹，发一句话安装技能——原文提示词逐字："帮我安装 GitHub 上 dmoshehun-prog 的 learn-from-materials 技能，装好之后用大白话告诉我它能做什么、怎么用。" | ⚠️ 作者一手操作描述，界面路径单源不可独立复核 |
| F-024 | 第二步：把 PDF 放进任务对应的本地文件夹，让它做一次快速概览——原文提示词逐字："请用 learn-from-materials 对这份 PDF 做一次快速概览，生成中文学习网页。整理核心观点和术语解释，保留原文页码，区分报告内容与模型补充。" | ✅ 提示词与官方"快速了解"深度语义一致 |
| F-025 | 作者实测样本为一份 54 页的生成式 AI 报告 | ⚠️ 作者一手实测，样本本身不可独立核验 |
| F-026 | 任务完成后得到一个 HTML 文件，可直接点开，在「豆包工作」内置浏览器里预览 | ⚠️ 单源（原文），官方 README 只说明交付含单文件 HTML，未描述豆包工作内置浏览器预览入口 |
| F-027 | 第三步：在内置浏览器点右上角「分享」→「生成链接」，得到可访问的网页链接 | ⚠️ 单源（原文），属宿主产品能力，非本 Skill 官方文档描述 |
| F-028 | 复制链接发给同事或朋友，对方打开即可查看总结好的内容 | — |

## 宿主与安装（F-029~F-033）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-029 | 原文：作者把这个 Skill 装到「豆包工作」 | ✅ 有独立佐证（见 F-033），但与官方宿主清单存在口径差异 |
| F-030 | 官方 README 列出的适用 Agent 环境：WorkBuddy、Codex、Claude Code、GitHub Copilot CLI | ✅ README EN/CN 双份一致 |
| F-031 | 官方用户级安装目录表：WorkBuddy `~/.workbuddy/skills/`；Codex `~/.agents/skills/`；Claude Code `~/.claude/skills/`；GitHub Copilot CLI `~/.copilot/skills/` 或 `~/.agents/skills/` | ✅ README 表格逐行 |
| F-032 | 安装方式：解压 `learn-from-materials-1.1.0.zip`，把完整的 `learn-from-materials/` 文件夹放入客户端 Skill 搜索目录；顶层须直接含 `SKILL.md`、`scripts/`、`references/`、`templates/`，避免多套一层目录 | ✅ README「1. 安装」 |
| F-033 | ⚠️ 口径差异：文章宿主为「豆包工作」（字节跳动），官方 README 宿主清单未列豆包工作；但豆包工作官方文档确有技能安装机制（技能页安装/「我安装的」管理/插件&技能&伙伴页面），第三方实践亦证实可在豆包工作中创建或导入 SKILL.md 技能——二者为不同公司产品（豆包工作=字节跳动；WorkBuddy=腾讯，与 CodeBuddy 同属 Buddy AI 产品线） | ⚠️ 双源并列登记，不判定文章有误 |

## 运行要求与边界（F-034~F-039）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-034 | 运行要求：Python 3.10 或更高版本；Agent 需能读取材料与 Skill 目录并运行本地 Python 命令；Node.js 仅用于可选 JavaScript 回归检查 | ✅ README badge + 「运行要求与兼容边界」 |
| F-035 | 纯聊天环境（无文件系统访问或 Python 执行）只能使用部分提示流程，无法完成材料提取、覆盖校验和 HTML 渲染 | ✅ README |
| F-036 | 扫描 PDF 与图片密集型幻灯片需要 OCR 或视觉能力；缺少能力时对应范围被标记为未核验 | ✅ README |
| F-037 | 离线优先：默认不联网、不自动安装依赖；页面笔记、画像和错题仅保存在当前浏览器本地 | ✅ README |
| F-038 | 长书、多材料交叉分析、专业论文和复杂开放题更适合长上下文、高推理能力模型 | ✅ README |
| F-039 | 命令行链（均在 Skill 根目录运行）：`extract.py`（提取/能力检查）、`methods.py bind`、`methodology.py bind`、`prepare_quick.py`、`pipeline.py assemble`、`render_page.py`、`finalize.py`（绑定+核验+打包交付） | ✅ README「命令行工具」全节 |

## 官方示例与版权（F-040~F-041）

| 编号 | 事实 | 核验 |
|------|------|------|
| F-040 | 官方 showcase 以三类材料示例演示同一六板块格式：传记《埃隆·马斯克传》、J.P. Morgan《2026 年中展望》、论文《Attention Is All You Need》；16 张截图为设计展示，不构成浏览器验收报告；仓库不含原始材料与完整生成结果，随包 Method Lab 为自编合成示例（MIT） | ✅ README「效果展示」+ 版权声明 |
| F-041 | 可选增强依赖及其回退：文字型 PDF（pdftotext/PyPDF2/pdfminer.six/PDFKit）、技术型 PDF（Docling）、扫描 PDF（OCRmyPDF+pdftotext）、EPUB（ebooklib+BeautifulSoup）、DOCX（python-docx）、RTF（striprtf）、MOBI/AZW/AZW3（Calibre ebook-convert，无内置回退） | ✅ README 可选增强能力表 |

## 事实统计

| 类别 | 数量 |
|------|------|
| 元信息与信源 | 3 |
| 项目与仓库 | 6 |
| 能力与支持格式 | 7 |
| 输出与交互 | 6 |
| 实操三步与实测 | 6 |
| 宿主与安装 | 5 |
| 运行要求与边界 | 6 |
| 官方示例与版权 | 2 |
| **合计** | **41** |
| ✅ P0通过 | 9/10 |
| ⚠️/单源与口径差异 | 1 口径差异（F-033）+ 4 项单源/一手实测（F-023/025/026/027） |
