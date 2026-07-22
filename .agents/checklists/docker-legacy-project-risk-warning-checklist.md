---
id: "docker-legacy-project-risk-warning-checklist"
title: "Docker 化老旧项目风险预警清单"
source: "docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md"
date: 2026-07-22
related_patterns:
  - "docker-build-reference-template-copy.md"
  - "shell-nested-quote-file-based-strategy.md"
  - "legacy-cpp-compilation-compatibility-checklist.md"
  - "ops-sop-standard-template.md"
tags: [docker, risk-warning, checklist, legacy-project, cpp, build-system, knowledge-management]
---

# Docker 化老旧项目风险预警清单

> 基于 Caffe Docker 运行时镜像构建全流程复盘中的 7 条洞察，提炼为 7 项风险预警。适用于：为 5 年以上老旧 C/C++ 项目创建 Docker 构建系统。
>
> 使用方式：项目启动前逐项评估，标记风险等级，制定应对预案。

---

## 风险等级定义

| 等级 | 含义 | 响应要求 |
|------|------|---------|
| 🔴 高 | 必然发生，影响严重 | 必须制定预案，预留缓冲时间 |
| 🟡 中 | 可能发生，影响可控 | 建议制定预案，按需应对 |
| 🟢 低 | 偶尔发生，影响轻微 | 知悉即可，无需专项预案 |

---

## 风险清单

### R01 — 从零设计目录结构导致构建系统搭建效率低下

