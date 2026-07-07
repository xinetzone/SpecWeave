# TuyaOpen 目录全链路复盘 — 学习与导出建议

> **分析对象**：`.temp/libs/TuyaOpen`
> **复盘日期**：2026-06-30

## 1. 学习路径（Learning）

### 1.1 最小可运行闭环（建议先跑通 LINUX target）

1. 环境初始化（仓库根目录）
   - `. ./export.sh`（Windows：`. .\\export.ps1`）
   - 目标：完成 `.venv`、`uv sync`、`tos.py prepare`，[AGENTS.md](../../../../../../AGENTS.md#L15-L30)
2. 环境校验
   - `tos.py check`，[AGENTS.md](../../../../../../AGENTS.md#L47-L54)
3. 选择一个示例工程进入并构建
   - `cd examples/<category>/<project>`
   - `tos.py build`，[AGENTS.md](../../../../../../AGENTS.md#L47-L54)
4. 产物认知
   - 中间产物：`<project>/.build/`
   - 最终产物：`<project>/dist/`，[AGENTS.md](../../../../../../AGENTS.md#L84-L88)

### 1.2 第二阶段：固件设备闭环（T 系列 / ESP32）

- 目标：在真实硬件上完成 build → flash → monitor 闭环
- 使用命令：`tos.py flash`、`tos.py monitor`（tos 子命令清单见 `tos.py（.temp/libs/TuyaOpen/tos.py#L33-L47）`）
- 注意：避免在自动化场景使用交互配置命令，优先修改 `app_default.config`，[AGENTS.md](../../../../../../AGENTS.md#L55-L58)

### 1.3 第三阶段：AI 智能体硬件能力区（价值区）

- 目标：将端侧能力与云侧多模态 AI 工作流打通（语音/视觉/传感器/云端控制/OTA）
- 入口：TuyaOpen “系统组成/框架栈”与 AI 能力概述，[README_zh.md](../../../../../../playground/debug/TuyaOpen-dev-skills/README_zh.md#L63-L71)

## 2. 改进建议与行动项（Exportable Action Items）

| 主题 | 改进项 | 优先级 | 预期效果 | 验收标准 |
|---|---|---|---|---|
| 学习 | 固化 3 阶段学习路径（LINUX→硬件→AI能力） | 高 | 新人上手时间可预估 | 能按文档在新环境跑通 LINUX build 并定位 dist |
| 工程 | 补充“非交互构建”最佳实践清单 | 中 | CI/云端跑通率提升 | 文档明确不使用 `config choice/menu` 的替代方式 |
| 安全 | 明确本地凭据与 `.env` 的处理规则 | 中 | 避免密钥泄露与误提交 | 文档列出需要忽略的文件模式与检查点 |

## 3. 导出建议（如何对外输出）

### 3.1 建议导出物清单

- 对外“介绍级”材料：TuyaOpen 的定位、目标平台、典型应用场景（来源：README_zh.md）
- 对内“落地级”材料：环境初始化与构建闭环（来源：AGENTS.md + tos.py）
- 复盘资产：
  - [execution-retrospective.md](execution-retrospective.md)
  - [insight-extraction.md](insight-extraction.md)
  - 本文件（export-suggestions.md）

### 3.2 导出安全检查（必须）

- 不读取、不复制、不外发任何 `.env` / token / 私钥文件内容
- 导出前做一次敏感信息扫描（至少包含：`TUYA_`、`API_KEY`、`token`、`secret` 关键字）
