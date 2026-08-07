---
id: retro-devcontainer-variants-milestone-20260807
date: 2026-08-07
type: project-milestone
source: apps/devcontainer-base/variants/ 实现 + AGENTS.md路由 + 测试体系
status: completed
tags: [docker, devcontainer, variants, conda, llvm, milestone, testing, governance]
commit: f9db7a87, b1ccfa43
---

# devcontainer-base 镜像变体系统 — 里程碑复盘报告

## 1. 里程碑概述

**里程碑名称**：devcontainer-base variants/ 镜像变体目录系统完成
**完成日期**：2026-08-07
**里程碑目标**：在 devcontainer-base 基础镜像之上，建立可扩展的镜像变体目录结构，支持基于基础镜像增量构建特殊功能变体（conda、conda-llvm 等），并提供统一构建脚本、模板和测试体系。

---

## 2. S1：事实还原（时间线与产出物）

### 2.1 执行时间线

| 阶段 | 活动 | 关键产出 |
|------|------|---------|
| Spec 阶段 | 研究现有 devcontainer-base、pytorch-base、caffe-ffi-jupyter 三个项目结构 | spec.md/tasks.md/checklist.md |
| Task 1 | 创建 variants/ 基础目录结构 | 目录骨架、README.md 占位、shared/lib/logging.sh |
| Task 2 | 实现 variants/build.sh 统一构建脚本 | 拓扑排序、依赖处理、国内镜像源、构建计时 |
| Task 3 | 实现 conda 变体 Dockerfile 和配置 | 5阶段追加构建、Miniconda3/opt/conda、conda-init.sh |
| Task 4 | 实现 conda-llvm 变体 Dockerfile 和配置 | 4阶段追加构建、LLVM 22.1.8/clang/cmake/ninja |
| Task 5 | 实现 _template/ 模板目录 | 7占位符模板、新增变体5步流程 |
| Task 6 | 更新主 AGENTS.md 添加 variants 路由 | 嵌套路由图、上下文路由表、规范入口、快速开始 |
| Task 7 | 端到端静态验证 | 62项检查、修复get_base_tag()双重前缀Bug |
| 增强阶段 | build.sh 日志增强+构建脚本+测试脚本 | 阶段日志解析、build-conda-llvm.sh、test-conda-llvm.sh(21项测试) |

### 2.2 最终产出物清单

```
variants/
├── README.md                              # 变体索引+使用指南+新增变体流程
├── build.sh                               # 统一构建脚本（增强版：|分隔符、详细日志、逐条验证）
├── shared/lib/logging.sh                  # 共享日志库
├── scripts/
│   ├── build-conda-llvm.sh                # conda-llvm 一键构建+验证脚本
│   └── test-conda-llvm.sh                 # conda-llvm 21项单元测试
├── _template/                             # 新变体模板
│   ├── Dockerfile                         # 3阶段模板Dockerfile（7占位符）
│   ├── .env.example
│   ├── README.md                          # 含5步新增Checklist
│   └── .agents/rules/dockerfile.md
├── conda/                                 # Miniconda3 基础环境变体
│   ├── Dockerfile                         # 5阶段追加构建
│   ├── .env.example
│   ├── README.md
│   └── .agents/rules/dockerfile.md
└── conda-llvm/                            # conda+LLVM/clang 编译工具链变体
    ├── Dockerfile                         # 4阶段追加构建（ENV PATH=/opt/conda/bin:$PATH）
    ├── .env.example
    ├── README.md
    └── .agents/rules/dockerfile.md
```

### 2.3 修复的问题

| 问题 | 严重程度 | 修复方式 |
|------|---------|---------|
| `get_base_tag()` 返回 `"${deps[0]}-${TAG}"` 与 Dockerfile `FROM devcontainer-base:conda-${BASE_TAG}` 产生双重前缀 `conda-conda-latest` | 🔴 阻断 | 修改为统一返回 `${TAG}` |
| variants/README.md "新变"笔误（缺"体"字） | 🟡 轻微 | 修正并扩充为完整的新增变体指南 |
| VARIANTS 数组用 `:` 分隔导致验证命令（含路径 `:`）解析错误 | 🟡 中等 | 改用 `\|` 作为字段分隔符 |

### 2.4 关键数据

- **新增/修改文件**：18 个
- **静态验证项**：62 项，通过 62 项（修复后）
- **Bash 脚本语法检查**：3/3 通过
- **Dockerfile 规范检查**：18/18 通过（syntax/ARG/FROM/SHELL/TIMER/VALIDATION 等）
- **单元测试用例**：21 项（6 个测试组）
- **构建脚本代码行数**：build.sh ~470行 + build-conda-llvm.sh + test-conda-llvm.sh

---

## 3. S2：过程分析

