# Checklist

## 脚本文件
- [x] `.agents/scripts/check-spec-consistency.py` 脚本文件存在
- [x] `.agents/scripts/README.md` 更新

## spec.md 解析器
- [x] `parse_spec()` 正确提取 Requirement、Scenario、数据引用

## tasks.md 解析器
- [x] `parse_tasks()` 正确提取 Task/SubTask、统计数量

## checklist.md 解析器
- [x] `parse_checklist()` 正确提取检查类别、检查点、统计数量

## 一致性检查引擎
- [x] 需求 → 任务覆盖、场景 → 检查点覆盖、数据一致性、交叉引用

## 结构化输出
- [x] 彩色输出、摘要、非零退出码

## 命令行参数
- [x] `--spec-dir`、`--all`、`--json`

## v1.0 验证
- [x] 3 个 spec 目录检查正常

## v1.1 优化 — 可配置阈值
- [x] `--match-threshold` 参数存在，默认值为 1
- [x] 默认阈值 1 下，create-agents-md-and-config 警告从 43 降至 40
- [x] `--match-threshold 2` 下行为与 v1.0 一致

## v1.1 优化 — 路径引用上下文感知
- [x] spec 相对路径以 spec 所在目录为基准解析
- [x] 以 `.agents/`、`vendor/`、`.trae/`、`docs/` 开头的路径以项目根目录解析
- [x] 交叉引用路径解析逻辑正确

## v1.1 优化 — 自引用/外部引用区分
- [x] `is_retrospective_context()` 函数存在
- [x] 自引用数据不一致 → 错误；外部引用数据不一致 → 警告
- [x] retrospective-agents-spec-system 数据错误 4→0（全部降级为警告）
- [x] check-spec-consistency 自身数据错误 2→0（全部降级为警告）

## v1.1 验证
- [x] 对 4 个现有 spec 目录执行检查，结果符合预期
- [x] check-spec-consistency 自身 spec.md 数据引用已修正

## v1.2 优化 — 元文档识别升级
- [x] `detect_meta_document()` 函数存在，替代 `is_retrospective_context()`
- [x] 显式标记 `<!-- meta_type: xxx -->` 正则匹配正确
- [x] 显式标记优先于关键词检测（detection_method="explicit"）
- [x] 无显式标记时关键词兜底（detection_method="keyword"）
- [x] 无标记无关键词时返回 (False, "none")
- [x] 关键词列表扩展至审计、评审、评估、对比分析、迁移方案
- [x] `check_data_consistency()` 参数 `is_retrospective` → `is_meta`
- [x] 警告消息从"疑似引用被复盘项目数据" → "疑似引用外部项目数据（元文档）"
- [x] `retrospective-agents-spec-system/spec.md` 已添加 `<!-- meta_type: retrospective -->`
- [x] 所有调用点已更新，无残留 `is_retrospective` 引用

## v1.2 验证
- [x] 对 4 个 spec 目录回归验证，行为与 v1.1 一致
- [x] retrospective 显式标记识别正确，数据错误为 0