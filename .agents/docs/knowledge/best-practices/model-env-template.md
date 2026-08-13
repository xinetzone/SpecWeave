---
id: model-env-template
title: 模型调用环境变量脱敏模板（.env 字段清单）
category: best-practices
tags: ["env", "environment-variable", "desensitization", "glm", "huggingface", "zai"]
date: "2026-08-07"
last_updated: "2026-08-07"
status: active
author: flexloop 沉淀
summary: 从 chaos/flexloop/models/.env 沉淀的脱敏环境变量模板：列出字段名与用途说明，所有值一律使用占位符，绝不含真实密钥或个人路径。
security_level: "public"
knowledge_type: "procedural"
validation_status: "verified"
reuse_count: "0"
integrity: "unchecked"
---

# 模型调用环境变量脱敏模板

> 一句话摘要：GLM 模型调用所需的 `.env` 字段清单与脱敏占位符模板，所有值必须用占位符表示，严禁写入真实密钥。

---

## 1. 概述

本条目沉淀自 `d:\spaces\chaos\flexloop\models\.env`，提供模型调用场景下的环境变量字段模板。**本模板只列出字段名与用途说明，所有值一律使用占位符（如 `<API_KEY>`、`<MODEL_PATH>`、`%USERPROFILE%` 等），绝不包含任何真实密钥、Token 或个人路径。**

---

## 2. .env 字段清单（脱敏模板）

```env
# Hugging Face Token（可选，本地模型联网下载/鉴权用）
HF_TOKEN=<API_KEY>

# Z.AI 云端 API Key（API 调用方式必需）
ZAI_API_KEY=<API_KEY>
```

### 字段说明

| 字段名 | 用途 | 是否必需 | 占位符示例 |
|--------|------|----------|------------|
| `HF_TOKEN` | Hugging Face 访问令牌，用于本地模型联网下载或鉴权 | 可选 | `<API_KEY>` |
| `ZAI_API_KEY` | Z.AI 云端 API 密钥，用于 zai-sdk API 调用 | 必需（API 方式） | `<API_KEY>` |

> 补充：本地模型加载方式还涉及模型路径配置（源码中通过变量 `model_path` 传入），该路径同样应使用占位符 `<MODEL_PATH>` 表示，如 `%USERPROFILE%\path\to\models\GLM-5.1`，不得写入真实用户目录。

---

## 3. 代码读取方式（脱敏规范）

环境变量一律通过 `python-dotenv` 读取，**严禁在源码中硬编码密钥**：

```python
import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')          # 可选
ZAI_API_KEY = os.getenv('ZAI_API_KEY')    # API 调用必需
```

---

## 4. 脱敏占位符规范

| 场景 | 推荐占位符 | 反例 |
|------|------------|------|
| API Key / Token | `<API_KEY>` | 真实密钥串 |
| 模型路径 | `<MODEL_PATH>` | 含真实用户名的绝对路径 |
| 用户主目录（Windows） | `%USERPROFILE%\` | `C:\Users\<真实用户名>\` |
| 用户主目录（Unix） | `~/` 或 `$HOME/` | `/home/<真实用户名>/` |

> 规则：仓库内任何文档、脚本、配置文件中不得出现真实密钥或真实个人路径；一律使用占位符替代。

---

## 5. 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-08-07 | 初始沉淀：从 chaos/flexloop/models/.env 萃取字段清单（HF_TOKEN、ZAI_API_KEY），全部值脱敏为占位符 |
