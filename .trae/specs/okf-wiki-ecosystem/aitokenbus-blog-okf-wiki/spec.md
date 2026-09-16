---
id: "aitokenbus-blog-okf-wiki"
version: "0.1.0"
scenario: knowledge
topic: AITokenBus Token共享交换平台
url: https://mp.weixin.qq.com/s/wtGxzSy0PvhoVAdhH-4fxw
author: 唐霜（独立开发者，tangshuang.net）
published: 2026-07-22
status: stable
---

# 规格：AITokenBus Token 共享与交换平台（博文 → OKF 知识包）

## 内容敏感度预检

| 项目 | 结论 |
|------|------|
| URL 特征 | `mp.weixin.qq.com` 公开文章，无 `share?code=`/`token=`/邀请码参数 |
| 内容级别 | **公开（Public）** → 标准工作流 |
| spec 位置 | `.trae/specs/okf-wiki-ecosystem/aitokenbus-blog-okf-wiki/` |
| 产出位置 | `projects/awesome-okf-xs/doc/bundles/jishu/ai/aitokenbus/` |
| 信源距离 | **厂商/个人开发者自宣**（作者即平台创建者，第一人称"我上线了…"）——所有产品能力与成效类声明默认 P0；零独立第三方信源 |

## 骨架判定（操作可复现性两问）

| 两问 | 答案 |
|------|------|
| ① 是否有读者可照做的安装/配置/代码/调用/实测流程？ | **否**。文中仅"访问网址→注册→托管 API 地址与 Key→建池→发邀请链接"的概念性描述，无 API 文档、无 base_url/请求示例、无版本、无输入输出 |
| ② 是否经作者实测、具备可复现性？ | **否**。无操作截图、无实测数据、无步骤级输入输出，属产品理念与功能发布介绍 |

**判定**：任一问为"否" → **不设 `examples/`**。内容性质 = **产品自述发布资讯（技术产品，非操作教程）**。

骨架：`index.md + concepts/ + references/ + log.md`（无 examples）。

## 归属位置分析（决策树 + 候选对照表）

主线实体 = AITokenBus 平台本身。

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/aitokenbus/`（选定，直挂束） | ✅ | ① 文章 100% 围绕 AITokenBus 展开，主线实体即产品名；② `jishu/ai/` 已有大量博文转化直挂束先例（token-economy-explosion、domestic-model-token-export、free-llm-api-roundup、mattpocock-skills 等 40+ 产品/主题束）；③ 域索引导语明确将此类列为"工程方法论等直挂束"；④ 与 token-economy-explosion、free-llm-api-roundup 构成 Token 经济/免费 API 主题互链 |
| `jishu/ai/token-economy-explosion/` 内成束 | ❌ | 该束是宋鸿兵宏观 Token 经济单篇分析，AITokenBus 是具体产品，粒度不匹配；以"主题关联"互链即可 |
| `jishu/ai/free-llm-api-roundup/` 内成束 | ❌ | 该束是 40 家免费 API 平台盘点，AITokenBus 非盘点对象且自有官网（核验日该盘点未收录）；互链即可 |
| `sheke/industry/` | ❌ | 行业趋势分析域，本文是具体产品发布介绍，非行业研究 |
| 新建顶级分组 | ❌ | 单篇博文禁止新建分组（违反最小变更）；`jishu/ai/` 直挂束即既定承接形态 |

## 知识拆分规划（三层，无 examples）

| 层次 | 文件 | 核心内容 |
|------|------|---------|
| 产品事实层（What/When/Who） | concepts/00-platform-overview.md | 发布事实、作者与信源矩阵、平台实测现状、核心数据（8 挂售/71 节点/2 在线/35 模型仅 1 可用） |
| 机制原理层（How） | concepts/01-token-sharing-mechanism.md | 共享池/Token 市场/TC 经济模型/免费矿池/GPU 贡献/路由分流，API 形态，含 Mermaid 生态流转图 |
| 边界与风险层（Why/Risk） | concepts/02-risks-and-boundaries.md | 营销宣称 vs 实测差距、账号条款/共享 API Key 合规风险、运营主体透明度、版本号勘误、读者使用边界 |

## P0 核验范围与结论摘要

| # | P0 声明 | F 编号 | 结论 |
|---|---------|--------|------|
| 1 | 平台已上线、网址可访问 | F-002/F-025/F-037 | ✅ 实测在线（2026-09-16） |
| 2 | 托管 Key 建共享池 + 邀请链接 | F-014/F-026 | ✅ 前端代码与公开接口可见 |
| 3 | Token 市场挂售、TC 支付交换 | F-015/F-027 | ✅ 公开可浏览，实测 8 个 active 挂售 |
| 4 | 官方免费矿池注册即用 | F-018/F-028 | ⚠️ 存在但供给极薄（2 节点在线、35 模型仅 1 可用） |
| 5 | 本地 ollama 算力贡献换 TC | F-017/F-031 | ⚠️ GPU 挖矿机制存在，"ollama"零佐证 |
| 6 | 路由分流 + 故障自动切换 | F-019/F-030 | ⚠️ 分流✅；跨池自动 failover 无公开说明 |
| 7 | TC 无法币兑换、不可转让 | F-013/F-029 | ⚠️ 产品行为一致但无任何条款公示 |
| 8 | "免费无限用 AI"（标题） | F-020/F-028 | ⚠️ 营销修辞，与供给现状差距显著 |
| 9 | glm-5.2 已跻身顶级 | F-021/F-033 | ✅ 2026-06-15/16 上线，ID `glm-5.2` |
| 10 | kimi-k3 已跻身顶级 | F-021/F-034 | ✅ 2026-07-16/17 发布（发文前 5 天） |
| 11 | qwen-3.8 已跻身顶级 | F-021/F-035 | ❌ **时间错位**：2026-08-03 才发布，官方 ID 为 `qwen3.8-*` |
| 12 | 运营主体/独立信源 | F-032/F-036 | ❌ 零独立信源、无 ICP/主体/协议（透明度风险，非事实性错误） |

**状态管理**：核心产品声明（平台与五大功能）经实地独立核验基本属实 → `status: stable`；两处 ❌ 中 qwen 版本号属**非核心顺带提及**（走勘误，正文呈现正确值），主体缺失属**风险提示**而非主结论证伪。不触发 flagged；但因自宣属性强、供给薄、无合规文本，index 顶部加"厂商自述"提示块，`stale_after: 2026-12-31`。

## 质量门检查点

- G1：事实无推断词；作者观点逐条标注 → facts.md（F-001~F-037，其中 F-001~F-024 博文源、F-025~F-037 核验补充）
- G3：信源先行；所有具体声明引用 F 编号；勘误在正文落实
- G4：双份 F 编号集合一致（37=37）；三级 toctree 全可达；计数按 gate 地面真值收敛为 555 束 / ai 203 / jishu 422（入库当日并行会话另有 16 个 WIP 束，共 17 个新束；已提交基线为 538）；直接运行 check-bundles-index/check-toctrees/check-utf8 三门全绿

## 参考先例

- [token-economy-explosion/](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/token-economy-explosion/)（Token 经济主题互链 + 自宣/分析类 bundle 结构参考）
- [free-llm-api-roundup/](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/free-llm-api-roundup/)（免费模型 API 主题互链）
- [bytedance-ai-consolidation（商业分析无 examples 先例）](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/trae/)
