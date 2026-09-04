# npu-ffi VTA FFI绑定库 - Verification Checklist

## 项目结构与配置
- [x] 目录结构完整：include/npu_ffi/vta/、src/vta/、python/npu_ffi/vta/、proto/、tests/python/、conda.recipe/、scripts/、.github/workflows/
- [x] LICENSE 文件存在（Apache 2.0）
- [x] .gitignore 配置正确（忽略 build/、dist/、__pycache__/、*.pyc 等）
- [x] pyproject.toml 存在且语法正确
- [x] 根 CMakeLists.txt 存在且 cmake_minimum_required >= 3.26
- [x] requires-python = ">=3.13" 在 pyproject.toml 中正确设置（遵循xuanspace规范）
- [x] protobuf >= 7.0.0 在 dependencies 中声明
- [x] apache-tvm-ffi 在 dependencies 中声明

## 构建系统验证
- [x] CMake 配置成功：`cmake -B build -DNPU_FFI_VTA_USE_STUB=ON` 无错误
- [x] CMake 能找到 tvm-ffi（通过 find_package CONFIG）
- [x] 编译成功：`cmake --build build --config Release` 无错误
- [x] `pip install --no-build-isolation -e .` 成功完成（先 pip install -e vendor/tvm-ffi）
- [x] build/lib/ 目录下生成 npu_ffi_vta.dll（Windows）
- [x] Python包正确安装到site-packages或editable路径
- [x] RPATH 设置正确（$ORIGIN on Linux, @loader_path on macOS）

## Python 导入与基础功能
- [x] `import npu_ffi` 不报错
- [x] `import npu_ffi.vta` 不报错
- [x] `npu_ffi.__version__` 存在且为 "0.1.0"
- [x] `from npu_ffi import vta` 正常工作
- [x] `dir(npu_ffi.vta)` 列出预期的公共函数和枚举

## VTA API 覆盖验证
- [x] `vta.tls_command_handle()` 可调用并返回递增整数值
- [x] `vta.buffer_alloc(nbytes)` 返回非空缓冲区指针
- [x] `vta.buffer_free(buf)` 不崩溃
- [x] `vta.buffer_copy(from_ptr, from_off, to_ptr, to_off, size, kind)` 正常执行
- [x] `vta.buffer_cpu_ptr(cmd, buf)` 返回指针
- [x] `vta.set_debug_mode(cmd, flag)` 可调用
- [x] `vta.load_buffer_2d(...)` 可调用（stub模式no-op）
- [x] `vta.store_buffer_2d(...)` 可调用
- [x] `vta.uop_push(...)` 可调用
- [x] `vta.uop_loop_begin(...)` / `vta.uop_loop_end()` 可调用
- [x] `vta.push_gemm_op(...)` 返回0（成功）
- [x] `vta.push_alu_op(...)` 返回0（成功）
- [x] `vta.dep_push(cmd, from, to)` 返回0
- [x] `vta.dep_pop(cmd, from, to)` 返回0
- [x] `vta.synchronize(cmd, wait_cycles)` 不崩溃
- [x] `vta.write_barrier(...)` 可调用
- [x] `vta.read_barrier(...)` 可调用
- [x] `vta.runtime_shutdown()` 存在且幂等
- [x] `vta.prepare_call_func(cmd, name)` 存在

## 类型安全与错误处理
- [x] 枚举类型安全（C++ enum class，Python IntEnum）
- [x] DebugFlag支持位运算组合（|、&、|=、&=）
- [x] 错误参数类型不会导致进程崩溃（tvm-ffi类型检查）

## Python 高层 API
- [x] `npu_ffi.vta.Buffer` 类存在
- [x] `with Buffer(1024) as buf:` 上下文管理器正常工作
- [x] Buffer析构时自动释放内存（RAII）
- [x] `CommandContext` 上下文管理器存在
- [x] `with CommandContext() as cmd:` 获取句柄，退出时自动synchronize
- [x] DebugFlag 枚举存在（DUMP_INSN=2、DUMP_UOP=4、SKIP_READ_BARRIER=8 等）
- [x] MemcpyKind 枚举存在（H2D=1、D2H=2、D2D=3）
- [x] MemoryType 枚举存在（DRAM=0、SRAM=1、UOP=2、INP=3、WGT=4、ACC=5、OUT=6）
- [x] ALUOpcode 枚举存在（ADD=0、SUB=1、MUL=2、MIN=3、MAX=4、SHR=5、SHL=6）
- [x] py.typed 标记文件存在（PEP 561）

