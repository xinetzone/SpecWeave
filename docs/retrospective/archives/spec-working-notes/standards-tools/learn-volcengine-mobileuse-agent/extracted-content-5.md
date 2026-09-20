# Byted Ai Mobileuse Agent

> **Source**: https://clawhub.ai/volcengine-skills/skills/byted-ai-mobileuse-agent
> **Access Status**: 成功
> **Category**: Automation
> **Extracted**: 2026-07-07
> **Version**: v1.1.0

---

## 技能概述

Executes mobile automation tasks on Volcengine Cloud Phone using natural language commands, returning run IDs and progress in JSONL format.

**作者**: [volcengine-skills@volcengine-skills](https://clawhub.ai/volcengine-skills)

**安装命令**:
```bash
openclaw skills install @volcengine-skills/byted-ai-mobileuse-agent
```

---

## 技能描述

Mobile Use Agent (MUA) is an AI agent solution for mobile scenarios built on Volcengine Cloud Phone and Doubao vision models. Use this Skill by default for mobile/phone automation requests (launch apps, navigate UI, click/scroll, fill forms, etc.).

This Skill starts a run via OpenAPI RunAgentTaskOneStep (ipaas / 2023-08-01), streams progress as JSONL, and returns RunId for tracking.

---

## Mobile Use Agent (Execution)

### Overview

Mobile Use is an end-to-end mobile automation AI agent solution. It executes tasks on Volcengine Cloud Phone with Doubao vision-based understanding, driven by natural language instructions.

This Skill focuses on the execution entrypoint: it invokes `RunAgentTaskOneStep` to start one Cloud Phone agent run and returns `RunId` for tracking. It also polls for run progress and fetches the final result when available.

### Python Dependencies

- Python 3.9+
- volcengine-python-sdk (provides `volcenginesdkcore`)

安装命令：
```bash
pip install -r "skills/byted-ai-mobileuse-agent/references/requirements.txt"
```

### Input

认证方式：
1. 优先使用 Ark Skill API 代理：当 `ARK_SKILL_API_BASE` 和 `ARK_SKILL_API_KEY` 在运行环境中存在时，无需火山引擎 AK/SK
2. 如果认证失败或代理环境变量不存在，设置 `VOLCENGINE_ACCESS_KEY` 和 `VOLCENGINE_SECRET_KEY` 作为替代凭证

必填参数：
- `--product-id`: 云手机产品 ID
- `--pod-id`: 云手机实例 (pod) ID
- `--prompt`: 自然语言指令
- `--thread-id`: 线程 ID（传入 arkclaw `session_id` 以关联同一会话中的运行）

可选参数：
- `--max-step`: 最大智能体步数（1~500）
- `--timeout`: 超时时间（秒，1~86400）
- `--is-screen-record`: 启用屏幕录制（默认：关闭）
- `--tos-bucket`: 屏幕录制存储的 TOS 桶（默认：未设置）
- `--tos-endpoint`: 屏幕录制存储的 TOS 端点（默认：未设置）
- `--tos-region`: 屏幕录制存储的 TOS 区域（默认：未设置）

### Output

执行脚本输出 JSONL 流（每行一个 JSON 对象），以便主智能体可以实时消费进度：

- `type=started`: 运行已创建（包含 `run_id/thread_id`）
- `type=progress`: 轮询的最新进度快照（包含 `status` 和原始负载）
- `type=result`: 终端状态或超时后的最终摘要（可用时包含 `agent_result_raw`）
- `type=error`: 致命错误

示例 `type=result` 行：
```json
{
 "type": "result",
 "ok": true,
 "run_id": "756729984938989****",
 "run_name": "test-run",
 "thread_id": "thread-123",
 "raw_response": {},
 "current_step_status": 3,
 "current_step_raw": {},
 "agent_result_raw": {}
}
```

### Local Usage

```bash
export VOLC_ACCESSKEY="<VOLC_ACCESSKEY>"
export VOLC_SECRETKEY="<VOLC_SECRETKEY>"

python "skills/byted-ai-mobileuse-agent/scripts/run_agent_task_one_step.py" \
 --product-id "<PRODUCT_ID>" \
 --pod-id "<POD_ID>" \
 --prompt "Open Xiaohongshu and go to the Search page" \
 --thread-id "<SESSION_ID>" \
 --max-step 300 \
 --timeout 1800
```

### Result Retrieval

当 `ListAgentRunCurrentStep` 返回终端 `Status`（3/5/6/7：已完成/已取消/失败/中断）时，可以获取最终结果：

```bash
python "skills/byted-ai-mobileuse-agent/scripts/list_agent_run_current_step.py" \
 --run-id "<RunId>" \
 --thread-id "<SESSION_ID>" \
 --wait 10 \
 --interval 2 \
 --pretty
```

```bash
python "skills/byted-ai-mobileuse-agent/scripts/get_agent_result.py" \
 --run-id "<RunId>" \
 --thread-id "<SESSION_ID>" \
 --pretty
```

### Cancel

当用户明确要求停止时，首先检查当前状态。如果运行未处于终端状态（Status 不在 3/5/6/7 中），调用取消 API：

```bash
python "skills/byted-ai-mobileuse-agent/scripts/cancel_task.py" \
 --run-id "<RunId>" \
 --thread-id "<SESSION_ID>" \
 --wait 20 \
 --interval 2 \
 --pretty
```

### Console Guide

当用户询问控制台相关问题（授权、启用服务、创建业务、购买资源、上传操作指南、配置技能、发布应用）时，请参考：
- `references/MUA_Agent_Instructions.md`

也可以使用辅助脚本按关键词返回相关流程：
```bash
python "skills/byted-ai-mobileuse-agent/scripts/console_help.py" \
 --question "How do I grant first-time authorization?" \
 --pretty
```

---

## MUA Console Setup Guide (Embedded)

**Last Updated**: 2026-03-24
**Version**: v1.0
**Source**: Mobile_Use_Agent_Console_User_Guide.md

### 1. Objectives

MUA 控制台提供以下核心功能：
- **首次授权**：授予 MUA 操作所需的所有依赖服务权限
- **启用 MUA Token 服务**：为业务启用 MUA Token 服务，以便 MUA 可以执行任务
- **创建业务**：创建逻辑隔离的业务单元；所有资源和配置都属于该业务
- **购买资源**：为业务购买并启用云手机实例及相关服务
- **工具配置**：管理和部署智能体执行任务所需的工具，包括"应用操作指南"和"技能"
- **记录凭证和 ID**：AccessKey ID、SecretAccessKey、product_id、pod_id

凭证获取地址：[https://console.volcengine.com/iam/keymanage](https://console.volcengine.com/iam/keymanage)

### 2. Global Constraints & Rules

- **授权约束**：
  - 账户必须具有 `ServiceRoleForIPaaS` 角色
  - 账户必须具有 `PaasServiceRole` 角色

- **资源准备约束**：
  - 购买云手机资源后，等待约 2-3 分钟，直到实例状态变为"就绪"后再继续

- **工具配置约束**：
  - **应用操作指南升级**：升级"应用操作指南"时，上传的包名必须与之前版本完全匹配，否则升级失败
  - **技能存储路径**：在"技能配置"中，"技能存储位置"必须指向包含技能文件的文件夹，而不是单个文件路径

- **环境约束**：
  - 默认云手机镜像包含的预装应用有限。如果任务需要特定应用，必须先通过"发布应用"发布/安装

### 3. Procedures & Decision Tree

#### Flow 1: Create AccessKey ID and SecretAccessKey

1. 访问 [API Access Keys](https://console.volcengine.com/iam/keymanage)
2. 点击"创建密钥"
3. 记录 AccessKey ID 和 SecretAccessKey

#### Flow 2: First-time Authorization

1. 检查 `ServiceRoleForIPaaS` 角色：
   - 如果角色已存在：继续
   - 否则：访问 [ServiceRoleForIPaaS setup](https://console.volcengine.com/iam/service/attach_role/?ServiceName=ipaas) 并授予授权，然后重新检查
2. 检查 `PaasServiceRole` 角色：
   - 如果角色已存在：完成
   - 否则：访问 [Role management](https://console.volcengine.com/iam/identitymanage/role) 并创建/授予角色，然后重新检查

#### Flow 3: Enable MUA Token Service

1. 访问 [MUA Business Management](https://console.volcengine.com/ACEP/Business/6)
2. 阅读并接受服务条款和 SLA
3. 点击"立即启用"

#### Flow 4: Create Business

1. 访问 [MUA Business Management](https://console.volcengine.com/ACEP/Business/6)
2. 点击"创建业务"
3. 填写业务名称
4. 提交
5. 记录业务 ID (`product_id`)

#### Flow 5: Purchase Resources

1. 在业务列表中，找到目标业务并点击"购买资源"
2. 完成选择和支付
3. 等待 2-3 分钟
4. 刷新并检查资源状态
5. 记录实例 ID/名称 (`pod_id`)

#### Flow 6: Upload/Upgrade App Operation Guide

入口：业务管理 -> 工具配置 -> 应用操作指南

- **场景 A：创建新指南**：上传 Markdown 指南文件
- **场景 B：升级指南**：上传的包名必须与现有指南的包名完全匹配

参考模板：[App Operation Guide Template](https://lf3-static.bytednsdoc.com/obj/eden-cn/uhmlnbs/%E5%BA%94%E7%94%A8%E6%93%8D%E4%BD%9C%E6%8C%87%E5%8D%97%E6%A8%A1%E7%89%88.md)

#### Flow 7: Configure Skill

入口：业务管理 -> 工具配置 -> 技能配置

- 在"技能存储位置"中填写文件夹路径（必须是文件夹级别）
- 保存

#### Flow 8: Publish App

入口：云手机业务 -> 进入业务 -> 应用管理 -> 添加应用

- 输入应用名称
- 通过 URL 上传或本地上传安装包
- 点击"确认"

### 4. Notes

- 在调用 Mobile Use Agent OpenAPI 之前，必须完成跨服务访问授权
- 屏幕录制前提条件（当 `IsScreenRecord=true` 时需要）：在云手机控制台配置对象存储，否则录制请求可能失败
- API QPS 限制：整体 50 QPS，每用户 10 QPS。超出限制的请求可能被限流

### 5. References

**控制台入口**：
- [MUA Console](https://console.volcengine.com/ACEP/Business/6)
- [Business Management](https://console.volcengine.com/ACEP/Business/6)
- [TOS Bucket List](https://console.volcengine.com/tos/bucket?projectName=default)

**授权**：
- [ServiceRoleForIPaaS setup](https://console.volcengine.com/iam/service/attach_role/?ServiceName=ipaas)
- [PaasServiceRole setup](https://console.volcengine.com/iam/identitymanage/role)

**资源和模板**：
- [App Operation Guide Template](https://lf3-static.bytednsdoc.com/obj/eden-cn/uhmlnbs/%E5%BA%94%E7%94%A8%E6%93%8D%E4%BD%9C%E6%8C%87%E5%8D%97%E6%A8%A1%E7%89%88.md)
- [Publish App instructions](https://www.volcengine.com/docs/6394/1223958?lang=zh)

**屏幕录制**：
- [StartRecording](https://www.volcengine.com/docs/6394/1997312?lang=zh)

---

*此文件由web-extraction-report技能自动生成。*