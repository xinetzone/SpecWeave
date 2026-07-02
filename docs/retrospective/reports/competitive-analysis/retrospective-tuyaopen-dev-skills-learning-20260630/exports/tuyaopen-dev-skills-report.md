# TuyaOpen-dev-skills 精简报告（导出）

> 对象：TuyaOpen-dev-skills（TuyaOpen 硬件开发 AI Skills 仓库）
> 本地路径：`d:\AI\external\TuyaOpen-dev-skills`
> 日期：2026-06-30

## 1. 这是什么

TuyaOpen-dev-skills 是一个面向 Cursor / Claude Code 等 AI 工具的 Skills 仓库，把 TuyaOpen 的开发流程（环境搭建、项目配置、编译、代码检查、烧录监控、授权、迭代闭环）封装为：

- `SKILL.md`：最小入口（触发词 + 指令）
- `references/`：长文档参考（按需加载，控制上下文）
- `scripts/`：可执行脚本（把“建议”变成“动作”）

核心证据：[README_zh.md](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/README_zh.md#L132-L136)

## 2. 为什么重要（给 AI 做事的工程化答案）

它的关键价值不是“写了很多提示词”，而是把智能体最常见的失败模式系统性压缩掉：

- 入口正确：技能触发与最小指令被固化在 `SKILL.md`
- 上下文可控：长文档被放到 `references/`，避免默认加载造成上下文爆炸
- 动作可复现：关键流程由 `scripts/` 提供脚本化执行路径

## 3. 值得复用的实现亮点

### 3.1 可编排脚本：JSON 输出契约 + 会话外部化

以后台日志抓取脚本 [monitor_helper.py](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/debug-helper/scripts/monitor_helper.py) 为例：

- `--json` 输出（机器可读，便于上层编排）
- `session.json` 保存状态（start/tail/stop 跨进程协同）
- stop 前校验 PID 属于 `tos.py monitor`，避免误杀

### 3.2 安全护栏优先（路径越界防护/误杀防护）

- 路径越界防护：拒绝 repo_root 外的文件参数（[check_files.py:L46-L55](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/code-check/scripts/check_files.py#L46-L55)）
- 误杀防护：停止前校验进程身份（[monitor_helper.py:L118-L140](https://github.com/tuya/TuyaOpen-dev-skills/blob/main/skills/tuyaopen/debug-helper/scripts/monitor_helper.py#L118-L140)）

## 4. 可直接迁移的模式清单

- 技能三分结构：`SKILL.md`（入口）+ `references/`（长文档）+ `scripts/`（动作）
- 脚本可编排输出：默认 `--json`，错误时 `ok=false` + 非 0 退出码
- 会话外部化：跨命令共享状态写入固定 session file
- 路径越界防护：realpath + 前缀校验阻断任意路径访问
- 停止前身份校验：kill 前先确认 cmdline 属于目标进程

## 5. 风险点（需要关注）

- Windows 下用于 cmdline 校验的 `wmic` 可能在新系统上不可用，建议增加 PowerShell CIM fallback
- `tail` 读取全文件的方式在超大日志下会退化，可改为 seek-based tail

## 6. 延伸阅读

- 学习笔记：[tuyaopen-dev-skills-learning.md](../../../../../knowledge/learning/tuyaopen-dev-skills-learning.md)
- 本次完整报告目录：[retrospective-tuyaopen-dev-skills-learning-20260630](../README.md)
