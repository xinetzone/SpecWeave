---
id: seven-concepts-deeptutor-02-quickstart
title: DeepTutor快速开始
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [DeepTutor, 快速开始, 实践]
---

# DeepTutor快速开始

本章介绍DeepTutor的三种部署和使用方式：PyPI安装、Docker部署、CLI-only模式。

---

## PyPI安装（5分钟跑起来）

DeepTutor提供PyPI安装方式，五分钟即可跑起来。

> 我实际用的是PyPI安装，五分钟跑起来。
>
> ——§3.0 PyPI安装

安装步骤如下：

```bash
mkdir my-deeptutor && cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

### 初始化配置

> deeptutor init会提示选端口、LLM提供商、API key和embedding模型，默认前端跑在3782端口，后端在8001。
>
> ——§3.0.1 初始化配置

运行`deeptutor init`时，系统会交互式提示配置以下选项：
- **端口**：服务端口设置
- **LLM提供商**：选择使用的大语言模型提供商
- **API key**：对应的API密钥
- **embedding模型**：嵌入模型选择

默认端口配置：
- 前端：**3782端口**
- 后端：**8001端口**

---

## Docker部署

DeepTutor提供官方Docker镜像，挂个卷就能跑，配置和知识库不会丢。

> Docker也有官方镜像，ghcr.io/hkuds/deeptutor:latest，挂个卷就能跑，配置和知识库不会丢。
>
> ——§3.1 Docker部署

### 基本部署命令

```bash
docker run --rm --name deeptutor \
  -p 127.0.0.1:3782:3782 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

### 端口说明

> 只暴露3782就行，Next.js中间件在容器内部转发API和WebSocket。
>
> ——§3.1.1 端口说明

Docker部署时只需要暴露**3782端口**即可。Next.js中间件会在容器内部负责转发API请求和WebSocket连接，不需要额外暴露后端端口。

### 连接本地模型

> 本地Ollama或LM Studio的用户，Docker里连host服务要加 `--add-host=host.docker.internal:host-gateway` ，然后在Settings里把Base URL指向 `http://host.docker.internal:11434/v1` 。
>
> ——§3.1.2 本地模型连接

如果要在Docker容器中连接宿主机上运行的Ollama或LM Studio，需要注意两点：

1. 运行Docker时添加host映射参数：
   ```
   --add-host=host.docker.internal:host-gateway
   ```

2. 在Settings中配置Base URL指向：
   ```
   http://host.docker.internal:11434/v1
   ```

---

## CLI-only模式

除了Web界面，DeepTutor还提供CLI-only模式，可以直接在命令行中使用。

> CLI-only模式也有， `deeptutor chat` 进交互式REPL， `deeptutor kb create` 建知识库， `deeptutor memory show` 看记忆状态。
>
> ——§3.2 CLI模式

可用的CLI命令：

| 命令 | 功能 |
|------|------|
| `deeptutor chat` | 进入交互式REPL对话环境 |
| `deeptutor kb create` | 创建知识库 |
| `deeptutor memory show` | 查看记忆状态 |

---

**上一章**：[Memory + Settings](02-modules/04-memory-settings.md) ｜ **下一章**：[优缺点评价](04-pros-cons.md)
