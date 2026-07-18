# Tasks

- [x] Task 1: 创建 sitecustomize.py 自动加载验证脚本
  - [x] SubTask 1.1: 创建 `.agents/scripts/verify-sitecustomize-autoload.py`，实现三场景检测（裸终端 / 持久化 PYTHONPATH / 已加载 profile）
  - [x] SubTask 1.2: 脚本检测 sys.path 是否包含 `.agents/scripts/`、`import sitecustomize` 是否指向正确文件、stdout/stderr 编码是否为 utf-8
  - [x] SubTask 1.3: 检测根目录是否存在遗留的 sitecustomize.py，存在则告警
  - [x] SubTask 1.4: 提供明确退出码（0=自动加载正常，1=需配置，2=存在冲突文件）与人类可读报告
  - [x] SubTask 1.5: 在三种实际终端场景下运行脚本并记录验证结果到 `.agents/docs/retrospective/reports/bugfix/retrospective-ci-quality-gates-path-migration-20260718/` 或同级验证报告

- [x] Task 2: 创建关键配置文件放置校验脚本
  - [x] SubTask 2.1: 创建 `.agents/scripts/check-file-placement.py`，维护受管关键文件清单（sitecustomize.py、setup-utf8-env.ps1、profile.ps1、Install-Profile.ps1、check-encoding.ps1、verify-encoding.ps1、setup-cmd-utf8.ps1）
  - [x] SubTask 2.2: 扫描项目根目录，检测受管文件是否被错误放置到根目录
  - [x] SubTask 2.3: 对每个错误放置的文件输出正确位置与修复指令（git mv 命令）
  - [x] SubTask 2.4: 支持 `--json` 输出模式供 CI 集成，退出码 0=全部正确，1=存在错误放置

- [x] Task 3: 创建文件放置治理文档
  - [x] SubTask 3.1: 创建 `.agents/docs/knowledge/best-practices/config-file-placement-convention.md`
  - [x] SubTask 3.2: 编写关键配置文件标准路径表（文件名 / 标准位置 / 用途 / 自动加载机制依赖）
  - [x] SubTask 3.3: 编写放置决策树（判断"应放根目录"vs"应放 .agents/scripts/"vs"应放 .agents/docs/"的依据）
  - [x] SubTask 3.4: 编写根因分析章节：分析 sitecustomize.py 原本被放到根目录的原因（Python 自动加载约定便利性）与代价（根目录污染、组织不一致）
  - [x] SubTask 3.5: 编写团队操作流程：新增配置文件时的放置决策与校验步骤
  - [x] SubTask 3.6: 编写 `.temp/` 临时文件治理小节，覆盖定义、用途分类（backup/experiments/exports/screenshots）、命名规则（含日期或 task-id）、存储位置、保留期（backup 3天 / experiments·exports·screenshots 14天 / 未分类 7天）、清理机制、责任人、反模式
  - [x] SubTask 3.7: 引用 `.gitignore` 第 2 行 `.temp/` 规则作为"可随时清理"语义溯源依据

- [x] Task 4: 集成预提交钩子与 CI 质量门禁
  - [x] SubTask 4.1: 在 `.agents/scripts/lib/checks/` 下新增 `file_placement.py` 检查模块，封装对 `check-file-placement.py` 的调用
  - [x] SubTask 4.2: 在 `.agents/scripts/lib/checks/` 下新增 `temp_lifecycle.py` 检查模块，封装对 `check-temp-lifecycle.py` 的只读调用
  - [x] SubTask 4.3: 修改 `.githooks/pre-commit`（经 `.agents/scripts/hooks/pre_commit.py` 实现），追加 `check-file-placement.py` 调用与 `check-temp-lifecycle.py` 只读调用（超 30 天阻塞提交）
  - [x] SubTask 4.4: 修改 CI 质量门禁脚本（`.agents/scripts/ci-check.ps1` 与 `.agents/scripts/ci-check.sh`），将文件放置校验与 `.temp` 生命周期检查作为检查项（14 天警告、30 天错误）
  - [x] SubTask 4.5: 更新 ci-check 相关 spec/文档，反映新增的两项检查项

