# agent-monetize

**Python 3.14+ 智能体自动变现平台** —— 自主循环 + 道家门控 + 沙箱通道 + tvm-ffi 桥接。

本项目是一个 **沙箱虚拟货币演示**：不接入任何真实资金流转。智能体在闭环内自动完成
「机会发现 → 决策 → 行动 → 反馈进化」，以道家「无为 / 知止」为治理门控，
以红绿区为合规边界，以 tvm-ffi 为高性能打分后端（原生不可用时优雅降级到纯 Python 参考实现）。

## 核心特性

| 特性 | 说明 |
|---|---|
| 🔁 自主循环 | `observe → decide → act → learn` 四步闭环，支持定时/事件驱动与 JSON 状态持久化 |
| 🧘 道家门控 | **无为门**（确定性/预期收益低于阈值 → 待时而动）+ **知止门**（单通道收益上限 + 总亏损红线） |
| 🧪 沙箱通道 | 内容计价（按阅读/采纳计价）、数据服务（按调用量/阶梯折扣）——虚拟货币，不接真实资金 |
| ⚡ tvm-ffi 桥接 | 原生 C++ FFI 打分优先，纯 Python 参考实现优雅降级（双路径） |
| 🚦 红绿区合规 | 红区禁行清单（欺诈/垃圾/诱导点击…）硬拦截；真实通道需用户显式确认才启用 |
| 🧬 自进化 | 基于反馈（净收益/转化）以指数加权 + 软最大更新各通道权重，影响下一轮决策 |

## 快速开始

### 环境

- Python 3.14+（推荐 conda 环境 `py314`）
- 依赖：`PyYAML`（运行）；`pytest`、`ruff`（开发）

```bash
cd apps/agent-monetize
# 开发安装（可选，`python -m agent_monetize` 已内置 src/ 自举路径）
pip install -e ".[dev]"
```

### 运行沙箱演示

```bash
# 方式一：模块入口（零安装，仓库内直接可跑）
python -m agent_monetize demo

# 方式二：CLI 脚本（安装后）
agent-monetize demo

# 常用参数
python -m agent_monetize --rounds 20 demo    # 覆盖循环轮数
python -m agent_monetize --help              # 查看用法
```

演示输出示例：

```
FFI 后端：native（tvm_ffi 可用=True）
通道：content_pricing, data_service
[round  1] 待时 -> (no-op)  [wuyou] 机会确定性 0.52 低于阈值 0.55，待时而动（无为）
[round  3] 行动 -> data_service     score=5.602 net=+11.13 balance=45.49
...
--- 最终收益（沙箱虚拟货币） ---
总收入   : 45.90
净收益   : 45.49
```

### 运行测试

```bash
pytest                                    # 全量测试
pytest --cov --cov-report=term-missing    # 覆盖率（门禁 ≥ 80%）
ruff check src tests                      # 静态检查
ruff format --check src tests             # 格式检查
```

当前状态：**81 用例全绿，覆盖率 89.6%**。

### 编译原生 FFI 模块（可选）

原生模块缺失时 demo 自动降级到纯 Python 参考实现（backend=reference）。若本机有
MSVC + Windows SDK，可编译启用原生打分（backend=native）：

```powershell
pwsh -NoProfile -File native/build.ps1
# 产物：native/build/score_opportunity.dll（被 core/ffi_bridge.py 自动加载）
```

## 项目结构

```
apps/agent-monetize/
├── config.yaml                  # 沙箱配置（轮数/门控阈值/合规确认/通道参数/FFI）
├── pyproject.toml               # 包配置 + ruff/pytest/coverage 门禁
├── native/
│   ├── score_opportunity.cc     # C++ FFI 模块（tvm-ffi 注册 score_opportunity 等）
│   └── build.ps1                # MSVC 编译脚本（自动定位 MSVC/SDK/tvm_ffi）
├── src/agent_monetize/
│   ├── models.py                # 数据模型（Signal/Opportunity/Decision/Feedback…）
│   ├── config.py                # YAML → dataclass 配置加载
│   ├── tao/gates.py             # 道家门控：无为门 / 知止门 / 编排器
│   ├── compliance/policies.py   # 合规红绿区：红区禁行 + 真实通道确认
│   ├── channels/                # 通道抽象 + 注册表 + 沙箱通道 + 真实适配器示例
│   ├── adapters/base.py         # 真实 API 适配器协议与启用守卫
│   ├── core/
│   │   ├── loop.py              # 自主循环编排（四步闭环 + 状态持久化）
│   │   ├── observe.py           # 观察层：信号采集 + ffi 打分
│   │   ├── decide.py            # 决策层：合规 → 适配 → 门控 → 择优/待时
│   │   ├── act.py               # 行动层：通道执行与计价
│   │   ├── learn.py             # 反馈层：指数加权 + 软最大自进化
│   │   ├── state.py             # 状态持久化（LoopState ↔ JSON）
│   │   └── ffi_bridge.py        # tvm-ffi 双路径桥接（原生优先/参考降级）
│   └── cli.py                   # CLI 入口（demo/--help）
└── tests/                       # pytest 测试（models/config/tao/compliance/channel/learn/ffi/loop/adapters/cli）
```

