# 修复验收检查清单

## 代码修改检查

- [ ] false-positive-rules.toml 的 line_filters.patterns 已添加nosec正则
- [ ] test_mp_forkserver_validation.py 中lock.acquire()行已添加nosec注释
- [ ] sensitive_info.py 的 DEFAULT_EXCLUDE_DIRS 已包含.cache
- [ ] false-positive-rules.toml 的 dir_names 已包含.cache
- [ ] article-content.md 中真实手机号已脱敏
- [ ] 没有引入新的语法错误
- [ ] 没有修改无关文件

## 功能验证

- [ ] check-concurrent-safety.py --fail-on-error 返回退出码0
- [ ] check-sensitive-info.py 无error级问题（手机号泄露等）
- [ ] onnx_adaround pytest全部通过
- [ ] onnx_adaround ruff check无错误
- [ ] workflow yamllint语法检查通过

## 回归验证

- [ ] 其他扫描器（check-hardcode等）仍然正常工作
- [ ] nosec标记在其他误报场景也能正常工作
- [ ] 排除.cache目录不影响其他路径扫描
- [ ] 没有误排除合法的源码目录
