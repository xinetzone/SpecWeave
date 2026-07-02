---
version: 1.0
---

# Frontmatter 脚本兼容性更新 - Implementation Plan

## [ ] Task 1: 更新 lib/patterns.py 共享库
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 更新 import 语句：从 `parse_toml_frontmatter, extract_frontmatter_field` 改为导入 `parse_frontmatter_unified`
  - 重写 `parse_pattern_frontmatter()` 函数：使用 `parse_frontmatter_unified()` 获取字段字典，直接从字典获取字符串/整数字段
  - 重写 `grep_maturity_per_directory()` 函数：使用 `parse_frontmatter_unified()` 获取 maturity 字段
  - 保持函数签名和返回值结构完全不变
  - 添加必要的类型注解
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: test_patterns.py 全部测试通过
  - `programmatic` TR-1.2: 运行 pattern-maturity.py stats 能正确统计模式数量和成熟度分布
  - `human-judgement` TR-1.3: 代码风格与现有代码一致，类型注解完整
- **Notes**: 这是最核心的共享库，pattern-maturity.py、check-pattern-quality.py（间接）等多个脚本依赖它

## [ ] Task 2: 更新 check-pattern-quality.py
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 更新 import 语句：移除 `parse_toml_frontmatter, extract_all_fields`，改为导入 `parse_frontmatter_unified`
  - 修改 `check_pattern()` 函数：使用 `parse_frontmatter_unified()` 替代 `parse_toml_frontmatter()` + `extract_all_fields()`
  - 修改 `check_frontmatter()` 函数：参数从 `frontmatter_text: Optional[str]` 改为 `fields: dict | None`，直接从字段字典检查字段存在性
  - 更新错误消息：将"TOML frontmatter"改为"frontmatter"
  - 处理字段值类型：对 validation_count/reuse_count 使用 `str(value)` 转换后再转 int，兼容字符串和列表
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 运行 check-pattern-quality.py 对现有模式文件检查，输出结果（通过/失败/警告/评分）与修改前一致
  - `programmatic` TR-2.2: 无 Python 异常或类型错误
- **Notes**: check_frontmatter 函数中 fields.get() 返回的值可能是 str 或 list[str]，需要使用 str() 安全转换

## [ ] Task 3: 更新 docgen.py
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 更新 import 语句：移除 `parse_toml_frontmatter, extract_all_fields, parse_toml_frontmatter_as_dict`，改为导入 `parse_frontmatter_unified`
  - 删除自定义的 `YAML_FRONTMATTER_RE` 正则和 `_dash_parse_yaml_simple()` 函数（已由 frontmatter.py 统一处理）
  - 修改 `_dash_scan_spec()` 函数：使用 `parse_frontmatter_unified()` 获取 status 字段，不再需要双重解析逻辑
  - 保持 tasks.md 状态检测逻辑（checkbox 计数）不变
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: test_docgen.py 全部测试通过
  - `programmatic` TR-3.2: 运行 `python docgen.py dashboard` 能正确生成看板
  - `programmatic` TR-3.3: 运行 `python docgen.py nav` 能正确生成导航表
- **Notes**: .trae/specs/ 下的 tasks.md 使用 YAML frontmatter，parse_frontmatter_unified() 原生支持

## [ ] Task 4: 更新 lib/checks/roles.py
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 更新 import 语句：从 `parse_toml_frontmatter, extract_frontmatter_field` 改为导入 `parse_frontmatter_unified`
  - 修改 `_extract_tier()` 函数：改为从字段字典获取 tier 值，而不是从 frontmatter 文本提取
  - 修改 `_validate_role_file()` 函数：使用 `parse_frontmatter_unified()` 获取标量字段（tier）
  - 保留 `_extract_permissions()` 函数和 `PERMISSIONS_TABLE_RE` 正则：[permissions] 是 TOML 表，parse_frontmatter_unified() 的 extract_all_fields() 不解析表，仍需正则提取
  - 更新错误消息：将"缺少有效的 TOML frontmatter"改为通用提示
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: test_checks_roles.py 全部测试通过（如果存在）
  - `programmatic` TR-4.2: 角色权限检查能正确识别 co-founder 和 standard 角色
