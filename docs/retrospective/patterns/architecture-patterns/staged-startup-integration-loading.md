+++
id = "staged-startup-integration-loading"
domain = "architecture"
layer = "architecture"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "standard"
source = "d:\\AI\\.temp\\libs\\home-assistant\\core\\homeassistant\\bootstrap.py"

[bindings]
rules = []
references = [
  "d:\\AI\\.temp\\libs\\home-assistant\\core\\homeassistant\\bootstrap.py",
  "d:\\AI\\.temp\\libs\\home-assistant\\core\\homeassistant\\setup.py"
]
skills = []
+++

# 分阶段集成加载（Staged Startup Integration Loading）

## 1. 问题

当系统拥有大量可选集成/插件时，启动装配存在三个典型风险：

- **长尾拖垮启动**：少数慢插件把整体启动时间拉长甚至卡死
- **依赖关系复杂**：装配顺序难以人工维护
- **早期不可观测**：系统未进入可用态之前，缺少诊断与自愈手段

## 2. 解决方案（模式）

将启动拆分为多个阶段（stage），对每个阶段：

- 明确装配目标（基础能力优先）
- 允许阶段内并发装配
- 为可超时的阶段配置超时策略，超时后“推进到下一阶段”

本模式来源于 Home Assistant Core 的 bootstrap 设计，其将集成装配分为 stage 0/1/2，并对部分阶段应用超时推进策略，以确保系统尽快进入可用态。

## 3. 适用场景

- 插件/集成数量较多（数十到数百）
- 启动期存在强依赖（网络/存储/注册中心等基础能力必须优先）
- 允许“部分能力延迟上线”，但要求整体尽快 RUNNING

## 4. 实施要点

### 4.1 阶段划分建议

- **Stage 0（基础能力）**：日志、存储、HTTP、配置中心、注册表、鉴权等
- **Stage 1（发现与基础生态）**：设备发现、网络发现、桥接层等
- **Stage 2（业务集成）**：所有剩余插件/集成

### 4.2 超时策略建议

- Stage 0 中对“数据库迁移/关键基础能力”可选择不设置或设置更大超时，避免半初始化导致数据一致性风险
- Stage 1/2 默认设置合理超时；超时后记录告警并继续推进

### 4.3 可观测性建议

- 每个 stage 输出：计划装配清单、完成数、失败数、超时数
- 启动结束后输出：仍在装配/未装配的长尾清单

## 5. 反例

- 所有集成“一锅并发”：短期看快，但会制造不可控竞态与资源争抢
- 所有集成“串行装配”：可控但极慢，长尾风险被放大
- 不设置超时：长尾集成可永久阻塞启动

