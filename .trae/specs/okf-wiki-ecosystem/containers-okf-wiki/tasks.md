# Containers 生态 OKF Wiki 生成 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 初始化 containers 技术域目录结构
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `doc/bundles/containers/` 目录
  - 创建 `doc/bundles/containers/index.md` 域索引（含 okf_version frontmatter 和 toctree）
  - 预留 11 个子项目的 bundle 目录位置
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录 `doc/bundles/containers/` 存在
  - `programmatic` TR-1.2: index.md 包含 `okf_version: "0.2"` frontmatter
  - `programmatic` TR-1.3: index.md 包含 {toctree} 指令预留子 bundle 位置
- **Notes**: 先不更新总 index.md，待所有 bundle 完成后统一更新

## [ ] Task 2: R阶段 - conmon 项目事实采集
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 阅读 conmon 源码（C语言，src/ 目录）
  - 提取可验证事实：核心数据结构、主要函数、CLI参数、cgroup/ctrl/oom 等模块功能
  - 所有事实编号 F-xxx，写入 spec 目录 facts-conmon.md
  - G1质量门：事实无推断词
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: facts-conmon.md 存在，包含 ≥20 条编号事实
  - `human-judgement` TR-2.2: 事实中不出现"用于"/"目的是"/"设计为"等推断性表述
  - `programmatic` TR-2.3: 每条事实附带源码路径引用
- **Notes**: conmon 是 C 项目，重点关注 conmon.c 主入口、cgroup、ctr_exit、ctrl、oom 模块

## [ ] Task 3: R阶段 - fuse-overlayfs 项目事实采集
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 阅读 fuse-overlayfs 源码（Rust，src/ 目录）
  - 提取核心模块：overlay、copyup、direct、layer、node 等
  - 事实写入 spec/facts-fuse-overlayfs.md
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: facts-fuse-overlayfs.md 存在，包含 ≥15 条事实
  - `human-judgement` TR-3.2: 事实零推测
- **Notes**: FUSE 文件系统实现，重点关注 overlay 逻辑

## [ ] Task 4: R阶段 - 其余9个项目事实采集（分批）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 批量采集 conmon-rs、libocispec、olot、omlmd、podman-py、podman-compose、qm、toolbox、ai-lab-recipes 的事实
  - 每个项目独立 facts 文件
  - Python项目重点关注模块结构和公开API；Go项目关注cmd/和pkg/；Rust项目关注src/
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 9 个 facts-*.md 文件均存在
  - `human-judgement` TR-4.2: 每个项目 ≥10 条事实，零推测
- **Notes**: 可通过 general_purpose_task 并行委派

## [ ] Task 5: I阶段 - 架构洞察与知识地图设计
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 基于所有 facts 文件，提炼每个项目 3-5 个核心洞察
  - 设计 containers 域知识地图：
    - 分组：容器运行时（conmon/conmon-rs）、存储（fuse-overlayfs）、规范与工具（libocispec）、Python生态（podman-py/olot/omlmd）、虚拟机（qm）、开发工具（toolbox/podman-compose）、AI（ai-lab-recipes）
  - 确定每个 bundle 的 concepts 列表（3-5个核心概念）
  - 洞察写入 spec/insights.md
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-5.1: 每个项目的洞察包含陈述/证据/反常识/行动四元组
  - `human-judgement` TR-5.2: 知识地图有清晰的学习路径（基础→进阶→生态）
- **Notes**: G2质量门：洞察四元组完整

## [ ] Task 6: E阶段 - 第一批 Bundle 生成（conmon, conmon-rs）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 信源先行：先生成每个 bundle 的 references/ 信源文件
  - 分批生成 concepts/（每批≤7文档）
  - 生成 examples/
  - 最后生成 index.md
  - 遵循 OKF v0.2 frontmatter 规范
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: conmon bundle 结构完整（concepts≥3, examples≥2, references≥1）
  - `programmatic` TR-6.2: conmon-rs bundle 结构完整
  - `programmatic` TR-6.3: 所有文档 frontmatter 字段齐全
  - `programmatic` TR-6.4: 交叉链接使用 / 开头路径且目标存在
