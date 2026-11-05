---
title: "Craft Anything 博文事实清单（spec 侧 F 编号登记）"
source: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
created: 2026-11-04
---

# Craft Anything 博文事实清单（spec 侧）

> 类型：O=客观事实，V=作者观点/体验，S=厂商自述。核验：✅ 官方一致 / ⚠️ 口径·时效差异（见 bundle `references/verification.md`）/ ➖ 无需外部核验。
> 本文件为 F 编号**双份登记**之一；另一份在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/craft-anything/references/article-source.md`，编号集合一致（F-001~F-043）。
> 博文：微信公众号文章《刚刚开源，5300 人关注的 AI 复刻项目火了》，作者「熊叔」，2026-11-03。F-001~F-023 出自博文，F-024~F-043 为 2026-11-04 官方一手核验补充。

## A. 博文元信息（F-001 ~ F-003）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-001 | O | 博文标题《刚刚开源，5300 人关注的 AI 复刻项目火了》，作者「熊叔」，2026-11-03 载于微信公众号 | ➖ |
| F-002 | O | 博文推介对象为开源项目 **Craft Anything**，称其"刚刚开源"、"5300 人关注"（成文时点口径） | ⚠️ F-033 动态数字 |
| F-003 | O | 博文称项目由 **ArtCraft** 团队开发、以**纯 Rust** 编写 | ⚠️ F-024/F-031（GitHub 归属组织为 `storytold`；语言 Rust ✅） |

## B. 项目定位与模式（F-004 ~ F-009）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-004 | O | 博文称其目标是"看懂任意网站、应用或游戏如何工作，然后让 AI 造出你自己的版本" | ✅ F-025 |
| F-005 | O | 博文称项目提供两种模式：**净室（Clean room）为默认**，另有**深度（Deep）**模式 | ⚠️ F-025 仅确认 clean-room 引擎，Deep 模式博文单源 |
| F-006 | O | 博文称工具白名单为强制约束 | ⚠️ 仅博文单源 |
| F-007 | O | 博文称项目 10 月 31 日建仓 | ✅ F-032 |
| F-008 | O | 博文称作者查看时项目约"四千七百多颗星" | ⚠️ F-033 时效差异 |
| F-009 | O | 博文称项目处于早期 alpha，11 月 2 日发布 v0.3.0 | ✅ F-034 |

## C. 相似度检查机制（F-010 ~ F-016）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-010 | O | 博文称检查在 1440 / 768 / 390 三种宽度下比对 | ✅ F-037 |
| F-011 | O | 博文称相似度取"布局"与"画面细节"两项的平均 | ✅ F-037 |
| F-012 | O | 博文称跨页面再取平均 | ✅ F-037 |
| F-013 | O | 博文称原站自身会变动的部分用"连拍三次"剔除 | ⚠️ 仅博文单源 |
| F-014 | O | 博文订正截图清单：390px 宽度下网页横向滚动，实际渲染宽度为 412px | ⚠️ 博文自身勘误（无独立源） |
| F-015 | O | 博文举例相似度：起始页 90%、about 页 91%、"右边"93% | ⚠️ 博文示例（无独立源） |
| F-016 | O | 博文称最多迭代 6 轮收敛，或相似度到九成即停止 | ✅ F-037 |

## D. 工具与集成（F-017 ~ F-020）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-017 | O | 博文称项目有 **314** 个工具，每个工具既是 CLI 子命令也是 MCP 工具 | ⚠️ F-036/F-041 口径差异 |
| F-018 | O | 博文称构建需安装并登录 **Claude Code** | ✅ F-039 |
| F-019 | O | 博文称 **Codex 适配器**尚未在真实安装中验证 | ⚠️ 官方自述（README Status "Partly there" 同向） |
| F-020 | O | 博文称提供人机审批卡片（human approval） | ⚠️ 仅博文单源 |

## E. 官方状态自述与安装（F-021 ~ F-023）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-021 | O | 博文称**净室模式的完整实跑**，官方状态页写着"还没做过" | ⚠️ 官方自述（无一手页面原文核对） |
| F-022 | O | 博文称官方记录过一次跑通在 **10 月 18 日**，网站做到 **96%** 相似度，耗时**一分半** | ⚠️ 时间线存疑（早于仓库建仓日 2026-10-31，见勘误①） |
| F-023 | O | 博文给出安装包形态：Windows（msi + 便携）、macOS（dmg）、Linux（AppImage/deb/Flatpak）、WASM 查看器 | ⚠️ F-035 部分核验 |

## F. 官方一手核验补充（F-024 ~ F-040，2026-11-04）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-024 | O | 仓库 `storytold/craft-anything`，归属组织 `storytold`，默认分支 main | ✅ GitHub API |
| F-025 | O | 官方一句话定位（README）："See how any website, app or game works, then have AI build your own version; an open-source, clean-room engine in pure Rust." | ✅ |
| F-026 | O | 官方 About："Craft Anything: understand how any software works, and craft your own." | ✅ |
| F-027 | O | 官方四步流程：Study → Build → Check → Ready | ✅ |
| F-028 | O | 前置依赖：**Rust 1.97+** | ✅ |
| F-029 | O | 构建命令示例 `craft-anything-cli rebuild`；项目文件夹含 craft.json / capture / app / checks / investigation.cany / inbox | ✅ |
| F-030 | O | 许可：**Apache-2.0**（GitHub API `license.spdx_id=Apache-2.0`）；仓库页另标注 "Apache-2.0, MIT licenses found" | ✅ |
| F-031 | O | 主语言 Rust；仓库体积约 8974 KB；默认分支 main | ✅ |
| F-032 | O | 创建时间 2026-10-31T14:50:00Z；最近推送 2026-11-04T01:45:16Z | ✅ |
| F-033 | O | 时点快照（2026-11-04）：Star **8531**、Fork **1422**、Open Issues **149**、Watch/订阅 36 | ✅ 动态数字 |
| F-034 | O | 最新 release：**v0.3.0**，发布于 2026-11-02T17:58:25Z | ✅ |
| F-035 | O | v0.3.0 发布资产含 Linux（aarch64 AppImage + .zsync、.deb、.flatpak、.pkg.tar.zst、.rpm、.tar.gz）与 FreeBSD（aarch64 / x86_64 tar.gz）系列 | ⚠️ 抓取样例，未穷尽全部资产 |
| F-036 | O | 官方 STATUS.md（updated 2026-11-04）：**300 个引擎工具（含 AI 与 setup 层共 320 个）** | ⚠️ 与博文 314 口径并存 |
| F-037 | O | 官方检查机制口径：检查在 1440/768/390 px 进行；likeness = 布局相似度与感知细节（SSIM）相似度的均值，跨页取平均；最多 6 轮或达 90% 停止 | ✅ 与 F-010~F-016 一致 |
| F-038 | O | 官方口径：builder turns 单次最长可运行 24 小时 | ✅ |
| F-039 | O | 官方口径：live runs 使用 **Claude Code 2.1.316**，在一台 Mac 上（2026-11-02） | ✅ |
| F-040 | O | 官方口径：2026-10-23 基线审计 923 项测试通过 | ✅ |

## G. 第三方报道交叉（F-041 ~ F-043）

| F编号 | 类型 | 事实 | 核验 |
|-------|------|------|------|
| F-041 | O | 第三方（kitploit）称"314 CLI/MCP inspection tools" | ⚠️ 与 F-036 口径并存 |
| F-042 | O | 第三方（madrobot.blog）称 11 月 1 日发布、代码 10 月 31 日上线 GitHub | ✅ 与 F-032 一致 |
| F-043 | O | 第三方（opennet.ru）称许可为 MIT + Apache 2.0、提供 Linux/FreeBSD/Windows/macOS 构建与 WASM 浏览器版 | ⚠️ 与 F-030 部分一致 |

---

## 双份一致性核对

- 本文件 F 编号集合 = {F-001 … F-043}，连续无跳号（A~G 节为题组，非编号）。
- 与 bundle `references/article-source.md` 编号集合逐一相等。
- V 阶段补充事实：无（全部核验事实在 R 阶段一次性登记）。
