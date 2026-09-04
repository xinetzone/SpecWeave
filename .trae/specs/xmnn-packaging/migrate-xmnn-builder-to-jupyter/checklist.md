# Checklist

## 副本与自包含
- [x] `.temp/xmnn-whl-builder/` 副本存在且文件齐全（Dockerfile/build.sh/scripts/pyproject.toml/CMakeLists.txt/_xmnn_bootstrap.py/xmnn_bootstrap.pth 等）
- [x] 副本 build.sh 不再依赖 `external/chaos/ai/scripts/lib/logging.sh`（日志库已内联到副本内）
- [x] 副本内所有 `.sh` 脚本为 LF 行尾，容器内 `bash -n` 全部通过
- [x] `.temp/README.md` 已记录副本用途与使用命令

## 环境与镜像
- [x] jupyter-podman-rootless 容器运行中，容器内 rootless Podman `podman info` 正常（fuse-overlayfs）
- [x] `devcontainer-base:onnx-quantized-latest` 已导入容器内 Podman 且可运行
- [x] 构建上下文已复制到容器原生 FS（`~/build/chaos`，非 9p 路径）
- [x] 容器内重建的 `xmnn-whl-builder:latest` 存在，verify-wheel.sh 11/11 PASS
- [x] `xmnn-whl-builder-full:latest`（+CPU torch 2.13.0）已构建，tvm/vta/xmnn/torch 导入验证通过

## 模型编译（验收核心）
- [x] `pytorch/resnet18` 编译成功（COMPILE_DONE，rc=0，network.xmnn=16K/param.bin=12M）
- [x] `caffe/resnet50` 编译成功（COMPILE_DONE，rc=0，122s，network.xmnn=32K/param.bin=25M）
- [x] `onnx/yolov5s` 编译成功（COMPILE_DONE，rc=0，478s，network.xmnn=44K/param.bin=7.0M）
- [x] `two_inputs` 编译成功（双输入，rc=0，network.xmnn=4K/param.bin=4K）
- [x] 4/4 模型组全部通过，无 FAIL（`verify-artifacts.sh` RESULT: 4 pass, 0 fail）

## 源目录保护与收尾
- [x] `external/chaos` 无本任务引入的变更（原件只读；git status 仅含无关既有改动）
- [x] `.temp/` 中转大文件（镜像 tar 等）已清理（无 >100MB 残留）
- [x] checklist 全项核对通过
