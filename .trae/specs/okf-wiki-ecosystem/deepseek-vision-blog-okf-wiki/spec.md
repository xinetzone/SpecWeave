---
status: "draft"
version: "1.0"
---

# DeepSeek 视觉模型博文 → OKF Wiki 教程 Spec

## Why

微信公众号文章《DeepSeek 多模态视觉实验模型发布！》（公众号"湖北"，2026-08-21，收录于"AI开发笔记"）报道了 DeepSeek-V4-Flash-Vision-Exp 实验性视觉模型的发布，并系统给出了跨厂商视觉模型选型建议（GLM-4.6V-Flash、Doubao-Seed-2.0-mini、Gemini 2.5 Flash-Lite、GPT-5 nano、MiniCPM-V 4.6、DeepSeek-OCR-2、GLM-OCR）以及"视觉模型感知 + DeepSeek 推理"的双模型协作落地模式。该博文属于**博文类公开内容**，蕴含可沉淀的选型知识与架构模式，需转化为 OKF 知识包纳入 awesome-okf-xs 体系。

## 归属位置分析（博文类内容判定）

**结论：放置于 `projects/awesome-okf-xs/doc/bundles/ai/deepseek/vision-model-selection/`（DeepSeek-AI 分组下新建 bundle）**

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `ai/deepseek/`（选定） | ✅ | ① 博文主线是 DeepSeek 视觉模型发布，双模型管线也是"视觉模型只做感知、DeepSeek 负责推理判断"；② 分组内已有非源码类 bundle 先例（`awesome-deepseek-agent` 为资源列表，`deepseek-ocr`/`deepseek-ocr2` 为应用模型介绍），且文中推荐的 DeepSeek-OCR-2 已有对应 bundle，可交叉引用；③ 分组定位可自然扩展为"DeepSeek 模型生态" |
| `ai/agnes-ai/` | ❌ | 特定厂商（AgnesAI）平台教程，主题不符 |
| `ai/ai-agent/` | ❌ | Agent 框架源码解读，主题不符 |
| `ml/` | ❌ | ONNX 模型生态，聚焦模型交换格式与推理后端 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**内容敏感度预检**：微信公开博文，无访问控制 → 公开内容 → 标准工作流（spec 位于 `.trae/specs/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`）。

## What Changes

- **新增** OKF bundle：`ai/deepseek/vision-model-selection/`，bundle 名"多模态视觉模型选型指南"
  - `index.md`（bundle 根索引，frontmatter 含 `sources` 指向微信博文 URL）
  - `log.md`（生成日志）
  - `concepts/`（4 篇概念文档 + 子目录索引）
  - `examples/`（3 篇示例文档 + 子目录索引）
  - `references/`（博文信源事实清单 + 子目录索引）
- **更新** `ai/deepseek/index.md`：新增 bundle 导航条目（12→13 束），在"应用模型与资源"小节追加
- **更新** `bundles/index.md`：总数 268→269，DeepSeek 分组束数 12→13
- **新增** 可复用模式文档：`.agents/docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md`（博文类文章→OKF 知识包转化模式），以本次 vision-model-selection bundle 为首个演示案例（demo）
- **更新** `.agents/docs/retrospective/patterns/documentation-patterns/README.md`（如该分类索引需登记新模式条目）
- **不修改** 源博文及 `external/` 下任何内容（博文为外部 URL，无本地文件）

## Impact

- **Affected specs**: 无（独立新增知识包 + 新增模式沉淀）
- **Affected code**: 无代码改动，仅文档新增与索引更新
- **Affected files**:
  - 新增：`projects/awesome-okf-xs/doc/bundles/ai/deepseek/vision-model-selection/` 整个目录（约 12 个文件）
  - 更新：`projects/awesome-okf-xs/doc/bundles/ai/deepseek/index.md`
  - 更新：`projects/awesome-okf-xs/doc/bundles/index.md`
  - 新增：`.agents/docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md`
  - 更新：`.agents/docs/retrospective/patterns/documentation-patterns/README.md`（登记新模式）

