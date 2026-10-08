---
title: "旅行规划工作台 travel-planner（Python 3.14+）"
status: "completed"
methodology: "seven-concepts (F→V→I→C)"
spec_mode: "Review"
---

# 旅行规划工作台（travel-planner）- 产品需求文档

> 方法论链路：七概念场景 5（创新突破）F → V → I → C。本 spec 为 F（第一性原理）与 V（五攻击者对抗审查）的产出固化。用户关键决策（2026-09-30 确认）：①功能 = 全功能 MVP + AI 行程生成；②运行时数据落 `playground/travel-planner/data/`；③MVP 不集成天气/地图/POI。

## Overview

- **Summary**：一个本地单用户 Web 应用，把旅游规划从「散落的攻略文档与聊天记录」升级为「多行程管理 + 每日行程编排 + 预算跟踪 + 打包清单 + 行中勾选」的闭环工作台，并可选接入 BYOK LLM（OpenAI 兼容端点）生成行程草稿。
- **Purpose**：降低行前组织摩擦（日期/地点/交通/住宿/预算分散多处难以统筹）与行中查看摩擦（一屏看清今天去哪、花多少、带什么）；AI 生成把「从零排行程」的冷启动成本压缩为「审阅修正草稿」。
- **Target Users**：旅行规划者本人（单用户、本机使用）。

## Goals

- G1：多行程管理（创建/编辑/复制/归档/删除），状态覆盖 规划中/进行中/已完成/已归档。
- G2：每日行程编排：按天分组的活动条目（景点/餐饮/住宿/交通/购物/其他），字段含时间段、标题、地点、费用、备注、完成态；支持条目上移/下移排序。
- G3：预算跟踪：总预算对照条目费用自动汇总（按类型分类、按天分布），超支提示。
- G4：打包清单：每行程独立清单，条目增删改、数量、勾选；复制行程时清单随行。
- G5：数据自主：单行程/全量 JSON 导出、导入校验预览后确认；数据落 playground 私域区，零数据库。
- G6：AI 行程生成（可选在线层）：BYOK OpenAI 兼容端点按「目的地/日期/人数/偏好/预算」生成结构化行程草稿；schema 严格校验；草稿预览可编辑，用户确认导入才落盘；无网络/无密钥/调用失败时核心功能 100% 可用，AI 入口显示降级态。
- G7：界面遵循既定审美——白底 + 淡蓝主色、简约高级、扁平线条图标、毛玻璃弹窗、紧凑布局。

## Non-Goals

- 不集成天气/地图/POI/票价等外部信息源（地点字段可手填名称与 URL 跳转）。
- 不做多用户、账号体系、云同步、公网监听、移动端原生应用。
- 不做数据库与前端构建链（零 DB、零 node_modules；SSR + 原生 CSS/JS）。
- AI 不自动落盘、不修改已确认行程：只产生草稿，导入是显式人工动作（human-in-the-loop）。
- 不内置任何模型厂商默认密钥/默认端点凭证（BYOK：端点、模型、密钥全由用户自配）。
- 不做 AI 对话式多轮规划、AI 修改既有条目、AI 生成打包清单（后续迭代评估）。
- 不做系统级通知（行中提醒仅界面内展示）。

## Background & Context

- **用户现状**：个人旅游攻略以文档形态散落 `playground/`（如 `hangzhou-travel-2026/`）；结构化编排、预算统筹与行中勾选是未被满足的痛点。
- **F 阶段公理体系**（设计的不可再分前提）：
  - A1：行程数据唯一事实源 = 本地 JSON 文件（人类可读、可 diff、可备份），UI 是其投影。
  - A2：单用户单浏览器会话，无并发写（文件锁防双开）。
  - A3：所有写操作原子落盘（同目录临时文件 + `os.replace`），崩溃不丢数据；写前备份滚动保留。
  - A4：核心功能（行程/编排/预算/清单/跟踪/导入导出）零网络依赖；AI 生成是唯一可选在线层，其不可用不得影响核心功能。
  - A5：服务仅监听 127.0.0.1；所有 POST 校验 CSRF token 与 Origin/Referer 同源。
