# Hermes Agent 安装方案验证清单

## 文档完整性检查
- [x] 环境要求章节列出了所有支持的操作系统及版本
- [x] 硬件要求（CPU、内存、磁盘）明确
- [x] 系统依赖清单完整，包含各平台安装命令
- [x] Python 版本要求（>=3.11,<3.14）明确标注
- [x] Node.js 版本要求（>=22.22.0）明确标注
- [x] uv 包管理器的安装方法已说明

## 安装方式覆盖检查
- [x] Linux/macOS/WSL2 官方脚本安装步骤完整
- [x] Windows PowerShell 官方脚本安装步骤完整
- [x] 手动源码安装（uv 方式）步骤完整
- [x] 手动源码安装（venv + pip 方式）步骤完整
- [x] Docker 镜像构建步骤完整
- [x] docker-compose 部署步骤完整
- [x] Termux（Android）特殊安装说明完整

## 安装脚本参数检查
- [x] --no-venv 参数说明
- [x] --skip-setup 参数说明
- [x] --skip-browser/--no-playwright 参数说明
- [x] --no-skills 参数说明
- [x] --branch 参数说明
- [x] --commit/--force-commit 参数说明
- [x] --dir/--hermes-home 参数说明
- [x] --include-desktop 参数说明
- [x] --non-interactive 参数说明

## 配置说明检查
- [x] .env 文件复制方法已说明
- [x] LLM 提供商配置（至少 5 个主流提供商）
- [x] 工具 API Key 配置说明
- [x] config.yaml 与 .env 的区别已解释
- [x] hermes setup 交互式配置向导说明
- [x] hermes model 模型选择命令说明
- [x] hermes tools 工具配置命令说明
- [x] 终端后端配置（local/docker/ssh/modal 等）说明
- [x] 安全提示（.env 不提交版本控制）醒目

## 验证步骤检查
- [x] hermes --version 版本检查
- [x] hermes doctor 诊断命令说明
- [x] 基础对话测试步骤
- [x] 工具功能验证方法
- [x] TUI 界面验证方法
- [x] 每个验证点有明确的通过/失败标准

## Docker 部署检查
- [x] Dockerfile 构建命令正确
- [x] docker-compose.yml 服务说明完整
- [x] 卷挂载配置说明
- [x] HERMES_UID/HERMES_GID 权限配置说明
- [x] s6-overlay 服务管理说明
- [x] 常用 docker compose 命令列表
- [x] 环境变量传递方法说明
- [x] dashboard 安全提示（仅绑定 127.0.0.1）

## 常见问题检查
- [x] 网络问题（GitHub/PyPI/npm 访问慢）
- [x] Python 版本问题（3.14 不支持的原因）
- [x] Node.js 版本问题
- [x] 依赖编译失败（gcc、Python.h）
- [x] 权限问题（sudo、EACCES）
- [x] Windows 特有问题（CRLF、长路径、pywin32）
- [x] Docker 特有问题（权限、卷挂载）
- [x] 日志查看方法说明
- [x] 完全卸载步骤
- [x] 重装步骤

## 升级与维护检查
- [x] hermes update 命令说明
- [x] 手动升级方法
- [x] Docker 镜像升级方法
- [x] 配置备份建议
- [x] 数据目录结构说明

## 国内网络优化检查
- [x] PyPI 镜像源配置
- [x] npm 镜像源配置
- [x] uv 镜像配置
- [x] GitHub 访问加速方法
- [x] Docker 镜像加速配置
- [x] Hugging Face 镜像配置
- [x] Playwright 下载镜像
- [x] 国内模型 API 替代方案

## 安全检查
- [x] API Key 安全提示
- [x] 文件权限说明
- [x] Docker 安全建议
- [x] dashboard 远程访问安全警告

## 质量门检查
- [x] G1: 所有事实描述无因果推断词，纯客观
- [x] G2: 每个问题包含症状+原因+解决方案三段式
- [x] G3: 安装步骤可迁移，有触发条件和反模式
- [x] G4: 验证步骤原子化，可独立验证
- [x] V: 已通过多视角对抗审查（魔鬼代言人/新人/老板/未来）