## 信源与事实基础（R 阶段采集）

**博文核心事实**（转化的唯一信源，编号 F-001 起）：

1. DeepSeek 发布实验性视觉模型 DeepSeek-V4-Flash-Vision-Exp（名字带 Exp，实验性质）
2. 支持通过官方 API 传图片：JPEG/PNG/GIF/WebP 格式，可接收 Base64、图片链接和 Files API 文件
3. 主打图片理解，不负责生成图片，未同步开放模型权重；V4-Flash 和 V4-Pro 普通版不能直接吃图
4. 选型推荐（5 类场景）：
   - 零成本尝鲜：GLM-4.6V-Flash（免费；中文截图/UI 页面/商品图片/普通 OCR）；不满足再换 FlashX（输入 $0.04、输出 $0.40/百万 tokens）
   - 国内生产：Doubao-Seed-2.0-mini（图像/视频/音频/文本，输入 ¥0.2、输出 ¥2/百万 tokens 起，人民币结算方便；需实测并发/限流/SLA）
   - 多图/长视频/海外：Gemini 2.5 Flash-Lite（图像/视频/文本，输入 $0.10、输出 $0.40/百万 tokens；给 DeepSeek 提供视觉事实没必要上 Gemini Pro）
   - 图片分类/简单截图/结构化抽取：GPT-5 nano（便宜）；不能上云则本地部署 MiniCPM-V 4.6（约 1.3B 参数，可 Ollama 运行）
   - PDF/扫描件/票据/表格：优先 DeepSeek-OCR-2 或 GLM-OCR（保留布局、控成本、生成 Markdown；复杂表格/小字/模糊件需抽样验收）
5. 落地模式：视觉模型只返回 OCR 文本、物体、位置关系、表格和不确定项，再交给 DeepSeek 判断——输出 tokens 更少、结果可缓存、避免两模型重复推理
6. 总结口诀：个人尝鲜用 GLM，国内生产用豆包，长视频用 Gemini，本地隐私用 MiniCPM，文档识别上 OCR 专用模型

## ADDED Requirements

### Requirement: Bundle 根索引
The system SHALL provide `vision-model-selection/index.md`，frontmatter 遵循 OKF v0.2（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources），`sources` 指向微信博文 URL 并注明公众号与发布日期。

#### Scenario: 用户定位知识包
- **WHEN** 用户打开 `ai/deepseek/vision-model-selection/index.md`
- **THEN** 包含：知识结构总览（concepts/examples/references 三层）、分层导航表、信任与生命周期说明、已知边界（Exp 模型与价格信息时效性声明）、toctree

### Requirement: 概念文档（concepts/）
The system SHALL provide 4 篇概念文档 + 子目录 index.md。

#### Scenario: 用户系统学习视觉模型选型
- **WHEN** 用户阅读 concepts/
- **THEN** 包含：
  - `00-deepseek-vision-exp.md`：DeepSeek-V4-Flash-Vision-Exp 模型详解——实验性质定位、API 传图方式（格式/Base64/URL/Files API）、能力边界（只理解不生成、未开放权重）、与 V4-Flash/V4-Pro 的关系
  - `01-selection-landscape.md`：视觉模型全景与选型维度——候选模型清单（7 个）、五个选型维度（成本/地域合规/模态覆盖/隐私/文档复杂度）
  - `02-scenario-matrix.md`：按场景选型矩阵——五类场景（零成本尝鲜/国内生产/多图长视频海外/简单抽取与本地隐私/文档 OCR）的推荐模型、价格数据、注意事项
  - `03-vision-reasoning-pipeline.md`：视觉-推理双模型协作架构——分工原则（视觉模型只返回 OCR 文本/物体/位置关系/表格/不确定项，DeepSeek 负责判断）、三大收益（输出 token 少/可缓存/避免重复推理）
  - `index.md`：子目录索引

