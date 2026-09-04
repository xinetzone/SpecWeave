# Checklist

## Phase 0：环境准备
- [ ] WSL Ubuntu-26.04 已启动，dockerd 持久化运行（setsid nohup）
- [ ] 国内 DNS 已配置（223.5.5.5 / 114.114.114.114）
- [ ] 基础镜像 `devcontainer-base:chaos-ai-npu` 已构建
- [ ] 容器内工具链验证通过：LLVM 22 六包族、cmake≥4.4、ninja≥1.13、patchelf、Python≥3.14

## Phase 1：目录骨架与自包含配置
- [ ] `external/chaos/ai/xmnn-whl-builder/` 目录存在且文件齐全（pyproject.toml、CMakeLists.txt、_xmnn_bootstrap.py、xmnn_bootstrap.pth）
- [ ] `pyproject.toml` 配置 scikit-build-core，`requires-python >= 3.14`，19 个运行时依赖
- [ ] `CMakeLists.txt` 安装 `_libs/`（libtvm.so + libLLVM + 依赖，RPATH `$ORIGIN`）、bootstrap、Nuitka .so、`tvm/relay/std`、`vta_hw/config`、`xmnn` 数据目录
- [ ] `_xmnn_bootstrap.py` 含 AST 兼容层 + TVM 环境引导，`xmnn_bootstrap.pth` 正确触发导入
- [ ] 所有新增文件与脚本不含对 `external/chaos/xmtools` 的引用（grep 验证通过）

## Phase 2：多阶段 Dockerfile
- [ ] Dockerfile 使用多阶段构建，BUILD 阶段 `FROM devcontainer-base:chaos-ai-npu`
- [ ] 源码通过 BuildKit `RUN --mount=type=bind` 挂载，不进最终镜像层
- [ ] FINAL 阶段无源码 `.py` 文件（Nuitka 已编译为 `.so`）
- [ ] `docker build` 成功

## Phase 3：build-wheel.sh
- [ ] 使用 `python -m build --wheel --no-isolation`，设置 `PIP_USER=0`、`PATH=/opt/conda/bin:$PATH`
- [ ] pyproject.toml 系统 cmake/ninja 补丁生效
- [ ] vta/xmnn 注入 AST PREAMBLE 完成 Nuitka 编译并还原
- [ ] 脚本在容器内可执行并产出 `dist/xmnn-*.whl`

## Phase 4：verify-wheel.sh（9 项检查）
- [ ] import tvm（v0.19.0）/ vta / xmnn 通过
- [ ] `_libs` 目录含 libtvm.so + libLLVM.so.22.1 + 依赖
- [ ] libtvm.so 动态加载（ctypes RTLD_GLOBAL）通过
- [ ] `tvm.build(llvm)` 计算验证通过（A[i]*2==B[i], n=1024, rtol=1e-5）
- [ ] `relay/std` 数据文件、`xmnn_bootstrap.pth`、`xmnn` 数据目录（autolibs/tools_cpp/fonts）存在
- [ ] 9 项全部 PASS 且 `FAIL=0`

## Phase 5：build-and-test.sh
- [ ] 一键跑通 构建镜像 → 打包 → 验证 全流程，退出码 0
- [ ] 支持 `--verify-only`、`--no-build`、`--cn` 参数

## Phase 6：验证与交付
- [ ] 全流程 checklist 逐项核对通过
- [ ] 原子提交完成（单一职责，Conventional Commits 规范）