- **F 阶段假设剥离**（被证伪剥离的经验假设）：必须接地图/天气/票务 API；必须数据库；必须前端框架；需要多用户云同步；AI 必须内置于核心链路。
- **V 阶段对抗审查结论**（须在设计中兑现）：

  | 攻击者 | 攻击路径 | 防御设计 |
  |---|---|---|
  | 🔴 安全 | 本地端口被外部页面 CSRF 攻击 | 仅绑 127.0.0.1 + CSRF token + Origin 白名单 |
  | 🔴 安全（AI 层新增） | API 密钥经日志/错误信息/响应泄露 | 密钥仅存 playground 数据目录 config 或环境变量；日志与响应一律不回显密钥（掩码显示） |
  | 🟢 边界 | 日期倒序、超长输入、畸形 JSON 导入 | 服务端 schema 校验 fail-fast，中文指引 |
  | 🟢 边界（AI 层新增） | LLM 输出注入 HTML/脚本（提示注入→XSS） | LLM 输出仅作数据；Jinja2 自动转义；类型/字段白名单校验，未知字段拒绝 |
  | 🟠 完整性 | 数据损坏/误删行程 | 原子写 + 写前备份（rolling）+ JSON 导出 |
  | 🔵 时序 | 双开进程并发写同文件 | 单实例文件锁（含陈旧锁接管） |
  | 🟣 模糊 | 随机 JSON 冒充行程导入、LLM 返回非 JSON/幻觉结构 | 结构校验拒绝并提示；AI 草稿必须经预览确认 |

- **仓库先例**：`apps/dev-tools/zhihu-checkin-hub/`（FastAPI + Jinja2 本地 Web、scikit-build-core 纯 Python 包、仅 127.0.0.1、CSRF、py314 实测可装）——本应用复用其本地安全与工程骨架模式；`apps/inurl-byok-token-hub/` 证明本机存在 OpenAI 兼容本地代理使用习惯（AI 层 base_url 可指向任意 OpenAI 兼容端点，含本机代理）。
- **仓库约束**：`apps/*` 新增 Python 子项目默认 scikit-build-core（PEP 517，纯 Python 不写 cmake 段）；新应用先经 `.temp/` 暂存开发、测试通过后全量迁移 `apps/`；Conventional Commits 中文主体。

## Functional Requirements

- **FR-1（数据目录与配置）**：应用通过 `--data-dir` / 环境变量 `TRAVEL_PLANNER_DATA` / 默认相对路径推算定位数据目录（默认 `playground/travel-planner/data/`）；首启自动创建 `trips/`、`backups/` 子目录与 `config.yaml` 模板；数据目录守卫：不存在则创建、指向文件系统根直接子级 fail-fast；`config.yaml` 含 `llm.base_url/api_key/model/timeout`，环境变量 `TRAVEL_PLANNER_API_KEY` 优先于文件密钥。
- **FR-2（行程管理）**：行程字段：名称（必填）、目的地、开始/结束日期（本地时区纯日期，end ≥ start 校验）、币种（默认 CNY，仅展示后缀）、总预算（可选数字）、状态（planning/ongoing/completed/archived）、备注；列表页按状态分组展示，进行中行程显示「今天」与未完成条目计数；支持复制（含条目与清单，完成态重置、id 重生成）与删除（确认弹窗）。
- **FR-3（每日编排）**：行程详情按天分组（Day 1..N 与对应日期）；条目字段：类型（sight/meal/lodging/transport/shopping/other 六枚举）、day_index（1..N，日期范围变更不产生孤儿条目）、开始/结束时间（可选 HH:MM，end ≥ start）、标题（必填）、地点、费用（可选 ≥0 数字）、备注、完成态、来源（manual/ai）；组内支持上移/下移；勾选即原子落盘；「今天」分组在行程期内置顶高亮。
- **FR-4（预算汇总）**：按类型与按天汇总条目费用，对照总预算显示差额与超支提示；无费用条目不计入；汇总为纯加法（不做币种换算）。
- **FR-5（打包清单）**：每行程独立清单，条目：名称（必填）、数量（默认 1）、勾选态；增删改、勾选即落盘；随行程复制。
- **FR-6（导入导出）**：导出单行程或全量为 JSON 文件（HTTP 下载，不落盘）；导入经上传 → schema 校验 → 预览（将创建的行程数与字段摘要，id 冲突自动生成新 id 并在预览说明）→ 用户确认才写入；畸形结构拒绝并给中文错误。
- **FR-7（AI 行程生成）**：
  - 7a 配置状态：界面常驻 LLM 配置指示（已配置/未配置，密钥掩码不回显）；未配置时生成入口引导查看 README 配置说明。
  - 7b 生成表单：目的地、日期范围（默认取当前行程）、同行人数、偏好（多行文本）、预算档位；调用 OpenAI 兼容 `POST {base_url}/chat/completions`（system prompt 要求严格 JSON，字段与 schema 一致）。
  - 7c 校验：解析 LLM 文本（容忍 markdown 代码围栏），按草稿 schema 白名单校验（天数 1..N、类型枚举、时间 HH:MM、费用数字≥0、标题非空、未知字段拒绝）；失败给中文错误与「重试」入口，不落任何数据。
  - 7d 预览导入：草稿以预览页呈现，条目可剔除/微调后点「导入」写入当前行程（day_index 定位到对应天，条目 source 标记 `ai`）；取消则丢弃。