### Requirement: 实战示例（examples/）
The system SHALL provide 3 篇示例文档 + 子目录 index.md。

#### Scenario: 用户按示例落地选型
- **WHEN** 用户阅读 examples/
- **THEN** 包含：
  - `cost-scenario-walkthrough.md`：成本-场景选型演练（如"识别报错弹窗"为何不必上旗舰视觉模型）
  - `pipeline-output-structure.md`：视觉模型输出结构设计示例（OCR 文本/物体/位置关系/表格/不确定项的结构化返回格式）
  - `selection-decision-tree.md`：选型决策树（个人尝鲜→GLM；国内生产→豆包；长视频→Gemini；本地隐私→MiniCPM；文档→OCR 专用）
  - `index.md`：子目录索引

### Requirement: 信源登记簿（references/）
The system SHALL provide 博文信源事实清单 + 子目录 index.md。

#### Scenario: 事实可溯源
- **WHEN** 用户查阅 references/
- **THEN** 包含 `article-source.md`（F-001 起编号的博文事实清单，每条标注原文位置）与 `index.md`；所有概念/示例文档中的事实引用 F 编号

### Requirement: 分组与总索引更新
The system SHALL update 分组索引与总索引。

#### Scenario: 导航可达
- **WHEN** 用户从总索引浏览
- **THEN** `ai/deepseek/index.md` 的"应用模型与资源"表格新增 vision-model-selection 条目（束数 12→13），`bundles/index.md` total_bundles 268→269、DeepSeek 分组束数 12→13，toctree 追加新条目

### Requirement: 博文转化模式沉淀（主任务完成后执行）
The system SHALL provide 可复用模式文档 `.agents/docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md`，遵循模式库 frontmatter 规范（id/title/date/source/maturity/validation_count/reuse_count/tags/pattern_type/category）与标准结构（触发场景/核心步骤/反模式/迁移验证），以本次转化任务为首个演示案例（demo）。

#### Scenario: 后续遇到同类博文类文章
- **WHEN** 用户提交新的博文/资讯类 URL 要求转化为 OKF 知识包
- **THEN** 按模式文档执行：①内容敏感度预检（公开/私域分流）②归属判定决策树（主线实体优先→分组先例→避免新建分组）③事实采集（F 编号登记 + 单源标注 + 可核验项轻量核验）④知识结构三层拆分（事实层/矩阵层/模式层）⑤bundle 生成（concepts/examples/references）⑥索引更新与链接验证
- **THEN** 反模式覆盖：无信源转述、忽视时效性声明、单篇博文新建分组、私域内容入公共 specs 区等
- **THEN** 迁移验证记录：✅ 首个案例 vision-model-selection bundle（2026-08-28）

## 约束与已知边界

- **单一信源**：本 bundle 唯一信源为微信博文；文中模型名与价格为博文发布时点信息（如 DeepSeek-V4-Flash-Vision-Exp 为实验版本，GLM-4.6V-Flash 免费政策等），需在"已知边界"中声明时效性
- **价格与模型能力声明**：以博文为信源登记事实，不做无信源的二次加工；如官方文档可公开核验的关键声明（DeepSeek 视觉模型存在性），可在 V 阶段做轻量核验并标注
- **交叉引用**：文中 DeepSeek-OCR-2 对应已有 bundle `ai/deepseek/deepseek-ocr2/`，概念文档中应使用相对路径交叉引用
- **路径规范**：遵循 awesome-okf-xs 现有 bundle 结构（index.md + concepts/ + examples/ + references/ + log.md），frontmatter 与 agnes-ai-models 等现有 bundle 保持一致

<!-- changelog -->
<!--
- 2026-08-28 | initial | 初始版本：博文类内容归属分析与 OKF bundle 转化方案
-->
