# 旅行规划工作台（travel-planner）- 实施计划

> 任务为依赖有序的垂直切片；每个 Task 至少含一条 TR。开发根：`.temp/travel-planner/`（暂存开发，测试通过后全量迁移）；最终代码根：`apps/travel-planner/`；运行时数据根：`playground/travel-planner/data/`。

## Task 1: 应用骨架、配置与数据目录守卫
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1：test_config.py 13 用例全过（显式/env/仓库根推算/根级守卫/幂等初始化/锁冲突）。
  - TR-1.2：`python -m build --wheel` 产出 `travel_planner-0.1.0-py3-none-any.whl`；test_cli.py 7 用例验证 serve/check 帮助、check 报告、非回环拒绝、锁冲突拒绝与释放。
  - TR-1.3：环境变量密钥优先、锁双分支见 test_config.py / test_cli.py。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 按仓库约定建 scikit-build-core 纯 Python 包：`pyproject.toml`（`requires = ["scikit-build-core>=0.9"]`、`build-backend = "scikit_build_core.build"`、`[tool.scikit-build]` 的 `wheel.packages = ["src/travel_planner"]`、`build-dir = "build/{wheel_tag}"`、`minimum-version = "0.9"`，无 cmake 段）；`requires-python = ">=3.14"`；包目录 `src/travel_planner/`（`__init__.py`/`__main__.py`）、`tests/`、`README.md`。
  - `config.py`：dataclass 配置（data_dir、host `127.0.0.1`、port、备份保留份数 5）；优先级 CLI `--data-dir` > 环境变量 `TRAVEL_PLANNER_DATA` > 默认相对路径推算 `playground/travel-planner/data/`；`llm` 配置段（base_url/api_key/model/timeout），环境变量 `TRAVEL_PLANNER_API_KEY` 优先于 config.yaml 文件密钥。
  - 首启初始化：自动创建 `trips/`、`backups/` 与 `config.yaml` 模板；数据目录守卫（不存在则创建、文件系统根直接子级 fail-fast 中文指引）。
  - `cli.py`（argparse）：`serve`（启动 Web）、`check`（校验数据目录与 LLM 配置状态并打印中文报告）子命令。
  - 单实例文件锁（`data/travel-planner.lock`，写入 PID；占用且进程存活则拒绝，陈旧锁接管）。
- **Acceptance Criteria Addressed**: AC-9（单实例部分）、AC-12（配置优先级部分）
- **Test Requirements**:
  - `rule` TR-1.1: 数据目录四种输入（不存在→自动创建、根直接子级→fail-fast、合法、含既有 config）行为正确；pytest 全通过。
  - `rule` TR-1.2: `python -m build`（或 pip install）在 py314 环境成功产出 wheel；`travel-planner --help` 可见 serve/check 两子命令。
  - `rule` TR-1.3: 环境变量 `TRAVEL_PLANNER_API_KEY` 覆盖文件密钥；锁文件占用/陈旧两分支行为正确。

## Task 2: 行程数据模型与存储层
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1：test_storage.py + test_models.py 全过：CRUD round-trip、日期倒序拒绝、未知字段拒绝、复制重置、models.py 覆盖率 96%。
  - TR-2.2：注入 os.replace 异常后原文件字节不变、无临时残留；同秒多次保存备份滚动保留 5 份（微秒时间戳）。
  - TR-2.3：篡改 JSON（非 JSON/缺字段/错类型/未知字段）逐分支拒绝且含字段定位；路径越界抛受控异常；损坏文件列表页跳过并记录。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `models.py`：dataclass 模型 Trip/Item/PackingItem 及字段校验（名称必填、日期 end≥start、day_index 1..N、类型六枚举、时间 HH:MM 且 end≥start、费用 ≥0、来源 manual/ai、状态四枚举）。
  - `storage.py`：行程 JSON CRUD（`trips/<id>.json`）、原子写（同目录临时文件 + `os.replace`）、写前备份（`backups/<id>-<ts>.json` 滚动保留 5 份）、id 生成、复制（完成态重置 + 新 id）、全部写入路径守卫（越界抛受控异常）。
  - schema 校验器（供存储与导入复用）：未知字段拒绝、类型不符拒绝、错误信息含字段路径的中文提示。
