# apps/ -- 应用开发工作空间

> **AI 智能体入口**：[AGENTS.md](AGENTS.md) — apps 区域智能体路由与资产索引，.agents/ 目录为元数据容器。

## 一、用途与定位

`apps/` 目录是本项目中**新应用的专用开发工作空间**，用于存放独立应用程序的源代码、资源文件与相关配置。每个应用在此目录下拥有独立的子目录，享有完整的生命周期管理。

本目录与项目中其他顶级目录职责分离，各司其职：

| 目录 | 职责 |
|---|---|
| `apps/` | 应用开发工作空间，存放独立应用的代码与资源（含 prompt_extraction/ 提示词萃取系统） |
| `.agents/` | AI 智能体规范，定义角色、协议、工作流与提示词 |
| `docs/` | 项目级文档中心（OKF v0.2），包含知识库、复盘报告、模式库、技术参考与开发标准（面向外部读者的公共文档站点） |

上述三个目录之间不相互包含，各自的文件与职责边界清晰，避免职责重叠。

## 二、子目录结构及职责

### 2.1 分组结构

apps/ 下的应用按**应用类型**分组存放，便于定位与扩展：

```
apps/
├── AGENTS.md              ← apps 区域入口路由
├── README.md              ← 本文件（目录总览）
├── .agents/               ← 区域元数据容器
├── shared/                ← 跨应用共享资源
├── tests/                 ← 全局测试用例
├── docker-images/         ← 容器镜像类应用（7 个）
├── ai-agents/             ← AI 应用类（3 个）
├── dev-tools/             ← 开发工具类（2 个）
└── samples/               ← 示例/原型类（3 个）
```

分组规则：

