# Checklist

## Wiki 结构
- [x] AC-1: `03-agent-platforms-tools/hermes-agent-wiki/` 目录存在，含 README.md 与 00-0X 编号章节（12 篇），命名 kebab-case
- [x] AC-2: 每个章节 frontmatter 含 id/title/source/description/tags/category/date/status，YAML 格式与现有 wiki 一致

## 内容覆盖
- [x] AC-3: 产品定位与核心理念阐述清晰（自进化 AI Agent、闭环学习、核心窄腰/能力在边缘）
- [x] AC-4: 核心特性覆盖完整（终端界面/随你所在/闭环学习/定时自动化/委派并行/随处运行/研究就绪）
- [x] AC-5: 快速安装上手可实操（curl/install.ps1 → hermes 对话 → model/tools/config/setup）
- [x] AC-6: CLI 与斜杠命令覆盖完整（hermes <subcommand>、/model、/skills、/compress、/new）
- [x] AC-7: 配置体系阐述清晰（config.yaml section、.env 仅密钥、HERMES_HOME、profiles）
- [x] AC-8: 消息网关/工具/技能/记忆系统覆盖完整（多平台、Footprint Ladder、SKILL.md/curator、provider/memory_manager）
- [x] AC-9: MCP/cron/委派并行覆盖完整（MCP 集成、cron、delegate_task 单/批/角色）
- [x] AC-10: 架构解析与源码导读覆盖完整（AIAgent 核心循环、CLI/TUI/桌面、项目结构、插件系统）
- [x] AC-11: 术语表/FAQ/资源完整（Hermes/prompt caching/toolset/memory provider/skill 等术语）

## 质量与链接
- [x] AC-12: 交叉链接有效、相对路径；与 hermes-okf-wiki / hermes-agent-integration 交叉引用指向存在文件；03-agent-platforms-tools/README.md 已添加 hermes-agent-wiki 入口
- [x] AC-13: 使用的 Mermaid 图表语法正确可渲染（10 章架构图语法有效）

## 规范约束
- [x] NFR-2: 单章节文件 <300 行
- [x] NFR-5: 交叉链接使用相对路径，禁止 file:/// 绝对路径
- [x] NFR-7: 三级标题使用 x.y 编号格式
- [x] NFR-8: 不虚构未公开特性，命令/字段有依据或标注"示例/需验证"
- [x] G1 质量门：事实无因果推断词，可追溯（R 阶段）
- [x] G2 质量门：3 条核心洞察四元组完整（I 阶段）
- [x] V 质量门：对抗审查 ≥5 条意见，采纳 ≥2 条修正（6 条意见，采纳 4 条，见 adversarial-review.md）

## 附加
- [x] 悬空 x-toml-ref 已解决：13 个 `.meta/toml` 元数据文件已生成并与 md frontmatter 核对一致
