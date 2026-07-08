---
version: 1.0
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/update-frontmatter-scripts-compat/spec.toml"
---
# Frontmatter 脚本兼容性更新 - Product Requirement Document

## Overview
- **Summary**: 更新项目中所有依赖 frontmatter 解析的 Python 脚本，使其兼容新的统一解析入口 `parse_frontmatter_unified()`，确保在 TOML(+++) → YAML+x-toml-ref 迁移前后都能正常工作。
- **Purpose**:
  1. 统一 frontmatter 解析入口，消除各脚本重复实现的解析逻辑
  2. 确保现有脚本在迁移过渡期同时支持两种格式
  3. 正确处理 `parse_frontmatter_unified()` 返回的列表类型值（如 tags、rules 等数组字段）
  4. 为即将到来的批量格式迁移做好工具链准备
- **Target Users**: AI 智能体（CI 检查脚本）、项目维护者（运行质量检查）

## Goals
- 更新所有使用 `parse_toml_frontmatter()` + `extract_all_fields()` 的脚本，改为使用 `parse_frontmatter_unified()`
- 更新所有自己实现正则匹配 `+++` 或 `---` 的脚本，改为使用 frontmatter.py 统一入口
- 保持 `extract_frontmatter_field()` 和 `extract_frontmatter_field_from_file()` 的向后兼容（无需修改已使用这些函数的脚本）
- 确保所有修改后的脚本通过现有测试
- 对每个修改的脚本进行冒烟测试，验证 TOML 格式和新格式都能正常解析
- 正确处理 `parse_frontmatter_unified()` 返回的字典中值为 `list[str]` 的情况

## Non-Goals (Out of Scope)
- 不修改 `frontmatter.py` 和 `migrate-frontmatter.py`（这两个文件刚更新完成）
- 不修改 `tests/` 目录下的测试文件
- 不修改 MDI 相关代码（mdi/ 目录），这些是新代码且已使用正确的解析方式
- 不修改 `scan_toml_frontmatter.py`（该脚本专门用于扫描 TOML 基线，属于迁移工具，迁移完成后可归档）
- 不执行实际的 TOML→YAML 文件迁移（这是 migrate-frontmatter.py 的工作）
- 不修改 `lib/spec/format_checkers.py`（该文件用正则直接匹配 version 字段，不依赖 frontmatter 库，且仅用于 Spec 文档检查）

## Background & Context
- **当前状态**：frontmatter.py 已更新，新增了 `parse_frontmatter_unified(file_path)` 统一入口函数，能自动识别 TOML(+++)/YAML(---)/x-toml-ref 格式并返回合并后的字典
- **返回值差异**：
  - 旧的 `parse_toml_frontmatter_as_dict()` 和 `extract_all_fields()` 返回 `dict[str, str]`（所有值都是字符串）
  - 新的 `parse_frontmatter_unified()` 返回 `dict[str, str | list[str]]`（数组字段如 tags/rules/references/skills 会被解析为 Python 列表）
- **向后兼容**：`extract_frontmatter_field()` 和 `extract_frontmatter_field_from_file()` 保持不变，仍返回字符串（用于单个字段提取场景）
- **需要更新的核心文件**：lib/patterns.py（被多个脚本依赖的共享库）、docgen.py、check-pattern-quality.py、lib/checks/roles.py、add-frontmatter.py、docs/knowledge/scripts/generate_index.py

## Functional Requirements

- **FR-1**: lib/patterns.py 更新
  - FR-1.1: `parse_pattern_frontmatter()` 函数从使用 `parse_toml_frontmatter()` + `extract_frontmatter_field()` 改为使用 `parse_frontmatter_unified()`
  - FR-1.2: 正确处理字符串和列表类型的字段值
  - FR-1.3: `grep_maturity_per_directory()` 函数从直接使用 `parse_toml_frontmatter()` + `extract_frontmatter_field()` 改为使用 `parse_frontmatter_unified()` 获取字段
  - FR-1.4: 保持函数签名和返回值结构不变，确保依赖它的脚本（pattern-maturity.py、pattern-maturity-stats.py 等）无需修改

