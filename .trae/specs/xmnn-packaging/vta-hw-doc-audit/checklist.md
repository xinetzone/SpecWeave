# VTA-HW 文档与源码偏差审计 - Verification Checklist

## 审计基础设施检查
- [ ] 文档-源码映射表完整，覆盖chisel-core全部150篇文档
- [ ] 源码版本确认（xmtools/npu_tvm当前commit hash记录）
- [ ] 偏差分类标准（4类×3级）明确定义
- [ ] .meta/目录下前期事实文件已读取并作为参考基准

## Core模块审计检查
- [ ] 子模块实例化（Fetch/Load/Compute/Store/EventCounters）描述正确
- [ ] VME读通道rd(0)~rd(4)分配描述正确
- [ ] VME写通道wr(0)分配描述正确
- [ ] i_post/o_post后同步信号连接描述与源码一致（重点：双向环形而非三级线性）
- [ ] VCR接口信号（launch/ptrs/vals/finish/ecnt/ucnt）描述正确
- [ ] 指令分发（inst.ld/inst.co/inst.st）描述正确
- [ ] 数据张量传递（inp/wgt/out）连接描述正确

## Compute模块审计检查
- [ ] 子模块构成描述正确
- [ ] uop/acc加载逻辑描述正确
- [ ] 输入/权重/累加器SRAM接口描述正确
- [ ] 与Load/Store的post信号连接正确
- [ ] finish信号生成逻辑正确

## Decode模块审计检查
- [ ] 指令解码逻辑描述正确
- [ ] 指令字段拆分与源码一致
- [ ] 指令队列（instQueueEntries）描述正确

## Fetch模块审计检查
- [ ] 指令获取逻辑描述正确
- [ ] PC（程序计数器）行为描述正确
- [ ] VME指令读取通道使用正确
- [ ] 各Fetch变体（VME64/WideVME）差异描述准确

## Load/Store模块审计检查
- [ ] DRAM地址计算（基地址+偏移）描述正确
- [ ] VME通道分配正确
- [ ] 与Compute模块的inp/wgt/out数据连接正确
- [ ] post信号握手逻辑描述正确
- [ ] 数据位宽转换描述正确

## TensorLoad/TensorStore模块审计检查
- [ ] 各变体（NarrowVME/Simple/WideVME）功能差异描述准确
- [ ] 张量分块（tiling）逻辑描述正确
- [ ] 数据排布转换描述正确
- [ ] SRAM读写时序描述正确

## TensorGemm/TensorAlu模块审计检查
- [ ] MAC阵列结构描述正确（blockIn×blockOut等参数）
- [ ] 累加器（acc）数据通路描述正确
- [ ] ALU操作类型描述与源码一致
- [ ] 量化/饱和处理描述正确
- [ ] uop微操作调度逻辑描述正确

## ISA/Configs模块审计检查
- [ ] 指令编码字段（内存指令/计算指令等）位宽定义与源码一致
- [ ] Configs参数（batch/blockIn/blockOut/inpBits/wgtBits等）定义正确
- [ ] 不同配置（pynq/ultra96/de10nano等）差异描述准确

## Shell/DPI层审计检查
- [ ] VCRClient/VMEMaster Bundle接口定义正确
- [ ] VTAShell顶层连接描述正确
- [ ] DPI仿真模块（VTASimDPI/VTAMemDPI/VTAHostDPI）功能描述正确
- [ ] AXI接口信号描述正确

## Git历史与根因检查
- [ ] 关键文件git log已获取
- [ ] Critical/Major偏差的可能根因已分析（版本差异/理解错误/生成幻觉）
- [ ] 与上游apache/tvm VTA版本差异已识别（如有）

## 统计与报告检查
- [ ] 偏差汇总表完整（按模块/严重程度/类型）
- [ ] 各模块偏差率已计算
- [ ] 高风险模块（偏差率>30%）已标记
- [ ] 报告中所有源码引用使用file:///可点击链接格式
- [ ] 修正建议具体可执行
- [ ] 报告输出位置正确（.chaos/docs/xmnn/.meta/）
