---
name: collect-api-decouple-cmd
version: 1.0.0
description: "当用户要求把'硬件/设备采集（推理、板端执行、远端拉取）与本地解析/后处理'拆开、让昂贵采集步骤变成可选、复用已有日志/产物重新计算（'可能已经推理过了'、'跳过设备执行'、'重放日志'）时，必须使用此技能。封装副作用边界切分、dataclass 阶段契约、run_<step> 复用开关贯通、以及复用分支对清理型工厂（rmtree/unlink）的规避清单。"
argument-hint: "<目标采集函数：文件#L起-止>"
user-invocable: true
paths:
  - "external/chaos/npuusertools/xmnn/infer_api.py"
  - "external/chaos/npuusertools/xmnn/performance_api.py"
title: "采集-解析分离与日志复用改造 Skill"
---

# 采集-解析分离与日志复用改造 Skill

> 本 Skill 是场景3（重构优化）的特化执行卡，方法论底座为 seven-concepts-cmd 的
> I→F→A→V 链路。遇到本卡覆盖的诉求时直接执行，不必重新推导切分原则。

## 1. Skill ID
`collect-api-decouple-cmd`

## 2. 适用判定（何时触发）

目标函数同时满足以下特征中的多数时触发：

- 函数体内既有**昂贵采集动作**（设备推理、Telnet/SSH 执行、远端下载、仿真运行），
  又有**本地确定性处理**（日志解析、指标聚合、TOML/Excel 组装）。
- 用户表达："推理和后处理分开"、"采集/推理变成可选的"、"已经跑过了，直接复用日志"、
  "跳过设备执行/重放"、"改了算法后只重新算指标"。
- 同一次采集的产物会被多组参数重复消费（典型：一份硬件耗时 × N 个带宽占比档位）。

**不适用**：纯本地数据处理函数（无外部副作用）；采集与解析无法共享同一份产物的场景；
实时性要求每次必须重新采集的在线链路（此时只能做结构分离，不能加复用开关）。

## 3. 核心原则（公理，不可协商）

1. **副作用边界即函数边界**：触网/触设备/写盘的动作收敛进"采集原子"；只读本地文件
   与纯计算收敛进"解析/后处理原子"。判断方法——函数能不能在断网、无设备环境下重复执行
   且输出逐位一致：能的是后处理，不能的是采集。
   > **为什么？** 复用的本质是"用历史产物重放确定性计算"。只要边界上残留一个写/删/触网
   > 动作，重放就不再幂等，"跳过采集"会悄悄污染它本该复用的产物。
2. **阶段间只用显式契约传参**：用 `@dataclass` 承载跨阶段产物（路径 + 原始解析结果），
   禁止用模块级全局变量或隐式文件约定衔接。dataclass 字段宁多勿少——持有未被下游消费的
   产物（如 memory 指标）成本为零，但未来扩展复用不需要重跑采集。
   > **为什么？** 全局变量与隐式文件约定在"同进程一次采集"时无害，但复用/多次重放场景
   > 下会产生跨次状态污染；显式契约让每次后处理的输入都可被独立构造与测试。
3. **复用开关默认走旧行为**：开关命名为正向 `run_<expensive_step>=True`（禁止反向
   `skip_xxx=False` 的双重否定）；所有既有调用方零改动即保持原时序。
   > **为什么？** 开关要贯通 3-5 层，双重否定在某一层被写成 `not skip` 的概率随层数
   > 指数上升；正向开关每一层的语义都与字面一致。
4. **复用分支零磁盘破坏**：跳过采集时，禁止调用任何带清理语义的工厂/初始化函数
   （会 `rmtree` 目录、`unlink` 文件、清空输出目录的函数）；路径一律纯推导
   （字段读取 + Path 运算）。
5. **复用必须有产物校验兜底**：跳过采集不等于跳过检查——日志/产物不存在时仍由解析层
   抛原有 `FileNotFoundError`（含排障信息），禁止静默产出空结果或零值指标。
   > **为什么？** 静默产出空/零结果会把"没有日志"伪装成"模型性能为零"，错误延迟到
   > 报告阶段才暴露，排障路径被彻底遮蔽。
6. **缩放参数一致性显式警示**：均值/归一化类参数（如 `sample_nums`）在复用时若与实际
   采集时不一致，会静默产生错误缩放的指标。必须在 docstring 中显式警示，不做自动探测
   （无法从日志可靠反推时宁可只警示）。

