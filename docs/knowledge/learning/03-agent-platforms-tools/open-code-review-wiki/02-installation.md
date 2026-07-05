---
id: "open-code-review-wiki-02"
title: "安装与配置指南"
source: "../open-code-review-wiki.md#安装与配置指南"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/open-code-review-wiki/02-installation.toml"
---

# 安装与配置指南

Open Code Review 是一款基于 Go 语言构建的 AI 驱动代码评审 CLI 工具，通过 npm 进行分发安装。本章介绍如何完成工具安装、LLM 配置以及基础验证，帮助你快速进入可用状态。

## 通过 npm 安装

Open Code Review 通过 npm 全局安装，安装后 `ocr` 命令即可在任意目录下使用。

执行以下命令完成全局安装：

```bash
npm install -g @alibaba-group/open-code-review
```

### 验证安装

安装完成后，通过 `version` 子命令验证安装是否成功：

```bash
# 验证版本
ocr version
```

如果终端正确打印出当前 `ocr` 的版本号，说明安装成功，`ocr` 命令已全局可用。

## 配置 LLM

Open Code Review 的代码评审能力依赖于大语言模型（LLM）。**在审查代码之前，必须先配置 LLM**，否则评审任务无法执行。

### 基础配置流程

通过 `ocr config` 命令完成两步配置：

```bash
ocr config provider          # 选择内置供应商或添加自定义供应商
ocr config model             # 为当前供应商选择模型
```

1. **配置供应商（provider）**：交互式选择一个内置的 LLM 供应商，或添加一个自定义供应商
2. **配置模型（model）**：为当前选定的供应商选择具体的模型

配置完成后，相关信息会被持久化保存，后续评审任务会自动读取该配置，无需重复配置。

### 配置自定义供应商

如果内置供应商列表中没有你需要的选项，可以通过 `ocr config provider` 命令添加自定义供应商。自定义供应商需要提供以下信息：

- **服务端点（LLM URL）**：模型服务的 API 地址
- **鉴权凭证（Auth Token）**：访问模型服务所需的认证 token
- **模型名称（Model）**：要调用的具体模型标识

在 CI/CD 等自动化场景中，也可以通过环境变量注入这些配置，避免在脚本中硬编码敏感信息：

- `OCR_LLM_URL`：模型服务端点
- `OCR_LLM_AUTH_TOKEN`：鉴权 token
- `OCR_LLM_MODEL`：模型名称

## 验证安装与配置

完成安装和 LLM 配置后，可以通过以下方式验证整体可用性：

1. **验证 CLI 安装**：执行 `ocr version`，确认版本号正常输出
2. **验证 LLM 配置**：在任意 Git 仓库中执行一次评审命令，确认能够正常调用模型并返回评审结果

```bash
# 在 Git 仓库中执行一次评审（工作区模式）
ocr review
```

如果命令能够正常执行并输出评审结果，说明安装与配置均已完成。

## 注意事项

- **全局可用**：通过 `npm install -g` 全局安装后，`ocr` 命令即可在系统任意目录下使用，无需切换到特定工作目录
- **必须先配置 LLM**：在审查代码之前，必须先通过 `ocr config provider` 和 `ocr config model` 完成 LLM 配置，否则评审任务无法启动
- **Git 仓库即用**：LLM 配置完成后，在任意 Git 仓库中即可开始评审。Open Code Review 支持工作区模式（评审暂存、未暂存和未追踪的变更）、分支对比模式、单次提交模式等多种评审场景，详见后续章节
