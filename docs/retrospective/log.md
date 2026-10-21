# 变更日志

## 2026-10-19

- 新增复盘报告 [retrospective-containers-openkylin-wsl-pytest-20261019](reports/task-reports/retrospective-containers-openkylin-wsl-pytest-20261019.md)：`df35c4426`（C-I12 bind 源树 other 位门禁）在 `wsl -d openKylin-3.0` + `/mnt/ai`（drvfs 9p）约束下对 `apps/containers` 四成员补跑 pytest。四成员计数 shared `rc=0`（进度字符 86 passed / 20 skipped）、client `23 failed, 288 passed, 1 skipped`、offline-delivery `1 failed, 114 passed, 10 skipped`、jupyter-podman-rootless `4 passed`；23 例失败经异常类型普查定性为 20 例 `PermissionError [Errno 1]`（chmod）+ 3 例 `invoke.exceptions.Exit`（xauth 写失败上抛），0 例产品逻辑回归。核心结论：drvfs 权限位恒 `0o777` 使 `_wanted_bind_mode` 单调只加判定为幂等 no-op，四组前置均返回 `(0, 0)` 且零告警，`0700` 前置态与 symlink 语义不可构造 ⇒ **门禁生效/失败路径在该挂载结构性不可验证**，需在 ext4/Linux 宿主补跑。附带登记真实缺陷 `666ea563f` 产物—测试契约漂移（xmflow-cli Dockerfile）、`test_kernel_inherit.py` 在 `with` 块外写已关闭文件致该成员收集期 `ValueError`（任意宿主均不可运行）、`shared` 库硬编码 `/tmp/podman-system-service.log` 落盘点，以及 `client_core.py:527` `utcnow()` DeprecationWarning；收尾合规取证将 `/tmp` 两残留逐条 `git grep` 溯源到被测代码自身，确认我方写入全部落在 `/mnt/ai/.temp/wsl-*`。七概念复合链路 R→I→E→V→C，36 条事实/5 条洞察/1 个 L1 模式含 5 条反模式/V 四视角 14 攻击点/9 项行动。执行边界：未 commit、未 push、`apps/containers` 零改动
- 上述报告升级至 **r2（同日报修订，不删除 r1 结论，只做证伪替换 + 追加）**：新增「落点层」实验——在同一台机器上只把 pytest `--basetemp`/`TMPDIR` 与能力探针从 `/mnt/ai`（9p）迁到 openKylin 发行版 ext4，源码树、解释器、依赖、日志一律不动，使落点成为唯一自变量。结果：9p 探针三项 `rc=1` vs ext4 三项 `rc=0`（同机对照）；client 由 `23 failed, 288 passed` 变为 `311 passed / 1 skipped / 0 failed`（`288+23=311` 逐条对账）、耗时 `821.17s → 93.17s`；C-I12 门禁 `test_bind_permissions.py` 13 项在 ext4 全绿（含正向提权、软链跳过、`failure_budget` 早退、W-I19 告警四条 r1 判定「结构性不可覆盖」的分支）；shared 缺统计行的**机制查明**为 `pyproject.toml` 的 `addopts = "-q"` 与命令行 `-q` 叠加至 verbosity −2（非「输出丢失」，r1 该解释被证伪并替换），去掉命令行 `-q` 复跑自报 `86 passed, 20 skipped` 与进度字符计数逐项吻合。r1 拒绝的攻击点「应改用 ext4 家目录跑测试」在 r2 被采纳并登记为**受控偏差**（落点清单化 + A-10 细化规格条款），与 r1 的纪律性拒绝不矛盾。契约漂移归因由推断升级为计数：`git log --reverse` 分钟级时序 + pickaxe + `git show <c>:<path>` blob 级核验三重锁定引入点为 `666ea563f`（2026-10-10 15:17，perf 改 bind-mount），期望串出生提交为 `895260096`（同日 11:06），HEAD 仍 `COPY_glob=0` 即至今未修；该提交自带注释「保持 `xmnn-*.whl` 通配契约不变」，揭示运行期通配契约与构建指令文本契约同名不同义。计数刷新：G1 事实 36 → **54** 条、V 攻击点校正为 **11**（r1 九 + r2 复核二，采纳 4 项修正）、G4 行动 9 → **10** 项；A-01 由「待外部执行」改为「basetemp 落点维度已结项 + 残余（源码树仍在 9p 的端到端形态待原生 Linux 复核）」。执行边界不变：未 commit、未 push、产品代码零改动；ext4 残留 `pytest-r3/r4/r5`（252K/212K/16M）已在 A-08 登记清理入口并待人工确认

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