- **Acceptance Criteria Addressed**: AC-1、AC-2（数据层部分）、AC-5（校验部分）、AC-10、AC-11（路径断言）
- **Test Requirements**:
  - `rule` TR-2.1: 行程 CRUD round-trip（字段与状态完整）；日期倒序拒绝；复制后 id 新、完成态重置、清单随行。
  - `rule` TR-2.2: 注入 os.replace 异常后原文件字节不变；备份按 5 份滚动；临时文件不留残留。
  - `rule` TR-2.3: 篡改 JSON（缺字段/错类型/未知字段）导入校验逐分支拒绝且错误含字段定位；路径越界（`..` 逃逸）抛受控异常。

## Task 3: 领域聚合（预算汇总/天数视图/进行中状态）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1：test_domain.py 手算对拍全过（1245/8000 汇总、超支判定、2026-10-01=周四、今天映射含期外分支）；domain.py 覆盖率 100%。
  - TR-3.2：未完成计数 5/6、清单进度 (1,2)、无日期降级归 Day 1 断言通过。
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `domain.py`：按类型/按天费用汇总、总预算差额与超支判定、按 day_index 分组条目、行程天数推导（date range）、「今天」day_index 映射、未完成条目计数、打包清单进度。
  - 纯函数实现，无 IO，便于 90% 覆盖率。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 构造行程（多类型/多天/无费用条目/总预算 8000）汇总与手算一致；超支判定正确；「今天」映射含行程期外（无今天）分支。
  - `rule` TR-3.2: 未完成计数与清单进度在构造数据上断言正确。

## Task 4: LLM 客户端与草稿 schema
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1：test_llm.py 六分支（合法/非 JSON/天数超界/类型非枚举/未知字段/超时）+ 围栏容忍 + HTTP 401 + 响应结构异常全过；llm.py 覆盖率 99%。
  - TR-4.2：未配置时不发网络请求（捕获列表为空）；全部错误信息断言不含密钥子串；请求头确证 Bearer 密钥已发送。
  - TR-4.3：围栏包裹/前后杂文/无右花括号 JSON 均正确处理或给中文错误。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `llm.py`：OpenAI 兼容 `chat/completions` 客户端（httpx，timeout 可配）；system prompt 要求严格 JSON 输出（字段与草稿 schema 一致，含天数、类型枚举、时间、费用、标题、地点、备注）；解析层容忍 markdown 代码围栏与前后杂文；未配置密钥/端点时返回「未配置」受控错误（不发起网络请求）。
  - 草稿 schema 白名单校验：天数 1..N、类型六枚举、HH:MM、费用 ≥0、标题非空、未知字段拒绝；全部错误转中文信息。
  - 密钥治理：请求头注入密钥但任何异常/日志路径不输出密钥原文。
- **Acceptance Criteria Addressed**: AC-6、AC-12
- **Test Requirements**:
  - `rule` TR-4.1: mock 端点六分支（合法 JSON/非 JSON/天数超界/类型非枚举/未知字段/超时）行为正确；合法草稿结构完整。
  - `rule` TR-4.2: 未配置密钥时不发网络请求并返回「未配置」错误；异常消息与日志断言不含密钥子串。
  - `rule` TR-4.3: 代码围栏包裹的 JSON 与前后杂文 JSON 均能正确提取。

## Task 5: Web 骨架、安全中间件与界面基座
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1：外部 Origin / 无 token / 错误 token 三类 POST 全部 403；绑定地址断言 127.0.0.1；security.py 覆盖率 100%。
  - TR-5.2：404（行程不存在）/ 422 中文错误页渲染断言通过，无堆栈泄露。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `web/app.py`：FastAPI 应用工厂 + Jinja2 模板 + 静态资源；路由注册；错误页（404/422/500 中文友好）。
  - `web/security.py`：CSRF token（cookie + 隐藏域比对）、Origin/Referer 同源校验（POST 中间件）、绑定地址断言 127.0.0.1。
  - 界面基座：`base.html` 布局 + `styles.css`（白底淡蓝主色、紧凑布局、扁平线条内联 SVG 图标、`<dialog>` 毛玻璃弹窗样式）+ `app.js`（确认弹窗、加载态）。