## Protobuf 配置
- [x] proto/vta_config.proto 文件存在
- [x] protoc可编译该proto文件
- [x] 预生成的 vta_config_pb2.py 可导入
- [x] protobuf 7.0+兼容（google-protobuf 7.35.1验证通过）
- [x] 纯Python VTAConfig dataclass无需protobuf即可使用
- [x] 可序列化/反序列化（二进制、JSON、TextProto格式往返正确）
- [x] 默认配置可加载（vta/vta_v3/vta_v4三种预设）
- [x] 配置字段完整（log2参数、计算属性）
- [x] 参数校验函数可用

## 测试
- [x] tests/python/__init__.py 存在
- [x] tests/python/conftest.py 存在（设置KMP_DUPLICATE_LIB_OK、提供fixtures）
- [x] test_enums.py 22个测试全部通过
- [x] test_ffi_api.py 34个测试全部通过
- [x] test_buffer.py 14个测试全部通过
- [x] test_command.py 15个测试全部通过
- [x] test_config.py 25个测试全部通过
- [x] `pytest tests/python/ -v` 全部通过（116 passed in ~2s）
- [x] 测试可重复运行（无状态泄漏）

## Conda 支持
- [x] environment.yml 存在（Python 3.13，cmake，ninja，cxx-compiler）
- [x] conda.recipe/meta.yaml 存在且语法正确（Jinja2模板）
- [x] conda.recipe/conda_build_config.yaml 存在（锁定Python 3.13）
- [x] conda.recipe/build.sh 存在（Linux/macOS）
- [x] conda.recipe/bld.bat 存在（Windows）
- [x] conda.recipe/README.md 存在（构建指南）
- [x] scripts/setup_conda_dev.sh 存在（Linux/macOS一键设置）
- [x] scripts/setup_conda_dev.ps1 存在（Windows PowerShell一键设置）
- [x] 国内镜像配置说明在文档中提供

## 代码质量
- [x] C++使用C++17标准
- [x] 公共头文件有Doxygen风格注释
- [x] 全局变量在匿名命名空间或static
- [x] 无using namespace std; 在头文件中
- [x] C++枚举使用enum class类型安全

## 文档
- [x] README.md 存在（中文）
- [x] README包含项目介绍与特性列表
- [x] README包含前置条件说明
- [x] README包含安装步骤（tvm-ffi先安装、npu-ffi --no-build-isolation）
- [x] README包含快速开始示例代码（5个完整示例）
- [x] README包含构建选项说明（NPU_FFI_VTA_USE_STUB、NPU_FFI_VTA_DIR、NPU_FFI_FROM_SOURCE）
- [x] README包含Conda使用说明
- [x] README包含目录结构说明
- [x] README包含API参考
- [x] README包含运行测试说明（含KMP_DUPLICATE_LIB_OK）

## 跨平台兼容性
- [x] CMake路径使用正斜杠/，无硬编码反斜杠
- [x] Windows构建验证（MSVC，pip install -e成功）
- [x] CI配置覆盖Windows/Ubuntu/macOS三平台

## 依赖完整性
- [x] pyproject.toml中所有依赖都实际使用
- [x] 不修改vendor/tvm-ffi源码（使用原生tvm-ffi API）
- [x] 不编译external/chaos/npu_tvm/vta的源码（stub模式下）

## 真实硬件支持（可选）
- [x] src/vta/real_rt.cc 已创建（直接转发VTA C API调用）
- [x] NPU_FFI_VTA_USE_STUB=OFF 时切换到real_rt.cc编译
- [x] NPU_FFI_VTA_DIR 可指定VTA安装路径
- [x] stub模式默认ON，所有现有功能不受影响

## CI配置
- [x] .github/workflows/ci.yml 存在
- [x] 三平台构建矩阵（Windows/Linux/macOS × Python 3.13）
- [x] 构建→安装→测试→wheel验证流程完整
- [x] KMP_DUPLICATE_LIB_OK=TRUE 环境变量已配置
- [x] libomp依赖已配置（Linux: libomp-dev, macOS: libomp）
