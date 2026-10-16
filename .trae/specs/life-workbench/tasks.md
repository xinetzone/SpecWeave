# 一页生活（life-workbench）- 实施计划

> 七概念链路：新功能开发 C → V。开发根：`.temp/life-workbench/`；正式应用根：`apps/life-workbench/`。实施前须由用户批准本文件与 `spec.md`；`review.md` 仅在实施队列清空后创建。

## Task 1: 自包含应用基座与可靠存储
- **Status**: `completed`
- **Completion Evidence**:
  - TR-1.1：静态扫描 `apps/life-workbench/index.html`，除 SVG 命名空间常量外无 `http(s)://`、外链脚本/样式/字体/图片引用；无头浏览器离线加载七模块全部可交互。
  - TR-1.2：无头浏览器新增/编辑/勾选后读取 localStorage 对拍一致（39 条断言全绿）；`pagehide`/`visibilitychange`/`beforeunload` 均绑定 `flushPending` 冲刷防抖（180ms）。
  - TR-1.3：写入 `meta.addedSinceBackup=19` 后新增 1 条记录，备份提醒横幅出现；合并模式导入 25 条记录全部落盘（无人工条数上限）；非 JSON/结构不可识别时仅弹提示、零写入。
  - TR-1.4：主数据被置为不可解析内容后弹出恢复对话框（可恢复安全快照/下载损坏原文/重置），恢复后主数据可解析；模拟 `setItem` 抛 `QuotaExceededError` 后显示持久错误条与「紧急导出 JSON」。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `.temp/life-workbench/` 创建自包含 `index.html` 与项目说明 `README.md`；所有 CSS、JavaScript、SVG 图标和演示数据内联，不产生运行时外链。
  - 建立带 `schemaVersion` 的统一状态、稳定 ID、演示数据标记、输入防抖与 `pagehide` 同步冲刷。
  - 实现主存储 + 最近安全快照、解析损坏恢复、保存异常显性提示、紧急 JSON 下载、演示数据清理和全量清空二次确认。
  - 实现全量 JSON 导出、合并/替换导入、结构校验、摘要确认、新增 20 条备份提醒。
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-7、AC-8
- **Test Requirements**:
  - `rule` TR-1.1: 静态扫描无远程脚本/样式/字体/图片与资源文件依赖；断网打开后基础导航和新增可用。
  - `rule` TR-1.2: 新增、字段输入、勾选和刷新对拍后状态一致；`pagehide` 冲刷防抖内容。
  - `rule` TR-1.3: 第 20 条新增出现备份提醒，导出后重置；合法大批量 JSON 可合并/替换，畸形 JSON 零写入。
  - `rule` TR-1.4: 主数据损坏时可恢复安全快照或下载损坏原文；模拟存储失败时显示持久错误并可导出最新内存状态。

## Task 2: 今日总览、记账理财与 Excel 导出
- **Status**: `completed`
- **Completion Evidence**:
  - TR-2.1：演示数据（两个月、多分类、收支）下收入/支出/结余、上月对比百分比、预算进度与消费占比与手算一致（代码为纯加法汇总 + 分类归一）。
  - TR-2.2：月份/类型/分类三级筛选后列表与筛选条件一致；下载 CSV 首三字节为 `EF BB BF`（UTF-8 BOM），表头为 `日期,类型,分类,金额,备注`，含新增记录行与合计行。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 建立编辑台式总览：日期问候、生活节奏综合分、预算健康、习惯完成、日程完成与今日重点。
  - 实现收支新增/删除、月预算、月份/类型/分类筛选、当月汇总、上月对比、预算进度和消费结构可视化。
  - 生成 Excel 可直接打开的 UTF-8 BOM CSV 下载，导出当前筛选结果。
- **Acceptance Criteria Addressed**: AC-3、AC-10
- **Test Requirements**:
  - `rule` TR-2.1: 两个月、多分类、收支数据的汇总、环比、结余、预算与消费占比和手算一致。
  - `rule` TR-2.2: 筛选结果与界面列表一致；下载 CSV 含 BOM、中文表头与正确金额。
  - `rubric` TR-2.3: 总览信息层次与财务结构图不呈现为等尺寸卡片阵列；视觉质量 1-5 分阈值 >=4，证据为独立审查。

