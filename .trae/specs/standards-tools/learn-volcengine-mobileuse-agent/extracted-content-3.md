# 云手机快速部署OpenClaw，集成飞书AI助手

> **Source**: https://www.volcengine.com/docs/6394/2227834
> **Access Status**: 成功（内容截断）
> **Extracted**: 2026-07-07

---

## 文档概述

本文主要介绍如何在火山引擎云手机上完成OpenClaw部署与飞书机器人对接，搭建可交互、可执行任务的个人AI助手。

---

## 发布动态

| 更新时间 | 说明 |
|---|---|
| 2026年03月10日 | OpenClaw升级到了3月2日的版本。 |
|  | 修复图片识别报错问题。 |
|  | 支持火山方舟Coding Plan。 |

---

## 使用场景

- **批量账号运营与自动化流程执行**：提供账号运营与自动化流程执行，如内容分发、任务调度、标准化操作流程等，有效降低重复操作成本。
- **AI智能客服自动响应**：作为AI客服助手，可实现消息自动回复与智能咨询处理，提升咨询响应速度与服务效率。
- **日常工作流智能协同**：深度集成日常工作流程，实现文档生成、任务提醒、待办事项实时推送，全面提升日常工作与生活效率。

---

## 背景信息

OpenClaw是一款开源、本地优先的AI代理与自动化平台，通过OpenClaw，可将飞书通信能力与大语言模型深度集成，构建具备持久记忆与主动执行能力的定制化AI助手，该助手可通过模拟人工操作各类应用，成为您的云端手机与贴身智能助理。

---

## 支持的实例规格

云盘存储类型业务以实例为资源订购单位，即一个实例对应一台云手机，每台实例可模拟完整的Android手机环境，具备独立的操作系统、应用运行环境及虚拟硬件配置（虚拟 CPU、内存、存储）。

| 实例规格 | vCPU核数（vCPU） | 内存（GB） | 支持的Android系统版本 |
|---|---|---|---|
| g3.8c24g单开 | 8 | 24 | AOSP13 |
| g3.8c24g双开 | 4 | 12 |  |
| g3.8c24g三开 | 3 | 8 |  |

---

## 部署步骤

### 步骤一：订购资源与创建实例

在云手机控制台购买资源并创建符合OpenClaw部署要求的实例，搭建火山引擎云手机运行环境。

#### 一、订购资源

1. 登录[云手机控制台](https://console.volcengine.com/ACEP/)
2. 创建云手机业务（若已有云盘存储业务可跳过）
3. 业务名称：OpenClaw
4. 存储方案：云盘存储（仅支持）
5. 购买资源：
   - 地域：国内通用
   - 计费方式：后付费
   - 区域：华东（OpenClaw暂仅支持）
   - 可用区/机房：指定机房-浙江温州三线03-ppe
   - 实例规格：g3.8c24g三开（3vCPU｜8GB内存）

#### 二、创建云手机实例

1. 在左侧导航树，选择「实例管理 > 实例列表」
2. 单击「创建实例」按钮，配置参数：
   - 实例存储：不低于32GB
   - 实例镜像：公共镜像/img-1080115458（必须选择此镜像）
   - 自动开机：勾选创建后开机

---

### 步骤二：开通火山方舟大模型并获取配置

1. 登录[开通管理页面](https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement?LLM=%7B%7D&advancedActiveKey=model)
2. 选择支持GUI能力的模型，建议使用Doubao-seed-1.8
3. 在「系统管理 > API Key管理」，创建并获取API Key

---

### 步骤三：创建飞书机器人应用并获取配置

1. 创建企业自建应用：登录[飞书开发者平台](https://open.larkoffice.com/app?lang=zh-CN)
2. 添加机器人能力
3. 配置权限（批量导入权限JSON）：
```json
{
"scopes": {
"tenant": [
"im:chat:read",
"im:chat:update",
"im:message.group_at_msg:readonly",
"im:message.p2p_msg:readonly",
"im:message.pins:read",
"im:message.pins:write_only",
"im:message.reactions:read",
"im:message.reactions:write_only",
"im:message:readonly",
"im:message:recall",
"im:message:send_as_bot",
"im:message:send_multi_users",
"im:message:send_sys_msg",
"im:message:update",
"im:resource",
"contact:contact.base:readonly"
],
"user": [
"contact:user.employee_id:readonly"
]
}
}
```
4. 获取App ID与App Secret
5. 发布应用

---

### 步骤四：初始化OpenClaw

1. 登录云手机控制台，连接云手机
2. 在实例详情页面，单击「终端」按钮
3. 执行命令：`config_openclaw`
4. 选择Service Provider：
   - ark：火山引擎方舟大模型平台
   - volcengine-plan：火山引擎Coding Plan（订阅服务）

配置参数说明：

**ark模式：**
| 参数 | 说明 | 示例 |
|---|---|---|
| Enter models id | 模型ID | doubao-seed-1-8-251228 |
| Enter apiKey | API Key | e615c7a1-dab3-40fa-af54-d4**** |
| Enter Feishu appId | 飞书App ID | cli_a92bfb97be3**** |
| Enter Feishu appSecret | 飞书App Secret | 2oGtsZDR083GMvWfPIbLFcy**** |
| Enter Feishu botName | 机器人名称 | My OpenClaw Bot |
| Enable Feishu? | 启用飞书 | true |

**volcengine-plan模式：**
| 参数 | 说明 | 示例 |
|---|---|---|
| Enter models id | 模型ID（推荐doubao-seed-2.0-code） | doubao-seed-2.0-code |
| Enter apiKey | API Key | e615c7a1-dab3-40fa-af54-d4**** |
| Enter Feishu appId | 飞书App ID | cli_a92bfb97be3**** |
| Enter Feishu appSecret | 飞书App Secret | 2oGtsZDR083GMvWfPIbLFcy**** |
| Enter Feishu botName | 机器人名称 | My OpenClaw Bot |
| Enable Feishu? | 启用飞书 | true |

5. 验证Web UI：
   - 执行命令：`openclaw dashboard`获取Dashboard URL
   - 在云手机中打开Via浏览器访问该URL
   - 验证可正常对话并生成内容

---

### 步骤五：配置OpenClaw飞书AI助手（部分内容）

1. 登录[飞书开发者平台](https://open.larkoffice.com/app?lang=zh-CN)
2. 选择创建的飞书机器人应用
3. 在「开发配置 > 事件与回调」进行配置：
   - 事件配置：选择「使用长连接接收事件」
   - 添加事件：勾选「接收消息」及其它需要订阅的事件

---

⚠️ **注意**：本文档内容在提取时被截断，后续步骤未完整获取。

---

*此文件由web-extraction-report技能自动生成。*