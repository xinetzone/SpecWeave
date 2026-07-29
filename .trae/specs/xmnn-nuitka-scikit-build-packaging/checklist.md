# XMNN Nuitka + scikit-build-core 打包系统 - 验证清单

## 代码质量与 Bug 修复
- [ ] xmpack/docker.py 中 `compile_nuitka()` 函数签名包含 `cache_dir` 参数，默认值为 `"/workspace/.temp/.nuitka_cache"`
- [ ] xmpack/docker.py 中 `build_nuitka()` 调用 `compile_nuitka()` 时正确传递 `cache_dir` 参数
- [ ] xmpack 所有模块可被 Python 正常导入（`from xmpack import ...` 无 ImportError）
- [ ] Nuitka include_modules/include_packages 列表覆盖 tvm/vta/xmnn 的所有必要子模块（对照实际目录结构验证）

## 源码与路径确认
- [ ] `npuusertools/xmnn/__init__.py` 存在且包含 `register_all_ops()` 和 `xmnn_task()` 函数
- [ ] npuusertools/xmnn/ 包含所有动态加载的 *_api.py 模块（compile_api, infer_api, accuracy_api, performance_api, bandwidth_api, autotune_api, excel_report_api）
- [ ] npuusertools/xmnn/ 包含 adaround/ 子包及量化模块
- [ ] npuusertools/xmnn/ 包含 autolibs/, fonts/, tools_cpp/ 数据目录
- [ ] npu_tvm/python/tvm/ 目录包含 relay/, topi/, ir/, tir/, runtime/, te/, auto_scheduler/, autotvm/, meta_schedule/, contrib/, driver/, target/, arith/, relax/ 等子包
- [ ] npu_tvm/vta/python/vta/ 目录存在且包含 Python 源码
- [ ] TVM C++ 构建目录确认（build/ 或 build_llvm22/），包含 libtvm.so 和 libtvm_runtime.so

## 构建系统配置
- [ ] packaging/pyproject.toml 的 `[tool.scikit-build]` 包含 `cmake.args = ["-G", "Ninja"]`
- [ ] packaging/pyproject.toml 的 build-system.requires 包含 ninja
- [ ] 顶层 packaging/CMakeLists.txt 使用 `LANGUAGES NONE`
- [ ] packaging/tvm/CMakeLists.txt 使用 `LANGUAGES NONE`
- [ ] packaging/vta/CMakeLists.txt 使用 `LANGUAGES NONE`
- [ ] Containerfile.build 安装 ninja（apt 或 pip）
- [ ] Containerfile.build 安装 wheel 包（用于 wheel unpack 验证）
- [ ] Containerfile.build 中 Python 版本与 pyproject.toml requires-python 一致

## Nuitka 编译产物
- [ ] 执行 Nuitka 编译后，`.temp/tvm/tvm.cpython-*.so` 存在且大小 > 10MB
- [ ] 执行 Nuitka 编译后，`.temp/vta/vta.cpython-*.so` 存在且大小 > 100KB
- [ ] 执行 Nuitka 编译后，`.temp/xmnn/xmnn.cpython-*.so` 存在且大小 > 1MB
- [ ] 从 /tmp 目录设置 PYTHONPATH 到 tvm 产物目录后，`python -c "import tvm; print(tvm.__version__)"` 成功
- [ ] libtvm*.so 已复制到 tvm 产物目录下的 tvm/_libs/ 子目录
- [ ] vta_hw/config 目录已复制到 vta 产物目录
- [ ] Nuitka 编译使用 `--static-libpython=no`（不静态链接 Python）
- [ ] Nuitka 编译使用 `--jobs=$(nproc)` 并行编译
- [ ] Nuitka 编译缓存目录正确挂载和持久化

## Wheel 打包产物
- [ ] 执行打包后，`packaging/dist/xmnn-*.whl` 存在
- [ ] wheel 文件名包含正确的 Python ABI tag（cp313 或 cp314）和平台 tag（linux_x86_64）
- [ ] wheel 解包后顶层包含 tvm.cpython-*.so
- [ ] wheel 解包后顶层包含 vta.cpython-*.so
- [ ] wheel 解包后顶层包含 xmnn.cpython-*.so
- [ ] wheel 解包后 tvm/_libs/ 包含 libtvm.so、libtvm_runtime.so
- [ ] wheel 解包后顶层包含 _tvm_nuitka_init.py
- [ ] wheel 解包后顶层包含 tvm_nuitka_init.pth
- [ ] wheel 解包后 xmnn/autolibs/ 目录存在且包含各芯片版本子目录
- [ ] wheel 解包后 xmnn/fonts/ 包含字体文件
- [ ] wheel 解包后 xmnn/tools_cpp/bin/ 和 xmnn/tools_cpp/libs/ 存在
- [ ] wheel 解包后 vta_hw/config/ 存在
- [ ] wheel 解包后不包含 tvm/vta/xmnn 的 .py 源码文件（仅 _tvm_nuitka_init.py 和 tvm_nuitka_init.pth 两个 bootstrap 文件）
- [ ] wheel 中 .dist-info/METADATA 包含正确的 Requires-Dist 依赖声明

## Wheel 安装与导入测试
- [ ] 在干净 Python 环境中 `pip install xmnn-*.whl` 退出码为 0
- [ ] 安装后 `python -c "import tvm; print(tvm.__version__)"` 成功，无需手动设置 LD_LIBRARY_PATH
- [ ] 安装后 `python -c "import vta"` 成功
- [ ] 安装后 `python -c "import xmnn"` 成功
- [ ] 安装后 `python -c "from xmnn import compile_api, infer_api, accuracy_api, performance_api, bandwidth_api, autotune_api, excel_report_api"` 所有动态导入模块均成功
- [ ] 安装后 `python -c "from tvm import relay, topi, ir, tir, runtime"` 成功
- [ ] TVM _tvm_nuitka_init 引导在 Python 启动时自动执行（通过 .pth 文件）
- [ ] TVM 运行时可正确加载 libtvm.so（ctypes FFI 模式）

## Invoke 命令行任务
- [ ] `inv image-build` 成功构建 nuitka-gcc-llvm Docker 镜像
- [ ] `inv build` 在容器内成功完成 TVM C++ 编译（cmake + ninja）
- [ ] `inv nuitka-compile` 成功完成 Nuitka 三组件编译
- [ ] `inv nuitka-package` 成功完成 wheel 打包
- [ ] `inv nuitka` 一键流水线（C++编译 + Nuitka编译 + wheel打包）端到端成功
- [ ] `inv client` 成功构建客户端运行时镜像
- [ ] `docker run --rm xmnn-client:1.2.1 python -c "import tvm; import vta; import xmnn"` 成功

## 源码保护
- [ ] wheel 安装后 site-packages 中不存在 tvm/ 目录下的 .py 源码文件（除 bootstrap 外）
- [ ] wheel 安装后 site-packages 中不存在 vta/ 目录下的 .py 源码文件
- [ ] wheel 安装后 site-packages 中不存在 xmnn/ 目录下的 .py 源码文件（数据目录中无 .py）
- [ ] 所有 Python 代码均以 .so 二进制扩展形式存在，无法通过文本编辑器直接阅读
