---
id: "retrospective-xmnn-py314-rebuild-20260828"
title: "XMNN Python 3.14 Wheel & Docker 镜像重构里程碑复盘"
date: 2026-08-28
type: "retrospective"
source: ".trae/specs/xmnn-py314-rebuild/ (Spec Mode 五阶段工作流)"
session: sc-20260828-xmnn-py314-milestone-retro
scenario: milestone-retrospective
methodology: seven-concepts R→I→E→V
tags: [xmnn, python314, nuitka, docker, podman, cp314, free-threading, milestone]
status: completed
duration: "1h28m"
tokens_used: 27590131
---

# XMNN Python 3.14 Wheel & Docker 镜像重构 — 里程碑复盘

> 方法论链路：R（复盘事实）→ I（洞察根因）→ E（萃取模式）→ V（对抗审查）
> 场景：里程碑复盘（milestone-retrospective）
> 日期：2026-08-28

## 一、R 阶段：事实清单

### 1.1 任务概览

| 项 | 值 |
|---|---|
| 任务发起 | 2026-08-28，用户通过 `/spec` `/goal` 命令发起 |
| 目标目录 | `external/chaos/ai/xmnn-whl-builder` |
| 硬性约束 | wheel 和 Docker 镜像必须基于 Python 3.14 |
| 追加要求 1 | `models/demo` 下 4 个模型精度正确（余弦相似度 > 0.99） |
| 追加要求 2 | `models/debug` 下 caffe 模型精度正确 |
| 方法论 | seven-concepts-cmd，问题解决场景 I→F→V→C |
| 工作流 | Spec Mode（Specify→Plan→Approve→Implement→Review） |
| 总耗时 | 约 1 小时 28 分钟 |
| Token 消耗 | 27,590,131 |

### 1.2 技术环境事实

| # | 事实 |
|---|------|
| F-001 | 容器引擎：Podman 5.7.1（WSL2 Fedora 43 VM），buildah 1.42.1，crun 运行时 |
| F-002 | WSL VM 资源：15GB RAM，16 CPU，1TB 磁盘（实际可用 13GB） |
| F-003 | 主机环境：Windows 11，无 Docker Desktop |
| F-004 | 基础镜像 `devcontainer-base:onnx-quantized-latest` 含双 conda 环境 |
| F-005 | base env（`/opt/conda`）原始 Python 版本为 3.13.13，GIL enabled |
| F-006 | main env（`/opt/conda/envs/main`）Python 版本为 3.14.7，free-threading（cp314t，GIL disabled） |
| F-007 | clang/llvm/cmake/ninja/ccache 仅安装在 main env（`/opt/conda/envs/main/bin`） |
| F-008 | Nuitka 版本：4.1.3 |
| F-009 | pyproject.toml 声明 `requires-python = ">=3.14"`，version = "1.2.1-dev0" |
| F-010 | CMakeLists.txt 包含 `VERSION_LESS "3.14"` 硬检查 |

### 1.3 Spike 验证事实

| # | 事实 |
|---|------|
| F-011 | cp314t free-threading 下 Nuitka 编译失败，错误为 `allocator.h:606: error: use of undeclared identifier 'op'` |
| F-012 | cp314 GIL mode 下 Nuitka 编译成功，生成 `tvm.cpython-314-x86_64-linux-gnu.so` |
| F-013 | cp314 GIL 编译通过模块数：1474 |
| F-014 | cp314 GIL 编译使用 clang 22.1.8（来自 main env） |
| F-015 | base env 升级命令：`conda install -n base -c conda-forge "python=3.14=*_cp314"` |
| F-016 | 升级后 base env Python 版本为 3.14.0，Py_GIL_DISABLED=0 |

### 1.4 代码变更事实

