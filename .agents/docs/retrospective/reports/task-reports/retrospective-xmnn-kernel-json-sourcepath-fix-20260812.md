---
title: "xmnn kernel.json 源码路径暴露修复与验证报告"
date: 2026-08-12
session: sc-20260812-xmnn-kernel-json-sourcepath-fix
scenario: problem-solving
chain: F→V→C→R→I→E
source: "conversation sc-20260812-xmnn-kernel-json-sourcepath-fix"
category: task-reports
---

# xmnn kernel.json 源码路径暴露修复与验证报告

## R：复盘事实清单（G1门检查）

### 问题发现
- F-001: `xmnn-whl-builder/kernelspec/xmnn-whl-builder/kernel.json` 第14行 `env.PYTHONPATH` 指向 `/workspace/chaos/npuusertools:/workspace/chaos/npu_tvm/python:/workspace/chaos/npu_tvm/vta/python`
- F-002: `xmnn-runtime/kernelspec/xmnn-runtime/kernel.json` 第14行存在完全相同的源码 `PYTHONPATH`
- F-003: 两镜像均为 wheel 运行时镜像——tvm/vta/xmnn 已通过 pip/Nuitka 打包进 `/opt/conda`，源码目录仅构建期 bind mount，**final 镜像内不存在** `/workspace/chaos/npu_tvm`、`/workspace/chaos/npuusertools`
- F-004: kernel.json 由 Dockerfile `COPY` 层写入镜像（`/opt/venv/share/jupyter/kernels/<name>/` 与 `/opt/conda/share/jupyter/kernels/<name>/` 双份）

### 修复执行
- F-005: 移除两个 kernel.json 的 `PYTHONPATH` 键，仅保留 `PATH` 与 `CHAOS_ROOT`
- F-006: 依赖链确认——`xmnn-runtime` 从 `xmnn-whl-builder` 的 `/opt/xmnn-dist/` COPY wheel，须先重建 builder 再重建 runtime
- F-007: kernel.json 通过 `COPY` 层哈希缓存自动失效，无需 `--no-cache` 即拾取新文件
- F-008: 重建 `xmnn-whl-builder:latest` 成功（新镜像 ID `10e58f929417`）
- F-009: 重建 `xmnn-runtime:latest` 成功（新镜像 ID `ff89c83cd6cf`）
- F-010: 运行中 3 个 jupyter 测试容器（xmnn-whl-builder-jupyter / xmnn-runtime-jupyter / chaos-jupyter）基于旧镜像，需重建同步

### 验证结果
- F-011: whl-builder 镜像内 kernel.json 无 PYTHONPATH，`grep npu_tvm/npuusertools` 无残留（CLEAN）
- F-012: runtime 镜像内 venv + conda 两份 kernel.json 均无 PYTHONPATH，grep 无残留（CLEAN）
- F-013: 两镜像容器启动后全局 `PYTHONPATH=[]`（Dockerfile 本无 ENV PYTHONPATH）
- F-014: 两镜像 kernel 均注册可见（`/opt/venv/share/jupyter/kernels/<name>`）
- F-015: 重建后 3 个测试容器全部 `healthy`，kernel.json 均无源码路径残留

---

## I：核心洞察（G2门检查）

### 洞察1：wheel 镜像的 runtime 配置指向构建期源码路径 = 过期的架构残留
- **陈述**：wheel 打包镜像的 kernel.json 仍引用构建期 bind-mount 的源码路径，这些路径在 final 镜像中不存在，是「源码开发镜像」架构向「wheel 分发镜像」演进时遗留的配置残留。
- **证据**：F-001/F-002/F-003（kernel.json 指向不存在路径）、F-011/F-012（移除后干净）
- **反常识**：挑战了「kernel.json 的 PYTHONPATH 是运行时必需」的假设——wheel 镜像中包已在 site-packages，PYTHONPATH 指向源码不仅多余，还暴露内部目录结构。
- **行动**：wheel 镜像的 kernel env 只保留 `PATH` + 运行时必要变量，删除构建期源码路径。

