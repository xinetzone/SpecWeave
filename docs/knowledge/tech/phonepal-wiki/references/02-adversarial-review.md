---
type: Reference
title: "对抗审查记录：PhonePal Wiki 的 V 阶段核验"
description: "V 阶段四视角对抗审查与机械核验记录：141 个 API 符号存在性、22 项计数断言、链接与 frontmatter 检查，以及审查中实际发现并修复的 6 处表述问题与 4 类残余风险"
tags: [phonepal, adversarial-review, verification, quality-gate, okf]
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
    resource: ./00-source-inventory.md
    title: 信源登记（commit 与路径口径）
  - id: S-02
    resource: ./01-api-map.md
    title: 关键类型与签名索引
---

# 对抗审查记录

本页记录 V 阶段实际做了什么、发现了什么、改了什么。原则：**只记录有证据的结论**；没跑的验证明确写「未执行」，不用「应该没问题」代替。

## 1. 机械核验结果

| 检查 | 方法 | 结果 |
|---|---|---|
| API 存在性 | 从正文与 [API 索引](./01-api-map.md) 抽取 141 个符号，在固定 commit 的全仓源码中按词边界搜索 | 141/141 存在，0 缺失 |
| 计数断言 | 独立脚本重新计算 22 项（模块、枚举、确认词、启动器、工具、命令、测试方法、文件/行数等），与正文数字逐项比对 | 22/22 一致，0 差异 |
| 本地链接 | `check-links.py --path docs/knowledge/tech/phonepal-wiki --check-frontmatter-paths` | 首轮 8 处断链（全部指向尚未创建的 `02-adversarial-review.md`），创建本文件后复跑通过：22 个文件、129 条本地引用全部有效 |
| frontmatter 路径 | 同上脚本 | 全部有效 |
| 目录级回归 | `check-links.py --path docs/knowledge/tech --check-frontmatter-paths` | 本包新增链接全部有效；该目录另有 5 处**既有** frontmatter 绝对路径失效（`p1-09`、`p1-10`、`p1-13`、`p1-17`、`p2-13`），不属于本次变更，未代为修改 |
| Sphinx 定向构建 | `python -m sphinx -b dummy -E docs <out> docs/knowledge/tech/phonepal-wiki/index.md` | 退出码 0；输出中的告警全部来自无关的既有文档（`knowledge/mdi`、`retrospective/archives`），本包 0 告警 |
| 信源路径 | 人工检索包内 `file:///`、`external/`、`.temp/` | 正文 0 处；仅 `log.md` 与信源登记提到 `.temp` 脚本为一次性工具，不含可点击路径 |
| GATE-SPS 清理前扫描 | `check-source-path-stability.py --path docs/knowledge/tech/phonepal-wiki --target external/dev/libs/others/xiaoman` | `rc=0`：本包 0 处引用待删目录，信源引用只以仓库相对路径 + commit hash 形式出现 |

核验脚本：`.temp/xiaoman-count/verify_bundle.py`（一次性工具，不随包分发）。核心输出：

```text
symbols_checked 141
symbols_missing 0 []
counts {'modules': 8, 'main_kt_files': 59, 'main_kt_lines': 6541, 'test_kt_files': 20,
        'test_kt_lines': 2669, 'kt_test_methods': 162, 'py_main_lines': 1679,
        'py_test_files': 4, 'py_test_methods': 68, 'py_test_lines': 739,
        'actions': 11, 'agent_events': 10, 'flow_step_types': 8, 'flow_step_kinds': 8,
        'skill_keys': 7, 'channels': 6, 'confirm_words': 17, 'launchers': 12,
        'tools': 6, 'cli_commands': 6, 'cli_traces_subcommands': 2, 'example_skills': 3}
count_diffs {}
```

## 2. 四视角审查