| # | 事实 |
|---|------|
| F-017 | Dockerfile 新增 `py314-base` 阶段（第 21-31 行），内置 Python 版本和 GIL 状态断言 |
| F-018 | Dockerfile BUILD 和 FINAL 阶段均 `FROM py314-base` |
| F-019 | PATH 配置为 `/opt/conda/bin:/opt/conda/envs/main/bin`（base 在前，提供 cp314 Python；main 在后，提供工具链） |
| F-020 | CC/CXX 显式指向 `/opt/conda/envs/main/bin/clang` 和 `clang++` |
| F-021 | LD_LIBRARY_PATH 包含 `/opt/conda/envs/main/lib:/opt/conda/lib` |
| F-022 | build-wheel.sh 删除了 sed 降级补丁块（原将 `VERSION_LESS "3.14"` 改为 `"3.13"`、`requires-python = ">=3.14"` 改为 `">=3.13"`） |
| F-023 | build-wheel.sh 直接执行 `python -m build --wheel --no-isolation`，无版本篡改 |
| F-024 | build.sh 添加 CONTAINER_ENGINE 自动检测（docker→podman 回退） |
| F-025 | build.sh Podman 选项包含 `--cgroup-manager=cgroupfs` 和 `--format docker` |
| F-026 | build.sh grep 模式修复为 `-qE "(^|/)${IMAGE_NAME}$"` 以匹配 localhost/ 前缀 |
| F-027 | .dockerignore 6 处行内注释移到独立注释行（buildah 1.42.1 不支持行内注释） |
| F-028 | Dockerfile kernel 注册动态检测 CONDA_PREFIX（base env cp314）和 JUPYTER_BIN（main env），kernel argv 指向 cp314 Python |

### 1.5 构建产物事实

| # | 事实 |
|---|------|
| F-029 | 四个基础镜像均存在：`:latest`（1.36GB）、`:conda-llvm-latest`（3.17GB）、`:onnx-dev-latest`（3.38GB）、`:onnx-quantized-latest`（3.5GB） |
| F-030 | 最终镜像名：`localhost/xmnn-whl-builder:latest`，大小 5.25GB |
| F-031 | Wheel 文件名：`xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl` |
| F-032 | Wheel 文件大小：187,277,839 字节（187MB） |
| F-033 | Wheel 位于容器内 `/opt/xmnn-dist/`（供下游镜像 COPY） |
| F-034 | verify-wheel.sh 结果：10 passed, 0 failed，退出码 0 |
| F-035 | 容器内 `python --version` 输出 Python 3.14.0 |
| F-036 | Jupyter kernelspec list 包含 xmnn-whl-builder kernel |

### 1.6 模型精度验证事实

| # | 事实 |
|---|------|
| F-037 | demo/caffe/resnet50：输出层余弦相似度 0.998446，全网络最低 0.993847，MSE 0.017533，编译耗时 160s |
| F-038 | demo/onnx/yolov5s：输出层余弦相似度 0.998638，全网络最低 0.994715，MSE 0.000045，编译耗时 546s |
| F-039 | demo/pytorch/resnet18：输出层余弦相似度 0.998958，全网络最低 0.996744，MSE 0.012610，编译耗时 89s |
| F-040 | demo/two_inputs：输出层余弦相似度 0.999879，全网络最低 0.999879，MSE 0.000240，编译耗时 4.6s |
| F-041 | debug/caffe_demo：输出层余弦相似度 0.999789，全网络最低 0.999789，MSE 0.000472，编译耗时 13s |
| F-042 | PyTorch 模型（resnet18、two_inputs）编译时需临时安装 torch 2.13.0+cpu cp314（来自 download.pytorch.org/whl/cpu） |
| F-043 | 所有 5 个模型输出层余弦相似度均 > 0.99 阈值 |

### 1.7 审查与版本控制事实

| # | 事实 |
|---|------|
| F-044 | 独立审查 Review R1 结果：pass，11/11 检查点通过 |
| F-045 | 审查发现 0 个 actionable finding，7 个 advisory finding（文档/注释同步问题） |
| F-046 | Spec 三文档：spec.md（10 项 AC）、tasks.md（8 个任务）、review.md（11 检查点） |
| F-047 | `external/` 目录在 `.gitignore` 中，代码变更不被主仓库追踪 |
| F-048 | `.trae/specs/xmnn-py314-rebuild/` 目录为 untracked |
| F-049 | 截至复盘时，Podman 中无 xmnn-whl-builder:latest 镜像（镜像已不存在） |
| F-050 | WSL 中 `~/build/chaos/` 构建上下文目录不存在 |
| F-051 | 代码文件修改时间：Dockerfile 2026-08-28 05:51，build.sh 05:47，build-wheel.sh 03:31 |

