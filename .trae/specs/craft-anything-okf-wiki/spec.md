---
title: "Craft Anything 博文 → OKF 知识包转化"
status: completed
created: 2026-11-04
source: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
target: "projects/awesome-okf-xs/doc/bundles/jishu/ai/products/craft-anything/"
---

# Craft Anything 博文 → OKF 知识包转化（spec）

## 一、任务

将微信公众号博文《刚刚开源，5300 人关注的 AI 复刻项目火了》（作者「熊叔」，2026-11-03）系统性转化为 OKF v0.2 知识包，落地 `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/craft-anything/`。

## 二、敏感度预检（步骤 1）

- 信源为公开微信公众号文章（无登录墙 / 无邀请码 / 无访问控制参数），配合公开 GitHub 仓库与 REST API。
- 判定为**公开内容** → 走标准工作流：规划与事实登记留主仓库 `.trae/specs/`，产出物入子模块 `projects/awesome-okf-xs/doc/bundles/`。

## 三、骨架判定（步骤 2 · 操作可复现性两问）

| 问 | 判定 |
|---|---|
| 问 1：博文 / 官方文档是否给出读者可照做的安装 / 构建流程？ | **是**——安装包（Windows msi + 便携、macOS dmg、Linux AppImage/deb/Flatpak、WASM 查看器）+ Rust 1.97+ 源码构建 + `craft-anything-cli rebuild` |
| 问 2：流程是否具备可复现性（有版本、有命令、有步骤顺序）？ | **是**——版本（Rust 1.97+、v0.3.0）与命令明确、步骤有序；**未在本机实测**（本机无对应工具链与 Claude Code 登录态） |

→ 两问皆「是」，设立 `examples/`。目录骨架：`index + concepts/ + examples/ + references/ + log`（技术教程 / 选型类）。

## 四、归属判定（步骤 3）

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/products/`（📱 AI 产品与终端工具） | ✅ **采用** | 主线实体 Craft Anything 是面向终端任务的 AI 产品 / 工具；该分组已有 36 束同形态先例（octop / orca-ade / wigolo / opencreator / creatorhub 等） |
| `jishu/ai/frameworks/` | ❌ | 本项目不是 Agent / LLM 框架库，而是终端产品 |
| `jishu/ai/practice/` | ❌ | 非工程方法论 / 行业洞察束 |
| 新建分组 | ❌ | 单篇博文禁止新建分组（最小变更原则） |

## 五、信源清单（R 阶段）

| source_id | 类型 | 标识 | 采集时点 |
|---|---|---|---|
| blog | 微信公众号 | 《刚刚开源，5300 人关注的 AI 复刻项目火了》 | 2026-11-04 |
| github-repo | GitHub 官方仓库 | storytold/craft-anything（README） | 2026-11-04 |
| github-api | GitHub REST API | api.github.com/repos/storytold/craft-anything | 2026-11-04 |
| github-releases | GitHub REST API | .../releases + release v0.3.0 assets | 2026-11-04 |
| official-status | 官方仓库根文件 | STATUS.md | 2026-11-04 |
| third-party | 第三方报道 | kitploit.com / opennet.ru / madrobot.blog / gadgetpilipinas.net / eyerys.com | 2026-11-04 |

## 六、核验与勘误摘要

- P0/P1 核验结果见 `facts.md` 与 bundle `references/verification.md`。
- 关键勘误：**① 时间线存疑**（博文称"十月十八号"跑通，早于仓库建仓日 2026-10-31）；**② 工具数口径三源并存**（博文 314 / README 314（298 引擎）/ STATUS.md 300 引擎、320 含 AI+setup 层）；**③ Star 数时效**（博文"四千七百多颗星""5300 人关注"均为成文时点，官方现值 8531，2026-11-04 快照）。
- 无**核心声明**（项目存在性、纯 Rust、净室引擎、检查机制、v0.3.0）核验失败 → bundle `status: stable`，勘误完整登记。

## 七、阶段进度

- [x] R：事实采集（F-001~F-043）+ P0 权威核验
- [x] I：骨架判定 + 三层知识拆分
- [x] E：信源先行生成 bundle（13 个文件：index + concepts/5+index + examples/1+index + references/3 + log）
- [x] V：对抗审查 + 双份 F 编号核对（43=43）+ 三级索引接入 + 计数同步（products 36→37）
  - 注：提交时发现**并发会话**已在其在途改动中把 `bundles 702→705 / jishu 512→515 / ai 279→281` 一并提升（其 `ai/index.md` 的 products 行亦为 37，与本包一致）；为避免夹带我未触碰的未提交目录（`ub-mode-coding-discipline/`、`pagekin/`、`riscv-automotive/`、`super-agent-architecture/`），本包提交**隔离为** `craft-anything/` 13 文件 + `products/index.md`，`bundles/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`iot/index.md`、`practice/index.md` 留待并发会话自行提交（其工作树值已含本包）
- [x] C：原子提交（子模块 → 主仓库 spec → 主仓库子模块指针）——子模块提交 `960d6634`；主仓库 spec 与子模块指针提交见本节末

## 八、V 阶段机械门禁结果（2026-11-04）

| 门禁 | 结果 |
|---|---|
| 链接门（bundle 13 文件） | ✅ 54 个本地引用全部可达，0 断链 |
| 链接门（三级索引 3 文件） | ✅ 全部可达 |
| 双份 F 编号一致性 | ✅ 43 = 43，连续无跳号 |
| UTF-8 roundtrip | ✅ 13 文件全部通过，无 BOM 异常 |
| frontmatter 完整性 | ✅ 12 个文档（bundle/Concept/Example/Reference/category）必填字段齐全 |
| 三级 toctree 完整性 | ✅ 4 个 index 的 toctree 条目全部指向存在文件 |
| 敏感信息零残留 | ✅ 无绝对本地路径 / token / key 残留 |
| 计数一致性 | ✅ 本包 `products/index.md` 37 = 37（目录数与束数相等）；三级计数快照在提交时已被并发会话提升为 bundles 705 / jishu 515 / ai 281，其 products 行亦为 37，与本包一致 |

