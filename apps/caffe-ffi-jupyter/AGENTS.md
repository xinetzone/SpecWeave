# caffe-ffi-jupyter - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本项目是 SpecWeave apps/ 下的子应用，全局规则继承自 SpecWeave 根 AGENTS.md
> 步骤 3：按上下文路由表加载本项目特有规范
> 步骤 3.5：自检 — 确认已理解父级规则与本项目特有约束
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 caffe-ffi-jupyter 子项目的 AI 协作者入口。本项目是一个基于 jupyter-ssh-base 的
> Caffe-FFI 开发环境 Docker 镜像，预安装 Miniconda3 + Python 3.14 + caffe-ffi，
> 支持 SSH + Jupyter Notebook 双服务访问。所有全局规则继承自 SpecWeave 根工作区，
> 本文件仅定义本项目特有的上下文路由与约束。

## 项目概述

- **项目类型**：Docker 镜像构建项目（Caffe-FFI 开发环境）
- **基础镜像**：jupyter-ssh-base（必须预先构建）
- **核心组件**：Miniconda3 + Python 3.14 + caffe-ffi + Jupyter Notebook + SSH
- **Conda 环境**：caffe-ffi（`/opt/conda/envs/caffe-ffi/`）
- **Jupyter 内核**：Python 3.14 (caffe-ffi)
- **非root用户**：jupyteruser（继承自 jupyter-ssh-base，UID 1000）
- **构建上下文**：SpecWeave 根目录（需要访问 projects/xuanspace/libs/caffe-ffi/ 源码）
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准

## 目录结构说明

```
caffe-ffi-jupyter/
├── AGENTS.md           ← 本文件，AI协作者入口
├── Dockerfile          ← 主镜像构建定义（基于jupyter-ssh-base）
├── .dockerignore       ← Docker构建忽略规则
├── docker-compose.yml  ← Compose编排示例
├── scripts/            ← 辅助脚本
│   └── build.sh        ← 一键构建脚本（含国内镜像源、依赖检查）
└── README.md           ← 使用文档
```

**嵌套路由关系**：

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/AGENTS.md（apps 区域入口路由）
       └─ apps/jupyter-ssh-base/AGENTS.md（基础镜像约束）
            └─ apps/caffe-ffi-jupyter/AGENTS.md（本文件，项目特有约束）
                 ├─ Dockerfile         ← 镜像构建定义
                 ├─ scripts/build.sh   ← 构建脚本
                 └─ docker-compose.yml ← Compose编排
```

**嵌套优先原则**：进入本目录后优先读取本文件；本文件未覆盖的规则回退到 jupyter-ssh-base/AGENTS.md → apps/AGENTS.md → SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile修改/构建优化 | 本文件 + Dockerfile | 基于jupyter-ssh-base增量构建、Miniconda安装、caffe-ffi编译、内核注册 |
| 构建脚本修改 | scripts/build.sh | 依赖检查（jupyter-ssh-base镜像）、国内镜像源、BuildKit缓存、自动验证 |
| Compose编排 | docker-compose.yml | 端口映射、volume挂载、环境变量配置 |
| 镜像构建与测试 | 本文件「快速开始」章节 | ./scripts/build.sh 一键构建 |
| caffe-ffi源码 | projects/xuanspace/libs/caffe-ffi/（构建时COPY） | Caffe-FFI源码，构建上下文从SpecWeave根目录访问 |
| 基础镜像参考 | [../jupyter-ssh-base/AGENTS.md](../jupyter-ssh-base/AGENTS.md) | jupyter-ssh-base约束（SSH/Jupyter/supervisord/jupyteruser） |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口 |
| apps区域路由 | [../AGENTS.md](../AGENTS.md) | apps区域入口路由 |
| 基础镜像规范 | [../jupyter-ssh-base/AGENTS.md](../jupyter-ssh-base/AGENTS.md) | jupyter-ssh-base约束（SSH/Jupyter/supervisord配置） |
| 本文件入口 | AGENTS.md（本文件） | caffe-ffi-jupyter子项目路由 |
| Docker构建文件 | Dockerfile | 基于jupyter-ssh-base，安装Miniconda+caffe-ffi |
| 构建脚本 | scripts/build.sh | 一键构建，支持--cn国内镜像源、自动检查基础镜像 |
| Docker忽略规则 | .dockerignore | 排除无关文件，加速构建 |
| Compose编排 | docker-compose.yml | SSH 2222 + Jupyter 8888端口映射、volume示例 |

## 构建命令速查

构建 caffe-ffi-jupyter 镜像：

```bash
# 前置条件：先构建jupyter-ssh-base基础镜像
cd ../jupyter-ssh-base && bash scripts/build.sh && cd ../caffe-ffi-jupyter

