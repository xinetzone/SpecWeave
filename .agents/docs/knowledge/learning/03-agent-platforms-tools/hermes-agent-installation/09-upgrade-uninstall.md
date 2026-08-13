---
title: "Hermes Agent 安装方案 - 升级与卸载"
chapter: 9
source:
  - external/libs/hermes-agent/hermes_cli/update_cmd.py
  - external/libs/hermes-agent/hermes_cli/uninstall.py
  - external/libs/hermes-agent/hermes_cli/backup.py
  - external/libs/hermes-agent/hermes_cli/subcommands/update.py
  - external/libs/hermes-agent/hermes_cli/subcommands/uninstall.py
  - external/libs/hermes-agent/hermes_cli/config_defaults.py
  - external/libs/hermes-agent/hermes_constants.py
  - external/libs/hermes-agent/scripts/install.sh
  - external/libs/hermes-agent/docker-compose.yml
  - external/libs/hermes-agent/README.md
---

# 9. 升级与卸载

本章详细说明 Hermes Agent 的版本升级、配置备份、版本回滚、卸载流程以及数据目录结构。内容涵盖 `hermes update` 自动升级命令的完整工作流、手动升级步骤、Docker 镜像升级、升级前备份策略、版本回滚方法、`hermes uninstall` 卸载命令、跨平台手动卸载步骤、`~/.hermes` 数据目录说明，以及升级过程中的常见问题与解决方案。

