---
id: "retro-20260811-xmnn-runtime-kernelspec-path"
title: "SpecWeave / external/chaos/ai/xmnn-runtime Kernelspec 路径不一致导致 UI 不可见复盘"
date: "2026-08-11"
scope: "problem"
type: "retrospective-report"
source: "2026-08-11 xmnn-runtime 镜像固化 Jupyter xmnn-conda kernel 后，kernel 在 CLI 可见但 Jupyter UI 不可见的排查与修复"
tags: ["seven-concepts", "problem-retro", "xmnn-runtime", "jupyter", "kernelspec", "docker", "path-resolution"]
related_patterns: ["compiled-wheel-runtime-image-build", "dockerfile-runtime-logical-layering", "context-aware-path-resolution"]
---

# SpecWeave / external/chaos/ai/xmnn-runtime Kernelspec 路径不一致复盘报告

> **项目**：`external/chaos/ai/xmnn-runtime`
> **宿主工程**：`SpecWeave`
> **方法论**：七概念方法论编排（问题复盘链路：`R→I→E→C`）
> **报告日期**：2026-08-11
> **相关文档**：
> - 镜像构建：[Dockerfile](../../../external/chaos/ai/xmnn-runtime/Dockerfile)
> - kernel 配置：[kernel.json](../../../external/chaos/ai/xmnn-runtime/kernelspec/xmnn-conda/kernel.json)
> - 使用说明：[README.md](../../../external/chaos/ai/xmnn-runtime/README.md)

***

## 一、概述

在 `xmnn-runtime` 镜像中固化 Jupyter `xmnn-conda` kernel（`tvm`/`vta`/`xmnn` 安装在 `/opt/conda`，Jupyter 服务在 `/opt/venv`）后，出现一个隐蔽问题：

> **`jupyter kernelspec list`（CLI）能看到 `xmnn-conda`，但 Jupyter Web UI 里选不到该 kernel。**

该问题对"一次成功"式构建验证极具迷惑性——构建期校验通过不代表真实用户场景可用。

---

## 二、复盘范围

本次复盘覆盖：

- `xmnn-runtime` 镜像 Dockerfile final 阶段 kernel 固化逻辑
- Jupyter server 与 CLI kernelspec 搜索路径的差异
- 排查方法与修复过程
- 防复发加固措施

本次复盘不包含：

- XMNN 推理功能本身
- 其他镜像（whl-builder 等）的 kernel 固化

---

## 三、方法论说明

本报告使用七概念方法论进行结构化复盘，本次属于**问题复盘**场景，使用标准链路：

`R → I → E → C`

各阶段产出物对应质量门：

- `G1`（R 事实无因果化）
- `G2`（I 洞察四元组：现象/根因/影响/建议）
- `G3`（E 模式可迁移：触发条件/核心步骤/反模式）
- `G4`（C 行动项原子化）

---

## 四、R（Retrospective 复盘）

### 4.1 事实回顾

按时间顺序还原排查与修复过程：

#### 阶段一：固化 kernel 到 `/opt/conda/share/jupyter/kernels`

在 `xmnn-runtime` Dockerfile final 阶段新增 `KERNEL_EOF` RUN 块：

- 在 conda 环境安装 `ipykernel`
- 将 `kernel.json` 复制到 `/opt/conda/share/jupyter/kernels/xmnn-conda/`
- 校验：`/opt/venv/bin/python -m jupyter kernelspec list | grep xmnn-conda`（CLI 校验，通过）

镜像重建成功，10 项运行时自检 + 冒烟测试全部通过。

#### 阶段二：构建期校验通过，但 UI 不可见

用户反馈：**Jupyter Web UI 里没有 `xmnn-conda` kernel**。

#### 阶段三：确认镜像与 kernel 注册无误

逐项排查：

| 检查项 | 结果 |
|--------|------|
| 容器是否用新镜像 | 是（`xmnn-runtime:latest`，Created 23:10） |
| 容器内 `kernelspec list` | 显示 `xmnn-conda` 于 `/opt/conda/share/jupyter/kernels/xmnn-conda` |
| `kernel.json` 是否存在且有效 | 存在，JSON 合法，argv 指向 `/opt/conda/bin/python` |
| **运行中 server API `/api/kernelspecs`** | **仅返回 `python3`，不含 `xmnn-conda`** |

关键事实：**server 实际返回给前端的 kernel 列表里没有 `xmnn-conda`**，与 CLI 结论矛盾。

#### 阶段四：用新容器复现，排除"旧进程缓存"

起一个全新一次性容器并启动 server，查询 `/api/kernelspecs`：

- 结论：**新 server 同样只返回 `python3`**，排除"旧进程/缓存"因素，为系统性问题。

#### 阶段五：定位路径差异

对比 CLI 与 server 的搜索路径：

- `jupyter --paths`（venv python）的 **data** 路径：
  - `/opt/venv/share/jupyter`
  - `/root/.local/share/jupyter`
  - `/usr/local/share/jupyter`
  - `/usr/share/jupyter`
  - **不含 `/opt/conda/share/jupyter`**
- `jupyter kernelspec list --debug` 却显示搜索到 `/opt/conda/share/jupyter/kernels`

结论：**CLI 通过 conda 前缀检测额外解析到 `/opt/conda/share/jupyter`，而 Jupyter server 只搜索其严格 data 路径，不含 `/opt/conda/share/jupyter`。**

#### 阶段六：验证修复路径