### 1.8 时间线

| 时间（约） | 事件 |
|-----------|------|
| 03:00 | 任务发起，Spec Mode 启动，环境准备与 Podman 适配 |
| 03:30 | 基础镜像链构建完成 |
| 03:45 | Nuitka cp314t Spike 失败，cp314 GIL 回退方案验证成功 |
| 04:00 | Dockerfile 和 build-wheel.sh 修改完成 |
| 04:30 | 首次全量构建失败（.dockerignore 行内注释导致 buildah 语法错误） |
| 04:45 | 修复 .dockerignore，第二次全量构建成功 |
| 05:15 | verify-wheel.sh 10/10 PASS |
| 05:50 | 模型精度验证：4 个 demo 模型 + 1 个 debug 模型全部通过 |
| 06:30 | 独立审查 Review R1 通过 |
| 07:20 | Spec 文档更新完成，任务结束 |

---

## 二、I 阶段：核心洞察

### 洞察 1：Python 3.14 的 ABI 分裂是编译器迁移的隐性风险源

- **陈述**：Python 3.14 存在两种 ABI（cp314 GIL 和 cp314t free-threading），"支持 Python 3.14"的声明不覆盖两种 ABI。原生编译器（Nuitka）对两种 ABI 的兼容性可能完全不同，迁移前必须分别验证。
- **证据**：F-008（Nuitka 4.1.3）、F-011（cp314t 编译失败 allocator.h:606）、F-012（cp314 GIL 编译成功）、F-013（1474 模块通过）
- **反常识**：直觉上认为"Python 3.14 兼容"是一个二元判断（是/否），但实际上同一版本号下存在两个 ABI 变体，编译器对它们的支持是独立的。cp314t 作为 PEP 703/779 引入的新 ABI，其 C API 兼容性成熟度显著低于 cp314。
- **行动**：未来涉及 Python 原生编译器（Nuitka/Cython/mypyc）的版本迁移，在 spec 阶段必须列出所有目标 ABI 变体，并在 spike 阶段逐一验证，不可假设"同版本号 = 同兼容性"。

### 洞察 2：跨 conda 环境工具链引用是双环境布局下的高效架构模式

- **陈述**：当 Docker 镜像包含多个 conda 环境时，Python 解释器和原生编译器无需在同一环境中。通过 PATH 分层 + CC/CXX 显式指向 + LD_LIBRARY_PATH 共享库配置，可实现"解释器在 A 环境、编译器在 B 环境"的跨环境编译，避免重建工具链。
- **证据**：F-007（工具链仅在 main env）、F-019（PATH base first + main second）、F-020（CC/CXX 指向 main env clang）、F-021（LD_LIBRARY_PATH 含 main lib）、F-014（使用 main env clang 22.1.8 成功编译）
- **反常识**：直觉上认为编译器和 Python 解释器必须在同一 conda 环境中才能正确链接 Python 头文件和库。实际上 Nuitka 通过 `sysconfig` 获取 Python 编译参数，编译器只需在 PATH 中可找到即可，跨环境引用完全可行。
- **行动**：在 `.agents/rules/dockerfile.md` 中补充"跨 conda 环境编译"模式文档，明确 PATH/CC/CXX/LD_LIBRARY_PATH 三要素配置规范，避免未来在类似双环境场景中重建工具链。

### 洞察 3：构建产物易失，代码变更才是持久资产

- **陈述**：Docker 镜像和 WSL 构建上下文在 VM 重启/清理后消失，但 Dockerfile、build.sh、build-wheel.sh 的代码变更持久保存在 Windows 文件系统。复盘时镜像已不存在（F-049、F-050），但代码变更和 spec 文档完整保留，可随时重建。
- **证据**：F-049（Podman 中无 xmnn-whl-builder 镜像）、F-050（WSL 构建上下文不存在）、F-051（代码文件时间戳保留）、F-046（spec 三文档完整）
- **反常识**：直觉上认为"Docker 镜像 = 构建成果"，镜像存在即任务完成。但在 WSL2 临时 VM 环境中，镜像是易失的；真正的交付物是"可重复构建的代码变更"而非镜像本身。187MB 的 wheel 文件也随容器销毁而消失，但 Dockerfile 中的构建逻辑使其可随时重建。
- **行动**：将"镜像持久化"纳入构建流程——构建成功后自动 `docker save` 到 Windows 文件系统（参考已有 docker-cache-cmd 技能），或在 CI 中推送到 registry。本地开发场景至少在构建日志中记录镜像 ID 和构建参数，便于追溯。

