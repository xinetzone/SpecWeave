---
type: Report
title: "EdgeOne Pages 静态站点部署里程碑复盘（designer-portfolio）"
date: 2026-09-29
archived: 2026-09-29
scenario: milestone
methodology: seven-concepts R→I→E→C
session: sc-20260929-edgeone-pages-deploy
scope: task
status: archived
topic: edgeone-pages-deploy
---

# EdgeOne Pages 静态站点部署里程碑复盘（designer-portfolio）

## 执行摘要

本里程碑完成「将 SpecWeave 单体仓库中的前端项目部署到 EdgeOne Pages」的全流程，交付三样产物：
1. 站点 `designer-portfolio` 成功部署上线（Production 环境，Deployment ID `dpebpaq47jjs`）；
2. 沉淀「EdgeOne Pages 静态站点部署模式」可复用模式 1 个；
3. 产出 OKF Wiki 教程束 `docs/knowledge/tech/edgeone-pages-deploy/`。

过程中遇到一次阻塞性故障：EdgeOne CLI 在 Windows 受管 Node 环境安装失败，表层报错 `Cannot find module 'open'` 掩盖了真实根因（esbuild postinstall 失败导致 npm 安装未终态）。通过 `--ignore-scripts` 绕过并固化排错结论到 Skill，故障从发现到解决约 3 分钟。

| 指标 | 值 |
|---|---|
| 部署站点 | `apps/samples/designer-portfolio`（纯静态，无 package.json） |
| Project ID | `makers-kibjgortw1bl` |
| Deployment ID | `dpebpaq47jjs` |
| 构建耗时 | 81ms（StaticAssetsBuilder 纯拷贝） |
| 部署总耗时 | 36s（含上传与 2 次状态轮询） |
| 客观事实 | 20 条（F1–F20） |
| 核心洞察 | 3 条（四元组完整） |
| 可复用模式 | 1 个（反模式 6 条） |
| 质量门 | G1✅ G2✅ G3✅ G4✅ |
| 故障修复 | 1 处（CLI 安装），已固化入 Skill |

---

## 1. 客观事实清单（R阶段）

> G1 质量门：以下事实均为工具输出直接记录，不含「因为/导致/所以」等推断性表述。推断统一移至第 3 节洞察。

| # | 事实 |
|---|---|
| F1 | 首次执行 `edgeone -v` 返回 `command not found: edgeone` |
| F2 | `npm install -g edgeone@latest` 执行 1m38s 后失败，npm 报错含 `spawnargs: [...esbuild\bin\esbuild, --version]`，`status: null`、`pid: 0` |
| F3 | 安装失败后运行 `edgeone -v`，Node 抛出 `Cannot find module 'open'`，`requireStack` 指向 `edgeone-dist/cli.js` |
| F4 | `edgeone/node_modules/@esbuild` 与 `edgeone/node_modules/esbuild/node_modules/@esbuild` 两个路径均不存在 |
| F5 | 改用 `npm install -g edgeone@latest --ignore-scripts`，42s 完成，输出 `added 6 packages, and changed 162 packages in 38s` |
| F6 | 修复后 `edgeone -v` 正常输出 ASCII 版本横幅；`edgeone whoami` 返回 `You are not authenticated` |
| F7 | 仓库根目录不存在 `package.json` |
| F8 | `find -maxdepth 4 -name package.json` 命中 11 个；同深度前端配置文件（vite/next/vue/angular/index.html）命中 11 个（均经 `wc -l` 独立计数） |
| F9 | 用户对项目消歧选择 `apps/samples/designer-portfolio`；站点选择 `China（国内站）` |
| F10 | `designer-portfolio` 目录含 6 个顶层条目：`README.md`、`assets`、`index.html`、`projects`、`script.js`、`style.css`；无 `package.json` |
| F11 | `assets` 目录 2.1M；`projects` 目录 32K，含 4 个文件（`project-1.html`–`project-4.html`） |
| F12 | 部署前该目录不存在 `edgeone.json`（首次部署，未关联项目） |
| F13 | `edgeone login --site china` 输出跳转 URL（`state=2d5c9b9a-e89b-4422-848a-1cd520c8baa4`），11s 后输出 `Login successfully`，并输出 `.gitignore updated` |
| F14 | 部署命令为 `edgeone pages deploy -n designer-portfolio`，整体耗时 36s |
| F15 | CLI 输出 `⚠ "edgeone pages" is deprecated. Use "edgeone makers" instead.` |
| F16 | 构建阶段识别为 `StaticAssetsBuilder`，拷贝 `index.html`、`script.js`、`style.css`、`README.md`、`assets/`、`projects/`，`build time 81ms` |
| F17 | 项目创建输出 `Creating new project with name: designer-portfolio in global area`；部署输出 `(Production environment, global area)` |
| F18 | Project ID 为 `makers-kibjgortw1bl`；Deployment ID 为 `dpebpaq47jjs`；上传进度显示 `100%` |
| F19 | Deploy URL：`https://designer-portfolio-w1ras6ms.edgeone.cool?eo_token=629627c63dd4e9bc9254e0518735a4b4&eo_time=1790663452` |
| F20 | Console URL：`https://console.cloud.tencent.com/edgeone/pages/project/makers-kibjgortw1bl/deployment/dpebpaq47jjs` |
| F21 | 技能文件 `~/.workbuddy/skills/edgeone-pages-deploy/SKILL.md` 已更新：Install CLI 段增补 `--ignore-scripts` 排错说明，Error Handling 表新增 2 行 |

