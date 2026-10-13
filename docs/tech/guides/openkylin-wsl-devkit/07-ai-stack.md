---
type: "Tutorial"
title: "okw AI 栈：本地 OCR 预检、安装与验收"
source: "../../../../docs/knowledge/tech/openkylin-docs-wiki/concepts/05-ai-stack.md"
---

# okw AI 栈：本地 OCR 预检、安装与验收

`okw ai` 把 openKylin AI 栈中**唯一完成落机 POC** 的能力封装为 CLI：Gen1 Kylin AI SDK 的文字识别（OCR）。本文说明它能做什么、为什么只做这一条路径，以及如何用 `preflight → install → verify` 三步在 WSL 发行版内获得离线 OCR。

## 背景：AI 三层体系与两代 SDK

openKylin 文档把 AI 内容分成三层：用户使用（模型管理工具、ollama、AI 编程助手）、模型接入配置（云端/局域网/本地三类来源）、开发者 SDK。应用侧 SDK 实际有两代互不从属的供给线：

| | Gen1 Kylin AI SDK | Gen2 kysdk |
|---|---|---|
| 代表包 | `libkylin-ai-base2` / `-dev` 2.0 | `libkysdk-genai-nlp0` 等 1.1 |
| OCR 本地后端 | tesseract 5.3.4（`chi_sim+eng`），CPU 离线 | —— |
| 形态 | OCR 为同步 C ABI（头文件 C++ 友好） | 全异步 IPC 薄代理，经 D-Bus 转发 runtime |
| 验证状态 | **OCR 已落机实测** | 客户端出厂预装，引擎插件/模型缺省，端到端未验证 |

Gen1 OCR 的本地后端经 `ldd` 直链 libtesseract、`gsettings` 权威值、tesseract CLI **三源钉死**为本地 tesseract CPU 离线：无云密钥、不依赖网络/GPU/大模型。识别可用但**精度中等**，存在形近误识（如 `Kylin→Kvylin`、`麒麟→户有`），不是高准确率商用 OCR。

> **先确认 `<name>`**：下文命令中的 `<name>` 是目标 WSL 发行版名称。先在 PowerShell 运行 `wsl -l -v` 查看本机发行版及其 `NAME`（本文实测机为 `openKylin-3.0-desktop`），把该名称原样填入；发行版需为 openKylin（`/etc/os-release` 的 `ID=openkylin`）。

## 第一步：只读预检

```text
okw ai preflight <name>
```

预检盘点 WSL2/openKylin/dpkg/apt 结构，再用**单条批量** `apt-cache policy` 查询 11 个组件的已装/候选版本：

- **必选 5 项**（决定门控）：`libkylin-ai-base-dev`、`libkylin-ai-base2`、`tesseract-ocr`、`tesseract-ocr-chi-sim`、`tesseract-ocr-eng`；
- **可选 6 项**（仅信息展示）：`kylin-ai-model-manager`、`libkysdk-genai-nlp0`、`kylin-ai-engine-plugins`、`kylin-ondevice-nlp-engine`、`kytensor-server`、`ollama`。

可选层缺失显示 `[UNKNOWN]` 但**不影响退出码**——例如 ollama 永不入官方源，若让它参与门控，预检将永远无法返回 0。退出码：`0` 必选项就绪 / `1` 有 FAIL（结构破损、网络错误、必选包无候选）/ `2` 必选项仅 UNKNOWN（多为索引过期，按提示 `sudo apt update`）。

## 第二步：显式安装

```text
okw ai install <name> --yes
```

`--yes` 后以 root 依次执行：

1. `apt update` 刷新索引；
2. 复查直接包 `libkylin-ai-base-dev` 候选；
3. `apt install -y --no-install-recommends libkylin-ai-base-dev`——由 APT 经 Depends 拉入 `libkylin-ai-base2`、`kylin-ai-runtime`、`libkylin-ai-document-qa-service`，并解析 `tesseract-ocr` 与 `chi_sim/eng` 语言包；
4. 事后只读 OCR 验收。

漏 `--yes` 时只打印副作用清单、以退出码 2 中止，**零写入**。POC 实测该直接包由 huanghe 官方源提供，安装即得 tesseract 5.3.4（`chi_sim/eng/osd`）。

## 第三步：只读验收与离线冒烟

```text
okw ai verify <name>
okw ai verify <name> --smoke-ocr /tmp/sample.png
```

`verify` 用 `dpkg-query` 确认 SDK/运行库已装，用 `tesseract --version` 与 `--list-langs` 权威确认引擎版本与语言；可选层缺失仅 UNKNOWN 不阻断。

`--smoke-ocr` 对一张**本地图片**执行一次离线识别（`tesseract <图片> stdout -l chi_sim+eng`）：

- 发行版内绝对路径（`/tmp/sample.png`）原样使用；
- Windows 盘符路径（`C:\Users\me\sample.png`）自动转换为 `/mnt/c/Users/me/sample.png`；
- 图片不存在、或识别结果为空记 FAIL；前置已有 FAIL 时跳过冒烟。

默认（不带 `--smoke-ocr`）不执行任何识别，保证验收只读、离线。

## 明确不做（Non-Goals）

okw 刻意不覆盖以下内容，需要时请按知识库手动操作：

| 能力 | 现状 | 手动路径 |
|---|---|---|
| API Key / 云端模型 | 敏感凭据，okw 不配置 | 见 05-ai-stack §5.2 分版配置指南 |
| 模型下载 | okw 不下载任何模型 | `kylin-ai-model-manager`（上游自述不完善） |
| ollama | 不在官方源，okw 不执行 `curl|sh` | 官方 `install.sh` 或 GitHub release |
| Gen2 全栈 / 本地 NLP | 引擎插件、模型仓库、自备 GGUF 缺省，端到端未验证 | `kylin-ai-engine-plugins` + `kylin-ondevice-nlp-engine` + kytensor + GGUF |
| 推理服务 | okw 不启动 kytensor/Triton | 另行准备模型仓库 |

## 证据与口径

- 事实来源：知识库 [05 AI 三层体系](../../../knowledge/tech/openkylin-docs-wiki/concepts/05-ai-stack.md)、[OCR 落机 POC](../../../knowledge/tech/openkylin-docs-wiki/references/ai-sdk-ocr-poc.md)、[AI 子系统源码架构剖析](../../../knowledge/tech/openkylin-docs-wiki/references/ai-subsystem-source-architecture.md)。
- OCR 路径为 2026-10-08 在 openKylin-3.0-desktop WSL（huanghe）实测；其余能力域仍为「成文未验证」，生产采用前应各自做最小 POC。
- okw 自身零第三方运行时依赖，AI 命令仅用标准库与本包模块；不修改软件源、不写 `wsl.conf`、不改默认发行版。
