#!/usr/bin/env python3
"""
TVM FFI 核心概念和API演示脚本
==============================

使用方法：
    python examples_demo.py

前置条件：
    - tvm_ffi 已正确安装（从源码编译安装：cd vendor/tvm-ffi && pip install -e .）
    - 可选依赖：numpy（Tensor演示）、torch（PyTorch互操作演示）
    - inline_module 演示需要：C++17编译器（MSVC/GCC/Clang）、CMake、Ninja

本脚本按模块演示TVM FFI的核心功能：
1. 基础API：全局函数注册与调用
2. 容器类型：Array/Map/List/Dict/String
3. Tensor/DLPack：与NumPy/PyTorch零拷贝互操作
4. dataclass反射：@py_class定义Python反射对象
5. inline_module：即时编译C++代码
"""

from __future__ import annotations

import sys
from typing import Any


def print_section(title: str) -> None:
    """打印分节标题"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def main() -> None:
    print_section("0. 环境检查")
    print(f"Python版本: {sys.version}")
    print()

    try:
        import tvm_ffi
    except ImportError as e:
        print("❌ 无法导入 tvm_ffi！")
        print()
        print("请按以下步骤安装：")
        print("  1. 确保已克隆 tvm-ffi 源码（含子模块）：")
        print("     git submodule update --init --recursive")
        print()
        print("  2. 从源码编译安装（需要 C++17 编译器、CMake、Ninja）：")
        print("     cd projects/xuanspace/vendor/tvm-ffi")
        print("     pip install --no-build-isolation -e .")
        print()
        print(f"  错误详情: {e}")
        sys.exit(1)

    print(f"✅ tvm_ffi 版本: {tvm_ffi.__version__}")
    print(f"✅ 核心库路径: {tvm_ffi.LIB._name if hasattr(tvm_ffi.LIB, '_name') else '已加载'}")

    # ========================================================================
    # 1. 基础API演示：全局函数注册与调用
    # ========================================================================
    print_section("1. 基础API演示 - 全局函数注册与调用")

    # 1.1 注册Python函数到全局注册表
    print("--- 1.1 register_global_func 注册Python函数 ---")

    def add_numbers(a: int, b: int) -> int:
        """简单的加法函数"""
        return a + b

    def greet(name: str) -> str:
        """问候函数"""
        return f"Hello, {name}! from TVM FFI"

    tvm_ffi.register_global_func("demo.add_numbers", add_numbers)
    tvm_ffi.register_global_func("demo.greet", greet)
    print("已注册函数: demo.add_numbers, demo.greet")

    # 1.2 获取并调用全局函数
    print("\n--- 1.2 get_global_func 获取并调用函数 ---")
    add_fn = tvm_ffi.get_global_func("demo.add_numbers")
    greet_fn = tvm_ffi.get_global_func("demo.greet")

    result1 = add_fn(3, 5)
    result2 = greet_fn("TVM FFI")
    print(f"add_numbers(3, 5) = {result1}")
    print(f"greet('TVM FFI') = {result2}")

    # 1.3 调用testing模块中预注册的测试函数
    print("\n--- 1.3 调用 tvm_ffi.testing 预注册函数 ---")
    try:
        from tvm_ffi import testing

        if hasattr(testing, "add_one"):
            result = testing.add_one(41)
            print(f"testing.add_one(41) = {result}")
        else:
            print("testing.add_one 不可用（需要编译C++扩展）")
    except Exception as e:
        print(f"testing模块演示跳过: {e}")

    # ========================================================================
    # 2. 容器类型演示
    # ========================================================================
    print_section("2. 容器类型演示")

    # 2.1 Array（不可变数组）
    print("--- 2.1 Array（不可变数组）---")
    arr = tvm_ffi.Array([1, 2, 3, 4, 5])
    print(f"创建Array: {arr}")
    print(f"类型: {type(arr)}")
    print(f"长度: {len(arr)}")
    print(f"arr[0] = {arr[0]}, arr[-1] = {arr[-1]}")
    try:
        arr[0] = 100
    except Exception as e:
        print(f"尝试修改Array（预期失败）: {type(e).__name__}")

    # 2.2 Map（不可变映射）
    print("\n--- 2.2 Map（不可变映射）---")
    m = tvm_ffi.Map({"name": "tvm-ffi", "version": 1, "tags": ["ffi", "ml"]})
    print(f"创建Map: {dict(m)}")
    print(f"类型: {type(m)}")
    print(f"m['name'] = {m['name']}")
    print(f"键列表: {list(m.keys())}")
    try:
        m["new_key"] = "value"
    except Exception as e:
        print(f"尝试修改Map（预期失败）: {type(e).__name__}")

    # 2.3 List（可变数组）
    print("\n--- 2.3 List（可变数组）---")
    lst = tvm_ffi.List([10, 20, 30])
    print(f"创建List: {list(lst)}")
    lst.append(40)
    print(f"append(40)后: {list(lst)}")
    lst[0] = 100
    print(f"修改lst[0]=100后: {list(lst)}")
    print(f"类型: {type(lst)}")

    # 2.4 Dict（可变映射）
    print("\n--- 2.4 Dict（可变映射）---")
    d = tvm_ffi.Dict({"a": 1})
    print(f"创建Dict: {dict(d)}")
    d["b"] = 2
    d["a"] = 100
    print(f"修改后: {dict(d)}")
    print(f"类型: {type(d)}")

    # 2.5 String
    print("\n--- 2.5 String ---")
    s = tvm_ffi.container.String("Hello from TVM FFI String!")
    print(f"创建String: {s}")
    print(f"类型: {type(s)}")
    print(f"长度: {len(s)}")
    print(f"Python str转换: {str(s)}")

    # ========================================================================
    # 3. Tensor/DLPack互操作演示
    # ========================================================================
    print_section("3. Tensor/DLPack互操作演示")

    have_numpy = False
    try:
        import numpy as np
        have_numpy = True
    except ImportError:
        print("⚠️ numpy未安装，跳过NumPy互操作演示")
        print("   安装命令: pip install numpy")

    if have_numpy:
        print("--- 3.1 NumPy Array → TVM FFI Tensor ---")
        np_x = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        print(f"NumPy数组: {np_x}, dtype={np_x.dtype}, shape={np_x.shape}")

        tensor_x = tvm_ffi.Tensor.from_numpy(np_x)
        print(f"转换为Tensor: shape={tensor_x.shape}, dtype={tensor_x.dtype}")
        print(f"Tensor设备: {tensor_x.device}")

        print("\n--- 3.2 TVM FFI Tensor → NumPy Array ---")
        np_y = tensor_x.numpy()
        print(f"转回NumPy: {np_y}")
        print(f"数据一致: {np.allclose(np_x, np_y)}")

        print("\n--- 3.3 Tensor零拷贝验证 ---")
        np_y[0] = 999.0
        print(f"修改转回的NumPy数组[0]=999后，原Tensor[0]={float(tensor_x[0])}")
        print("（DLPack约定：转换共享内存，非拷贝）")

    # PyTorch互操作
    have_torch = False
    try:
        import torch
        have_torch = True
    except ImportError:
        print("\n⚠️ torch未安装，跳过PyTorch互操作演示")
        print("   安装命令: pip install torch")

    if have_torch and have_numpy:
        print("\n--- 3.4 PyTorch Tensor ↔ TVM FFI Tensor（零拷贝）---")
        try:
            torch_x = torch.tensor([1.0, 2.0, 3.0], dtype=torch.float32)
            print(f"PyTorch Tensor: {torch_x}")

            tensor_from_torch = tvm_ffi.from_dlpack(torch_x)
            print(f"转为TVM Tensor: shape={tensor_from_torch.shape}")

            torch_back = torch.from_dlpack(tensor_from_torch)
            print(f"转回PyTorch: {torch_back}")
            print(f"数据一致: {torch.allclose(torch_x, torch_back)}")

            torch_x[0] = 100.0
            print(f"修改原PyTorch tensor[0]=100后，TVM Tensor[0]={float(tensor_from_torch[0])}")
            print("✅ PyTorch零拷贝互操作验证成功！")
        except Exception as e:
            print(f"PyTorch互操作演示遇到问题（可能需要CUDA或版本匹配）: {e}")

    # ========================================================================
    # 4. dataclass反射演示：@py_class
    # ========================================================================
    print_section("4. dataclass反射演示 - @py_class")

    from tvm_ffi import Object, method
    from tvm_ffi.dataclasses import py_class

    @py_class("demo.Point")
    class Point(Object):
        """二维点对象，使用@py_class注册到FFI反射系统"""
        x: float
        y: float

        @method
        def distance_from_origin(self) -> float:
            """计算到原点的距离"""
            return (self.x ** 2 + self.y ** 2) ** 0.5

        @method
        def translate(self, dx: float, dy: float) -> "Point":
            """平移点，返回新的Point"""
            return Point(x=self.x + dx, y=self.y + dy)

        @staticmethod
        @method
        def origin() -> "Point":
            """创建原点(0,0)"""
            return Point(x=0.0, y=0.0)

    print("已使用@py_class注册 demo.Point 类")

    # 创建对象
    p1 = Point(x=3.0, y=4.0)
    p_origin = Point.origin()
    p2 = p1.translate(1.0, 2.0)

    print(f"\np1 = Point(x=3.0, y=4.0)")
    print(f"p1.x = {p1.x}, p1.y = {p1.y}")
    print(f"p1到原点距离 = {p1.distance_from_origin():.1f}")
    print(f"原点 = ({p_origin.x}, {p_origin.y})")
    print(f"p1.translate(1,2) = ({p2.x}, {p2.y})")
    print(f"p1 repr: {p1}")

    # 类型信息
    type_info = Point.__tvm_ffi_type_info__
    print(f"\n类型key: {type_info.key}")
    print(f"字段数: {len(type_info.fields)}")
    print(f"方法数: {len(type_info.methods)}")
    method_names = [m.name for m in type_info.methods]
    print(f"已注册方法: {method_names}")

    # 结构体相等性测试
    p3 = Point(x=3.0, y=4.0)
    print(f"\nstructural_equal(p1, p3) = {tvm_ffi.structural_equal(p1, p3)}")
    print(f"p1.same_as(p3) = {p1.same_as(p3)}（指针比较，不同实例）")

    # ========================================================================
    # 5. inline_module演示：即时编译C++代码
    # ========================================================================
    print_section("5. inline_module演示 - load_inline（即时编译C++）")

    print("提示：此演示需要C++17编译器（MSVC/GCC/Clang）、CMake、Ninja")
    print("首次运行会自动编译并缓存，后续运行直接加载缓存\n")

    try:
        import tvm_ffi.cpp

        add_one_source = r"""
        #include <cstdint>

        int64_t add_one_cpp(int64_t x) {
            return x + 1;
        }

        void vector_add_cpp(tvm::ffi::TensorView a,
                            tvm::ffi::TensorView b,
                            tvm::ffi::TensorView out) {
            DLDataType f32{kDLFloat, 32, 1};
            TVM_FFI_ICHECK(a.dtype() == f32) << "a must be float32";
            TVM_FFI_ICHECK(b.dtype() == f32) << "b must be float32";
            TVM_FFI_ICHECK(out.dtype() == f32) << "out must be float32";
            TVM_FFI_ICHECK(a.ndim() == 1 && b.ndim() == 1 && out.ndim() == 1);
            TVM_FFI_ICHECK(a.size(0) == b.size(0) && a.size(0) == out.size(0));

            int64_t n = a.size(0);
            const float* pa = static_cast<const float*>(a.data_ptr());
            const float* pb = static_cast<const float*>(b.data_ptr());
            float* pout = static_cast<float*>(out.data_ptr());
            for (int64_t i = 0; i < n; ++i) {
                pout[i] = pa[i] + pb[i];
            }
        }
        """

        print("正在编译C++代码（首次运行需要较长时间）...")
        mod = tvm_ffi.cpp.load_inline(
            name="demo_inline",
            cpp_sources=add_one_source,
            functions=["add_one_cpp", "vector_add_cpp"],
        )
        print("✅ C++模块编译并加载成功！")

        result = mod.add_one_cpp(41)
        print(f"\nmod.add_one_cpp(41) = {result}")

        if have_numpy:
            print("\n--- NumPy ↔ 编译的C++函数 零拷贝调用 ---")
            a_np = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
            b_np = np.array([10.0, 20.0, 30.0, 40.0, 50.0], dtype=np.float32)
            out_np = np.empty_like(a_np)

            a_t = tvm_ffi.Tensor.from_numpy(a_np)
            b_t = tvm_ffi.Tensor.from_numpy(b_np)
            out_t = tvm_ffi.Tensor.from_numpy(out_np)

            mod.vector_add_cpp(a_t, b_t, out_t)
            print(f"a = {a_np}")
            print(f"b = {b_np}")
            print(f"vector_add(a, b) = {out_np}")
            print(f"预期结果: {a_np + b_np}")
            print(f"结果正确: {np.allclose(out_np, a_np + b_np)}")

    except Exception as e:
        print(f"⚠️ inline_module演示跳过:")
        print(f"   原因: {type(e).__name__}: {e}")
        print()
        print("可能的原因：")
        print("  1. 未安装C++编译器（需要MSVC 2022/GCC 9+/Clang 10+）")
        print("  2. 未安装CMake或Ninja")
        print("  3. 编译器不在PATH中")
        print()
        print("Windows提示：请在「x64 Native Tools Command Prompt for VS 2022」中运行")

    # ========================================================================
    # 完成
    # ========================================================================
    print_section("完成")
    print("所有演示完成！")
    print()
    print("下一步建议：")
    print("  - 阅读 tvm-ffi 文档: projects/xuanspace/vendor/tvm-ffi/docs/")
    print("  - 查看更多示例: projects/xuanspace/vendor/tvm-ffi/examples/")
    print("  - 运行测试: cd projects/xuanspace/vendor/tvm-ffi && pytest tests/python -v")


if __name__ == "__main__":
    main()
