# VTA FFI (npu-ffi) 全面优化 - Verification Checklist

## P0严重问题修复验证
- [x] CP-1: ffi_registry.cc中所有size/offset/stride参数使用int64_t，内部转换带static_cast
- [x] CP-2: push_gemm_op/push_alu_op正确转发所有参数（uop_handle, finit, signature, nbytes）
- [x] CP-3: Buffer分配失败时检查nullptr并抛出std::bad_alloc
- [~] CP-4: Python DebugFlag枚举已包含FORCE_SERIAL，DUMP_PROFILER待真实VTA后端确认后补充
- [x] CP-5: pyproject.toml中requires-python为">=3.13"
- [x] CP-6: runtime_common.cc统一实现，real/stub仅保留后端C函数，无重复
- [x] CP-7: 所有头文件统一使用#pragma once
- [x] CP-8: Python Buffer有double-free保护和reset()方法；析构函数裸except已加注释说明必要性（Python析构禁止抛异常）

## P1重要问题修复验证
- [~] CP-9: FFI边界异常转换通过TVM FFI框架自动处理；未添加额外try-catch以避免开销
- [x] CP-10: Buffer::cpu_ptr()检查data_==nullptr返回nullptr
- [x] CP-11: CMake使用target_include_directories，移除全局include_directories
- [x] CP-12: pyproject.toml sdist路径正确（头文件在include/，包含CMakePresets.json）
- [x] CP-13: _ffi_api.py版本检查修正为期望0.0.1，最小版本(0,0,0)
- [x] CP-14: Buffer类有const void* data() const访问器
- [x] CP-15: Python Buffer有reset()方法，完整类型注解
- [x] CP-16: buffer_copy_safe()类型安全包装（支持Buffer/int、MemcpyKind枚举）
- [x] CP-17: ffi_registry.cc有前缀一致性重要注释
- [x] CP-18: stub_rt.cc shutdown时无条件输出泄漏警告（修复原条件反转bug）
- [x] CP-19: 有C++单元测试(test_buffer.cc)覆盖核心逻辑

## P2次要问题修复验证
- [x] CP-20: npu_ffi.h有NPU_FFI_API导出宏（NPU_FFI_DLL_EXPORT/IMPORT）
- [x] CP-21: 测试覆盖size=0、nullptr边界条件
- [x] CP-22: examples/目录包含basic_usage.cc和basic_usage.py
- [x] CP-23: ffi_registry.cc中prepare_call_func使用const char*
- [x] CP-24: C++层有CommandContext RAII类（析构自动synchronize）
- [x] CP-25: Doxygen/Google风格文档注释完善

## 功能兼容性验证
- [x] CP-26: 原有API保持兼容（仅添加重载/方法，未删除/修改现有签名）
- [x] CP-27: 原有API函数签名保持兼容（buffer_alloc/buffer_free等FFI名称未变）
- [x] CP-28: stub和real后端通过runtime_common.cc保持行为一致
- [~] CP-29: pip install需在完整构建环境（tvm_ffi已安装）验证
- [~] CP-30: verify_install.py验证需在完整环境执行

## 性能验证（静态分析）
- [x] CP-31: 重构零额外虚函数开销，编译时内联，性能无退化
- [x] CP-32: FFI调用路径无额外包装层开销
- [x] CP-33: stub模式泄漏检测在shutdown时执行一次，无运行时开销

## 最佳实践对齐验证
- [x] CP-34: CMakePresets.json（stub/release/debug预设）
- [x] CP-35: examples/有可运行的基本使用示例
- [x] CP-36: ffi_registry.cc注释提示check_ffi_prefix.py
- [x] CP-37: Python版本>=3.13与xuanspace规范一致

## 交付物验证
- [x] CP-38: 优化通过6个原子提交记录完整
- [~] CP-39: 模式萃取见本会话总结中的"可复用模式"
- [x] CP-40: 提交遵循Conventional Commits，6次提交每次单一职责