- **FR-2**: check-pattern-quality.py 更新
  - FR-2.1: `check_pattern()` 函数从使用 `parse_toml_frontmatter()` + `extract_all_fields()` 改为使用 `parse_frontmatter_unified()`
  - FR-2.2: `check_frontmatter()` 函数参数从 `frontmatter_text: Optional[str]` 改为 `fields: dict | None`，直接接收解析好的字段字典
  - FR-2.3: 错误消息从"TOML frontmatter"改为通用的"frontmatter"，不特指 TOML 格式
  - FR-2.4: 处理 `validation_count`/`reuse_count` 字段时，兼容字符串和整数类型

- **FR-3**: docgen.py 更新
  - FR-3.1: `_dash_scan_spec()` 函数从使用 `parse_toml_frontmatter_as_dict()` + 自定义 `_dash_parse_yaml_simple()` 改为使用 `parse_frontmatter_unified()`
  - FR-3.2: 删除自定义的 `_dash_parse_yaml_simple()` 函数和 `YAML_FRONTMATTER_RE` 正则（已由 frontmatter.py 统一处理）
  - FR-3.3: 保持 tasks.md 状态检测逻辑不变

- **FR-4**: lib/checks/roles.py 更新
  - FR-4.1: `_validate_role_file()` 函数从使用 `parse_toml_frontmatter()` + `extract_frontmatter_field()` 改为使用 `parse_frontmatter_unified()`
  - FR-4.2: `_extract_tier()` 函数改为从字段字典直接获取值，而不是从 frontmatter 文本提取
  - FR-4.3: `_extract_permissions()` 函数目前解析 `[permissions]` TOML 表，由于角色文件暂不迁移（仍使用 TOML），保留解析能力但通过 `parse_frontmatter_unified()` 的 deprecation 警告提示迁移
  - FR-4.4: 错误消息更新为通用 frontmatter 术语

- **FR-5**: add-frontmatter.py 更新
  - FR-5.1: `has_frontmatter()` 函数简化为直接调用 `parse_frontmatter_unified()`，如果返回非 None 则表示存在 frontmatter
  - FR-5.2: 删除冗余的双重检查逻辑（自定义 YAML 正则 + parse_toml_frontmatter + parse_yaml_frontmatter）

- **FR-6**: docs/knowledge/scripts/generate_index.py 更新
  - FR-6.1: 将自定义的 `parse_frontmatter()` 函数替换为调用 `.agents/scripts/lib/frontmatter.py` 的 `parse_frontmatter_unified()`
  - FR-6.2: 添加正确的 sys.path 设置以能导入项目共享库
  - FR-6.3: 保持 tags 列表解析逻辑兼容（新函数已支持解析 YAML 行内列表）
  - FR-6.4: 保留 DEFAULT_META 默认值逻辑和编码 fallback 处理

- **FR-7**: 列表类型值处理
  - FR-7.1: 所有使用字段值的地方，使用 `str(value)` 进行安全转换，兼容字符串和列表类型
  - FR-7.2: 对于整数类型字段（validation_count、reuse_count），先转换为字符串再转 int
  - FR-7.3: 检查逻辑中判断字段存在性时，使用 `key in dict` 而非 `value is not None`

## Non-Functional Requirements
- **NFR-1**: 向后兼容性：所有脚本在迁移前（纯 TOML 格式）必须正常工作，输出结果与修改前一致
- **NFR-2**: 向前兼容性：所有脚本在迁移后（YAML+x-toml-ref 格式）必须正常工作
- **NFR-3**: 代码质量：添加必要的类型注解，遵循现有代码风格，不添加注释（除非必要的 docstring）
- **NFR-4**: 零回归：现有测试套件全部通过
- **NFR-5**: Deprecation 警告：解析 TOML 格式时的 DeprecationWarning 不影响脚本正常运行（可以被 warnings 过滤或正常输出）

