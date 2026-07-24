# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 格式，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

<!-- changelog -->

## [1.2.0] - 2026-07-24

### Added

- **`run.sh` 一键运行脚本**：支持 10 个子命令（`build` `run` `stop` `shell` `ssh` `logs` `verify` `clean` `rebuild` `info`），提供用户友好的 CLI 入口
- **SSH 公钥自动检测**：`run.sh` 启动时自动检测 `~/.ssh/id_ed25519.pub` → `~/.ssh/id_rsa.pub`，通过 `SSH_PUBLIC_KEY` 环境变量注入容器，实现免密 SSH 登录
- **`build.sh --verify` 嵌入式验证**：构建后自动启动临时容器，依次执行 healthcheck、SSH 非交互路径、Jupyter API 三项验证，验证失败则退出
- **`build.sh --verify-only` 仅验证模式**：跳过构建，仅对已有镜像运行验证流水线
- **`run.sh --compose` 模式**：支持以 `docker compose` 模式启动，与 `docker run` 模式切换

### Changed

- 文档更新：README.md、GUIDE.md、DELIVERY.md 新增"一键启动"章节和 `run.sh` 快速参考

## [1.1.0] - 2026-07-24

### Added

- CI/CD 流水线（`.github/workflows/jupyter-ssh-base-ci.yml`）：build、test、scan、push 四阶段
- `DELIVERY.md`：13 章交付文档，含快速参考卡片、部署指南、FAQ

### Fixed

- Dockerfile 添加 `/etc/environment` PATH 配置，解决 SSH 非交互 shell 找不到 `jupyter` 命令的问题
- entrypoint.sh 中 `ENABLE_SUDO_NOPASSWD` 别名不生效的条件判断修复
- 变量引用 false positive 误报优化（`${jupyter_password_hash}` 等 shell 变量不再误报）
- `sensitive_info.py` 增强 shell 变量引用识别

### Changed

- 构建脚本 `build.sh` 支持 `--cn`/`--apt-mirror`/`--pip-mirror` 参数，方便国内用户使用镜像源
- 健康检查 `healthcheck.sh` 改为 exec TCP 探测方式
- entrypoint.sh 中 Jupyter stderr 重定向优化，减少非关键告警
- 移除 Dockerfile 中的敏感 ENV 声明

## [1.0.0] - 2026-07-24

### Added

- 初始版本：基于 Ubuntu 26.04 的 Jupyter + SSH 双服务 Docker 基础镜像
- 7 阶段优化 Dockerfile：builder → runtime → jupyter-runtime 多阶段构建
- 企业级 SSH 安全：ED25519 密钥、非 root 用户 `jupyteruser`、密码认证、禁用 root 登录
- 安全 Jupyter 配置：固定版本、token/密码认证、0.0.0.0 绑定
- Supervisord 双服务管理：自动重启、日志输出到 stdout
- 灵活环境变量配置：`USER_PASSWORD`、`JUPYTER_TOKEN`、`JUPYTER_PASSWORD`、`SSH_PUBLIC_KEY`、`GRANT_SUDO`、`ALLOW_ROOT_SSH`、`TZ`、`LANG`
- 健康检查脚本 `healthcheck.sh`、`healthcheck-test.sh`
- 自动化测试脚本 `test-ssh-noninteractive-path.sh`
- docker-compose.yml 编排文件
- 中文环境支持（zh_CN.UTF-8、Asia/Shanghai 时区）