---
id: "abi-concept"
title: "四、ABI（应用二进制接口）：二进制兼容约定"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/03-abi.toml"
source: "spec:create-tech-interface-wiki-tutorial"
category: "learning"
tags: ["abi", "binary-compatibility", "calling-convention", "ffi", "shared-library", "syscall"]
date: "2026-07-03"
status: "stable"
author: "SpecWeave"
summary: "ABI的技术内涵、与API的本质区别、核心技术特征、底层系统应用场景与案例"
---

# ABI（应用二进制接口）：二进制兼容约定

## ABI技术内涵定义

ABI（Application Binary Interface，应用二进制接口）是两个二进制模块（如可执行程序与共享库）之间在**机器码层面**的接口约定。它定义了程序模块如何在二进制级别交互，无需访问源代码即可实现链接和运行。

### 与API的本质区别

API（Application Programming Interface，应用编程接口）是**源码级兼容**：只要源代码符合API约定，重新编译后即可运行。而ABI是**二进制级兼容**：预编译的二进制模块可以直接链接运行，完全不需要重新编译。

### 通俗类比

| 概念 | 类比 | 说明 |
|------|------|------|
| API | 菜谱的食材和做法说明 | 你需要按照菜谱自己做菜（编译源码），不同厨房（编译器）做出来的菜可能略有差异 |
| ABI | 预制菜的封装规格和加热方式 | 拿到就能直接加热食用（直接链接运行），不需要重新做菜（重新编译），只要包装规格匹配就能用 |

### API vs ABI 对比表

| 维度 | API | ABI |
|------|-----|-----|
| 兼容级别 | 源码级 | 二进制级 |
| 是否需要重新编译 | 是 | 否 |
| 关注点 | 函数签名、数据结构定义、调用语法 | 寄存器使用、栈布局、字节序、内存对齐 |
| 稳定性要求 | 相对宽松（版本升级可逐步废弃） | 极其严格（微小变化就会导致崩溃） |
| 面向对象 | 程序员、编译器 | 链接器、操作系统内核、CPU |
| 可见性 | 可见（头文件、文档） | 不可见（二进制约定） |

## 核心技术特征

ABI是一套精密的底层约定，涵盖二进制交互的方方面面。以下是五个核心技术特征：

### 1. 数据类型表示

这是ABI最基础的约定，定义了基本数据类型在内存中的表示方式：

- **基本类型大小**：在不同架构下基本类型占用的字节数不同：
  - 32位x86：int=4字节，pointer=4字节，long=4字节
  - 64位x86_64：int=4字节，pointer=8字节，long=8字节
- **字节序（Endianness）**：多字节数据的存储顺序：
  - 大端序（Big-endian）：高位字节存低地址（网络字节序、PowerPC）
  - 小端序（Little-endian）：低位字节存低地址（x86/x86_64、ARM默认）
- **数据对齐要求（Alignment/Padding）**：数据在内存中的起始地址必须是其大小的整数倍，编译器会自动填充padding字节以满足对齐要求，这直接影响结构体大小。

例如：
```c
// 32位x86下，这个结构体大小可能是8字节而非5字节
struct Example {
    char a;      // 1字节，后填充3字节
    int b;       // 4字节
};
```

### 2. 函数调用约定（Calling Convention）

调用约定定义了函数调用时参数如何传递、返回值放在哪里、栈由谁清理，是ABI的核心。

- **参数传递**：前几个参数通常用寄存器传递（速度快），多余参数压栈
- **返回值**：整数/指针返回值通常放在特定寄存器（如x86_64的rax）
- **栈清理责任**：
  - caller-save：调用者负责清理栈上的参数
  - callee-save：被调用者负责恢复栈状态
- **常见调用约定**：
  - `cdecl`：C语言默认约定，caller清理栈，支持可变参数（如printf）
  - `stdcall`：Win32 API默认约定，callee清理栈
  - `fastcall`：前两个参数用ecx、edx传递，其余压栈
  - **System V AMD64**：Linux/macOS/BSD的64位约定，前6个整数参数用rdi、rsi、rdx、rcx、r8、r9传递

### 3. 内存布局

定义了复合数据类型在内存中的排列方式：

- **结构体/类成员偏移量**：每个成员相对于结构体起始地址的偏移位置，必须在编译时确定
- **虚函数表（vtable）布局**：C++多态实现的核心，虚函数指针在对象内存中的位置、虚函数表中函数指针的顺序必须严格一致
- **继承时的内存排列**：基类子对象在派生类中的位置、多重继承时的偏移调整、虚继承的额外指针位置

如果内存布局不一致，访问成员变量或调用虚函数时就会读到错误的数据或跳到错误的地址，导致程序崩溃。

