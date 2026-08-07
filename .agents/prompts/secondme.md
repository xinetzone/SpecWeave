---
id: "secondme"
title: "SecondMe 交互提示词模板"
source: "chaos/flexloop/prompts/secondme.md"
---

# SecondMe 交互提示词模板

> 本模板用于指导与 SecondMe 平台相关的 Skill 接入、联调与信息提交任务。
> 使用时请依据 SecondMe 官方文档（默认入口：`https://develop.second.me/skill.md`，如平台地址变化请以实际官方地址为准）中定义的 Skill 规范执行。
> 凡涉及密钥、凭证、账号、路径等敏感信息，一律以占位符标注，严禁写入真实值。

请根据 SecondMe 官方文档中定义的 Skill 规范，完成以下任务：

## 1. 安装该 Skill
在本地开发环境（或指定部署环境）中正确集成该 Skill，确保其符合 SecondMe 平台对 Skill 的以下要求：

- **结构**：遵循平台规定的目录/文件组织方式；
- **接口**：实现平台约定的对外接口；
- **元数据**：正确编写清单文件（如 `manifest.yml` 或 `skill.json`，以文档实际规定为准）；
- **权限声明**：明确声明 Skill 所需的权限范围；
- **生命周期钩子**：实现平台要求的生命周期钩子（如 `install` / `uninstall` / `activate` / `deactivate`）。

## 2. 联调对接
配置并启动与 SecondMe 平台的双向通信，包括但不限于：

- **注册与认证**：正确注册 Skill ID 并与平台完成认证（认证机制如 OAuth2 / JWT / API Key 等，请依据官方文档明确的具体机制实施；相关密钥与凭证一律使用占位符 `{{SECRET}}`，不得写入真实值）；
- **Webhook 回调端点**：实现平台要求的回调端点（如 `/webhook`），支持接收 `skill_event`（如 `user_connected`、`task_started`）并返回符合 schema 的响应；
- **通信安全校验**：验证平台下发的签名/加密字段（如 `x-secondme-signature`），确保通信安全性。

## 3. 信息提交
按文档要求，向 SecondMe 平台提交完整且合规的 Skill 信息包，包括：

- **代码包**：最终可运行的代码包（含依赖声明）；
- **功能说明**：清晰的功能说明、使用场景与用户授权范围说明；
- **测试凭证**：测试账号（以 `{{TEST_ACCOUNT}}` 占位）、模拟事件 payload 示例（以 `{{EVENT_PAYLOAD_EXAMPLE}}` 占位）及联调成功日志截图（以 `{{LOG_SCREENSHOT_PATH}}` 占位）；
- **合规声明**：符合平台审核要求的隐私政策与数据处理声明（如涉及用户数据采集）。

## 交付要求
全程需提供：

- 分步操作指南；
- 关键命令/配置片段（涉及密钥/路径处使用占位符）；
- 常见错误排查提示；

并确认每一步均通过 SecondMe 官方联调工具或沙箱环境验证。

## 占位符约定
| 占位符 | 含义 |
|---|---|
| `{{SECRET}}` | 各类密钥/令牌（OAuth2 Client Secret、JWT 密钥、API Key 等） |
| `{{TEST_ACCOUNT}}` | 测试账号 |
| `{{EVENT_PAYLOAD_EXAMPLE}}` | 模拟事件 payload 示例 |
| `{{LOG_SCREENSHOT_PATH}}` | 联调成功日志截图路径 |
| `{{DEPLOY_ENV}}` | 部署环境（本地/指定环境） |