## 4. 标准执行步骤（A 阶段模板）

### 步骤 0：I 事实采集（改之前必查）

- [ ] grep 全部调用方，记录每个调用点的位置参数/关键字参数用法（签名必须兼容）。
- [ ] 逐行标注目标函数每一段的副作用类型：设备执行 / 写文件 / 删文件 / 只读 / 纯计算。
- [ ] 找出所有被调用的**路径工厂与对象构造器**，逐个确认其内部是否有清理副作用
      （重点查 `__post_init__`、`__call__`、`ensure/mkdir/rmtree/unlink`）。
- [ ] 确认装饰器是否 `*args, **kwargs` 透传（决定开关能否穿过 task wrapper 层）。
- [ ] 确认 CLI/任务注册表是否有参数白名单（白名单外的新参数走默认值，CLI 接口属
      L2 变更，本改造不动 CLI）。

### 步骤 1：F 切分设计

- 采集原子：`_run_<domain>_collection(...) -> <Result>`，返回 dataclass，包含
  产物目录与全部原始解析结果。
- 解析原子：`_parse_<domain>_logs(config, compile_dir, ...)`，保留全部既有存在性
  校验与错误文案。
- 组装原子（可选，函数较长时）：`_build_<domain>_toml(compile_dir, logs, ...)`，
  纯计算，返回最终结构。
- 原公开函数退化为 3-5 行薄编排，签名仅在尾部追加 `run_<step>=True`。

### 步骤 2：A 贯通开关（由内向外逐层）

```
底层采集原语（bandwidth/costtime/...）
  → 领域聚合阶段（_run_<domain>_collection）
  → 公开编排函数（xmnn_<domain>）
  → task wrapper 层（<domain>_task）
  → 用户入口（<domain>_xmnn 等）
```

每层同一开关名、同一默认值、同一语义；只在最底层真正分叉执行路径，上层只做透传。
跳过分支的 compile_dir 等路径从 config 确定性推导，不要求调用方新传路径参数。

### 步骤 3：代码骨架

```python
@dataclass
class CollectResult:
    """采集与后处理之间的显式数据契约。"""
    work_dir: Path
    raw_metrics: dict
    # 宁多勿少：下游暂不消费的产物也保留


def _run_collection(config, ..., run_collection=True):
    work_dir = config.env.dst_model_dir / task_name
    if run_collection:
        ensure_dir(work_dir)
        io_dirs = config.env(work_dir, group="")   # 清理型工厂只允许在采集分支调用
        run_on_device(...)
    else:
        io_dirs = _pure_path_derivation(config.env) # 纯路径推导，零磁盘触碰
    logs = _parse_logs(config, work_dir, io_dirs)   # 两种模式共用，内部做存在性校验
    return CollectResult(work_dir=work_dir, raw_metrics=logs)
```

纯路径推导复刻工厂的路径规则（绝对路径取 basename、相对路径原样），但删除其中一切
mkdir/rmtree 调用，并在代码处留注释说明为何不能调用原工厂。

## 5. V 对抗审查与安全检查清单（改造后逐项核对）

- [ ] **默认等价**：`run_<step>=True`（含不传该参）路径与改造前逐行等价：执行顺序、
      日志输出顺序、异常类型与异常文案、异常抛出时机（例如某校验必须在输入生成之后
      抛出，就不得提前到函数入口）。
- [ ] **复用安全**：`run_<step>=False` 全路径无 rmtree/unlink/设备连接/输入重生成；
      待复用的产物目录不可能被本函数自身删除。
- [ ] **缺失产物行为**：删除/改名产物文件后走复用分支，确认抛出与采集分支同源的
      FileNotFoundError 且排障信息完整。
- [ ] **CWD 相对路径**：检查清理型工厂是否按 CWD 相对路径删除（复用模式下 CWD 可能
      不同）；纯推导分支不得继承这一行为。
- [ ] **1:N 场景**：一次采集、N 组后处理参数时，确认采集只发生一次，循环只包后处理。
- [ ] **静态门禁**：`python -m py_compile` 与 IDE 诊断零问题；grep 确认无调用方依赖
      被删的局部变量或旧返回结构。
