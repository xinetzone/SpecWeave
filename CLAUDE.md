# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目性质

SpecWeave 不是可安装的软件，而是一套 **AI 智能体工作区规范体系**——以 `AGENTS.md` 为统一入口，提供角色定义、协作协议、质量门禁与自我演进机制的多智能体协作开放标准。仓库主体是 Markdown 规范文档、Sphinx 在线文档中心与 Python 验证脚本，而非应用代码。

## 四大顶层区域（修改权限差异极大，务必区分）

| 目录 | 性质 | 可否直接修改 |
|---|---|---|
| `.agents/` | AI 智能体规范容器（主权区） | ✅ 直接维护、纳入版本控制 |
| `apps/` | 主仓库内置应用工作空间 | ✅ 直接维护、纳入版本控制 |
| `projects/` | 第一方自有子项目 | ❌ git submodule，走子项目流程 |
| `vendor/` | 第三方依赖 | ❌ git submodule，**禁止本地修改**（只读引用） |

`apps/` 与 `projects/`/`vendor/` 有本质区别：前者的文件直接纳入主仓库版本控制；后两者通过 gitlink 追踪外部仓库引用，本地修改无法提交回主仓库。进入任一子区域前先读对应的 `AGENTS.md`（`apps/AGENTS.md`、`projects/AGENTS.md`、`vendor/AGENTS.md`），退出子区域后恢复 SpecWeave 主权区路由。

## 启动协议（最高优先级）

收到任何任务后，按 `AGENTS.md` 顶部的 PRIORITY ZERO 协议执行：①读 `AGENTS.md` 全文 → ②按上下文路由表（`.agents/context-routing.md`）定位需读取的规范 → ③完成内容敏感度预检（公开 vs 私域）→ ④自检 → ⑤在规范指导下选 Skill 执行。在完成步骤 1–3.5 之前不得加载 Skill 或生成产出物。即使工作目录不在 `vendor/` 内，也必须执行任务类型预检（步骤 2.0）。

## 常用命令

### 测试（Python 脚本验证套件）
```bash
# 全量测试（testpaths 已锁定 .agents/scripts/tests）
pytest
# 单个测试文件 / 单个用例
pytest .agents/scripts/tests/test_xxx.py
pytest .agents/scripts/tests/test_xxx.py::test_case_name
# 覆盖率（coverage source = .agents/scripts，配置见 pytest.ini）
pytest --cov
```

### 文档构建（Sphinx + MyST）
```bash
# 安装文档依赖
pip install -r docs/requirements.txt
# 构建 HTML（Sphinx 配置在 docs/conf.py，入口 master_doc = index）
sphinx-build -b html docs docs/_build/html
```
在线文档发布由 Read the Docs（`.readthedocs.yml`，Python 3.13）自动构建，本地一般无需手动发布。`docs/_config.toml` 仅承载 `html_theme_options`，由 `docs/conf.py` 用 `tomllib` 读取。

### 提交前验证脚本
```bash
python .agents/scripts/check-gitignore.py                      # .gitignore 完整性
python .agents/scripts/check-links.py --path <变更目录>         # Markdown 相对路径断链 / file:/// 检查
python .agents/scripts/check-pwsh7-compliance.py               # Windows .ps1 必须 pwsh 7.4+ 合规
python check_mermaid.py                                         # Mermaid 图表校验
```
Windows 平台所有 `.ps1` 脚本必须用 PowerShell 7.4+（pwsh7）执行，禁止 Windows PowerShell 5.1；`vendor/`、`projects/` 豁免。

### build.sh（仅特定 app 的 Docker/Nuitka 构建）
根目录 `build.sh` 是 `apps/` 下 vta-dev 镜像（Nuitka 编译 xmnn wheel + 运行时镜像）的构建脚本，**不是仓库主构建入口**。日常规范与文档工作不涉及它。

## 文档体系边界（极易踩坑）

- **根 `docs/`**：唯一文档中心（OKF v0.2，Sphinx 构建），面向人类读者与外部消费，承载 Wiki 教程、知识包、复盘报告、模式库与最佳实践。新增对外可读文档一律入此。
- **`AGENTS.md`/`.agents/`**：面向 AI 智能体的规范与执行资产（角色、规则、协议、工作流、脚本、技能、模板），不再包含 `docs/` 子树（2026-08-31 起 `.agents/docs/` 已整体迁入根 `docs/`）。
- **路径解析**：一律以文件/目录实际位置为准使用相对路径，**禁止沿用 "docs/ 自动解析为 .agents/docs/" 的历史隐式规则**。`.agents/` 内引用根 `docs/` 用 `../docs/...`；仓库根文件引用 `docs/` 用 `docs/...`。

## 内容敏感度分流

任务启动时判定内容级别（步骤 2.3）：
- **公开内容**（公开网页/开源代码/官方文档）→ 标准工作流，规划在 `.trae/specs/<theme-subdir>/`，产出物入根 `docs/`。
- **私域内容**（内部会议、带 `share?code=`/`token=` 的私域链接、个人笔记、商业培训）→ 跳过 `.trae/specs/`，产出物直接入 `playground/` 或用户指定目录；**就高不就低**，不确定默认按私域处理。

## 开发规范要点

- **提交规范**：Conventional Commits（`type(scope): subject`），主体用**中文**描述；修复类提交须标注预防措施类型。分支命名 `type/brief-description`。
- **新增脚本**：写入 `.agents/scripts/` 前先查阅 `.agents/scripts/lib/README.md` 共享库，禁止重复实现已有功能。
- **派生产物溯源**：YAML/TOML frontmatter 须携带 `source` 字段标注来源。
- **Mermaid 优先**：流程/架构/关系/状态机优先用 Mermaid，遵循安全编码六规则（见 `.agents/docs/development-standards.md`）。
- **修复即闭环**：Bug 修复遵循「修复→预防→闭环」三阶段 SOP，禁止纯点修复（平凡修复可豁免）；三阶段递进顺序不可颠倒。
- **测试覆盖率**：单元测试不低于 80%，关键模块不低于 90%。
- **禁止提交临时依赖**：`.temp/`、`__pycache__/`、`.venv/`、`node_modules/` 等不得入库。

## 知识可信度分级（概念类查询按级取材）

1. **最高可信度**：`projects/awesome-okf-xs/doc/bundles/`（OKF 知识包库，10 域/28 组/248 包）——概念、术语、技术事实的冲突裁决依据，**只读引用**（位于 git submodule 内，不得修改）。
2. **二级**：`docs/knowledge/` 技术知识库与 `docs/retrospective/` 复盘模式库。冲突时以 bundles 为准并注明裁决来源；bundles 未覆盖则回退二级，不因缺失而中断。

## 核心入口索引

- `AGENTS.md` — 智能体最高优先级入口与上下文路由
- `.agents/context-routing.md` — 任务类型→必读规范映射表
- `.agents/global-core-rules.md` — 全局核心规则（启动协议、路径解析、内容敏感度、沟通语言等）
- `.agents/capability-registry.md` — scripts/skills/commands/workflows/protocols/rules 全量静态索引（L1）
- [development-standards.md](docs/tech/references/development-standards.md) — 完整开发规范（代码风格、提交、Mermaid、路径引用、PowerShell 规范）
- `docs/conf.py` — Sphinx 文档构建配置
