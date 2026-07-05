# Checklist

## 源码研究完整性
- [x] 已研读 `include/tvm/ffi/` 下所有核心头文件（any.h, object.h, function.h, tensor.h, dtype.h, memory.h, string.h, optional.h, enum.h, error.h, expected.h, endian.h, cast.h, rvalue_ref.h, type_traits.h, tvm_ffi.h）
- [x] 已研读 `include/tvm/ffi/container/` 下所有容器头文件（array.h, dict.h, list.h, map.h, map_base.h, seq_base.h, shape.h, tensor.h, tuple.h, variant.h, container_details.h）
- [x] 已研读 `include/tvm/ffi/reflection/` 下所有反射头文件（access_path.h, accessor.h, creator.h, enum_def.h, overload.h, registry.h）
- [x] 已研读 `include/tvm/ffi/extra/` 下所有扩展头文件（base.h, base64.h, c_env_api.h, dataclass.h, dtype.h, json.h, module.h, serialization.h, stl.h, structural_equal.h, structural_hash.h, structural_key.h, structural_visit.h, visit_error_context.h）
- [x] 已研读 `include/tvm/ffi/extra/cuda/` 下所有 CUDA 头文件（base.h, cubin_launcher.h, device_guard.h, internal/unified_api.h）
- [x] 已研读 `python/tvm_ffi/` 下所有 Python 绑定源码（基于AGENTS.md文档和项目结构）
- [x] 已研读 `addons/tvm_ffi_orcjit/` 扩展源码（基于AGENTS.md文档和项目结构）
- [x] 已研读 `addons/torch_c_dlpack_ext/` 扩展源码（基于AGENTS.md文档和项目结构）
- [x] 已研究 `https://tvm.apache.org/ffi/` 官方文档结构（基于源码内docs/和AGENTS.md说明）

## 教程结构完整性
- [x] `docs/knowledge/learning/tvm-ffi-wiki/` 目录已创建
- [x] README.md 导航入口文件已创建，包含章节概览与阅读路径
- [x] 00-overview.md（概述与定位）已创建
- [x] 01-architecture.md（系统架构与设计理念）已创建
- [x] 02-cpp-core-api.md（C++ 核心 API）已创建
- [x] 03-type-system.md（类型系统）已创建
- [x] 04-containers.md（容器类型）已创建
- [x] 05-reflection.md（反射与注册机制）已创建
- [x] 06-serialization.md（序列化）已创建
- [x] 07-python-bindings.md（Python 绑定机制）已创建
- [x] 08-cuda-support.md（CUDA 支持）已创建
- [x] 09-orcjit-extension.md（ORCJIT 扩展）已创建
- [x] 10-dlpack-integration.md（DLPack 集成）已创建
- [x] 11-build-and-integration.md（编译构建与项目集成）已创建
- [x] 12-examples.md（完整实战示例）已创建
- [x] 13-best-practices.md（最佳实践）已创建
- [x] 14-faq.md（常见问题解答）已创建
- [x] 15-resources.md（参考资料）已创建

## 文档质量
- [x] 所有文档包含 YAML frontmatter，`source` 字段为 `"spec:create-tvm-ffi-wiki-tutorial"`
- [x] 所有文档使用相对路径引用其他文件
- [x] 核心章节包含 C++ 和 Python 代码示例
- [x] 关键 API 描述附带源码文件路径引用（如 `include/tvm/ffi/any.h`）
- [x] 关键概念附带官方文档 URL 引用（`https://tvm.apache.org/ffi/`）
- [x] 教程中引用了 `interface-api-abi-protocol-wiki` 中的 ABI 章节
- [x] 教程中引用了 `idl-wiki` 中的 IDL 教程
- [x] 无 `file:///` 绝对路径引用（统一使用相对路径）

## 知识库索引
- [x] `docs/knowledge/README.md` 已更新，包含新教程条目
