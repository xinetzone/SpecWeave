# CI工作流失败修复Spec

## 背景

用户要求修复6个GitHub Actions工作流失败，使用seven-concepts-cmd方法论进行系统性分析和修复。

## 失败工作流列表

1. **devcontainer-variants.yml** (run 31982082346) - 0s完成
2. **onnx-quantize-ci.yml** (run 31982081648) - 0s完成
3. **concurrent-safety-scan.yml** - CC-TIMEOUT ERROR
4. **onnx-adaround-ci.yml** - 本地验证通过，之前环境问题
5. **sensitive-info-scan.yml** - 扫描.cache目录和真实手机号
6. **daily-stats-update.yml** - 最新run已成功

## 问题根因分析（I阶段）

### 问题1：concurrent-safety-scan 失败（CC-TIMEOUT ERROR）

**现象**：
```
文件: tests\test_error_tolerance.py 第 64 行
代码: lock.acquire()
错误码: CC-TIMEOUT
消息: 锁操作 acquire() 未设置timeout，可能导致死锁
```

**本质**：
- 扫描器报告的文件名有误，实际文件是 `tests/test_mp_forkserver_validation.py`
- 这是**测试代码**，`_thread_that_holds_lock()` 函数的目的是**故意持有锁**来演示fork()在多线程场景下的死锁问题，这是测试用例的预期行为，不是生产代码的bug
- 扫描器目前通过 `rules_engine.is_excluded_line()` 支持行级过滤，但 `false-positive-rules.toml` 的 `line_filters.patterns` 中没有nosec标记匹配
- concurrent safety扫描器缺少对nosec/sensitive-ignore标记的原生支持（虽然sensitive_info扫描器有自己的实现）

**根因**：
1. false-positive-rules.toml的line_filters中没有添加nosec标记正则
2. 测试代码中需要标记为故意忽略的行没有添加nosec注释

---

### 问题2：sensitive-info-scan 失败

**现象**：扫描发现大量手机号误报，以及一个真实手机号需要脱敏

**本质**：
1. `.cache` 目录（GitHub Actions缓存目录，包含Miniconda安装包等下载文件）没有被排除
2. `docs/knowledge/learning/analyze-wechat-article-ai-switch-governance/article-content.md` 中包含真实手机号 `13269078023` 需要脱敏

**根因**：
1. `sensitive_info.py` 的 `DEFAULT_EXCLUDE_DIRS` 和 `false-positive-rules.toml` 的 `path_exclusions.dir_names` 缺少 `.cache` 目录
2. 文档中存在未脱敏的真实手机号

---

### 问题3：devcontainer-variants.yml 和 onnx-quantize-ci.yml 0s完成

**现象**：这两个工作流在文档修改的commit上运行，0s完成并显示失败

**分析**：
- 检查workflow配置，它们都有正确的 `paths` 过滤规则：
  - devcontainer-variants.yml: 触发路径为 `.devcontainer/`, `Dockerfile*`, `.github/workflows/devcontainer-*`
  - onnx-quantize-ci.yml: 触发路径为 `apps/tests/onnx_quantize/**`, `.github/workflows/onnx-quantize-ci.yml`
- 失败commit "docs(index): 添加GitHub项目徽章增强文档中心首页展示" 只修改了 `docs/index.md`
- GitHub Actions中，当commit不匹配paths过滤时，workflow应该显示为 **skipped**（灰色），而非failure
- 可能原因：需要验证是否是workflow语法错误，或者是GitHub UI显示问题

---

### 问题4：onnx-adaround-ci.yml

**本地验证结果**：
- pytest: 59 passed ✅
- ruff lint: All checks passed! ✅
- zero-torch检查：未发现torch导入 ✅

**结论**：本地测试全部通过，之前的失败可能是临时环境问题或已修复，不需要代码修改

---

### 问题5：daily-stats-update.yml

**最新状态**：run 31983012169 (2026-08-17) 状态为success ✅

**结论**：已自动恢复，不需要修复

## 修复方案（F阶段）

### 修复1：统一nosec标记支持（concurrent safety扫描）

**文件**：`.agents/scripts/config/false-positive-rules.toml`

**修改**：在 `[line_filters].patterns` 中添加nosec标记正则，与sensitive_info的 `_has_nosec_marker` 保持一致：
- 支持多种注释格式：`# nosec`, `// nosec`, `/* nosec */`, `<!-- nosec -->`, `%% nosec`, `-- nosec`
- 同时支持 `sensitive-ignore` 别名

**文件**：`.agents/scripts/tests/test_mp_forkserver_validation.py`

**修改**：在第64行 `lock.acquire()` 后添加 `# nosec: 测试用例故意持有锁验证fork死锁` 注释

---

### 修复2：敏感信息扫描排除.cache目录

**文件**：`.agents/scripts/lib/check_sensitive_info/sensitive_info.py`

**修改**：在 `DEFAULT_EXCLUDE_DIRS` 中添加 `.cache`

**文件**：`.agents/scripts/config/false-positive-rules.toml`

**修改**：在 `path_exclusions.dir_names` 中添加 `.cache`

---

### 修复3：真实手机号脱敏

**文件**：`docs/knowledge/learning/analyze-wechat-article-ai-switch-governance/article-content.md`

**修改**：使用扫描器的自动脱敏功能，将真实手机号 `13269078023` 脱敏为 `132****8023`

---

### 修复4：验证0s工作流问题

**方案**：检查workflow语法是否正确，确认paths过滤配置无误

## 验收标准

1. `python .agents/scripts/check-concurrent-safety.py --fail-on-error` 返回0退出码
2. `python .agents/scripts/check-sensitive-info.py --scan-root . --auto-redact` 返回0退出码（或只显示info，无error）
3. 本地运行所有相关检查脚本无报错
4. 确认workflow配置语法正确
5. 不破坏现有功能（onnx-adaround测试仍然通过，其他扫描器正常工作）

## 风险评估

- **低风险**：配置文件修改和添加注释，不影响核心逻辑
- **中风险**：修改敏感信息扫描的排除目录，需要确保不会漏扫真实敏感信息（.cache是临时缓存目录，不包含项目源码）
- **测试验证**：所有修复需要本地运行验证通过
