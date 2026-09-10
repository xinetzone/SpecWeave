---
id: "external-cli-version-drift-fallback"
title: "外部 CLI 版本漂移的候选回退与能力探测"
type: "code-pattern"
date: "2026-09-10"
maturity: "L1-draft"
source: "jpman-client refresh_host_keys 对 Windows 双份 ssh-keyscan 的兼容处理 (2026-09-10)"
related_patterns:
  - "multi-strategy-auto-discovery"
  - "platform-aware-dependency-detect"
  - "ffi-fallback-diagnostics"
tags: ["cli", "version-drift", "fallback", "capability-probe", "windows", "ssh-keyscan", "kex", "robustness"]
validation_count: 1
reuse_count: 0
---

# 外部 CLI 版本漂移的候选回退与能力探测

## 模式概述

调用外部命令行工具时，同样的工具名在不同环境可能来自**不同来源、不同版本、不同构建配置**，其能力并不等价。典型：`ssh-keyscan` 在 Windows 上同时存在于 `C:\Windows\System32\OpenSSH\`（OpenSSH_for_Windows 9.5p2，KEX 构建集不含 `sntrup761x25519-sha512`）与 `C:\Program Files\Git\usr\bin\`（MSYS 构建），前者对 OpenSSH 10 服务器协商直接失败，后者成功。

模式做法：**不依赖 `which` 的单点结果**，而是构建候选可执行列表逐个尝试，并以"**产出是否符合预期**"而非"退出码是否为 0"判定成功；失败时保留诊断信息而非静默降级。

## 触发场景

- **适用于**：代码需要调用系统外部 CLI（git/curl/ssh/ffmpeg/tar/unzip/keyscan…）；目标环境不可控（多平台、CI、容器、Windows 多套工具共存）；对端服务版本较新（协议/算法协商可能失败）
- **不适用于**：工具由项目自身随包分发且版本固定（如 vendor 内置二进制）；纯 Python 库可替代的场景（优先用库而非 CLI）；一次性人工排障（直接敲命令即可）

## 核心做法

1. **枚举候选**：按可靠性排序构造候选列表（如"附带新版 → 环境自带 → `shutil.which` 兜底"），而非硬编码单一绝对路径
2. **逐个尝试并判定产出**：对每个候选执行，判定标准是"是否产出符合预期的内容"（本案例：是否解析出合法 host key 行），退出码仅作辅助
3. **保留诊断**：记录每个候选的失败原因（stderr、kex 失败的算法名），失败时给出可执行建议而非静默降级
4. **消除地址/环境歧义**：对 `localhost` 这类双栈名，先显式探测可达地址（`127.0.0.1` / `::1`）再直连，避免"连接被拒"被误读为目标不可达
5. **必要时规范化产出**：不同候选的输出格式可能不同（`[127.0.0.1]:2222` vs `[localhost]:2222`），统一改写为目标消费者期望的形式
6. **前置就绪门**：调用前先确认运行时/依赖就绪（如容器运行时可达），避免在注定失败的状态下执行重操作

## 反模式

| 反模式 | 表现 | 后果 | 正确做法 |
|--------|------|------|---------|
| ❌ `which()` 命中即认为可用 | 只取 PATH 首个结果，不验证能力 | 版本/构建差异导致协商失败，表现为"目标不可达"误导排障（本案例 System32 keyscan 报 unsupported KEX） | 候选列表 + 以产出判定成功 |
| ❌ 用退出码作为唯一成功判据 | `returncode == 0` 才继续 | 部分工具失败也返回 0（或成功返回非 0），漏判/误判；也可能拿到有效输出却因非 0 被丢弃 | 以"产出是否符合预期"判定，退出码仅辅助 |
| ❌ 硬编码单一绝对路径 | 写死 `C:\Program Files\...\tool.exe` | 换机/换安装位置即失效 | 候选多路径 + `which` 兜底 |
| ❌ 把协商失败当成网络不可达 | 见 "connection refused / unsupported" 就去查网络 | 排查方向错误，浪费时间 | 区分"连不上"与"连上了但协商失败"，保留 stderr 原始信息 |
| ❌ 静默降级不提示 | 候选全失败后直接返回默认值 | 用户以为已生效，实际功能缺失 | 失败时输出原因与下一步建议 |

## 检验标准

- 至少两个候选来源被显式枚举，且优先级有依据（新版/附带优先）
- 成功判据基于产出内容，而非退出码
- 全部候选失败时，输出包含失败原因与可执行建议（不静默）
- 存在地址族/格式歧义时已做显式归一化
- 在"旧版可用候选"与"新版不可用候选"共存的环境下实测通过

## 迁移案例（跨场景）

- **HTTP 客户端**：系统 `curl` 过旧不支持 TLS1.3/HTTP2 → 候选列表（随包 curl → 系统 curl），以响应内容判定成功
- **媒体处理**：发行版 `ffmpeg` 缺失编码器 → 候选（项目自带静态构建优先），以产物可解码判定
- **CI Python 解释器**：`python` 指向不同版本导致语法/依赖行为差异 → 显式探测版本能力而非依赖 PATH 首项
- **Windows 归档工具**：`tar`/`unzip` 在 System32 与 Git、MSYS 下行为不一致 → 候选回退 + 产物校验

## 相关复盘

- 里程碑全貌见 [retrospective-jpman-client-stability-milestone-20260910](../../reports/concepts/milestone/retrospective-jpman-client-stability-milestone-20260910.md)
