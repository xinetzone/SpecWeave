# 洞察与萃取（tao-ai-knowledge 复盘）

> **复盘对象**：`d:\spaces\chaos\libs\tests\Claw\tao-ai-knowledge`
> **日期**：2026-08-07
> **方法论**：七概念 I（洞察）→ E（萃取）
> **来源事实**：[README.md](README.md) 二、复盘环节 2.3 数据表

---

## 一、核心洞察（3 条，四元组：陈述 / 证据 / 反常识 / 行动）

### 洞察 1：文档与实现的「规划-落地」断层

- **陈述**：项目存在大量"文档声称已规划/已选型"但代码未落地的技术栈与模块，架构文档描述的蓝图（Prisma/Algolia/Zustand/支付/飞书/社区 CRUD）与仓库实际实现严重脱节，README 声称已完成的功能（如搜索用 Fuse.js）实际为 mock。
- **证据**：
  - 架构文档称用 Prisma 5.0+/Algolia，但 `node_modules/@prisma`、`algoliasearch` 均未安装（命令验证 False）。
  - `package.json` 声明 `test/jest` scripts，但 jest 未安装、`jest.config.js` 不存在、测试文件数为 0。
  - README 列 Fuse.js 为搜索方案，但 `src/app/api/search/route.ts` 返回写死的 `mockData`，未引用 Fuse.js。
  - 架构文档描述的 `(marketing)`/`(platform)` 路由分组与 README 的 `(main)` 分组均不存在，页面直接位于 `src/app/` 平铺。
- **反常识**：一个以"知识库/内容"为核心卖点的项目，最应扎实的内容数据层反而全部是占位符——81 章只有 4 章有原文，其余都是"待补充"；且文档写得越详细，与实现差距越大。
- **行动**：以"实现为唯一事实源"重构 README/ARCHITECTURE，删除或明确标注未落地的技术选型；优先夯实内容数据层（补齐 81 章或接入数据源）。

### 洞察 2：认证体系"双轨并存"且服务端密钥治理失守

- **陈述**：认证实际采用「自研 Supabase REST + SecondMe OAuth」双轨，`next-auth` 依赖虽已安装却未使用；同时 Supabase 真实 service role key 与 anon key 被硬编码进 `.env.example` 存在泄露风险，`secondme/me` 接口返回硬编码未认证。
- **证据**：
  - `node_modules/next-auth` 存在（True），但代码中无任何 `next-auth` 引用；login/register 用 `fetch` 直接调 Supabase auth REST。
  - `.env.example` 含真实 supabase URL `hnwlvtcwsdsiezpnrvbm.supabase.co` 与真实 service role key `sb_secret_...`（本应放占位符）。
  - `src/app/api/auth/secondme/me/route.ts` 忽略读取的 cookie，返回固定 `authenticated: false`。
  - `login/route.ts` 用 `SUPABASE_SERVICE_ROLE_KEY` 在 API 路由做 token 交换。
- **反常识**：越是想"开箱即用"的 `.env.example`，越容易变成密钥泄露的出口——示例文件本该放占位符，却放了真实生产凭据；且"装了 next-auth 却不用"说明选型未收敛。
- **行动**：立即轮换泄露的 Supabase 密钥；`.env.example` 改纯占位符；收敛为单一认证栈；修复 `me` 接口的硬编码返回。

### 洞察 3：产品"重包装、轻内核"——营销文档远重于实际功能

- **陈述**：`products/ai-programming-monetization` 的营销文档（产品设计/定价/推广/用户画像）非常完整精细，而实际可运行的 Web 功能停留在静态 mock 页面层，形成鲜明反差。
- **证据**：
  - products 目录有 7 个文件，含完整定价三档（¥399/999/2999）、推广计划（首发 7 天）、用户画像（A/B/C 三类）、12 章内容大纲（含字数）。
  - `community/page.tsx`、`learn/page.tsx`、`classic/page.tsx` 内容全部为硬编码静态数据，无任何数据库读写。
  - 首页"精选章节"、社区统计数据（成员 1234、笔记 567）等均为写死的演示值。
- **反常识**：对内容变现产品，花在"卖"上的文档功夫远大于"造"的工程功夫，易导致"发布后无真实内容可交付"的信任崩塌。
- **行动**：优先补齐核心内容（道德经 81 章 + AI 专栏章节），将营销文档的销售主张降级为路线图，避免过度承诺。

---

## 二、可复用模式萃取（2 个，均 L1-draft）

### 模式 1：文档-实现对齐审计（doc-impl-alignment-audit）

- **触发场景**：当项目进入里程碑复盘，或发现"文档声称的功能与代码对不上"、接手遗留项目、评估他人项目时。
- **核心做法**：
  1. 以代码仓库为唯一事实源，列出所有已安装依赖、实际 API 路由、真实页面。
  2. 逐项比对文档声称的技术选型、模块、功能。
  3. 分类标注：`已落地` / `已安装未使用` / `仅规划未实现` / `纯占位`。
  4. 对未落地项删除或降级为"路线图"。
  5. 生成"文档↔实现"对齐矩阵，纳入复盘质量门。
- **反模式（不要这么做）**：
  - ❌ 凭 README 判断项目真实状态（README 是营销，不是事实源）。
  - ❌ 文档先行但从不回校（"设计蓝图"停留在纸面）。
  - ❌ 先装依赖后用不上（next-auth/Prisma/Algolia 装了即"已完成"的错觉）。
- **检验标准**：对齐矩阵中"已落地"项能对应到真实文件/依赖；"仅规划"项有明确路线图标注而非伪装成已实现。
- **迁移示例**：
  - 场景 1（非当前领域）：接手任何开源项目前的尽职调查清单。
  - 场景 2（跨领域）：技术债评估、外包交付验收、软件采购选型。

---

### 模式 2：环境变量占位符纪律（env-placeholder-hygiene）

- **触发场景**：任何创建 `.env.example`、提交配置模板、搭建可复用脚手架时。
- **核心做法**：
  1. 示例文件一律只用占位符（`your-xxx`、`<your-project>.supabase.co`）。
  2. 真实密钥只放 `.env.local`，并确保 `.gitignore` 排除 `*.local`。
  3. 提交前用 grep 扫描仓库内是否残留真实密钥格式（如 `sb_secret_`、`sk-`）。
  4. 一旦发现真实密钥进入版本控制，立即轮换并清除历史。
- **反模式（不要这么做）**：
  - ❌ 为"开箱即用"在示例文件填真实密钥。
  - ❌ 忽略 `.gitignore`，把 `.env*` 一并提交。
  - ❌ 泄露后只改本地文件而不轮换远端密钥。
- **检验标准**：`.env.example` 中 grep 不到任何真实凭据；`git grep` 仓库内无 `sb_secret_`/`sk-` 等敏感模式。
- **迁移示例**：
  - 场景 1（非当前领域）：任何 SaaS、开源库、微服务脚手架的环境配置。
  - 场景 2（跨领域）：团队 onboarding 文档、CI/CD 密钥管理、云资源初始化模板。

---

> **成熟度说明**：以上 2 个模式均基于单一案例（tao-ai-knowledge 复盘）萃取，符合 L1-draft（单案例待验证）。需在后续 ≥1 个独立项目中验证后方可升级为 L2-validated。
