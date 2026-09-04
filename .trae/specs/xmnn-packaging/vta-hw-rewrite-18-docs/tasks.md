# VTA-HW 18篇虚构文档重写 - The Implementation Plan

## [x] Task 1: 重写ISA模块6篇文档（VH-133~VH-138）
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成（对抗审查后修正aluId位位置105-107→108-110）
- **Description**: 基于ISA.scala重写6篇ISA文档，覆盖指令编码、参数位宽、接口契约、量化路径、构建机制、优化方向
- **Acceptance Criteria Addressed**: [AC-1, AC-4]
- **Verification**: 所有常量值、指令名称、编码与源码一致；13篇一次通过

## [x] Task 2: 重写Configs模块6篇文档（VH-139~VH-144）
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成（对抗审查后修正CoreParams参数数量16→15）
- **Description**: 基于core/Configs.scala和vta/Configs.scala重写6篇Configs文档，覆盖数据通路、接口契约、构建集成、参数配置、量化精度、优化方向
- **Acceptance Criteria Addressed**: [AC-2, AC-4]
- **Verification**: 15个参数名称和默认值完全正确；三个DefaultConfig组合关系正确

## [x] Task 3: 重写package模块6篇文档（VH-145~VH-150）
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成（对抗审查后修正OP_BITS行号:32→:33和字段提取示例代码）
- **Description**: 基于core/package.scala重写6篇package文档，解释package object extends ISAConstants机制，覆盖接口契约、版本差异、构建集成、精度一致性、健壮性、优化方向
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Verification**: 无虚构模块；核心机制描述准确；Scala语言特性解释正确

## [x] Task 4: 对抗审查-验证重写文档与源码一致性
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Status**: ✅ 已完成（修正5篇共11处错误后100%通过）
- **Description**: 逐篇核对18篇文档的所有事实性描述，修正发现的所有错误
- **Acceptance Criteria Addressed**: [AC-5]
- **修正汇总**：
  - VH-133/VH-138: aluId位位置105-107→108-110（BitPat拼接顺序：17+3+105+3=128）
  - VH-139: CoreParams参数数量16→15（实际为15个命名参数）
  - VH-145/VH-148: OP_BITS行号:32→:33
  - VH-148: memId字段提取代码修正（需包含M_DEP_BITS=4偏移，正确位置bit 7-9）
- **最终通过率**: 18/18 = 100%
