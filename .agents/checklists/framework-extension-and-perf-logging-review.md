---
id: "framework-extension-and-perf-logging-review"
title: "框架扩展与性能日志代码审查清单"
source: "retrospective/2026-07-31-caffe-ffi-backward-logging-milestone-retro.md"
related_patterns:
  - progressive-interface-extension
  - single-pass-perf-instrumentation
  - monorepo-ci-blindspot-detection
x-toml-ref: "../../.meta/toml/.agents/checklists/framework-extension-and-perf-logging-review.toml"
maturity: "L1"
date: "2026-07-31"
---

# 框架扩展与性能日志代码审查清单

> 📅 创建日期：2026-07-31
> 🎯 用途：审查基类接口变更、算子性能日志埋点、Monorepo CI配置时快速对照
> 📂 关联模式：[框架接口渐进式扩展](../docs/retrospective/patterns/code-patterns/progressive-interface-extension.md) | [单次遍历性能统计日志埋点](../docs/retrospective/patterns/code-patterns/single-pass-perf-instrumentation.md) | [Monorepo子项目CI盲区检测](../docs/retrospective/patterns/process-patterns/monorepo-ci-blindspot-detection.md)

---

## 一、使用说明

当PR/Diff涉及以下场景时，使用本清单逐项审查：

| 场景 | 适用章节 |
|------|---------|
| 基类/框架接口添加新虚方法，影响多个子类 | §二 接口扩展检查 |
| 新增/修改计算层/算子的性能日志埋点 | §三 性能日志检查 |
| Monorepo中子项目CI配置变更/新增子项目 | §四 CI覆盖检查 |

---

## 二、框架接口渐进式扩展检查

> 适用：在基类添加新虚方法，影响N≥3个子类时

### 2.1 扩展策略检查

- [ ] **影响范围已评估**：已统计受影响的子类数量；<3个直接实现，≥3个用渐进式策略
- [ ] **非纯虚默认实现**：新方法**不是**纯虚（`=0`），提供有意义的默认实现
- [ ] **默认实现安全**：默认实现要么输出WARN日志（"Backward_cpu not implemented for XxxLayer"），要么THROW明确异常，**不是**空函数`{}`
- [ ] **调用路径已确认**：如果上层调用路径（如编排方法Net::Backward）尚未实现/启用，默认实现用WARN（不阻断）；调用路径已激活时默认实现用THROW

### 2.2 分批实现检查

- [ ] **优先级已划分**：子类按P0（核心路径立即实现）/P1（常用层近期实现）/P2（边缘层按需实现）分级
- [ ] **原子提交**：每批次实现独立commit，每个commit < 200行diff
- [ ] **无桩代码残留**：P0批次已实现真实逻辑，没有"为了通过编译写return;"或空函数体残留
- [ ] **任务已登记**：P1/P2实现任务已在Issue/Backlog中登记，不会遗忘

### 2.3 反模式排查（Red Flags 🚩）

| 反模式 | 检查方式 | 正确做法 |
|--------|---------|---------|
| 🚩 新方法直接`=0`纯虚 | 看基类声明是否有`=0` | 先用默认WARN/THROW，分批实现 |
| 🚩 默认实现是空函数`{}` | 看默认方法体是否为空 | 必须输出WARN或THROW |
| 🚩 一次性修改所有子类 | 看单次commit修改文件数 | 分批提交，每批≤3个子类 |
| 🚩 为通过编译写空桩 | 看新增方法体是否无实际逻辑 | 核心层必须真实实现 |

---

## 三、性能统计日志埋点检查

> 适用：为计算层/算子添加Forward/Backward性能监控日志时

### 3.1 基础原则检查（所有层通用）

- [ ] **单次遍历融合**：计算+min/max统计+条件计数在同一个for循环内完成（逐元素激活层）
- [ ] **栈上变量**：in_min/in_max/out_min/out_max/计数器是栈上局部变量，无`static`、无类成员变量
- [ ] **极值正确初始化**：`min = std::numeric_limits<float>::max()`，`max = -std::numeric_limits<float>::max()`，计数器`= 0`
- [ ] **耗时用double**：elapsed_us用`double`存储，不是`float`（避免大数截断）
- [ ] **循环外日志**：`CAFFE_FFI_LOG_INFO()`在循环外部调用，不在for/while内
- [ ] **循环外计时**：`t_start`在循环前，`t_end`在循环后；chrono使用`high_resolution_clock`
- [ ] **零堆分配**：循环内无`new`、无`std::vector`临时构造、无可能分配内存的函数调用

### 3.2 日志格式检查

