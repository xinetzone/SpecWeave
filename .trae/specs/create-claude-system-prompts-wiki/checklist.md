# Checklist：create-claude-system-prompts-wiki

## 内容质量
- [x] 束位于 `jishu/ai/anthropic/system-prompts/`，骨架完整（index + concepts/ 7 篇 + concepts/index + references/ 2 篇 + references/index + log.md，共 13 文件）
- [x] 18 模型 × 30 日期条目矩阵完整（实测口径修正：spec 撰写时基于旧版单页快照估为 16×28，实际全量采集核实为 18×30，含 2026-09-01 上线的 Fable 5.1）；无"（待补）"项（全部条目采集成功）
- [x] 关键行为规范段落引用官方英文原文并配中文解析，引文与官方页逐字一致（V 抽查：前置 6/6 + 对抗审查 20+ 条引文三向比对，含 6 条追溯官方原文逐字吻合）
- [x] 无虚构内容（对抗审查虚构探测 6/6 断言均有逐字支撑）；第三方来源仅作交叉印证且显式标注（source-index 明确"未采集、不列名"非权威媒体）
- [x] 设计思想演进分析有事实支撑（06-evolution 引用 45 个不同 F 编号，每小节 ≥2 处证据）

## 格式合规
- [x] 全部 frontmatter 符合 OKF v0.2，含 `sources` 溯源字段，无 ASCII 双引号嵌套陷阱（yaml.safe_load 全部解析通过）
- [x] 正文中文、文件名 kebab-case 纯英文、相对路径交叉引用、无 `file:///`（对抗审查链接检查 0 断链）
- [x] 全部文件 UTF-8 无 BOM（PowerShell 实测 10 文件 + Write 工具默认无 BOM 3 文件）；脚注块前无手写 `---`（正则核验仅 frontmatter 定界符）
- [x] toctree 完整：束 index 引用全部内容页；组索引/域索引/总索引引用链闭合（gates.toctrees 失败清单中零条涉及本束）

## 质量门
- [x] `invoke gates.utf8` 通过（8109 文件均为有效 UTF-8）
- [x] `invoke gates.toctrees`：**本束零问题**；全局 138 处失败均为并行会话在途束（wigolo / jishu/gui / sheke/finance / sheke/marketing / ai-app-survival），非本任务引入，按"不代他方补齐在途工作"纪律未越界修复
- [x] `invoke gates.bundles`：**本束零问题**；全局 6 处计数漂移同源于并行会话在途束（本束注册计数 411/311/128 与"基线+本束"地面真值一致）
- [x] `invoke build`（Sphinx）：经用户指示跳过（构建太慢）；YAML/MyST 风险已由 yaml.safe_load + 对抗审查覆盖

## 收尾
- [x] 未自动 commit/push；变更文件清单已在最终报告向用户呈报
- [x] spec 目录 `facts.md`（5 件）/ `insights.md` 已产出，支撑 E 阶段溯源
