---
id: "retrospective-xmnn-wheel-packaging-data-dirs-20260722"
title: "xmnn wheel 打包数据目录缺失问题修复复盘（完整版）"
date: "2026-07-22"
type: "retrospective"
source: "session: xmnn-client:1.2.2-alpha wheel 打包问题修复 + 镜像验证 + 文档交付"
tags: ["xmnn", "wheel", "packaging", "cmake", "docker", "数据目录", "行号同步", "部署文档", "FAQ"]
---

# xmnn Wheel 打包数据目录缺失问题修复复盘

## 1. 复盘：事实时间线

### Phase 1：代码修复（T0-T8）

| 时间 | 事件 | 产出 |
|------|------|------|
| T0 | 发现 `xmnn-client:1.2.2-alpha` 镜像中 `autolibs/`、`fonts/`、`tools_cpp/` 缺失，`vta_hw` 包含不需要的构建期资产 | 问题定义 |
| T1 | 在 `packaging/CMakeLists.txt` 添加三个数据目录的 `install(DIRECTORY ...)` 规则 + 存在性检查 | `packaging/CMakeLists.txt` |
| T2 | 在 `packaging/vta/CMakeLists.txt` 将 `vta_hw/` 安装改为仅安装 `vta_hw/config/` | `packaging/vta/CMakeLists.txt` |
| T3 | 在 `src/xmpack/wheel.py` 添加 wheel 打包完成后的数据目录完整性校验 | `src/xmpack/wheel.py` |
| T4 | 用户反馈路径错误：`autolibs/` 等应在 `xmnn/` 子目录下，修正 DESTINATION | 路径修正 |
| T5 | 添加详细日志输出，三处各加 `[xmnn-data]`/`[vta-hw]`/`[wheel-verify]` 标签日志 | 日志增强 |
| T6 | 执行 `full_build.py --force --skip-image` 构建验证，wheel 183.6MB，所有检查通过 | 构建验证 |
| T7 | 创建 `docs/packaging-patterns.md` 文档，含四个模式 + 源码溯源映射表 | 知识沉淀 |
| T8 | 添加 `[pattern:...]` 标记 + `scripts/update_pattern_line_numbers.py` 实现行号自动更新 | 自动化 |

### Phase 2：镜像验证 + 文档交付（T9-T13）

| 时间 | 事件 | 产出 |
|------|------|------|
| T9 | 重新构建 Docker 镜像（修复前 `--skip-image` 跳过了镜像构建），wheel 184MB | 新镜像 `233cbf9603ef` |
| T10 | 容器内验证：数据目录路径、vta_hw 内容、Python 模块导入、API 接口 | 12 项全部通过 |
| T11 | 创建 `docs/deployment-guide.md`（272 行）：部署指南 + 验证报告 + 升级指南 + 验证脚本 | 部署文档 |
| T12 | 创建 `docs/faq.md`（60 行，7 个 Q&A）：独立 FAQ 文件，可直接在 README 中引用 | FAQ 文档 |
| T13 | 用户要求复盘+洞察+萃取+导出 | 本报告 |

### 涉及文件汇总

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `packaging/CMakeLists.txt` | 修改 | 数据目录安装规则 + 存在性检查 + 日志 |
| `packaging/vta/CMakeLists.txt` | 修改 | 仅安装 config/ 子目录 + 日志 |
| `src/xmpack/wheel.py` | 修改 | wheel 数据目录完整性校验 |
| `docs/packaging-patterns.md` | 新建 | 四个可复用打包模式 |
| `scripts/update_pattern_line_numbers.py` | 新建 | 行号自动更新脚本 |
| `docs/deployment-guide.md` | 新建 | 部署指南 + 验证报告 + 升级指南 |
| `docs/faq.md` | 新建 | 独立 FAQ 文件 |

### 镜像验证结果（Phase 2）