### 3.1 成功因素

1. **第一性原理设计先行**：在编码前先完成了 R（研究3个现有项目）→ F（第一性原理推导变体目录结构）→ V（对抗审查多视角验证）→ I（输出spec/tasks/checklist），避免了边做边改的返工
2. **继承而非复制**：变体 Dockerfile 采用 FROM 基础镜像 + 追加层的模式，避免了复制 Dockerfile 导致的代码重复
3. **拓扑排序构建**：build.sh 自动处理变体间依赖关系（conda-llvm 依赖 conda），按正确顺序构建
4. **模板驱动新增**：_template/ 提供标准化模板，新增变体只需复制+替换占位符
5. **端到端静态验证**：在 Docker 环境不可用时通过 62 项静态检查发现了阻断性 Bug

### 3.2 遇到的挑战与应对

| 挑战 | 应对方式 |
|------|---------|
| 基础镜像 PATH 优先级与 conda 冲突 | conda 变体不修改 PATH（通过 profile.d 手动激活），conda-llvm 变体才将 conda/bin 前置 |
| 验证命令含 `:` 导致字段解析错误 | 将 VARIANTS 分隔符从 `:` 改为 `\|` |
| Docker 环境不可用无法做实际构建验证 | 通过 bash -n 语法检查 + 静态结构检查 + Dockerfile 规范检查保证代码质量 |
| get_base_tag() 与 Dockerfile FROM 双重前缀 | 简化函数统一返回 `${TAG}`，变体前缀由 Dockerfile FROM 中的变体名决定 |

### 3.3 瓶颈与改进点

1. **缺乏 Docker 构建时验证**：静态验证无法替代实际 `docker build`，首次实际构建可能还会发现问题
2. **Dockerfile 阶段数不统一**：conda 用 5 阶段，conda-llvm 用 4 阶段，模板用 3 阶段，可以进一步标准化
3. **共享脚本不足**：变体间的 conda 镜像源配置等逻辑在各 Dockerfile 中重复，可以提取为共享脚本片段

---

## 4. S3：洞察与可复用模式

### 洞察 1：镜像变体"基础继承+配置化"模式

**现象**：传统做法是每个变体复制完整 Dockerfile，导致基础镜像更新时需要同步修改所有变体。
**根因**：缺乏统一的变体管理框架，变体间代码重复。
**影响**：维护成本随变体数量线性增长，容易出现配置不一致。
**建议模式**：
- 基础镜像定义核心服务（SSH/Docker/Podman/Jupyter）
- 变体通过 FROM base + 追加层实现增量功能
- 统一构建脚本处理依赖关系、镜像源、验证
- 模板驱动新增，确保新变体符合规范

### 洞察 2：Dockerfile 多阶段构建中"构建计时器"模式

**现象**：Docker 构建耗时长，无法快速定位哪个阶段是瓶颈。
**根因**：BuildKit 输出虽然有进度信息，但没有阶段级耗时汇总。
**建议模式**：
- 每个 RUN 阶段开始时记录 `_STAGE_START=$(date +%s)`
- 阶段结束时计算 `_ELAPSED` 并输出 `[TIMER] Stage X/Y took Ns`
- 最终阶段输出 ASCII 汇总表
- 构建脚本通过 tee 保存日志并解析 [TIMER] 标记

### 洞察 3：单元测试"分层验证"模式

**现象**：Docker 镜像验证通常只做 `docker run --rm image cmd --version`，遗漏功能测试。
**根因**：缺乏系统化的测试框架，验证停留在"命令存在"层面。
**建议模式**：
- L1 工具链可用性（version 检查）
- L2 功能编译测试（Hello World + 语言特性）
- L3 核心组件深度验证（components、include 路径）
- L4 基础服务继承检查（确保变体未破坏基础功能）
- L5 环境隔离验证（路径优先级、venv 完整性）
- L6 配置验证（镜像源等配置文件存在）

### 洞察 4：字段分隔符选择原则

**现象**：使用 `:` 作为数组字段分隔符时，验证命令中的路径（如 `/opt/conda/bin/conda`）会导致解析错误。
**根因**：选择分隔符时未考虑数据内容可能包含的字符。
**反模式**：使用数据中常见字符（`:`、`/`、`=`、空格）作为分隔符。
**建议模式**：选择数据中极不可能出现的字符作为分隔符（如 `|` 在 shell 命令中需要转义，在描述文本中也很少出现）。

---

## 5. 行动项