---

## 三、E 阶段：可迁移模式萃取

### 模式 1：Spike-Validate-Fallback（SVF）编译器迁移模式

> 已入库：[svf-compiler-migration.md](../../../patterns/process-patterns/svf-compiler-migration.md)（L2 已验证，含回退穷尽分支与跨领域迁移示例）

```yaml
id: pattern-svf-compiler-migration
name: SVF 编译器迁移
maturity: L2
validation_count: 2  # xmnn py314 + 历史 py313 降级
tags: [compiler-migration, nuitka, python-ab, spike, fallback]
```

**触发场景**：
- 适用于：将原生编译器（Nuitka/Cython/mypyc/Taichi）迁移到新 Python 版本或新 ABI 变体
- 适用于：编译器对目标平台兼容性未知、全量构建耗时长（>10 分钟）的场景
- 不适用于：纯 Python 代码迁移（无原生编译）、编译器已明确声明兼容性的场景

**核心步骤**：

1. **识别 ABI 变体**：列出目标 Python 版本的所有 ABI（如 cp314、cp314t），不假设"同版本 = 同兼容"
2. **最小 Spike**：在目标环境中编译 hello-world 或最小模块（非全量项目），5 分钟内暴露编译器兼容性问题
3. **失败路径记录**：记录完整错误信息（文件名、行号、错误类型），作为社区 issue 搜索关键词
4. **回退方案设计**：确定替代 ABI（如 cp314 替代 cp314t）或替代编译器版本
5. **回退方案预验证**：在全量构建前，用回退方案编译项目中最复杂的原生模块（本次为 tvm，1474 子模块）
6. **全量构建**：回退方案验证通过后执行全量构建
7. **决策记录**：在 Dockerfile/构建脚本注释中记录 spike 结果和方案选择依据

**反模式**：

- ❌ **直接全量构建**：假设编译器兼容新 ABI，直接跑 15-30 分钟全量构建，失败后浪费时间且难以定位是哪个模块的问题
- ❌ **无回退预案**：Spike 失败后无替代方案，临时在构建过程中试错（如本次历史方案的 sed 降级补丁）
- ❌ **只验证不记录**：Spike 结果只在对话中提及，未写入代码注释或文档，下次迁移时重复踩坑
- ❌ **混淆版本与 ABI**：认为"Python 3.14 兼容"就等于"cp314 和 cp314t 都兼容"

**检验标准**：
- Spike 阶段在全量构建前完成，耗时 < 10 分钟
- 回退方案经预验证（编译了项目中最复杂的原生模块）
- 构建脚本中有注释记录 spike 结果和方案选择依据
- 全量构建一次成功（不因编译器兼容性问题返工）

**跨场景迁移示例**：
- Cython 迁移到 Python 3.14 free-threading：先编译最小 .pyx 文件，失败则回退到 GIL 模式
- CUDA 编译器升级：先编译最小 kernel，失败则回退到上一版本 CUDA toolkit
- Emscripten 版本升级：先编译 hello-world.wasm，失败则锁定版本号

### 模式 2：跨 conda 环境工具链引用模式

> 已入库：[cross-conda-toolchain.md](../../../patterns/code-patterns/cross-conda-toolchain.md)（L1 实验性，单案例待验证，含前置条件与 LD_LIBRARY_PATH 顺序风险等对抗审查修正）

```yaml
id: pattern-cross-conda-toolchain
name: 跨环境工具链引用
maturity: L1
validation_count: 1  # xmnn py314（待更多案例验证）
tags: [conda, docker, cross-compile, toolchain, dual-env]
```

**触发场景**：
- 适用于：Docker 镜像含多个 conda 环境，Python 解释器和原生编译器在不同环境
- 适用于：基础镜像由其他团队维护，无法更改环境布局
- 不适用于：单环境镜像、可自由重建工具链的场景

**核心步骤**：