- **FR-8（本地安全）**：仅绑 127.0.0.1；所有 POST 校验 CSRF token（cookie + 隐藏域比对）与 Origin/Referer 同源；单实例文件锁（占用时中文报错退出，陈旧锁检测 PID 后接管）。
- **FR-9（数据安全）**：全部写操作原子化（同目录临时文件 + `os.replace`）；行程写前备份至 `backups/`（每行程滚动保留最近 N 份，默认 5）；任何写入路径必须位于数据目录之内（越界抛受控异常）。

## Non-Functional Requirements

- **NFR-1（技术栈）**：Python 3.14+（`requires-python = ">=3.14"`，本机 py314 实测）；FastAPI + Jinja2 服务端渲染 + uvicorn；原生 CSS/JS 零构建链；httpx（仅 AI 层）；PyYAML（仅配置）；argparse CLI；包构建按仓库硬性约定使用 **scikit-build-core 纯 Python 包**（`wheel.packages`、`build-dir = "build/{wheel_tag}"`、`minimum-version = "0.9"`，无 cmake 段）；禁止 `__future__` 导入（py314 全默认，含 PEP 649）。
- **NFR-2（文件化存储）**：零数据库；行程 = `data/trips/<id>.json`；配置 = `data/config.yaml`；备份 = `data/backups/`；全部人类可读、可 diff。
- **NFR-3（离线可用）**：断网、无密钥、LLM 端点不可达/超时/返回垃圾时，除 AI 生成外全部功能 100% 可用；AI 入口显示降级态（中文原因 + 指引），无未捕获异常。
- **NFR-4（测试）**：关键模块（存储/校验/预算汇总/LLM 客户端）覆盖率 ≥90%，整体 ≥80%；LLM 客户端与生成流程用 mock HTTP 测试，不依赖真实端点。
- **NFR-5（UI 品质）**：白底 + 淡蓝主色、扁平线条图标（内联 SVG）、毛玻璃弹窗（原生 `<dialog>` + backdrop-filter）、紧凑布局；≥1280px 桌面主场景，窄屏可读不崩坏。
- **NFR-6（性能）**：本地页面 P95 响应 < 300ms（无网络依赖页面）；启动到可交互 < 3s；AI 生成同步等待有加载态提示。
- **NFR-7（仓库卫生）**：运行时数据全部落 `playground/travel-planner/data/`（`.gitignore` 的 `playground/` 规则已覆盖）；应用目录无运行时产物；`git status` 零污染（测试断言）。
- **NFR-8（凭证治理）**：api_key 仅存数据目录 `config.yaml` 或环境变量；不入仓库、不入日志、不在任何 HTTP 响应/模板中回显；UI 仅显示「已配置/未配置」。

## Constraints