| 优先级 | 行动项 | 验收标准 | 状态 |
|--------|--------|---------|------|
| 🔴 高 | 在 WSL2/Linux 环境中执行实际 Docker 构建验证 | `bash variants/scripts/build-conda-llvm.sh` 成功，21 项测试全部 PASS | ✅ 已完成 (2026-08-07) |
| 🟡 中 | 提取共享 conda 配置脚本片段到 variants/shared/ | 新增 shared/scripts/conda-mirror-setup.sh，conda 和 conda-llvm Dockerfile 通过 COPY 使用 | ✅ 已完成 |
| 🟡 中 | 标准化 Dockerfile 阶段结构 | 更新 _template/Dockerfile 为标准5阶段模板，对齐 conda 变体 | ✅ 已完成 |
| 🟢 低 | 添加第三个变体示例（如 cuda 或 nodejs） | 验证模板可复用性，新增变体耗时 < 30 分钟 | ⬜ 待办 |
| 🟢 低 | 将 variants/ 构建集成到 CI 流水线 | PR 时自动构建并运行 test-conda-llvm.sh | ⬜ 待办 |

### 5.1 🔴 高行动项执行记录 (2026-08-07)

在 WSL2/Linux 环境中实际执行 `bash variants/scripts/build-conda-llvm.sh --tag 1.0` 构建验证，过程中发现并修复两个真实缺陷：

**缺陷 1：`clang-tools-extra=22.1.8` 包在 conda-forge 不存在**
- 现象：conda 求解环境失败，报 `PackagesNotFoundInChannelsError: clang-tools-extra=22.1.8`
- 根因：`clang-tools-extra` 包在 conda-forge 通道中并不存在（API 确认 `{"error":"\"clang-tools-extra\" could not be found"}`）
- 修复：从 [conda-llvm/Dockerfile](../../../../../../variants/conda-llvm/Dockerfile) 安装列表中移除该包，同步更新 README、`.env.example`、`.agents/rules/dockerfile.md` 等文档引用
- 影响：该包不被 21 项测试与项目约束依赖，移除后其余 LLVM 包（llvmdev/clang/clangdev/lld/lldb 22.1.8）正常安装

**缺陷 2：T4 cmake 测试断言过时 + 提取逻辑缺陷**
- 现象：21 项测试中 T4 失败，`cmake version expected >= 3.x, got:`（空值）
- 根因 A：conda-forge 现已提供 cmake 4.x（实际安装 4.4.2），测试正则 `^3\.` 只匹配 3.x
- 根因 B：`head -1 | awk '{print $3}'` 取到容器 entrypoint 的服务诊断日志行而非 cmake 版本行，导致 `cmake_ver` 为空
- 修复：[test-conda-llvm.sh](../../../../../../variants/scripts/test-conda-llvm.sh) 的 T4 改为从完整输出 grep `cmake version X.Y`，并接受 `^[34]\.`

**构建验证结果**
- 镜像 `devcontainer-base:conda-llvm-1.0` 构建成功（6.17GB）
- 关键版本：llvmdev/clang/clangdev/lld/lldb 22.1.8、cmake 4.4.2、ninja 1.13.2、make 4.4.1
- 21 项测试全部 PASS（0 FAIL）

---

## 6. 交付物快速索引

| 类别 | 路径 |
|------|------|
| 构建脚本 | [variants/build.sh](../../../../../../variants/build.sh) |
| 一键构建脚本 | [variants/scripts/build-conda-llvm.sh](../../../../../../variants/scripts/build-conda-llvm.sh) |
| 完整单元测试 | [variants/scripts/test-conda-llvm.sh](../../../../../../variants/scripts/test-conda-llvm.sh) |
| 冒烟测试 | [variants/scripts/test-conda-llvm-smoke.sh](../../../../../../variants/scripts/test-conda-llvm-smoke.sh) |
| TIMER解析器测试 | [variants/scripts/test-timer-parser.sh](../../../../../../variants/scripts/test-timer-parser.sh) |
| conda 变体 Dockerfile | [variants/conda/Dockerfile](../../../../../../variants/conda/Dockerfile) |
| conda-llvm 变体 Dockerfile | [variants/conda-llvm/Dockerfile](../../../../../../variants/conda-llvm/Dockerfile) |
| 变体模板 | [variants/_template/Dockerfile](../../../../../../variants/_template/Dockerfile) |
| 变体索引 | [variants/README.md](../../../../../../variants/README.md) |
| **变体治理路由** | [variants/AGENTS.md](../../../../../../variants/AGENTS.md) |
| **变体规则容器** | [variants/.agents/](../../../../../../variants/.agents/README.md) |
| 项目主路由 | [AGENTS.md](../../../../../../AGENTS.md) |

---

## 7. 治理层增强：AGENTS.md 路由 + .agents/ 规范容器（commit b1ccfa43）

在 variants/ 功能实现完成后，为其建立了完整的 AI 协作治理层，确保后续维护和新增变体时有规范可依。

### 7.1 产出物

