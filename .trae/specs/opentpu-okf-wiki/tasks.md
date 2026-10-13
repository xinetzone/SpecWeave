# openTPU 源码 → OKF Wiki 教程知识包 - 实施计划（tasks）

> 工作流：source-code-to-okf-wiki v1.5.0（G0 信源固定 → R → I → E → V → C），七概念场景4。
> 固定信源：`ffe997e9a8b8607b07b3d1bb3c1132db0faf044e`（2026-10-12，远程 FeSens/openTPU）。
> 产出根：`projects/awesome-okf-xs/doc/bundles/jishu/iot/opentpu/`（下称 BUNDLE）。
> 每批 ≤7 文件；index 永远最后写；数量事实只信脚本计数；工作底稿先放 `.trae/specs/opentpu-okf-wiki/`，发布版移入 BUNDLE/references/。

## Task 1: R-0 信源复核与审计基线锁定

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 复核本地审计副本仍检出 ffe997e 且工作树干净（`git rev-parse HEAD` + `git status --porcelain`）；登记 remote URL、提交日期、与 v0.5(730ca28，落后1499)、8eaa4806(相距232) 的关系到工作底稿。
  - 建立 ffe997e blob 只读取证手段：`git show ffe997e:<path>` 与 Grep 对工作树（前提：工作树==HEAD，已核）；所有计数命令在底稿记录完整命令行与输出。
  - 列出 R 阶段阅读清单（按六层链排序，见 Notes），确认每个待引文件在 ffe997e 存在。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-1.1: 底稿记录 HEAD 全 hash == ffe997e…44e 且 porcelain 为空，附命令输出。
  - `rule` TR-1.2: 阅读清单每个路径 `git cat-file -e ffe997e:<path>` rc=0。
