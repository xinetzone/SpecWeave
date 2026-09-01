---
id: "retrospective-py314t-conda-freethreading"
title: "Windows 11 建 py314t 免费线程 conda 环境里程碑复盘"
date: "2026-08-19"
type: "milestone-retrospective"
source: "与 AI 助手协作搭建 py314t no-GIL 环境并联调基准（Trae 会话）"
scope: "task"
category: "environment-setup"
---

# py314t conda 免费线程（no-GIL）环境 — 里程碑复盘报告

> **复盘主题**：在 Windows 11 + conda 上创建并验证 Python 3.14.6t（no-GIL）环境
> **复盘日期**：2026-08-19
> **项目范围**：环境创建 → GIL 验证 → 性能基准 → 环境迁移导出
> **报告类型**：任务级里程碑复盘（range=depth light，跳过 V 对抗审查）

***

## 一、项目概述

### 1.1 项目背景
需要在 Windows 11 原生系统（不引入 WSL）下，为 `external/libs/python/cpython` 的调试测试提供一个支持 no-GIL（free-threading）的 Python 3.14.6t 环境。

### 1.2 项目目标
- 创建 conda 免费线程环境 py314t（Python 3.14.6t）
- 验证 GIL 确已禁用（`sys._is_gil_enabled()==False`、SOABI 含 `cp314t`）
- 用 CPU 密集基准验证 no-GIL 的实际多线程收益
- 打通环境导出/迁移到标准 envs 目录的完整链路

### 1.3 交付物清单
| 交付物 | 路径 | 状态 |
|--------|------|------|
| py314t 环境（临时位→标准位） | `.temp/conda-envs/py314t` → `<USER_HOME>\anaconda3\envs\py314t` | 完成 |
| 基准脚本（多线程数扫描） | `.temp/gil_nogil_scan.py` | 完成 |
| 环境导出文件 | `.temp/environment.yml` | 完成（已去 prefix） |
| 使用说明 | [python-314t-conda-env-usage](../../../knowledge/tech/python-314t-conda-env-usage.md) | 完成 |
| 性能曲线图（归档） | [assets/gil-vs-nogil-curve.png](./retrospective-py314t-conda-freethreading-20260819-assets/gil-vs-nogil-curve.png) | 完成 |
| 扫描数据（归档） | [assets/scan-nogil.json](./retrospective-py314t-conda-freethreading-20260819-assets/scan-nogil.json) / [scan-gil.json](./retrospective-py314t-conda-freethreading-20260819-assets/scan-gil.json) | 完成 |
| 本复盘报告 | 本文件 | 完成 |

***

## 二、复盘环节

### 2.1 实施过程回顾

```mermaid
flowchart LR
  A[conda create py314t\n3.14.6t free-threading] --> B[落位 .temp/conda-envs\n沙箱拦截标准目录写入]
  B --> C[验证 GIL 禁用\nsys._is_gil_enabled False + cp314t]
  C --> D[基准验证\nthreading 3.36x / pool 3.97x]
  D --> E[导出环境\n-f py314t.yml 报错]
  E --> F[改为 environment.yml\nCONDA_ENVS_DIRS 定位]
  F --> G[create 重建\nyaml prefix 覆盖 -n 仍落 .temp]
  G --> H[删除 prefix 行\n重建可落标准目录]
```

### 2.2 关键节点分析
- **环境创建**：conda-forge 提供 win-64 的 `cp314t` free-threading 构建；沙箱无标准 envs 目录写权限，环境暂落工作区 `.temp`。
- **GIL 验证**：`sys._is_gil_enabled()==False` 且 SOABI=`cp314t-win_amd64`，确认使用免费线程运行时。
- **性能基准**：4 线程 CPU 密集任务较串行加速 3.36x（threading）/ 3.97x（pool），证明多线程真实并行。
- **导出报错**：`conda env export -f py314t.yml` 触发 `EnvironmentExporterNotDetected`。
- **重建回退**：`conda env create` 读取 yaml 内 `prefix:` 行，优先于 `-n` 指定的目标，环境仍创建到原 `.temp` 路径。

### 2.3 执行情况与结果数据
| 指标 | 值 |
|------|-----|
| 环境版本 | 3.14.6 free-threading build |
| GIL_enabled | False |
| SOABI | cp314t-win_amd64 |
| python_abi | 3.14=8_cp314t |

**多线程数扫描（每线程基准 6,000,000 次迭代 · CPU 密集）：**

| 线程数 | no-GIL 耗时 | no-GIL 加速 | 标准 GIL 耗时 | GIL 加速 |
|---|---|---|---|---|
| 2 | 0.133s | 1.91x | 0.409s | 1.11x |
| 4 | 0.074s | 3.42x | 0.401s | 1.13x |
| 8 | 0.048s | **5.26x** | 0.393s | 1.15x |
| 12 | 0.056s | 4.51x | 0.401s | 1.13x |