- **Notes**: 角色文件包含 [permissions] TOML 表，这是旧版 TOML frontmatter 的嵌套结构。parse_frontmatter_unified() 只能解析顶层标量字段，[permissions] 表仍需用正则提取。这是已知限制，不影响迁移——角色文件迁移时需要特殊处理。

## [ ] Task 5: 更新 add-frontmatter.py
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 更新 import 语句：移除 `parse_yaml_frontmatter, parse_toml_frontmatter`，改为导入 `parse_frontmatter_unified`
  - 简化 `has_frontmatter()` 函数：直接调用 `parse_frontmatter_unified(file_path)`，返回非 None 即表示存在 frontmatter
  - 删除冗余的自定义 YAML 正则 `YAML_FM_RE`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-5.1: 运行 add-frontmatter.py --dry-run 能正确识别已有 frontmatter 的文件
  - `programmatic` TR-5.2: 无 frontmatter 的文件被正确识别为需要添加
- **Notes**: 该脚本用于批量添加 YAML frontmatter，更新后能同时识别 TOML 和 YAML 格式的现有 frontmatter

## [ ] Task 6: 更新 docs/knowledge/scripts/generate_index.py
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 添加 sys.path 设置，将项目根目录的 .agents/scripts 加入路径，以便导入 lib.frontmatter
  - 替换自定义的 `parse_frontmatter()` 函数为调用 `parse_frontmatter_unified()`
  - 保留 DEFAULT_META 默认值逻辑
  - 保留编码 fallback 处理（gbk 编码尝试）
  - 保留 tags 解析逻辑但适配 parse_frontmatter_unified 已返回 list 的情况
  - 保留 _parse_string_value 等辅助函数用于处理字段值
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: 运行 generate_index.py 能正常生成 docs/knowledge/README.md
  - `programmatic` TR-6.2: 生成的索引包含正确的分类、标签、条目数量
- **Notes**: 该脚本位于 docs/knowledge/scripts/，不在 .agents/scripts/ 下，需要特殊处理 import 路径

## [ ] Task 7: 运行现有测试套件验证无回归
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 运行 pytest 执行所有现有测试：test_frontmatter.py、test_patterns.py、test_docgen.py、test_check_duplication.py、test_checks_roles.py、test_frontmatter_unified.py 等
  - 确保所有测试通过，无失败、无错误
  - 如发现测试失败，分析原因并修复代码（不修改测试文件本身）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-7.1: pytest 运行所有测试，exit code 为 0
  - `programmatic` TR-7.2: 无失败用例、无错误用例
- **Notes**: 如果测试因为 frontmatter 解析逻辑变化而失败，优先修复应用代码，除非测试本身有明显错误

## [ ] Task 8: 冒烟测试验证所有脚本正常运行
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 依次运行关键脚本进行冒烟测试：
    1. python .agents/scripts/check-source-traceability.py
    2. python .agents/scripts/check-pattern-quality.py --score
    3. python .agents/scripts/pattern-maturity.py stats
    4. python .agents/scripts/docgen.py dashboard --dry-run（或实际运行验证输出）
    5. python .agents/scripts/check-duplication.py
    6. cd docs/knowledge/scripts && python generate_index.py
  - 验证所有脚本正常退出（exit code 0 或预期的非 0 但无 Python 异常）
  - 验证输出结果合理
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有冒烟测试脚本运行无 Python 异常（AttributeError/KeyError/TypeError 等）
  - `programmatic` TR-8.2: 输出结果与修改前相比在合理范围内（数量级一致、无明显错误）
- **Notes**: 冒烟测试使用当前项目中已有的 TOML frontmatter 文件，验证向后兼容性
