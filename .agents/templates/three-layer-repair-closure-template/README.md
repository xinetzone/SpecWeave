# 三层修复闭环 · 通用自动化脚本模板

基于 [三层修复闭环模式](../../../docs/retrospective/patterns/methodology-patterns/three-layer-repair-closure.md)（`bp-three-layer-repair-closure`）生成的**通用自动化修复脚本模板**，用于处置"反复复发型故障"（同类问题修复后短期再次出现）。

## 模板定位

- **配套模式**：[三层修复闭环](../../../docs/retrospective/patterns/methodology-patterns/three-layer-repair-closure.md)
- **参考实现**：[fix-screenshot-tool.ps1](../../scripts/fix-screenshot-tool.ps1)（Windows 截图工具修复，含 `-Watch` 守护模式）
- **相关模式**：[自动化幂等四要素](../../../docs/retrospective/patterns/methodology-patterns/automation-idempotent-four-elements.md)（脚本遵循 E1-E4 幂等要素）

## 三层结构

| 层 | 名称 | 脚本对应 | 说明 |
|:---:|------|---------|------|
| 1 | 止血 | `Invoke-StopBleeding` | 最小修复恢复症状，幂等 + 可验证 |
| 2 | 断源 | `Invoke-SourceProbe` | 探测周期性破坏源（只读） |
| 3 | 兜底 | `Invoke-WatchHeal` | `-Watch` 守护模式，自动止血 |

## 使用方法

1. 复制 `three-layer-repair-closure-template.ps1` 到目标位置并重命名
2. 搜索 `TODO` 标记，替换 4 处关键实现：
   - `$TargetName`：目标应用/服务/包名
   - `Test-FaultSignal`：故障信号判定（事件日志/进程/文件缺失）
   - `Invoke-StopBleeding` 内的止血命令（幂等、改配置前备份）
   - `Invoke-SourceProbe` 内的破坏源探测逻辑
3. 先用 `-DryRun` 演练验证逻辑，再实际执行

```powershell
# 演练
pwsh -File your-script.ps1 -TargetName "my-service" -DryRun

# 单次：止血 + 断源探测
pwsh -File your-script.ps1 -TargetName "my-service"

# 守护自愈（第3层兜底）
pwsh -File your-script.ps1 -TargetName "my-service" -Watch -WatchIntervalSeconds 60

# 计划任务开机自启（需管理员）
schtasks /Create /TN "MyAppHealWatch" /TR "pwsh.exe -NoProfile -ExecutionPolicy Bypass -File \"<绝对路径>\your-script.ps1\" -TargetName my-service -Watch" /SC ONLOGON /RL HIGHEST /F
```

## 定制注意事项

- **止血命令必须幂等**：重复执行无副作用，否则自动化比手动更危险（反模式3）
- **改配置前备份**：`Invoke-StopBleeding` 中改任何用户配置前先 `.bak-<ts>` 备份（E3）
- **断源探测保持只读**：只提示，不自动卸载/禁用，避免误操作
- **故障信号用机器可判**：`Test-FaultSignal` 返回布尔，配合退出码可进 CI
- **继承本模式 5 个反模式**：只治标不找源、知识不独立沉淀、无自动兜底、归因不验证、断源不备份

## 适用范围

- 适用于：反复复发型故障、存在周期性破坏源的环境、需免人工兜底的运维
- 不适用于：一次性故障（三层是过度工程）、纯只读查询、需人工决策的复杂根因