- **Acceptance Criteria Addressed**: AC-9、AC-13（基座部分）
- **Test Requirements**:
  - `rule` TR-5.1: 外部 Origin / 无 token / 错误 token 三类 POST 全部 403；正常同源带 token 成功；绑定地址断言非 0.0.0.0。
  - `rule` TR-5.2: 404/422 错误页含中文提示不泄露堆栈。

## Task 6: 行程管理与每日编排页面
- **Status**: `completed`
- **Completion Evidence**:
  - TR-6.1：TestClient 全链路（创建→加条目→移动→勾选→编辑→删除）落盘一致；日期范围缩短时超界条目被拦截且原数据未破坏（422）。
  - TR-6.2：预算面板渲染 620/剩余正确；清单增删改勾落盘正确；真实服务冒烟 /trips 200。
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 5
- **Description**:
  - 列表页（状态分组、进行中「今天」与未完成计数、新建/复制/归档/删除确认弹窗）；行程创建/编辑表单（字段校验中文报错）。
  - 行程详情页：按天分组卡片（Day N + 日期 + 星期）、「今天」置顶高亮、条目增删改表单、上移/下移、勾选即落盘、预算面板（按类型/按天汇总 + 超支提示）、打包清单面板（增删改/数量/勾选）。
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-3（界面部分）、AC-4
- **Test Requirements**:
  - `rule` TR-6.1: TestClient 驱动创建→加条目→移动→勾选→改日期范围全链路，落盘 JSON 断言与界面流转一致；日期范围缩短时超界条目被拦截并提示。
  - `rule` TR-6.2: 预算面板渲染含分类汇总数字与超支提示；清单勾选落盘正确。

## Task 7: 导入导出
- **Status**: `completed`
- **Completion Evidence**:
  - TR-7.1：导出→删原→导入 round-trip 字段级等价；id 冲突预览明示并自动换新 id；全量导出包装可再导入。
  - TR-7.2：非 UTF-8/非 JSON/未知字段全部 422 拒绝且行程数零变化。
- **Priority**: medium
- **Depends On**: Task 2, Task 5
- **Description**:
  - 导出：单行程/全量 JSON HTTP 下载（流式响应，不落盘）；导出文件为合法 schema（可被自身导入 round-trip）。
  - 导入：上传 → schema 校验 → 预览页（将创建的行程摘要、id 冲突自动换新 id 说明）→ 确认写入；拒绝分支中文错误。
- **Acceptance Criteria Addressed**: AC-5、AC-11
- **Test Requirements**:
  - `rule` TR-7.1: 导出→导入 round-trip 数据等价（字段级断言）；id 冲突时预览明确说明且确认后生成新 id。
  - `rule` TR-7.2: 畸形上传（非 JSON/缺字段/未知字段）拒绝且无任何文件写入副作用。

## Task 8: AI 行程生成链路
- **Status**: `completed`
- **Completion Evidence**:
  - TR-8.1：mock LLM 全链路：生成→预览剔除 1 条→导入 1 条（source=ai、day_index 正确）；取消分支行程数据零变化；网络错误 502 中文提示。
  - TR-8.2：未配置时生成页显示降级引导、提交返回 502 中文、其余页面全部正常（离线可用断言）。
- **Priority**: high
- **Depends On**: Task 4, Task 6
- **Description**:
  - 生成表单页（目的地/日期范围默认当前行程/人数/偏好/预算档位）+ LLM 配置状态指示（已配置/未配置，未配置引导 README）。
  - 生成流程：POST → LLM 客户端 → 草稿校验 → 预览页（条目可剔除/微调）→ 「导入」写入行程（source=ai，day_index 定位）/「取消」丢弃；同步等待页显示加载态；错误页含中文原因与重试。
- **Acceptance Criteria Addressed**: AC-6、AC-7、AC-8（降级部分）、AC-14
- **Test Requirements**:
  - `rule` TR-8.1: mock LLM 全链路（生成→预览剔除 1 条→导入）仅新增对应条目、source=ai、day_index 正确；取消分支行程零变化。
  - `rule` TR-8.2: 未配置密钥时生成入口显示降级态与指引，其余功能页面全部正常（离线可用性断言）。