> **升级方式选择**：本地安装（install.sh / install.ps1）使用 `hermes update` 命令升级；Docker 容器化部署通过拉取新镜像升级，容器内**不支持** `hermes update`。升级前建议先阅读 [9.4 节](#94-升级前配置备份建议) 了解备份策略。

---

## 9.1 `hermes update` 升级命令详解

`hermes update` 是 Hermes Agent 的标准升级命令，自动完成从代码拉取到依赖更新、前端重建、服务重启的全流程。该命令定义在 `hermes_cli/update_cmd.py` 的 `_cmd_update_impl` 函数中，CLI 参数定义在 `hermes_cli/subcommands/update.py`。

### 9.1.1 命令语法与参数

```bash
hermes update [选项]
```

| 参数 | 说明 |
|---|---|
| `--check` | 仅检查是否有可用更新，不执行任何安装操作 |
| `--no-backup` | 跳过本次升级前的所有备份（包括快速快照和完整备份），覆盖 `updates.pre_update_backup` 配置 |
| `--backup` | 强制执行完整备份（快速快照 + HERMES_HOME zip 包），忽略配置中的设置 |
| `--yes`, `-y` | 对所有交互式提示自动回答"是"（配置迁移、stash 恢复等）；API Key 输入将被跳过，需后续单独运行 `hermes config migrate` |
| `--branch <NAME>` | 指定更新分支（默认为 `main`）。若当前在其他分支，会先自动 stash 本地修改再切换到目标分支 |
| `--gateway` | 网关模式：使用文件 IPC 进行提示而非 stdin（内部由 `/update` 命令使用） |
| `--force` | Windows 专用：即使检测到另一个 hermes.exe 正在运行也继续升级。可能导致 WinError 32 警告和延迟替换 |
| `--force-venv` | Windows 专用：即使有其他进程正在使用 venv 解释器也修改 venv。可能导致依赖同步中途失败 |

### 9.1.2 升级流程概述

`hermes update` 的完整执行流程如下（以标准 git 安装为例）：

1. **并发检测（Windows）**：检测是否有其他 hermes.exe 进程正在运行，避免文件锁定导致升级失败
2. **暂停网关服务（Windows）**：暂停 Windows 网关服务，升级完成后自动恢复
3. **升级前备份**：根据配置执行快速快照或完整备份（详见 [9.1.3 节](#913-备份机制)）
4. **清理锁文件噪音**：丢弃 npm package-lock.json 的非确定性变动，规范化行尾符
5. **Fork 检测**：检测当前仓库是否为 fork，若为 fork 则提示添加 upstream 远程并同步
6. **获取更新**：`git fetch origin <branch>`，仅获取目标分支引用
7. **分支切换**：若当前不在目标分支，自动 stash 本地修改后切换
8. **本地修改处理**：检测工作区是否有未提交的修改，自动 stash（详见 [9.1.4 节](#914-本地修改处理)）
9. **检查更新数量**：`git rev-list HEAD..origin/<branch> --count`
10. **拉取代码**：`git merge --ff-only origin/<branch>`（快进合并）；若历史分叉则回退到 `git reset --hard origin/<branch>`
11. **语法守卫**：对关键文件执行 `py_compile` 语法检查，若发现语法错误自动回滚到拉取前的 SHA
12. **清除字节码缓存**：清除 `__pycache__` 目录，防止旧字节码导致 ImportError
13. **更新 Python 依赖**：使用 `uv pip install -e .[all]`（或回退到 pip），支持可选依赖分组的逐个回退
14. **刷新惰性后端**：刷新已激活的 lazy backend 依赖包到最新版本
15. **修复记忆提供者依赖**：修复活跃 memory provider 的 bridge 包
16. **验证关键模块导入**：在子进程中导入关键模块，检测跨模块兼容性问题
17. **更新 Node.js 依赖**：`npm install` 更新根目录及 `ui-tui`、`web` 工作区（跳过 desktop 工作区）
18. **构建 Web UI**：在 `web/` 目录执行前端构建
19. **重建桌面应用**：若检测到桌面应用已安装，按需重建 Electron 应用
20. **state.db 完整性检查**：验证 state.db 在升级后是否完好，若损坏则自动从升级前快照恢复
21. **同步技能**：同步内置技能库到所有 profile
22. **配置迁移检查**：检测新增的配置项和环境变量，交互式引导用户配置
23. **重启网关服务**：重启 systemd/launchd/Windows 网关服务

### 9.1.3 备份机制

升级前备份由 `updates.pre_update_backup` 配置项控制，在 `hermes_cli/config_defaults.py` 中默认为 `"quick"`。`_run_pre_update_backup` 函数（`update_cmd.py:2559`）实现了三种模式：

| 模式 | 配置值 | 行为 |
|---|---|---|
| 关闭 | `off` / `false` / `none` / `disabled` | 不执行任何备份 |
| 快速快照（默认） | `quick` | 创建关键状态文件的快照到 `state-snapshots/` 目录 |
| 完整备份 | `full` / `zip` / `true` | 快速快照 + HERMES_HOME 完整 zip 包到 `backups/` 目录 |

**快速快照**由 `create_quick_snapshot` 函数（`backup.py:1125`）实现，包含以下关键状态文件（`_QUICK_STATE_FILES`，`backup.py:1085`）：

- `state.db` — 会话与消息数据库
- `config.yaml` — 主配置文件
- `.env` — API 密钥与环境变量
- `auth.json` — 认证信息
- `cron/jobs.json`、`cron/executions.db` — 定时任务
- `gateway_state.json`、`processes.json` — 网关运行时状态
- `channel_directory.json`、`channel_aliases.json` — 频道配置
- `projects.db`、`response_store.db`、`memory_store.db`、`verification_evidence.db` — 项目、响应、记忆、验证数据库
- `kanban.db`、`kanban/boards/` — 看板数据
- `pairing/`、`platforms/pairing/`、`feishu_comment_pairing.json` — 平台配对信息
- `gateway/discord_message_recovery.db` — Discord 重连恢复账本

快速快照的关键特性：

- **SQLite 安全复制**：所有 `.db` 文件通过 SQLite 的 `backup()` API 复制，确保 WAL 模式下的一致性快照，不会复制到损坏的数据库
- **大小限制**：超过 1 GiB 的文件会被跳过并输出警告，防止过大的 state.db 阻塞升级流程
- **自动清理**：默认保留最近 20 份快照（`_QUICK_DEFAULT_KEEP = 20`），自动清理更旧的快照
- **跨进程锁**：使用文件锁（POSIX `flock` / Windows `msvcrt.locking`）确保同一时刻只有一个备份进程
- **存储位置**：`$HERMES_HOME/state-snapshots/<时间戳>-pre-update/`

**完整备份**在快速快照的基础上，额外创建 HERMES_HOME 目录的 zip 归档（排除 `hermes-agent/`、`node_modules/`、`venv/`、`__pycache__/`、`.cache/` 等可再生成目录），存储到 `$HERMES_HOME/backups/` 目录，可通过 `hermes import <备份文件>` 恢复。完整备份默认保留最近 5 份（`updates.backup_keep: 5`）。

### 9.1.4 本地修改处理

当工作区存在未提交的修改时，`_stash_local_changes_if_needed` 函数（`update_cmd.py:1086`）会自动处理：

1. 执行 `git status --porcelain` 检测工作区状态
2. 若存在未合并的索引条目（来自之前中断的 merge/rebase），先执行 `git reset` 清除冲突状态
3. 执行 `git stash push --include-untracked -m "hermes-update-autostash-<时间戳>"` 保存所有修改（包括未跟踪文件）
4. 升级完成后，根据运行模式决定恢复策略：

**交互式终端**（默认）：升级后提示用户是否恢复本地修改：
```
⚠ Local changes were stashed before updating.
Restore local changes now? [Y/n]
```

**非交互式更新**（`--yes`、网关模式、无 TTY）：根据 `updates.non_interactive_local_changes` 配置决定：
- `"stash"`（默认）：自动 stash 并在升级后自动恢复到更新后的代码上
- `"discard"`：自动 stash 后丢弃 stash，保持工作区干净

若 stash 恢复时发生冲突，系统会：
- 显示冲突文件列表
- 执行 `git reset --hard HEAD` 清除冲突标记（防止 SyntaxError 导致 CLI 无法启动）
- 保留 stash 条目，提示用户手动执行 `git stash apply <ref>` 恢复

### 9.1.5 自动回滚机制

`hermes update` 内置多重安全网：

**语法守卫自动回滚**：拉取代码后，`_validate_critical_files_syntax` 函数（`update_cmd.py:120`）对以下关键文件执行 `py_compile` 编译检查：

- `hermes_cli/main.py`、`hermes_cli/config.py`、`hermes_cli/__init__.py`、`hermes_cli/web_server.py`
- `cli.py`、`run_agent.py`、`model_tools.py`、`toolsets.py`、`hermes_constants.py`

若任何文件存在语法错误（如遗留的合并冲突标记），自动执行 `git reset --hard <pre_pull_sha>` 回滚到升级前的状态，确保 CLI 始终可启动。

**模块导入验证**：`_validate_critical_modules_import` 函数（`update_cmd.py:174`）在子进程中导入 `hermes_cli.main`、`run_agent`、`model_tools`、`toolsets` 等模块，检测跨模块兼容性问题（如某个模块引用了已被删除的名称）。

**state.db 自动恢复**：升级完成后，`verify_sqlite_integrity` 检查 state.db 完整性。若数据库损坏（清零、头部缺失、PRAGMA 完整性检查失败），自动从升级前快照中恢复有效的 state.db 副本。

### 9.1.6 依赖更新

**Python 依赖**：

- 优先使用项目管理的 `uv`（`hermes_cli/managed_uv.py`），执行 `uv pip install -e .[all]`
- 若 `.[all]` 安装失败，自动回退到逐个安装可选依赖分组，确保更新不会静默剥离可用的功能
- Termux 环境使用 `termux-all` 可选分组
- 更新前自动升级 pip（防止旧版 pip 在源码构建时失败导致 venv 部分写入）
- 更新后刷新已激活的惰性后端（lazy backends），修复记忆提供者的 bridge 包

> **手动升级提示**：`hermes update` 内部使用 `uv pip install`（灵活解析依赖）；手动升级时推荐使用 `uv sync --extra all`，它基于 `uv.lock` 锁文件进行哈希校验安装，安全性更高（与安装脚本 `install.sh` 的 Tier 0 路径一致）。

**Node.js 依赖**（`_update_node_dependencies`，`update_cmd.py:2053`）：

- 通过 lockfile 哈希判断是否需要执行 `npm install`，未变化则跳过
- 第一步：根目录安装（`--workspaces=false`），不递归工作区
- 第二步：安装 `ui-tui` 和 `web` 工作区依赖
- **跳过 desktop 工作区**：避免下载约 200MB 的 Electron 二进制文件，桌面应用依赖按需安装
- npm 参数：`--no-fund --no-audit --prefer-offline --progress=false`
- WSL 环境下若仅能访问 Windows 版 npm，会跳过并输出明确警告

### 9.1.7 检查更新

使用 `--check` 参数仅检查更新而不安装：

```bash
hermes update --check
```

该命令由 `_cmd_update_check` 函数（`update_cmd.py:2201`）实现，执行 `git fetch` 后报告本地与远程的提交差异，不修改任何文件。

### 9.1.8 Windows ZIP 回退更新

在 Windows 上，当 git 文件 I/O 损坏（杀毒软件、NTFS 过滤驱动导致"Invalid argument"错误）且 `.git` 目录不存在时，`_update_via_zip` 函数（`update_cmd.py:725`）会通过下载 GitHub ZIP 归档进行更新：

1. 从 `https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip` 下载
2. 解压后使用两阶段原子替换（stage-then-swap）更新文件，保留 `venv/`、`node_modules/`、`.git/`、`.env`
3. 更新 Python 依赖和 Node.js 依赖，构建 Web UI
4. 该路径**不支持** `--branch` 参数（ZIP 仅提供 main 分支）

---

## 9.2 手动升级方法

当 `hermes update` 不可用或需要更精细的控制时，可以手动执行升级步骤。以下是跨平台的手动升级流程。

### 9.2.1 定位安装目录

Hermes Agent 的代码安装位置：

| 平台 | 默认安装目录 |
|---|---|
| Linux / macOS | `~/.hermes/hermes-agent` |
| Windows（原生） | `%LOCALAPPDATA%\hermes\hermes-agent` |
| Docker | `/opt/hermes`（容器内，不可手动升级） |

若设置了 `HERMES_HOME` 环境变量，代码目录通常位于 `$HERMES_HOME/hermes-agent`。

### 9.2.2 Linux / macOS 手动升级

```bash
# 1. 进入安装目录
cd ~/.hermes/hermes-agent

# 2. 拉取最新代码
git fetch origin main
git merge --ff-only origin/main

# 3. 更新 Python 依赖（推荐使用 uv sync，基于 uv.lock 哈希校验）
uv sync --extra all

# 若 uv.lock 不存在或不同步，回退到：
# uv pip install -e .[all]

# 若未安装 uv，使用 venv 中的 pip：
# source venv/bin/activate
# pip install -e .[all]

# 4. 更新 Node.js 依赖
npm install --no-fund --no-audit --prefer-offline

# 5. 构建前端（Web UI）
cd web && npm run build && cd ..

# 6. 重启网关服务（若正在运行）
hermes gateway restart
```

### 9.2.3 Windows 手动升级

在 PowerShell 或 Git Bash 中执行：

```powershell
# 1. 进入安装目录
cd $env:LOCALAPPDATA\hermes\hermes-agent

# 2. 拉取最新代码
git fetch origin main
git merge --ff-only origin/main

# 3. 更新 Python 依赖（推荐使用 uv sync）
uv sync --extra all

# 若未安装 uv 或 uv.lock 不同步，使用 venv 中的 pip：
# .\venv\Scripts\python.exe -m pip install -e .[all]

# 4. 更新 Node.js 依赖
npm install --no-fund --no-audit --prefer-offline

# 5. 构建前端
cd web
npm run build
cd ..

# 6. 重启网关
hermes gateway restart
```

> **注意**：手动升级前请确保已关闭所有 Hermes 进程（桌面应用、网关、终端 REPL），否则 Windows 上可能因文件锁定导致 `pip install` 失败。

### 9.2.4 手动升级后的验证

```bash
# 验证 CLI 可正常启动
hermes --version

# 运行诊断
hermes doctor

# 验证关键模块导入
python -c "import hermes_cli.main; import run_agent; print('OK')"
```

---

## 9.3 Docker 镜像升级

Docker 容器化部署的升级方式与本地安装完全不同——容器内**不支持** `hermes update`，版本更新通过拉取新镜像并重建容器实现。数据通过挂载的卷持久化保留。

### 9.3.1 升级步骤

```bash
# 1. 进入 docker-compose.yml 所在目录
cd /path/to/hermes-agent

# 2. 拉取最新镜像
#    若使用预构建镜像：
docker compose pull

#    若从源码本地构建镜像：
docker compose build --pull

# 3. 重建并启动容器（数据卷自动保留）
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d

# 4. 查看启动日志
docker compose logs -f gateway
```

### 9.3.2 数据卷保留机制

`docker-compose.yml` 中将宿主机的 `~/.hermes` 目录挂载到容器内的 `/opt/data`：

```yaml
volumes:
  - ~/.hermes:/opt/data
environment:
  - HERMES_UID=${HERMES_UID:-10000}
  - HERMES_GID=${HERMES_GID:-10000}
```

升级容器镜像时，`~/.hermes` 目录中的所有数据（配置、会话、技能、记忆等）不会受到影响。容器重建后，s6-overlay 的 stage2 hook 会自动处理文件所有权（通过 `HERMES_UID`/`HERMES_GID` 重新映射容器内 `hermes` 用户），确保宿主机用户仍可读写数据文件。

### 9.3.3 Docker 升级注意事项

- **HERMES_UID / HERMES_GID**：升级时保持与首次部署一致，否则可能导致文件权限问题。默认值为 `10000`
- **镜像标签**：若使用 `hermes-agent:latest` 标签，`docker compose pull` 会拉取最新版；若使用固定版本标签，需修改 `docker-compose.yml` 中的 `image` 字段
- **网络模式**：默认使用 `network_mode: host`，升级后网络配置不变
- **配置迁移**：新版本首次启动时，容器内的 Hermes 会自动检测并执行配置迁移（与本地安装一致）
- **回滚**：若新版本有问题，可修改镜像标签回旧版本后重新 `docker compose up -d`，数据卷保持不变

---

## 9.4 升级前配置备份建议

虽然 `hermes update` 默认会执行快速快照（`updates.pre_update_backup: quick`），但在跨大版本升级、生产环境或重要数据场景下，建议手动执行更完整的备份。

### 9.4.1 必须备份的关键数据

以下数据存储在 `$HERMES_HOME` 目录中，是升级前需要重点关注的内容：

| 数据 | 文件/目录 | 说明 | 备份优先级 |
|---|---|---|---|
| 环境变量与密钥 | `.env` | API 密钥、服务凭证等敏感信息 | ★★★ 最高 |
| 主配置 | `config.yaml` | 所有 Hermes 配置项 | ★★★ 最高 |
| 认证信息 | `auth.json` | 认证令牌 | ★★★ 最高 |
| 会话数据 | `state.db` | 所有对话历史、消息记录（SQLite） | ★★★ 最高 |
| 定时任务 | `cron/jobs.json`、`cron/executions.db` | 计划任务定义与执行记录 | ★★☆ 高 |
| 技能库 | `skills/` | 用户自定义和修改的技能 | ★★☆ 高 |
| 记忆数据 | `memory_store.db` | 全息记忆事实与实体 | ★★☆ 高 |
| 项目数据 | `projects.db` | 项目存储 | ★★☆ 高 |
| 看板数据 | `kanban.db`、`kanban/` | 看板与任务板 | ★☆☆ 中 |
| 网关状态 | `gateway_state.json`、`channel_directory.json` | 网关与频道配置 | ★☆☆ 中 |
| 配对信息 | `pairing/`、`platforms/pairing/` | 消息平台配对凭证 | ★★☆ 高 |

### 9.4.2 使用内置备份命令

```bash
# 完整备份（创建 zip 归档到 backups/ 目录）
hermes backup

# 快速快照（仅关键状态文件到 state-snapshots/ 目录）
hermes backup --quick

# 升级前强制执行完整备份
hermes update --backup
```

完整备份的 zip 文件可通过以下命令恢复：

```bash
hermes import /path/to/backup.zip
```

### 9.4.3 手动备份方式

若需要额外的异地备份，可直接复制关键文件：

```bash
# Linux / macOS — 创建带时间戳的备份目录
BACKUP_DIR=~/hermes-backup-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

cp ~/.hermes/.env "$BACKUP_DIR/"
cp ~/.hermes/config.yaml "$BACKUP_DIR/"
cp ~/.hermes/auth.json "$BACKUP_DIR/"
cp ~/.hermes/state.db "$BACKUP_DIR/"
cp -r ~/.hermes/cron "$BACKUP_DIR/"
cp -r ~/.hermes/skills "$BACKUP_DIR/"
cp -r ~/.hermes/memory "$BACKUP_DIR/" 2>/dev/null || true

# 使用 SQLite 安全复制（推荐，避免 WAL 模式下的一致性问题）
sqlite3 ~/.hermes/state.db ".backup '$BACKUP_DIR/state.db'"
```

```powershell
# Windows PowerShell
$backupDir = "$env:USERPROFILE\hermes-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force

Copy-Item "$env:LOCALAPPDATA\hermes\.env" $backupDir
Copy-Item "$env:LOCALAPPDATA\hermes\config.yaml" $backupDir
Copy-Item "$env:LOCALAPPDATA\hermes\state.db" $backupDir
Copy-Item "$env:LOCALAPPDATA\hermes\cron" $backupDir -Recurse
Copy-Item "$env:LOCALAPPDATA\hermes\skills" $backupDir -Recurse
```

### 9.4.4 Docker 环境备份

Docker 环境的数据位于宿主机挂载的 `~/.hermes` 目录（对应容器内 `/opt/data`），备份方式与本地安装相同：

```bash
# 在宿主机上执行
tar czf hermes-docker-backup-$(date +%Y%m%d).tar.gz -C ~ .hermes
```

---

## 9.5 版本回滚方法

若升级后遇到问题，可通过 Git 回滚到之前的版本。`hermes update` 在拉取代码前会记录当前 HEAD SHA（`pre_pull_sha`），并在语法检查失败时自动回滚。手动回滚步骤如下。

### 9.5.1 查看可用版本

```bash
cd ~/.hermes/hermes-agent

# 查看最近的提交记录
git log --oneline -20

# 查看操作记录（包括被 reset 的提交）
git reflog -20
```

### 9.5.2 回滚到指定版本

**方式一：检出指定提交（临时查看/测试）**

```bash
# 查看某个版本而不修改当前分支
git checkout <commit-sha>

# 测试完成后回到 main
git checkout main
```

**方式二：硬重置到之前的版本（永久回滚）**

```bash
# 重置到升级前的提交（使用 git reflog 找到之前的 SHA）
git reset --hard <prev-commit-sha>

# 然后重新安装对应版本的依赖
uv sync --extra all
# 或回退方式：uv pip install -e .[all]
npm install --no-fund --no-audit --prefer-offline
cd web && npm run build && cd ..
```

**方式三：创建回滚分支（保留历史）**

```bash
# 从当前状态创建备份分支
git branch backup-before-rollback

# 重置到目标版本
git reset --hard <target-commit-sha>

# 重新安装依赖
uv sync --extra all
```

### 9.5.3 恢复升级前的 stash

若升级时本地修改被 stash 且需要恢复：

```bash
# 查看 stash 列表
git stash list

# 恢复指定的 stash
git stash apply stash@{0}

# 恢复后删除 stash
git stash drop stash@{0}
```

### 9.5.4 从快照恢复数据

若升级后 state.db 损坏或数据丢失，可从升级前快照恢复：

```bash
# 列出可用快照
ls -la ~/.hermes/state-snapshots/

# 手动恢复 state.db
cp ~/.hermes/state-snapshots/<snapshot-id>/state.db ~/.hermes/state.db

# 或使用完整备份恢复
hermes import ~/.hermes/backups/<backup-file>.zip
```

### 9.5.5 Docker 环境回滚

Docker 环境通过镜像标签回滚，数据不受影响：

```bash
# 修改 docker-compose.yml 中的 image 标签为旧版本
# 例如：image: hermes-agent:v1.2.3

# 重建容器
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d
```

---

## 9.6 `hermes uninstall` 卸载命令

`hermes uninstall` 命令提供交互式卸载流程，支持保留数据和完全删除两种模式。卸载逻辑实现在 `hermes_cli/uninstall.py`，CLI 参数定义在 `hermes_cli/subcommands/uninstall.py`。

### 9.6.1 命令语法与参数

```bash
hermes uninstall [选项]
```

| 参数 | 说明 |
|---|---|
| `--full` | 完全卸载：删除代码和所有配置/数据（`~/.hermes/`） |
| `--gui` | 仅卸载桌面 Chat GUI，保留 Agent 和数据 |
| `--gui-summary` | 以 JSON 格式输出已安装的 GUI/Agent 组件摘要后退出 |
| `--yes`, `-y` | 跳过确认提示（非交互式） |
| `--dry-run` | 仅打印将要删除的内容，不做任何修改 |

### 9.6.2 交互式卸载

直接运行 `hermes uninstall` 进入交互式界面：

```
┌─────────────────────────────────────────────────────────┐
│            ⚕ Hermes Agent Uninstaller                  │
└─────────────────────────────────────────────────────────┘

Current Installation:
  Code:    /home/user/.hermes/hermes-agent
  Config:  /home/user/.hermes/config.yaml
  Secrets: /home/user/.hermes/.env
  Data:    /home/user/.hermes/cron/, /home/user/.hermes/sessions/, /home/user/.hermes/logs/

Uninstall Options:

  1) Keep data - Remove code only, keep configs/sessions/logs
     (Recommended - you can reinstall later with your settings intact)

  2) Full uninstall - Remove everything including all data
     (Warning: This deletes all configs, sessions, and logs permanently)

  3) Cancel - Don't uninstall

Select option [1/2/3]:
```

**选项 1：保留数据（推荐）**

删除代码和可执行文件，但保留 `~/.hermes/` 中的配置、会话、日志等数据。重新安装后可直接使用原有配置。

**选项 2：完全卸载**

删除所有内容，包括代码、配置、API 密钥、会话记录、定时任务和日志。此操作不可逆。若存在命名 profile，会额外询问是否一并删除。

### 9.6.3 非交互式卸载

```bash
# 保留数据的非交互式卸载
hermes uninstall --yes

# 完全卸载（删除所有数据）
hermes uninstall --full --yes

# 预览将要删除的内容
hermes uninstall --dry-run
hermes uninstall --full --dry-run
```

### 9.6.4 卸载执行步骤

`_perform_uninstall` 函数（`uninstall.py:756`）按以下顺序执行：

1. **停止网关服务**：`uninstall_gateway_service()` 停止并卸载：
   - Linux：systemd 用户级和系统级服务（`systemctl stop/disable`，删除 unit 文件，`daemon-reload`）
   - macOS：launchd plist（`launchctl unload`，删除 plist）
   - Windows：计划任务和启动文件夹条目（通过 `gateway_windows.uninstall()`）
   - 所有平台：杀死独立运行的 `hermes gateway run` 进程
   - Termux/Android：跳过 systemd，仅杀死独立进程

2. **清理 PATH 环境变量**：
   - POSIX：从 `.bashrc`、`.bash_profile`、`.profile`、`.zshrc`、`.zprofile` 中移除 Hermes PATH 条目
   - Windows：从注册表 `HKCU\Environment` 的 User-scope PATH 中移除 Hermes 相关条目
   - 使用原子写入（`atomic_write_text`），防止写入过程中终端中断导致 shell rc 文件被截断

3. **删除环境变量（Windows）**：删除 `HERMES_HOME` 和 `HERMES_GIT_BASH_PATH` 用户级环境变量

4. **删除包装脚本**：删除 `~/.local/bin/hermes`、`~/.local/bin/hermes-acp`、`/usr/local/bin/hermes` 等路径下的 hermes 命令包装脚本（仅删除包含 `hermes_cli` 或 `hermes-agent` 引用的脚本）

5. **删除 Node 符号链接**：删除安装程序创建的 `node`、`npm`、`npx` 符号链接（仅删除指向 Hermes node 目录的链接，不影响用户自行安装的 nvm/fnm 管理的 Node）

6. **删除桌面 GUI 组件**：删除 Electron 构建产物、打包的应用包和 Electron userData 目录

7. **删除代码目录**：删除 `hermes-agent` 安装目录

8. **删除 Windows 安装工具**（仅 Windows）：删除 PortableGit、捆绑的 Node.js、gateway-service 目录（这些是安装工具，不是用户数据，即使在"保留数据"模式下也会删除）

9. **删除数据目录**（仅 `--full` 模式）：删除整个 `$HERMES_HOME` 目录及所有命名 profile

---

## 9.7 手动卸载步骤

当 `hermes uninstall` 命令不可用（如安装已损坏）时，可按以下步骤手动卸载。

### 9.7.1 Linux / macOS 手动卸载

```bash
# 1. 停止网关服务
hermes gateway stop 2>/dev/null

# 若使用 systemd 用户服务：
systemctl --user stop hermes-gateway 2>/dev/null
systemctl --user disable hermes-gateway 2>/dev/null
rm -f ~/.config/systemd/user/hermes-gateway.service 2>/dev/null
systemctl --user daemon-reload 2>/dev/null

# 若使用 systemd 系统服务（需要 sudo）：
sudo systemctl stop hermes-gateway 2>/dev/null
sudo systemctl disable hermes-gateway 2>/dev/null
sudo rm -f /etc/systemd/system/hermes-gateway.service 2>/dev/null
sudo systemctl daemon-reload 2>/dev/null

# 若使用 launchd（macOS）：
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/ai.hermes.gateway.plist 2>/dev/null

# 2. 杀死残留的 Hermes 进程
pkill -f "hermes gateway" 2>/dev/null
pkill -f "hermes_cli" 2>/dev/null

# 3. 删除包装脚本
rm -f ~/.local/bin/hermes ~/.local/bin/hermes-acp ~/.local/bin/hermes-agent
sudo rm -f /usr/local/bin/hermes /usr/local/bin/hermes-acp /usr/local/bin/hermes-agent

# 4. 删除 Node 符号链接（仅删除指向 Hermes 的链接）
rm -f ~/.local/bin/node ~/.local/bin/npm ~/.local/bin/npx

# 5. 清理 shell 配置中的 PATH 条目
#    手动编辑 ~/.bashrc 或 ~/.zshrc，删除包含 "hermes" 的 PATH 行
#    例如删除类似下面的行：
#    export PATH="$HOME/.hermes/hermes-agent/venv/bin:$PATH"

# 6. 删除代码目录
rm -rf ~/.hermes/hermes-agent

# 7a. 保留数据（推荐）：数据保留在 ~/.hermes/ 中，重新安装后可继续使用

# 7b. 完全删除（谨慎）：
# rm -rf ~/.hermes
```

### 9.7.2 Windows 手动卸载

在 PowerShell（以当前用户身份）中执行：

```powershell
# 1. 停止网关
hermes gateway stop 2>$null

# 2. 删除计划任务（若存在）
schtasks /Delete /TN "Hermes Gateway" /F 2>$null

# 3. 删除启动文件夹条目
$startup = [Environment]::GetFolderPath("Startup")
Remove-Item "$startup\Hermes Gateway.lnk" -Force -ErrorAction SilentlyContinue

# 4. 杀死残留进程
Get-Process | Where-Object { $_.Path -like "*hermes*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# 5. 删除 User-scope 环境变量
[Environment]::SetEnvironmentVariable("HERMES_HOME", $null, "User")
[Environment]::SetEnvironmentVariable("HERMES_GIT_BASH_PATH", $null, "User")

# 6. 从 User PATH 中移除 Hermes 条目
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$entries = $userPath -split ";" | Where-Object { $_ -notlike "*hermes*" }
$newPath = $entries -join ";"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# 7. 删除安装目录
$hermesHome = $env:LOCALAPPDATA + "\hermes"
Remove-Item "$hermesHome\hermes-agent" -Recurse -Force -ErrorAction SilentlyContinue

# 8. 删除 Windows 安装工具（PortableGit、Node、gateway-service）
Remove-Item "$hermesHome\git" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$hermesHome\node" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$hermesHome\gateway-service" -Recurse -Force -ErrorAction SilentlyContinue

# 9a. 保留数据：$hermesHome 中的 config.yaml、.env、state.db 等保留

# 9b. 完全删除（谨慎）：
# Remove-Item $hermesHome -Recurse -Force
```

手动卸载后需要**打开新的终端窗口**才能使 PATH 和环境变量变更生效。

### 9.7.3 Docker 环境卸载

```bash
# 1. 进入 docker-compose.yml 所在目录
cd /path/to/hermes-agent

# 2. 停止并删除容器
docker compose down

# 3. 删除镜像（可选）
docker rmi hermes-agent

# 4. 数据处理：
#    保留数据：~/.hermes/ 目录不受 docker compose down 影响
#    完全删除：
rm -rf ~/.hermes
```

若使用了 Docker 命名卷而非绑定挂载，先查看卷名再决定是否删除：

```bash
# 查看 Docker 卷
docker volume ls | grep hermes

# 删除关联卷（谨慎，会删除所有数据）
docker compose down -v
```

---

## 9.8 数据目录 `~/.hermes` 结构说明

Hermes Agent 的所有用户数据存储在 HERMES_HOME 目录中。路径解析逻辑见 `hermes_constants.py`：

| 平台 | 默认路径 |
|---|---|
| Linux / macOS | `~/.hermes/` |
| Windows（原生） | `%LOCALAPPDATA%\hermes\`（通常为 `C:\Users\<用户>\AppData\Local\hermes\`） |
| Docker 容器内 | `/opt/data/`（从宿主机 `~/.hermes/` 挂载） |

可通过 `HERMES_HOME` 环境变量自定义路径。

### 9.8.1 目录结构总览

```
$HERMES_HOME/
├── .env                    # API 密钥与环境变量（敏感，需备份）
├── config.yaml             # 主配置文件（需备份）
├── auth.json               # 认证令牌（需备份）
├── state.db                # 会话与消息数据库（SQLite，需备份）
├── state.db-wal            # SQLite WAL 日志（临时，可删除）
├── state.db-shm            # SQLite 共享内存（临时，可删除）
├── gateway_state.json      # 网关运行时状态（机器相关，可不备份）
├── channel_directory.json  # 频道目录
├── channel_aliases.json    # 频道别名
├── processes.json          # 进程注册表（机器相关，可不备份）
├── projects.db             # 项目数据库
├── response_store.db       # 网关对话历史/工具载荷
├── memory_store.db         # 全息记忆事实与实体
├── verification_evidence.db # 验证审计记录
├── kanban.db               # 默认看板数据库
├── feishu_comment_pairing.json # 飞书评论配对
├── hermes-agent/           # 代码检出目录（可重新克隆，不需备份）
├── venv/                   # Python 虚拟环境（可重建，不需备份）
├── node/                   # Node.js 运行时（可重新下载，不需备份）
├── web/                    # Web UI 构建产物（可重建，不需备份）
├── skills/                 # 技能库（用户修改的需备份）
│   ├── .archive/           # 技能归档（可恢复，建议备份）
│   └── ...
├── cron/                   # 定时任务
│   ├── jobs.json           # 任务定义（需备份）
│   └── executions.db       # 执行记录（可备份）
├── kanban/                 # 非默认看板
│   └── boards/
├── pairing/                # 平台配对信息（旧位置，需备份）
├── platforms/
│   └── pairing/            # 平台配对信息（新位置，需备份）
├── gateway/                # 网关数据
│   └── discord_message_recovery.db
├── profiles/               # 命名 profile 目录
│   └── <profile-name>/
├── backups/                # 完整备份 zip 归档
├── state-snapshots/        # 快速快照目录
│   └── <timestamp>-pre-update/
├── logs/                   # 日志文件（可安全删除）
│   ├── gateway.log
│   ├── update.log
│   └── errors.log
├── cache/                  # 各种缓存（可安全删除）
│   ├── model_catalog.json
│   └── images/
└── .update_check           # 更新检查缓存（可删除）
```

### 9.8.2 需要备份的数据

以下数据不可自动重建，升级或卸载前应备份：

| 路径 | 类型 | 说明 |
|---|---|---|
| `.env` | 文件 | API 密钥，泄露后需重新生成 |
| `config.yaml` | 文件 | 所有用户配置 |
| `auth.json` | 文件 | OAuth 令牌和认证状态 |
| `state.db` | SQLite | 全部对话历史 |
| `cron/jobs.json` | JSON | 定时任务定义 |
| `skills/` | 目录 | 特别是用户创建或修改的技能 |
| `memory_store.db` | SQLite | 长期记忆数据 |
| `projects.db` | SQLite | 项目上下文 |
| `pairing/`、`platforms/pairing/` | 目录 | 消息平台配对凭证 |
| `kanban.db`、`kanban/` | 数据库/目录 | 看板任务 |
| `response_store.db` | SQLite | 网关工具调用历史 |
| `verification_evidence.db` | SQLite | 验证审计记录 |
| `profiles/` | 目录 | 命名 profile 的所有数据 |

### 9.8.3 可安全删除的数据

以下数据可自动重建，磁盘空间不足时可安全删除：

| 路径 | 类型 | 说明 |
|---|---|---|
| `hermes-agent/` | 目录 | 代码仓库，可通过 `git clone` 重新获取 |
| `venv/` | 目录 | Python 虚拟环境，可通过 `uv pip install` 重建 |
| `node/` | 目录 | Node.js 运行时，安装程序可重新下载 |
| `node_modules/` | 目录 | Node.js 依赖，可通过 `npm install` 重建 |
| `__pycache__/` | 目录 | Python 字节码缓存，导入时自动生成 |
| `logs/` | 目录 | 日志文件，删除不影响功能 |
| `cache/` | 目录 | 模型目录缓存、图片缓存等，可重新下载 |
| `backups/` | 目录 | 旧备份归档，可按需清理 |
| `state-snapshots/` | 目录 | 旧快照，自动保留最近 20 份 |
| `*.db-wal`、`*.db-shm` | 文件 | SQLite 临时文件，正常关闭后自动清理 |
| `.update_check` | 文件 | 更新检查缓存，自动重新生成 |
| `*.pid` | 文件 | 进程 PID 文件（`gateway.pid`、`cron.pid`） |
| `.backup.lock` | 文件 | 备份锁文件，陈旧时可删除 |

### 9.8.4 Profile 目录结构

使用命名 profile 时（`hermes --profile <name>`），每个 profile 的数据位于 `$HERMES_HOME/profiles/<name>/`，结构与根目录类似。卸载时需注意：

- `hermes uninstall --full` 在交互模式下会询问是否删除命名 profile
- `--yes` 非交互模式下**不会**自动删除命名 profile（防止意外数据丢失）
- 需手动删除 profile 目录或在交互模式下确认
- 每个 profile 有独立的网关服务和别名包装脚本（`~/.local/bin/<profile-name>`）

---

## 9.9 升级常见问题

### 9.9.1 Python 依赖冲突

**【症状】**

- `hermes update` 在"Updating Python dependencies"阶段失败
- 错误信息包含 `ResolutionImpossible`、`conflicting dependencies`、`pip install` 返回非零退出码
- 更新后 `hermes` 命令无法启动，报 `ImportError` 或 `ModuleNotFoundError`

**【原因】**

- 旧版本依赖与新版本的依赖约束不兼容
- venv 中存在手动安装的包与项目要求冲突
- uv 或 pip 版本过旧，无法正确解析依赖
- Windows 上其他进程锁定了 `.pyd` 文件，导致安装中途失败

**【解决方案】**

1. **重新运行更新**——部分依赖冲突是暂时的，`hermes update` 会自动尝试逐个安装可选依赖分组：
   ```bash
   hermes update
   ```

2. **关闭所有 Hermes 进程后重试**（Windows 常见）：
   ```bash
   hermes gateway stop
   # 关闭桌面应用和所有终端中的 hermes 进程
   hermes update
   ```

3. **重建虚拟环境**（彻底解决依赖冲突）：
   ```bash
   cd ~/.hermes/hermes-agent
   rm -rf venv
   uv venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   uv sync --extra all
   # 若 uv.lock 不同步，回退到：uv pip install -e .[all]
   ```

4. **运行 doctor 诊断和修复**：
   ```bash
   hermes doctor --fix
   ```

5. **使用 `--force-venv`**（Windows，仅当确认锁定进程为误报时）：
   ```bash
   hermes update --force-venv
   ```

### 9.9.2 Node.js 依赖或前端构建失败

**【症状】**

- 更新完成后提示"Node.js dependencies for ... did not refresh"
- Web UI 无法访问或显示空白页面
- 错误信息包含 `npm ERR!`、`node-gyp`、`ELIFECYCLE`

**【原因】**

- npm lockfile 变动导致部分安装失败
- WSL 环境中仅能访问 Windows 版 npm（路径不兼容）
- 网络问题导致 npm 包下载失败
- Node.js 版本不兼容

**【解决方案】**

1. **手动重新安装 Node 依赖并构建**：
   ```bash
   cd ~/.hermes/hermes-agent
   npm install --no-fund --no-audit
   cd web && npm run build && cd ..
   ```

2. **WSL 用户**：确保在 WSL 内部安装了 Linux 版 Node.js，而非使用 Windows 版：
   ```bash
   # 在 WSL 内安装 Node.js（使用 nvm）
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
   nvm install --lts
   ```

3. **清除 npm 缓存后重试**：
   ```bash
   npm cache clean --force
   rm -rf node_modules
   npm install
   ```

4. **Node 依赖刷新失败不影响核心功能**：CLI 和网关仍可正常工作，仅 Dashboard/TUI 可能处于混合状态。修复 npm 后重新运行 `hermes update` 即可。

### 9.9.3 配置迁移问题

**【症状】**

- 升级后出现"new required settings need configuration"提示
- 某些功能无法正常工作，日志中报缺少配置项
- `--yes` 升级后 API Key 相关功能不可用

**【原因】**

- 新版本引入了新的必需环境变量或配置字段
- 配置文件格式版本过旧（`config.yaml` 中的 `version` 字段低于当前版本）
- `--yes` 模式跳过了 API Key 的交互式输入

**【解决方案】**

1. **手动运行配置迁移向导**：
   ```bash
   hermes config migrate
   ```

2. **检查缺失的配置项**：
   ```bash
   hermes config get
   ```

3. **交互式更新**（不使用 `--yes`），在提示时逐项配置新选项：
   ```bash
   hermes update
   ```

4. **配置版本仅格式变更时**（无新设置需要填写），系统会自动静默升级版本号，无需干预。

### 9.9.4 版本不兼容或升级后无法启动

**【症状】**

- 升级后执行 `hermes` 命令报 SyntaxError 或 ImportError
- 网关服务无法启动
- 桌面应用白屏或崩溃

**【原因】**

- 拉取的代码存在未被 CI 发现的语法错误（极少数情况）
- 依赖安装中途中断（网络问题、进程被杀、磁盘空间不足）
- 本地修改的 stash 恢复与新代码冲突
- Python 或 Node.js 版本不满足新版本要求

**【解决方案】**

1. **检查 Python 和 Node.js 版本**是否满足新版本要求（参见 [第 1 章](01-environment.md)）：
   ```bash
   python --version
   node --version
   ```

2. **回滚到之前的版本**（详见 [9.5 节](#95-版本回滚方法)）：
   ```bash
   cd ~/.hermes/hermes-agent
   git reflog -10
   git reset --hard <prev-commit-sha>
   uv sync --extra all
   ```

3. **清除字节码缓存后重试**：
   ```bash
   find ~/.hermes/hermes-agent -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
   hermes update
   ```

4. **从备份恢复数据后重新安装**：
   ```bash
   hermes import ~/.hermes/backups/<backup-file>.zip
   # 然后重新运行安装脚本
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```

5. **运行诊断**：
   ```bash
   hermes doctor
   hermes doctor --fix
   ```

### 9.9.5 Windows 文件锁定导致升级失败

**【症状】**

- 错误信息包含 `WinError 32`、`Permission denied`、`file is being used by another process`
- 提示"Another hermes.exe is running"
- 依赖安装中途失败，venv 处于半更新状态

**【原因】**

- Hermes 桌面应用、网关或终端 REPL 正在运行，锁定了 venv 中的 `.pyd`/`.exe` 文件
- 杀毒软件正在扫描文件
- NTFS 过滤驱动干扰 git 文件操作

**【解决方案】**

1. **关闭所有 Hermes 进程**：
   ```powershell
   # 停止网关
   hermes gateway stop

   # 关闭桌面应用窗口

   # 检查残留进程
   Get-Process | Where-Object { $_.Path -like "*hermes*" }
   # 强制终止残留进程（将 <PID> 替换为实际进程 ID）
   taskkill /PID <PID> /F
   ```

2. **临时禁用杀毒软件实时防护**后重试升级

3. **使用 `--force` 参数**（仅当确认进程已关闭但检测为误报时）：
   ```powershell
   hermes update --force
   ```

4. **若 git 文件 I/O 持续损坏**，安装程序会自动回退到 ZIP 更新模式，也可手动重新安装：
   ```powershell
   iex (irm https://hermes-agent.nousresearch.com/install.ps1)
   ```

### 9.9.6 本地修改冲突

**【症状】**

- 升级后提示"restoring local changes hit conflicts"
- 某些源文件中出现 Git 冲突标记（`<<<<<<<`、`=======`、`>>>>>>>`）
- CLI 无法启动，报 SyntaxError

**【原因】**

- 用户手动修改了 Hermes 源代码，升级后 stash 恢复时与新代码冲突

**【解决方案】**

1. **系统已自动执行 `git reset --hard HEAD`** 清除冲突标记，确保 CLI 可启动
2. **手动审查并恢复修改**：
   ```bash
   cd ~/.hermes/hermes-agent
   git stash list
   git stash apply stash@{0}
   # 手动解决冲突后：
   git stash drop stash@{0}
   ```
3. **若不需要保留本地修改**，直接丢弃 stash：
   ```bash
   git stash drop stash@{0}
   ```

### 9.9.7 state.db 损坏

**【症状】**

- 升级后会话历史消失
- 日志中出现"database disk image is malformed"
- 错误提示"state.db is corrupted after update"

**【原因】**

- 升级过程中数据库文件被异常修改（杀毒软件、磁盘错误、进程强制终止）
- SQLite WAL 文件与主数据库不一致

**【解决方案】**

1. **系统通常会自动从升级前快照恢复**，注意观察输出中的"Auto-restored from snapshot"消息
2. **手动恢复**：
   ```bash
   # 列出可用快照
   ls ~/.hermes/state-snapshots/

   # 从快照恢复
   cp ~/.hermes/state-snapshots/<snapshot-id>/state.db ~/.hermes/state.db
   ```
3. **从完整备份恢复**：
   ```bash
   hermes import ~/.hermes/backups/<backup-file>.zip
   ```
4. **SQLite 完整性检查**：
   ```bash
   sqlite3 ~/.hermes/state.db "PRAGMA integrity_check;"
   ```

### 9.9.8 Docker 升级后权限问题

**【症状】**

- 容器日志中出现 `Permission denied` 错误
- 容器内无法写入 `/opt/data/` 目录
- 网关无法创建状态文件

**【原因】**

- `HERMES_UID`/`HERMES_GID` 与宿主机 `~/.hermes` 目录的所有者不匹配

**【解决方案】**

```bash
# 确保使用正确的 UID/GID 启动容器
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d

# 若之前使用了错误的 UID/GID，修复宿主机文件所有权
sudo chown -R $(id -u):$(id -g) ~/.hermes

# 然后重启容器
docker compose restart
```

### 9.9.9 升级后网关无法启动

**【症状】**

- `hermes gateway run` 启动失败
- systemd/launchd 服务状态为 failed
- 日志中报配置或导入错误

**【解决方案】**

1. **检查网关状态和日志**：
   ```bash
   hermes gateway status
   hermes logs gateway
   ```

2. **前台运行以查看详细错误**：
   ```bash
   hermes gateway run
   ```

3. **重新安装网关服务**：
   ```bash
   hermes gateway uninstall
   hermes gateway install
   hermes gateway start
   ```

4. **运行诊断**：
   ```bash
   hermes doctor
   ```

### 9.9.10 更新检查缓存陈旧

**【症状】**

- `hermes update --check` 报告有更新，但实际 `hermes update` 提示"Already up to date"
- 升级后仍显示"commits behind"提示

**【原因】**

- 各 profile 的更新检查缓存未及时清除

**【解决方案】**

`hermes update` 成功后会自动清除所有 profile 的 `.update_check` 缓存。若缓存未正确清除，可手动删除：

```bash
find ~/.hermes -name ".update_check" -delete
```