1. **环境盘点**：确认各 conda 环境的 Python 版本、ABI、已安装工具链
2. **PATH 分层**：将含目标 Python 的环境 bin 放在 PATH 前面，含工具链的环境 bin 放在后面
3. **CC/CXX 显式指向**：设置 `CC=/path/to/other/env/bin/clang`，避免 PATH 解析到错误的编译器
4. **LD_LIBRARY_PATH 共享库**：包含工具链环境的 lib 目录，确保运行时能找到 LLVM 共享库
5. **断言验证**：在 Dockerfile RUN 中添加版本断言（Python 版本、GIL 状态、编译器版本）
6. **kernel 双环境处理**：Jupyter kernel argv 指向含 xmnn 的 Python 环境，Jupyter 服务本身在工具链环境

**反模式**：

- ❌ **重建工具链**：在目标 Python 环境中重新安装 clang/LLVM（数 GB 下载 + 数十分钟构建）
- ❌ **假设编译器同环境**：认为编译器必须和 Python 在同一 conda 环境，不尝试跨环境引用
- ❌ **忽略 LD_LIBRARY_PATH**：PATH 配置正确但运行时找不到 libLLVM.so，导致 tvm.build 失败
- ❌ **不设断言**：Python 版本或 GIL 状态不符合预期时构建不报错，运行时才出现 ABI 不兼容

**检验标准**：
- `python --version` 和 `clang --version` 均输出版本号
- `python -c "import sysconfig; print(sysconfig.get_config_var('CC'))"` 指向正确的编译器
- Nuitka/CMake 构建过程中无"编译器未找到"或"头文件缺失"错误
- Dockerfile 中包含版本断言，构建失败时能立即定位问题

**跨场景迁移示例**：
- GPU 镜像：Python 在 base env，CUDA toolkit 在 nvidia env，通过 PATH + LD_LIBRARY_PATH 跨环境编译
- 数据科学镜像：Python 3.12 在 base env，pandas/numpy 在 py312 env，编译器在 build env

---

## 四、V 阶段：对抗审查

### 4.1 魔鬼代言人视角

**攻击点 1：模型精度数据是否可信？**
- 5 个模型的余弦相似度数据（6 位小数）来自 tasks.md 中的自报告表格，未附原始 CSV 或日志文件路径。
- 数据自洽性检查：输出层相似度 >= 全网络最低相似度 ✅；MSE 量级与相似度一致 ✅
- **结论**：数据内部自洽，但缺乏可审计的原始日志。建议在 tasks.md 中补充日志路径。（advisory A5，已记录）

**攻击点 2：镜像已不存在，如何确认构建真的成功过？**
- Podman 中无 xmnn-whl-builder 镜像（F-049），构建上下文也不存在（F-050）
- 但代码变更（Dockerfile/build.sh/build-wheel.sh）在磁盘上完整保留，spec 文档记录了镜像 ID（3518ab0e4c83）和验证结果
- **结论**：代码可随时重新构建，spec 文档提供了构建成功的充分证据。但镜像易失性确实是一个流程缺陷（洞察 3）。

**攻击点 3：7 个 advisory finding 中是否有被低估的？**
- A1（spec FR 文字未更新）：spec 内部 FR-1/FR-2 写"main env 在前"但实际"base env 在前"，这是 spec 与实现的不一致。虽然 Background 部分已更新，但 FR 文字未同步可能导致未来维护者困惑。评级 advisory 合理（不影响功能），但建议尽快修正。
- A2（dockerfile.md 规范未同步）：规范文档写"两阶段构建"实际三阶段，可能导致未来审查时误判。建议同步。
- **结论**：7 个 advisory 均不阻塞验收，但 A1 和 A2 应在下次维护时优先处理。

### 4.2 新人视角

**攻击点 4：cp314 和 cp314t 的区别没有在报告开头解释**
- 新接触 Python 3.14 的工程师可能不了解 free-threading（PEP 703/779）背景
- **修正**：在事实清单 F-005/F-006 中补充了 GIL 状态说明，在洞察 1 中解释了 ABI 分裂

**攻击点 5：Nuitka 是什么？为什么用它？**
- 报告假设读者了解 Nuitka 是 Python-to-C 编译器
- **修正**：在萃取模式中补充了 Nuitka 的定位说明

