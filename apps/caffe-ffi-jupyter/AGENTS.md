# caffe-ffi-jupyter - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本项目是 SpecWeave apps/ 下的子应用，基于jupyter-ssh-base构建
>         全局规则继承自 SpecWeave 根 AGENTS.md；SSH/Jupyter/supervisord/entrypoint规范继承自
>         ../jupyter-ssh-base/.agents/
> 步骤 3：按上下文路由表加载本项目特有规范（.agents/rules/ 下对应文件）
> 步骤 3.5：自检 — 确认已理解父级规则与本项目特有约束
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 caffe-ffi-jupyter 子项目的 AI 协作者入口。本项目基于 jupyter-ssh-base 增量构建，
> 添加 Miniconda3 + caffe-ffi（C++扩展库）+ conda环境内核注册。
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，
> SSH/Jupyter/entrypoint/supervisord规范继承自jupyter-ssh-base，本文件仅定义本项目特有的
> 上下文路由与约束入口。详细规则已原子化拆分至 `.agents/rules/` 目录。

## 项目概述

- **项目类型**：Docker 镜像构建项目（caffe-ffi Jupyter开发环境）
- **基础镜像**：jupyter-ssh-base:1.1（必须预先构建）
- **核心组件**：Miniconda3 + Python 3.14 + caffe-ffi（C++扩展库）+ Jupyter内核注册
- **构建前提**：必须在WSL2/Linux环境中构建（C++编译）
- **构建上下文**：SpecWeave根目录（需要COPY caffe-ffi源码）
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai（继承自jupyter-ssh-base）
- **非root用户**：jupyteruser（继承自jupyter-ssh-base）
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）
- **直接父镜像**：[`../jupyter-ssh-base/.agents/`](../jupyter-ssh-base/.agents/)
- **AI资产容器**：`.agents/` 目录（本项目特有规则/脚本/模板）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/jupyter-ssh-base/.agents/（SSH + Jupyter + supervisord + entrypoint规范）
       └─ apps/caffe-ffi-jupyter/AGENTS.md（本文件，增量构建路由入口）
            ├─ .agents/README.md       ← AI资产容器索引
            │   └─ rules/
            │       ├─ dockerfile.md   ← Dockerfile 增量构建规范
            │       └─ build-test.md   ← 构建与测试流程
            ├─ Dockerfile          ← 增量构建定义（基于jupyter-ssh-base添加conda+caffe-ffi）
            ├─ scripts/build.sh    ← 一键构建脚本（基础镜像检测/上下文处理/自动验证）
            ├─ compose/docker-compose.yml  ← 运行编排
            └─ jupyter/            ← Jupyter自定义配置