| 视角 | 攻击 | 结论 |
|---|---|---|
| 魔鬼代言人 | 「这套 Sentinel 能挡住恶意模型吗？」 | 不能，也不声称能。它挡的是「模型被页面诱导」「技能偷偷放宽权限」「在支付/密码页乱操作」；对恶意 App 伪造 UI、无障碍权限被滥用、设备被 root 不提供保护。已在 [04 概念页](../concepts/04-sentinel.md) 的威胁模型表中写明 |
| 新人 | 「为什么不用 Hilt / 向量库 / 插件框架？」 | 代码规模小（59 个 main 文件），手写 `AppGraph` 足够；记忆选择 Markdown 是为了可读与可外部编辑，不是性能最优。正文没有声称这些选择「更好」，只解释取舍 |
| 老板 | 「能不能直接商用？」 | MIT 允许，但本项目只做了源码学习，未运行真机、未构建 APK、未调用模型 API；可靠性、成本、合规都未验证。首页「能力边界」与本节「未执行」明确写出 |
| 未来 | 「半年后哪里最先过期？」 | CLI 命令与参数、模型默认 Base URL、Sentinel 确认词、Android 截图限制。已写入首页「维护提示」与 `next_review` |

## 3. 实际发现并修复的问题

| # | 问题 | 类型 | 处理 |
|---|---|---|---|
| 1 | 首页曾写「3300+ 行测试」，未经验证 | 计数断言无依据 | 重算：Kotlin 测试 2669 行 + Python 测试 739 行 = 3408 行；改为「3400+ 行（2669 + 739）」，并在信源登记补齐两项计数 |
| 2 | 正文引用 `maxSteps` 可调范围 `1..200`，但事实清单没有对应事实 | 事实缺号 | 新增 F-079（`AppSettings.MAX_STEPS_RANGE`、温度范围、默认 Base URL），正文改引 F-079 |
| 3 | 「审批卡（聊天页与悬浮窗都能显示）」 | 过度声称 | 阅读 `OverlayController` 后确认悬浮窗只显示步骤文字与停止按钮；改为「聊天界面审批卡或通知栏通知」，新增 F-081 支撑 |
| 4 | `step-<n>.png` 被描述为「动作前的屏幕」 | 口径不精确 | `RecordingDevice` 是在每次 `observe()` 后保存截图；改为「每次 observe 的截图」，新增 F-082 支撑 |
| 5 | 「Sentinel 还会再弹一次审批」写成绝对行为 | 过度声称 | 改为「target 或被点节点文字命中确认词时才会再弹」，与 Sentinel 的实际匹配来源一致 |
| 6 | 首轮链接检查 8 处断链 | 结构问题 | 本文件创建后全部指向真实文件；复跑链接检查通过 |

事实清单的编号在写作过程中从 F-076 增长到 F-082，每增加一条都同步了首页、本页与信源登记的计数；最终口径统一为 **82 条**。

## 4. 没有做的事（明确边界）

| 未执行 | 原因 | 影响 |
|---|---|---|
| Gradle 构建 / 单元测试实际运行 | 环境未安装 Android SDK 35 与 JDK 17 组合；本次是源码学习任务 | 「测试可脱离设备运行」来自构建脚本与测试文件结构，不是运行结果 |
| 真机安装与任务运行 | 无 Android 设备 | 所有运行时行为描述来自源码与仓库文档；未验证实际 App 表现 |
| 模型 API 调用 | 无 API Key | 未验证具体供应商兼容性；正文只描述客户端代码行为 |
| 上游仓库完整性校验 | 无网络/凭据访问 `git@github.com:aduoge/xiaoman.git` | commit hash 来自本地仓库；无法确认远程是否仍可访问 |
| 独立模式文档入库 | 避免同一结论两处维护 | 五条可迁移模式保留在 [10 工程模式](../concepts/10-engineering-patterns.md)，未写入 `docs/retrospective/patterns/` |

## 5. 结论

- **事实层**：82 条事实均有源码路径与行号；数量类事实经独立脚本复核。
- **API 层**：141 个符号全部存在，无虚构 API。
- **结构层**：根索引与三个子索引均含 `{toctree}`，链接与 frontmatter 通过检查。
- **表述层**：修复 5 处过度声称/口径不精确，保留 1 处结构性修复（断链）。
- **可信度**：作为「源码学习 Wiki」可交付；作为「运行手册」需补真机验证。

## 相关概念

- [信源登记](./00-source-inventory.md)
- [关键类型与签名索引](./01-api-map.md)
- [工程模式与边界](../concepts/10-engineering-patterns.md)