### 4. 符号命名修饰（Name Mangling）

C++支持函数重载、命名空间、类等特性，编译器需要将源码中的函数名修饰成唯一的符号名，这就是Name Mangling。

例如，C++函数`Foo::bar()`经过GCC修饰后可能变成`_ZN3Foo3barEv`。

不同编译器的修饰规则不同，这就是为什么C++编译器之间的二进制兼容性比C差很多。`extern "C"`的作用就是告诉C++编译器按照C语言的方式修饰符号名（不做额外修饰），这样C++代码就能和C代码在二进制层面互操作。

### 5. 系统调用号

操作系统内核提供服务的编号约定是用户态与内核态之间最基础的ABI。用户态程序通过特定的中断指令（如x86的`int 0x80`）或专用指令（如x86_64的`syscall`）陷入内核，系统调用号放在约定的寄存器中（如x86_64的rax），内核根据这个编号找到对应的服务函数。

系统调用号是操作系统最稳定的ABI之一，Linux内核承诺系统调用号一旦确定就不会改变。

## 应用场景

ABI虽然底层，但在许多关键场景中发挥着不可替代的作用：

### 编译器开发

为什么同一平台不同编译器需要兼容ABI？因为开发者可能用GCC编译程序，用Clang编译依赖库，或者反过来。如果两个编译器不遵循同一套ABI约定，它们编译出来的目标文件就无法链接到一起。这就是为什么类Unix系统都遵循System V ABI，Windows遵循Microsoft ABI。

### 跨语言调用（FFI - Foreign Function Interface）

跨语言调用本质上就是通过C ABI作为桥梁：

- **Python ctypes/cffi**：Python直接调用C共享库
- **Java JNI（Java Native Interface）**：Java调用C/C++代码
- **Go cgo**：Go调用C代码
- **Node.js N-API**：Node.js调用C/C++扩展模块
- **Rust FFI**：Rust声明`extern "C"`函数与其他语言互操作

几乎所有跨语言调用最终都通过C ABI实现，因为C ABI是最通用、最稳定的二进制约定。

### 操作系统系统调用接口

用户态程序与内核之间的唯一接口就是系统调用ABI。libc（如glibc、musl）封装了系统调用，但程序也可以直接通过syscall指令调用内核服务。系统调用ABI的稳定性保证了几十年前编译的程序在最新内核上依然能运行。

### 动态链接库二进制兼容

- Windows：DLL（Dynamic-Link Library）
- Linux：.so（Shared Object）
- macOS：.dylib

动态链接的核心就是ABI兼容：只要共享库导出的符号和调用约定不变，更新共享库不需要重新编译依赖它的所有程序。这就是Linux发行版可以独立升级系统库的基础。

### 插件系统

浏览器插件、IDE插件、图像处理软件插件（如Photoshop滤镜）等都是基于预定义的二进制接口。插件是预编译的二进制模块，宿主程序加载插件时不需要插件源代码，只要双方遵循相同的ABI约定即可。

## 实战案例：Python ctypes调用C标准库

我们通过Python的ctypes模块展示如何通过ABI直接调用二进制共享库中的函数，完全不需要重新编译C代码。

C标准库的`printf`函数我们非常熟悉，它已经以二进制形式存在于系统中，Python可以通过ABI直接调用它。

```python
import ctypes
import sys

# 根据平台加载C标准库
if sys.platform == 'win32':
    libc = ctypes.CDLL('msvcrt.dll')
else:
    libc = ctypes.CDLL('libc.so.6')

# 按照C ABI约定设置函数参数和返回值类型
# int printf(const char *format, ...);
libc.printf.argtypes = [ctypes.c_char_p]
libc.printf.restype = ctypes.c_int

# 构造C风格字符串（字节串）
message = b"Hello from ABI! printf called directly from Python, no compilation needed!\n"

# 调用二进制层面的printf函数
# 参数按照System V AMD64调用约定传递到寄存器
# 执行流直接跳转到libc中printf的机器码地址
libc.printf(message)

# 再调用一个：计算字符串长度
libc.strlen.argtypes = [ctypes.c_char_p]
libc.strlen.restype = ctypes.c_size_t

length = libc.strlen(message)
print(f"(Python side) Message length: {length}")
```

运行这个Python脚本，你会看到C标准库的`printf`直接输出了文本。整个过程中：
- 我们没有C标准库的源代码
- 没有编译任何C代码
- Python解释器按照C ABI约定设置好参数和返回值位置
- 直接跳转到libc.so.6中printf函数的机器码地址执行
- 这就是ABI在跨语言调用中的实际作用

---

**上一章：** [02 - API：源码与服务级契约](02-api.md)  
**下一章：** [04 - Protocol：通信规则约定](04-protocol.md)
