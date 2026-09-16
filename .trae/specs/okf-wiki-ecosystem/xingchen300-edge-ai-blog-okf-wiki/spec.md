---
title: "Spec：星辰300 端侧 AI 博文 → OKF 知识包"
status: "draft"
---

# Spec：星辰300 端侧 AI 博文 → OKF 知识包

## 目标

将微信公众号「硅基之声」博文《端侧AI算力新解法：CPU+NPU异构如何让嵌入式设备"本地觉醒"》（2026-09-14）转化为 OKF v0.2 知识包，归属 `jishu/iot/` 分组，bundle 名 `xingchen-300-edge-ai`。

## 内容敏感度预检（阶段 0）

- URL：`https://mp.weixin.qq.com/s/wF73pvBDlMQNn9lIopAOcw`（无 `share?code=`/`token=`/邀请码等访问控制参数）
- 微信公众号公开文章 → **公开内容（Public）**，走标准工作流
- spec 位于 `.trae/specs/okf-wiki-ecosystem/xingchen300-edge-ai-blog-okf-wiki/`，产出位于 `projects/awesome-okf-xs/doc/bundles/`

## 信源距离预判

**厂商自宣（二手改写通稿）**：公众号"硅基之声"非安谋科技官方账号；核验确认博文内容逐字对应安谋科技官方通稿（界面新闻 2026-09-07 标注"商讯"的付费商业稿、EET-China 2026-09-13 完整版署名自媒体"白话IC"，多媒体同稿分发不构成独立多源）。全部能力结论无第三方实验室复测、无精度/时延/功耗公开数据。成效数字一律按 P0 核验，bundle 顶部加"厂商自述"提示块。

## 骨架判定（操作可复现性两问）

1. 博文中有读者可照做的安装/配置/代码/调用/实测流程吗？❌（仅列举模型名、演示形态与应用领域，无代码、无版本、无步骤）
2. 流程经作者实测且可复现吗？❌（非作者实测，为安谋科技 FPGA demo 视频与通稿改写）

→ **任一为"否"：不设 examples/**。内容性质为**技术综述/资讯盘点（厂商产品资讯）**，骨架 index + concepts/ + references/ + log。

## 归属位置分析（决策树）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/iot/`（选定） | ✅ | 主线实体"星辰300"是 AIoT/嵌入式原型平台（Cortex-M MCU + microNPU + MPS3 IoT 原型板），端侧物联网语义最贴；组内已有非源码类先例（sunlogin 产品矩阵、oray 公司生态、comparison 厂商对比） |
| `jishu/ai/` | ❌ | 187 束主体为云侧大模型/Agent/LLM 应用生态，无 TinyML/MCU 端侧硬件锚点 |
| `jishu/ml/` | ❌ | ONNX/TVM 模型工具链（编译器/推理后端），非芯片平台 |
| `sheke/industry/` | ❌ | AI 行业商业趋势快照；本文为技术产品资讯与架构机制介绍，非商业分析 |
| 新建分组 | ❌ | 单篇博文禁止新建分组（最小变更原则） |

组内接入方式：新增"📰 端侧 AI 资讯（博文核验）"板块（现有 5 束为源码教程/产品矩阵/横向对比，语义不符），导语补一句方法论链路说明（博文核验 R→I→E→V，区别于源码深读）。

## 事实与核验（R）

- F-001~F-015 来自博文（元信息 2 + 平台事实 5 + 技术叙事 4 + 用例 4；其中 F-015 为厂商叙事/作者改写）
- F-016~F-029 为 14 条核验补充（含 5 项重要勘误/口径补正）
- P0 核验分两路独立执行：厂商侧 V1~V6（安谋科技/星辰300/STAR-MC2/MPS3）、Arm 侧 H1~H4（Helium/Ethos-U55/五个模型/软件栈）
- **勘误四张清单命中**：
  - ①日期/版本：STAR-MC2 发布于 2022-07-06，早于 Cortex-M52 全球命名（2023-11-22）；"近日跑通"实为 2026-07 WAIC 已演示
  - ②成效数字溯源：Helium 5×/15× 主体是 Cortex-M55（2020）对"前几代 Cortex-M"的泛称基线，**非 M52 数字**（M52 官方 ML 5.6×/DSP 2.7×）；"32MHz→500MHz/1GHz 提速 20-30 倍"为厂商线性外推
  - ③口径对照：0.5 TOPS 是 U55 顶配 256MAC@1GHz 峰值（配置区间 64–512 GOPS）；32MHz 是 FPGA 软核时钟非芯片频率
  - ④名称/引文：博文"ESR"高置信为 **SESR**（Arm Research, arXiv:2103.09404）漏字；U55 不原生支持 Transformer，Conformer 靠 Vela 算子分区回退 CPU
- **状态裁决**：核心声明（平台存在 + FPGA 跑通四用例）有厂商通稿+WAIC 现场报道+商用芯片旁证（Synaptics SYN765x），失败项均为支撑性营销数字/名称，非核心声明 → `status: stable`，但勘误必须完整、正文呈现正确值、顶部"厂商自述"提示

## 知识地图（I：三层拆分，技术综述/资讯类）

| 层 | 文件 | 内容 |
|----|------|------|
| references | article-source.md | F-001~F-029 双份事实登记（与 facts.md 集合一致） |
| references | verification.md | V1~V6 + H1~H4 核验报告、勘误四清单、信源距离、权威 URL |
| concepts/00 | platform-and-demos.md | 事件事实层：平台构成、时间线（WAIC 首发→9月通稿）、四用例与模型、MPS3/32MHz、目标应用领域（厂商宣称） |
| concepts/01 | cpu-npu-heterogeneous-design.md | 机制原理层：CPU/NPU 分工、Helium 数字勘误与代际对照、Ethos-U55 规格与 Vela 图分区、Corstone 组合对照、Synaptics 商用先例 |
| concepts/02 | model-zoo-and-trust-boundaries.md | 生态/边界层：五模型档案（含 SESR 名称勘误）、软件栈、英文语料/单源/外推/非量产等可信边界 |

## 质量门

- G1：事实句无因果推断词，全部 F 编号可溯
- G2：洞察四元组（现象→机制→边界→信源）；作者/厂商观点与事实分层
- G3：信源先行、F 编号双份集合一致、index 最后写
- G4：toctree 三级完整、相对链接可达、UTF-8 strict、计数同步（bundles 537→538 / jishu 405→406 / iot 5→6）

## 门禁环境

`invoke gates.*` 依赖 optional-dependencies.doc（invocations）；若环境不可用，执行手动等效验证清单（toctree 条目 Test-Path、相对链接 Grep 核对、UTF-8 strict roundtrip、双份 F 编号集合比对）并在 log.md 注明，禁止声称"gates 通过"。