- **docker-images/**：以 Docker 镜像形态交付的基础设施/运行时应用
- **ai-agents/**：AI 智能体/AI 应用（Agent、代码助手、AI 洞察项目）
- **dev-tools/**：开发者工具类（硬件控制、提示词萃取等实用工具）
- **samples/**：示例框架、Demo 站点、原型项目

> 应用目录名保持唯一且在 apps/ 全区域内唯一；新增应用时先按应用类型判定所属分组，再放入对应子文件夹。

### 2.2 应用独立目录

每个应用在分组下的 `apps/<group>/<app-name>/` 独立存放，享有完整的目录自治权。典型结构如下：

```
apps/<group>/<app-name>/
  README.md          -- 本应用的功能说明、安装与使用方式
  package.json       -- 依赖声明文件（或等效的 go.mod / Cargo.toml 等）
  src/               -- 源代码目录
  tests/             -- 测试目录
  config/            -- 应用级配置文件（可选）
  scripts/           -- 构建与部署脚本（可选）
```

### 2.3 分组内应用列表

按应用类型分组的实际应用明细（与下方「应用清单」自动表互补；人工维护，新增/移动应用后同步）：

#### containers/ —— 容器编排类（Podman 生态）

| 应用 | 说明 |
|------|------|
| [jupyter-podman-rootless](containers/jupyter-podman-rootless/README.md) | 基于 Podman rootless 的 Jupyter 开发容器（Python 3.14t + Miniforge3 + SSH + OMLMD/OLOT + Toolbx 透传） |
| [client](containers/client/README.md) | jupyter-podman-rootless 镜像消费端：podman-py load/run/stop + 镜像备份（invoke save/load）+ quant/xmnn/monetize 工作负载栈 |
| [shared](containers/README.md)（[pyproject](containers/shared/pyproject.toml)） | 组内共享包 jpman-common：podman SDK 连接层唯一事实源 + 只读工具，两端共同依赖（组层 [AGENTS](containers/AGENTS.md) 代管） |

#### docker-images/ —— 容器镜像类（Docker 生态）

| 应用 | 说明 |
|------|------|
| [devcontainer-base](docker-images/devcontainer-base/README.md) | 全功能开发容器（Ubuntu 26.04，SSH+Docker DinD/DooD+Podman+Jupyter，supervisord 管理，Python 3.14 cp314t） |
| devcontainer-win11 | Windows 11 开发容器（Server Core 2022，SSH+Docker DooD+Jupyter，PowerShell 管理，暂缺 README） |
| [docker-ssh-dind](docker-images/docker-ssh-dind/README.md) | Docker SSH DinD（Docker-in-Docker）环境 |
| [jupyter-ssh-base](docker-images/jupyter-ssh-base/README.md) | Jupyter Notebook SSH 基础镜像（docker-ssh-dind 与 eva 生态共用的底层底座） |
| [pytorch-base](docker-images/pytorch-base/README.md) | PyTorch 基础环境镜像 |
| [caffe-ffi-jupyter](docker-images/caffe-ffi-jupyter/README.md) | Caffe-FFI Jupyter 开发环境（基于 jupyter-ssh-base） |
| caffe-ffi-cross | Caffe-FFI 交叉编译（macOS/Windows 交叉构建镜像，暂缺 README） |
| xmnn-runtime | XMNN 运行时环境（暂缺 README） |

#### ai-agents/ —— AI 应用类

| 应用 | 说明 |
|------|------|
| [zhujian-wudao](ai-agents/zhujian-wudao/README.md) | 竹简悟道——道家哲学 AI 洞察项目 |
| [ai-code-assistant](ai-agents/ai-code-assistant/README.md) | AI 代码助手 Web 应用 |
| [eve-minimal-agent](ai-agents/eve-minimal-agent/README.md) | Vercel Eve 最小可运行 Agent 示例 |

#### dev-tools/ —— 开发者工具类

| 应用 | 说明 |
|------|------|
| [prompt_extraction](dev-tools/prompt_extraction/README.md) | 提示词质量评估与提取工具 |
| [okf-zhihu-publisher](dev-tools/okf-zhihu-publisher/README.md) | OKF 知乎发布器（内容同步发布工具） |
| camera-power-controller | 摄像头电源控制工具（暂缺 README） |

#### samples/ —— 示例/原型类

| 应用 | 说明 |
|------|------|
| [cow-demo](samples/cow-demo/README.md) | 零拷贝 COW 读写分离模式 C++ 示例框架 |
| [short-video-site](samples/short-video-site/README.md) | ReelVibe 短视频网站（AI 全流程开发 Demo） |
| [serial-camera-controller](samples/serial-camera-controller/README.md) | 串口控制 USB 摄像头抓图/录像（CH340+OpenCV+pyserial） |
| [samples-retrospective](samples/samples-retrospective/README.md) | samples 区复盘与经验沉淀 |
| zleap-workspace-first-prototype | 工作区首个原型（多模型路由，暂缺 README） |

> **维护约定**：`agent-monetize/` 为根级独立应用（不属上述分组，见下方自动应用清单）；新增/移动应用时同步本小节与下方自动清单（运行 `python .agents/scripts/docgen.py apps` 刷新）。

### 2.4 应用清单

<!-- APPS_TABLE_START -->

| 应用 | 说明 | 入口 |
|---|---|---|
| `agent-monetize/` | **Python 3.14+ 智能体自动变现平台** —— 自主循环 + 道家门控 + 沙箱通道 + tvm-ffi 桥接。 | [README.md](agent-monetize/README.md) |
| `ai-agents/` | ai-agents 应用 | `ai-agents/`（暂无 README） |
| `containers/` | containers/ — Podman rootless 容器工作区分组 | [README.md](containers/README.md) |
| `dev-tools/` | dev-tools 应用 | `dev-tools/`（暂无 README） |
| `docker-images/` | docker-images 应用 | `docker-images/`（暂无 README） |
| `samples/` | samples 应用 | `samples/`（暂无 README） |
| `tests/` | tests 应用 | `tests/`（暂无 README） |

<!-- APPS_TABLE_END -->

## 三、新应用创建规范

### 3.1 命名约定

应用名称采用 **kebab-case**（小写字母与连字符），例如：

- 正确：`my-web-app`、`data-pipeline`、`api-gateway`
- 错误：`MyWebApp`、`my_web_app`、`myWebApp`

命名应简洁且自描述，能够反映应用的核心用途。

### 3.2 目录结构要求

每个新应用至少应包含以下文件或目录：

- `README.md`：应用自身的功能说明、安装步骤与使用指南
- **依赖声明文件**：根据技术栈选择对应文件（如 `package.json`、`go.mod`、`Cargo.toml`）
- `src/`：源代码目录
- `tests/`：测试目录

### 3.3 依赖管理

- 优先使用对应语言生态的标准包管理器（如 npm、pip、go mod、cargo 等）
- 各应用的依赖应在自身的依赖声明文件中明确列出
- 满足提升条件的公共依赖可放入 `apps/shared/`，由各应用引用
- 应用不应直接依赖项目根目录下 `vendor/` 中的第三方库（详见第五节）

## 四、`.temp/` 到 `apps/` 的迁移流程

### 4.1 开发阶段规则

新应用的初期开发与验证**必须**在 `d:\AI\.temp\<app-name>\` 中进行。此阶段的代码处于探索与迭代状态，尚未达到正式纳入应用工作空间的质量标准。

### 4.2 迁移条件

当应用同时满足以下全部条件时，方可执行迁移：

1. **功能稳定**：核心功能已实现并通过验收，无阻塞性缺陷
2. **测试通过**：单元测试与集成测试全部通过，覆盖率满足项目标准（整体不低于 80%，核心模块不低于 90%）
3. **代码审查完成**：已通过代码审查者（reviewer）的质量审查，无遗留严重问题

满足上述条件后，将应用从 `.temp/<app-name>/` 迁移至 `apps/<app-name>/`。

### 4.3 迁移后清理

迁移完成后，**必须清理** `.temp/<app-name>/` 中的残留文件，避免暂存区膨胀。清理操作包括删除源目录及其全部内容。

### 4.4 详细规范

完整的生命周期规范（包括各阶段参与角色、质量门禁与回退策略）见 `.agents/protocols/app-development-workflow.md`。

## 五、与项目其他目录的关系

### `.temp/`

`.temp/` 是应用开发的**暂存区**。所有新应用在通过质量验证之前，在此目录中进行初期开发与迭代。`.temp/` 中的代码不受 `apps/` 的规范约束，但受 `.gitignore` 排除规则的管控。

### `vendor/`

`vendor/` 是第三方库的本地存放目录，已被 `.gitignore` 排除在版本控制之外。**应用不应直接依赖 `vendor/` 中的库**，应通过各自语言生态的标准包管理器管理依赖。`vendor/` 仅在特定构建场景下作为离线构建缓存使用。

### `docs/`

`docs/` 存放**项目级文档**，包括技术知识库、复盘报告、开发标准等。应用自身的文档（功能说明、API 参考、架构设计等）应放在应用目录内的 `README.md` 或独立文档文件中，不应散落在项目级 `docs/` 目录中。

### `.agents/`

`.agents/` 定义了 AI 智能体的角色、协议、工作流与提示词体系。应用开发的完整生命周期受 `.agents/protocols/app-development-workflow.md` 中定义的工作流协议约束，确保开发过程遵循项目整体治理框架。
