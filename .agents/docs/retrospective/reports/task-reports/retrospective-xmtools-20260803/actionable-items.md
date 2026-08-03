# XMNN 复盘行动项清单（actionable-items）

> 质量门 G4：每个行动项满足单一职责、可独立验证、有验收标准。

---

## 行动项汇总

| ID | 行动项 | 优先级 | Owner | 来源 | 状态 |
|---|---|---|---|---|---|
| A-01 | 验证既有 wheel 通过 11 项检查 | P0 | xmnn 构建 | 复盘交付目标 | 待执行 |
| A-02 | 构建并导出生产级 Docker 镜像 | P0 | xmnn 构建 | 复盘交付目标 | 待执行 |
| A-03 | 清理 CMakeLists.txt 死代码块 | P1 | 开发者 | P0-1 | 待执行 |
| A-04 | 统一 pyproject 与 run-build.sh 构建策略 | P1 | 开发者 | P0-2/I-01 | 待执行 |
| A-05 | 评估 `_libs` 收敛到包内 + 去全局 ldconfig | P2 | 开发者 | P1-1/I-03 | 待评估 |
| A-06 | dev 镜像按需装 torch，runtime 移除 opencv | P2 | 开发者 | P1-2/P1-3 | 待评估 |
| A-07 | 复盘报告归档 + 索引更新 | P0 | 复盘 | 复盘闭环 | 待执行 |
| A-08 | 修复变更原子提交 | P0 | 复盘 | C 原子提交 | 待执行 |

---

## 详细行动项

### A-01 验证既有 wheel 通过 11 项检查
- **优先级**: P0
- **Owner**: xmnn 构建
- **内容**: 使用 `xmnn-dev:llvm22` 镜像执行 `verify-wheel.sh`，对 `dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl` 运行 import tvm/vta/xmnn、_libs、libtvm.so、tvm.build(llvm)、relay/std、vta_hw/config、bootstrap.pth、数据目录、依赖完整性等 11 项检查。
- **验收标准**: 11 项全部 PASS，保证 wheel 可用。

### A-02 构建并导出生产级 Docker 镜像
- **优先级**: P0
- **Owner**: xmnn 构建
- **内容**: 基于既有 wheel 构建 runtime 镜像（ubuntu:26.04 + Miniconda + Python 3.14 + xmnn wheel，空 ENTRYPOINT，时区 Asia/Shanghai），镜像内冒烟测试，`docker save` 导出 tar。
- **验收标准**: 镜像可运行，`docker load` 还原后 import tvm/vta/xmnn + tvm.build 通过。

### A-03 清理 CMakeLists.txt 死代码块
- **优先级**: P1
- **Owner**: 开发者
- **内容**: 删除 CMakeLists.txt 第 39-55 行被注释掉的 xmnn 源码安装块。
- **验收标准**: 删除后 `cmake` 配置仍通过，wheel 构建不受影响。

### A-04 统一 pyproject 与 run-build.sh 构建策略
- **优先级**: P1
- **Owner**: 开发者
- **内容**: 明确单一构建策略——以 `--no-isolation` 系统工具为准，从 pyproject `build-system.requires` 移除 cmake/ninja（或明确保留隔离构建），消除 run-build.sh 的 sed patch 依赖。
- **验收标准**: pyproject 与 run-build.sh 不再互相矛盾，非 Docker 环境可复现构建。

### A-05 评估 `_libs` 收敛到包内
- **优先级**: P2
- **Owner**: 开发者
- **内容**: 评估将 `_libs` 从 site-packages 根目录收敛到 `xmnn/_libs`，依赖 `$ORIGIN` RPATH 替代 runtime 全局 ld.so.conf 注册。
- **验收标准**: 收敛后 wheel 在干净环境仍可加载 libtvm，无全局链接器污染。

### A-06 镜像按需依赖分流
- **优先级**: P2
- **Owner**: 开发者
- **内容**: dev 镜像默认不装 torch/torchvision（改 `--build-arg` 按需）；runtime 移除 opencv-python-headless，由 `xmnn[examples]` 按需安装。
- **验收标准**: dev/runtime 镜像体积显著下降，核心功能不受影响。

### A-07 复盘报告归档 + 索引更新
- **优先级**: P0
- **Owner**: 复盘
- **内容**: 将三件套（README/insight-extraction/actionable-items）归档至 `retrospective-xmtools-20260803/`，更新 task-reports/README.md 索引。
- **验收标准**: 归档目录存在，索引文件含本次复盘条目。

### A-08 修复变更原子提交
- **优先级**: P0
- **Owner**: 复盘
- **内容**: 对本轮修复变更执行原子提交（Conventional Commits，中文描述）。
- **验收标准**: 提交信息符合规范，单一职责，可独立验证。