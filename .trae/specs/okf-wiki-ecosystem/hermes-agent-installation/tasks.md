# Hermes Agent 完整安装方案 - 实施计划

## [ ] Task 1: 编写环境要求与前置准备章节
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 列出支持的操作系统及版本要求
  - 明确硬件要求（CPU、内存、磁盘空间）
  - 列出必需的系统依赖（git、ripgrep、ffmpeg、gcc 等）
  - 说明 Python 和 Node.js 版本要求
  - 提供各平台依赖安装命令（apt、brew、choco 等）
- **Acceptance Criteria Addressed**: FR-5, NFR-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 文档中列出的所有系统依赖在目标平台上可通过标准包管理器安装
  - `human-judgement` TR-1.2: 版本要求明确，无歧义

## [ ] Task 2: 编写官方脚本安装指南（Linux/macOS/WSL2）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 提供一键安装命令
  - 说明安装脚本的参数选项（--no-venv、--skip-setup 等）
  - 解释安装过程的每个步骤（环境检测、依赖安装、仓库克隆、venv 创建）
  - 说明安装后的目录结构（~/.hermes/）
  - 提供安装后立即执行的验证命令
- **Acceptance Criteria Addressed**: AC-1, FR-1
- **Test Requirements**:
  - `programmatic` TR-2.1: 安装命令在干净的 Ubuntu 22.04/24.04 环境中可成功执行
  - `programmatic` TR-2.2: 安装完成后 `hermes --version` 可正常输出版本号
  - `human-judgement` TR-2.3: 脚本参数说明完整，每个参数有使用场景说明

## [ ] Task 3: 编写 Windows PowerShell 安装指南
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 提供 PowerShell 一键安装命令
  - 说明 Windows 特有的注意事项（8.3 短路径、执行策略、pywin32）
  - 解释环境变量配置
  - 说明 WSL2 作为推荐替代方案
  - 提供 Windows 特有的故障排查提示
- **Acceptance Criteria Addressed**: AC-2, FR-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 安装命令在 Windows 10/11 PowerShell 中可成功执行
  - `programmatic` TR-3.2: 安装后新终端中 `hermes` 命令可用
  - `human-judgement` TR-3.3: Windows 特有问题（路径、权限、CRLF）有明确说明

## [ ] Task 4: 编写手动源码安装指南
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 说明克隆仓库的方法（HTTPS/SSH）
  - 提供使用 uv 创建虚拟环境的步骤
  - 提供使用标准 venv + pip 的备选步骤
  - 说明 Python 依赖安装（核心依赖 + 可选 extras）
  - 说明 Node.js 依赖安装和前端构建
  - 提供开发者模式安装（-e ".[all,dev]"）
- **Acceptance Criteria Addressed**: AC-3, FR-3, FR-6, FR-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 按照文档步骤可在干净环境中完成安装
  - `programmatic` TR-4.2: `python -c "import hermes_cli"` 无导入错误
  - `programmatic` TR-4.3: `hermes --version` 正常输出
  - `human-judgement` TR-4.4: uv 和 venv 两种方式都有清晰说明

## [ ] Task 5: 编写 Docker 容器化部署指南
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 说明 Docker 镜像构建方法
  - 提供 docker-compose.yml 配置说明
  - 解释卷挂载（~/.hermes:/opt/data）
  - 说明权限配置（HERMES_UID/HERMES_GID）
  - 解释 s6-overlay 服务管理
  - 提供常用 docker compose 命令（up、logs、exec、down）
  - 说明环境变量传递方法
- **Acceptance Criteria Addressed**: AC-4, FR-4
- **Test Requirements**:
  - `programmatic` TR-5.1: `docker compose build` 可成功构建镜像
  - `programmatic` TR-5.2: `docker compose up -d` 后 gateway 和 dashboard 服务正常运行
  - `programmatic` TR-5.3: `docker exec hermes hermes --version` 正常输出
  - `human-judgement` TR-5.4: 卷挂载和权限配置说明清晰

