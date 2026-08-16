---
version: "1.0"
---

# DeepSeek Harness Wiki 教程 Checklist

## 规范合规检查

### 文档结构检查
- [ ] 所有16个章节文件均已创建在 `docs/knowledge/ai/deepseek-harness/` 目录下
- [ ] 每个文件包含正确的YAML frontmatter（id/title/source/date/tags/maturity）
- [ ] 每个文件包含正确的上一章/下一章导航链接
- [ ] 文件名遵循xx-slug-case-kebab命名规范
- [ ] 目录结构与spec.md中What Changes章节一致

### 内容准确性检查

#### 基础信息准确性
- [ ] 发布日期正确：2026年8月13日晚
- [ ] 版本号正确：v0.1开发者预览版（基于0.1.0-rc.6实测）
- [ ] 开源协议正确：MIT
- [ ] Node.js版本要求正确：^22.19 || >=24（奇数版本不支持）
- [ ] 默认端口正确：3080
- [ ] 默认配置目录正确：~/.dsh/
- [ ] 启动命令正确：`npx @deepseek-ai/dsh web`
- [ ] 数据截止日期标注：2026年8月15日

#### 架构概念准确性
- [ ] "一切皆插件"哲学描述准确，无特权内核
- [ ] Cordis元框架描述准确，引用时空可组合性论文
- [ ] Profile与Bundle机制描述准确
- [ ] Turn/Step事件模型定义准确：Step=一次模型请求+工具调用，Turn=0~N个Step
- [ ] 三类事件分类准确：会话事件/Agent事件/能力事件
- [ ] 瀑布型事件与next()机制描述准确
- [ ] 会话日志append-only、"模型看到的必须写进日志"硬规则准确
- [ ] Capability Seam三角色（Service Definition/Provider/Consumer）描述准确
- [ ] 可逆效应（reversible effects）概念准确

#### 功能特性准确性
- [ ] 四种运行模式（Standard/Code/Minimal/Creator）描述准确，能力对比表正确
- [ ] 默认模型（deepseek-v4-pro/flash）参数正确：100万上下文/256k输出
- [ ] 三档思考强度（low/high/max）适用场景正确
- [ ] 多Provider支持列表正确（Anthropic/OpenAI/Bedrock/Azure/Vertex + 自定义）
- [ ] 内置工具清单准确
- [ ] hooks兼容（Claude Code/Codex）、MCP支持、AGENTS.md/CLAUDE.md读取描述准确
- [ ] Python SDK（自带Node运行时）、JSON-RPC、ACP描述准确
- [ ] 本地服务限制：CLI拒绝--host 0.0.0.0描述准确
- [ ] Windows限制：PTY不可用、官方运行时仅Linux/macOS描述准确

### 质量门检查（七概念方法论）

#### G1: 事实无因果词
- [ ] 所有陈述基于可验证来源，无主观臆断
- [ ] 明确标注"预览版"、"v0.1"等状态，不夸大成熟度
- [ ] 风险提示醒目，不误导用户用于生产

#### G2: 洞察四元组完整（在01-introduction和14-use-cases中体现）
- [ ] 现象描述：Harness发布的行业现象客观
- [ ] 根因分析：为什么DeepSeek选择开源框架路线的逻辑清晰
- [ ] 影响评估：架构选择对生态的影响分析有依据
- [ ] 建议给出：适用/不适用场景建议明确

#### G3: 模式可迁移
- [ ] 插件架构模式描述清晰，读者可理解其设计思想
- [ ] 可观测性模式（日志即真相源）可迁移到其他Agent项目参考
- [ ] Capability Seam抽象作为设计模式有参考价值

#### G4: 行动项原子化（在教程步骤中体现）
- [ ] 安装步骤原子化，每步可独立验证
- [ ] 第一个任务的步骤清晰可复现
- [ ] FAQ每个问题-解决方案对独立

### 生态与资源检查
- [ ] 官方资源链接正确且可访问（GitHub/官网/API平台/Cordis）
- [ ] 推荐阅读文章链接正确
- [ ] 与Claude Code/Codex对比表维度准确、客观
- [ ] QQ Bot接入、国家超算互联网等生态动态描述准确

### 导航与链接检查
- [ ] 00-overview.md中16章导航表链接全部正确
- [ ] 每个章节的上一章/下一章链接正确，无断链
- [ ] docs/knowledge/ai/README.md已正确添加deepseek-harness条目
- [ ] 所有外部URL使用完整https链接
- [ ] 内部Markdown链接使用相对路径，格式正确

### 风险提示检查
- [ ] 14-use-cases-limitations.md中包含醒目的⚠️预览版风险提示
- [ ] 明确说明"会有破坏性变更"、"不建议生产使用"
- [ ] 明确说明会话格式不兼容升级
- [ ] 明确说明主仓库暂不接受外部PR
- [ ] Windows平台限制提示清晰

### 格式规范检查
- [ ] 遵循项目Markdown规范（myst-parser兼容）
- [ ] 代码块使用正确的语言标识（bash/typescript等）
- [ ] 表格格式规范，列对齐
- [ ] 标题层级正确（# 一级/## 二级/### 三级，不跳级）
- [ ] 中文排版：中英文之间有空格、标点使用正确
- [ ] 无emoji滥用（仅⚠️等必要提示符号）
- [ ] 无广告/推广内容，保持中立技术文档风格

## 完成度检查

| 章节 | 文件名 | 状态 |
|------|--------|------|
| 00 | 00-overview.md | [ ] |
| 01 | 01-introduction-background.md | [ ] |
| 02 | 02-installation-setup.md | [ ] |
| 03 | 03-quickstart-first-task.md | [ ] |
| 04 | 04-four-modes.md | [ ] |
| 05 | 05-architecture-everything-plugin.md | [ ] |
| 06 | 06-agent-loop-events.md | [ ] |
| 07 | 07-session-log-observability.md | [ ] |
| 08 | 08-model-configuration.md | [ ] |
| 09 | 09-tools-capability-seam.md | [ ] |
| 10 | 10-plugin-development.md | [ ] |
| 11 | 11-ecosystem-interop.md | [ ] |
| 12 | 12-headless-sdk.md | [ ] |
| 13 | 13-faq-troubleshooting.md | [ ] |
| 14 | 14-use-cases-limitations.md | [ ] |
| 15 | 15-ecosystem-resources.md | [ ] |
| README | docs/knowledge/ai/README.md | [ ] |

## 验证命令

所有文档完成后，运行以下验证：

- [ ] 链接检查：运行link-check-cmd验证无断链
- [ ] 格式检查：所有Markdown文件语法正确
- [ ] 导航完整性：从00-overview开始依次点击下一章可遍历所有16章
- [ ] 事实核对：关键数据（版本/端口/命令/版本要求）与deepseekagent.io指南及官方README一致
