# Anthropic 生态 OKF Wiki - Verification Checklist

## 组织级Bundle验证
- [ ] `doc/bundles/ai/anthropic/` 目录存在
- [ ] `doc/bundles/ai/anthropic/index.md` 存在且含 `okf_version: "0.2"` frontmatter
- [ ] 组织级index.md包含Anthropic生态简介、6个子bundle导航表格
- [ ] 组织级index.md的toctree引用所有6个子bundle的index
- [ ] `doc/bundles/ai/anthropic/log.md` 存在且有2026-08-27创建记录
- [ ] `doc/bundles/ai/index.md` 已更新包含anthropic条目

## 目录结构验证
- [ ] `python-sdk/` 子bundle目录存在，含concepts/examples/references子目录
- [ ] `claude-code/` 子bundle目录存在
- [ ] `cookbooks/` 子bundle目录存在
- [ ] `prompt-engineering/` 子bundle目录存在
- [ ] `official-skills/` 子bundle目录存在
- [ ] `financial-services/` 子bundle目录存在

## python-sdk R阶段 事实采集验证
- [ ] `.trae/specs/okf-wiki-ecosystem/anthropic-python-sdk-okf-wiki/facts.md` 存在
- [ ] 事实数量≥80条，编号F-001起
- [ ] 每条事实包含具体源码文件路径
- [ ] 事实中无推断性表述（"用于"/"目的是"/"设计为"等）
- [ ] 覆盖8大模块：客户端、消息API、流式处理、工具系统、Beta API、多后端、中间件、异常

## python-sdk I阶段 架构洞察验证
- [ ] `.trae/specs/okf-wiki-ecosystem/anthropic-python-sdk-okf-wiki/insights.md` 存在
- [ ] 包含3-5个核心架构洞察
- [ ] 每个洞察有四元组：陈述、证据（F-xxx引用）、反常识、行动
- [ ] 知识地图明确文档分组（入门/核心/高级）和学习路径
- [ ] 明确每个待生成文档覆盖的F-xxx事实范围

## python-sdk references/ 信源验证
- [ ] `references/sdk-client.md` 存在（客户端入口与基础设施）
- [ ] `references/messages-api.md` 存在（消息API与流式）
- [ ] `references/tools-beta.md` 存在（工具与Beta）
- [ ] `references/multi-cloud.md` 存在（多云后端）
- [ ] `references/types-errors.md` 存在（类型与异常）
- [ ] `references/source.md` 存在（源码版本与目录）
- [ ] `references/index.md` 存在且无frontmatter
- [ ] 每个信源文件frontmatter完整（type=reference）
- [ ] 信源中API签名与facts.md一致

## python-sdk concepts/ 概念文档验证
- [ ] `concepts/00-overview.md` 存在（整体架构）
- [ ] `concepts/01-client-init.md` 存在（客户端初始化）
- [ ] `concepts/02-messages-basics.md` 存在（Messages API基础）
- [ ] `concepts/03-streaming.md` 存在（流式处理）
- [ ] `concepts/04-tool-use.md` 存在（工具调用）
- [ ] `concepts/05-vision-files.md` 存在（视觉与文件）
- [ ] `concepts/06-pagination-models.md` 存在（分页与模型）
- [ ] `concepts/07-multi-cloud.md` 存在（多云部署）
- [ ] `concepts/08-beta-agents.md` 存在（Beta Agent/Memory）
- [ ] `concepts/09-middleware-extended.md` 存在（中间件）
- [ ] `concepts/10-error-handling.md` 存在（错误处理，如生成）
- [ ] `concepts/index.md` 存在且无frontmatter
- [ ] 每个概念文档500-5000字，用##分节
- [ ] 每个概念文档结尾有「## 相关概念」章节
- [ ] 交叉链接使用`/`开头路径，无`../`
- [ ] 每个概念文档frontmatter完整（type=concept）

## python-sdk examples/ 示例验证
- [ ] `examples/01-basic-chat.md` 存在（基础对话）
- [ ] `examples/02-streaming-chat.md` 存在（流式对话）
- [ ] `examples/03-tool-use.md` 存在（工具调用）
- [ ] `examples/04-vision.md` 存在（视觉理解）
- [ ] `examples/05-bedrock-vertex.md` 存在（Bedrock/Vertex）
- [ ] `examples/06-thinking-extended.md` 存在（Extended Thinking，如生成）
- [ ] `examples/index.md` 存在且无frontmatter
- [ ] 每个示例含完整可运行代码框架
- [ ] import路径与`__init__.py`的__all__一致
- [ ] 每个示例文档frontmatter完整（type=example）

## python-sdk 根文档验证
- [ ] 根`index.md`含okf_version frontmatter
- [ ] 根index.md含快速开始代码、文档导航表格、能力速查表
- [ ] 根index.md含toctree引用concepts/index、examples/index、references/index、log
- [ ] `log.md`含创建记录

