# 脚本共享代码库重构 Spec

## Why

`.agents/scripts` 目录下约 30 个脚本中存在大量重复代码（约 280 行），多个脚本绕过已有的 `lib/` 共享模块自建实现相同逻辑。这不仅增加了维护成本，还导致目录结构调整时多处失效的风险——例如 9 个脚本硬编码 `Path(__file__).parent.parent.parent` 解析项目根目录，若目录层级变动将全部失效。提取重复代码为共享模块可一次性消除重复，提升可维护性与一致性。

## What Changes

- **新建 `lib/markdown.py` 模块**：提供 `find_markdown_files`（统一 5 处重复的目录遍历）、`extract_title`/`extract_description`（统一 3 处标题/描述提取）、`parse_inline_links`（统一 3 处链接解析）
- **新建标记区替换功能**：提供 `update_marker_region` 函数，统一 generate-apps-index、generate-nav、generate-dashboard 三个脚本的 HTML 标记区切片替换逻辑
- **提取 `discover_spec_dirs` 到 `lib/spec/`**：统一 check-spec-consistency 与 generate-tests 中完全相同的实现
- **批量迁移 9 个脚本使用 `resolve_project_root`**：替换硬编码 `Path(__file__).parent.parent.parent`
- **迁移 5 个脚本使用 `lib.frontmatter`**：替换自建的 TOML frontmatter 正则解析
- **迁移 3 个脚本使用 `lib.link_fixer.INLINE_LINK_RE`**：替换重定义的链接正则
- **迁移 10+ 脚本使用 `lib.cli`**：替换手写的 `print("=" * 60)` 标题和 `--json`/`--path` 参数
- **重构 check-spec-consistency.py 内部重复**：提取 `run_spec_checks` 共享函数，消除 main() JSON 批量分支与 check_single_spec() 的 80% 重复
- **统一 `EXCLUDED_DIRS` 常量**：消除本地重定义，从 `constants.py` 统一引用

## Impact

- 受影响脚本：约 20 个 `.agents/scripts/*.py` 文件
- 受影响共享库：`lib/__init__.py`、`lib/markdown.py`（新增）、`lib/spec/`（扩展）、`constants.py`
- 风险：重构涉及文件遍历、frontmatter 解析、输出格式化等核心路径，需确保功能完全一致
- 依赖：无外部依赖变更，仅内部模块重组

## ADDED Requirements

### Requirement: Markdown 文件处理模块

系统 SHALL 提供 `lib/markdown.py` 模块，封装 Markdown 文件遍历、标题/描述提取、内联链接解析等通用功能，供所有需要处理 Markdown 文件的脚本复用。

#### Scenario: 统一目录遍历

- **WHEN** 脚本需要遍历目录下所有 Markdown 文件
- **THEN** 调用 `find_markdown_files(root, exclude_dirs=None)` 返回 `Path` 列表，自动排除 `EXCLUDED_DIRS` 中列出的目录
- **AND** 支持调用方传入额外排除目录列表

#### Scenario: 标题与描述提取

- **WHEN** 脚本需要从 Markdown 文件提取首个标题和描述
- **THEN** 调用 `extract_title(path)` 返回首个 `#` 标题文本
- **AND** 调用 `extract_description(path)` 返回标题下的首行描述文本

#### Scenario: 内联链接解析

- **WHEN** 脚本需要从 Markdown 内容提取所有内联链接
- **THEN** 调用 `parse_inline_links(content)` 返回 `(text, url)` 元组列表，使用 `lib.link_fixer.INLINE_LINK_RE` 统一正则

### Requirement: 标记区替换功能

系统 SHALL 提供 `update_marker_region(file_path, marker_start, marker_end, new_content)` 函数，统一处理 HTML 注释标记包裹的动态内容替换。

#### Scenario: 标记区内容替换

- **WHEN** 脚本需要更新 Markdown 文件中 `<!-- MARKER_START -->` 与 `<!-- MARKER_END -->` 之间的内容
- **THEN** 调用 `update_marker_region` 完成切片拼接，保留标记本身和文件其他内容不变
- **AND** 若文件中未找到标记对，返回明确错误提示

### Requirement: Spec 目录发现函数共享

系统 SHALL 将 `discover_spec_dirs(project_root)` 提取到 `lib/spec/` 模块中，供所有需要扫描 spec 目录的脚本复用。

#### Scenario: 统一 spec 目录扫描

- **WHEN** 脚本需要发现项目中所有 spec 目录
- **THEN** 调用 `lib.spec.discover_spec_dirs(project_root)` 返回按名称排序的 `Path` 列表
- **AND** check-spec-consistency 与 generate-tests 不再各自维护相同实现

## MODIFIED Requirements

### Requirement: 项目根目录解析统一

所有脚本 SHALL 使用 `lib.project.resolve_project_root(__file__)` 解析项目根目录，禁止硬编码 `Path(__file__).parent.parent.parent` 等层级计算。

#### Scenario: 迁移硬编码路径解析

- **WHEN** 脚本需要获取项目根目录
- **THEN** 调用 `resolve_project_root(__file__)` 通过 AGENTS.md 锚点自适应定位
- **AND** 移除 check-retrospective-index.py 中复制的 `resolve_project_root` fallback 实现

### Requirement: TOML frontmatter 解析统一

所有需要解析 TOML frontmatter 的脚本 SHALL 使用 `lib.frontmatter.parse_toml_frontmatter` 和 `extract_frontmatter_field`，禁止自建正则表达式。

#### Scenario: 迁移自建 frontmatter 解析

- **WHEN** 脚本需要从 Markdown 文件提取 frontmatter 字段（如 `source`、`maturity`、`id`）
- **THEN** 调用 `parse_toml_frontmatter(content)` 获取字典后用 `extract_frontmatter_field(fm, field_name)` 提取
- **AND** 移除 check-source-traceability、check-atomization-coverage、pattern-maturity-stats、verify-atomization 中的自建正则

### Requirement: CLI 输出与参数统一

所有脚本 SHALL 使用 `lib.cli` 模块提供的输出函数和参数定义，禁止手写 `print("=" * 60)` 等标题格式或重复定义 `--json`/`--path` 参数。

#### Scenario: 统一输出格式

- **WHEN** 脚本需要输出标题、通过/警告/错误信息
- **THEN** 使用 `print_header`、`print_pass`、`print_warn`、`print_error`、`print_summary`
- **AND** 需要命令行参数时优先使用 `add_common_args(parser)` 注册通用参数

### Requirement: 内部重复逻辑消除

check-spec-consistency.py SHALL 提取共享检查函数，消除 main() JSON 批量分支与 `check_single_spec()` 的逻辑重复。

#### Scenario: 消除批量检查重复

- **WHEN** main() 需要批量执行 spec 检查并输出 JSON
- **THEN** 调用提取的 `run_spec_checks(spec_dir, project_root, match_threshold)` 获取检查结果字典
- **AND** `check_single_spec()` 与 JSON 批量分支共用同一检查逻辑

## REMOVED Requirements

（无移除需求，本 spec 为纯重构，不删除功能）
