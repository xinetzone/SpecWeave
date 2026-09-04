# Tasks：claude-vision-skill OKF 知识包

## T1 内容获取与事实采集

- [x] T1.1 敏感度预检（公开文章，标准工作流）
- [x] T1.2 browser_use 获取博文全文（标题/作者/时间/正文）
- [x] T1.3 内容性质判定：开源工具技术教程 → 完整骨架含 examples/
- [x] T1.4 归属判定：ai/ai-agent/，Bundle 名 claude-vision-skill
- [x] T1.5 facts.md 落盘（F-001~F-035，共35条）

## T2 P0 核验（R 阶段）

- [x] T2.1 仓库 asuojun/claude-vision-skill 存在性与内容 ✅
- [x] T2.2 DeepSeek V4 Pro 纯文本无视觉 ✅（补充：flash-vision-exp 08-21 上线）
- [x] T2.3 qwen-vl-max + DashScope compatible-mode 端点 ✅
- [x] T2.4 qwen3.5-omni-plus 模型 ✅（补充：全模态、成本4倍）
- [x] T2.5 Claude Code Skill 自动触发机制 ✅
- [x] T2.6 macrozheng 身份与 mall-swarm ✅
- [x] T2.7 verification.md 核验报告落盘（6✅0⚠️0❌ + 3时效补充）

## T3 I 阶段拆分

- [x] T3.1 concepts 3 篇：视觉鸿沟 / 转录架构 / Skill 机制
- [x] T3.2 examples 2 篇：安装配置 / 三场景实战

## T4 E 阶段生成

- [x] T4.1 index.md
- [x] T4.2 concepts/index.md + 3 篇概念文档
- [x] T4.3 examples/index.md + 2 篇实战文档
- [x] T4.4 references/index.md + article-source.md + verification.md
- [x] T4.5 log.md

## T5 索引更新

- [x] T5.1 ai/ai-agent/index.md：total_bundles 26→27、产品资讯表格追加行、toctree 追加
- [x] T5.2 bundles/index.md：total 278→279、"279个"、ai域 105→106束、ai-agent 26→27

## T6 V 阶段验证

- [x] T6.1 UTF-8 严格解码 roundtrip：14/14 通过
- [x] T6.2 无 file:/// 绝对路径链接
- [x] T6.3 内部相对链接全部有效（含 ../../ 跨bundle引用 anthropics-skills/book-to-skill）
- [x] T6.4 toctree 三级完整（4个toctree块）；ai-agent 组索引 toctree 27 条 = frontmatter 27
- [x] T6.5 索引计数三级同步（279总/106域/27组）