## 工作原理解析

### 自主循环（core/loop.py）

每轮 `run_round()` 完成：

1. **observe**：轮询各沙箱通道采集机会信号，估算经济参数，经 `ffi_bridge` 打分；
   通道自进化权重放大/缩小得分。
2. **decide**：红区合规过滤 → 通道适配过滤 → 按得分排序 → 道家门控（无为/知止）。
   最优机会被门控拦截则整体 no-op（动善时：最好的机会都不行就不做）。
3. **act**：将决策交给对应通道执行，更新通道余额、全局余额与历史。
4. **learn**：以本轮净收益/转化为反馈，指数加权 + 软最大更新通道权重，进入下一轮。

状态按 `loop.persist_every` 周期写入 JSON；重启时自动恢复。

### 道家门控（tao/gates.py）

- **无为门**（动善时）：机会确定性 < `min_certainty` 或预期收益 < `min_expected_return` → 不行动（待时）。
- **知止门**（知足不辱，知止不殆）：单通道累计收益 ≥ `per_channel_revenue_cap` → 该通道停摆；
  全局余额 ≤ `total_loss_redline` → 整体止损。

### 合规红绿区（compliance/policies.py）

- **红区**（禁行）：`fraud` / `spam` / `clickbait` / `unauthorized_data` / `stock_tip` /
  `medical_diagnosis` —— 任何情况下不得执行。
- **绿区**（许可）：真实通道需 `enable_real=true` 且行为加入 `compliance.confirmed_behaviors`
  才启用；否则以沙箱空适配器对照，不对外发送。

### tvm-ffi 桥接（core/ffi_bridge.py）

```
probe tvm_ffi 可导入 → 加载 native/build/score_opportunity.dll
   → 静态初始化注册 PackedFunc（score_opportunity / risk_adjusted_net）
   → 经 tvm_ffi.get_global_func 调用（backend=native）
   → 任一环节失败 → 纯 Python 参考实现（backend=reference）+ WARN
```

C++ 与 Python 参考实现公式一致：`score = (max(0,收益)·clamp(确定性,0,1)·(1+clamp(稀缺,0,3)) / (1+max(0,成本))) ^ 0.8`，clamp 到 `[0, 100]`。

## 配置说明（config.yaml）

```yaml
tao:
  wuyou:  { min_certainty: 0.55, min_expected_return: 1.5 }   # 无为门阈值
  zhizhi: { per_channel_revenue_cap: 200.0, total_loss_redline: -100.0 }  # 知止门
compliance:
  enable_red_zone: true
  require_confirmation: true
  confirmed_behaviors: []        # 显式确认的真实通道行为
channels:
  content_pricing: { enabled: true, read_price: 0.5, ... }   # 沙箱通道 1
  data_service:    { enabled: true, per_call_price: 0.8, ... } # 沙箱通道 2
  rest_report:     { enabled: false, enable_real: false }     # 真实适配器示例（默认关闭）
ffi:
  native_lib: "native/build/score_opportunity.dll"
  fallback_to_reference: true
```

## 通道扩展指南

新增一个沙箱通道只需三步：

1. **实现子类**：继承 `channels/base.py` 的 `Channel`，实现两个抽象钩子，并按需覆盖其余钩子：

   ```python
   from agent_monetize.channels.base import Channel
   from agent_monetize.models import ActionResult, Feedback, Opportunity, Signal

   class MyChannel(Channel):
       channel_id = "my_channel"          # 注册表 key（须唯一）
       kind = "my_channel"
       requires_real_confirmation = False  # 真实模式需置 True 并走合规确认

       def observe_signal(self) -> list[Signal]:
           # 观察层：采集机会信号（沙箱内模拟，不真联网）
           ...

       def act(self, opportunity: Opportunity) -> ActionResult:
           # 行动层：执行价值交付与计价（虚拟货币）
           ...

       # 可选覆盖
       # decide_eligibility(opp) -> bool   决策层：机会是否适配本通道
       # learn_feedback(feedback) -> None  反馈层：通道内自进化钩子
       # estimate_opportunity(signal) -> Opportunity 机会经济估算（默认读 payload）
   ```

2. **注册**：在 `cli.py::build_registry()` 中按 `config.channels` 开关实例化并 `registry.register(...)`。

3. **配置**：在 `config.yaml` 的 `channels:` 下新增条目（`enabled` + 自定义参数）。

真实 API 通道另需实现 `adapters/base.py::RealAdapterProtocol`（`send()`），
并通过 `AdapterGuard` 保证 `enable_real=true` + 行为被显式加入 `compliance.confirmed_behaviors`
才真正对外发送；否则回退沙箱空适配器。

## 合规声明

- 本平台为 **沙箱虚拟货币演示**，所有计价、余额、净收益均为虚拟，不产生任何真实资金流转。
- 红区行为在任何配置下均被硬拦截；真实通道默认关闭，需人工显式确认后方可启用。
- 真实适配器仅描述「上报」等非资金流转操作，不接入支付/收款等资金通道。

## 许可证

Apache-2.0
