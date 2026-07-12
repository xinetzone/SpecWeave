# spec_loader 冷启动风暴应急预案

> 适用场景：spec_loader 缓存版本升级、缓存文件批量清除、服务扩容/重启导致大量实例同时冷启动
> 影响：并发磁盘IO飙升、原子写入竞态导致部分缓存条目丢失、首次请求延迟升高至冷启动水平（~0.9ms，仍可接受）
> 触发条件：缓存文件不存在/损坏/版本不匹配，且并发新实例数 > 5

## 风险等级与影响评估

| 并发实例数 | 风险等级 | 预期影响 | 需要行动 |
|-----------|---------|----------|---------|
| 1-3 | 🟢 低 | 无感知，OS页缓存吸收IO | 无需干预 |
| 4-10 | 🟡 中 | 个别实例冷启动延迟略升（<2ms） | 监控即可 |
| 11-30 | 🟠 中高 | 原子写入竞态导致~10%缓存条目丢失 | 分批预热 |
| 30+ | 🔴 高 | 缓存文件读写冲突，冷启动风暴正反馈 | 立即启用分批重启 |

## 预案一：分批重启策略（推荐用于部署/扩容）

### 核心原则
> **先预热，后切流**。确保新实例在接收流量前已完成缓存预热。

### 分批步骤

```
┌─────────────────────────────────────────────────────────┐
│  批次N（旧实例）          批次N+1（新实例）              │
│  ┌──────────┐            ┌──────────┐                   │
│  │ 服务中 ✓  │  预热脚本  │ 预热中   │  等待预热完成     │
│  │ 缓存热   │ ────────→ │ 无流量   │ ──────→ 切流量    │
│  └──────────┘            └──────────┘                   │
│       ↓ 下一批                                          │
│  ┌──────────┐            ┌──────────┐                   │
│  │ 终止旧实例│            │ 服务中 ✓ │                   │
│  └──────────┘            └──────────┘                   │
└─────────────────────────────────────────────────────────┘
```

**批次大小建议**：
- 总实例 ≤ 10：每批 2-3 个
- 总实例 10-30：每批 3-5 个
- 总实例 > 30：每批 5-8 个，批次间隔 ≥ 2秒

### 操作命令

```bash
# === 批次1：启动新实例组，预热后切流 ===

# 1.1 在新实例上执行预热（不接流量）
python .agents/scripts/spec-loader-warmup.py --quiet --json

# 1.2 验证预热效果（健康检查）
python .agents/scripts/spec-loader-warmup.py --check --json

# 1.3 确认缓存有效后，将流量切换到新实例组
# （由部署系统/负载均衡器执行）

# === 批次2：间隔2秒后启动下一组 ===
sleep 2
python .agents/scripts/spec-loader-warmup.py --quiet --json

# ... 重复直到所有实例完成
```

### 单命令批量预热脚本

```bash
#!/bin/bash
# batch-warmup.sh — 分批预热所有实例
BATCH_SIZE=3
INTERVAL=2
INSTANCES=("host1" "host2" "host3" "host4" "host5" "host6")

for ((i=0; i<${#INSTANCES[@]}; i+=BATCH_SIZE)); do
  BATCH=("${INSTANCES[@]:i:BATCH_SIZE}")
  echo "=== 预热批次 $((i/BATCH_SIZE+1)): ${BATCH[*]} ==="
  for host in "${BATCH[@]}"; do
    ssh "$host" "cd /path/to/SpecWeave && python .agents/scripts/spec-loader-warmup.py --quiet" &
  done
  wait
  echo "批次 $((i/BATCH_SIZE+1)) 预热完成"
  sleep $INTERVAL
done
echo "✅ 所有实例预热完成"
```

## 预案二：缓存版本升级平滑过渡

当需要递增 `cache.version`（如缓存格式变更）时，避免同时失效所有实例缓存：

### 步骤

1. **灰度阶段**（不升级版本，先部署新代码）
   ```toml
   # 新代码兼容读取旧版本缓存，先部署到10%实例
   [cache]
   version = 2   # 保持旧版本号
   ```
   - 验证新代码对旧缓存的读取兼容性
   - 观察无异常后进入全量阶段

