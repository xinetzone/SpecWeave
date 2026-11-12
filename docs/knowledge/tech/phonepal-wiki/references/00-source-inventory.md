---
type: Reference
title: "信源登记：PhonePal（xiaoman）源码快照"
description: "本知识包的唯一信源台账：仓库地址、固定 commit、模块清单与文件/行数、随仓库文档资产、采集与复核命令，以及 external/ 本地副本的持久性说明"
tags: [phonepal, xiaoman, source-inventory, android, kotlin, okf]
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
    title: 本文即信源台账
---

# 信源登记：PhonePal（xiaoman）源码快照

本知识包的所有事实只来自一个信源：开源 Android 应用 **PhonePal**（仓库目录名 `xiaoman`）的源码快照。本页登记该快照的不可变坐标、规模与复核方式；正文文档中的 `F-xxx` 编号对应 R 阶段事实清单（76 条）。

## 1. 信源坐标（固定版本）

| 项 | 值 |
|---|---|
| 产品名 | PhonePal（中文 README 亦称「跑在 Android 手机上的开源私人助手」） |
| 仓库目录 | `external/dev/libs/others/xiaoman` |
| 远程地址 | `git@github.com:aduoge/xiaoman.git` |
| 固定 commit | `580fdf750f946a6e411c3f54a86443c66aa46652` |
| commit 时间 | 2026-11-01 18:04:22 +0800 |
| commit 信息 | 文档中文化并整理 core-agent 代码结构 |
| tag | 无（仓库只有 2 个提交：`057482b` Initial import、`580fdf7`） |
| 工作树 | 干净（`git status --short` 无输出） |
| 许可证 | MIT（仓库根 `LICENSE`） |
| 采集时点 | 2026-11-12 |

> **为什么固定 commit 而不是分支或 tag**：该仓库没有发布 tag，`main` 会前进。本文所有行号与结论都绑定到上面的 40 位 commit；信源更新后需重新采集，不能假定旧行号仍有效。

> **持久性说明**：`external/` 在 SpecWeave 主仓 `.gitignore` 中，属于本地外部资料区，不随主仓分发。因此本知识包的引用一律写成**仓库相对路径 + commit hash**（例如 `core-agent/src/main/kotlin/dev/phonepal/agent/OperatorLoop.kt:51-149`），不写 `file:///` 绝对路径，也不依赖本地副本长期存在。复核时按远程地址检出到同一 commit 即可复现。

## 2. 规模（脚本计数，非人工枚举）

| 指标 | 数值 | 口径 |
|---|---|---|
| Gradle 模块 | 8 | `settings.gradle.kts` 的 `include` 列表 |
| main Kotlin 文件 | 59 | `*/src/main/**/*.kt` |
| main Kotlin 行数 | 6541 | 同上，按 `splitlines()` 计 |
| test Kotlin 文件 | 20 | `*/src/test*/**/*.kt` |
| test Kotlin 行数 | 2669 | 同上 |
| Kotlin `@Test` 方法 | 162 | 同上文件内正则计数 |
| CLI Python 文件 | 8 | `cli/phonepal_cli/*.py` + 入口 `cli/phonepal.py`，不含测试 |
| CLI Python 行数 | 1679 | 同上 |
| CLI 测试文件 / 测试函数 / 行数 | 4 / 68 / 739 | `cli/tests/test_*.py` |
| 示例技能 | 3 | `skills/examples/*/`：`open-settings-wifi`、`takeout-reorder`、`taxi-home` |

分模块 main 文件数：core-api 6、core-llm 2、core-memory 5、core-skills 4、core-sentinel 2、core-agent 11、hands 7、app 22（合计 59）。

计数脚本为一次性工具，落在 `.temp/xiaoman-count/count_facts.py`（临时目录，不随知识包分发）。复核时可用等价命令：

```bash
# 模块数
grep -c '":' settings.gradle.kts
# main Kotlin 文件数
find . -path '*/src/main/*' -name '*.kt' | wc -l
# Kotlin 测试方法数
grep -rho '@Test' --include='*.kt' . | wc -l
# 示例技能数
find skills/examples -mindepth 1 -maxdepth 1 -type d | wc -l
```

## 3. 随仓库的文档资产（二手信源，仅作交叉印证）

| 文件 | 内容 | 与本包的关系 |
|---|---|---|
| `README.md` | 产品定位、工作方式图、安全摘要、构建与使用、目录树 | 与源码一致；本包 00 概念页以其为骨架但逐条回源码核验 |
| `README.en.md` | 英文版 README | 未单独引用 |
| `docs/ARCHITECTURE.md` | 模块表、依赖方向、聊天/操作循环伪代码、技能与记忆格式、Sentinel 规则、调试桥与轨迹格式 | 结构描述与源码一致；本包在其基础上补了实现细节（行号级） |
| `docs/skills.md` | 技能作者指南：放置位置、7 个 frontmatter 字段、flow 示例、校验规则、安全边界 | 与 `SkillParser/FlowParser` 一致 |
| `cli/README.md` | CLI 用法 | 与 `main.py` argparse 定义一致 |
| `skills/examples/*` | 3 个示例技能 | 示例 01 逐行拆解 |

> 文档资产只用于「交叉印证」：本知识包的每条结论都能落到具体源码行；两者冲突时以源码为准（本次采集未发现冲突）。

## 4. 构建与运行环境（供复现）

| 项 | 值 | 来源 |
|---|---|---|
| JDK | 17（toolchain 与 CI 均为 17） | `app/build.gradle.kts:68`、`.github/workflows/ci.yml:14-16` |
| Android compileSdk / minSdk / targetSdk | 35 / 30 / 35 | `app/build.gradle.kts:37-42` |
| 版本号 | `0.1.0`（versionCode 1） | `app/build.gradle.kts:43-44` |
| Kotlin / AGP | 2.1.0 / 8.7.3 | `gradle/libs.versions.toml:2-3` |
| 构建入口 | `scripts/gradle.sh test :app:assembleDebug` | `README.md:42-45` |
| CI | `./gradlew test :app:assembleDebug` + CLI unittest + 示例技能 lint | `.github/workflows/ci.yml:14-26` |

## 5. 本包的验证方式（V 阶段口径）

1. **API 真实性**：正文引用的类名/方法名/常量名逐个在源码中 Grep 验证，命令与结果见 [对抗审查记录](./02-adversarial-review.md)。
2. **计数断言**：模块数、Action/事件/步骤枚举数、确认词数、启动器包数、工具数、命令数、测试方法数均以脚本或 `Grep` 独立复核，口径写在数字旁。
3. **链接**：包内交叉链接全部为相对路径，按 `docs/knowledge/tech/phonepal-wiki/` 目录解析。
4. **信源路径**：正文只出现仓库相对路径与 commit hash，不出现本地绝对路径或临时目录。

## 相关概念

- [关键类型与签名索引](./01-api-map.md)
- [对抗审查记录](./02-adversarial-review.md)
- [PhonePal 全景](../concepts/00-overview.md)
