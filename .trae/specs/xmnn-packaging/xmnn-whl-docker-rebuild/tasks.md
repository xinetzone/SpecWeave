# Tasks

- [x] Task 1: 版本号统一与构建环境检查
  - [x] Subtask 1.1: 确认 `packaging/pyproject.toml` 中 `version = "1.2.2-alpha"` 为当前目标版本
  - [x] Subtask 1.2: 同步 `client/Containerfile` 中 `LABEL version` 和镜像 tag 为 `1.2.2-alpha`
  - [x] Subtask 1.3: 同步 `scripts/full_build.py` 中 `--image-tag` 默认值为 `xmnn-client:1.2.2-alpha`
  - [x] Subtask 1.4: 验证 Docker daemon 可用且 `nuitka-gcc-llvm:latest` 镜像存在
  - [x] Subtask 1.5: 验证源码目录完整性（`npu_tvm/`、`npuusertools/`、`xmnn/packaging/` 均存在）

- [x] Task 2: 从零执行 Nuitka 编译 + Wheel 打包
  - [x] Subtask 2.1: 在 WSL/Linux 环境中执行 `python xmnn/scripts/full_build.py --force --skip-image`
  - [x] Subtask 2.2: 验证 Nuitka 编译产物：确认 `tvm.cpython-314-x86_64-linux-gnu.so`(118MB)、`vta.cpython-314-x86_64-linux-gnu.so`(12MB)、`xmnn.cpython-314-x86_64-linux-gnu.so`(5.7MB) 生成
  - [x] Subtask 2.3: 验证 Wheel 文件：确认 `packaging/dist/xmnn-1.2.2a0-cp314-cp314-linux_x86_64.whl`(187MB) 存在

- [x] Task 3: 构建客户端 Docker 镜像
  - [x] Subtask 3.1: 复制 wheel 到 `client/.temp/` 目录
  - [x] Subtask 3.2: 执行 `docker build -t xmnn-client:1.2.2-alpha -f client/Containerfile client/`
  - [x] Subtask 3.3: 验证镜像内导入：tvm OK, vta OK, xmnn OK, 6个API全部可用, typer/rich OK

- [x] Task 4: 导出 Docker 镜像并生成校验文件
  - [x] Subtask 4.1: 执行 `docker save xmnn-client:1.2.2-alpha | gzip > xmnn-client-1.2.2-alpha.tar.gz`
  - [x] Subtask 4.2: 生成 SHA256 校验：`sha256sum xmnn-client-1.2.2-alpha.tar.gz > xmnn-client-1.2.2-alpha.tar.gz.sha256`
  - [x] Subtask 4.3: 验证导出文件完整性（1.8GB，sha256 校验通过）

# Task Dependencies

- Task 2 depends on Task 1（版本号统一后才能构建）
- Task 3 depends on Task 2（wheel 打包完成后才能构建镜像）
- Task 4 depends on Task 3（镜像构建完成后才能导出）