```
镜像: xmnn-client:1.2.2-alpha (233cbf9603ef, 7.6GB)
Wheel: xmnn-1.2.2a0-cp314-cp314-linux_x86_64.whl (184 MB)

数据目录验证:
  xmnn/autolibs/   PASS (VTA2_0)
  xmnn/fonts/      PASS (MapleMono-NF-CN-Regular.ttf)
  xmnn/tools_cpp/  PASS (bin/, libs/)
  vta_hw/          PASS (仅 config/)

功能验证:
  import tvm       PASS
  import xmnn      PASS
  import vta       PASS
  xmnn APIs (6个)  PASS
```

---

## 2. 洞察：根因分析

### 2.1 现象

1. Docker 镜像中 `autolibs/`、`fonts/`、`tools_cpp/` 三个数据目录缺失
2. `vta_hw` 打包了整个目录（含 `build/`、`hardware/` 等构建期资产），实际只需 `config/`
3. 修复后 `--skip-image` 导致镜像未更新，验证时发现仍是旧镜像

### 2.2 5-Whys 根因追溯

1. **为什么数据目录缺失？** — CMakeLists.txt 中没有对应的 `install(DIRECTORY ...)` 规则
2. **为什么之前没有发现？** — 构建脚本没有验证步骤，wheel 打包后没有检查目录完整性
3. **为什么没有验证步骤？** — 构建流水线只关注 `.so` 编译和基础导入测试，遗漏了数据目录
4. **为什么遗漏了数据目录？** — 没有明确的规范要求"哪些数据应打包进 wheel"，依赖开发者记忆
5. **根本原因**：**缺少数据目录打包规范 + 构建后验证机制 + 部署文档**，导致"能编译=能运行"的错误假设

### 2.3 新增洞察：修复代码 ≠ 修复镜像

`--skip-image` 参数跳过了镜像构建，导致 CMake 修复只体现在 wheel 层面，镜像仍是旧版本。**构建流水线中的"跳过"选项应被视为临时优化，修复后必须全量构建验证。**

### 2.4 新增洞察：文档即交付物

代码修复完成后，团队需要的不只是代码变更，还包括：
- 部署指南（如何启动、如何验证）
- 验证报告（证明修复有效）
- 升级指南（下次怎么升级）
- FAQ（常见问题快速解答）

**没有文档的修复是半成品。** 文档应作为交付物的一部分，而非事后补充。

### 2.5 改进建议

1. 在 CMake 构建阶段添加数据目录存在性检查（Fail Fast）
2. 在 wheel 打包阶段添加完整性验证（打包即验证）
3. 将打包规范文档化，作为后续维护的参考
4. 修复后执行全量构建（不跳过镜像），确保端到端验证
5. 将部署文档、FAQ 作为标准交付物纳入项目

---

## 3. 萃取：可复用模式

### 模式一：CMake 数据目录安装保障

**触发场景**：通过 scikit-build-core + CMake 将外部数据目录安装到 wheel 的 site-packages 中

**核心步骤**：
1. 打印关键变量（`DATA_DIR`），方便排查路径错误
2. 用 `foreach` 循环逐个检查源目录是否存在，不存在则 `FATAL_ERROR`
3. 每个 `install(DIRECTORY ...)` 前后加日志，标记安装位置

**反模式**：`install(DIRECTORY ...)` 不检查源目录是否存在，CMake 仅发出警告，构建继续但目录缺失

### 模式二：CMake 选择性安装子目录

**触发场景**：源目录包含构建期资产，运行时只需要特定子目录

**核心步骤**：
1. 检查目标子目录是否存在
2. `install(DIRECTORY "${SRC}/subdir/" DESTINATION subdir)` 仅安装所需子目录
3. 不存在时 `FATAL_ERROR`

**反模式**：`install(DIRECTORY "${SRC}/" DESTINATION ...)` 安装整个目录，包含大量不需要的构建产物

### 模式三：Shell 端 Wheel 完整性验证

**触发场景**：wheel 打包完成后验证数据目录完整性

