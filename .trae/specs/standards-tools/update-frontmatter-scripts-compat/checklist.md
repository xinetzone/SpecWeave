---
version: 1.0
---

# Frontmatter 脚本兼容性更新 - Verification Checklist

## 代码修改验证
- [ ] lib/patterns.py 的 import 语句已更新，使用 parse_frontmatter_unified
- [ ] lib/patterns.py 的 parse_pattern_frontmatter() 函数正确使用统一入口，返回值结构不变
- [ ] lib/patterns.py 的 grep_maturity_per_directory() 函数正确使用统一入口
- [ ] check-pattern-quality.py 的 import 语句已更新
- [ ] check-pattern-quality.py 的 check_frontmatter() 函数参数改为 fields 字典，正确处理字符串/列表值
- [ ] check-pattern-quality.py 的错误消息不再硬编码"TOML frontmatter"
- [ ] docgen.py 的 import 语句已更新，移除未使用的导入
- [ ] docgen.py 已删除自定义的 YAML_FRONTMATTER_RE 和 _dash_parse_yaml_simple()
- [ ] docgen.py 的 _dash_scan_spec() 函数使用 parse_frontmatter_unified() 获取 status
- [ ] lib/checks/roles.py 的 import 语句已更新
- [ ] lib/checks/roles.py 的 _extract_tier() 改为从字典获取值
- [ ] lib/checks/roles.py 的 _validate_role_file() 使用 parse_frontmatter_unified() 并保留 [permissions] 正则解析
- [ ] add-frontmatter.py 的 has_frontmatter() 简化为使用 parse_frontmatter_unified()
- [ ] add-frontmatter.py 移除冗余的 YAML_FM_RE 正则
- [ ] docs/knowledge/scripts/generate_index.py 添加了正确的 sys.path 导入路径
- [ ] docs/knowledge/scripts/generate_index.py 使用 parse_frontmatter_unified() 替代自定义解析
- [ ] docs/knowledge/scripts/generate_index.py 保留了编码 fallback 和 DEFAULT_META 逻辑

## 类型安全与兼容性
- [ ] 所有使用 fields.get(key) 的地方都考虑了值可能是 list[str] 的情况
- [ ] 整数字段（validation_count、reuse_count）使用 str() 转换后再转 int
- [ ] 字段存在性检查使用 `key in dict` 或 `fields.get(key) is not None`
- [ ] 向后兼容：对现有 TOML frontmatter 文件，解析结果与修改前一致
- [ ] 向前兼容：对 YAML+x-toml-ref 格式，脚本能正确解析（代码逻辑支持）

## 测试验证
- [ ] test_patterns.py 全部通过
- [ ] test_docgen.py 全部通过
- [ ] test_frontmatter.py 全部通过
- [ ] test_frontmatter_unified.py 全部通过
- [ ] test_checks_roles.py 全部通过（如果存在）
- [ ] pytest 整体测试套件无回归
- [ ] 所有冒烟测试脚本运行无 Python 异常
- [ ] check-source-traceability.py 正常运行
- [ ] check-pattern-quality.py --score 正常运行
- [ ] pattern-maturity.py stats 正常运行
- [ ] docgen.py dashboard 正常运行
- [ ] docs/knowledge/scripts/generate_index.py 正常运行

## 代码质量
- [ ] 遵循现有代码风格（缩进、命名、导入顺序）
- [ ] 添加了必要的类型注解
- [ ] 没有引入未使用的导入
- [ ] 没有添加不必要的注释（遵循项目规范）
- [ ] 没有修改 frontmatter.py 和 migrate-frontmatter.py
- [ ] 没有修改 tests/ 目录下的文件
- [ ] 没有修改 mdi/ 目录下的文件
