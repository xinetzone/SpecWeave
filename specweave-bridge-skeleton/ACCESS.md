---
name: specweave-bridge-access
description: Hermes 使用者接入 specweave-bridge 插件的完整指南（零配置接入、交互式接入、Agent 自主接入）
---

# Hermes 使用者接入指南

`specweave-bridge` 是 Hermes Agent 的 SpecWeave 工作区规范集成插件。本文档说明 **Hermes 使用者如何接入**。

## 前提

- Hermes 已安装
- 插件已部署至 `<HERMES_HOME>/plugins/specweave-bridge/`
- `config.yaml` 的 `plugins.enabled` 包含 `specweave-bridge`
- 已重启 Hermes 会话

## 接入方式总览

| 层级 | 使用者 | 入口 | 适用诉求 |
|------|--------|------|---------|
| 零配置 | 所有用户 | `pre_llm_call` hook | 默认生效，无需任何操作 |
| 交互式 | 人 | `/specweave` 斜杠命令、`hermes specweave` CLI | 查询状态 / 路由 |
| Agent 自主 | Hermes Agent | `specweave_route` / `specweave_check` 工具 | 规范感知 / CI 校验 |

> **核心机制**：接入是**目录感知**的——取决于当前工作目录（cwd）是否在 SpecWeave 工作区内（存在含「启动协议」关键词的 `AGENTS.md`）。换目录后能力自动切换。

## 第 1 步：零配置接入（默认生效）

在 SpecWeave 工作区（如 `SpecWeave/` 根目录）下启动 Hermes 会话即可，无需任何配置。

每次调用前 `pre_llm_call` 会向**用户消息层**注入一段「启动协议」brief，Hermes 据此按 SpecWeave 规范路由与执行。注入不污染 system prompt，保留 prompt cache。

**检验**：会话上下文出现「[SpecWeave 启动协议]」标记。

## 第 2 步：交互式接入（人用）

会话中输入：

```
/specweave status        # 查看当前工作区与子区域
/specweave route 复盘    # 查询任务对应规范路径
/specweave help          # 帮助
```

终端中：

```
hermes specweave status
hermes specweave route Mermaid
```

## 第 3 步：Agent 自主接入（Hermes Agent 用）

Hermes 在对话中自动调用：

- `specweave_route <task>`：任务类型 → 规范路径（支持 apps/projects/vendor 子区域路由，无匹配回退 `.agents/context-routing.md`）
- `specweave_check <script>`：运行 `.agents/scripts/` 下验证脚本（服务门控，非工作区不派发）

## 反模式（避免）

1. **换目录仍期待规范生效** —— 工具是目录感知的，离开 SpecWeave 工作区自动失效（预期行为，非 Bug）。
2. **手动记忆规范路径** —— 应交由 `specweave_route`，避免路径漂移。
3. **直接修改 Hermes 核心** —— 遵循 Footprint Ladder，只用插件/技能叠加，保持核心纯净。

## 检验标准

```powershell
$env:HERMES_HOME = "C:\Users\admin\.hermes"
hermes plugins list --plain --no-bundled   # specweave-bridge = enabled/user
hermes specweave status                    # 能识别当前工作区与子区域
```

`hermes specweave status` 能识别当前工作区 → 接入成功。
