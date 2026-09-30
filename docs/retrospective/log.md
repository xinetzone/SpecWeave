# 变更日志

## 2026-09-29

- 新增复盘报告 [retrospective-openkylin-wsl-install-sparse-20260929](reports/task-reports/retrospective-openkylin-wsl-install-sparse-20260929/index.md)：openKylin 3.0 WSL 导入四次失败（E_UNEXPECTED×3 / CreateVm E_ABORT×1）的内存因素排障与 8 秒成功路径，及稀疏 VHD 被安全策略拦截后 `--allow-unsafe` 启用的风险决策；七概念复合链路 R→I→E→V→C，29 条事实/4 条洞察/1 个模式文件含 2 个子模式；V 阶段独立审查 18 条意见（P0×1/P1×5 已全修复）
- 新增代码模式 [wsl-import-memory-triage-sparse-vhd](patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md)（L1）：非确定性导入失败的内存分诊法 + 稀疏 VHD 双问题决策法；为既有 wsl-distro-install-migration-guide 的排障与磁盘空间维度增量
- 关联教程 `docs/knowledge/tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md` 落知识中心（2026-09-29 由 `docs/knowledge/tech/openkylin/` 合并迁入），与 openKylin 调研报告 §7.2/§8 局限 5 建立互链（补上"WSL 试用路径未实测"缺口）
- openKylin 调研报告 §4 两模式独立化入方法论模式库（product-growth）：[root-community-commercial-distro-flywheel](patterns/methodology-patterns/product-growth/root-community-commercial-distro-flywheel.md)（L2，根社区—商业发行版双轮，四案例证据分级）与 [agent-native-os-capability-ladder](patterns/methodology-patterns/product-growth/agent-native-os-capability-ladder.md)（L1，终端 OS 智能体原生化四级演进）；源报告 §4 降级为摘要+链接，G3 门标注独立化

## 2026-09-01

- 复盘体系随文档中心统一迁移入本目录：patterns（849 文件，六类 + methodology-patterns 23 文件合并）、reports（1704 文件，22 类 + 5 个旧独有文件回补）、配套目录（archives/assets/concepts/frameworks/guides/templates）与根级复盘文件共 79 个，全部 git mv 保留历史；reports/concepts 旧副本 40 文件去重丢弃
- 门禁适配：pattern-maturity 扫描目标切换至 `docs/retrospective/patterns`，EXCLUDED_FILENAMES 增补 `index.md`/`log.md`（docgen 导航文件按 FM 规则禁 frontmatter），check 复跑 0 FAIL（327 通过）；version-ripple `--root docs/retrospective --bootstrap` 红错清零
- [cross-reference-ledger.md](cross-reference-ledger.md) 随迁入本目录：R3 冻结策略声明废止（由单文档中心迁移取代）、B1-B5 批次结项、基线 675/164 跨区引用随迁移自然消解
- 存量遗留：pattern-maturity 475 项成熟度警告、205 个目录缺 README、7 条 first-principles/llm-token-optimization 历史死链等，登记于 `.trae/specs/docs-restructure/agents-docs-migration/mapping.md` §8

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- `index.md` 添加 `okf_version: "0.2"` frontmatter（原文件无 frontmatter）
- 保留正文内容，未做改写
- 单文件 Bundle，不创建 `concepts/` 或 `references/` 目录
