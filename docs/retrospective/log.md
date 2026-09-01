# 变更日志

## 2026-09-01

- 复盘体系随文档中心统一迁移入本目录：patterns（849 文件，六类 + methodology-patterns 23 文件合并）、reports（1704 文件，22 类 + 5 个旧独有文件回补）、配套目录（archives/assets/concepts/frameworks/guides/templates）与根级复盘文件共 79 个，全部 git mv 保留历史；reports/concepts 旧副本 40 文件去重丢弃
- 门禁适配：pattern-maturity 扫描目标切换至 `docs/retrospective/patterns`，EXCLUDED_FILENAMES 增补 `index.md`/`log.md`（docgen 导航文件按 FM 规则禁 frontmatter），check 复跑 0 FAIL（327 通过）；version-ripple `--root docs/retrospective --bootstrap` 红错清零
- [cross-reference-ledger.md](cross-reference-ledger.md) 随迁入本目录：R3 冻结策略声明废止（由单文档中心迁移取代）、B1-B5 批次结项、基线 675/164 跨区引用随迁移自然消解
- 存量遗留：pattern-maturity 475 项成熟度警告、205 个目录缺 README、7 条 first-principles/llm-token-optimization 历史死链等，登记于 `.trae/specs/agents-docs-migration/mapping.md` §8

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- `index.md` 添加 `okf_version: "0.2"` frontmatter（原文件无 frontmatter）
- 保留正文内容，未做改写
- 单文件 Bundle，不创建 `concepts/` 或 `references/` 目录
