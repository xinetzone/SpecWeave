---
okf_version: "0.2"
type: spec
title: "RAG_Techniques 博文 → OKF 知识包转化规格"
source: "https://mp.weixin.qq.com/s/WsgnBpEtTytatRFkKUlfeA"
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-10-31T11:00:00+08:00" }
---

# RAG_Techniques 博文 → OKF 知识包转化规格

## 1. 任务来源

用户指令：使用 `seven-concepts-cmd` 全面学习微信公众号博文《3万Star！42个notebook，专治RAG答不准》，生成 OKF wiki 教程到 `projects/awesome-okf-xs/doc/bundles`。

- **信源**：微信公众号「架构文摘」，作者「小七」，发布时间 2026-10-27 01:08
- **推文链接**：https://mp.weixin.qq.com/s/WsgnBpEtTytatRFkKUlfeA
- **文章性质**：第三方综述 + 开源项目盘点（拆解 GitHub 仓库 `NirDiamant/RAG_Techniques`）
- **执行 Skill**：`seven-concepts-cmd`（元编排，场景 4 知识沉淀 R→I→E 链路）+ `blog-article-to-okf-wiki`（七阶段工作流门面）

## 2. 步骤 0：内容敏感度预检（结论）

| 判定项 | 检查结果 |
|--------|---------|
| URL 访问控制参数 | 无 `share?code=` / `token=` / 邀请码，仅含广告/样式参数 `bar_style_type`、`from`、`color_scheme` |
| 域名特征 | `mp.weixin.qq.com` 公开推文，非企业内网 |
| 用户标注 | 无「私域/内部/保密」标注 |
| 内容主题 | 公开发布的技术开源项目盘点 |

**结论**：**公开内容（Public）** → 标准工作流。spec 落 `.trae/specs/okf-wiki-ecosystem/rag-techniques-blog-okf-wiki/`，产出物落 `projects/awesome-okf-xs/doc/bundles/`。

## 3. 步骤 2：骨架判定（操作可复现性两问）

| 两问 | 判定 | 依据 |
|------|------|------|
| 问1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **否（部分）** | 博文「安装与配置」节仅给出 `git clone` + `cd` 两行，并明确写「**没有然后了**」；本地流程仅示意 `jupyter lab` + 打开 notebook + 首个 cell 装依赖。作者自述「建议先用 Colab 跑通，再决定要不要本地复现」，未给出完整可照做的本地环境搭建序列 |
| 问2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **否** | 仓库**无 requirements.txt**（无版本锁定）；博文亦未给出任何实测的输入输出对照；Colab 徽章虽存在，但博文未实际执行亦未记录结果 |

**判定结论**：两问**未同时为「是」** → **不设 `examples/`**。

理由补充：
- 主体内容是 42 篇 notebook 的**分类盘点与生态解读**（七段 pipeline 分段、Graph RAG / LightRAG 机制解说、企业落地四建议），而非作者亲自跑通的实测教程；
- 「企业团队怎么用」四节（团队改造/批量部署/流水线集成/规范定制）属**落地建议**，非可复现操作步骤；
- 参照同组先例：`mattpocock-skills`（资讯盘点）、`qbs-book-to-skill`（方法论非操作教程）均正确地无 `examples/`。

**目录骨架**：`index + concepts/ + references/ + log`（技术综述/资讯盘点型）。

## 4. 步骤 3：归属判定

主线实体：**`NirDiamant/RAG_Techniques` 仓库**（RAG 技术集合与学习资源）。

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/learning/` | ✅ **选中** | 该分类语义为「学习路径与实战教程」，已容纳 3 个同类博文转化产物（`mattpocock-skills` 资讯盘点、`free-llm-api-hands-on` 实操、`qbs-book-to-skill` 方法论），证明可容纳非源码类 bundle；RAG_Techniques 本质是**学习资源库**（作者自述「它是学习资源，不是库」F-027） |
| `jishu/ai/frameworks/` | ❌ | 该分类为「Agent 与 LLM 应用的框架、运行时与代码库教程」；博文开篇即声明「**它不是框架**，是一张可执行的 RAG 故障对照表」（F-003），归入框架与主线矛盾 |
| `jishu/ai/practice/` | ❌ | 该分类为「AI 工程方法论、上下文工程、安全红队与行业趋势研究」；本 bundle 主体是**技术方法集合盘点**而非方法论/行业研究 |
| 新建 `jishu/ai/rag/` 分组 | ❌ **禁止** | 违反「单篇博文禁止新建分组」（过度工程，违反最小变更） |

**最终归属**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/learning/rag-techniques/`

## 5. 三层知识地图（concepts 篇目）

| 篇目 | 主题 | 覆盖 F 编号 |
|------|------|------------|
| `concepts/00-intro.md` | 项目概述与定位：仓库身份、30k Star、42 notebook 七段结构、双轨（notebook+脚本）、作者背景 | F-001~F-008、F-030~F-033 |
| `concepts/01-techniques.md` | 技术机制：七段 pipeline 分类详解、Graph RAG 双阶段双路扩图、LightRAG 双层关键词、评估与进阶架构 | F-009~F-016、F-021 |
| `concepts/02-practice.md` | 落地与边界：安装与配置现状、企业团队四步用法、五类适用场景、五项局限与四个具体坑、License 非商用约束 | F-017~F-020、F-022~F-029 |

## 6. 信源距离预判

| 信源 | 距离分类 | 处置 |
|------|---------|------|
| 微信公众号博文 | **第三方综述**（非厂商自宣，但为二手转述） | 全部事实登记 F 编号；P0（数字/日期/成效）走 WebSearch 权威核验 |
| `NirDiamant/RAG_Techniques` 仓库 | **开源项目文档**（一手） | F 核验的权威来源 |
| 配套书《RAG Made Simple》/ 视频 | **厂商自述**（作者自宣标注） | 成效数字默认 P0，标注「作者自述」 |

## 7. 交付物清单

```
projects/awesome-okf-xs/doc/bundles/jishu/ai/learning/rag-techniques/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-intro.md
│   ├── 01-techniques.md
│   └── 02-practice.md
└── references/
    ├── index.md
    ├── article-source.md
    └── verification.md
```

索引同步面（4 处）：
1. `jishu/ai/learning/index.md`：束数 7→8，新增表行 + toctree
2. `jishu/ai/index.md`：learning 类 7→8、ai 域 278→279，description 与正文计数
3. `jishu/index.md`：ai 组描述文本中的 278 束 → 279 束
4. `bundles/index.md`：`total_bundles` 696→697、正文计数行、jishu 域节标题 511→512 束、ai 分组行 278→279
