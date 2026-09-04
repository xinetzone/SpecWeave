# Bundles 自包含自洽化重构 - Verification Checklist

## 链接修复验证
- [ ] Checkpoint 1: 所有 `/concepts/` 开头的链接都带 `.md` 后缀（保留锚点）
- [ ] Checkpoint 2: 所有 `/examples/` 开头的链接都带 `.md` 后缀
- [ ] Checkpoint 3: 所有 `/references/` 开头的链接都带 `.md` 后缀
- [ ] Checkpoint 4: frontmatter 中 sources 字段的路径都带 `.md` 后缀
- [ ] Checkpoint 5: 代码块内的路径/URL 未被误伤修改

## 本地绝对路径清理验证
- [ ] Checkpoint 6: bundles 目录下无 `file:///` 开头的本地绝对路径
- [ ] Checkpoint 7: apache-tvm 的 facts-relax-te-topi.md 中无硬编码的 `d:/AI/` 路径
- [ ] Checkpoint 8: 清理后事实文档的可读性未受影响

## 重复文件清理验证
- [ ] Checkpoint 9: mobile-use 仅在根目录有 verification-report.md
- [ ] Checkpoint 10: okf-ecosystem 仅在根目录有 verification-report.md
- [ ] Checkpoint 11: veadk-python 仅在根目录有 verification-report.md
- [ ] Checkpoint 12: 无链接指向被删除的 references/verification-report.md

## 入口文件验证
- [ ] Checkpoint 13: bundles/index.md 存在且格式正确
- [ ] Checkpoint 14: bundles/chaos/index.md 存在且列出所有 10 个 bundle
- [ ] Checkpoint 15: bundles/index.md 中的链接可正确导航到 chaos/index.md
- [ ] Checkpoint 16: chaos/index.md 中的每个 bundle 链接都可点击且带 .md 后缀
- [ ] Checkpoint 17: 入口文件的 frontmatter 格式规范（参考 tiktoken）

## 全量链接检查（质量门禁）
- [ ] Checkpoint 18: 运行 check-links.py 扫描 bundles 目录，broken_local = 0
- [ ] Checkpoint 19: check-links.py 显示 warning_local = 0（无目录链接）
- [ ] Checkpoint 20: check-links.py 显示 broken_frontmatter = 0
- [ ] Checkpoint 21: 从 bundles/index.md 出发可导航到每个 bundle 的 index.md
- [ ] Checkpoint 22: 每个 bundle 内部可导航到其 concepts/examples/references

## 自包含性验证
- [ ] Checkpoint 23: 所有本地链接目标都在 bundles/ 目录树内
- [ ] Checkpoint 24: 无链接指向 bundles/ 外部的本地文件路径（如 ../projects/、../vendor/）
- [ ] Checkpoint 25: 外部 HTTP/HTTPS 链接可保留（不受此限制）
- [ ] Checkpoint 26: laozi-lineage 和 english-grammar 的特殊结构未被破坏
- [ ] Checkpoint 27: 所有修改未改变知识包的正文内容（仅修复链接和元数据）
