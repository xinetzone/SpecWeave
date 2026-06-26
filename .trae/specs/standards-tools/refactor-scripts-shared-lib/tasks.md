# Tasks

- [x] Task 1: 创建 `lib/markdown.py` 共享模块
  - [x] SubTask 1.1: 实现 `find_markdown_files(root, exclude_dirs=None)` 函数，使用 `constants.EXCLUDED_DIRS` 默认排除目录，支持调用方传入额外排除目录
  - [x] SubTask 1.2: 实现 `extract_title(path)` 和 `extract_description(path)` 函数，提取首个 `#` 标题和描述文本
  - [x] SubTask 1.3: 实现 `parse_inline_links(content)` 函数，复用 `lib.link_fixer.INLINE_LINK_RE` 正则
  - [x] SubTask 1.4: 实现 `update_marker_region(file_path, marker_start, marker_end, new_content)` 函数，处理 HTML 注释标记区内容替换
  - [x] SubTask 1.5: 添加模块 docstring 和函数文档，编写单元测试

- [x] Task 2: 迁移 9 个脚本使用 `resolve_project_root`
  - [x] SubTask 2.1: 迁移 check-gitignore.py、check-vendor.py、check-filename-convention.py、check-action-items.py
  - [x] SubTask 2.2: 迁移 check-source-traceability.py、generate-apps-index.py、generate-dashboard.py、generate-nav.py
  - [x] SubTask 2.3: 迁移 check-retrospective-index.py，移除复制的 `resolve_project_root` fallback 实现

- [x] Task 3: 迁移 5 个脚本使用 `lib.frontmatter`
  - [x] SubTask 3.1: 迁移 check-source-traceability.py，移除自建 `FRONTMATTER_RE` 和 `SOURCE_FIELD_RE`
  - [x] SubTask 3.2: 迁移 check-atomization-coverage.py，移除自建 `FRONTMATTER_RE`
  - [x] SubTask 3.3: 迁移 pattern-maturity-stats.py，移除自建 `parse_frontmatter()`，统一使用 pathlib 风格
  - [x] SubTask 3.4: 迁移 verify-atomization.py，移除自建 `TOML_ID_RE`、`ID_RE`、`MATURITY_RE`、`SOURCE_RE` 正则
  - [x] SubTask 3.5: 迁移 check-atomization-duplication.py 的 `MATURITY_RE`，改用 `extract_frontmatter_field`

- [x] Task 4: 迁移 3 个脚本使用 `lib.link_fixer.INLINE_LINK_RE`
  - [x] SubTask 4.1: 迁移 check-move.py、check-links.py、build-ref-index.py，移除重定义的正则常量

- [x] Task 5: 迁移 10+ 脚本使用 `lib.cli` 输出与参数
  - [x] SubTask 5.1: 迁移 check-gitignore.py、check-vendor.py、generate-apps-index.py、generate-nav.py、generate-dashboard.py、pattern-maturity-stats.py 的 `print("=" * 60)` 为 `print_header`
  - [x] SubTask 5.2: 迁移 check-source-traceability.py、check-report-categorization.py、check-links.py、check-mermaid.py 的手写 `--json`/`--path` 参数为 `add_common_args`

- [x] Task 6: 提取 `discover_spec_dirs` 到 `lib/spec/`
  - [x] SubTask 6.1: 在 `lib/spec/` 中实现 `discover_spec_dirs(project_root)` 函数
  - [x] SubTask 6.2: 迁移 check-spec-consistency.py 和 generate-tests.py 使用共享实现
  - [x] SubTask 6.3: 更新 `lib/spec/__init__.py` 导出

- [x] Task 7: 重构 check-spec-consistency.py 内部重复
  - [x] SubTask 7.1: 提取 `run_spec_checks(spec_dir, project_root, match_threshold)` 共享函数
  - [x] SubTask 7.2: 重构 main() JSON 批量分支和 check_single_spec() 共用同一检查逻辑

- [x] Task 8: 统一 `EXCLUDED_DIRS` 常量引用
  - [x] SubTask 8.1: 迁移 check-filename-convention.py 和 check-vendor.py 的本地重定义为从 `constants` 引入

- [x] Task 9: 更新 `lib/__init__.py` 导出新模块
  - [x] SubTask 9.1: 导出 `lib.markdown` 模块及其公共函数
  - [x] SubTask 9.2: 更新 `__all__` 列表

- [x] Task 10: 全量功能验证
  - [x] SubTask 10.1: 验证所有 check-*.py 脚本的 `--help` 输出正常
  - [x] SubTask 10.2: 验证所有 generate-*.py 脚本的 `--help` 输出正常
  - [x] SubTask 10.3: 对实际 spec 目录运行 check-spec-consistency.py 和 check-spec-format.py，确认结果与重构前一致
  - [x] SubTask 10.4: 运行 ci-check.ps1 综合检查，确认无回归

# Task Dependencies

- [Task 2] ~ [Task 5] 依赖 [Task 1]（需要 lib/markdown.py 提供的共享函数）
- [Task 7] 依赖 [Task 6]（discover_spec_dirs 已提取后重构 check-spec-consistency）
- [Task 9] 依赖 [Task 1] 和 [Task 6]
- [Task 10] 依赖所有其他任务完成
- [Task 2]、[Task 3]、[Task 4]、[Task 5]、[Task 8] 互相独立，可并行执行
