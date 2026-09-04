---
title: "Spec：agora-gemini-transcribe OKF 知识包"
status: "draft"
---

# Spec：agora-gemini-transcribe OKF 知识包

> 来源：微信公众号"声网"（Agora 官方中文品牌）《Agora 携手 Google Gemini 3.5 Transcribe，共同加速对话式 AI 应用落地》（2026-08-27 17:35）
> URL：https://mp.weixin.qq.com/s/sbXT5BPvrj4CcuiyJttcgA
> 模式：blog-article-to-okf-bundle **L3**（资讯速报骨架，无 examples/；信源距离=厂商自宣）
> CMD-LOG session：sc-20260829-blog13-okf（第 13 篇博文转化）

## 产出位置

- Bundle：`projects/awesome-okf-xs/doc/bundles/ai/ai-agent/agora-gemini-transcribe/`
- 归属：ai 域 / ai-agent 组（产品资讯序列，组内第 29 个 bundle）

## 文件骨架（10 文件，无 examples/）

| 文件 | 内容 |
|------|------|
| index.md | 入口、版图Mermaid、厂商自宣提示、P0-5措辞勘误、已知边界 |
| concepts/index.md | 概念学习路径（4篇） |
| concepts/00-voice-agent-runtime.md | 背景：文本→语音转型、实时听懂三难点、RTC/SD-RTN™ 门槛 |
| concepts/01-gemini-transcribe-model.md | 模型：双API/模型ID、WER 4.0%/2.6%、85+语言、定价与限制 |
| concepts/02-agora-conversational-ai.md | 平台：Agents SDK三语言、链式/MLLM两架构、OpenAI合作时间线勘误 |
| concepts/03-smart-transcription-scenarios.md | 场景：口语清理/自动排版、CRM/信息采集、合作展望 |
| references/index.md | 信源索引（Google官方+Agora官方+第三方媒体共10源） |
| references/article-source.md | F-001~F-032 事实登记（博文24条+V补充8条） |
| references/verification.md | P0核验报告（5✅1⚠️0❌）+勘误四张清单 |
| log.md | 变更日志（含 V 补充事实注记） |

操作可复现性两问皆"否"（无安装/配置/代码/实测流程）→ 无 examples/。

## 事实基数

32 条事实（F-001~F-032，编号连续）：
- 博文事实 24 条（F-001~F-024），其中 📝 作者观点 7 条：F-007/F-011/F-012/F-015/F-022/F-023/F-024
- V 阶段核验补充 8 条（F-025~F-032）：发布日期与双API、模型ID、WER/定价/词表、OpenAI合作精确时间线、Agora SDK包名与两架构、SD-RTN™规模、媒体转载核对

P0 核验 6 项 = **5✅ 1⚠️ 0❌**：
1. ✅ Gemini 3.5 Transcribe 真实（Google 官方博客 2026-08-26）
2. ✅ Agora×Gemini 合作（Agora 官方文档 Gemini Live/Vertex AI 集成页 + 教程 + 媒体转载）
3. ✅ Agora Agents SDK 真实（Python/TS/Go 三包，链式/MLLM 两架构）
4. ✅ Smart Transcription 为 Google 已发布能力，博文"计划支持"未来时准确
5. ⚠️ "全球首个 Realtime API"措辞归属含糊：API 为 OpenAI 产品，Agora 为首发语音合作/集成方（2024-10 公测合作，2025-09-04 GA）
6. ✅ 噪声/专业词汇/口语停顿应对与官方表述一致

博文无成效数字；模型性能数字（WER 4.0%/2.6%、快70%、85+语言）均来自 Google 官方引述的 Artificial Analysis 第三方测评。

## 质量门

- G1（信源）：厂商自宣预判 → 全部合作/产品声明 P0 三方佐证；10 权威信源
- G2（结构）：10 文件、3 toctree 块、相对链接、无 file:///、UTF-8 roundtrip
- G3（事实）：F-001~F-032 连续无跳号；事实/观点分离；V 补充事实单独成节并 log 注记；勘误四张清单
- G4（索引）：bundles 280→281、ai 域 107→108、ai-agent 组 28→29（frontmatter=toctree=29）

status: verified；stale_after: 2026-11-30。