- **Notes**: 阅读清单——README.md；docs/{isa,compiler,quant,offload,mtp,stream,board,host,lens,benchmarks,formats,targets,scoreboard,observability,prefill,serve}.md；docs/superpowers/specs/2026-09-23-opentpu-design.md；docs/superpowers/specs/2026-10-10-multi-target-design.md；opentpu/{isa.py,language.py,compiler.py,isasim.py,fp32.py,quant.py,lens.py,rtlsim.py,target.py,runtime.py}；opentpu/kernels/*；rtl/{top,mxu,vpu,dma,mem,seq,shell,tech}/关键 .sv；boards/ypcb-00338/*；targets/*.toml；asic/nangate45/*（PPA 文档）；tools/{validate,scoreboard}.py；tests/ 清单；pyproject.toml/Makefile。

## Task 2: R-1 规模计数与知识地图事实底座

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 对全部计划写入正文的数量断言脚本计数，至少含：ISA 指令（助记符数与 opcode 集合，来源 opentpu/isa.py + docs/isa.md 双口径）、VOP 功能码数（func 0-20 实际定义数）、LOOP 深度、寄存器数、参数默认值（S/D/MCOLS/ACT_ROWS/LANES/WIN）、kernels 文件数与内核函数数、RTL .sv 文件数（按 mxu/vpu/dma/mem/seq/top/shell/tech 分组）、tests 文件数（按 test_ 前缀分组）、docs .md 篇数、llm 模型适配文件数与 README 结果表模型数/行数、targets/*.toml 数、VOP 函数在 isasim 与 otpu_fp.sv 的实现配对数。
  - 每个数字记录：命令、原始匹配数、去重名数（如适用）、口径说明、取证时间；写入工作底稿 `facts-draft.md` 的计数专章。
  - 产出模块知识地图（目录树 + 每个模块 1-3 句职责 + 关键入口符号），供 I/E 阶段使用。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 计数清单 ≥15 项，每项有可复跑命令与原始输出摘录；无「人工数出」数字。
  - `rule` TR-2.2: ISA 指令数/VOP 数采用「Python 定义 + 文档表格」双源，差异显式记录。
- **Notes**: 用 `git grep -c`/Select-String 统计时固定路径前缀；Windows 下优先 `git grep <pat> ffe997e -- <pathspec>` 保证对 blob 取证。

## Task 3: R-2 六层链深读与事实登记（F-xxx）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 按六层链深读并登记事实（文件:行号区间 + 短引文）：
    - L0 契约层：README 阅读路径/复现命令/结果表口径；docs/isa.md 指令编码（8×32-bit 字、字段位段）；opentpu/isa.py 编码常量。
    - L1 数值层：fp32.py RNE/FTZ/canonical NaN/exp2/recip/rsqrt/log2 固定序列；isasim.py 与 rtl/vpu/otpu_fp.sv 三处一致性组织方式。
    - L2 计算层：MM 整数累加边界（<2^47）、ACT RAM、MXU 四列脉动阵列（rtl/mxu/otpu_mxu.sv DSP48E1）、DSTEP/STREAM；VPU 21 func；GATHER。
    - L3 量化层：quant.py 权重格式（int8/int4/E2M1 FP4/NVFP4 两级块缩放 4.25 bits/weight）、QACT 行缩放 Sa+子块偏移 da、QST、PAIR、RMAX/ASCALE flash-attention 修正、LM head 保 int8。
    - L4 软件层：language.py（@ol.jit、ol.load/ol.dot 等原语全集——Grep 登记）、compiler.py（布局即 API、仿射循环寻址、融合）、kernels/（attention/mlp/lib/layouts/mailbox/gather/deltanet 入口签名）。
    - L5 仿真/硬件层：isasim.py Machine/Config 接口、rtlsim.py、rtl/top/otpu_top.sv 与 slice/pkg/coll、seq、dma、mem（native_dram/tmem/actram）、boards/ypcb-00338 规格（xc7k480t、DDR3-1066、4GiB、133.33MHz、17.1GB/s——以板级文档为准）、targets/*.toml + target.py 单加载器、asic/nangate45 PPA 口径。
    - L6 验证/运行层：tools/validate.py 四行对照（device vs W+A、device vs fp32、W+A vs fp32、W+A~ 一ulp 扰动）、通过判据（top-1≥80%、mean KL ≤3×floor、--against 位级）、tools/scoreboard.py WIN=32；host/（board/offload/chat/smi/diag）、serve/（api/batching/scheduler）、lens.py roofline/时间线；MoE offload（153MB/token、1.41GB/s 等数字以 README 原文为准并标注作者报告）。
  - 事实编号 F-001 起连续编号，按模块分组入 `facts-draft.md`。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 每条事实含 path#Lxx-Lyy 与固定 hash；至少 120 条事实，覆盖六层全部层。
  - `rule` TR-3.2: 每个计划在正文使用的符号（ol 原语、Machine/Config、quantize_mxu、指令助记符等）在事实登记中有 Grep 命中行号。
  - `rule` TR-3.3: 板卡/性能数字逐条标注「项目作者报告」信源级。
- **Notes**: 大文件分段读（compiler.py 1712 行、otpu_mxu.sv 1570 行等），优先读文档再读实现；设计规格 docs/superpowers/specs/2026-09-23-opentpu-design.md 已在 Specify 阶段全文读过，结论复用但行号重新对 ffe997e 取。

## Task 4: R-3 概念页 F-053~F-072 基线对账

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 取概念页事实 F-053~F-072（必要时 git show 8eaa4806 旧版辅助），逐条在 ffe997e 核对：仍成立 / 扩展（数值或范围变大变小）/ 变更（接口或结论改变）/ 无法静态确认。
  - 重点核对项：README 结果表配置数（7→18）、模型数（→10）、指令集新增（STREAM 0x13、DSTEP 0x12 旧基线是否已有）、tests 数量与分组、板卡 0 ulp 组数与步数、生产镜像 tag、resident decode、otpu-serve、bcu1525、Nangate45、多 target 体系。
  - 对账表 20 行齐写入 facts-draft 专章。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 对账表恰好覆盖 F-053~F-072 共 20 条（编号连续无缺），每条有裁决+ffe997e 证据定位。
  - `rule` TR-4.2: 「变更/扩展」项的新数字来自 Task 2 脚本计数或原文行号，不得估算。

## Task 5: I 阶段 洞察四元组与知识地图定稿

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 基于 facts-draft 产出 3-5 个四元组洞察（陈述/证据/反常识点/可迁移行动），候选：①契约对拍——Python 模拟器与 RTL 互为 golden 的开发顺序与成本结构；②主动限制隐式行为（无 cache/无乱序/顺序机）如何让「位精确」可达成；③修复配反例（exp2/recip/rsqrt 一ulp 修复的测试纪律）；④量化不是降级开关而是 ISA 一等公民（QACT/PAIR/子块缩放的硬件契约）；⑤AI agent 产物归属与可审计性分离（设计文档即 commit、验证脚本即声明）。
  - 每个洞察标注适用边界与反模式；产出束知识地图（17 concepts 的依赖顺序与 matmul 贯穿路线）。
  - 工作底稿 `insights-draft.md`。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-5.1: 洞察 3-5 个，四元组字段齐全，每个证据指回 F-xxx 编号。
  - `rubric` TR-5.2: 知识沉淀深度；scale 1-5；anchors 同 AC-8；threshold ≥4；evidence 为 insights 草稿与 concept 16 提纲评审。
- **Notes**: 洞察先于正文写作冻结，E 阶段只消费不新造（新洞察回灌需同步更新 insights）。

## Task 6: E-0 references 信源先行（4 份 + references/index 最后统一写）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 按顺序落盘 BUNDLE/references/：
    1. `source-code-map.md`（type: Reference）：信源四要素（canonical URL https://github.com/FeSens/openTPU、固定全 hash、日期、审计副本说明但不写本地路径）、目录地图、六层文件清单、版本关系（v0.5/8eaa4806/ffe997e）、阅读顺序建议。
    2. `facts.md`（type: Reference）：facts-draft 发布版（去除本地路径，行号引用以 GitHub pinned URL 表达）。
    3. `insights.md`（type: Reference）：insights-draft 发布版。
    4. `verification.md`（type: Reference）：先建骨架（G1-G5 占位），V 阶段回填。
  - frontmatter 对齐 embedded-weekly-03 风格：generated.by=source-code-to-okf-wiki/E、verified、status: draft、stale_after: 2027-04-30、sources。
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-6.1: 4 份文件 frontmatter 可解析、type 正确；source-code-map 为 BUNDLE 内最先创建的内容文件（按提交批顺序记录于 log）。
  - `rule` TR-6.2: 全文扫描 0 个 file:///、0 个 `external/dao`、0 个 .tmp/.chaos 字样。
- **Notes**: references/index.md 在 Task 11 与其他 index 同批最后写。

## Task 7: E-1 concepts 批次 A：00-03（全景/机器模型/ISA/DMA）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - `concepts/00-overview.md`：项目定位、六层执行链总览、学习路径、matmul 贯穿路线图、证据边界声明（静态读码、作者报告口径）。
  - `concepts/01-machine-model.md`：S slices、D、MCOLS=8、ACT_ROWS、16×32-bit 寄存器（R0=0、R8-R15=ARG0-7）、顺序机、无 cache/无隐藏调度、参数化测试矩阵。
  - `concepts/02-isa.md`：指令字 8×32-bit、指令全集与 opcode（NOP/HALT+CHAIN/LI/ADDI/LOOP 深度4/BAR/LD/ST/DSTEP/STREAM/MM/QACT/QST/VOP/GATHER 等以计数为准）、编码字段、isa.py 与 isa.md 双源。
  - `concepts/03-dma-memory.md`：RLD/WAITW、显式 DMA、scoreboard 窗口（WIN=32）、TMEM LANES=16 banks、两层 MM 存储层次、ACT RAM、native_dram。
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `rule` TR-7.1: 每篇 ≤7 篇批次约束；所有 opcode/寄存器名 Grep 命中 F 编号；数量与 Task 2 计数表一致。
  - `rule` TR-7.2: 每篇含 frontmatter（type: Concept）、正文信源 pinned URL、结尾「相关概念」`/`-链接。
  - `rubric` TR-7.3: 教学有效性（AC-7 维度），threshold ≥4，evidence：篇章内 matmul 路线兑现点标注。

## Task 8: E-2 concepts 批次 B：04-07（MXU/权重量化/VPU 数值/激活量化）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - `concepts/04-mxu-matmul.md`：四列脉动阵列、DSP48E1、MM 指令、整数累加 <2^47、fp32 epilogue、一次 matmul 在硬件中的生命周期（贯穿示例核心章）。
  - `concepts/05-weight-formats.md`：int8/int4/E2M1(FP4)/NVFP4 两级块缩放、4.25 bits/weight、PAIR 列复用、LM head 保 int8。
  - `concepts/06-vpu-fp32-contract.md`：VPU 21 func、roundTiesToEven+FTZ+canonical NaN(0x7FC00000)、非完整 IEEE 754 声明、exp2(7阶)/recip/rsqrt/log2 ulp 指标与固定 add/mul 序列、fp32.py↔isasim.py↔otpu_fp.sv 三处逐位一致组织。
  - `concepts/07-quantization.md`：QACT/QST、行缩放 Sa、每 D/4 子块偏移 da、RMAX/ASCALE 的 flash-attention 修正、饱和 q8[-127,127]。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-7
- **Test Requirements**:
  - `rule` TR-8.1: ulp 指标、累加上界、块尺寸等数字与 facts.md 完全一致（逐数比对清单）。
  - `rule` TR-8.2: VOP func 列表名与计数来自 Task 2，不照抄周报数字。

## Task 9: E-3 concepts 批次 C：08-11（ol/编译器/模拟器/RTL）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - `concepts/08-ol-kernel-language.md`：@ol.jit、ol 原语全集（load/dot/… 以 Grep 登记为准）、kernels/ 六个模块如何用 ol 写 attention/mlp/deltanet。
  - `concepts/09-compiler.md`：布局即 API、仿射循环寻址、算子融合、编译产物（ISA 程序）、compiler.py 阶段划分。
  - `concepts/10-isasim.md`：位精确模拟器结构（Machine/Config）、与 fp32.py/quant.py 的契约、rtlsim.py Verilator 桥、模拟器作为 golden 的角色。
  - `concepts/11-rtl.md`：otpu_top/slice/pkg/coll、mxu、vpu（se_comp/tail/fpipe/vtree）、seq、dma、mem、shell、tech（generic/xilinx7/xilinxus/asic）映射；参数化 S/D 的实现方式。
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `rule` TR-9.1: ol 原语与类名 100% Grep 命中（TR-3.2 清单交叉勾销）。
  - `rule` TR-9.2: RTL 模块名与文件路径一一对应（otpu_*.sv 映射表）。

## Task 10: E-4 concepts 批次 D：12-16（验证/板卡/性能/多目标/方法论）

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - `concepts/12-validation.md`：validate.py 四行对照语义、通过判据、--against 位级模式、scoreboard WIN=32、pytest 三层（非 rtl / Verilator / 板卡）、8eaa4806 修复反例方法论。
  - `concepts/13-board-host.md`：ypcb-00338 规格与 bring-up、host/board+offload、otpu-chat/otpu-smi/otpu-diag、PCIe、resident decode。
  - `concepts/14-performance-models.md`：device/wall 口径（512 prompt+64 greedy、argmax 归属）、README 18 配置结果表导读（作者报告口径）、DRAM 82-94%、Lens roofline/时间线、llm/ 10 模型适配、MoE offload（专家流入非常驻、153MB/token 等以原文为准）、otpu-serve（api/batching/scheduler）。
  - `concepts/15-targets-asic.md`：targets/*.toml + target.py 单加载器、ypcb-00338/bcu1525(VU9P,4×DDR4)/nangate45/nangate45-small、D1-D4 多目标决策、OpenROAD 流程与 PPA 文档口径。
  - `concepts/16-agent-designed-hardware-method.md`：AI agent 设计硬件的工程方法迁移（四元组行动项）：契约先行、对拍金字塔、修复配反例、限制自由度换可验证性、归属分离与证据边界；触发条件/步骤/反模式/不适用边界。
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-10.1: 性能表数字逐项可回指 README ffe997e 行号；18 配置/10 模型与计数一致。
  - `rule` TR-10.2: concept 16 每条方法含「适用边界/反模式」小节。
  - `rubric` TR-10.3: 教学有效性 AC-7 threshold ≥4。

## Task 11: E-5 examples 3 篇 + 全部 index/log 收尾

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - `examples/00-isasim-walkthrough.md`：pip install -e . + 模拟器 chat/最小内核的源码级走读（命令标注「本次未执行」，给预期输出的出处行号而非杜撰输出）。
  - `examples/01-matmul-six-layers.md`：跟一次 matmul：ol 写法→编译后 ISA→isasim 执行→RTL 模块→（板卡路径说明），六层片段全部引自真实 blob。
  - `examples/02-validate-output.md`：validate.py 四行对照输出解读（以 README/脚本 help 与 docs 为证据，给字段含义表）。
  - 最后统一写 index（永远最后）：BUNDLE 根 index.md（okf_version+type:bundle、人类可读分区列表、隐藏 toctree）、concepts/index.md、examples/index.md、references/index.md（无 frontmatter、含 toctree + 人类列表）、log.md（生成日志：批次、时间、命令、计数勘误记录）。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-11.1: examples 中每条命令在 ffe997e 存在对应入口（setup/Makefile/tools 脚本 Grep 命中）；无伪造运行输出。
  - `rule` TR-11.2: 4 个 index 中 toctree stem 与同目录文件名一一对应（含根 index 收录三个子目录 index）。
  - `rubric` TR-11.3: examples 可跟做性（AC-7 维度）threshold ≥4。

## Task 12: 三级索引计数面更新

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 更新 `jishu/iot/index.md`：源码教程表新增 opentpu 行 + toctree 增加 opentpu/index（先读现状确定列格式与排序位置）。
  - 更新 `jishu/index.md`：IoT 束计数 7→8（先核当前实际数）。
  - 更新 `doc/bundles/index.md`：total_bundles 617→618、jishu 域束数 +1、IoT 描述行（以当前磁盘实际数值为准，先脚本核对再改）。
  - 与 embedded-weekly-03 概念页建立交叉链接（在其束外链方向：仅新束指向概念页；如概念页适合回链，仅在不违反 N2 时——默认不改概念页，改为在 iot/index 表注中体现关系）。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-12.1: `python scripts/check-bundles-index.py` rc=0；`python scripts/check-toctrees.py` rc=0（cwd=子项目根），输出留存。
  - `rule` TR-12.2: 计数三角（总索引/域索引/组索引）三处数值一致，改动前后数值均有命令输出佐证。

## Task 13: V 阶段 全量验证与回填

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - G1 结构/frontmatter：全文件清单、type 分布、index 规则、toctree 校验。
  - G2 零虚构：汇总全部正文符号清单（文件名/类/函数/指令/opcode/CLI），对 ffe997e 逐一 Grep；未命中项修复后复验。
  - G3 计数复核：对 Task 2 计数表用独立命令（换 pattern/换工具，如 git grep 与 Select-String 互换）复核，原始数/去重数双列。
  - G4 链接：束内 `/`-链接与跨束链接逐目标存在性检查；UTF-8/编码检查（check-utf8 若存在）。
  - G5 构建：`invoke gates.toctrees`/`gates.bundles`（或直接 python scripts/…）+ 变更文件 dummy Sphinx 构建（`sphinx-build -b dummy` 定向）；缺依赖记 blocked 证据。
  - 回填 references/verification.md（G1-G5 证据、遗留问题、F-053~F-072 对账复核），同步 log.md 勘误记录。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-13.1: verification.md 含每项 G 门的命令+输出摘要+结论；符号核验表 0 未命中。
  - `rule` TR-13.2: dummy 构建 0 error；若环境 blocked，明确 blocker 与恢复条件，不以其他证据冒充。
  - `rule` TR-13.3: 路径纪律扫描（file:///、external/dao、绝对路径、.tmp）束内 0 命中。

## Task 14: C 阶段 fresh-context 独立评审与收口

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 委派一次 fresh-context general_purpose_task 只读评审：给其 spec.md/tasks.md 与 BUNDLE 路径、固定 hash、验证命令；按 AC-1~AC-8 逐项独立取证（含抽查 10+ 符号自行 Grep、抽查 5 个数量自行计数、20 条对账表完整性、链接与 toctree、rubric 双维打分）。
  - 评审结果写 `.trae/specs/opentpu-okf-wiki/review.md`（仅此时创建）；actionable 发现按 Issue 模板回 Implement 修复并复验，至 pass。
  - pass 后向用户汇报：文件清单、门禁输出、证据边界、未提交提示（不主动 commit）。
- **Acceptance Criteria Addressed**: AC-1~AC-8（全覆盖）
- **Test Requirements**:
  - `rule` TR-14.1: review.md 中每个 AC 有独立检查点与证据；actionable 发现清零才允许 pass。
  - `rubric` TR-14.2: AC-7/AC-8 两维独立评分均 ≥4 并引用篇章。