| 属性 | 内容 |
|------|------|
| **风险等级** | 🟡 中 |
| **来源洞察** | [洞察 1](docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md#洞察-1参考成熟项目结构可以大幅加速-docker-构建系统搭建)：参考成熟项目结构可以大幅加速 Docker 构建系统搭建 |
| **触发条件** | 目标项目无现有 Docker 构建系统；团队不熟悉 Docker 多阶段构建最佳实践；未事先寻找同类项目参考 |
| **早期预警信号** | 开始编写 Dockerfile 时频繁纠结目录组织方式；脚本文件散落在不同目录无统一规范；超过 30 分钟仍在设计目录结构 |
| **发生概率** | 高（无参考模板时几乎必然发生） |
| **忽略后果** | 脚本散落、维护困难；后期重构成本 3-5 倍；团队成员无法快速上手 |
| **应对措施** | 1. 启动前先搜索同类项目的 Docker 构建系统（至少 2 个参考项目）<br>2. 沿用成熟目录骨架：`lib/`（公共库）+ `build/`（构建脚本）+ `config/`（配置）+ `scripts/`（辅助脚本）<br>3. 参考 [可参考项目索引](docs/retrospective/assets/reference-project-index.md) 选择模板 |

---

### R02 — Sandbox/受限环境输出过滤导致调试盲飞

| 属性 | 内容 |
|------|------|
| **风险等级** | 🔴 高 |
| **来源洞察** | [洞察 2](docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md#洞察-2sandbox-环境对-docker-输出的过滤导致调试效率严重下降)：sandbox 环境对 docker 输出的过滤导致调试效率严重下降 |
| **触发条件** | 在 trae-sandbox 或类似受限环境中执行 docker 命令；CI/CD 环境对子进程输出有限制；使用远程执行代理 |
| **早期预警信号** | `docker run` 执行后无任何输出；`docker logs` 返回空；即使重定向到文件也捕获不到内容 |
| **发生概率** | 高（受限环境中几乎必然发生） |
| **忽略后果** | 每次验证额外增加 5-10 分钟调试延迟；复杂错误（如 docker 内部崩溃）完全无法诊断；可能将失败误判为成功 |
| **应对措施** | 1. 优先使用容器内验证脚本（`build-multistage.sh --verify`），避免依赖外部 `docker run` 输出<br>2. 采用文件化策略：将命令写入脚本→挂载到容器→执行→输出写入文件系统→读取文件<br>3. 使用 Python subprocess 捕获 exit code 作为最低限度验证<br>4. 在非受限环境（如 WSL 原生终端）中完成关键调试 |

---

### R03 — 多层命令嵌套引号转义失败

| 属性 | 内容 |
|------|------|
| **风险等级** | 🟡 中 |
| **来源洞察** | [洞察 3](docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md#洞察-3多层嵌套引号是-shell-脚本中最常见的错误来源)：多层嵌套引号是 shell 脚本中最常见的错误来源 |
| **触发条件** | 命令跨越 3 层以上执行环境（如 PowerShell → WSL → docker → bash -c → python -c）；使用 heredoc 在混合环境中；在 CI pipeline 中拼接动态命令 |
| **早期预警信号** | 命令中出现 3 层以上嵌套引号；在不同 shell 间切换时出现语法错误；heredoc 边界不匹配 |
| **发生概率** | 中（跨环境操作时较常见） |
| **忽略后果** | 每次调试 3-5 分钟，累计可观；代码可读性极差难以维护；运行时错误难以定位 |
| **应对措施** | 1. 超过 3 层嵌套时采用"文件化"策略：写入脚本文件→挂载→执行<br>2. 使用 Python subprocess 替代复杂 shell 命令<br>3. 参考 [文件化规避策略](docs/retrospective/patterns/code-patterns/shell-nested-quote-file-based-strategy.md) |

---

### R04 — Dockerfile 层顺序不当导致缓存全部失效

| 属性 | 内容 |
|------|------|
| **风险等级** | 🔴 高 |
| **来源洞察** | [洞察 4](docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md#洞察-4多阶段-dockerfile-的缓存策略决定了开发迭代效率)：多阶段 Dockerfile 的缓存策略决定了开发迭代效率 |
| **触发条件** | Dockerfile 中 `COPY . .` 放在 apt/pip 安装之前；未按变更频率排序层；未使用多阶段构建 |
| **早期预警信号** | 每次代码变更后所有层都重建；构建时间稳定在 15-40 分钟无缩短；`docker build` 输出中大量"Cache miss" |
| **发生概率** | 高（未刻意优化时几乎必然发生） |
| **忽略后果** | 首次 vs 二次构建差异 800 倍（3 秒 vs 40 分钟）；开发迭代效率极低；每次调试都需等待完整构建 |
| **应对措施** | 1. 设计 Dockerfile 时标注每层"变更频率"（低/中/高），低频层在前<br>2. 使用多阶段构建：base-system → base-builder → builder → runtime<br>3. 使用 `--target` 只构建需要的阶段<br>4. 构建后验证二次构建缓存命中率 > 90% |

---

### R05 — 老旧 C++ 项目编译兼容性问题

| 属性 | 内容 |
|------|------|
| **风险等级** | 🔴 高 |
| **来源洞察** | [洞察 5](docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md#洞察-5caffe-这种老旧框架的编译兼容性处理需要系统化方法)：老旧框架的编译兼容性处理需要系统化方法 |
| **触发条件** | 目标项目发布超过 5 年；目标 OS/编译器/Python 版本与原始开发环境差异大；使用 Makefile 而非 CMake 构建 |
| **早期预警信号** | 编译时出现头文件找不到；链接时 undefined reference；Python 绑定导入失败；setuptools 废弃函数警告 |
| **发生概率** | 极高（5 年以上 C++ 项目在新环境编译几乎必然遇到兼容性问题） |
| **忽略后果** | 兼容性问题消耗 30-40% 开发时间；每个问题需要单独排查修复；可能导致项目无法完成 Docker 化 |
| **应对措施** | 1. 启动前执行 6 项预检：BLAS 库 → Python 版本 → OpenCV 版本 → protobuf 版本 → C++ 标准 → Boost 版本<br>2. 参考 [编译兼容性预检清单](docs/retrospective/patterns/process-patterns/legacy-cpp-compilation-compatibility-checklist.md)<br>3. 在 Dockerfile 中预留编译标志修改空间（`CXXFLAGS`、`INCLUDE_DIRS`、`LIBRARY_DIRS`）<br>4. 每修复一个兼容性问题后立即记录，形成项目专属兼容性文档 |

---

### R06 — 知识闭环断裂：经验无法转化为可执行资产

| 属性 | 内容 |
|------|------|
| **风险等级** | 🟡 中 |
| **来源洞察** | [洞察 6](docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md#洞察-6操作-sop-文档化是知识闭环的最后一步)：操作 SOP 文档化是知识闭环的最后一步 |
| **触发条件** | 项目完成后仅做口头总结或简单记录；没有将操作步骤整理为可执行文档；团队成员变动 |
| **早期预警信号** | 复盘报告只有"分析"没有"操作步骤"；项目文档中无"快速开始"章节；3 个月后无人能复现构建流程 |
| **发生概率** | 中（时间压力下容易跳过文档化步骤） |
| **忽略后果** | 3 个月后需要重新排查所有兼容性问题；新人无法独立操作；知识留在个人脑中而非团队资产 |
| **应对措施** | 1. 将"SOP 创建"作为项目收尾的强制步骤<br>2. 按"前置条件→快速开始→详细步骤→验证→故障排查→关联文档"结构组织<br>3. 每个步骤提供可复制的命令<br>4. 参考 [SOP 标准化模板](docs/retrospective/patterns/process-patterns/ops-sop-standard-template.md) |

---

### R07 — 文档孤立：产出物无法被后续任务发现复用

| 属性 | 内容 |
|------|------|
| **风险等级** | 🟡 中 |
| **来源洞察** | [洞察 7](docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md#洞察-7知识库索引更新是文档可发现性的关键)：知识库索引更新是文档可发现性的关键 |
| **触发条件** | 创建新文档后未更新索引（README.md）；文档存放在非标准路径；知识库规模增长但索引未同步 |
| **早期预警信号** | 新增文档后无法从导航树找到；目录 README 中分类计数与实际文件数不一致；快速参考表中缺少新条目 |
| **发生概率** | 高（创建文档后容易忘记更新索引） |
| **忽略后果** | 文档复用率趋近于零；重复造轮子（不知道已有解决方案）；知识库变成"文档坟场" |
| **应对措施** | 1. 将"索引更新"作为文档创建/修改的强制步骤<br>2. 更新三类索引：分类表（新增条目）→ 计数更新 → 快速参考表<br>3. 在 SOP 模板和 extraction 指令中明确标注索引更新要求 |

---

## 风险热力图

| 风险 | 概率 | 影响 | 等级 | 核心应对 |
|------|------|------|------|---------|
| R01 从零设计目录 | 高 | 中 | 🟡 | 先找参考模板 |
| R02 输出过滤 | 高 | 高 | 🔴 | 文件化 + 容器内验证 |
| R03 引号嵌套 | 中 | 低 | 🟡 | 超过 3 层用文件化 |
| R04 缓存失效 | 高 | 高 | 🔴 | 标注变更频率，低频在前 |
| R05 编译兼容性 | 极高 | 高 | 🔴 | 6 项预检 + 预留编译标志 |
| R06 知识闭环断裂 | 中 | 中 | 🟡 | 收尾强制创建 SOP |
| R07 文档孤立 | 高 | 中 | 🟡 | 创建文档即更新索引 |

---

## 使用流程

1. **项目启动前**：逐项检查 R01-R05，确认已制定应对预案
2. **项目执行中**：关注 R02-R04 的预警信号，触发时立即执行应对措施
3. **项目收尾后**：检查 R06-R07，确保 SOP 已创建且索引已更新

---

## 关联资源

| 资源 | 路径 |
|------|------|
| 来源复盘报告 | [retrospective-caffe-docker-runtime-20260722/README.md](docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md) |
| 模式 1：参考模板复制法 | [docker-build-reference-template-copy.md](docs/retrospective/patterns/process-patterns/docker-build-reference-template-copy.md) |
| 模式 2：文件化策略 | [shell-nested-quote-file-based-strategy.md](docs/retrospective/patterns/code-patterns/shell-nested-quote-file-based-strategy.md) |
| 模式 3：编译兼容性预检 | [legacy-cpp-compilation-compatibility-checklist.md](docs/retrospective/patterns/process-patterns/legacy-cpp-compilation-compatibility-checklist.md) |
| 模式 4：SOP 标准化模板 | [ops-sop-standard-template.md](docs/retrospective/patterns/process-patterns/ops-sop-standard-template.md) |
| Caffe Docker SOP | [caffe-docker-sop.md](docs/knowledge/operations/caffe-docker-sop.md) |
| 可参考项目索引 | [reference-project-index.md](docs/retrospective/assets/reference-project-index.md) |