- [ ] **统一标签**：使用`[CATEGORY-PERF]`格式标签（如`[ACTIVATION-PERF]`、`[CONV-PERF]`、`[SPLIT-PERF]`、`[LOSS-PERF]`）
- [ ] **字段顺序**：标签 → 层实例名（`this->name()`）→ 层类型（type()）→ 方向（forward/backward）→ count=N → 参数k=v → 值域 → 特有指标 → time=Xus
- [ ] **值域格式**：`in=[min, max]`、`out=[min, max]`、梯度用`diff_in=[min, max]`、`diff_out=[min, max]`
- [ ] **k=v格式**：参数和特有指标使用`key=value`，不用空格分隔，便于grep/awk解析
- [ ] **耗时单位**：时间字段以`us`结尾（微秒）

### 3.3 层特有指标检查

| 层类型 | 特有诊断指标 | 检查项 |
|--------|------------|--------|
| ReLU | `dead=N/M (ratio)` | 统计`x <= 0`元素数，检测死亡ReLU |
| Sigmoid/TanH | `saturate=N/M (ratio)` | 统计饱和区元素数，预警梯度消失 |
| PReLU | `slope=[min,max]`, `channel_shared=true/false` | 统计slope值域，检测参数退化 |
| ELU | `alpha=value` | 记录超参数 |
| Dropout | `zero_mask=N/M (ratio)` | 验证实际dropout率 |
| BatchNorm | `mean=[min,max]`, `var=[min,max]` | 检测分布偏移 |
| Conv/FC/InnerProduct | `w_norm=value`, `w_diff_norm=value`, `b_diff=[min,max]` | 检测梯度爆炸/消失 |
| Split | `ZEROCOPY memcpy_saved=N` | 验证零拷贝优化效果 |
| Pooling | `pooled=N/M (ratio)` | 统计有效池化区域 |

- [ ] **至少1个特有指标**：每层除通用in/out/time外，至少有1个层特有诊断指标
- [ ] **指标有诊断意义**：特有指标能预警常见训练问题（死亡ReLU、梯度消失/爆炸、分布偏移等）

### 3.4 多阶段算子检查（Conv/FC/GEMM类，非逐元素层）

> 卷积/全连接层的核心计算是im2col+GEMM（BLAS库黑盒），无法在GEMM内部插入统计代码。使用阶段级计时+输出后独立reduce策略。

- [ ] **端到端总计时**：t_start包住所有阶段（im2col+gemm+bias+col2im），t_end在最后
- [ ] **子阶段分计时（可选但推荐）**：im2col/gemm_data/gemm_filter/gemm_bias分别计时，便于定位瓶颈
- [ ] **GEMM后独立reduce**：GEMM输出后对输出数组做独立O(N) min/max遍历（纯读操作，开销<1%可接受）
- [ ] **跨batch聚合**：多batch（num维度）使用running min/max，不在每个batch内重置统计变量
- [ ] **weight_diff/bias_diff独立统计**：权重梯度和偏置梯度在backward_filter/backward_bias完成后统计
- [ ] **不统计中间缓冲区**：col_buffer/col_diff_buff等临时缓冲区不做统计（生命周期短、无诊断价值）
- [ ] **范数计算可选**：w_diff_norm/b_diff_norm用Welford或独立循环计算，用于梯度爆炸/消失诊断
- [ ] **禁止试图在BLAS GEMM内部插入统计**：GEMM由OpenBLAS/MKL/BLIS实现，是黑盒优化，不要hack进去

### 3.5 反模式排查（Red Flags 🚩）

| 反模式 | 危害 | 检查方式 |
|--------|------|---------|
| 🚩 先计算再二次遍历统计 | cache miss翻倍，大数组性能降40-50% | 看是否有两个for循环遍历同一数组 |
| 🚩 循环内调用LOG/CAFFE_FFI_LOG | 日志锁导致严重串行化，输出爆炸 | grep循环体内是否有LOG/PRINT |
| 🚩 min初始化为0或未初始化 | 统计结果错误（全负输入时min永远为0）；未初始化是UB | 看极值变量初始化值 |
| 🚩 统计变量声明为static/类成员 | 多线程数据竞争；跨调用污染 | grep `static float.*min` / 成员变量声明 |
| 🚩 循环内堆分配 | 每次调用分配/释放内存开销大，异常不安全 | grep循环内`new`/`vector<>` |
| 🚩 耗时用float存储 | 大耗时值精度丢失 | 看elapsed_us类型是否为double |
| 🚩 日志无统一TAG标签 | 无法grep提取性能数据 | grep日志字符串是否有`[XXX-PERF]`格式 |
| 🚩 循环内if(log_enabled)判断 | 多余分支（日志宏已有编译期门控） | grep循环内日志级别判断 |