## Task 3: 习惯健康与减脂健身
- **Status**: `completed`
- **Completion Evidence**:
  - TR-3.1：勾选/计数/数值三型打卡均落盘，计数型 `+` 点击后当日值 +1 并持久化；每个习惯渲染 30 格热力图（30 天达标数与完成率同步）。
  - TR-3.2：8 条日志下 BMI、目标进度、热量缺口与按日排序的滚动 7 日均线由同一组纯函数计算并渲染为两条 `polyline`（原始值 + 均线）。
  - TR-3.3：周计划七天文本可直接编辑（input 事件即存），当天行可勾选且刷新后保留。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现习惯新增/删除、勾选/计数/数值三种打卡、目标值与单位、最近 30 天热力图。
  - 实现身高/起始体重/目标体重设置，体重/体脂/摄入/消耗日志，BMI、目标进度、累计变化与热量缺口。
  - 使用内联 SVG 绘制体重原始趋势与 7 日移动均线；实现周一至周日可编辑训练计划及完成态。
- **Acceptance Criteria Addressed**: AC-4、AC-5
- **Test Requirements**:
  - `rule` TR-3.1: 三种习惯当天值、目标完成度、删除逻辑与每项 30 格热力图正确，刷新后保留。
  - `rule` TR-3.2: 构造 8 条日志后 BMI、目标进度、热量缺口与 7 日均线同手算结果一致。
  - `rule` TR-3.3: 周计划七天内容可编辑、当天可勾选，刷新后内容与完成态保留。

## Task 4: 日程、待买与书影音收藏
- **Status**: `completed`
- **Completion Evidence**:
  - TR-4.1：日程按今天/未来/逾期/全部筛选正确，逾期项标红，完成态刷新后保留。
  - TR-4.2：待买未完成数量与 `数量×单价` 预估总额正确，购买态按优先级排序后置并持久化。
  - TR-4.3：收藏封面墙（本地色块，无远程图片）与列表视图切换正常；类型/状态筛选、年度完成数、类型分布、平均星级、月度柱状统计正确。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 实现日程新增/完成/删除、今天/未来/逾期分组与日期查看。
  - 实现待买条目新增/购买/删除、数量/单价/优先级/分类、未买数量与预估总额。
  - 实现书影音新增/删除、类型/状态/星级/短评、CSS 本地封面、墙/列表切换、筛选与年度统计。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 日程状态分组和逾期判定正确，完成切换刷新后保留。
  - `rule` TR-4.2: 待买未完成数量与数量×单价总额正确，购买态可筛除并持久化。
  - `rule` TR-4.3: 收藏墙/列表、类型/状态筛选、年度完成数/类型分布/平均星级/月度趋势正确。

## Task 5: 响应式整合与应用迁移登记
- **Status**: `completed`
- **Completion Evidence**:
  - TR-5.1：360px 与 1440px 双视口下七个模块均无横向溢出（`scrollWidth - 视口宽 <= 1`）且内容非空，顶栏可见（30 条断言全绿）。
  - TR-5.2：迁移后直接以 HTTP 打开 `apps/life-workbench/index.html` 完整冒烟通过；`.temp/life-workbench/` 已清理。
  - TR-5.3：`apps/AGENTS.md` 路由表与边界声明各 +1 行，`apps/README.md` 经 `python .agents/scripts/docgen.py apps` 刷新（12 条目，含 life-workbench）并补充根级应用说明。
  - TR-5.4：独立对抗审查评分见 `review.md`（CP-U1 阈值 ≥4）。
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 整合模块导航、快捷新增、表单对话框、空状态、提示条、键盘焦点与 `prefers-reduced-motion`。
  - 在 360×800 与 1440×900 视口完成全模块冒烟，修复横向溢出、遮挡和不可触达操作。
  - 验证正式 `index.html` 自包含性后，将 `.temp/life-workbench/` 全量迁移到 `apps/life-workbench/`，清理暂存目录。
  - 更新 `apps/AGENTS.md` 路由表与边界声明，运行应用索引生成器同步 `apps/README.md`。
- **Acceptance Criteria Addressed**: AC-1、AC-9、AC-10、NFR-8
- **Test Requirements**:
  - `rule` TR-5.1: 双视口无页面级横向溢出，所有模块、对话框和主要按钮可达；基础键盘焦点与标签检查通过。
  - `rule` TR-5.2: 迁移后直接打开 `apps/life-workbench/index.html` 的完整冒烟通过，`.temp/life-workbench/` 无残留。
  - `rule` TR-5.3: `apps/AGENTS.md` 与 `apps/README.md` 均存在 life-workbench 登记，仓库状态仅含预期文件。
  - `rubric` TR-5.4: 克制、高级、有生活感与非模板化布局 1-5 分阈值 >=4，证据为独立对抗审查。