**性能曲线图：**

![GIL vs no-GIL 性能曲线](./retrospective-py314t-conda-freethreading-20260819-assets/gil-vs-nogil-curve.png)

### 2.4 成功经验
- conda-forge 免费线程构建直接可用，免去源码编译（事实 F-003/F-004）。
- `pinned` 文件持久化 `python_abi=*_cp314t`，避免后续 pip 安装关回 GIL（事实 F-007）。

### 2.5 存在问题
- 环境默认落在 `.temp`，不能直接在标准 envs 目录使用（事实 F-002）。
- `conda env export/import` 存在两处隐式规则导致命令不一致（事实 F-013/F-019）。

***

## 三、洞察环节

### 3.1 关键发现
| 洞察 | 陈述 | 证据 | 反常识 | 行动 |
|------|------|------|--------|------|
| I1 | conda-forge 在 win-64 原生提供 free-threading 构建，Windows 本地无需 WSL/编译源码 | F-003, F-004 | 此前假设 free-threading 平台受限、必须自定义构建 | Windows 上调试 no-GIL 优先用 `conda-forge::python-freethreading=*_cp314t` |
| I2 | no-GIL 对 CPU 密集真实加速，但任务过轻时加速比偏离理论值 15%~24% | F-010, F-011, F-012 | 基准越快越接近核心数，任务太小加速比失真 | 加大任务量并在带 GIL 的 py314 上做对照 |
| I3 | `export -f` 按文件名识别格式、`create` 时 yaml 的 `prefix` 优先于 `-n`，是两个隐藏陷阱 | F-013, F-018, F-019 | `-f` 非任意路径、`-n` 不一定覆盖 prefix | 导出用 `environment.yml` 约定名并移除 `prefix:` 行 |

### 3.2 规律认知
`conda env export` 的格式是**隐式文件名绑定**，而 `conda env create` 的落点由 yaml 内 `prefix:` 强绑定 —— 环境迁移的"导出路径"与"重建落点"两处规则都需要显式核对，不能依赖直觉。

### 3.3 潜在机会
- 补充带 GIL 的 py314 对照基准，量化 no-GIL 收益边界。
- 将本环境迁移路径沉淀为可复用模式并入库。
- 在真实 CPython 调试场景（`external/libs/python/cpython`）中应用 no-GIL 多线程并行。

***

## 四、导出环节

### 4.1 改进建议
| 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|------|---------|--------|---------|------|
| 基准任务过轻，加速比偏离理论值 | 增大单任务迭代量并做带 GIL 对照 | 中 | 收益曲线更贴近核心数 | 已完成 |
| 环境滞留 `.temp`，未在标准目录 | 用去 prefix 的 environment.yml 重建到标准 envs 目录 | 高 | `conda activate py314t` 全局可用 | 已完成 |
| export/create 隐式规则易踩坑 | 沉淀为模式 + 更新 USAGE 文档 | 高 | 后人复用不报错 | 待规划 |

### 4.2 行动计划
| 优先级 | 改进项 | 具体措施 | 建议时间 | 状态 |
|--------|--------|---------|---------|------|
| 高 | 标准位置重建 | 全新终端运行 `conda env create -n py314t -f .temp\environment.yml` 并 `conda env list` 核对 | 2026-08-19 | 已完成 |
| 高 | 模式沉淀 | 将"conda 自定义路径环境迁移"模式写入 patterns 目录 | 2026-08-19 | 待规划 |
| 中 | 精确基准 | 增大任务量的 no-GIL vs GIL 对照基准 | 2026-08-20 | 已完成 |
| 中 | 内存更新 | 将两处 conda 陷阱写入 project_memory | 2026-08-19 | 已完成 |

### 4.3 模式成熟度更新
| 模式 ID | 成熟度变化 | 触发原因 | 更新时间 | 验证/复用次数 |
|---------|-----------|---------|---------|-------------|
| conda-custom-env-migration（新增） | L1 | 本任务经验萃取，单案例 | 2026-08-19 | 1 |

### 4.4 后续优化方向
- 完成标准位置重建后，即可对 `external/libs/python/cpython` 目标工程进行 no-GIL 调试。
- 补充 GIL 对照组，形成可量化的 no-GIL 收益报告。

***

> **报告编制**：本文档基于本会话执行记录，遵循"事实 → 分析 → 洞察 → 建议"逻辑结构，所有数据均有事实依据支撑。
> **状态语义**：`待规划` / `进行中` / `已完成` / `已关闭`。