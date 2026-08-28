# Tasks

## Phase 0：环境准备（前置门禁）
- [x] Task 0: 验证 jupyter 容器与内嵌 rootless Podman 就绪
  - [ ] 0.1 确认 jupyter-podman-rootless 容器运行中（`bash bin/jpman start` / `jpman info`）
  - [ ] 0.2 容器内验证 rootless Podman 可用：`podman --cgroup-manager=cgroupfs info`（DinP 配置：fuse-overlayfs/crun/subuid）
  - [ ] 0.3 容器内磁盘空间检查（基础镜像 + whl-builder + ccache 构建缓存，建议 ≥40GB）
  - [ ] 0.4 确认宿主机（WSL Podman）存在 `devcontainer-base:onnx-quantized-latest` 镜像
  - 验证：容器内 `podman info` 正常返回且存储驱动为 fuse-overlayfs

## Phase 1：创建自包含副本
- [x] Task 1: 复制 xmnn-whl-builder 到 .temp 并自包含化
  - [ ] 1.1 复制 `external/chaos/ai/xmnn-whl-builder` → `apps/containers/jupyter-podman-rootless/.temp/xmnn-whl-builder`（排除 `logs/`、`.build-cache/`）
  - [ ] 1.2 将 `external/chaos/ai/scripts/lib/logging.sh` 复制到副本内 `scripts/lib/logging.sh`，并修改副本 `build.sh` 的 source 路径指向副本内位置
  - [ ] 1.3 检查并转换副本内所有 `.sh` 脚本为 LF 行尾（CRLF 在 Linux 容器内会语法错误），逐一 `bash -n` 校验
  - [ ] 1.4 在 `.temp/README.md` 记录副本用途与容器内使用命令（遵循 .temp 目录约定）
  - 验证：容器内 `bash /workspace/.temp/xmnn-whl-builder/build.sh --help` 正常输出

## Phase 2：基础镜像导入
- [x] Task 2: 导入 devcontainer-base:onnx-quantized-latest 到容器内 Podman
  - [ ] 2.1 宿主机 WSL Podman 执行 `podman save devcontainer-base:onnx-quantized-latest`，产物传输入容器（流式管道或经 `.temp/` 中转，注意 .temp 文件数约定，大文件用后即删）
  - [ ] 2.2 容器内 `podman load` 导入镜像
  - 验证：容器内 `podman images` 含该镜像，且 `podman run --rm devcontainer-base:onnx-quantized-latest python -V` 正常

## Phase 3：容器内重建 whl-builder 镜像
- [x] Task 3: 准备构建上下文并重建 xmnn-whl-builder:latest
  - [ ] 3.1 容器内复制构建上下文到原生 FS：`cp -a /workspace/external/chaos ~/build/chaos`（含 `npu_tvm/`、`npuusertools/`、`models/`）
  - [ ] 3.2 将 `.temp` 副本同步覆盖到 `~/build/chaos/ai/xmnn-whl-builder`（构建使用适配副本）
  - [ ] 3.3 容器内执行 `bash ~/build/chaos/ai/xmnn-whl-builder/build.sh --cn`（Podman 引擎自动回退；`--cgroup-manager=cgroupfs`、`--format docker`）
  - [ ] 3.4 确认 verify-wheel.sh 11 项验证全部 PASS
  - 验证：容器内 `podman images` 含 `xmnn-whl-builder:latest`；验证日志 11/11 PASS

## Phase 4：demo 模型编译
- [x] Task 4: 编译 external/chaos/models/demo 全部 4 个模型组
  - [x] 4.1 编写 `.temp/compile-demo-models.sh`（容器内 Podman run、挂载 `~/build/models-demo`、`--cgroup-manager=cgroupfs`、`xmnn.compile_api.compile_xmnn`）
  - [x] 4.2 冒烟：先编译 `onnx/yolov5s` 与 `caffe/resnet50`（无需 torch），确认 `COMPILE_DONE`
  - [x] 4.2b 构建 `xmnn-whl-builder-full`（xmnn-whl-builder + CPU torch 2.13.0，`.temp/xmnn-whl-builder-full/`），解决 pytorch 前端 `torch.jit.load` 依赖
  - [x] 4.3 编译 `pytorch/resnet18` 与 `two_inputs`（双输入），全部通过
  - [x] 4.4 汇总编译结果（4/4 成功，产物验证 `verify-artifacts.sh` 全 pass）
  - 结果：onnx/yolov5s(478s)、caffe/resnet50(122s)、pytorch/resnet18、two_inputs 全部 rc=0，
    产物 `~/build/models-demo/temp/<tag>/<group>/<model>/compile/{network.xmnn,param.bin}`

## Phase 5：收尾
- [x] Task 5: 验证收尾与源目录保护确认（核心验收全部完成；仅剩 5.4 提交待用户确认）
  - [x] 5.1 逐项核对 checklist.md 全部通过
  - [x] 5.2 确认 `external/chaos` 无本任务引入的变更（源目录只读保护；git status 仅含无关既有改动）
  - [x] 5.3 清理 `.temp/` 中转的大文件（无 >100MB 残留文件）
  - [ ] 5.4 通过 atomic-commit-cmd 原子提交（.temp 被 git 忽略，仅提交 spec 文档）——待用户确认后执行

# Task Dependencies
- [Task 0] 无依赖（环境准备门禁）
- [Task 1] 依赖 [Task 0]
- [Task 2] 依赖 [Task 0]（可与 Task 1 并行）
- [Task 3] 依赖 [Task 1, Task 2]
- [Task 4] 依赖 [Task 3]
- [Task 5] 依赖 [Task 4]
