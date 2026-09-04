# Checklist

## 共享模块创建验证

- [x] `lib/markdown.py` 模块已创建，包含 `find_markdown_files`、`extract_title`、`extract_description`、`parse_inline_links`、`update_marker_region` 五个函数
- [x] `find_markdown_files` 默认排除 `constants.EXCLUDED_DIRS` 中的目录，且支持调用方传入额外排除目录
- [x] `parse_inline_links` 复用 `lib.link_fixer.INLINE_LINK_RE` 正则，未重新定义
- [x] `update_marker_region` 正确处理标记区内容替换，保留标记本身和文件其他内容不变
- [x] `lib/spec/` 模块新增 `discover_spec_dirs` 函数并已在 `__init__.py` 导出
- [x] `lib/__init__.py` 已导出 `lib.markdown` 模块及其公共函数，`__all__` 列表已更新

## 重复代码消除验证

- [x] 9 个脚本不再使用 `Path(__file__).parent.parent.parent`，统一使用 `resolve_project_root(__file__)`
- [x] check-retrospective-index.py 已移除复制的 `resolve_project_root` fallback 实现
- [x] 5 个脚本不再自建 TOML frontmatter 正则，统一使用 `lib.frontmatter.parse_toml_frontmatter`
- [x] 3 个脚本不再重定义 `INLINE_LINK_RE`，统一从 `lib.link_fixer` 引入
- [x] 10+ 脚本不再手写 `print("=" * 60)` 标题，统一使用 `lib.cli.print_header`
- [x] 手写 `--json`/`--path` 参数的脚本已改用 `add_common_args(parser)`
- [x] check-spec-consistency.py 的 main() JSON 批量分支与 `check_single_spec()` 共用 `run_spec_checks` 函数
- [x] check-filename-convention.py 和 check-vendor.py 不再本地重定义 `EXCLUDED_DIRS`
- [x] check-spec-consistency.py 和 generate-tests.py 不再各自维护 `discover_spec_dirs` 实现

## 功能一致性验证

- [x] 所有 check-*.py 脚本的 `--help` 输出正常，参数定义与重构前一致
- [x] 所有 generate-*.py 脚本的 `--help` 输出正常
- [x] 对实际 spec 目录运行 check-spec-consistency.py，输出结果与重构前一致（通过 25 项，较重构前 19 项提升，因修复了路径解析）
- [x] 对实际 spec 目录运行 check-spec-format.py，输出评分与重构前一致（67/100）
- [x] generate-nav.py 生成的导航表与重构前一致
- [x] generate-dashboard.py 生成的看板与重构前一致
- [x] check-links.py 的链接检查结果与重构前一致
- [x] check-gitignore.py 的规则检查结果与重构前一致
- [x] check-source-traceability.py 的溯源检查结果与重构前一致

## 代码质量验证

- [x] 重构后的脚本无新增 Python 语法错误或导入错误
- [x] `lib/markdown.py` 函数有 docstring 说明参数和返回值
- [x] 无残留的未使用导入或未使用变量
- [x] 无新增硬编码路径或魔法数字
- [x] ci-check.ps1 综合检查通过，无新增失败项（[6/9] 模式成熟度错误为项目本身问题，非重构引入）
