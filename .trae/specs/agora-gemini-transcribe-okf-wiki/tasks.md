# Tasks：agora-gemini-transcribe OKF 知识包

## T1 内容获取与事实采集（R 阶段）

- [x] T1.1 敏感度预检（公开文章，标准工作流）
- [x] T1.2 browser_use 获取博文全文与元信息（标题/公众号"声网"/发布时间 2026-08-27 17:35）
- [x] T1.3 内容性质判定：厂商自宣新闻稿/资讯速报（约千字，无代码/步骤/数据）→ 资讯速报骨架，操作可复现性两问皆"否"，无 examples/
- [x] T1.4 归属判定：ai/ai-agent/，Bundle 名 agora-gemini-transcribe
- [x] T1.5 article-source.md 落盘（F-001~F-024 博文事实，📝 观点 7 条）

## T2 P0 核验（R/V 阶段）

- [x] T2.1 P0-1 Gemini 3.5 Transcribe 真实性 ✅（Google 官方博客 2026-08-26、Pichai X 宣布）
- [x] T2.2 P0-2 Agora×Gemini 合作 ✅（Agora 文档 Gemini Live/Vertex AI 页 2026-07-30、2026-05-07 教程、媒体转载）
- [x] T2.3 P0-3 Agents SDK 与灵活组合 ✅（agora_agent/agora-agents/agora-agents-go；链式/MLLM 两架构）
- [x] T2.4 P0-4 Smart Transcription ✅（Google 已发布；博文"计划"未来时准确）
- [x] T2.5 P0-5 "全球首个 Realtime API" ⚠️（合作真实，措辞归属含糊；F-029 写准确时间线）
- [x] T2.6 P0-6 噪声/专业词/口语应对 ✅（与官方博客一致）
- [x] T2.7 核验补充事实 F-025~F-032（双API/模型ID/WER/定价/词表/时间线/SDK/网络规模/转载）
- [x] T2.8 verification.md 落盘（5✅1⚠️0❌ + 勘误四张清单 + 10 信源）

## T3 I 阶段拆分

- [x] T3.1 concepts 4 篇：语音转型与RTC门槛 / Gemini模型双API / Agora开放集成架构 / Smart Transcription场景

## T4 E 阶段生成

- [x] T4.1 index.md（含厂商自宣提示 + P0-5 勘误块 + 6 条已知边界）
- [x] T4.2 concepts/index.md + 4 篇概念文档
- [x] T4.3 references/index.md + article-source.md + verification.md
- [x] T4.4 log.md（含 F-025~F-032 为 V 阶段补充的注记）

## T5 索引更新

- [x] T5.1 ai/ai-agent/index.md：计数 28→29、表格追加行、toctree 追加
- [x] T5.2 bundles/index.md：total 280→281、ai 域 107→108、ai-agent 28→29

## T6 V 阶段验证

- [x] T6.1 UTF-8 严格解码 roundtrip：15/15 通过（bundle 10 + spec 3 + 索引 2）
- [x] T6.2 无 file:/// 绝对路径链接（0）、无敏感路径（0）
- [x] T6.3 内部相对链接全部有效（0 断链）
- [x] T6.4 F 编号一致性：article-source.md 与 spec facts.md 表行正则各 32 条，1-32 连续无缺失
- [x] T6.5 toctree 完整（bundle 3 块）；ai-agent 组 toctree 29 条 = frontmatter 29 = 实际目录 29
- [x] T6.6 索引计数三级同步（281 总 / 108 域 / 29 组）

## T7 C 阶段提交

- [ ] T7.1 子模块 awesome-okf-xs：bundle 新文件 + 两索引更新，原子提交（git-commit-utf8.py）
- [ ] T7.2 主仓库 SpecWeave：spec 三文件 + 子模块指针更新，原子提交
- [ ] T7.3 不 push（用户未要求）