## Constraints
- **Technical**: Python 3.13+，不引入新依赖，仅使用标准库和现有 lib/ 模块
- **Business**: 不阻塞现有 CI 流水线，修改后所有检查脚本必须能立即正常运行
- **Dependencies**: 依赖已更新的 `lib/frontmatter.py`（已包含 `parse_frontmatter_unified()`）

## Assumptions
- `parse_frontmatter_unified()` 已正确实现并通过测试（已存在 test_frontmatter_unified.py）
- 角色文件（.agents/roles/*.md）短期内仍使用 TOML 格式（包含 [permissions] 表），但 parse_frontmatter_unified() 仍能解析其标量字段
- docs/knowledge/scripts/generate_index.py 可以通过 sys.path 正确导入项目的 lib.frontmatter 模块
- 现有测试文件中已包含 frontmatter 相关的测试用例，修改后能直接验证正确性

## Acceptance Criteria

### AC-1: lib/patterns.py 正确解析两种格式
- **Given**: 存在 TOML 格式和 YAML+x-toml-ref 格式的模式文件
- **When**: 调用 `parse_pattern_frontmatter()` 和 `scan_patterns()`
- **Then**: 两种格式的文件都能被正确解析，返回的字段字典包含所有必要字段（id/domain/layer/maturity/validation_count/reuse_count 等）
- **Verification**: `programmatic`

### AC-2: check-pattern-quality.py 检查结果一致
- **Given**: 同一批模式文件（TOML 格式）
- **When**: 分别运行修改前后的 check-pattern-quality.py
- **Then**: 检查结果（通过/失败/警告数量、评分）与修改前一致
- **Verification**: `programmatic`

### AC-3: docgen.py 看板生成正常
- **Given**: .trae/specs/ 目录下的 Spec 文件
- **When**: 运行 `python docgen.py dashboard`
- **Then**: 能正确解析所有 tasks.md 的 frontmatter，生成正确的进度看板
- **Verification**: `programmatic`

### AC-4: 现有测试套件全部通过
- **Given**: 修改完成后的代码
- **When**: 运行 pytest 测试套件（test_patterns.py、test_docgen.py、test_frontmatter.py 等）
- **Then**: 所有测试通过，无失败、无错误
- **Verification**: `programmatic`

### AC-5: 冒烟测试验证 TOML 格式正常工作
- **Given**: 项目当前的 TOML frontmatter 文件
- **When**: 依次运行 check-pattern-quality.py、pattern-maturity.py stats、docgen.py dashboard、check-source-traceability.py
- **Then**: 所有脚本正常运行，无异常退出，输出合理结果
- **Verification**: `programmatic`

### AC-6: roles.py 角色权限检查正常
- **Given**: .agents/roles/ 目录下的角色文件
- **When**: 运行角色权限检查
- **Then**: 能正确解析 tier 和 [permissions] 表，输出与修改前一致
- **Verification**: `programmatic`

### AC-7: generate_index.py 知识库索引生成正常
- **Given**: docs/knowledge/ 目录下的知识文件
- **When**: 运行 generate_index.py
- **Then**: 能正确解析 YAML frontmatter，生成正确的 README.md 索引
- **Verification**: `programmatic`

## Open Questions
- [ ] add-frontmatter.py 的 `has_frontmatter()` 是否需要考虑 x-toml-ref 引用的外部文件？（当前 parse_frontmatter_unified() 会自动处理，无需额外逻辑）
- [ ] lib/checks/roles.py 中的 [permissions] TOML 表解析：角色文件是否会在本次迁移中转换为 YAML 格式？如果会，需要调整解析逻辑；如果不会，保持现有解析方式即可（标量字段通过 parse_frontmatter_unified 获取，[permissions] 表保留正则解析）