# 默认构建（官方源）
bash scripts/build.sh

# 国内镜像源构建（推荐在国内网络环境使用）
bash scripts/build.sh --cn

# 自定义标签
bash scripts/build.sh --tag my-caffe-ffi:latest

# 无缓存构建（用于调试）
bash scripts/build.sh --no-cache

# 运行容器
docker run -d -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -v $(pwd)/workspace:/workspace \
  --name caffe-ffi caffe-ffi-jupyter:latest

# SSH连接
ssh -p 2222 jupyteruser@localhost

# Jupyter访问
# http://localhost:8888/?token=mysecret
# 内核选择：Python 3.14 (caffe-ffi)

# 验证caffe-ffi导入
docker exec caffe-ffi bash -lc "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c 'import caffe_ffi; print(caffe_ffi.__version__)'"
```

## 项目特有约束

1. **基础镜像依赖**：必须先构建 `jupyter-ssh-base:1.1` 镜像，构建脚本会自动检查；Dockerfile 使用 `FROM jupyter-ssh-base:1.1`
2. **构建上下文**：构建上下文必须为 SpecWeave 根目录（`../../`），以便 COPY caffe-ffi 源码（`projects/xuanspace/libs/caffe-ffi/`）
3. **Conda环境**：环境名为 `caffe-ffi`，路径 `/opt/conda/envs/caffe-ffi/`，Python 3.14；通过 profile.d 和 .bashrc 自动激活（仅对jupyteruser的SSH会话）
4. **Jupyter内核**：在conda环境中安装ipykernel并注册为 `Python 3.14 (caffe-ffi)`，保留基础镜像的默认venv内核
5. **编译依赖**：安装build-essential, cmake, ninja-build, libopenblas-dev, libprotobuf-dev, protobuf-compiler用于编译caffe-ffi C++扩展
6. **镜像优化**：编译完成后卸载编译工具链（build-essential等），清理apt/pip/conda缓存，减小镜像体积
7. **中文环境**：继承jupyter-ssh-base的中文环境配置（zh_CN.UTF-8 / Asia/Shanghai）
8. **非root用户**：继承jupyter-ssh-base的jupyteruser用户；构建阶段使用USER root，最终切换回USER jupyteruser
9. **ENTRYPOINT保留**：继承jupyter-ssh-base的ENTRYPOINT（tini + entrypoint.sh），不覆盖；conda环境激活通过.bashrc和profile.d实现
10. **构建日志**：Dockerfile中使用 `echo "[BUILD] ..."` 输出构建日志
11. **caffe-ffi安装**：通过 `pip install --no-build-isolation` 在conda环境中编译安装（必须使用--no-build-isolation防止pip构建隔离导致运行时链接失效）；scikit-build-core自动调用CMake+Ninja；通过SKBUILD_CMAKE_ARGS启用RPATH（CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON）
12. **运行时库路径**：通过三层机制确保C++扩展动态库可被找到：(1) ENV LD_LIBRARY_PATH包含conda环境lib目录；(2) /etc/ld.so.conf.d/caffe-ffi.conf动态注册tvm_ffi和caffe_ffi的site-packages路径并执行ldconfig；(3) 编译时RPATH嵌入链接库路径
13. **Jupyter内核**：在runtime阶段通过 `python -m ipykernel install --prefix=/usr/local` 注册到系统级kernel目录（/usr/local/share/jupyter/kernels/），确保/opt/venv中的Jupyter能发现conda环境的内核
14. **Protobuf兼容**：runtime阶段安装libprotobuf-dev（而非硬编码版本包名），确保apt自动解析与builder阶段一致的protobuf运行时库版本，适配Ubuntu 26.04
15. **敏感信息**：禁止在Dockerfile中硬编码密码/token，通过环境变量注入（继承自jupyter-ssh-base）
16. **网络容错**：wget配置5次重试/120秒超时，apt配置5次重试
17. **WSL构建**：所有构建操作必须在WSL2/Linux环境中执行，build.sh包含环境检测警告

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程

## 变更日志

- 2026-07-29 | fix | 修复Dockerfile关键问题：--no-build-isolation防止构建隔离链接失效、LD_LIBRARY_PATH+ldconfig运行时库路径、runtime阶段Jupyter内核注册、libprotobuf-dev版本兼容、ldd共享库验证
- 2026-07-29 | feat | 初始化项目结构：AGENTS.md、Dockerfile、.dockerignore、scripts/build.sh、docker-compose.yml、README.md
