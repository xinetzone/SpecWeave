# Checklist

## sitecustomize.py 自动加载验证

- [x] `.agents/scripts/verify-sitecustomize-autoload.py` 脚本已创建并可独立运行
- [x] 脚本检测 sys.path 是否包含 `.agents/scripts/`
- [x] 脚本检测 `import sitecustomize` 是否成功且 `__file__` 指向 `.agents/scripts/sitecustomize.py`
- [x] 脚本检测 stdout/stderr 编码是否为 utf-8（_reconfigure_std_streams 副作用）
- [x] 脚本检测根目录是否存在遗留的 sitecustomize.py 并告警
- [x] 退出码规范：0=自动加载正常，1=需配置，2=存在冲突文件
- [x] 裸终端场景：脚本报告"需配置"并退出码 1，提示运行 setup-utf8-env.ps1 或加载 profile
- [x] 已持久化 PYTHONPATH 场景：脚本报告 sys.path 含 `.agents/scripts/`、import 成功、编码 utf-8，退出码 0
- [x] 已加载 profile.ps1 场景：验证结果与持久化场景一致，退出码 0
- [x] 根目录存在 sitecustomize.py 场景：脚本告警并建议删除根目录副本

## 关键配置文件放置校验

- [x] `.agents/scripts/check-file-placement.py` 脚本已创建
- [x] 受管关键文件清单覆盖：sitecustomize.py、setup-utf8-env.ps1、profile.ps1、Install-Profile.ps1、check-encoding.ps1、verify-encoding.ps1、setup-cmd-utf8.ps1
- [x] 脚本扫描项目根目录检测受管文件是否被错误放置
- [x] 对错误放置的文件输出正确位置与修复指令（git mv 命令）
- [x] 支持 `--json` 输出模式供 CI 集成
- [x] 退出码规范：0=全部正确，1=存在错误放置
- [x] 所有关键文件位置正确场景：脚本报告全部正确，退出码 0
- [x] 关键文件被错误放置场景：脚本列出错误文件及正确位置，退出码 1
- [x] CI/预提交集成场景：错误放置时提交/CI 失败并显示修复指引

## 文件放置治理文档

- [x] `.agents/docs/knowledge/best-practices/config-file-placement-convention.md` 文档已创建
- [x] 文档包含关键配置文件标准路径表（文件名 / 标准位置 / 用途 / 自动加载机制依赖）
- [x] 文档包含放置决策树（根目录 vs `.agents/scripts/` vs `.agents/docs/`）
- [x] 文档包含 Python 自动加载约定（sitecustomize.py、.pth 文件）与 PYTHONPATH 关系说明
- [x] 文档包含 sitecustomize.py 根因分析（原放根目录原因与代价）
- [x] 文档包含团队操作流程（新增配置文件的放置决策与校验步骤）
- [x] 文档包含 `.temp/` 治理小节，覆盖定义、用途分类、命名规则、存储位置、保留期、清理机制、责任人
- [x] `.temp/` 治理小节定义了四种用途分类（backup/experiments/exports/screenshots）
- [x] `.temp/` 治理小节命名规则要求含日期（YYYYMMDD）或 task-id，给出合规与不合规示例
- [x] `.temp/` 治理小节保留期明确：backup 3天 / experiments·exports·screenshots 14天 / 未分类 7天
- [x] `.temp/` 治理小节清理机制引用 `check-temp-lifecycle.py` 手动与 `--clean` 交互式
- [x] `.temp/` 治理小节明确责任人：创建者命名清理 / CI 与钩子自动检测 / 维护者定期审查
- [x] `.temp/` 治理小节引用 `.gitignore` 第 2 行 `.temp/` 规则作为"可随时清理"语义溯源
- [x] `.temp/` 治理小节记录反模式（禁 `.temp/` 外放置、禁无日期内容、禁依赖人工记忆清理）

## 预提交钩子与 CI 集成