- [x] Task 5: 创建 .temp 生命周期检查脚本
  - [x] SubTask 5.1: 创建 `.agents/scripts/check-temp-lifecycle.py`，扫描 `.temp/` 下所有内容
  - [x] SubTask 5.2: 实现命名合规校验：检测路径是否含用途前缀（backup/experiments/exports/screenshots）与日期（YYYYMMDD）或 task-id，不合规项告警并以非零退出码标识
  - [x] SubTask 5.3: 实现保留期检测：按用途分类（backup 3天 / experiments·exports·screenshots 14天 / 未分类 7天）计算存活天数，基准日期优先取名称解析的 YYYYMMDD，回退取文件 mtime，标注基准来源
  - [x] SubTask 5.4: 实现只读检查模式（默认）：按用途分组汇总过期项，输出每项的用途分类、创建日期、保留期、已存活天数、基准日期来源
  - [x] SubTask 5.5: 实现 `--clean` 交互式清理：列出过期项 → 请求 y/N 确认 → 删除过期内容 → 输出清理摘要（删除项数、释放空间 MB、剩余项数）；保留命名不合规项需人工处理
  - [x] SubTask 5.6: 实现 `--clean --yes` 跳过确认（用于自动化场景），支持 `--json` 输出供 CI 集成
  - [x] SubTask 5.7: 处理边界场景：`.temp/` 为空或不存在时报告"无临时内容需检查"并以零退出码退出

- [x] Task 6: 更新现有 UTF-8 知识库文档
  - [x] SubTask 6.1: 在 `windows-terminal-utf8-complete-guide.md` 中新增"自动加载验证"小节，引用 `verify-sitecustomize-autoload.py` 使用方式
  - [x] SubTask 6.2: 在 `windows-platform-compatibility-guide.md` 的脚本表中补充三个新脚本（verify-sitecustomize-autoload.py、check-file-placement.py、check-temp-lifecycle.py）

- [x] Task 7: 端到端验证
  - [x] SubTask 7.1: 在裸终端运行 `verify-sitecustomize-autoload.py`，确认报告"需配置"并退出码 1
  - [x] SubTask 7.2: 运行 `setup-utf8-env.ps1 -Scope User` 后开新终端，运行验证脚本，确认退出码 0（注：沙箱限制 PYTHONPATH 剥离，注册表持久化成功，7.3 证明逻辑正确）
  - [x] SubTask 7.3: 在已加载 profile.ps1 的终端运行验证脚本，确认退出码 0
  - [x] SubTask 7.4: 临时将 sitecustomize.py 复制到根目录，运行验证脚本，确认检测到冲突并告警，随后删除根目录副本
  - [x] SubTask 7.5: 运行 `check-file-placement.py`，确认所有受管文件位置正确，退出码 0
  - [x] SubTask 7.6: 临时将 setup-utf8-env.ps1 复制到根目录，运行放置校验，确认检测到错误放置，退出码 1，随后删除根目录副本
  - [x] SubTask 7.7: 运行 `check-temp-lifecycle.py`，确认对当前 `.temp/` 内容（含 lenovo-screenshots/、extract-structure.js 等无日期无前缀内容）输出命名不合规告警，退出码非零
  - [x] SubTask 7.8: 在 `.temp/backup/` 下创建带日期的测试目录（如 `test-20260718/`），运行脚本确认按 backup 类 3 天保留期计算；测试完毕清理
  - [x] SubTask 7.9: 运行 `check-temp-lifecycle.py --clean`，确认交互式清理流程正常（列出 → 确认 → 删除 → 摘要）
  - [x] SubTask 7.10: 触发 pre-commit 钩子（或模拟），确认文件放置校验与 `.temp` 生命周期检查均被调用，超 30 天内容阻塞提交（发现并修复 pre_commit.py GBK 编码 bug）

