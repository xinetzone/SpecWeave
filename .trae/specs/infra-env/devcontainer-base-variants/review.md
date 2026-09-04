# devcontainer-base 镜像变体目录结构 - Verification Checklist

## 目录结构检查
- [ ] variants/ 目录已创建在 apps/devcontainer-base/ 下
- [ ] variants/README.md 存在且包含变体列表、快速开始、新增变体指南
- [ ] variants/build.sh 存在且可执行
- [ ] variants/_template/ 目录包含完整模板（Dockerfile/.env.example/README.md/.agents/rules/dockerfile.md）
- [ ] variants/shared/lib/logging.sh 存在（或正确 symlink 到 scripts/lib/logging.sh）
- [ ] variants/conda/ 目录包含 Dockerfile/.env.example/README.md/.agents/rules/dockerfile.md
- [ ] variants/conda-llvm/ 目录包含 Dockerfile/.env.example/README.md/.agents/rules/dockerfile.md
- [ ] 每个变体子目录的 .agents/rules/dockerfile.md 描述该变体特有规范

## conda 变体验证
- [ ] Dockerfile 以 `# syntax=docker/dockerfile:1.7-labs` 开头
- [ ] Dockerfile 使用 `FROM devcontainer-base:latest` 作为基础镜像
- [ ] Dockerfile 支持 APT_MIRROR 和 CONDA_MIRROR 构建参数
- [ ] Miniconda 安装到 /opt/conda 路径
- [ ] conda 镜像源配置正确（支持清华 TUNA 和官方源）
- [ ] /etc/profile.d/conda-init.sh 存在且包含 conda 初始化逻辑
- [ ] 系统 /opt/venv 未被覆盖或破坏
- [ ] Dockerfile 包含构建计时器（[TIMER] 标记）
- [ ] Dockerfile 包含语法验证检查点（[VALIDATION CHECKPOINT]）
- [ ] Dockerfile 包含最终验证阶段（验证 conda --version 等）
- [ ] .env.example 包含所有可配置构建参数及注释说明

## conda-llvm 变体验证
- [ ] Dockerfile 以 `# syntax=docker/dockerfile:1.7-labs` 开头
- [ ] Dockerfile FROM devcontainer-base:conda（利用层缓存）
- [ ] LLVM 版本锁定为 22.1.8
- [ ] clang 版本锁定为 22.1.8
- [ ] cmake 和 ninja 通过 conda 安装
- [ ] 使用 conda-forge 频道安装 LLVM/clang
- [ ] 环境变量配置正确（PATH 包含 conda 环境 bin 目录）
- [ ] Dockerfile 包含构建计时器和验证检查点
- [ ] 最终验证阶段检查 llvm-config/clang/cmake/ninja 版本
- [ ] .env.example 包含 LLVM_VERSION 等可配置参数

## 构建脚本验证
- [ ] variants/build.sh 可执行且 bash 语法正确（bash -n 通过）
- [ ] `--list` 参数正确列出所有可用变体（conda, conda-llvm）
- [ ] `--variant <name>` 参数正确构建指定变体
- [ ] `--all` 参数按依赖顺序构建所有变体（先 conda，后 conda-llvm）
- [ ] `--cn` 参数预设国内镜像源（APT_MIRROR=aliyun, CONDA_MIRROR=tuna）
- [ ] `--no-cache` 参数传递给 docker build
- [ ] `--build-arg` 参数正确传递给 docker build
- [ ] 构建前检查 devcontainer-base:latest 是否存在，不存在时给出清晰提示
- [ ] 构建日志使用与现有 build.sh 一致的格式（[INFO]/[OK]/[ERROR]/[TIMER]）
- [ ] 构建完成后输出计时器汇总表
- [ ] 复用 scripts/lib/logging.sh 日志库

## 服务继承验证
- [ ] conda 变体容器中 SSH 服务可正常启动
- [ ] conda 变体容器中 Docker DinD 服务可正常启动
- [ ] conda 变体容器中 Jupyter 服务可正常启动
- [ ] conda-llvm 变体容器中 SSH 服务可正常启动
- [ ] conda-llvm 变体容器中 Docker DinD 服务可正常启动
- [ ] conda-llvm 变体容器中 Jupyter 服务可正常启动
- [ ] 健康检查脚本（healthcheck.sh）在变体中仍然有效

## 环境共存验证
- [ ] conda 变体中 /opt/venv/bin/python 仍然可用（Jupyter 依赖）
- [ ] conda 变体中 /opt/conda/bin/conda 可用
- [ ] 默认 PATH 优先使用 /opt/venv/bin（不破坏 Jupyter 等服务）
- [ ] `source /etc/profile.d/conda-init.sh` 后 conda 命令可用
- [ ] `conda activate base` 后 Python 是 conda 环境的 Python
- [ ] devuser 用户的 .bashrc 包含 conda 初始化（可选，参考 pytorch-base 模式）

## 文档和路由验证
- [ ] variants/README.md 包含变体列表表格（名称/描述/基础镜像/包含组件）
- [ ] variants/README.md 包含快速开始命令示例
- [ ] variants/README.md 包含构建参数说明（--variant/--all/--cn/--no-cache 等）
- [ ] variants/README.md 包含"如何新增变体"5步指南
- [ ] devcontainer-base/AGENTS.md 嵌套路由关系图中包含 variants/ 目录
- [ ] devcontainer-base/AGENTS.md 上下文路由表包含变体构建入口
- [ ] devcontainer-base/AGENTS.md 核心规范入口表包含 variants 相关条目
- [ ] 所有 Markdown 内部链接有效（无断链）
- [ ] 每个变体的 README.md 包含：镜像说明、构建命令、运行命令、验证命令

## 模板验证
- [ ] _template/Dockerfile 包含清晰的占位符注释
- [ ] _template/README.md 包含新变体创建 Checklist
- [ ] _template/.env.example 包含所有通用构建参数
- [ ] _template/.agents/rules/dockerfile.md 包含变体规范模板

## 镜像体积检查
- [ ] conda 变体镜像体积 < 2GB（基于 devcontainer-base ~1.2GB + Miniconda ~500MB）
- [ ] conda-llvm 变体镜像体积 < 4GB（基于 conda + LLVM/clang/cmake/ninja ~1.5GB）
