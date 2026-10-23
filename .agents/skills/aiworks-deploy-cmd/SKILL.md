---
name: aiworks-deploy-cmd
version: 1.0.0
description: "知乎 AI Works（AI Works / 科学季 / 创作者项目）源码代部署与发布流程。当用户要上传源码部署项目、打包作品发布到知乎 AI Works、处理部署失败（如错误码 8 / 部署包校验失败 / frontend.deploy.json 缺失）、或需要把静态 HTML 作品一键部署上线并走审核发布时，必须使用此技能。也适用于任何『平台要求上传源码 ZIP 自动构建』的静态前端作品部署场景（参照官方 deploy-helper 流程生成合规部署包）。不要手工把 index.html 塞进 ZIP 就上传——本 Skill 封装了官方工具链（探测→描述符→校验→settle→归档→上传→构建→审核→发布→复核）与全部已知陷阱。"
argument-hint: "<作品目录或 index.html 路径> [部署目标平台]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/aiworks-deploy-cmd/**"
  - "work/zhihu-science-workshop-2026/deploy/**"
title: "AI Works 源码代部署与发布 Skill"
x-toml-ref: "../../.meta/toml/.agents/skills/aiworks-deploy-cmd/SKILL.toml"
---

# AI Works 源码代部署与发布 Skill

> 萃取自 sc-20261023-zhihu-ai-science-workshop 实战（知乎 AI Works「记忆实验室」发布全链路：错误码 8 修复 → 官方 deploy-helper 合规打包 → 上传构建 → 审核声明 → 发布 → 审核通过）。本 Skill 将「平台源码部署契约」经验固化为可重复执行的五步流程。

## 1. Skill ID

`aiworks-deploy-cmd`

## 2. 功能描述

提供**官方工具链驱动的合规部署**单一方案（配套决策树判断是否适用），核心操作：

1. 下载并解压平台官方 deploy-helper Skill 到本地只读引用目录
2. 探测项目类型（inspect_node_project.py）→ 生成部署描述符（write_deploy_descriptors.py）
3. 校验部署输出（validate_deploy_output.py，先 `--plan-only` 后全量）
4. 生成合规 ZIP 归档（create_project_archive.py）+ settle agent 元数据
5. 浏览器上传 → 观察平台构建 → 填审核声明 → 发布 → 详情页复核

> **为什么必须走官方工具链？** 平台「一键部署」隐藏包格式契约：ZIP 内只有前端产物会触发 `部署包校验失败，错误码:8`（`_tmp` 必须包含 frontend.deploy.json 或 backend.deploy.json）。官方 helper 生成的描述符同时声明构建命令（BuildCmd）与部署命令（DeployCmd），跳过它会浪费轮次且无法定位问题。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：

- "上传源码"、"一键部署"、"代部署"、"发布项目到知乎"、"部署失败"
- "错误码 8"、"部署包校验失败"、"frontend.deploy.json"、"backend.deploy.json"
- "把作品发布到 AI Works"、"科学季投稿"、"知乎 AI Works"、"deploy-helper"
- "打包部署"、"静态作品上线"、"部署成功/可预览"、"审核声明"
- 任何涉及「平台要求上传源码 ZIP 自动构建」的静态前端作品部署请求

> **关于触发**：即使没有说"用 skill"，只要用户要部署静态作品到源码上传型平台，就应该使用本技能——手工打包必然踩错误码 8 或平台契约差异，本 Skill 已封装官方工具链、安全校验与错误处理。

## 4. 方案选择决策树

```
收到「部署作品」请求？
├─ 平台要求「上传源码 ZIP 自动构建」？ → 走官方 deploy-helper 流程（第 6-10 节）
│   ├─ 纯静态前端（index.html + 内联 CSS/JS）？ → frontend-static 分支（inspect 探测确认）
│   └─ 含后端/服务端逻辑？ → 需 backend.deploy.json（官方 helper 对应分支）
├─ 平台提供可视化上传（直接传文件/表单）？ → 不走本流程，直接表单上传
├─ 已有平台官方 CLI/SDK？ → 优先官方 CLI（本 Skill 的浏览器上传部分可跳过）
└─ 首次使用未下载 helper？ → 先执行第 5 节下载步骤
```

> **为什么先探测再生成？** inspect_node_project.py 会确认项目类型（frontend-static/backend）并列出阻断项（外部 CDN 依赖、非内联资源、事件桥缺失），这决定了描述符里写什么——探测错误会直接导致后续构建失败。

## 5. 依赖与前置准备

- **必读参考**（按需）：官方 deploy-helper 的 SKILL.md 与 `references/schemas/`（部署描述符 schema、平台契约文档）。平台契约可能更新，始终以解压后的官方文件为准。
- **运行环境**：Python 3.10+；浏览器（用于上传/审核/发布，配合 browser-use 或用户接管）。
- **前置状态**：用户已登录目标平台账号（发布操作需要登录态；登录/验证码场景按浏览器自动化规范请求用户接管）。
- **操作限制**：每账号应用数有限（知乎 AI Works 每用户最多 10 个应用）；发布后生成预览/正式链接，审核通过前仅预览链接可访问。

