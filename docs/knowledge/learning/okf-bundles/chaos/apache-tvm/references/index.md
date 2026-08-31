# References 索引

本目录包含 Apache TVM 知识包的参考资料，包括知识地图、事实清单和信源登记。

## 知识地图

| 文件 | 说明 |
|------|------|
| [insights.md](insights.md) | TVM 架构洞察与核心论点知识地图 |

## 事实清单

事实清单基于源码采集，每条事实标注文件路径与行号，零推测。

| 文件 | 涵盖范围 | 事实数量 |
|------|---------|---------|
| [facts-tvm-ffi.md](facts-tvm-ffi.md) | FFI 基础设施：Object 系统、Function/Registry、容器、Any、C ABI、Module 系统、反射、错误处理 | 详见文件 |
| [facts-ir-tir.md](facts-ir-tir.md) | IR 核心与 TIRx：表达式/语句节点、SBlock、Schedule、调度原语、MetaSchedule、Python 绑定 | 详见文件 |
| [facts-relax-te-topi.md](facts-relax-te-topi.md) | Relax/TE/TOPI：Relax IR、算子、Pass、后端、TE 张量表达式、TOPI 算子库、Python 绑定 | 244 |
| [facts-runtime-target-arith.md](facts-runtime-target-arith.md) | Runtime/Target/Arith/Support：DeviceAPI、NDArray、VM、RPC、Target/CodeGen、Arith 分析器 | 详见文件 |

## 信源登记

信源登记记录源码树的结构、文件统计和关键文件清单。

| 文件 | 源路径 | 文件数 | 涵盖范围 |
|------|--------|--------|---------|
| [tvm-ffi-source.md](tvm-ffi-source.md) | `d:\AI\.chaos\libs\ffi\tvm\` | 详见文件 | C ABI、C++ 核心、Python 绑定、Rust 绑定 |
| [ir-tir-source.md](ir-tir-source.md) | `d:\AI\.chaos\libs\ffi\tvm\` | 详见文件 | IR 核心、TIRx、Schedule、MetaSchedule |
| [relax-te-topi-source.md](relax-te-topi-source.md) | `d:\AI\.chaos\libs\ffi\tvm\` | 664 | Relax 图级 IR、TE、TOPI 算子库 |
| [runtime-target-arith-source.md](runtime-target-arith-source.md) | `d:\AI\.chaos\libs\ffi\tvm\` | 332 | Runtime、Target、Arith、Support、TVMScript、Driver |

```{toctree}
:maxdepth: 2

facts-ir-tir
facts-relax-te-topi
facts-runtime-target-arith
facts-tvm-ffi
insights
ir-tir-source
relax-te-topi-source
runtime-target-arith-source
tvm-ffi-source
```