- [x] `.agents/scripts/lib/checks/file_placement.py` 检查模块已创建，封装 `check-file-placement.py` 调用
- [x] `.agents/scripts/lib/checks/temp_lifecycle.py` 检查模块已创建，封装 `check-temp-lifecycle.py` 只读调用
- [x] `.githooks/pre-commit` 追加 `check-file-placement.py` 调用，错误放置时阻塞提交
- [x] `.githooks/pre-commit` 追加 `check-temp-lifecycle.py` 只读调用，超 30 天内容阻塞提交
- [x] CI 质量门禁脚本调用 `check-file-placement.py` 作为检查项
- [x] CI 质量门禁脚本调用 `check-temp-lifecycle.py` 只读模式作为检查项
- [x] CI 检测超 14 天 `.temp/` 内容时报警告（不阻塞）
- [x] CI 检测超 30 天 `.temp/` 内容时报错误（阻塞）
- [x] ci-check 相关 spec/文档已更新，反映新增两项检查项

## .temp 临时文件生命周期治理

- [x] `.agents/scripts/check-temp-lifecycle.py` 脚本已创建
- [x] 脚本扫描 `.temp/` 下所有内容（子目录与根级文件）
- [x] 命名合规校验：检测路径是否含用途前缀（backup/experiments/exports/screenshots）
- [x] 命名合规校验：检测名称是否含日期（YYYYMMDD）或 task-id
  - 已修复（Task 8）：新增 TASK_ID_PATTERN 正则，classify_item 在 parse_date_from_name 返回 None 时检查 task-id，命中则 has_date=True、date_source="task-id"
- [x] 命名不合规项被列出并告警原因（缺少日期 / 缺少用途前缀），不自动重命名
- [x] 命名不合规场景以非零退出码退出
- [x] 保留期检测按用途分类：backup 3天 / experiments·exports·screenshots 14天 / 未分类 7天
- [x] 基准日期优先取名称解析的 YYYYMMDD，回退取文件 mtime
- [x] 输出中标注每项基准日期来源（"名称解析"或"文件 mtime"）
  - 已修复（Task 9）：不合规项输出行追加 `({it.date_source})` 标注；新增合规未过期项汇总说明；JSON 模式保持不变
- [x] 只读检查模式（默认）按用途分组汇总过期项
- [x] `--clean` 交互式清理：列出过期项 → 请求 y/N 确认 → 删除 → 输出摘要（删除项数、释放空间 MB、剩余项数）
- [x] `--clean` 保留命名不合规项需人工处理
- [x] `--clean --yes` 跳过确认（自动化场景）
- [x] 支持 `--json` 输出供 CI 集成
- [x] `.temp/` 为空或不存在时报告"无临时内容需检查"，退出码 0
- [x] 合规命名示例正确识别：`.temp/backup/docs-migration-20260715/`、`.temp/experiments/color-palette-20260718/`
- [x] 不合规命名示例正确告警：`.temp/record.md`（无前缀无日期）、`.temp/backup/old/`（无日期）

## 端到端验证

- [x] 裸终端运行 verify-sitecustomize-autoload.py 退出码 1
- [x] setup-utf8-env.ps1 -Scope User 后新终端运行验证脚本退出码 0
- [x] 已加载 profile.ps1 终端运行验证脚本退出码 0
- [x] 根目录临时放置 sitecustomize.py 被检测告警，删除后恢复
- [x] check-file-placement.py 确认所有受管文件位置正确，退出码 0
- [x] 根目录临时放置 setup-utf8-env.ps1 被检测错误放置，退出码 1，删除后恢复
- [x] check-temp-lifecycle.py 对当前 `.temp/` 无日期无前缀内容输出命名不合规告警
- [x] `.temp/backup/test-20260718/` 测试目录按 backup 类 3 天保留期计算正确
- [x] check-temp-lifecycle.py --clean 交互式清理流程正常（列出→确认→删除→摘要）
- [x] pre-commit 钩子触发文件放置校验与 `.temp` 生命周期检查均被调用
- [x] pre-commit 钩子对超 30 天 `.temp/` 内容阻塞提交

## 文档与知识库更新

- [x] `windows-terminal-utf8-complete-guide.md` 新增"自动加载验证"小节
- [x] `windows-platform-compatibility-guide.md` 脚本表补充三个新脚本
- [x] 所有新增脚本与文档的交叉引用使用相对路径（禁 `file:///` 绝对路径）
- [x] 通过 `python .agents/scripts/check-links.py --path .agents/scripts --path .agents/docs/knowledge/best-practices` 链接校验无断链
