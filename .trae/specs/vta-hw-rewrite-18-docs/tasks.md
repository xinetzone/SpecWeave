# VTA-HW 18篇虚构文档重写 - The Implementation Plan

## [ ] Task 1: 重写ISA模块6篇文档（VH-133~VH-138）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 基于 d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\core\ISA.scala 重写
  - 6篇文档对应6个维度：
    - VH-133: ISA模块指令流与控制逻辑分析（指令编码格式、BitPat匹配机制、指令解码流程）
    - VH-134: ISA模块参数化配置与版本差异（OP_BITS/M_*_BITS/C_*_BITS等位宽参数、TODO注释中提到的未来扩展）
    - VH-135: ISA模块模块接口与信号契约（ISAConstants trait的混入方式、ISA object的公开方法）
    - VH-136: ISA模块定点量化与精度路径（通过指令如何控制量化、ALU操作与精度的关系）
    - VH-137: ISA模块构建依赖与集成机制（ISA如何被Fetch/Decode模块使用、BitPat模式匹配在Chisel中的工作方式）
    - VH-138: ISA模块性能瓶颈与NPU优化方向（指令编码密度、扩展空间、VXOR等TODO项）
- **Acceptance Criteria Addressed**: [AC-1, AC-4]
- **Test Requirements**:
  - `programmatic` TR-1.1: INST_BITS=128, OP_BITS=3等所有位宽常量与源码一致
  - `programmatic` TR-1.2: 9条指令（LUOP/LWGT/LINP/LACC/SOUT/GEMM/VMIN/VMAX/VADD/VSHX/FNSH）名称正确
  - `programmatic` TR-1.3: 操作码编码值正确（OP_L=0, OP_S=1, OP_G=2, OP_F=3, OP_A=4, OP_X=5）
  - `programmatic` TR-1.4: memId编码正确（uop=000, wgt=001, inp=010, acc=011, out=100）
  - `programmatic` TR-1.5: aluId编码正确（minpool=000, maxpool=001, add=010, shift=011）
  - `human-judgement` TR-1.6: 文档格式与VH-019等高质量文档一致
- **Notes**: 必须读取ISA.scala完整内容，逐行核对常量定义和BitPat模式

## [ ] Task 2: 重写Configs模块6篇文档（VH-139~VH-144）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 基于两个Configs.scala文件重写：
    - d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\core\Configs.scala（CoreParams和CoreConfig）
    - d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\vta\Configs.scala（顶层DefaultConfig）
  - 6篇文档对应6个维度：
    - VH-139: Configs模块数据通路与微架构剖析（CoreParams如何定义数据通路宽度、SRAM深度等关键参数）
    - VH-140: Configs模块模块接口与信号契约（CoreKey字段、Parameters隐式传参机制、Config混合组合方式）
    - VH-141: Configs模块构建依赖与集成机制（CoreConfig与ShellConfig如何通过++组合、Config对象的链式构建）
    - VH-142: Configs模块参数化配置与版本差异（batch/blockIn/blockOut等参数对硬件规模的影响、不同FPGA平台配置差异）
    - VH-143: Configs模块定点量化与精度路径（inpBits/wgtBits/accBits/outBits如何决定数据通路精度、量化位宽配置）
    - VH-144: Configs模块性能瓶颈与NPU优化方向（参数调整对性能/面积的影响、blockOutFactor=1的优化空间、instQueueEntries深度优化）
- **Acceptance Criteria Addressed**: [AC-2, AC-4]
- **Test Requirements**:
  - `programmatic` TR-2.1: CoreParams全部16个参数名称和默认值与源码完全一致
  - `programmatic` TR-2.2: uopBits % 8 == 0约束被准确记录
  - `programmatic` TR-2.3: 三个DefaultConfig组合关系正确（CoreConfig ++ PynqConfig/F1Config/De10Config）
  - `human-judgement` TR-2.4: 文档格式与现有高质量文档一致
- **Notes**: 区分core/Configs.scala（CoreParams）和vta/Configs.scala（DefaultConfig）两个文件

## [ ] Task 3: 重写package模块6篇文档（VH-145~VH-150）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 基于 d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\core\package.scala 重写
  - package.scala只有23行，核心是`package object core extends vta.core.ISAConstants`
  - 6篇文档需要基于这个简单但重要的机制展开，不要虚构内容：
    - VH-145: package模块模块接口与信号契约（解释package object是什么、extends ISAConstants意味着什么、哪些常量被全局可见）
    - VH-146: package模块参数化配置与版本差异（package机制是Scala语言特性、不同Scala版本package object行为差异、TODO: deprecate ISAConstants的演进方向）
    - VH-147: package模块构建依赖与集成机制（为什么通过package object让ISAConstants全局可见、这如何简化其他模块的import、与Chisel导入的关系）
    - VH-148: package模块定点量化与精度路径（全局可见的ISAConstants如何让量化参数在解码/执行模块中直接使用、位宽常量的全局一致性保证）
    - VH-149: package模块异常路径与健壮性设计（这是一个纯声明文件，无运行时逻辑；说明其简单性如何减少出错可能、全局常量的命名空间污染风险）
    - VH-150: package模块性能瓶颈与NPU优化方向（TODO: Eventually deprecate ISAConstants的演进路径、用ISA object替代trait的可能改进）
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-3.1: 准确描述package object core extends ISAConstants这一核心机制
  - `programmatic` TR-3.2: 不虚构任何源码中不存在的类、模块或函数
  - `human-judgement` TR-3.3: 基于真实内容（仅23行代码）展开分析，不灌水
  - `human-judgement` TR-3.4: 文档格式与现有高质量文档一致
- **Notes**: package.scala内容极少，分析要深入但不虚构，解释Scala包对象机制的作用即可

## [ ] Task 4: 对抗审查-验证重写文档与源码一致性
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 逐篇读取重写后的18篇文档
  - 逐行核对文档中的所有事实性描述（常量值、参数值、指令名称、编码、机制描述）
  - 在源码中找到对应证据，标记源码行号
  - 检查是否有任何虚构内容、错误描述、与源码不一致之处
  - 如有问题直接修正
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有数值常量（位宽、参数默认值）在源码中有对应
  - `programmatic` TR-4.2: 所有指令名称、操作码、编码与源码一致
  - `human-judgement` TR-4.3: 无虚构模块、无过度推断
  - `human-judgement` TR-4.4: YAML frontmatter完整，sources字段正确