### 4.3 老板视角

**攻击点 6：投入 1.5 小时 + 2700 万 token，产出的镜像却没了，ROI 如何？**
- 镜像虽然不在了，但代码变更持久保存，重建只需执行 build.sh（约 15-30 分钟，无需 AI 介入）
- 更重要的产出是：① 消除了 Python 3.13 降级技术债；② 验证了 Nuitka cp314 兼容性；③ 沉淀了 2 个可复用模式
- **结论**：ROI 正向。持久资产（代码 + 模式 + 知识）的价值远超临时镜像。

### 4.4 未来视角

**攻击点 7：Nuitka 未来版本支持 cp314t 后，当前方案是否需要回退？**
- 当 Nuitka 修复 free-threading 兼容性后，可切换回 main env cp314t 方案（PATH main first）
- 当前 Dockerfile 的 py314-base 阶段设计使得切换成本低：只需删除该阶段并恢复 PATH 顺序
- **建议**：在 Dockerfile 注释中添加"切换回 cp314t 的条件和步骤"，便于未来维护者评估

### V 门检查

- [x] 4 个视角全部覆盖
- [x] 审查意见 7 条，每条有具体攻击点
- [x] 采纳修正：在事实清单中补充 ABI 说明、在模式中补充 Nuitka 定位
- [x] 无 actionable finding（advisory 不阻塞）

---

## 五、行动项

| # | 行动项 | 优先级 | 类型 | 状态 |
|---|--------|--------|------|------|
| A-1 | 更新 spec.md FR-1/FR-2/AC-4 文字，反映 base env cp314 方案（审查 A1） | medium | docs | pending |
| A-2 | 更新 `.agents/rules/dockerfile.md` 同步三阶段结构和跨环境编译模式（洞察 2、审查 A2） | medium | docs | pending |
| A-3 | 构建成功后自动 `podman save` 到 Windows 文件系统或推送 registry（洞察 3） | medium | feat | pending |
| A-4 | 同步静态 kernelspec/kernel.json 与 Dockerfile 动态版本（审查 A3） | low | chore | pending |
| A-5 | 统一 verify-wheel.sh/Dockerfile 注释中的验证项数为 10 项（审查 A7） | low | docs | pending |
| A-6 | 将 SVF 编译器迁移模式入库到 `docs/retrospective/patterns/` | medium | knowledge | ✅ completed（[svf-compiler-migration.md](../../../patterns/process-patterns/svf-compiler-migration.md)，L2 已验证） |

---

## 六、质量门记录

| 质量门 | 阶段 | 结果 | 说明 |
|--------|------|------|------|
| G1 | R | ✅ pass | 50 条事实，无因果词，可验证可追溯 |
| G2 | I | ✅ pass | 3 条洞察，每条含陈述/证据/反常识/行动四元组 |
| G3 | E | ✅ pass | 2 个模式，含触发/步骤/反模式/检验/迁移 |
| V门 | V | ✅ pass | 4 视角覆盖，7 条审查意见，2 处修正 |
| G4 | C | N/A | 本次为复盘文档产出，无代码提交；行动项 A-1~A-6 待后续执行 |

---

## 七、关联资源

- Spec 文档：[spec.md](../../../../../.trae/specs/xmnn-py314-rebuild/spec.md)、[tasks.md](../../../../../.trae/specs/xmnn-py314-rebuild/tasks.md)、[review.md](../../../../../.trae/specs/xmnn-py314-rebuild/review.md)
- 代码变更：
  - [Dockerfile](../../../../../../external/chaos/ai/xmnn-whl-builder/Dockerfile)
  - [build.sh](../../../../../../external/chaos/ai/xmnn-whl-builder/build.sh)
  - [build-wheel.sh](../../../../../../external/chaos/ai/xmnn-whl-builder/scripts/build-wheel.sh)
  - [.dockerignore](../../../../../../external/chaos/.dockerignore)
- Nuitka free-threading issue: https://github.com/Nuitka/Nuitka/issues/3772
- PEP 779 (Python 3.14 free-threading): https://peps.python.org/pep-0779/
- free-threading 兼容性追踪: https://py-free-threading.github.io/tracking/