- **Notes**: 每批≤7文档，references先于concepts生成

## [ ] Task 7: E阶段 - 第二批 Bundle 生成（fuse-overlayfs, libocispec）
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 同 Task 6 流程，生成 fuse-overlayfs 和 libocispec 两个 bundle
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: fuse-overlayfs bundle 结构完整
  - `programmatic` TR-7.2: libocispec bundle 结构完整
- **Notes**: libocispec 是 C/Rust 双语言项目，注意区分

## [ ] Task 8: E阶段 - 第三批 Bundle 生成（Python工具：olot, omlmd, podman-py）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 生成 olot、omlmd、podman-py 三个 Python 项目的 bundle
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 三个 Python bundle 结构完整
  - `programmatic` TR-8.2: Python API 示例语法正确
- **Notes**: podman-py 是较成熟的绑定库，API 文档可更详细

## [ ] Task 9: E阶段 - 第四批 Bundle 生成（podman-compose, toolbox, qm）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 生成 podman-compose（Python）、toolbox（Go）、qm（Shell/Python混合）三个 bundle
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: 三个 bundle 结构完整
- **Notes**: qm 是 QEMU/KVM 容器化工具，子系统较多，重点关注核心架构

## [ ] Task 10: E阶段 - 第五批 Bundle 生成（ai-lab-recipes）
- **Priority**: low
- **Depends On**: Task 9
- **Description**:
  - 生成 ai-lab-recipes bundle
  - 若内容较少可适当精简 concepts 数量
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-10.1: bundle 存在且结构合规
- **Notes**: 这是 AI 容器示例仓库，可能以 examples 为主

## [ ] Task 11: V阶段 - 独立验证与修复
- **Priority**: high
- **Depends On**: Task 6, Task 7, Task 8, Task 9, Task 10
- **Description**:
  - 结构检查：所有 bundle 目录结构合规
  - Frontmatter 检查：所有非保留文件有完整 frontmatter
  - Grep API 验证：对文档中引用的关键类名/函数名在源码中验证存在性
  - 链接检查：所有交叉引用有效
  - Index 完整性检查：各级 index.md 包含所有子文档
  - 输出检查报告，逐一修复问题
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-11.1: Grep 验证 ≥30 个关键 API 标识符存在
  - `programmatic` TR-11.2: 无断链
  - `programmatic` TR-11.3: index.md 无遗漏文档
  - `human-judgement` TR-11.4: 虚构 API 数量为 0
- **Notes**: G4质量门，重点拦截虚构API

## [ ] Task 12: 更新总索引并运行质量门
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 更新 `doc/bundles/containers/index.md` 的 toctree，包含所有 11 个子 bundle
  - 更新 `doc/bundles/index.md`：
    - 在 mermaid 生态关系图中加入 containers 域
    - 在十域导航中加入 containers 域章节
    - 在 hidden toctree 中加入 containers/index
    - 更新 total_bundles 计数（248+11=259）和 groups/domains 计数
  - 在 awesome-okf-xs 目录运行 `invoke gates.all`
  - 修复所有质量门报告的问题
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-12.1: `invoke gates.toctrees` 通过
  - `programmatic` TR-12.2: `invoke gates.utf8` 通过
  - `human-judgement` TR-12.3: 总索引中 containers 域导航完整
- **Notes**: 最后一步，确保构建完整性

## [ ] Task 13: C阶段 - 复盘与模式沉淀
- **Priority**: medium
- **Depends On**: Task 12
- **Description**:
  - 回顾本次任务执行过程
  - 记录顺利点和问题点
  - 如发现新反模式，补充到 source-code-to-okf-wiki 模式库
- **Acceptance Criteria Addressed**: （过程性任务）
- **Test Requirements**:
  - `human-judgement` TR-13.1: 生成 log.md 更新记录
- **Notes**: 可选，时间充裕时执行