```

**嵌套优先原则**：进入本目录后优先读取本文件；caffe-ffi特有约束按主题加载 `.agents/rules/` 对应文件；SSH/Jupyter/entrypoint/supervisord规范回退到jupyter-ssh-base；全局规则回退到SpecWeave根。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile增量构建/caffe-ffi编译 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | FROM依赖、conda环境、pip --no-build-isolation、RPATH三层机制、Jupyter内核注册、protobuf兼容 |
| 构建脚本修改 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | WSL前提、基础镜像检测、构建上下文、自动验证、--cn镜像源 |
| SSH/Jupyter/entrypoint/supervisord | [../jupyter-ssh-base/.agents/rules/](../jupyter-ssh-base/.agents/rules/) | **继承自jupyter-ssh-base**，本项目不覆盖 |
| Docker Compose运行 | [.agents/rules/build-test.md](.agents/rules/build-test.md#docker-compose运行) | compose/目录、端口映射、token获取 |
| caffe-ffi内核验证 | [.agents/rules/build-test.md](.agents/rules/build-test.md#验证caffe-ffi安装) | 内核列表、动态库ldconfig验证、ldd检查 |
| AI资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/目录结构、继承链 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |
| Dockerfile自动化测试 | [../../.agents/scripts/test-dockerfiles.ps1](../../.agents/scripts/test-dockerfiles.ps1) | 项目根目录测试脚本 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口 |
| 直接父镜像规范 | [../jupyter-ssh-base/.agents/](../jupyter-ssh-base/.agents/) | SSH/Jupyter/entrypoint/supervisord规范**直接继承** |
| 本文件入口 | AGENTS.md（本文件） | caffe-ffi-jupyter子项目路由入口 |
| AI资产容器 | [.agents/README.md](.agents/README.md) | .agents/目录索引与继承链 |
| Docker增量构建规范 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | Miniconda/caffe-ffi编译/RPATH三层机制/内核注册/protobuf兼容 |
| 构建测试规范 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | WSL前提/基础镜像检测/Compose/动态库验证 |
| Docker构建文件 | Dockerfile | 增量构建：jupyter-ssh-base→系统包→Miniconda→caffe-ffi编译→runtime配置→清理 |
| 构建脚本 | scripts/build.sh | 一键构建，自动检测基础镜像和WSL环境 |
| Compose编排 | compose/docker-compose.yml | 端口映射、卷挂载、环境变量 |
| Jupyter配置 | jupyter/ | 自定义Jupyter配置 |

## 项目约束速览

详细约束已按主题拆分到 `.agents/rules/` 下各文件，继承的约束见jupyter-ssh-base：

| 约束主题 | 所在文件 |
|---------|---------|
| FROM依赖jupyter-ssh-base:1.1 | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| 构建上下文必须为SpecWeave根目录 | [dockerfile.md](.agents/rules/dockerfile.md#构建上下文) |
| WSL2/Linux构建前提 | [build-test.md](.agents/rules/build-test.md#重要构建前提) |
| Miniconda3到/opt/conda，conda环境caffe-ffi | [dockerfile.md](.agents/rules/dockerfile.md#conda环境规范) |
| pip install --no-build-isolation编译caffe-ffi | [dockerfile.md](.agents/rules/dockerfile.md#构建阶段结构) |
| RPATH三层机制（LD_LIBRARY_PATH+ldconfig+编译时RPATH） | [dockerfile.md](.agents/rules/dockerfile.md#运行时库路径三层机制) |
| Jupyter内核注册到/usr/local/share/jupyter/kernels/ | [dockerfile.md](.agents/rules/dockerfile.md#jupyter内核注册) |
| 不覆盖ENTRYPOINT（继承父镜像tini+entrypoint） | [dockerfile.md](.agents/rules/dockerfile.md#重要继承关系) |
| protobuf版本兼容（runtime安装libprotobuf-dev） | [dockerfile.md](.agents/rules/dockerfile.md#protobuf版本兼容) |
| 编译工具链最终卸载 | [dockerfile.md](.agents/rules/dockerfile.md#镜像优化) |
| SSH/Jupyter双服务/supervisord/非root用户 | [../jupyter-ssh-base/.agents/rules/](../jupyter-ssh-base/.agents/rules/) | **继承自jupyter-ssh-base** |

## 快速开始

```bash
# 0. 先构建基础镜像
cd ../jupyter-ssh-base && bash build.sh && cd -

# 1. 构建（WSL2中执行）
bash scripts/build.sh

# 2. 运行
cd compose/ && docker compose up -d

# 3. 获取Jupyter token
docker compose logs jupyter | grep "token="

# 4. 验证caffe-ffi内核可用
docker compose exec jupyter /opt/venv/bin/jupyter kernelspec list
```

完整构建参数、WSL环境配置、验证命令和问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md` 和直接父镜像 `../jupyter-ssh-base/.agents/`
- 遵循嵌套优先原则，SSH/Jupyter/entrypoint规范继承jupyter-ssh-base，全局规则回退到父级工作区
- 支持工作区发现协议的五步发现流程
- AI资产已原子化拆分至 `.agents/` 目录，遵循单一职责原则

## 变更日志

- 2026-08-07 | refactor | 原子化拆分AGENTS.md：详细约束迁移至.agents/rules/（2个主题文件），AGENTS.md精简为路由入口
- 2026-07-22 | feat | 初始化 caffe-ffi-jupyter 项目结构：AGENTS.md、Dockerfile、build.sh、docker-compose.yml