## python-sdk V阶段 API真实性验证（最关键）
- [ ] 所有类名（Anthropic/AsyncAnthropic/Stream/AsyncStream/AnthropicBedrock/AnthropicVertex/BaseModel等）Grep源码验证存在
- [ ] 所有方法名（messages.create/messages.stream等）Grep源码验证存在
- [ ] 所有import语句验证导入路径正确
- [ ] 无虚构的类、方法、参数
- [ ] 无虚构的异常类型
- [ ] 所有交叉链接目标文件存在（Glob验证）
- [ ] concepts/index.md列出所有概念文档
- [ ] examples/index.md列出所有示例文档
- [ ] references/index.md列出所有信源文件

## claude-code 子Bundle验证
- [ ] `claude-code/concepts/00-overview.md` 存在（CLI概览）
- [ ] `claude-code/concepts/01-plugin-system.md` 存在（插件体系）
- [ ] `claude-code/references/plugins-index.md` 存在（插件索引）
- [ ] `claude-code/examples/basic-usage.md` 存在（基本使用）
- [ ] `claude-code/index.md` 存在且含正确frontmatter和toctree
- [ ] `claude-code/log.md` 存在
- [ ] `claude-code/concepts/index.md`、`references/index.md`、`examples/index.md` 存在
- [ ] 插件索引覆盖plugins/README中列出的主要插件

## cookbooks 子Bundle验证
- [ ] `cookbooks/concepts/00-overview.md` 存在（导览）
- [ ] `cookbooks/concepts/01-tool-use-patterns.md` 存在（工具调用模式）
- [ ] `cookbooks/concepts/02-multimodal-patterns.md` 存在（多模态模式）
- [ ] `cookbooks/concepts/03-rag-patterns.md` 存在（RAG模式）
- [ ] `cookbooks/concepts/04-advanced-techniques.md` 存在（高级技巧）
- [ ] `cookbooks/references/recipe-index.md` 存在（食谱索引）
- [ ] `cookbooks/index.md` 存在且含正确frontmatter和toctree
- [ ] `cookbooks/log.md` 存在
- [ ] 食谱索引按能力域分类，覆盖README中列出的主要类别

## prompt-engineering 子Bundle验证
- [ ] `prompt-engineering/concepts/00-overview.md` 存在（概览）
- [ ] `prompt-engineering/concepts/01-basic-structure.md` 存在（基础结构Ch1-3）
- [ ] `prompt-engineering/concepts/02-intermediate-techniques.md` 存在（中级技巧Ch4-7）
- [ ] `prompt-engineering/concepts/03-advanced-patterns.md` 存在（高级模式Ch8-9）
- [ ] `prompt-engineering/concepts/04-beyond-standard.md` 存在（进阶附录）
- [ ] `prompt-engineering/index.md` 存在且含正确frontmatter和toctree
- [ ] `prompt-engineering/log.md` 存在
- [ ] 内容覆盖README中9章+附录的核心要点

## official-skills 子Bundle验证
- [ ] `official-skills/concepts/00-overview.md` 存在（Skills生态概览）
- [ ] `official-skills/concepts/01-skill-format.md` 存在（SKILL.md格式规范）
- [ ] `official-skills/concepts/02-skill-creator.md` 存在（Skill Creator详解）
- [ ] `official-skills/concepts/03-claude-api-skill.md` 存在（Claude API Skill详解）
- [ ] `official-skills/references/skills-index.md` 存在（Skills总索引）
- [ ] `official-skills/index.md` 存在且含正确frontmatter和toctree
- [ ] `official-skills/log.md` 存在
- [ ] Skills索引覆盖skills/skills/下所有子目录（xlsx/docx/pptx/frontend-design/skill-creator/theme-factory/webapp-testing/web-artifacts-builder/slack-gif-creator/claude-api等）

## financial-services 子Bundle验证
- [ ] `financial-services/concepts/00-overview.md` 存在（金融服务概览）
- [ ] `financial-services/concepts/01-agent-architecture.md` 存在（Agent双模式架构）
- [ ] `financial-services/references/agents-index.md` 存在（Agent清单）
- [ ] `financial-services/references/vertical-plugins.md` 存在（垂直插件索引）
- [ ] `financial-services/index.md` 存在且含正确frontmatter和toctree
- [ ] `financial-services/log.md` 存在
- [ ] Agent清单覆盖README中表格列出的10个Agent（Pitch/Meeting Prep/Market Researcher/Earnings Reviewer/Model Builder/Valuation Reviewer/GL Reconciler/Month-End Closer/Statement Auditor/KYC Screener）

## 全局格式合规验证
- [ ] 所有交叉链接使用`/`开头bundle-relative路径
- [ ] 子目录index.md（非根index）无frontmatter
- [ ] 所有非保留.md文件有可解析YAML frontmatter
- [ ] 每个frontmatter有非空type字段
- [ ] 所有文件UTF-8编码无BOM
- [ ] 代码块标注语言类型（python/bash等）
- [ ] 中文撰写，英文术语首次出现有括号注释

## 质量门验证
- [ ] 在projects/awesome-okf-xs/下运行`invoke gates.toctrees`通过（退出码0）
- [ ] 在projects/awesome-okf-xs/下运行`invoke gates.utf8`通过（退出码0）
- [ ] 无孤立文档（所有文档被index或toctree引用）
- [ ] 无断链（所有链接目标存在）