- [ ] **审批级别**：核心库内部重构属 L1；CLI 参数/对外命令变更属 L2，本改造默认不触及。
- [ ] 硬件链路无法本地实跑时，在交付说明中明确"待板端回归"，不得宣称已验证产物数值。

## 6. 反模式（来自实战教训）

1. **先撕账本再查账**：复用分支仍调用会清空 outputs 目录的环境工厂，待复用日志正在
   被删目录中——功能看似正常，实际在 True/False 两条路径上行为相反。
2. **开关双重否定**：`skip_inference=False` 与 `not skip` 组合，贯通四层后语义必然
   在某一层写反。一律正向 `run_<step>=True`。
3. **跳过后静默成功**：产物缺失时返回空 dict 或全零指标，错误延迟到报告生成阶段才
   暴露，排障成本倍增。
4. **顺手改异常时序**：重构时把 target 拦截、目录创建等"提前"到入口，破坏了原有
   "先生成输入再报错"的副作用契约（调用方可能依赖中间产物已落盘）。
5. **每层各自推导 compile_dir**：开关在多个层级分别用不同表达式推导路径，造成分叉。
   路径只在最底层推导一次，上层透传结果。
6. **给 CLI 同步加开关**：未经 L2 审批扩展命令行参数与任务白名单，扩大变更面。
   Python API 可先行，CLI 单独走审批。
7. **缩放参数静默错配**：复用时 `sample_nums` 默认值与实际采集轮数不同，均值指标
   全部偏差却无任何告警。

## 7. Gotchas（无报错的隐性陷阱）

这些陷阱不会抛异常，程序"正常结束"但结果或环境已被破坏：

- **环境工厂自带清理**：名为 `env()`/`prepare()`/`__post_init__` 的函数看似只做初始化，
  实际内含 rmtree/unlink。判断依据是读源码而非函数名；复用分支必须审计所有间接调用
  （包括 dataclass 构造器内部）。
- **CWD 相对删除**：清理逻辑按相对路径（如 `outputs/`）删除，换个 CWD 跑复用模式时
  可能删到无关目录；纯推导路径不继承此行为，但也要警惕把相对路径直接传给下游。
- **构造器即副作用**：某些对象（如执行器/Evaluate）在 `__post_init__` 中删除并重新
  拷贝可执行文件。"只 new 了一个对象，还没执行"并不等于无副作用。
- **均值参数默认值陷阱**：函数签名上 `sample_nums=10` 的默认值与历史采集轮数无关；
  复用分支不会因为"用了默认值"而自动正确。
- **装饰器提前建目录**：task wrapper 常在调用业务函数前 ensure_dir/初始化日志，
  这不会删除产物但会改变"目录是否存在"的前提；分析副作用时要把装饰器层算进去。
- **1:N 循环位置**：开关放错层级会导致"每档都重新采集一次"——循环只能包后处理，
  采集必须在循环外且只执行一次。

## 8. 参考案例（本工作区实证）

- [infer_api.py](../../../external/chaos/npuusertools/xmnn/infer_api.py)：
  `inference_xmnn_dump_costtime` 拆为 `_run_costtime_inference`（设备两次采集）→
  `_parse_costtime_logs`（存在性校验+解析）→ `_build_costtime_toml`（纯计算），
  契约为 `CosttimeLogData`；`inference_xmnn_dump_bandwidth` 对称加开关。
  关键坑：`Evaluate.__post_init__` 会 unlink 旧可执行文件并重新拷贝——它只允许出现在
  采集分支。
- [performance_api.py](../../../external/chaos/npuusertools/xmnn/performance_api.py)：
  外层 `xmnn_performance` 实现"采集一次 × N 档后处理"；`run_inference` 由
  `performance_xmnn → performance_task → xmnn_performance → _run_performance_inference`
  五层透传。
  关键坑：`Env.__call__` 会 `shutil.rmtree` 已有 inputs/outputs 目录，复用分支改为
  复刻其纯路径推导逻辑，严禁调用原工厂。

## 9. 与其他 Skill 的边界

- 需要完整重构决策树/质量门记录/沉淀模式时，上层用 seven-concepts-cmd（场景3），
  本卡是其在"采集类 API"领域的执行特化。
- 纯文档/目录拆分用 atomization-cmd；提交环节用 atomic-commit-cmd。
