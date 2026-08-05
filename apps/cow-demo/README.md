# cow-demo

零拷贝COW读写分离模式（Zero-copy COW Read-Write Separation Pattern）的C++示例框架。

## 概述

本项目是架构模式「零拷贝COW读写分离」的可编译参考实现，演示了如何在C++中平衡**零拷贝性能**与**多方共享数据安全**。

## 目录结构

```
cow-demo/
├── CMakeLists.txt          # CMake构建配置（C++17，零第三方依赖）
├── include/
│   └── cow_buffer.hpp      # CowBuffer核心类头文件（header-only）
└── src/
    └── main.cpp            # 7个测试场景演示
```

## 核心特性

对应模式5步法：

1. **const/non-const读写API分离**：`data() const`只读零开销 vs `mutable_data()`写入按需COW
2. **引用计数O(1)零拷贝共享**：`ShareFrom()`仅指针赋值+引用计数+1，无memcpy
3. **写时自动克隆**：多方共享时`mutable_data()`自动触发COW，获得私有副本
4. **分层策略**：N=1单消费者identity直通（in-place可见）+ N≥2多消费者COW隔离
5. **双重开关回退**：编译期宏（`COW_DISABLED_AT_COMPILE_TIME`）+ 运行期原子开关（`SetCOWEnabled()`）

## 构建与运行

```bash
mkdir build && cd build
cmake ..
cmake --build .

# Linux/WSL:
./cow_demo

# Windows:
# Debug\cow_demo.exe
```

## 测试场景

| 测试 | 说明 |
|------|------|
| TestExclusiveAccess | 独占缓冲区读写，无复制 |
| TestConstAccess | const只读访问，零开销不改变引用计数 |
| TestN1IdentityPassthrough | N=1单消费者identity直通，in-place修改对源可见 |
| TestN2MultiConsumerCOW | N=2多消费者，写时自动COW隔离 |
| TestExplicitUnshare | 显式Unshare()强制断开共享 |
| TestResizeBreaksSharing | Resize元数据修改自动打断共享 |
| TestRuntimeSwitch | 运行期开关动态启用/禁用，紧急回退演示 |

## 模式文档

- [zerocopy-cow-readwrite-separation.md](../../.agents/docs/retrospective/patterns/architecture-patterns/zerocopy-cow-readwrite-separation.md) — 完整模式文档（触发场景、核心步骤、反模式、迁移示例）
