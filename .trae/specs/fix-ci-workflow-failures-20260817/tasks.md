# 修复任务清单

## 任务1：添加nosec标记支持到false-positive规则

- **文件**：`.agents/scripts/config/false-positive-rules.toml`
- **操作**：在 `[line_filters].patterns` 中添加nosec和sensitive-ignore标记的正则表达式，支持多种注释格式
- **验证**：确认concurrent safety扫描器通过is_excluded_line()能识别nosec标记
- **优先级**：高

---

## 任务2：给测试代码添加nosec注释

- **文件**：`.agents/scripts/tests/test_mp_forkserver_validation.py`
- **操作**：在第64行 `lock.acquire()` 后添加 `# nosec: 测试用例故意持有锁验证fork死锁` 注释
- **验证**：运行 `python .agents/scripts/check-concurrent-safety.py --fail-on-error` 确认不再报CC-TIMEOUT错误
- **优先级**：高

---

## 任务3：敏感信息扫描排除.cache目录

- **文件**：
  1. `.agents/scripts/lib/check_sensitive_info/sensitive_info.py`
  2. `.agents/scripts/config/false-positive-rules.toml`
- **操作**：
  1. 在 `DEFAULT_EXCLUDE_DIRS` 集合中添加 `.cache`
  2. 在 `path_exclusions.dir_names` 数组中添加 `.cache`
- **验证**：运行敏感信息扫描，确认不再扫描.cache目录下的文件
- **优先级**：高

---

## 任务4：脱敏文档中的真实手机号

- **文件**：`docs/knowledge/learning/analyze-wechat-article-ai-switch-governance/article-content.md`
- **操作**：运行自动脱敏命令或手动将手机号 `13269078023` 替换为 `132****8023`
- **验证**：运行敏感信息扫描，确认没有error级别的手机号泄露
- **优先级**：高

---

## 任务5：验证0s完成的workflow配置

- **文件**：
  1. `.github/workflows/devcontainer-variants.yml`
  2. `.github/workflows/onnx-quantize-ci.yml`
- **操作**：检查workflow语法是否正确，paths过滤配置是否合理
- **验证**：使用GitHub CLI或本地yamllint验证语法
- **优先级**：中

---

## 任务6：本地全量验证

- **操作**：运行所有相关检查脚本
  ```bash
  python .agents/scripts/check-concurrent-safety.py --fail-on-error
  python .agents/scripts/check-sensitive-info.py --scan-root .
  cd apps/tests/onnx_adaround && pytest && ruff check .
  ```
- **预期结果**：所有检查通过或只有info/warn级别的提示
- **优先级**：高
