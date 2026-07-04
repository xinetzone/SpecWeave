# Tasks

## 阶段一：学习与研究

- [ ] Task 1: 深度研究 TVM FFI 源码目录结构与核心架构
  - [ ] SubTask 1.1: 研读 `include/tvm/ffi/` 下所有 C++ 头文件，理解核心 API 设计
  - [ ] SubTask 1.2: 研读 `python/tvm_ffi/` 下所有 Python 绑定源码
  - [ ] SubTask 1.3: 研读 `docs/` 下 RST 文档，理解官方文档结构
  - [ ] SubTask 1.4: 研读 `examples/` 下示例代码
  - [ ] SubTask 1.5: 研读 `addons/tvm_ffi_orcjit/` 和 `addons/torch_c_dlpack_ext/` 扩展代码

- [ ] Task 2: 研究官方文档网站内容
  - [ ] SubTask 2.1: 抓取 `https://tvm.apache.org/ffi/` 首页及所有子页面内容
  - [ ] SubTask 2.2: 整理官方文档中与源码对应的关键概念和 API 说明

## 阶段二：教程编写

- [ ] Task 3: 创建教程目录骨架与导航入口
  - [ ] SubTask 3.1: 创建 `docs/knowledge/learning/tvm-ffi-wiki/` 目录
  - [ ] SubTask 3.2: 编写 README.md 导航入口（含章节概览与阅读路径）

- [ ] Task 4: 编写核心概念章节（并行）
  - [ ] SubTask 4.1: 编写 `00-overview.md`（TVM FFI 概述与定位）
  - [ ] SubTask 4.2: 编写 `01-architecture.md`（系统架构与设计理念）
  - [ ] SubTask 4.3: 编写 `02-cpp-core-api.md`（C++ 核心 API：Any/Object/Function/Tensor）
  - [ ] SubTask 4.4: 编写 `03-type-system.md`（类型系统：DType/Enum/Optional/String）
  - [ ] SubTask 4.5: 编写 `04-containers.md`（容器类型：Array/Map/Dict/List/Tuple/Shape）
  - [ ] SubTask 4.6: 编写 `05-reflection.md`（反射与注册机制）
  - [ ] SubTask 4.7: 编写 `06-serialization.md`（序列化：JSON/Base64/Structural）

- [ ] Task 5: 编写高级功能章节（并行）
  - [ ] SubTask 5.1: 编写 `07-python-bindings.md`（Python 绑定机制：Cython/ffi_api）
  - [ ] SubTask 5.2: 编写 `08-cuda-support.md`（CUDA 支持：cubin launcher/device guard）
  - [ ] SubTask 5.3: 编写 `09-orcjit-extension.md`（ORCJIT 扩展：LLVM JIT 编译）
  - [ ] SubTask 5.4: 编写 `10-dlpack-integration.md`（DLPack 集成：跨框架张量交换）

- [ ] Task 6: 编写实战与总结章节
  - [ ] SubTask 6.1: 编写 `11-build-and-integration.md`（编译构建与项目集成）
  - [ ] SubTask 6.2: 编写 `12-examples.md`（完整实战示例）
  - [ ] SubTask 6.3: 编写 `13-best-practices.md`（最佳实践与性能优化）
  - [ ] SubTask 6.4: 编写 `14-faq.md`（常见问题解答）
  - [ ] SubTask 6.5: 编写 `15-resources.md`（参考资料与学习路径）

## 阶段三：收尾与验证

- [ ] Task 7: 教程质量验证与收尾
  - [ ] SubTask 7.1: 检查所有文档的 YAML frontmatter 完整性
  - [ ] SubTask 7.2: 检查所有相对路径引用有效性
  - [ ] SubTask 7.3: 更新 `docs/knowledge/README.md` 知识库索引
  - [ ] SubTask 7.4: 交叉引用关联：与 `interface-api-abi-protocol-wiki`、`idl-wiki` 建立双向链接

# Task Dependencies
- Task 3 依赖 Task 1 和 Task 2（需先学习再编写）
- Task 4、Task 5 依赖 Task 3（需先有目录骨架）
- Task 4 和 Task 5 可并行执行
- Task 6 依赖 Task 4 和 Task 5
- Task 7 依赖 Task 3-6 全部完成