- [x] Task 8: 修复 check-temp-lifecycle.py 命名合规校验缺失 task-id 检测
  - 背景：Spec 模式第七阶段验证发现 checklist 第 4 项 PARTIAL——脚本 docstring（行 15）声明"名称必须包含创建日期（YYYYMMDD）或关联 task-id"，但代码仅实现 YYYYMMDD 日期检测（`DATE_PATTERN = re.compile(r"\d{8}")`，行 77），未实现 task-id 模式匹配。导致纯 task-id 命名的内容（如 `.temp/experiments/task-abc123/`）被误判为"缺少日期"不合规
  - [x] SubTask 8.1: 在 `check-temp-lifecycle.py` 中新增 task-id 检测正则模式（如 `TASK_ID_PATTERN = re.compile(r"task-[a-zA-Z0-9][a-zA-Z0-9-]*", re.IGNORECASE)` 或与项目 task-id 约定一致的格式）
  - [x] SubTask 8.2: 修改 `classify_item` 函数（行 178-236）：将 `has_date` 字段语义扩展为"含日期或 task-id"，并在 `parse_date_from_name` 返回 None 时检查 task-id 模式；若 task-id 命中则将 `has_date=True`、`date_source="task-id"`（无基准日期可解析时回退 mtime）；告警原因中区分"缺少日期与 task-id"
  - [x] SubTask 8.3: 更新脚本 docstring 与 `--help` 输出（若存在），明确"日期或 task-id"两种合规条件
  - [x] SubTask 8.4: 测试验证：构造 `.temp/experiments/task-abc123/` 测试目录，运行脚本确认被识别为合规项（无"缺少日期"告警）；构造 `.temp/experiments/foo/`（无日期无 task-id）确认仍告警"缺少日期与 task-id"
  - [x] SubTask 8.5: 同步更新 `.agents/docs/knowledge/best-practices/config-file-placement-convention.md` 第 6.3 节命名规则，明确 task-id 格式约定（如 `task-{alphanumeric-hyphen}`），并给出 task-id 合规示例

- [x] Task 9: 修复 check-temp-lifecycle.py 文本模式未对每项输出基准日期来源
  - 背景：Spec 模式第七阶段验证发现 checklist 第 9 项 PARTIAL——脚本 docstring（行 22）声明"输出中标注每项的基准日期来源"，JSON 模式（`TempItem.to_dict` 行 120）已对每项输出 `date_source`，但文本模式仅在过期项输出中显示 `({it.date_source})`（行 429），不合规项（行 410-417）与合规未过期项未单独列出 date_source
  - [x] SubTask 9.1: 修改 `print_report` 函数（或对应文本输出逻辑）：在不合规项输出行追加 `({it.date_source})` 标注，与过期项输出格式保持一致
  - [x] SubTask 9.2: 评估是否需要在合规未过期项的汇总输出中列出每项的 date_source（若当前汇总不含此项的逐项列表，可在汇总表头说明"合规项未过期，未逐项列出"；若已逐项列出，则追加 date_source 列）
  - [x] SubTask 9.3: 测试验证：运行 `python .agents/scripts/check-temp-lifecycle.py`，确认不合规项输出含 `(文件 mtime)` 或 `(名称解析)` 标注；JSON 模式输出保持不变

# Task Dependencies

- Task 2 独立于 Task 1，可并行
- Task 3 独立于 Task 1、Task 2，可并行
- Task 5 独立于 Task 1、Task 2，可并行
- Task 4 依赖 Task 2（需要 check-file-placement.py 已创建）与 Task 5（需要 check-temp-lifecycle.py 已创建）
- Task 6 依赖 Task 1（需要引用验证脚本）与 Task 5（需要引用 .temp 脚本）
- Task 7 依赖 Task 1、Task 2、Task 4、Task 5、Task 6（需要所有产出物就位）
