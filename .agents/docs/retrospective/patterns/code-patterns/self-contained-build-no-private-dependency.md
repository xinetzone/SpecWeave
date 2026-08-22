---
id: "self-contained-build-no-private-dependency"
title: "自包含构建链路：公开项目不耦合个人私域依赖"
type: code-pattern
date: 2026-08-20
maturity: L1
maturity_note: "单案例验证（mystx Sphinx 主题库文档构建耦合 taolib），待第二独立案例升级 L2"
source: "playground/reports/mystx-analysis-20260820/02-insights.md#洞察-i-5"
related_patterns:
  - "python-implicit-dependency-detection.md"
  - "../methodology-patterns/governance-strategy/four-negatives-external-dependency.md"
  - "../methodology-patterns/governance-strategy/docker-canonical-build-environment.md"
tags: ["build-reproducibility", "self-containment", "private-dependency", "documentation-build", "governance", "open-source"]
validation_count: 1
reuse_count: 0
---

# 自包含构建链路：公开项目不耦合个人私域依赖

## 触发场景

- 一个面向社区/开源的公开仓库，其构建、打包或文档构建链路 `import`/调用了作者**个人私有库/私有工具/私域资产**
- 该私有依赖仅出现在 `dev`/`doc` 等 optional 分组中，或指向非公共索引、无版本锁定、无公开文档
- 外部贡献者 clone 仓库后无法用标准命令（`pip install -e '.[doc]'` / `sphinx-build` 等）复现构建或文档
- 私有依赖不在公共索引、或其 API 变更时，文档 CI / 构建链路会整体断裂

**识别信号**：
- 构建入口（`tasks.py`、`Makefile`、`conf.py`、`noxfile.py`、CI 脚本）顶部 `import` 某个非公共包或作者私人命名空间包（如 `taolib.*`）
- 该依赖在 `pyproject.toml` 中仅列于 extras，但无法在公共 PyPI/conda-forge 检索到（或需私有源）
- 全新环境（干净容器/CI 镜像）构建失败，而作者本机正常

**不适用场景**：
- 纯个人项目、单人维护、无外部贡献者 → 容忍度较高，可延后处理
- 私有依赖已发布到公共索引、锁定版本、有公开文档 → 属普通依赖治理，不算「私域耦合」

## 问题本质

公开项目构建链路的「可复现性」是协作前提。当构建链路绑定作者个人私有库时，构建能力就从「仓库自包含」退化为「作者本机专属」：

| 维度 | 自包含构建链路 | 耦合个人私域依赖 |
|------|--------------|----------------|
| 新贡献者复现 | ✅ `pip install -e '.[doc]'` 即可 | ❌ 缺 taolib 或私有源即断 |
| CI 稳定性 | ✅ 干净镜像可构建 | ❌ 私有库不在公共索引/API 变更即断 |
| 依赖可审计性 | ✅ 锁定版本、公开来源 | ❌ 私域资产不可审计 |

本模式与「零声明 vs 运行时强依赖」（见 [Python包隐式依赖检测模式](python-implicit-dependency-detection.md)）不同：taolib 是**已声明**（在 dev 分组中）的依赖，问题不在地下「没声明」，而在于它**对社区不可复现**——是个人的、私域的、非公开的。即：声明了依赖 ≠ 依赖可复现。

## 核心步骤

1. **识别私域依赖**：检查构建/文档入口（`tasks.py`、`conf.py`、`noxfile.py`、`Makefile`、CI 脚本）的 `import` 中，哪些指向作者私人命名空间（`taolib.*`、`xxx_utils`、`~/personal_lib` 等）或非公共索引的包。

2. **判定可复现性**：逐一检查该依赖是否（a）可从公共索引安装，（b）有锁定版本，（c）有公开文档/不再依赖作者本机状态。任一不满足即标记为「私域耦合」。

3. **内聚回仓库（首选）**：用标准/公开工具替换私有库能力。如文档构建用标准 `sphinx-build` 替换 `taolib.doc.sites`；把私有库中真正需要的少量逻辑（如 matplotlib 字体配置）内聚进 `doc/conf.py` 或本仓库的 `_static/`。

4. **公开化 + 锁版本（次选）**：若确需外部私有能力，将其发布到公共索引、写入公开依赖清单并锁定版本；否则 vendored 进本仓库并标注来源。

5. **以「干净环境复现」作门禁**：CI 用全新镜像（不带作者本机缓存）执行 `pip install -e '.[doc]' && sphinx-build`，仅当从零可复现才算通过。

## 反模式

- ❌ **把个人私有库硬编码进构建入口，却只丢进 `dev`/`doc` 分组**：表面「已声明」，实际社区装不上——声明掩盖了不可复现的本质。
- ❌ **依赖作者本机 `sys.path`/`PYTHONPATH`/全局安装才能跑**：另一个「我机器上能跑」的变体，构建可复现性为零。
- ❌ **私有库 API 变更后不在仓库锁版本**：CI 断在作者一次不经意的私有库改动上，外部贡献者无从排查。
- ❌ **只在本机验证文档构建通过就交差**：未在干净环境复现，无法证明「文档可复现」是对外能力而非第一方专属。

## 检验标准

- [ ] 全新环境（干净容器/CI 镜像）执行 `pip install -e '.[doc]'` 后文档构建成功
- [ ] 构建/文档入口无指向非公共索引或作者私人命名空间的硬依赖
- [ ] 所有构建依赖均有公开来源 + 锁定版本（或已 vendored 并标注来源）
- [ ] 文档 CI 在干净镜像中从零复现，而非依赖作者缓存

## 迁移示例

- **Docker 镜像构建**：基础镜像从私有 registry/作者自建镜像迁到公共镜像（`ubuntu`/`python`/`nvidia/cuda`），构建脚本不依赖作者个人 Docker Hub 账号下的私有镜像。
- **前端脚手架**：把作者私有的 `@scope/internal-cli` 构建工具替换为公开脚手架（`vite`/`cra`），或 vendored 进仓库并公开版本。
- **CI 脚本**：把依赖作者个人密钥/私有 API 的构建步骤改为公开可复现的等价流程，敏感信息走 secrets 而非硬编码私域逻辑。

## 验证来源

- **验证1：mystx Sphinx 主题库文档构建耦合 taolib**（2026-08-20）：文档构建入口 `tasks.py` import `taolib.doc.sites`、`doc/conf.py` import `taolib.plot.configs.matplotlib_font`，而 taolib 仅是 `dev` 分组中的普通依赖（作者个人私有库）。外部贡献者仅凭 `pip install .[doc]` 无法复现官方文档构建；taolib 不在公共索引或 API 变更时文档 CI 整体断裂。✅ 验证「声明了依赖 ≠ 依赖可复现」的核心命题，标记 L1。

## 关联模式

- [python-implicit-dependency-detection.md](python-implicit-dependency-detection.md)：Python包隐式依赖检测（「零声明 vs 运行时强依赖」断层，本模式是其「声明了但不可复现」的互补情形）
- [four-negatives-external-dependency.md](../methodology-patterns/governance-strategy/four-negatives-external-dependency.md)：外部依赖四不原则（vendor/第三方依赖治理的上位框架）
- [docker-canonical-build-environment.md](../methodology-patterns/governance-strategy/docker-canonical-build-environment.md)：Docker 作为规范构建环境（构建可复现性的黄金标准实现手段）

## Changelog

- **2026-08-20** (v1.0.0): 初始版本，从 mystx 主题库分析报告 I-5（文档构建链路强耦合个人私有库 taolib）萃取，单案例验证，标记 L1。