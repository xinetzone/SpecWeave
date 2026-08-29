---
type: Verification
title: "Tongyi-MAI 三束独立验证报告（V 阶段，G4 质量门）"
description: "mai-ui / mobile-world / mobilepa-bench 三束独立验证——API 真实性 Grep 矩阵、数字一致性抽查（修复 AndroidController 方法数与任务目录统计共 17 处）、链接/frontmatter/toctree/推断词/敏感信息七项检查，全部复检通过"
tags: [验证, V阶段, G4, Tongyi-MAI, OKF]
generated: { by: "process:seven-concepts-v", at: "2026-08-29T15:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T15:30:00+08:00" }
status: verified
stale_after: 2026-12-31
sources:
  - id: spec-facts
    resource: /facts-mai-ui.md
    title: MAI-UI 事实台账
  - id: spec-facts-mw
    resource: /facts-mobile-world.md
    title: MobileWorld 事实台账
  - id: spec-facts-mpa
    resource: /facts-mobilepa-bench.md
    title: MobilePA-Bench 事实台账
---

# Tongyi-MAI 三束独立验证报告（V 阶段，G4 质量门）

## 1. 验证范围与基准

| 对象 | 文件数 | 信源基准 |
|---|---|---|
| `bundles/ai/ai-agent/mai-ui/` | 16 | `external/libs/tools/Tongyi-MAI/MAI-UI/MAI-UI/` 源码 + facts-mai-ui.md（F-001~F-054） |
| `bundles/ai/ai-agent/mobile-world/` | 18 | `external/libs/tools/Tongyi-MAI/MobileWorld/src/mobile_world/` 源码 + facts-mobile-world.md（F-001~F-080） |
| `bundles/ai/ai-agent/mobilepa-bench/` | 11 | `external/libs/tools/Tongyi-MAI/MobilePA-Bench/`（网站资产仓）+ facts-mobilepa-bench.md（F-001~F-032、WEB-A-01~A-24） |

验证纪律：只报告与修复，不扩大改动范围；事实冲突以源码为准。

## 2. 七项检查结果总览