- **Technical**：Windows 本机运行；Python py314 环境；LLM 仅经 OpenAI 兼容 HTTP 接口（BYOK，端点/模型/密钥用户自配）。
- **Business**：AI 产物必须用户确认导入（human-in-the-loop 不可绕过）；不预置任何厂商默认端点与密钥。
- **Dependencies**：无运行时外部服务硬依赖（AI 层为可选增强）。
- **区域**：代码属 `apps/travel-planner/`（主仓库直接管理，根级，参照 inurl-byok-token-hub 先例；新增后登记 apps 路由表与 README 索引）；运行时数据属 `playground/travel-planner/data/`（gitignore 私域区）。

## Assumptions

- 单用户、单机、单浏览器；无并发写（文件锁防双开）。
- LLM 端点支持 OpenAI 兼容 `chat/completions`，能按要求输出 JSON（解析层容忍代码围栏与前后杂文）。
- 行程数据量级：单行程 ≤ 数百条目，全量读写性能可接受；不需要增量索引。
- 日期处理用本地时区纯 `date`，不涉及时区换算；币种仅作展示后缀不做换算。
- AI 生成质量受第三方模型制约，草稿导入前的预览编辑是必要兜底。

## Acceptance Criteria

### AC-1：行程 CRUD 与字段校验
- **Type**：`rule`
- **Given**：空数据目录启动的应用
- **When**：创建合法行程；创建结束日期早于开始日期的行程；编辑、复制、归档、删除行程
- **Then**：合法操作成功且 JSON 落盘正确（字段与状态机完整）；日期倒序被服务端拒绝并给中文提示；复制产生新 id、条目与清单随行、完成态重置；删除需确认弹窗
- **Pass Condition**：全部分支测试通过；行程文件可被再次解析（round-trip）
- **Evidence**：pytest `test_storage.py` / `test_web.py`

### AC-2：每日编排与排序
- **Type**：`rule`
- **Given**：一个 3 天、含 6 条目的行程
- **When**：新增/编辑/删除条目；上移/下移；勾选完成；修改行程日期范围（缩短为 2 天）
- **Then**：条目按 day_index 分组正确、组内顺序符合移动结果；勾选原子落盘；日期范围缩短时超界 day_index 的条目被校验拦截或明确迁移提示，不产生静默孤儿
- **Pass Condition**：构造用例断言通过
- **Evidence**：pytest

### AC-3：预算汇总机械正确
- **Type**：`rule`
- **Given**：构造的行程（多类型、多天、含无费用条目、总预算 8000）
- **When**：计算按类型/按天汇总与总差额
- **Then**：汇总与手算一致；无费用条目不计入；超支时界面出现超支提示
- **Pass Condition**：断言通过
- **Evidence**：pytest `test_domain.py`

### AC-4：打包清单
- **Type**：`rule`
- **Given**：某行程
- **When**：添加条目（名称/数量）、勾选、删除、随行程复制
- **Then**：清单状态落盘正确；复制行程清单随行且勾选重置
- **Pass Condition**：断言通过
- **Evidence**：pytest

### AC-5：JSON 导入导出 round-trip
- **Type**：`rule`
- **Given**：导出的行程 JSON
- **When**：原样导入；篡改结构（缺字段/错类型/未知字段）后导入
- **Then**：合法导入经预览确认后数据等价（round-trip 一致）；畸形结构被拒绝且给出中文错误定位，未写入任何文件
- **Pass Condition**：等价性与拒绝分支断言通过
- **Evidence**：pytest

### AC-6：AI 草稿 schema 校验与拒绝
- **Type**：`rule`
- **Given**：mock 的 LLM 端点分别返回——合法 JSON 草稿 / 非 JSON 文本 / JSON 但天数超界 / 类型非枚举 / 含未知字段 / 超时
- **When**：调用生成
- **Then**：合法草稿进入预览；全部非法情形给中文错误与重试入口，不产生任何落盘副作用；超时按配置时限中断并降级提示
- **Pass Condition**：六分支 mock 测试通过
- **Evidence**：pytest `test_llm.py`