## Task 9: README、测试收口与覆盖率
- **Status**: `completed`
- **Completion Evidence**:
  - TR-9.1：迁移后 `apps/travel-planner` 复跑 91 用例全绿；覆盖率整体 93%，关键模块 domain 100% / llm 99% / models 96% / storage 91% / security 100%（全部 ≥90%）。
  - TR-9.2：test_no_future_annotations + ruff（含 TID251 __future__ 禁令）全过；README 含安装/快速开始/BYOK 配置/数据目录/开发测试。
  - 附加：真实 uvicorn 服务冒烟（health/trips/静态/404 全 200）；UI 视觉评审（视觉模型打分）：列表页 4/5（打磨后）、详情页 4/5、草稿预览页 4/5，均达 AC-13 阈值 ≥4。
- **Priority**: medium
- **Depends On**: Task 6, Task 7, Task 8
- **Description**:
  - README.md：定位、安装（py314 + pip install）、快速开始（serve/check）、LLM 配置说明（BYOK、任意 OpenAI 兼容端点、环境变量优先、密钥安全）、数据目录说明、导入导出说明、开发与测试。
  - `test_no_future_annotations.py`（py314 禁 `__future__` 导入红线，沿用 zhihu-checkin-hub 先例）；覆盖率收口（关键模块 ≥90%、整体 ≥80%）。
- **Acceptance Criteria Addressed**: NFR-4、NFR-8（静态扫描）
- **Test Requirements**:
  - `rule` TR-9.1: 全量测试通过；`pytest --cov` 报告关键模块（storage/llm/domain）≥90%、整体 ≥80%。
  - `rule` TR-9.2: 静态扫描源码无 `__future__` 导入、无密钥硬编码。

## Task 10: 全量迁移 apps/ 与索引登记
- **Status**: `completed`
- **Completion Evidence**:
  - TR-10.1：`.temp/travel-planner` → `apps/travel-planner` 迁移后 91 用例复跑全绿；apps/AGENTS.md 应用路由表 + 边界声明各增 1 行；generate-apps-index.py 刷新 apps/README.md（diff 仅 +1 行）。
  - TR-10.2：git status 仅含预期入库变更（spec 三件套、apps/travel-planner/、apps 路由表与索引）；.temp/ 残留仅临时依赖（venv/缓存/预览），随清理阶段移除。
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 迁移条件核验（测试 100% 通过、README 完善、无 P0/P1 缺陷）后将 `.temp/travel-planner/` 整体迁移至 `apps/travel-planner/`。
  - `apps/AGENTS.md` 应用路由表新增根级条目；运行 `generate-apps-index.py` 刷新 `apps/README.md` 应用清单。
  - 迁移后在 `apps/travel-planner/` 路径重跑测试验证；清理 `.temp/travel-planner/` 残留。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-10.1: 迁移后路径重跑全量测试通过；`apps/README.md` 索引含 travel-planner 条目；`.temp/` 无残留。
  - `rule` TR-10.2: 仓库根 `git status` 仅含预期入库变更（应用目录、路由表、README 索引、spec 三件套）。

## Task 11: 原子提交（C 阶段）
- **Status**: `completed`
- **Completion Evidence**:
  - TR-11.1：三笔原子提交全部通过 pre-commit 钩子门禁并落库（仅本地，未推送），实际提交顺序为 ①应用本体 → ②路由登记 → ③本提交（spec 三件套）：①`eded8a574` feat(travel-planner) 应用本体（38 文件 +4469，含 InstanceLock.acquire() → acquire_nowait() 更名修复钩子 TIMEOUT 拦截，修复后 91 用例全绿、覆盖率 93% 复验通过）；②`acc259908` chore(apps) 路由表与索引登记（2 文件 +5）；③本提交 docs(travel-planner) 固化 spec 三件套。各提交后工作区按对应范围 clean，提交信息符合 `type(scope): subject` 中文规范（UTF-8 无 BOM 临时文件 + git commit -F）。
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 按单一职责原子提交（Conventional Commits 中文主体）：①spec 三件套；②应用本体迁移；③apps 路由表与索引登记。仅本地提交不推送。
- **Acceptance Criteria Addressed**: 七概念 C 阶段闭环
- **Test Requirements**:
  - `rule` TR-11.1: 每次提交后工作区 clean（对应范围）；提交信息符合 `type(scope): subject` 中文规范。

> AI生成