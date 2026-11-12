---
type: Example
title: "示例：CLI 迭代剧本（无设备也能做完一半）"
description: "从 lint 到 push、run、traces 的完整真机迭代流程，以及没有设备时如何用 lint、单元测试与示例技能完成离线验证；附常见报错对照表"
tags: [phonepal, example, cli, adb, lint, traces]
generated:
  by: specweave-agent
  at: "2026-11-12T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-12T00:00:00+08:00"
status: stable
stale_after: "2027-05-12"
sources:
  - id: S-01
    resource: ../references/00-source-inventory.md
    title: 信源登记：PhonePal 源码快照
---

# 示例：CLI 迭代剧本（无设备也能做完一半）

下面是一条从「我写了个技能」到「我确认它在真机上跑通」的完整路径。前半段不需要手机，后半段需要一台开启无障碍的 Android 11+ 设备。

## 0. 前置条件

| 需要 | 检查方式 | 说明 |
|---|---|---|
| Python 3 | `python3 --version` | CLI 只用标准库，无需装包 |
| 仓库代码 | 当前目录有 `cli/phonepal.py` | — |
| adb（真机阶段） | `adb devices` | 能列出设备 |
| debug APK（真机阶段） | 已安装 `dev.phonepal.app` | release 包没有调试桥 |
| 无障碍服务（真机阶段） | 系统设置里 PhonePal 已开启 | 未开启时任务会报「无障碍服务未开启」 |
| 两个模型（真机阶段） | App 设置里聊天模型与操作模型都已填 Key | 未配置时聊天提示「还没有配置模型」 |

## 1. 离线阶段：只靠 lint

```bash
python3 cli/phonepal.py lint skills/examples/taxi-home
```

**期望输出**（stderr）：

```text
1 skill(s) checked, 1 ok, 0 problem(s)
```

退出码 0。如果技能有问题，会逐条打印 `文件:行号: 消息`，退出码 1：

```text
skills/examples/taxi-home/SKILL.md:9: unknown key 'confirm-before'; expected one of name, description, apps, channel, confirm_before, memory, deeplinks
skills/examples/taxi-home/flow.yaml:3: step 2 (wait): expected milliseconds as an integer 0..600000
1 skill(s) checked, 0 ok, 2 problem(s)
```

一次校验多个目录也可以：

```bash
python3 cli/phonepal.py lint skills/examples/*
```

CLI 还会检查跨目录重名：两个文件夹里出现同一个 `name` 会额外报一条 [F-074]。

## 2. 离线阶段：跑单元测试（可选）

如果你改了 Kotlin 端（比如解析器），这些命令不需要设备：

```bash
./gradlew test
(cd cli && python3 -m unittest discover -s tests -v)
```

Kotlin 侧 162 个测试方法覆盖了 Agent 循环、Sentinel、记忆、技能解析；Python 侧 68 个测试函数覆盖 CLI 参数、lint、trace/logcat 解析 [F-075]。

## 3. 真机阶段：推送技能

```bash
python3 cli/phonepal.py push skills/examples/taxi-home
```

**它做了什么** [F-073]：

1. 先跑一遍 lint，失败则拒绝推送；
2. `rm -rf` 设备上的同名技能目录，再 `mkdir -p`；
3. 逐个 `adb push` 非隐藏文件；
4. 发 `dev.phonepal.debug.RELOAD_SKILLS` 广播，让 App 重新加载并打印问题。

**期望输出**：

```text
pushed skills/examples/taxi-home -> /sdcard/Android/data/dev.phonepal.app/files/skills/taxi-home (SKILL.md, flow.yaml)
skills reloaded; problems found by the app are logged under tag PhonePal
```

## 4. 真机阶段：跑任务并跟随事件

```bash
python3 cli/phonepal.py run "帮我打车回家" --skill taxi-home --follow
```

**执行顺序** [F-073]：

1. 生成 run id（`cli-YYYYMMDD-HHMMSS-xxxx`）或使用 `--run-id`；
2. 先启动 `adb logcat -v threadtime -s PhonePal`，避免漏事件；
3. 发 `dev.phonepal.debug.RUN` 广播，带 `goal`、`skill`、`run_id`；
4. 逐行解析事件，打印到终端；
5. 收到 `PhoneTaskFinished` 或 `Failed` 后退出；成功返回 0，失败返回 1。