### 3.6 Python端验证检查

- [ ] 有pytest测试验证性能日志存在性（使用ptrace/capsys捕获日志输出）
- [ ] 测试断言`[TAG-PERF]`标签、`in=`、`out=`、`time=`字段存在
- [ ] 至少一个测试通过已知输入验证统计值的数值正确性（如输入全0/全1时min=max=0/1）

---

## 四、Monorepo CI覆盖检查

> 适用：新增子项目/修改CI配置/怀疑测试未被覆盖时

### 4.1 配置审计

- [ ] **根pytest配置已检查**：根pyproject.toml/pytest.ini的`testpaths`明确列出了哪些目录
- [ ] **子项目独立配置已检查**：每个子项目是否有独立pyproject.toml配置自己的testpaths
- [ ] **testpaths范围确认**：确认根testpaths是否递归发现子项目（默认不递归！）
- [ ] **构建vs测试分离**：构建命令（build/make/cmake --build）只编译不测试；测试命令独立

### 4.2 collect-only计数验证

- [ ] **根目录collect-only计数已记录**：`pytest --collect-only -q`统计根CI能发现的测试数
- [ ] **子项目collect-only计数已记录**：在每个子项目目录分别运行`pytest --collect-only -q`
- [ ] **计数对比完成**：子项目测试数之和是否≈根收集数？差距>10%说明有盲区
- [ ] **CI日志验证**：查看最近CI运行日志，确认子项目测试确实在运行（不是只跑根3个测试）

### 4.3 修复方案选择（根据子项目特点）

| 子项目类型 | 推荐方案 | 原因 |
|-----------|---------|------|
| 轻量Python子项目（无C++编译） | 统一递归配置（pytest --recursive或配置testpaths包含所有子目录） | 测试快，不拖慢主CI |
| 含C++/CUDA编译的重子项目 | 独立CI（独立GitHub Actions workflow） | 编译耗时，不拖慢主CI反馈 |
| 中等耗时子项目 | 路径过滤条件步骤（changes: paths: 子项目目录/**） | 只在相关代码变更时运行 |
| 多个子项目需统一入口 | 新增统一测试命令（如`xs test`） | 开发者可以一键跑所有测试 |

- [ ] **方案已匹配子项目特点**：不是无脑所有子项目都塞主CI
- [ ] **红灯测试已做**：故意破坏一个子项目测试，验证CI能捕获失败
- [ ] **绿灯测试已做**：恢复破坏后CI恢复绿灯
- [ ] **文档已更新**：README/贡献指南说明CI覆盖策略

### 4.4 反模式排查（Red Flags 🚩）

| 反模式 | 危害 | 验证方式 |
|--------|------|---------|
| 🚩 "pytest会递归发现"的假设 | 子项目测试永远不跑，绿灯无意义 | 跑collect-only对比计数 |
| 🚩 主CI无条件跑所有测试 | C++编译30分钟+，开发者绕过CI | 看CI耗时和触发条件 |
| 🚩 build命令里隐含测试 | 职责不清，构建失败和测试失败混淆 | 看build脚本是否调用pytest |
| 🚩 只看CI绿灯不看跑了什么 | 测试可能几个月没跑，回归bug堆积 | 定期审CI日志中的测试计数 |
| 🚩 新增子项目后忘记配CI | 子项目代码无测试保护 | 新增子项目检查清单包含CI配置 |

---

## 五、审查通过标准

全部检查项中：
- **🚩 Red Flag反模式**：0个（必须全部排除）
- **必须项**（无"可选"标记）：全部通过
- **可选项**（标记"可选"/"推荐"）：≥80%通过
- **Python验证测试**：必须有

审查者在PR评论中引用本清单，标注未通过项编号和具体问题。

---

## 六、快速速查卡（打印贴屏版）

```
┌─────────────────────────────────────────────────────────────┐
│  框架扩展 & 性能日志 CR 速查                                │
├─────────────────────────────────────────────────────────────┤
│  □ 接口扩展：新虚方法非纯虚? 默认有WARN/THROW? 分批提交?    │
│  □ 性能日志：单次遍历? 栈上变量? min=float_max?            │
│  □ 性能日志：[TAG-PERF]标签? 循环外输出? double耗时?       │
│  □ 卷积层：阶段计时+GEMM后reduce? 跨batch running min/max? │
│  □ CI覆盖：collect-only计数对比? 子项目CI方案匹配?         │
│  🚩 排除：纯虚=0/空函数{} / 二次遍历 / 循环内LOG / min=0  │
└─────────────────────────────────────────────────────────────┘
```
