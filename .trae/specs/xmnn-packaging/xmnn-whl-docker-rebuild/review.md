# Checklist

## 版本号统一
- [x] `packaging/pyproject.toml` 中 `version` 字段与 `client/Containerfile` 中 `LABEL version` 一致
- [x] `scripts/full_build.py` 中 `--image-tag` 默认值与版本号一致
- [x] 关键代码文件版本号已同步（`docker.py`、`tasks.py` 默认值已更新为 `1.2.2-alpha`）

## 构建环境
- [x] Docker daemon 正常运行（v29.6.1）
- [x] `nuitka-gcc-llvm:latest` 基础镜像存在
- [x] 源码目录 `npu_tvm/`、`npuusertools/`、`xmnn/packaging/` 完整存在
- [x] 构建在 WSL（Ubuntu 24.04）环境中执行

## Nuitka 编译
- [x] 编译使用 `--force` 标志，强制重新编译所有组件
- [x] `tvm.cpython-314-x86_64-linux-gnu.so` 编译产物生成（118MB）
- [x] `vta.cpython-314-x86_64-linux-gnu.so` 编译产物生成（12MB）
- [x] `xmnn.cpython-314-x86_64-linux-gnu.so` 编译产物生成（5.7MB）
- [x] 编译过程无错误退出

## Wheel 打包
- [x] `packaging/dist/xmnn-1.2.2a0-cp314-cp314-linux_x86_64.whl` 文件生成
- [x] Wheel 文件大小 187MB > 100MB
- [x] Wheel 内包含 `tvm/_libs/libtvm.so` 等 C++ 共享库（通过 Containerfile 验证确认）
- [x] Wheel 内包含 `_tvm_nuitka_init.py` 和 `.pth` 启动钩子（通过 Containerfile 验证确认）

## Docker 客户端镜像
- [x] `docker build` 成功完成，无错误
- [x] 镜像标签正确：`xmnn-client:1.2.2-alpha`
- [x] `import tvm` 成功
- [x] `import vta` 成功
- [x] `import xmnn` 成功
- [x] `from xmnn import compile_api, infer_api, accuracy_api, performance_api, bandwidth_api, excel_report_api` 全部成功
- [x] 镜像内 `typer` 和 `rich` 可正常导入

## Docker 镜像导出
- [x] `xmnn-client-1.2.2-alpha.tar.gz` 文件生成
- [x] 导出文件大小 1.8GB > 500MB
- [x] `xmnn-client-1.2.2-alpha.tar.gz.sha256` 校验文件生成
- [x] SHA256 校验通过（`sha256sum -c` 返回 OK）
- [ ] 导出文件可被 `docker load` 重新加载（可选验证）