```
variants/
├── AGENTS.md                    # 变体系列AI协作者入口（启动协议+五层路由+约束速览）
└── .agents/
    ├── README.md                # AI资产目录索引+五层路由加载顺序
    └── rules/
        ├── build-orchestration.md  # 构建编排规范（VARIANTS数组格式、拓扑排序、参数传递）
        ├── variant-conventions.md  # 变体Dockerfile共享约定（FROM/SHELL/PATH/缓存挂载）
        ├── testing.md             # 测试规范（L1-L6分层策略+脚本模板）
        └── new-variant-guide.md   # 新增变体7步指南
```

### 7.2 五层路由体系

```
第1层（根级）：SpecWeave 全局规范 → ../../../../.agents/global-core-rules.md
第2层（应用级）：apps/ 区域路由 → ../../../AGENTS.md
第3层（项目级）：devcontainer-base 项目规范 → ../../.agents/rules/
第4层（子系统级）：变体管理规范 → 本目录 rules/
第5层（变体级）：单个变体特有规则 → ../<variant>/.agents/rules/dockerfile.md
```

### 7.3 父级路由更新

同步更新了 [apps/devcontainer-base/AGENTS.md](../../../../../../AGENTS.md) 的嵌套路由图和上下文路由表，将变体相关任务指向 variants/AGENTS.md，确保路由链完整。

---

## 8. 测试体系验证与Bug修复（commit f9db7a87）

### 8.1 测试脚本产出

| 脚本 | 测试项 | 层级 | 耗时 | 依赖 |
|------|--------|------|------|------|
| test-timer-parser.sh | 13项单元测试 | L0（无Docker） | <2秒 | 仅bash |
| test-conda-llvm-smoke.sh | 4项冒烟测试 | L1-L2 | <10秒 | Docker镜像存在 |
| test-conda-llvm.sh | 21项完整测试 | L1-L6 | ~30秒 | Docker镜像存在 |

**test-timer-parser.sh 设计特点**：
- 不依赖Docker，从build.sh中动态提取parse_timer_logs()函数
- 生成模拟docker build日志（覆盖conda/conda-llvm两种变体格式+边缘情况）
- 验证函数正确提取started at事件、阶段耗时、总构建时长
- 发现Bug → 修复Bug → 更新mock → 全部通过的闭环验证

### 8.2 发现并修复的Bug

| Bug | 根因 | 修复方式 | 验证 |
|-----|------|---------|------|
| 🔴 Final stage缺少[TIMER]行 | conda Stage 5/5和conda-llvm Stage 4/4只输出格式化表格，未输出`[TIMER] Stage N/M took Xs`标记，导致parse_timer_logs()遗漏final stage | 在两个Dockerfile的timing summary前添加`echo "[TIMER] Stage N/M (metadata+final verify) took ${_ELAPSED}s \| ..."` | test-timer-parser.sh T6/T9通过 |
| 🔴 Build duration不进日志文件 | build.sh中`log_info "[TIMER] Build duration:"`输出到stdout（终端），不经过`docker build \| tee`管道，日志文件中没有此行 | 在`BUILD_DURATION`计算后立即`echo "[TIMER] Build duration: ${BUILD_DURATION}s" >> "$log_file"`追加写入 | test-timer-parser.sh T7通过 |

### 8.3 关键数据（本次测试验证）

- **test-timer-parser.sh**：13/13 全部通过
- **Bash语法检查**：build.sh + 2个新脚本 全部通过
- **发现并修复阻断Bug**：2个（final stage计时缺失 + Build duration丢失）
- **新增代码行数**：627行
- **新增/修改文件**：5个

---

## 9. 经验萃取

### 洞察5：单元测试发现Bug的"测试即修复"闭环模式

**现象**：在为已有代码编写单元测试时，通过精心构造测试数据，发现了2个实际运行时才会暴露的Bug。
**根因**：代码编写时只关注"正常路径"，测试编写时才关注"解析边界"——final stage和wrapper输出是两个代码路径的交汇点，容易遗漏。
**建议模式**：
1. 为每个核心函数编写不依赖运行环境的单元测试
2. 使用mock数据覆盖所有输出格式变体（而非只测一种）
3. 测试脚本本身也需作为代码审查对象
4. 发现Bug后立即更新mock数据，形成"发现→修复→验证"闭环

### 洞察6：治理层（AGENTS.md + .agents/）应在功能完成后立即建立

**现象**：variants/功能实现完成后，如果没有AGENTS.md路由和.agents/规范，后续维护者无法快速理解构建系统的约束和约定。
**建议模式**：
- 功能模块完成后第一时间建立AGENTS.md入口
- 规则文件按单一职责原子化拆分（build-orchestration/testing/conventions等）
- 嵌套路由从根级到模块级清晰定义加载顺序
- 父级路由表同步更新，确保路由链不断裂