## [x] Task 6: 编写配置说明章节
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 说明 .env 文件的作用和复制方法
  - 列出关键 LLM 提供商配置（OpenRouter、Fireworks、OpenAI 等）
  - 说明工具 API Key 配置（Exa、Firecrawl、Browserbase 等）
  - 解释 config.yaml 与 .env 的区别
  - 提供 `hermes setup` 交互式配置向导说明
  - 说明模型选择命令 `hermes model`
  - 包含安全提示（不要提交 .env 到版本控制）
- **Acceptance Criteria Addressed**: FR-8, AC-5, NFR-5
- **Test Requirements**:
  - `human-judgement` TR-6.1: 每个配置项有清晰的说明和获取链接
  - `human-judgement` TR-6.2: 安全提示醒目且可操作
  - `programmatic` TR-6.3: 按照文档配置后 `hermes doctor` 不报告配置缺失

## [ ] Task 7: 编写安装验证章节
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 提供版本检查命令（`hermes --version`）
  - 详细说明 `hermes doctor` 诊断命令的输出解读
  - 提供基础对话测试步骤
  - 说明工具功能验证方法（终端工具、浏览器工具等）
  - 提供 TUI 界面验证方法
  - 列出常见的"安装成功"标志
- **Acceptance Criteria Addressed**: FR-9, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: `hermes doctor` 在正确安装的环境中返回 0 退出码
  - `human-judgement` TR-7.2: 验证步骤循序渐进，从简单到复杂
  - `human-judgement` TR-7.3: 每个验证点有明确的通过/失败判断标准

## [ ] Task 8: 编写常见问题与故障排除章节
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 网络问题（GitHub 访问慢、PyPI 超时、npm 镜像）
  - Python 版本问题（3.14 不支持、版本找不到）
  - Node.js 版本问题（版本过低、npm 权限）
  - 依赖编译失败（gcc 缺失、Python.h 找不到）
  - 权限问题（sudo、文件所有权、EACCES）
  - Windows 特有问题（CRLF、长路径、pywin32）
  - Docker 特有问题（权限、卷挂载、网络模式）
  - 提供日志查看方法
  - 提供完全卸载和重装的步骤
- **Acceptance Criteria Addressed**: FR-10, AC-7, NFR-3, NFR-4
- **Test Requirements**:
  - `human-judgement` TR-8.1: 每个问题有症状描述、原因分析和解决方案
  - `human-judgement` TR-8.2: 解决方案包含具体命令，不是泛泛而谈
  - `programmatic` TR-8.3: 文档中提到的修复命令可在对应环境中执行

## [ ] Task 9: 编写升级与卸载章节
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 说明 `hermes update` 升级命令
  - 说明手动升级方法（git pull + 依赖更新）
  - 说明 Docker 镜像升级方法
  - 提供配置备份建议
  - 提供完全卸载步骤
  - 说明数据目录（~/.hermes）的保留/删除选项
- **Acceptance Criteria Addressed**: FR-11
- **Test Requirements**:
  - `programmatic` TR-9.1: 卸载步骤可彻底移除程序文件（保留用户数据的选项明确）
  - `human-judgement` TR-9.2: 升级注意事项（配置备份、依赖变化）有说明

## [ ] Task 10: 编写 Termux（Android）特殊安装说明
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 说明 Termux 环境的特殊限制
  - 提供 Termux 依赖安装命令
  - 说明 `.[termux]` 扩展的选择原因
  - 列出不支持的功能（语音、某些原生依赖）
  - 提供 Termux 特有的故障排查
- **Acceptance Criteria Addressed**: FR-12
- **Test Requirements**:
  - `human-judgement` TR-10.1: Termux 限制说明清晰，用户不会期望不支持的功能
  - `programmatic` TR-10.2: 安装命令在 Termux 环境中可执行

## [ ] Task 11: 编写国内网络环境优化指南
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 提供 PyPI 镜像源配置方法（清华、北外等）
  - 提供 npm 镜像源配置方法（淘宝镜像等）
  - 说明 GitHub 访问加速方法
  - 提供 uv 镜像配置
  - 说明 Docker 镜像加速配置
- **Acceptance Criteria Addressed**: NFR-4
- **Test Requirements**:
  - `human-judgement` TR-11.1: 镜像源地址准确且为最新
  - `programmatic` TR-11.2: 镜像配置命令可正确执行