### AC-7：AI 草稿须确认才落盘
- **Type**：`rule`
- **Given**：一次成功的 AI 生成（预览页有 5 条草稿，用户剔除 1 条）
- **When**：仅点「取消」；或点「导入」
- **Then**：取消后行程数据零变化；导入后仅新增 4 条 source=ai 的条目、落在正确 day_index、既有条目与清单不受影响
- **Pass Condition**：两分支断言通过
- **Evidence**：pytest `test_web.py`（mock LLM）

### AC-8：离线核心可用
- **Type**：`rule`
- **Given**：断网且未配置密钥
- **When**：完成查看列表、编辑行程、增删条目、勾选、预算、清单、导出全套操作
- **Then**：全部成功且数据落盘正确；AI 入口显示「未配置/不可用」降级态而非错误页
- **Pass Condition**：手工冒烟通过（LLM 置空场景）
- **Evidence**：冒烟记录 + mock 测试

### AC-9：本地服务安全
- **Type**：`rule`
- **Given**：服务运行于 127.0.0.1
- **When**：外部 Origin 头、无 CSRF token、错误 token 发起 POST；尝试二次启动实例
- **Then**：三类 POST 一律拒绝（403）；绑定地址断言非 0.0.0.0；二次启动被文件锁拒绝并给中文提示
- **Pass Condition**：测试覆盖三类拒绝与单实例锁
- **Evidence**：pytest

### AC-10：原子写与备份
- **Type**：`rule`
- **Given**：写行程过程中模拟替换失败（注入异常）
- **When**：检查数据目录
- **Then**：原文件未被破坏（临时文件机制）；写前备份落 `backups/` 且滚动保留 ≤5 份
- **Pass Condition**：注入测试断言通过
- **Evidence**：pytest

### AC-11：仓库卫生
- **Type**：`rule`
- **Given**：应用完成若干行程/条目/清单/导入导出操作
- **When**：在仓库根执行 `git status --porcelain`
- **Then**：除应用代码目录与预期入库文件外无任何未跟踪/修改文件；`playground/travel-planner/data/` 下无文件出现在 git status（`playground/` 已 ignore）
- **Pass Condition**：写入路径断言全部位于数据目录内
- **Evidence**：集成测试断言 + git status 验证

### AC-12：凭证零泄露
- **Type**：`rule`
- **Given**：已配置 api_key 的运行实例
- **When**：审计全部 HTTP 响应、模板渲染输出与日志输出
- **Then**：密钥原文不出现在任何输出（仅「已配置」态或掩码）；配置读取支持环境变量优先
- **Pass Condition**：响应/模板/日志断言无密钥子串
- **Evidence**：pytest + 静态扫描

### AC-13：界面品质
- **Type**：`rubric`
- **Dimension**：视觉与信息设计契合度（白底淡蓝、简约高级、扁平线条图标、毛玻璃弹窗、紧凑布局）
- **Scale**：1-5
- **Anchors**：1 = 通用后台模板感/高对比刺眼；3 = 配色正确但层次普通；5 = 精致本地工具质感，淡蓝主色统领、留白与密度平衡、弹窗毛玻璃自然
- **Pass Threshold**：>= 4
- **Evidence**：列表/行程详情/生成表单/草稿预览四页面截图评审

### AC-14：AI 生成端到端顺滑度
- **Type**：`rubric`
- **Dimension**：生成→校验→预览→导入链路顺滑度（加载态清晰、错误中文明确、预览可编辑、导入准确）
- **Scale**：1-5
- **Anchors**：1 = 链路断裂或静默失败；3 = 主流程可用但需 ≥2 次人工补救；5 = mock 一次通过，仅用户确认导入一步人工
- **Pass Threshold**：>= 3（真实模型质量受第三方制约，以 mock 链路 + 真实端点至少一次冒烟收口；环境不具备则 Review 标 blocked 并以 mock 证据临时收口）
- **Evidence**：mock 测试 + 用户在场真实冒烟记录

## Open Questions

- [ ] LLM 提供方与 `base_url`/`model` 由用户自配（任意 OpenAI 兼容端点，含本机 inurl-byok-token-hub 代理）；不阻塞 MVP。
- [ ] 行中模式系统级提醒——MVP 仅界面内提示，后续版本评估。

> AI生成