> **为什么限制要前置说明？** 应用数上限与审核时效直接影响发布策略（先本地验收再上传、审核通过前不要对外宣传正式链接），避免用户误把预览链接当正式链接传播。

## 6. 步骤 1：获取官方 deploy-helper

```powershell
# 从平台页面提供的 zhstatic 链接下载（以知乎 AI Works 为例，链接随页面/版本变化，以页面实际提供为准）
# 下载后解压到只读引用目录，禁止修改官方脚本
New-Item -ItemType Directory -Force -Path "<workdir>/_deploy_helper/unpacked"
# 解压 zip 到该目录
# 读取解压后的 SKILL.md 与 references/schemas/frontend.deploy.schema.json
```

- 确认 helper 版本与页面提供版本一致。
- 读取其 `SKILL.md` 确认调用顺序与脚本名（官方版本可能更新脚本名）。

> **为什么放只读引用目录？** helper 是平台官方工具，vendor 边界内只读引用；后续生成的合规包在 deploy/ 目录，两者分离避免污染。

## 7. 步骤 2-3：探测 + 生成描述符

```powershell
# 2. 探测项目类型（在作品目录执行）
python <helper>/scripts/inspect_node_project.py <workdir>/deploy

# 3. 生成部署描述符（生成 _tmp/frontend.deploy.json + 根 package.json + 事件桥材料）
python <helper>/scripts/write_deploy_descriptors.py
```

- 探测输出应显示 `frontend-static`、无阻断项、事件桥可注入。
- 描述符关键字段（静态分支）：SchemaVersion 1.1.0、Framework other、NodeVersion 20、BuildCmd "npm run build:track"、InstallCmd ""、DeployCmd "tcb hosting deploy ./"、BuildPath ./。

> **为什么描述符要声明构建命令？** 平台在服务端执行 BuildCmd 注入事件桥（tracking.aiworks.site），并依据 DeployCmd 决定产物发布路径——这两项写错或缺失 = 构建失败或产物不可访问。

## 8. 步骤 4：校验部署输出

```powershell
# 先 plan-only 只读校验（不产生副作用）
python <helper>/scripts/validate_deploy_output.py --plan-only
# 全量校验（生成最终校验结论）
python <helper>/scripts/validate_deploy_output.py
```

- 两个校验都必须 passed（0 错误）才继续。
- 校验失败时按输出逐项修复（常见：index.html 引用了外部 URL、缺少 package.json、_tmp 文件不完整）。

> **为什么先 --plan-only？** 这是本 Skill 的 dry-run 安全防线：plan-only 只读展示校验结果，不生成/改写任何产物；确认无误再全量执行，防止校验过程本身污染部署包。

## 9. 步骤 5：settle + 归档

```powershell
# settle agent 元数据（记录部署来源，如 ProductCode=doubao/ProductName=豆包/Platform=desktop/Source=agent-self-report）
python <helper>/scripts/settle_agent.py
# 生成合规 ZIP 归档
python <helper>/scripts/create_project_archive.py
```

- 校验 ZIP：文件名、大小、文件数、根前缀（如 deploy/）正确；ZIP 内含 index.html 且事件桥占位符（`__AIWORKS_EVENT_TRACKING_TICKET__`）存在。

> **为什么 settle 与 archive 分离？** settle 记录"由谁/以什么身份部署"的审计元数据（平台可能据此区分人类与 agent 部署）；archive 才生成最终上传物。合并会导致审计信息丢失或打包内容错误。

## 10. 步骤 6-9：上传 → 构建 → 审核 → 发布

1. **上传**：浏览器进入创建/编辑页 step=2（上传源码），选择合规 ZIP 上传。
2. **观察构建**：等待平台自动构建；出现「部署成功，项目已完成部署，可预览确认」才算成功。
3. **填审核声明**：逐项如实选择（如「是否接入账号登录/是否含大模型内容」按作品实际选「否/是」）；用 label click 后验证 checked 状态。
4. **发布**：用户确认后点发布；进入详情页。
5. **复核**：详情页状态 = 科学季/可运行/审核通过；「可在当前页面直接运行项目应用」。

> **为什么审核声明要如实填写并验证？** 平台审核依据声明内容；勾选状态验证（checked=true/false）防止自动化点击未生效导致声明为空提交被拒或违规。发布是外部不可逆动作，执行前必须获得用户明确确认（用户在流程中已要求"不用预览，直接发布"时除外）。

## 11. 安全检查清单（逐项确认）