2. **全量阶段**（版本递增+分批预热）
   ```toml
   [cache]
   version = 3   # 新版本号
   ```
   - 按照"预案一"分批重启策略执行
   - 新版本实例启动时自动忽略旧缓存（版本不匹配），通过预热脚本重建

3. **回滚方案**
   - 若新版本出现问题，回滚代码即可
   - 旧版本实例将忽略新版本缓存文件（版本号不匹配），自动重建
   - 无数据丢失风险

## 预案三：应急降级（极端情况）

当冷启动风暴已经发生且影响服务质量时：

### 3.1 临时禁用磁盘缓存（避免写入竞态加剧）
```toml
[cache]
enabled = false

[performance]
auto_save_cache = false
```
- 所有实例直接读源文件（~0.9ms），消除写入竞态
- 适用于IO压力极端高的场景（>50并发冷启动）

### 3.2 手动预热后恢复
```bash
# 1. 清除可能损坏的缓存
python .agents/scripts/spec-loader.py cache-clear

# 2. 在一个实例上执行完整预热
python .agents/scripts/spec-loader-warmup.py

# 3. 将预热好的缓存文件复制到所有实例
scp .agents/.cache/spec-loader.json host2:/path/to/SpecWeave/.agents/.cache/
scp .agents/.cache/spec-loader.json host3:/path/to/SpecWeave/.agents/.cache/
# ...

# 4. 恢复缓存配置
# （将 enabled 改回 true，重启服务）
```

### 3.3 缓存文件损坏应急
```bash
# 缓存损坏时SpecLoader自动降级（打印warning日志并重建），无需手动干预
# 若需强制重建：
python .agents/scripts/spec-loader.py cache-clear
python .agents/scripts/spec-loader-warmup.py --quiet
```

## 预案四：低峰期定时预热（预防性）

在每日低峰期（如凌晨3点）主动刷新缓存，确保缓存文件包含最新规范内容：

### Cron 配置
```bash
# 每天凌晨3:00执行预热
0 3 * * * cd /path/to/SpecWeave && python .agents/scripts/spec-loader-warmup.py --quiet >> logs/warmup.log 2>&1
```

### Windows Task Scheduler
```powershell
# 创建每日凌晨3点的计划任务
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument ".agents\scripts\spec-loader-warmup.py --quiet" `
    -WorkingDirectory "D:\spaces\SpecWeave"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -TaskName "SpecLoader-Warmup" -Action $action -Trigger $trigger
```

## 监控指标与告警

通过预热脚本 `--json` 输出采集以下指标：

| 指标 | JSON路径 | 正常阈值 | 告警阈值 |
|------|---------|---------|---------|
| 预热总耗时 | `total_time_ms` | <50ms | >200ms |
| 缓存条目数 | `cache_entry_count` | ≥10 | <5 |
| 缓存文件大小 | `cache_file_size_bytes` | ≥5000 | <1000 |
| 缓存文件有效性 | `cache_file_valid` | `true` | `false` |
| 缓存版本 | `cache_version` | 与配置一致 | 版本落后 |

### 健康检查命令（供监控系统调用）
```bash
python .agents/scripts/spec-loader-warmup.py --check --json
# exit code: 0=健康, 1=缓存异常
```

## 预热脚本参考

完整预热脚本：[spec-loader-warmup.py](../.agents/scripts/spec-loader-warmup.py)

```bash
# 预热全部任务类型（execution+planning）
python .agents/scripts/spec-loader-warmup.py

# 仅预热高频任务类型
python .agents/scripts/spec-loader-warmup.py --tasks code_review,commit,mermaid

# 健康检查（不写入缓存）
python .agents/scripts/spec-loader-warmup.py --check

# JSON输出（供监控采集）
python .agents/scripts/spec-loader-warmup.py --quiet --json

# 预热后运行基准测试验证
python .agents/scripts/spec-loader-warmup.py --benchmark
```

## 版本历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-07-12 | 1.0 | 初始版本，覆盖分批重启、版本升级、应急降级、定时预热四种场景 |