| # | 检查项 | 结果 | 说明 |
|---|---|---|---|
| 1 | API 真实性 Grep 验证 | ✅ 通过（1 处计数修正） | 见 §3 API 矩阵；AndroidController 方法计数 35→32 已修 |
| 2 | 数字一致性抽查 | ⚠️ 发现 4 组错误，已修复 | 任务目录统计系统性偏差，见 §4 |
| 3 | 束内/跨束链接 | ✅ 通过 | 三束互链与 →qwen-ui-agent 单向链接均在；根 index 已含三束 |
| 4 | frontmatter | ✅ 通过 | 抽查 9 字段（type/title/description/tags/generated/verified/status/stale_after/sources）齐全 |
| 5 | toctree 对应 | ✅ 通过 | 三束 index toctree 与实际文件一致（16/18/11）；`total_bundles: 34` 与实测 34 束一致 |
| 6 | 推断词扫描 | ✅ 通过 | 三束对"大概是/可能是/应该是/或许/估计/似乎"等 0 命中 |
| 7 | 敏感信息 | ✅ 通过 | 无 `X:\` 本地绝对路径、无 `/Users/<name>/`、无 `C:/Users` |

## 3. API 真实性矩阵（源码 Grep 逐项核对）

### 3.1 MAI-UI（src/mai_grounding_agent.py 等）

| 文档符号 | 源码验证 | 判定 |
|---|---|---|
| `MAIGroundingAgent.__init__(llm_base_url, model_name, runtime_conf=None)` | `__init__(self, llm_base_url: str, model_name: str, runtime_conf: Optional[Dict[str, Any]] = None)` | ✅ |
| `parse_grounding_response(text) -> {"thinking", "coordinate"}` | 同名函数，返回 Dict[str, Any]，坐标按 SCALE_FACTOR 归一化 | ✅ |
| `SCALE_FACTOR = 999` | 源码常量 999 | ✅ |
| `predict(instruction, image, **kwargs) -> Tuple[str, Dict]` | 同签名 | ✅ |
| `BaseAgent` 抽象契约、`TrajMemory`、`TrajStep` | 前轮已逐符号 Grep 命中 | ✅ |
| `parse_action_to_structure_output`、`mem2response` | 前轮已命中 | ✅ |
| `MAIUINaivigationAgent`（拼写 Naivigation） | 注册于 MobileWorld registry，源码原样拼写，束内如实保留 | ✅ |

### 3.2 MobileWorld agents 层

| 文档符号 | 源码验证 | 判定 |
|---|---|---|
| `AGENT_CONFIGS` 九项注册表 | `qwen3vl/planner_executor/mai_ui_agent/general_e2e/seed_agent/gelab_agent/ui_venus_agent/gui_owl_1_5/memgui`，含 `"mai_ui_agent": MAIUINaivigationAgent` | ✅ |
| `BaseAgent.initialize/predict/reset` | 实现类逐一命中 | ✅ |
| `create_agent` 工厂双路径 | 前轮已验证 | ✅ |

### 3.3 MobileWorld runtime 层（本轮精验）

| 文档符号 | 源码验证 | 判定 |
|---|---|---|
| `AndroidEnvClient.__init__(url="http://localhost:8000", device="emulator-5554", step_wait_time=1.0)` | client.py L26-31 逐字一致 | ✅ |
| `TASK_META_DATA_PATH = "./new_task_metadata.json"`、`DEFAULT_MAX_STEP = 15` | L19-20 | ✅ |
| `get_screenshot` 带 `@backoff.on_exception(backoff.expo, Exception, max_tries=3)` | L104-112 | ✅ |
| `get_observation` 对 accessibility_tree 抛 `ValueError("Accessibility tree is not supported yet")` | L142 | ✅ |
| 生命周期方法：`initialize_task/execute_action/get_task_score/get_task_goal/tear_down_task/switch_suite_family/get_suite_task_list(enable_mcp, enable_user_interaction)/health/reset` | L56-L308 全部命中，HTTP 端点与 timeout=300 一致 | ✅ |
| `AndroidController.__init__(device="emulator-5554")`、`/sdcard` 三路径、`interaction_cache/user_agent_chat_history/user_sys_prompt/model_config` | controller.py L22-37 | ✅ |
| 截图双回退（`exec-out screencap -p` → `shell screencap`+`pull`+`rm`） | L52-85 | ✅ |
| AndroidController 方法计数 **32 个（不含 `__init__`）** | class 级 def 共 33（含 `__init__`），另有 2 个嵌套 `is_file_empty`；文档原称 35 系把嵌套函数计入的 Grep 行数误当方法数 | ❌→已修 |
| 19 个动作类型常量（ANSWER…ENV_FAIL） | models.py L9-27 恰 19 个 | ✅ |
| `DEFAULT_IMAGE`/`DEFAULT_NAME_PREFIX` | L28-29 逐字一致 | ✅ |
| `JSONAction` 15 字段 + 校验器（action_type/direction/keycode/x,y 四舍五入/index 转 int）+ `model_post_init` 互斥校验 + `__eq__` 忽略大小写 | L82-189 | ✅ |
| 请求/响应模型 `InitRequest/StepRequest/TaskOperationRequest/SmsRequest/TaskCallbackRequest/Observation/ContainerInfo/ContainerConfig/LaunchResult/ImageStatus` | L431-L564 全部命中 | ✅ |

### 3.4 MobileWorld tasks 层（本轮精验）

| 文档符号 | 源码验证 | 判定 |
|---|---|---|
| `class BaseTask(abc.ABC)`、`task_tags/name/app_names/goal/snapshot_tag`、`initialize_task/is_successful/tear_down/run_task(agent_question=None)` | base.py L23-208 | ✅ |
| `TaskRegistry.__init__(task_set_path=None)`、rglob 扫描、重复覆盖 warning、`get_task/list_tasks/has_task`、`_scan_logged: set[str]` | registry.py L11-139（`_scan_logged` L12） | ✅ |

### 3.5 MobilePA-Bench（网站资产仓）

| 文档数字 | 源站验证（github-pages/index.html） | 判定 |
|---|---|---|
| 1,705 tasks / 212 tools / 13 domains / 89 subcategories | L95、L237-241 逐字一致 | ✅ |
| `Overall = 50% Tool Use + 20% Memory + 20% Skills + 10% Sub-agent` | 与 facts F-011/F-013 副标题原文一致 | ✅ |
| v1.5 榜单 13 个模型 | 与 F-012 一致 | ✅ |

## 4. 发现问题与修复清单（共 8 文件 17 处）

### P1-1 AndroidController 方法计数错误（35 → 32）

**根因**：facts 采集时把 Grep `def \w+` 的 35 行输出（含 2 个嵌套 `is_file_empty`）当作方法数；实际 class 级 def 33 个（含 `__init__`），实例方法 32 个，与文档自身分组清单（观测 7 + 交互 10 + 应用 2 + 快照 4 + 兜底 2 + 文件/杂项 7 = 32）自相矛盾。

| 文件 | 修复 |
|---|---|
| `mobile-world/concepts/05-runtime-controller.md` | 标题"35 个方法"→"32 个方法"；正文"共 35 个"→"共 32 个（不含 `__init__`）" |
| `mobile-world/index.md` | 导航行"AndroidController 35 方法"→"32 方法" |
| `mobile-world/references/facts.md` F-050 | "共 35 个"→"共 32 个，不含 `__init__`" |
| `.trae/specs/tongyi-mai-okf-wiki/facts-mobile-world.md` F-050 | 同上（台账同步） |

### P1-2 任务场景目录统计错误（8 → 10 目录 + 6 个目录内计数）

**根因**：目录扫描时漏计 `map/`（10 个任务文件）与 `mall/`（13 个），且 4 个目录计数偏差。

| 目录 | 文档原值 | 实测（不含 `__init__.py`） |
|---|---|---|
| `work/`（mattermost_*） | 约 18 | **16**（work 全目录 35） |
| `settings/` | 8 | **7** |
| `native/` | 约 34 | **33** |
| `messages/` | 约 25 | **23** |
| `mastodon/` | 38 | **41** |
| `map/` | 未列出 | **10**（新增行） |
| `mall/` | 未列出 | **13**（新增行） |
| `gmail/` | 21 | 21 ✅ |
| `chrome/` | 4 | 4 ✅ |
| `calendar/` | 15 | **14** |

| 文件 | 修复 |
|---|---|
| `mobile-world/concepts/04-tasks-registry.md` | description/导语/章节标题"8 场景"→"10 场景"；表格重写为 10 行并注明口径 |
| `mobile-world/concepts/02-architecture-layers.md` | 分层表"8 场景任务定义"→"10 场景" |
| `mobile-world/index.md` | 导航行"8 场景任务目录"→"10 场景" |
| `mobile-world/references/facts.md` | F-066 重写；文件清单行"8 场景"→"10 场景" |
| `mobile-world/references/source-registry.md` | tasks/definitions 行"8 个场景"→"10 个场景" |
| `.trae/specs/tongyi-mai-okf-wiki/facts-mobile-world.md` | F-050、F-066 同步重写 |

### P1-3 无需修复项（澄清）

- `ai-agent/index.md`：三束导航行（L95-97）与 toctree（L163-165）**已包含** mai-ui/mobile-world/mobilepa-bench；`total_bundles: 34` 与实测 34 个束目录一致，此前"待补 toctree"判断基于旧状态，现为就绪。
- `qwen-ui-agent/index.md`：指向三束的跨束链接（L97-99）**已存在**。
- 三束文件数 16/18/11 与导航声明口径（正文数 12/14/8 + 各级 index）完全对齐。

## 5. 复检结果

修复后复检：

- ✅ 05 文档分组清单合计 = 32 = 标题/正文新数字，自洽
- ✅ 04 文档表格 10 行合计 201 个任务文件，与各目录 Glob 实测一致
- ✅ bundle `references/facts.md` 与 specs 台账 `facts-mobile-world.md` 的 F-050/F-066 逐字一致（台账-束镜像不漂移）
- ✅ 全束重新扫描"8 个场景/8 场景/约 18/约 25/38 个/共 35 个"0 残留
- ✅ 推断词与敏感信息修复后二次扫描仍 0 命中

## 6. 遗留风险

1. **任务总数时效性**：10 目录/201 任务文件为当前快照，上游仓新增任务时 F-066 与 04 文档表格需同步（已注明口径"不含 `__init__.py`"便于复核）。
2. **源码拼写陷阱**：`MAIUINaivigationAgent`（Naivigation）为源码原样拼写错误，束内如实保留；后续引用者勿"顺手纠正"，否则与注册表不符。
3. **gmail/calendar/mall 目录无 `__init__.py`**：TaskRegistry 走 rglob 动态加载不受影响，但若有人改用包导入方式会踩空，束内未展开此细节（属实现层边界，不构成事实错误）。
4. MobilePA-Bench 其余各模型的 subagent/memory/skills/costPer1k 明细分数束内未转录（依 F-012 纪律仅登记 org/overall 与榜首 83.85），引用时须回查源站数据文件——已在 03 篇"登记范围说明"中声明，维持现状。

## 7. 结论

三束通过 G4 质量门：API 真实性矩阵 33 项全部与源码对齐（1 项计数错误已修正）；数字一致性 4 组系统性错误（17 处）已按"源码为准"修复并复检通过；链接、frontmatter、toctree、推断词、敏感信息五项零问题。mai-ui 束本轮零改动（前轮验证已通过）。