- [ ] 官方 helper 已下载且版本与页面一致，未修改官方脚本
- [ ] 探测确认项目类型（frontend-static）且无阻断项
- [ ] `validate_deploy_output.py --plan-only` 通过后才全量校验
- [ ] 全量校验 passed（0 错误）
- [ ] ZIP 内容核验：含 frontend.deploy.json + index.html + 事件桥占位符
- [ ] 幂等性检查：上传/发布前确认目标应用未重复存在（重复上传会在草稿/应用列表产生重复项；平台页面异常时尤其可能生成重复草稿，见 Gotchas 13.1）
- [ ] 上传前已向用户确认目标作品与平台账号
- [ ] 审核声明逐项如实选择并验证 checked 状态
- [ ] 发布前获得用户明确确认（或用户已预先授权"直接发布"）
- [ ] 发布后详情页复核（可运行/审核状态）
- [ ] 未向额外账号、仓库、云盘写入内容

## 12. 常见错误处理

| 错误 | 场景 | 处理方式 |
|------|------|---------|
| 错误码 8 | ZIP 缺 frontend.deploy.json/backend.deploy.json | 走官方 helper 生成描述符，禁止手工补 JSON |
| 构建失败 | 描述符 BuildPath/BuildCmd 错误 | 检查相对路径与 schema 字段，重新 write_deploy_descriptors |
| 上传无反应 | 创建页按钮失效（React 组件 bug） | 见 Gotchas 12.2：刷新恢复/换草稿编辑页入口 |
| 说明不持久 | 富文本字段写入失败 | 见 Gotchas 12.3：真实键盘输入 + 刷新验证 |
| 审核被拒 | 声明不符/内容违规 | 按平台审核意见逐项整改后重新提交 |

## 13. Gotchas（陷阱与反直觉行为）

### 13.1 平台表单/页面 React bug

- **按钮点不动不等于表单没填对**：知乎创建页「下一步」在写操作后失效（console：`Uncaught Error: Got unexpected null or undefined`，React-dom@17 production 堆栈），刷新恢复、填表复发。排查顺序：console 查错 → 字段逐项排除 → 刷新验证 → 找替代入口（草稿编辑页字段自动恢复）。
- **创建页刷新不恢复草稿**：已填字段刷新即丢；草稿编辑页（`project/edit?projectId=xxx&source=draft`）刷新后字段自动载入——优先用草稿编辑页做填表。
- **写操作可能产生重复草稿**：异常页面写操作后，草稿/应用列表可能出现多个同名条目（实战曾出现 3 个同名草稿）。发布前清理多余草稿，避免同名应用堆积占应用数配额。

### 13.2 富文本编辑器（Draft.js 类）

- **execCommand('insertText') 不触发状态树更新**：DOM 有字但编辑器 state 为空 → 占位层不隐藏（叠影）+ 保存不持久。必须真实键盘输入（click 聚焦内容区再 type）。
- **合成 beforeinput 事件被 isTrusted 拒绝**：自动化注入会被丢弃；验证成功标准 = 占位符卸载 + 刷新后内容仍在。

### 13.3 部署契约

- **ZIP 里只有 index.html 不够**：平台要求 `_tmp/frontend.deploy.json`（或 backend.deploy.json），且描述符声明 BuildCmd/DeployCmd。
- **本地验证 ≠ 平台构建**：平台在服务端跑构建注入事件桥；本地能开 ≠ 平台构建成功，以平台「部署成功」文案为准。
- **审核通过前只有预览链接**：正式链接在审核通过后生成，不要提前对外宣传。

## 14. 关键参考速查表

| 目标 | 入口/脚本 | 注意事项 |
|------|----------|---------|
| 官方 helper | 平台页面 zhstatic 下载链接 | 版本随页面变化，以实际提供为准 |
| 项目类型探测 | scripts/inspect_node_project.py | frontend-static 分支 |
| 描述符生成 | scripts/write_deploy_descriptors.py | 生成 _tmp/frontend.deploy.json + package.json |
| 校验 | scripts/validate_deploy_output.py | 先 --plan-only |
| settle | scripts/settle_agent.py | ProductCode=产品代号 |
| 归档 | scripts/create_project_archive.py | 核验 ZIP 根前缀与事件桥 |
| 线上状态 | 平台详情页 | 可运行 + 审核通过 |

## 15. 长期方案与演进方向

- 官方 helper 可能演进（schema 版本、新字段），执行前重读解压后的官方 SKILL.md。
- 若平台开放官方部署 CLI/API，浏览器上传部分可迁移到 CLI 全自动。
- 后端/混合项目分支（backend.deploy.json）待案例验证后补充。

## 16. Changelog

- **v1.0.0** (2026-10-23): 初始版本。萃取自知乎 AI Works「记忆实验室」发布实战（错误码 8 → 官方 helper 五步 → 审核发布通过）；含 React 表单 bug 与 Draft.js 富文本两大 Gotchas 族；L2 案例支撑（本次实战 + 官方教程流程）。