### 数据验证三查法执行记录

- **查关键数据**：11 / 11 / 4 / 6 四个数量均经 `wc -l` 独立计数确认（命令见 V 阶段记录），非目测。
- **查链接**：本报告无 `file:///` 链接，跳过断链检查。
- **查章节结构**：Grep `^#` 确认「执行摘要 / 1. 客观事实清单 / 2. 过程分析 / 3. 核心洞察 / 4. 改进建议 / 5. 可复用模式」六段齐全。

---

## 2. 过程分析

### 2.1 时间线

| 顺序 | 动作 | 结果 |
|---|---|---|
| 1 | 环境检查（CLI 版本 / 登录态 / 项目关联） | CLI 未安装，未登录，未关联 |
| 2 | 定位前端项目 → 发现 11+11 个候选 | 触发消歧提问 |
| 3 | 用户确认项目与站点 | `designer-portfolio` + China |
| 4 | 安装 CLI（常规方式） | 失败（esbuild postinstall） |
| 5 | 诊断根因（缺 `open`、缺 `@esbuild` 平台包） | 定位到 postinstall 中断 |
| 6 | 改用 `--ignore-scripts` 重装 | 成功（42s） |
| 7 | 浏览器登录 China 站 | 成功（11s） |
| 8 | 部署 | 成功（36s，构建 81ms） |
| 9 | 排错结论固化入 Skill | 完成 |

### 2.2 关键决策节点

- **决策 A（安装方式）**：不重试常规安装，改用 `--ignore-scripts`。依据：本项目为纯静态站点，构建阶段是 `StaticAssetsBuilder` 纯文件拷贝（F16），不触发 esbuild 变换。
- **决策 B（项目定位）**：不猜测项目，改为列举候选并让用户确认。依据：仓库根无 `package.json`（F7），候选多达 11 个（F8）。
- **决策 C（登录方式）**：桌面环境采用浏览器登录而非 Token。依据：用户在本地 Win32 桌面 IDE，浏览器可自动弹出。

### 2.3 成功因素与瓶颈

- **成功因素**：先做环境检查再动手（一次 `edgeone -v` 就暴露了未安装）；把排错结论写回 Skill，使经验可复用。
- **瓶颈**：安装故障的表层报错（`Cannot find module 'open'`）与真实根因（esbuild postinstall）不在同一层，若不检查 `@esbuild` 目录是否存在，容易误判为「包损坏」而反复重装。

---

## 3. 核心洞察（I阶段）

> G2 质量门：每条洞察含「现象 + 根因 + 影响 + 建议」四元组，根因均标注对应事实编号。

### 洞察 1：安装失败的表层报错与真实根因不在同一层，需下钻一层才能定位

- **现象**：CLI 安装后运行报 `Cannot find module 'open'`（F3）。
- **根因**：esbuild 的 postinstall 在 Windows 受管 Node 环境 spawn 失败（F2），npm 判定整包安装失败并中止，导致依赖未装全（`open` 缺失，F3）；平台二进制目录 `@esbuild` 不存在（F4）。表层报错指向 `open`，真实断点在 esbuild postinstall。
- **影响**：若按表层报错处理，会误判为「edgeone 包损坏」而反复重装，或绕道改用 Token 登录规避安装，浪费时间且问题仍在；该故障具有环境复发性（同环境下次安装仍会命中）。
- **建议**：静态站点（无构建步骤）部署直接用 `npm install -g edgeone@latest --ignore-scripts`（F5），并将该排错写入 Skill（F21）；对需构建的项目，改为单独修复 esbuild 平台二进制而非整包重装。

### 洞察 2：单体仓库中「这个前端项目」是指代歧义源，部署前必须显式消歧

- **现象**：用户指令为「把这个前端项目部署到 EdgeOne Pages」，而仓库根无 `package.json`（F7），`find` 命中 11 个 package.json 与 11 个前端配置文件（F8）。
- **根因**：monorepo 内含多个前端候选，指令中的「这个」缺少唯一定位信息；且候选横跨 `apps/`、`playground/`、`vendor/`（其中 `vendor/` 为 git submodule，禁止本地修改）。
- **影响**：凭直觉猜测会部署错误产物——既浪费一次部署，又会在 EdgeOne 账号下留下错误项目记录，且可能误将 submodule 内容上传。
- **建议**：部署前先用候选列表消歧（本次经一次交互确认 `designer-portfolio` + China，F9）；后续可在 Skill 的部署流程前增加「monorepo 项目消歧」检查项。

