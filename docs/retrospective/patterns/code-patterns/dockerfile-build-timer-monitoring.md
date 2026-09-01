---
id: "dockerfile-build-timer-monitoring"
title: "Dockerfile 多阶段构建计时器模式"
type: "code-pattern"
maturity: "L1-实验性"
maturity_note: "devcontainer-base variants/ 里程碑实战验证；单案例，待更多 Docker 项目验证后升级L2"
source:
  - "devcontainer-base variants/ 多阶段构建计时器实现（[TIMER] 标记 + 日志解析）"
related_patterns:
  - "structured-lightweight-logging.md"
  - "docker-buildkit-optimization-best-practices.md"
tags: ["docker", "multi-stage-build", "build-timer", "logging", "performance", "buildkit", "stage-timing"]
validation_count: 1
reuse_count: 1
---

# Dockerfile 多阶段构建计时器模式

## 触发场景

- 编写或审查多阶段 Dockerfile，构建耗时长但无法定位瓶颈阶段
- 遇到以下任一痛点：
  - BuildKit 输出有进度信息，但缺少阶段级耗时汇总，无法判断"哪个 RUN 是瓶颈"
  - 构建脚本难以从日志中自动提取各阶段耗时用于性能分析
  - 需要为每次构建生成可审计的阶段耗时报告

**适用于**：多阶段 Dockerfile、需要构建耗时观测与瓶颈定位的项目。
**不适用于**：单阶段快速构建、构建时间 <1 分钟无需观测的场景。

## 问题本质

Docker BuildKit 的默认输出虽然有进度信息，但**没有阶段级耗时汇总**。构建耗时长时，开发者只能靠肉眼观察，无法快速定位瓶颈阶段，也无法在脚本中自动解析阶段耗时。

## 解决方案（四步计时器）

### 1. 每个 RUN 阶段开始时记录起始时间

```bash
_STAGE_START=$(date +%s)
```

### 2. 阶段结束时计算耗时并输出 `[TIMER]` 标记

```bash
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
echo "[TIMER] Stage X/Y (阶段描述) took ${_ELAPSED}s"
```

### 3. 最终阶段输出 ASCII 汇总表

将各阶段 `_STAGE_START` 存入临时文件（如 `/tmp/.variant-build-timer`），最终阶段读取并计算每阶段耗时，输出 ASCII 汇总表：

```
╔══════════════════════════════════════════════════════════════╗
║  BUILD TIMING SUMMARY (5 Stages)                             ║
╠══════════════════════════════════════════════════════════════╣
║  Stage 1/5  base verification         35s                    ║
║  Stage 2/5  system+mirror config      66s                    ║
╚══════════════════════════════════════════════════════════════╝
```

### 4. 构建脚本通过 tee 保存日志并解析 `[TIMER]` 标记

```bash
docker build --progress=plain ... 2>&1 | tee "$log_file"
# 解析 [TIMER] Stage X/Y took Ns 标记
```

## 关键设计决策

- **阶段计时状态跨 RUN 不共享**：`_STAGE_START` 只在单个 RUN 内有效，跨 RUN 的状态（起始时间）必须写入 `/tmp/` 文件持久化
- **`[TIMER]` 标记格式统一**：使用固定格式 `[TIMER] Stage X/Y (desc) took Ns`，便于 grep/awk 解析
- **final stage 必须输出 `[TIMER]` 行**：即使最终阶段输出格式化表格，也需额外输出 `[TIMER] Stage N/M took Ns` 行，否则日志解析器会遗漏 final stage
- **Build duration 必须显式追加到日志文件**：如果通过 `docker build | tee` 管道保存日志，构建脚本中直接 `echo` 的 Build duration 不会进入管道，需显式 `>> "$log_file"` 追加
- **解析需防御非数字耗时**：`duration` 可能为 `N/A`（解析失败），累加前需判断是否为纯数字（`^[0-9]+s$`），避免 `set -e` 下算术求值错误中断主循环

## 反模式

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| 各 RUN 内部单独计时但不持久化起始时间 | 无法跨 RUN 汇总总耗时 | 起始时间写入 `/tmp/` 临时文件 |
| final stage 只输出表格不输出 `[TIMER]` 标记 | 日志解析器遗漏 final stage 耗时 | 同时输出 `[TIMER] Stage N/M took Ns` 行 |
| Build duration 直接 echo 到终端 | `docker build \| tee` 管道中不进入日志文件 | 显式 `>> "$log_file"` 追加 |
| 解析耗时直接算术累加不判断类型 | duration=N/A 时触发 `set -e` 算术错误中断构建 | 先正则判断 `^[0-9]+s$` 再累加 |

## 迁移验证

本模式可迁移到以下场景：
- ✅ 任何多阶段 Dockerfile 的构建耗时观测
- ✅ 需要构建脚本自动提取阶段耗时的 CI 流水线
- ✅ 其他需要"分阶段计时 + 日志可解析"的长时构建过程

## 检查清单

- [ ] 每个 RUN 阶段开始时记录 `_STAGE_START=$(date +%s)`
- [ ] 阶段结束时输出 `[TIMER] Stage X/Y (desc) took Ns` 标记
- [ ] 跨 RUN 计时状态已写入 `/tmp/` 文件持久化
- [ ] final stage 同时输出 `[TIMER]` 行和格式化汇总表
- [ ] Build duration 已显式追加到日志文件
- [ ] 日志解析器已防御非数字耗时（N/A）
