# 执行复盘

## 时间线

| 时间 | 事件 | 关键决策 |
|------|------|---------|
| 2026-07-17 | 用户报告 palmDet 编译出现 Segmentation fault | 开始定位问题 |
| 2026-07-17 | 发现 adaround=false 可绕过问题 | 确认与 PyTorch 加载相关 |
| 2026-07-17 | 分析 use_hide_symbols 参数链路 | 确定 HIDE_PRIVATE_SYMBOLS=OFF 为根因 |
| 2026-07-18 | 修改 CMakeLists.txt 实现精确符号控制 | 使用 --exclude-libs,ALL 替代 -fvisibility=hidden |
| 2026-07-18 | 修改 cmake/config.cmake 默认值 | HIDE_PRIVATE_SYMBOLS=ON |
| 2026-07-18 | 修改 tasks.py 默认值 | use_hide_symbols=True |
| 2026-07-18 | 修改 rebuild_tvm_codegenc.sh | -DHIDE_PRIVATE_SYMBOLS=ON |
| 2026-07-18 | 使用 Docker 开发环境重新编译 TVM | 884编译单元，6.3分钟 |
| 2026-07-18 | 验证符号可见性 | LLVM符号隐藏，TVM符号正常导出 |
| 2026-07-18 | 验证 TVM+PyTorch 共存 | 无段错误，测试通过 |

## 事实清单

### 问题现象
1. palmDet config.toml 中 adaround=true 时编译失败，Segmentation fault (core dumped)
2. adaround=false 时编译正常，说明问题与 PyTorch 加载相关
3. 错误发生在 TVM 编译代码生成阶段，涉及 LLVM 静态链接

### 技术分析
1. TVM 静态链接 LLVM (libLLVM*.a)，默认 HIDE_PRIVATE_SYMBOLS=OFF
2. 未隐藏的 LLVM 符号被导出到 libtvm.so 的动态符号表
3. PyTorch 的 libtorch.so 也包含 LLVM 符号
4. 动态链接器解析符号时发生 Symbol Interposition，相同符号被绑定到错误实现
5. 结果：运行时调用错误的 LLVM 函数导致段错误

### 修复方案对比
| 方案 | 旧方案 (OFF) | 新方案 (ON) |
|------|-------------|-------------|
| 符号控制方式 | 无控制，所有符号导出 | -Wl,--exclude-libs,ALL |
| -fvisibility=hidden | 不使用 | 不使用 |
| --gc-sections | 不使用 | 不使用 |
| 静态注册影响 | 无 | TVM_REGISTER_* 正常工作 |
| LLVM 符号泄露 | 是 | 否 |

## 变更摘要

**核心配置文件：**
- CMakeLists.txt: 修改 HIDE_PRIVATE_SYMBOLS 默认值和实现逻辑
- cmake/config.cmake: 修改默认值和注释
- tasks.py: 修改 use_hide_symbols 默认值

**构建脚本：**
- dev-env/rebuild_tvm_codegenc.sh: 更新 CMake 参数

**依赖清理：**
- docker/local/nuitka/tvm/CMakeLists.txt: 移除 libtvm_allvisible.so
- docker/local/nuitka/compile.sh: 移除 libtvm_allvisible.so 复制
- ci/jenkins/data.py: 移除 tvm_allvisible 产物条目

**文档：**
- docs/install/from_source.rst: 更新 HIDE_PRIVATE_SYMBOLS 说明

## 验证结果

1. Docker 容器内重新编译成功 (884编译单元, 6.3分钟)
2. build.ninja 确认包含 --exclude-libs,ALL
3. 符号表验证：LLVM cl::opt 符号完全隐藏
4. TVM 符号正常导出 (154112个DEFAULT符号)
5. TVM Python 导入和 relay.build 正常
6. TVM+PyTorch 2.13.0+cu130 共存测试通过