### 洞察 3：登录站点与项目实际落区、预览链接时效三者不一致，需以控制台为准

- **现象**：以 `--site china` 登录（F13），但创建项目与部署输出均显示 `global area`（F17）；Deploy URL 携带 `eo_token` 与 `eo_time` 参数（F19）。
- **根因**：CLI 输出的落区字段与登录站点参数解耦，不由 `--site` 唯一决定；预览链接自带鉴权参数，`eo_time` 表明其带时间属性。
- **影响**：容易误认为已部署到国内站；分享链接后被访问者可能因鉴权参数过期/域名备案策略出现 401。
- **建议**：以控制台 URL（F20）核对项目真实区域与加速区域；长期稳定对外访问应绑定已备案自定义域名，不依赖预览链接。

---

## 4. 改进建议（行动项）

| # | 行动项 | 优先级 | 责任人 | 验收标准 |
|---|---|---|---|---|
| A1 | 静态站点部署统一使用 `--ignore-scripts` 安装 CLI | P0 | developer | 同环境重装 CLI 一次成功，`edgeone -v` 正常 |
| A2 | Skill 增加「monorepo 项目消歧」前置检查项 | P1 | orchestrator | `edgeone-pages-deploy/SKILL.md` 含该检查项 |
| A3 | 后续部署改用 `edgeone makers` 命令（规避弃用警告） | P2 | developer | 部署输出不再出现 deprecated 警告 |
| A4 | 核对 `designer-portfolio` 控制台落区；如需国内加速则绑定已备案域名 | P1 | developer | 控制台区域字段与预期一致 |
| A5 | 将 OKF 教程束纳入 `docs/knowledge/tech/` 索引 | P1 | orchestrator | 束可从知识索引导航到达 |

---

## 5. 可复用模式（E阶段）

> G3 质量门：模式含触发场景 + 核心步骤 + 反模式（≥5）+ 迁移验证。共列 6 条反模式。

### 模式：EdgeOne Pages 静态站点部署模式

- **成熟度**：L2（已在本仓库 1 次实战验证，跨 1 个项目）
- **触发场景**：需将纯静态前端站点（无 package.json / 无构建步骤，或构建产物为静态文件）部署到 EdgeOne Pages，运行环境为 Windows 受管 Node。
- **核心步骤**：
  1. 环境预检：`edgeone -v` / `edgeone whoami` / `cat edgeone.json` / `cat .edgeone/.token`
  2. 项目消歧：仓库存在多个前端候选时，先列举并确认目标目录
  3. 安装 CLI：`npm install -g edgeone@latest --ignore-scripts`（静态站点场景）
  4. 登录：`edgeone login --site china`（桌面环境浏览器登录）
  5. 部署：`edgeone pages deploy -n <project-name>`（在项目目录内执行）
  6. 解析产物：完整保留 `EDGEONE_DEPLOY_URL` 的 query 参数，勿截断
- **反模式**：
  1. 忽略 CLI 版本与登录态直接 deploy → 报未安装/未鉴权后返工
  2. 安装失败时按表层报错 `Cannot find module 'open'` 反复重装 → 未触及 esbuild postinstall 根因
  3. 在 monorepo 中凭直觉猜目标项目 → 部署错误产物、污染账号项目列表
  4. 截断 Deploy URL 的 query 参数 → 分享后页面无法访问
  5. 未确认站点/落区就假定「已部署到国内站」 → 区域与预期不符
  6. 把预览链接当作长期对外地址 → 鉴权参数过期后 401
- **迁移验证**：本模式在 `apps/samples/designer-portfolio`（F10–F20）完整跑通；其核心步骤与 EdgeOne Pages Deploy Skill 的「检查 → 安装 → 登录 → 部署 → 解析」五段一致，可迁移至同仓库其他静态站点（如 `apps/samples/short-video-site`）。对含构建步骤的项目（有 package.json），步骤 3 需改为修复 esbuild 平台二进制后正常安装，其余步骤不变。

---

## 6. 质量门记录

| 门 | 检查项 | 结果 |
|---|---|---|
| G1 | 事实清单无因果推断词，每条指向工具输出 | ✅ 21 条事实（F1–F21） |
| G2 | 洞察四元组完整（现象/根因/影响/建议） | ✅ 3 条 |
| G3 | 模式含触发场景+核心步骤+反模式+迁移验证 | ✅ 反模式 6 条（≥5） |
| G4 | 数量陈述经独立计数；章节结构完整 | ✅ 11/11/4/6 经 `wc -l` 核对 |

---

## 关联资源

- 部署技能：`~/.workbuddy/skills/edgeone-pages-deploy/SKILL.md`（已含本次排错结论）
- OKF 教程束：`docs/knowledge/tech/edgeone-pages-deploy/`
- 部署站点：`https://designer-portfolio-w1ras6ms.edgeone.cool`
- 控制台：`https://console.cloud.tencent.com/edgeone/pages/project/makers-kibjgortw1bl/deployment/dpebpaq47jjs`