将 kernel 复制到 server 确定搜索的路径并查 API：

- 注册到 `/root/.local/share/jupyter/kernels/xmnn-conda/` → server API 立即返回 `xmnn-conda`
- 注册到 `/opt/venv/share/jupyter/kernels/xmnn-conda/` → server API 与 CLI 均可见

#### 阶段七：修复并重建

- Dockerfile 改为**主注册 `/opt/venv/share/jupyter/kernels/xmnn-conda/`，同步一份 `/opt/conda/share/jupyter/kernels/xmnn-conda/`**
- 重建镜像，重建容器，验证 server `/api/kernelspecs` 返回 `xmnn-conda` ✅

---

## 五、I（Insight 洞察）

### 5.1 现象

`jupyter kernelspec list`（CLI）能看到某 kernel，但 Jupyter Web UI（server）选不到。

### 5.2 根因

`jupyter_core.paths.jupyter_path()` 在多解释器环境下的解析存在**上下文差异**：

- **CLI 上下文**：`jupyter kernelspec list` 通过 `sys.prefix` 的 conda 前缀检测，额外附加 `/opt/conda/share/jupyter`，因此能发现注册在 `/opt/conda` 的 kernel。
- **Jupyter server 上下文**：`jupyter_server` 的 `KernelSpecManager` 数据目录基于其自身 `sys.prefix`（`/opt/venv`）解析为严格集合（`/opt/venv/share`、`~/.local/share`、`/usr/local/share`、`/usr/share`），**不含** `/opt/conda/share/jupyter`，因此丢弃了注册在 `/opt/conda` 的 kernel。

简言之：**kernel 注册位置必须落在"使用者（server/UI）实际读取的数据路径"内，而不是 CLI 的附加路径内。**

### 5.3 影响

- 构建期用 CLI 校验 kernel 注册 = **假阳性**：CLI 通过，真实 UI 场景失败。
- 浪费一次完整镜像重建（约数分钟至十余分钟）与排查时间。
- 若未及时拦截，会以"构建成功"的假象交付，实际用户不可用。

### 5.4 建议

- kernel 固化到 **server 实际搜索的数据路径**（本环境为 `/opt/venv/share/jupyter/kernels`），并同步 `/opt/conda` 供 CLI 工具。
- 校验应上升到 **server API 级**（`GET /api/kernelspecs`），而非仅 CLI。
- 将"CLI 可见 ≠ UI 可见"纳入多解释器环境 kernel 注册的既有陷阱清单。

---

## 六、E（Extraction 萃取）

### 6.1 模式：Jupyter Kernel 注册须对准"使用者读取路径"

**触发条件**：

- 多解释器环境：Jupyter 服务位于 venv（`/opt/venv`），目标包位于 conda（`/opt/conda`）。
- 需要固化一个指向 conda 解释器的 kernel。

**核心步骤**：

1. 确定 Jupyter **server** 的实际数据路径：`/opt/venv/bin/python -m jupyter --paths`，取 **data** 列表。
2. 将 `kernel.json` 注册到 server data 路径首位（如 `/opt/venv/share/jupyter/kernels/<name>/`）。
3. 同步一份到 CLI 可见路径（如 `/opt/conda/share/jupyter/kernels/<name>/`）。
4. **用 server API 校验**：`curl http://<host>/api/kernelspecs?token=<token>` 确认返回该 kernel。

**反模式**：

- 只注册到 `/opt/conda/share/jupyter/kernels`（CLI 可见，server/UI 不可见）。
- 只用 `jupyter kernelspec list`（CLI）作为注册成功的唯一校验。

### 6.2 迁移验证

- 本环境验证：注册 `/opt/venv/share/jupyter/kernels` 后，server API 与 CLI 均可见。
- 该模式适用于任何"server 与 CLI 解释器/前缀不同"的容器或 venv+conda 组合。

---

## 七、C（原子行动项 / 预防闭环）

以下变更已完成或建议，确保重建镜像不再复发：

| # | 行动项 | 状态 | 验收标准 |
|---|--------|------|----------|
| 1 | Dockerfile 主注册 `/opt/venv/share/jupyter/kernels/xmnn-conda/`，同步 `/opt/conda/` | ✅ 已完成 | `docker run --rm <img> /opt/venv/bin/python -m jupyter kernelspec list` 显示 xmnn-conda |
| 2 | 重建镜像并用 server API 验证 | ✅ 已完成 | `GET /api/kernelspecs` 返回 `xmnn-conda` |
| 3 | 更新项目记忆（纠正"注册到 /opt/conda"错误结论） | ✅ 已完成 | 记忆文档记录正确路径 |
| 4 | （建议）Dockerfile 构建期增加 server API smoke test | ⏳ 建议 | 构建后启动临时 server 并断言 `/api/kernelspecs` 含 xmnn-conda |

> 第 4 项为防复发加固建议：将校验从"CLI 可见"升级为"server UI 可见"，避免再次出现"构建通过但用户不可用"。

---

## 八、结论

本次问题的本质是 **Jupyter CLI 与 server 对 kernelspec 数据路径的解析不一致**：CLI 通过 conda 前缀检测附加 `/opt/conda/share/jupyter`，而 server 只消费其严格数据路径。修复方法是将 kernel 注册到 server 真正读取的 `/opt/venv/share/jupyter/kernels`（并同步 `/opt/conda` 供 CLI），同时把校验口径从 CLI 提升到 server API，形成"修复→预防→闭环"的完整闭环。