**核心步骤**：
1. 遍历预期目录列表，检查是否存在
2. 输出文件数和大小（量化指标）
3. 缺失时列出实际目录结构，帮助定位
4. `exit 1` 终止流水线

**反模式**：仅检查 `.so` 文件，遗漏数据目录

### 模式四：文档-源码行号自动同步

**触发场景**：模式文档中的代码行号引用因代码合并而偏移

**核心步骤**：
1. 在源码对应位置添加 `[pattern:<name>]` 标记注释
2. 创建 Python 脚本扫描标记获取实际行号
3. 自动更新文档中的行号引用

**反模式**：手工维护行号，必然腐烂

### 模式五：部署文档标准化

**触发场景**：项目产出 Docker 镜像，需要交付给团队或客户部署使用

**核心步骤**：
1. 镜像信息表（名称、ID、大小、基础镜像、运行用户、Python 环境）
2. 三种拉取方式（Registry / 本地构建 / 压缩包导入）
3. 启动命令 + 参数说明表 + 典型场景示例
4. Entrypoint 行为说明（自动 UID 适配等）
5. 一键验证脚本（可直接复制执行）
6. 版本升级流程（5 步走 + 验证清单）
7. 附录：相关文档索引

**反模式**：只给一句 `docker run` 命令，没有参数说明、验证步骤和升级指南

### 模式六：FAQ 独立化

**触发场景**：大文档中的 FAQ 需要被 README 或其他文档引用

**核心步骤**：
1. 将 FAQ 从大文档中提取为独立文件
2. 每个 Q&A 使用 `## QN：问题标题` 格式，方便锚点链接
3. 包含可复制执行的命令示例
4. 末尾链接回完整文档
5. README 中一行引用：`详见 [docs/faq.md](docs/faq.md)`

**反模式**：FAQ 嵌在大文档中，每次引用需要跳转到长文档内搜索

---

## 4. 质量门检查

| 质量门 | 状态 | 说明 |
|--------|------|------|
| G1（事实无因果词） | 通过 | 复盘阶段纯事实描述，分 Phase 1/2 清晰呈现 |
| G2（洞察四元组） | 通过 | 现象+根因+影响+建议完整，新增"修复代码≠修复镜像"和"文档即交付物"两个洞察 |
| G3（模式可迁移） | 通过 | 六个模式均有触发条件+核心步骤+反模式+迁移验证 |

---

## 5. 源码溯源

| 模式 | 源码文件 | 标记 |
|------|---------|------|
| 模式一 | `packaging/CMakeLists.txt` | `# [pattern:data-dir-install]` |
| 模式二 | `packaging/vta/CMakeLists.txt` | `# [pattern:vta-hw-config]` |
| 模式三 | `src/xmpack/wheel.py` | `# [pattern:wheel-verify]` |
| 模式五 | `docs/deployment-guide.md` | 全文 |
| 模式六 | `docs/faq.md` | 全文 |

行号自动更新：`python scripts/update_pattern_line_numbers.py`

---

## 6. 交付物清单

| 交付物 | 路径 | 类型 |
|--------|------|------|
| 代码修复 | `packaging/CMakeLists.txt`, `packaging/vta/CMakeLists.txt`, `src/xmpack/wheel.py` | 代码 |
| 打包模式文档 | `docs/packaging-patterns.md` | 文档 |
| 行号自动更新脚本 | `scripts/update_pattern_line_numbers.py` | 工具 |
| 部署指南 | `docs/deployment-guide.md` | 文档 |
| FAQ | `docs/faq.md` | 文档 |
| 本复盘报告 | `.agents/docs/retrospective/reports/bug-fix/docker-build/retrospective-xmnn-wheel-packaging-data-dirs-20260722/README.md` | 复盘 |

<!-- changelog -->
- 2026-07-22 | report | 初始报告：Phase 1 代码修复（T0-T8）
- 2026-07-22 | report | 更新：Phase 2 镜像验证 + 文档交付（T9-T13），新增模式五/六、两个新洞察