### 洞察2：COPY 层哈希缓存让配置修复"零成本"生效，无需强制重建
- **陈述**：kernel.json 是 `COPY` 进镜像的独立文件，Docker 以内容哈希做 COPY 层缓存——文件一改，该层及后续 kernel 注册层自动失效，无需 `--no-cache` 全量重建。
- **证据**：F-006/F-007（COPY 层哈希缓存机制）、F-008/F-009（常规构建即拾取新文件）
- **反常识**：挑战了「配置改了必须 --no-cache 重建」的常见直觉——对 COPY 进镜像的独立配置文件，层缓存会正确感知内容变化。
- **行动**：修改镜像内独立配置文件后，常规 `build.sh` 重建即可；`--no-cache` 仅用于 bind-mount 源码（其哈希不被层缓存追踪）。

### 洞察3：测试环境容器必须与镜像同步重建，否则修复不落地
- **陈述**：镜像重建只更新镜像层；运行中的容器仍持有旧文件系统状态。若只重建镜像不重建容器，测试环境仍暴露源码路径，修复形同虚设。
- **证据**：F-010（容器基于旧镜像 ID）、F-015（重建后容器才干净）
- **反常识**：挑战了「重建镜像 = 修复生效」的假设——运行中的容器是独立实例，需显式重建/重启才能应用新镜像内容。
- **行动**：镜像与测试容器成对管理：镜像重建后，基于该镜像的测试容器须同步重建并验证。

---

## V：对抗审查（F 后强制）

### 魔鬼代言人视角
1. **攻击**：删除 PYTHONPATH 会不会导致 kernel 启动时 import tvm 失败？
   - **采纳修正**：通过容器内实际启动验证——重建后 kernel 注册可见（F-014）、测试容器 healthy（F-015），且 wheel 包已装进 `/opt/conda`，import 无需 PYTHONPATH。
2. **攻击**：`/workspace/chaos` 是否还有其它用途需要 CHAOS_ROOT 之外的路径？
   - **采纳修正**：保留 `CHAOS_ROOT`，仅删除指向源码的 `PYTHONPATH`；核对两镜像 Dockerfile 均无 `ENV PYTHONPATH`，全局环境本就为空（F-013）。

### 新人视角
1. **攻击**：其它 kernel.json 是否也有同样的路径残留？
   - **采纳修正**：全仓扫描确认唯一含源码 PYTHONPATH 的 kernel.json 仅这两个（已修）；`config/jupyter/kernels/npu/kernel.json` 属已退役的 dev 开发镜像（源码本应挂载），不在 wheel 分发镜像范围内，未误改。

### 老板视角
1. **攻击**：改动是否影响客户运行时功能？
   - **采纳修正**：修复仅删除不存在的路径引用，不改包、不改 kernel 注册逻辑；运行时功能由 wheel 包保证，验证 11 项（whl-builder）与 10 项（runtime）均通过。

### 未来视角（6个月后）
1. **攻击**：若未来新增 kernel 或改镜像架构，如何防止路径残留复发？
   - **采纳修正**：kernel.json 应作为「仅运行时必需 env」的单一事实来源；建议后续在 verify 脚本中增加「kernel.json 不含 npu_tvm/npuusertools 路径」的防复发检查项。

---

## 修复与同步动作汇总（C 阶段）

| 动作 | 对象 | 状态 |
|------|------|------|
| 删除源码 PYTHONPATH | whl-builder kernel.json | ✅ |
| 删除源码 PYTHONPATH | runtime kernel.json | ✅ |
| 重建镜像 | xmnn-whl-builder:latest | ✅ |
| 重建镜像 | xmnn-runtime:latest | ✅ |
| 重建测试容器 | xmnn-whl-builder-jupyter | ✅ healthy |
| 重建测试容器 | xmnn-runtime-jupyter | ✅ healthy |
| 重建测试容器 | chaos-jupyter | ✅ healthy |
| 镜像内残留扫描 | 两镜像 | ✅ 无 npu_tvm/npuusertools |

## 防复发建议
1. 在 `verify-kernel-registration.sh` 中新增检查：kernel.json `env` 不含 `npu_tvm`/`npuusertools` 路径。
2. 后续 wheel 镜像 kernel 配置统一原则：仅含 `PATH` + 运行时必需变量，禁止携带构建期源码路径。