**终端会看到的行**（示意）：

```text
10:15:03.120 cli-20261112-101500-abcd PhoneTaskStarted  #0 | 帮我打车回家
10:15:04.880 cli-20261112-101500-abcd StepPlanned        #0 launch "打开 com.autonavi.minimap"
10:15:05.690 cli-20261112-101500-abcd StepExecuted       #0 launch "launched com.autonavi.minimap" ok=true
10:15:07.010 cli-20261112-101500-abcd StepPlanned        #1 deeplink "打开链接 amapuri://..."
...
10:15:22.400 cli-20261112-101500-abcd NeedsUser          #5 | 即将点击「确认呼叫」，是否继续？
10:15:31.900 cli-20261112-101500-abcd StepExecuted       #5 tap "click node 12" ok=true [ask: ...]
10:15:33.200 cli-20261112-101500-abcd MemoryUpdated      #7 | howto/taxi-home
10:15:33.210 cli-20261112-101500-abcd PhoneTaskFinished  #8 | 已叫到快车，预估 32 元 ok=true
```

注意 `StepExecuted` 行可能带 `[ask: ...]`：说明这一步经过审批后被允许 [F-071]。

## 5. 真机阶段：看轨迹

```bash
python3 cli/phonepal.py traces show cli-20261112-101500-abcd --full
```

如果本地 `traces/` 没有这个 run，CLI 会先从设备 `adb pull` 下来再渲染 [F-073]。输出是一张步骤表，列包括 step、kind、action、decision、ok、text；`--full` 不截断长单元格。

想看原始证据：

```bash
python3 cli/phonepal.py traces pull cli-20261112-101500-abcd --out traces
```

然后打开：

```text
traces/cli-20261112-101500-abcd/
├── trace.jsonl     # 每行一个事件，8 个固定键
├── audit.jsonl     # 每行一条 Sentinel 决策
└── step-*.png      # 每个动作前的屏幕
```

## 6. 中断与停止

```bash
python3 cli/phonepal.py stop
```

它发 `dev.phonepal.debug.STOP`。停止是协作式的：会话会释放待答问题与审批，Agent 在下一个循环开头检查 `StopSignal` 并退出 [F-069]。

## 7. 常见现象对照表

| 现象 | 可能原因 | 处理 |
|---|---|---|
| `adb not found` | adb 不在 PATH | `--adb /path/to/adb` 或设 `ADB` 环境变量 |
| `broadcast ... failed: Error` | App 不是 debug 包或未安装 | 装 debug APK，确认接收器存在 |
| 终端一直不结束 | 任务没有发终止事件（理论不应发生） | 检查 App 是否被杀；重跑并看 logcat |
| `无障碍服务未开启` | 服务未启用 | 系统设置 → 无障碍 → PhonePal |
| `还没有配置模型` | 聊天或操作模型缺字段 | 设置里补齐 Base URL / 模型 / Key |
| `找不到技能 taxi-home` | 技能没推上去或名字不一致 | 重新 `push`，或看 reload 日志 |
| `invalid YAML` | frontmatter 缩进/引号问题 | 按 lint 的行号修 |
| `step N (type): expected { target: ..., text: ... }` | `text: {destination}` 未加引号 | 改成 `text: "{destination}"` |

## 8. 没有设备时，这个剧本能走到哪一步

| 阶段 | 无设备 | 有设备 |
|---|---|---|
| 写技能 + lint | ✅ | ✅ |
| 跨技能重名检查 | ✅ | ✅（App 也会报） |
| 单测（解析器/循环/记忆/安全） | ✅ | ✅ |
| push | ❌ | ✅ |
| run / logs / traces | ❌ | ✅ |
| 看某一步的截图 | ❌ | ✅ |

所以「先把 lint 与单测跑绿」不是妥协，而是这个项目本身的开发方式：CI 里也没有真机 [F-076]。

## 相关概念

- [CLI 与轨迹：三层证据的设计](../concepts/09-cli-and-traces.md)
- [技能与 flow：lint 的规则来源](../concepts/06-skills-and-flows.md)
- [示例：技能解剖](01-skill-anatomy.md)
- [示例：测试替身](03-test-doubles.md)
