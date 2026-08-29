---
id: jupyter-podman-rootless-changelog
title: jupyter-podman-rootless 变更日志
source: 从 apps/containers/jupyter-podman-rootless/AGENTS.md 拆分归档
---

# 变更日志

## 2026-08-29

| 类型 | 变更 |
|------|------|
| feat | passt 固化进 Containerfile（Stage 1 apt 清单 + 版本回显 + Layer 5 最终验证），修复 DinP 场景 rootless 网络命名空间 pasta 缺失报错 |
| fix | jpman rebuild-all/rebuild 补 `--format docker`：OCI 格式忽略 SHELL 指令导致 Stage 2 bash 数组语法在 dash 下报 Syntax error |
| fix | Containerfile Miniforge 下载 `--max-time` 300s→900s：慢速链路（~200KB/s）拉取 124MB 安装包双源 4 次尝试全部超时 |
| refactor | 合并 Containerfile.hidden 至主 Containerfile 并删除：Layer 4 吸收 root 配置权限与 allow_hidden 校验（VALIDATE 5/5→6/6）；jpman rebuild 改为主 Containerfile 层缓存构建（配置变更仅重建 Layer 4/5）；同步 AGENTS/README/docs/14/16、.agents/README、jpman-podman-ops SKILL.md 共 8 处引用 |

## 2026-08-27

| 类型 | 变更 |
|------|------|
| feat | jpman `-w/--workspace` 自定义工作区挂载：支持CLI参数覆盖.env配置，Windows路径自动转换为WSL/mnt/路径 |
| feat | jpman .env安全加载：逐行解析（非source），剥离CRLF，支持引号值，反斜杠路径不被破坏 |
| feat | jpman 短变量名兼容：CONTAINER_NAME/SSH_PORT/IMAGE_TAG/USER_PASSWORD 自动fallback到JUPYTER_*前缀 |
| feat | jpman WORKSPACE优先级链：-w CLI > WORKSPACE env > JUPYTER_WORKSPACE env > .env > 默认workspace |
| fix | jpman: 移除podman create错误的-d标志（create本身不启动，-d是run的选项） |
| fix | jpman: CRLF行结尾导致bash语法错误（脚本转为LF，.env加载自动剥离\r） |
| fix | jpman: cmd_restart参数透传丢失（"$@"透传给cmd_start） |
| fix | jpman: bash source破坏Windows反斜杠路径（重写为安全逐行解析） |
| docs | 更新docs/14-jpman-cli.md：补充-w参数、短名兼容表、WORKSPACE优先级、路径自动转换说明 |
| docs | 更新.env.example：补充jpman路径自动转换说明和短名兼容注释 |
| docs | 里程碑复盘+4个L2模式入库（bash-safe-dotenv-loading/wsl-windows-path-autoconvert/multi-entrypoint-config-unification/cross-platform-bash-preflight-checklist） |
| feat | jpman零依赖CLI：跨平台bash/cmd/ps1脚本，无需Python依赖 |
| feat | 镜像缓存：jpman save/load，pigz多线程压缩，manifest元数据，latest软链接 |
| feat | WSL2一键导出：jpman wsl-export，自动配置wsl.conf+Conda激活+冒烟测试验证 |
| feat | 增量重建：Containerfile.hidden + jpman rebuild，配置变更<10秒完成 |
| feat | WSL保活：jpman keepalive自动启动sleep infinity防止容器退出 |
| feat | jpman install：全局命令安装symlink到~/.local/bin |
| refactor | 文档更新：README.md、AGENTS.md、docs/README.md更新，新增3个文档（共17个） |
| docs | 新增docs/14-jpman-cli.md：jpman CLI完整参考 |
| docs | 新增docs/15-wsl-export.md：WSL2发行版导出与使用指南 |
| docs | 新增docs/16-image-cache.md：镜像缓存与增量重建指南 |
| fix | .agents/README.md父级路径修正（4级向上而非3级） |
| refactor | AGENTS.md精简为路由入口，约束迁移至.agents/rules/（7个主题文件）；README.md原子化至docs/（14个文档） |
| feat | R5/Toolbx集成：Toolbx兼容标记(LABEL+/run/host+markers+capsh)、compose.dev.yaml透传覆盖文件、注释式透传文档 |
| feat | R4/OLOT集成：KServe ModelCar标准镜像打包(model.pack/extract)、olot_car.py辅助脚本 |
| feat | R3/OMLMD集成：ML模型OCI artifact分发(model.push/pull/config)、model-registry compose service(profile:registry) |
| feat | R2/podman-compose集成：声明式compose.yaml编排、.env配置管理、compose_backend.py |
| feat | R1/podman-py SDK集成：三层exec后端架构、client.py封装 |

## 2026-08-26

| 类型 | 变更 |
|------|------|
| feat | 完整实现：Containerfile(7层)、entrypoint.sh(7步)、config/配置、invoke任务、healthcheck |
| feat | 初始化项目结构：AGENTS.md、目录结构、pyproject.toml、.containerignore、README.md |
