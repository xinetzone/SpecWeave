# Tasks

> 目标：为 ai/Dockerfile、xmnn-whl-builder、xmnn-runtime 三个环境的 Jupyter 内核分配全局唯一名称，并统一挂载 `d:\spaces\SpecWeave\external\chaos`，验证挂载路径与权限。涉及 Dockerfile 修改时，先读对应 `.agents/rules/dockerfile.md` 规范。

## Phase 1：环境盘点与命名方案
- [x] Task 1: 盘点三个内核当前配置，确定唯一命名方案
  - [x] 1.1 读取 ai/Dockerfile 的 `npu` 内核、whl-builder 的 `xmnn-conda`、runtime 的 `xmnn-conda` 三处 kernel.json 与注册逻辑
  - [x] 1.2 确认唯一命名：`npu` / `xmnn-whl-builder` / `xmnn-runtime`，及各自 display_name
  - [x] 1.3 确认统一挂载点（容器内路径 `/workspace/chaos`）与环境变量命名（`CHAOS_ROOT` / PYTHONPATH 追加）
  - 验证：三处配置清单与命名映射表输出，无旧名残留规划遗漏 ✅

## Phase 2：xmnn-whl-builder 内核重命名 + 挂载
- [x] Task 2: 重命名 whl-builder 内核为 `xmnn-whl-builder` 并注入 external/chaos 挂载
  - [x] 2.1 将 `kernelspec/xmnn-conda/kernel.json` 重命名为 `kernelspec/xmnn-whl-builder/kernel.json`
  - [x] 2.2 更新 kernel.json：display_name 为 `Python 3.14 (xmnn whl-builder)`，env 增加 `CHAOS_ROOT=/workspace/chaos` 与 PYTHONPATH 追加
  - [x] 2.3 更新 `xmnn-whl-builder/Dockerfile` 内核注册块（COPY 源路径、`/opt/venv/share/jupyter/kernels/xmnn-whl-builder`、`/opt/conda/share/jupyter/kernels/xmnn-whl-builder`、校验 grep）
  - 验证：Dockerfile 中无残留 `xmnn-conda` 引用 ✅；kernel.json 内容正确 ✅

## Phase 3：xmnn-runtime 内核重命名 + 挂载
- [x] Task 3: 重命名 runtime 内核为 `xmnn-runtime` 并注入 external/chaos 挂载
  - [x] 3.1 将 `kernelspec/xmnn-conda/kernel.json` 重命名为 `kernelspec/xmnn-runtime/kernel.json`
  - [x] 3.2 更新 kernel.json：display_name 为 `Python 3.14 (xmnn runtime)`，env 增加 `CHAOS_ROOT=/workspace/chaos` 与 PYTHONPATH 追加
  - [x] 3.3 更新 `xmnn-runtime/Dockerfile` 内核注册块（COPY 源路径、两处 kernels 目录、校验 grep）
  - 验证：Dockerfile 中无残留 `xmnn-conda` 引用 ✅；kernel.json 内容正确 ✅

## Phase 4：ai/Dockerfile 开发内核 + 挂载
- [x] Task 4: 为 ai/Dockerfile 的 `npu` 内核注入 external/chaos 挂载
  - [x] 4.1 更新 `config/jupyter/kernels/npu/kernel.json`：display_name 为 `Python 3 (NPU Dev)`，env 增加 `CHAOS_ROOT=/workspace/chaos` 与 PYTHONPATH 追加
  - [x] 4.2 同步更新 `scripts/setup-npu-kernel.sh` 中内联生成的 kernel.json 模板
  - 验证：脚本与静态 kernel.json 两处 env 一致 ✅

## Phase 5：挂载与权限验证
- [x] Task 5: 编写/运行挂载路径与权限验证
  - [x] 5.1 提供容器内验证命令/脚本（`scripts/verify-chaos-mount.sh`）：`ls -ld /workspace/chaos`、读取 external/chaos 下资源、`echo $CHAOS_ROOT`
  - [x] 5.2 在 WSL docker run 挂载 external/chaos 中验证挂载点存在、可读、权限正确
  - 验证：9/9 PASS（挂载点存在、可读、可写、npuusertools/npu_tvm/ai/models 可访问）✅

## Phase 6：全流程验证与提交
- [x] Task 6: 核对 checklist 并原子提交
  - [x] 6.1 逐项核对 checklist.md 全部通过
  - [x] 6.2 通过原子提交（单一职责，feat(jupyter-kernel)，15 文件变更）

# Task Dependencies
- [Task 1] 无依赖（盘点）
- [Task 2] 依赖 [Task 1]
- [Task 3] 依赖 [Task 1]
- [Task 4] 依赖 [Task 1]
- [Task 5] 依赖 [Task 2, Task 3, Task 4]（需三处配置就绪）
- [Task 6] 依赖 [Task 5]
