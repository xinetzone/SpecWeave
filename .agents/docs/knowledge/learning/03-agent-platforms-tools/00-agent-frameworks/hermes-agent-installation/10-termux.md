---
title: "Hermes Agent 安装方案 - Termux（Android）特殊安装说明"
chapter: 10
source:
  - external/libs/hermes-agent/scripts/install.sh
  - external/libs/hermes-agent/constraints-termux.txt
  - external/libs/hermes-agent/pyproject.toml
  - external/libs/hermes-agent/README.md
---

# 10. Termux（Android）特殊安装说明

本章面向希望在 Android 设备上通过 Termux 运行 Hermes Agent 的用户，详细说明 Termux 环境的特殊限制、系统依赖安装、安装脚本的 Termux 专属行为、`[termux]` / `[termux-all]` extras 构成、不支持的功能清单、存储权限配置、后台保活方法、常见故障排查以及性能优化建议。所有内容均以项目源码中的 `scripts/install.sh`、`constraints-termux.txt`、`pyproject.toml` 与 `README.md` 为准。

> Termux 是一个无需 root 即可在 Android 上运行的 Linux 终端模拟器。Hermes Agent 在 Termux 上提供**经过测试的精简安装路径**，使用 Python 标准库 venv + pip（而非 uv），并通过 `constraints-termux.txt` 锁定与 Android 兼容的依赖版本。由于 Bionic libc、原生依赖兼容性和 Android 后台限制，部分桌面端功能在 Termux 上不可用。

---

## 10.1 Termux 环境特殊限制

### 10.1.1 Bionic libc 与 wheel 兼容性

Termux 使用 Android 的 **Bionic libc**，而非 glibc 或 musl。这导致：

- Termux Python 报告 `sys_platform == 'linux'`、`platform_machine == 'aarch64'`，但实际运行在 Bionic libc 上；
- 该组合**既不满足 manylinux 标签，也不满足 musllinux 标签**，因此大量仅发布 wheel（无 sdist）的原生包无法直接安装；
- 内核版本字符串中包含 `-androidNN-`（GKI 内核），安装脚本通过检测该特征识别 Android 环境。

最典型的受影响包是 **nemo-relay**（Hermes 的原生中继模块）。`pyproject.toml` 中通过环境标记将其严格排除在 Android 之外：

```
'nemo-relay>=0.7.1,<0.8; ... (sys_platform == 'linux' and platform_machine == 'aarch64' and 'android' not in platform_release) ...'
```

当 `platform_release` 包含 `android` 时，该依赖不会被安装，pip 解析也不会因找不到匹配 wheel 而直接失败。

### 10.1.2 无 systemd

Termux 环境中没有 systemd，也不使用传统的 SysV init。安装脚本在 Termux 上：

- 跳过 `systemctl` 服务安装；
- 改用 `nohup ... &` 将 gateway 以后台进程方式启动；
- 日志写入 `$HERMES_HOME/logs/gateway.log`。

### 10.1.3 目录结构差异

| 项目 | 桌面 Linux（非 root） | Termux |
|---|---|---|
| 安装目录 | `$HERMES_HOME/hermes-agent` | `$HERMES_HOME/hermes-agent` |
| 命令链接位置 | `$HOME/.local/bin` | `$PREFIX/bin`（已在 PATH 中） |
| Python 来源 | uv 托管下载 | Termux pkg（`pkg install python`） |
| 包管理器 | apt/dnf/pacman 等 | `pkg`（Termux 专属） |
| venv 创建方式 | `uv venv` | `python -m venv`（stdlib） |

Termux 的 `$PREFIX` 通常为 `/data/data/com.termux/files/usr`，该目录由 Termux 包管理器管理，因此 `hermes` 命令符号链接直接放入 `$PREFIX/bin`，无需修改 shell 配置。

### 10.1.4 不使用 uv

安装脚本在检测到 Termux 时，**跳过 uv 的下载与安装**，改用 Python 标准库的 `venv` + `pip`：

```bash
if [ "$DISTRO" = "termux" ]; then
    log_info "Termux detected — using Python's stdlib venv + pip instead of uv"
    UV_CMD=""
    return 0
fi
```

这是因为 uv 的预编译二进制在 Bionic libc 上可能存在兼容性问题，而 Termux 自带的 Python 和 pip 经过 Termux 团队适配，更为可靠。

---

## 10.2 Termux 依赖安装命令

### 10.2.1 安装脚本自动安装的系统包

安装脚本在 Termux 上会自动通过 `pkg install` 安装以下系统包：

| 包名 | 用途 |
|---|---|
| `clang` | C 编译器，编译 Python C 扩展 |
| `rust` | Rust 编译器，编译含 Rust 代码的依赖（如 pydantic-core、tiktoken） |
| `make` | 构建工具 |
| `pkg-config` | 编译配置查询 |
| `libffi` | FFI 库，供 ctypes/ cffi 使用 |
| `openssl` | SSL/TLS 库 |
| `ca-certificates` | CA 根证书 |
| `curl` | HTTP 下载工具 |
| `ripgrep` | 快速文件搜索（仅在未安装时安装） |
| `ffmpeg` | 音频处理（TTS 语音消息，仅在未安装时安装） |

对应源码逻辑：

```bash
local termux_pkgs=(clang rust make pkg-config libffi openssl ca-certificates curl)
if [ "$need_ripgrep" = true ]; then termux_pkgs+=("ripgrep"); fi
if [ "$need_ffmpeg" = true ]; then termux_pkgs+=("ffmpeg"); fi
pkg install -y "${termux_pkgs[@]}"
```

### 10.2.2 手动预装命令

如果希望在运行安装脚本前手动准备环境，执行：

```bash
pkg update && pkg upgrade -y
pkg install -y python git ripgrep ffmpeg clang rust make pkg-config libffi openssl ca-certificates curl
```

其中：
- `python`：Termux 版 Python（要求 3.11+，安装脚本会自动检测版本，不满足时通过 `pkg install python` 安装）；
- `git`：用于克隆 Hermes Agent 仓库。

### 10.2.3 可选包

```bash
pkg install -y nodejs          # 浏览器工具需要（非测试路径的一部分）
pkg install -y termux-api      # 提供 wakelock、通知等 Android API 访问
```

---

## 10.3 安装脚本在 Termux 上的特殊行为

### 10.3.1 Termux 环境检测

安装脚本通过 `is_termux()` 函数识别 Termux：

```bash
is_termux() {
    [ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *"com.termux/files/usr"* ]]
}
```

满足以下任一条件即判定为 Termux：
1. 环境变量 `TERMUX_VERSION` 非空；
2. `PREFIX` 路径包含 `com.termux/files/usr`。

检测成功后设置 `OS="android"`、`DISTRO="termux"`。

### 10.3.2 Python 检测与安装

在 Termux 上，脚本直接使用系统 Python（而非 uv 下载的托管 Python）：

```bash
if command -v python >/dev/null 2>&1; then
    PYTHON_PATH="$(command -v python)"
    if "$PYTHON_PATH" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
        # 版本满足要求
    fi
fi
# 否则：pkg install -y python
```

要求 Python ≥ 3.11。

### 10.3.3 虚拟环境创建

使用 Python 标准库 venv 而非 uv：

```bash
"$PYTHON_PATH" -m venv venv
```

### 10.3.4 Android API Level 检测

脚本会自动检测 Android API Level 并导出为环境变量，供原生包编译时使用：

```bash
if [ -z "${ANDROID_API_LEVEL:-}" ]; then
    ANDROID_API_LEVEL="$(getprop ro.build.version.sdk 2>/dev/null || true)"
    if [ -z "$ANDROID_API_LEVEL" ]; then
        ANDROID_API_LEVEL=24
    fi
    export ANDROID_API_LEVEL
fi
```

默认回退值为 24（Android 7.0）。可通过预设 `ANDROID_API_LEVEL` 环境变量覆盖。

### 10.3.5 psutil Android 兼容垫片

在 Android 上，psutil 的 `setup.py` 在执行 C 构建前会以 `sys.platform == 'android'` 为由拒绝安装。安装脚本会预先运行 `scripts/install_psutil_android.py`，从官方 sdist 应用一行标记补丁后构建安装：

```bash
if "$PIP_PYTHON" -c 'import sys; raise SystemExit(0 if sys.platform == "android" else 1)'; then
    log_info "Android Python detected: prebuilding psutil compatibility shim..."
    "$PIP_PYTHON" "$INSTALL_DIR/scripts/install_psutil_android.py" --pip "$PIP_PYTHON -m pip"
fi
```

> 这是针对 psutil 上游 issue #2762 的临时解决方案，直到上游正式支持 Android。

### 10.3.6 分层依赖安装与三级回退

Termux 上的 pip 安装采用**三级回退策略**，优先尝试最完整的配置，失败时逐步降级：

```bash
# 第一级：termux-all（最完整）
if ! "$PIP_PYTHON" -m pip install -e '.[termux-all]' -c constraints-termux.txt; then
    # 第二级：termux（基线）
    if ! "$PIP_PYTHON" -m pip install -e '.[termux]' -c constraints-termux.txt; then
        # 第三级：仅基础包
        if ! "$PIP_PYTHON" -m pip install -e '.' -c constraints-termux.txt; then
            log_error "Package installation failed on Termux."
            exit 1
        fi
    fi
fi
```

安装前会先升级 pip 工具链：

```bash
"$PIP_PYTHON" -m pip install --upgrade pip setuptools wheel
```

### 10.3.7 constraints-termux.txt 约束文件

所有 pip 安装命令都通过 `-c constraints-termux.txt` 应用版本约束。该文件锁定了在 Android 上经过测试的交互环境依赖版本：

```text
ipython<10
jedi>=0.18.1,<0.20
parso>=0.8.4,<0.9
stack-data>=0.6,<0.7
pexpect>4.3,<5
matplotlib-inline>=0.1.7,<0.2
asttokens>=2.1,<3
```

这些版本钉选防止上游包发布过快、Termux 兼容 wheel/sdist 尚未跟上时导致安装失败。

### 10.3.8 Git 与 Node.js

- **Git**：未安装时通过 `pkg install -y git` 自动安装；
- **Node.js**：未安装时通过 `pkg install -y nodejs` 安装（注意：浏览器自动化不是 Termux 测试路径的一部分，脚本会跳过自动浏览器依赖设置）。

---

## 10.4 `[termux]` 与 `[termux-all]` extras 内容

### 10.4.1 `[termux]` 基线配置

`[termux]` 是经过验证的可靠基线安装，包含核心消息平台和基础工具：

| 包含项 | 对应 extra / 包 | 说明 |
|---|---|---|
| `python-telegram-bot[webhooks]==22.6` | — | Telegram 机器人（含 webhook 支持） |
| `hermes-agent[cron]` | `cron` | 定时任务调度（croniter 已是核心依赖，此 extra 为向后兼容保留） |
| `hermes-agent[cli]` | `cli` | CLI 交互菜单（`simple-term-menu==1.6.6`） |
| `hermes-agent[mcp]` | `mcp` | MCP 服务器支持（`mcp==1.28.1`、`starlette==1.3.1`） |
| `hermes-agent[honcho]` | `honcho` | Honcho AI 用户上下文管理（`honcho-ai==2.2.0`） |
| `hermes-agent[acp]` | `acp` | Agent Client Protocol（`agent-client-protocol==0.9.0`） |

### 10.4.2 `[termux-all]` 扩展配置

`[termux-all]` 在基线之上增加以下 extras（尽力而为安装，失败时自动回退到基线）：

| 包含项 | 对应 extra | 说明 |
|---|---|---|
| `hermes-agent[google]` | `google` | Google Workspace 技能（Gmail、Calendar、Drive 等） |
| `hermes-agent[homeassistant]` | `homeassistant` | Home Assistant 智能家居集成（`aiohttp==3.14.3`） |
| `hermes-agent[sms]` | `sms` | SMS 消息网关（`aiohttp==3.14.3`） |
| `hermes-agent[web]` | `web` | Dashboard Web 服务器（FastAPI、uvicorn、Starlette） |
| `hermes-agent[pty]` | `pty` | PTY 终端支持 |

### 10.4.3 明确排除的 extras

以下 extras 因上游 Android wheel/toolchain 阻塞，**不包含**在 `[termux-all]` 中：

- `matrix`（含 `python-olm`，需要原生加密库，无 Android 构建路径）；
- `voice`（含 `faster-whisper`，依赖 `ctranslate2`、`onnxruntime`，无 Android wheel）；
- `wake`（含 `openwakeword`、`onnxruntime`、`sherpa-onnx`、`pvporcupine`）；
- `messaging` 中的 Discord 语音部分等。

安装脚本完成后会明确提示：

> Termux note: matrix e2ee and local faster-whisper extras are excluded from .[termux-all] due to upstream Android wheel/toolchain blockers.
> Termux note: browser/WhatsApp tooling is not installed by default; see the Termux guide for optional follow-up steps.

---

## 10.5 Termux 上不支持的功能

### 10.5.1 语音识别（STT）与语音合成（TTS）

以下功能因原生依赖不兼容而**不可用**：

| 功能 | 受影响依赖 | 原因 |
|---|---|---|
| 本地语音识别（faster-whisper） | `ctranslate2`、`onnxruntime`、`numpy` | 仅提供 x86_64/aarch64 glibc wheel，Bionic libc 不兼容 |
| 本地 TTS（neutts） | 原生音频库 | 无 Android 构建路径 |
| Mistral Voxtral STT/TTS | `mistralai` | 依赖原生音频推理栈 |
| ElevenLabs 高级 TTS | `elevenlabs`（纯 Python 包） | 包本身可安装，但音频播放依赖 `sounddevice` 等原生库 |

> **注意**：基于云端的 TTS（如 Edge TTS）不依赖原生推理库，理论上可通过 lazy-install 后使用，但音频播放仍受 Android 音频子系统限制。`ffmpeg` 可用于音频格式转换。

### 10.5.2 唤醒词（Wake Word）

"Hey Hermes" 唤醒词功能完全不可用，因为所有引擎均依赖不兼容的原生库：

- `openwakeword==0.6.0`（ONNX 模型）；
- `onnxruntime==1.27.0`；
- `sherpa-onnx==1.13.4`；
- `pvporcupine==4.0.3`（Porcupine 商业引擎）；
- `sounddevice==0.5.5`（音频采集）。

### 10.5.3 Matrix 端到端加密

`matrix` extra 依赖 `mautrix[encryption]`，后者需要 `python-olm`（libolm 的 Python 绑定）。python-olm 仅有 Linux wheel，在 Termux/Bionic 上没有可用的原生构建路径。

### 10.5.4 nemo-relay 原生中继

如 10.1.1 节所述，nemo-relay 仅发布 wheel 且不支持 Bionic libc，在 Termux 上自动排除。这意味着：
- 无法使用本地原生中继编解码；
- 回退到 no-op Relay host，部分共享指标和高性能消息路径不可用。

### 10.5.5 桌面应用

Hermes Agent 桌面应用（Electron，位于 `apps/desktop/`）在 Termux 上不可用。Termux 仅支持 CLI、TUI 和 Web Dashboard（通过 `[web]` extra）。

### 10.5.6 浏览器自动化

安装脚本在 Termux 上**跳过自动浏览器依赖设置**：

```bash
if [ "$DISTRO" = "termux" ]; then
    log_info "Skipping automatic Node/browser dependency setup on Termux"
    log_info "Browser automation is not part of the tested Termux install path yet."
fi
```

虽然可以手动 `pkg install nodejs`，但 Playwright Chromium 等浏览器在 Termux 上缺乏官方支持。

---

## 10.6 Termux 存储权限配置

### 10.6.1 授予存储访问权限

Termux 默认只能访问自身的私有目录。如需让 Hermes Agent 访问设备共享存储（如下载、文档目录），需运行：

```bash
termux-setup-storage
```

该命令会弹出 Android 权限请求对话框，授权后在 `$HOME/storage/` 下创建以下符号链接：

| 链接 | 指向 |
|---|---|
| `~/storage/shared/` | 设备共享存储根目录 |
| `~/storage/downloads/` | Download 目录 |
| `~/storage/dcim/` | DCIM（相机照片） |
| `~/storage/movies/` | Movies |
| `~/storage/music/` | Music |
| `~/storage/pictures/` | Pictures |

### 10.6.2 Hermes 数据目录

Hermes Agent 的所有数据默认存储在 `$HERMES_HOME`（通常为 `~/.hermes`），位于 Termux 私有目录内，**无需存储权限即可访问**：

```
~/.hermes/
├── hermes-agent/       # 代码仓库
├── logs/               # 日志（gateway.log 等）
└── ...
```

只有当需要让 Hermes 读写共享存储中的文件（如处理下载目录中的文档）时，才需要执行 `termux-setup-storage`。

### 10.6.3 注意事项

- Android 11+ 对共享存储有分区存储（Scoped Storage）限制，部分系统目录可能仍不可写；
- 不要将 `HERMES_HOME` 设置到 SD 卡或外部存储，FAT32/exFAT 文件系统不支持 Unix 权限和符号链接，会导致 venv 和 git 操作失败；
- 如需备份 Hermes 数据，打包 `~/.hermes/` 即可。

---

## 10.7 Termux 后台运行方法

### 10.7.1 安装脚本默认方式

安装脚本在 Termux 上通过 `nohup` 启动 gateway：

```bash
nohup hermes gateway > "$HERMES_HOME/logs/gateway.log" 2>&1 &
```

脚本会提示：

> Android may stop background processes when Termux is suspended or the system reclaims resources.

即 Android 系统可能在 Termux 切到后台或内存紧张时终止进程。

### 10.7.2 使用 Termux Wake Lock

安装 `termux-api` 并获取唤醒锁，防止 CPU 休眠：

```bash
pkg install termux-api
termux-wake-lock
```

获取唤醒锁后，Termux 进程在后台运行时 CPU 不会进入深度休眠。释放唤醒锁：

```bash
termux-wake-unlock
```

> 建议在运行 `hermes gateway` 前先执行 `termux-wake-lock`。唤醒锁会增加电量消耗，但能显著提高后台稳定性。

### 10.7.3 使用 termux-services

`termux-services` 提供类似 systemd 的服务管理功能，可在 Termux 启动时自动运行服务：

```bash
pkg install termux-services
```

重启 Termux 后，创建服务脚本：

```bash
mkdir -p $PREFIX/var/service/hermes-gateway
cat > $PREFIX/var/service/hermes-gateway/run <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
exec hermes gateway 2>&1
EOF
chmod +x $PREFIX/var/service/hermes-gateway/run
```

常用服务管理命令：

```bash
sv up hermes-gateway      # 启动服务
sv down hermes-gateway    # 停止服务
sv status hermes-gateway  # 查看状态
sv restart hermes-gateway # 重启服务
```

如需开机自启，创建符号链接：

```bash
mkdir -p $PREFIX/var/service/enable
ln -sf $PREFIX/var/service/hermes-gateway $PREFIX/var/service/enable/
```

### 10.7.4 前台通知保活

结合 `termux-api` 发送持久通知，降低进程被系统杀死的概率：

```bash
termux-notification --title "Hermes Agent" --content "Gateway running" --ongoing
```

### 10.7.5 电池优化白名单

在 Android 设置中将 Termux 加入电池优化白名单（具体路径因厂商而异）：

- **设置 → 应用 → Termux → 电池 → 不受限制**；
- 关闭 Termux 的"后台限制"和"省电模式"；
- 部分厂商（小米、华为、OPPO、vivo）需额外在"自启动管理"中允许 Termux。

---

## 10.8 Termux 特有故障排查

### 10.8.1 编译失败

**症状**：`pip install` 过程中出现 `error: command 'clang' failed` 或 Rust 编译错误。

**解决方案**：

1. 确保所有构建工具已安装：
   ```bash
   pkg install clang rust make pkg-config libffi openssl
   ```
2. 确保 `ANDROID_API_LEVEL` 已正确导出（安装脚本自动处理）：
   ```bash
   echo $ANDROID_API_LEVEL
   export ANDROID_API_LEVEL=$(getprop ro.build.version.sdk)
   ```
3. 更新 Termux 到最新版：
   ```bash
   pkg update && pkg upgrade
   ```
4. 如果某个特定包编译失败，可尝试先单独安装其 Termux 系统依赖。

### 10.8.2 内存不足（OOM）

**症状**：编译 Rust 依赖时进程被 killed，或出现 `MemoryError`。

**原因**：Android 设备内存有限，Rust 编译（尤其对 pydantic-core、tiktoken 等）峰值内存可达 1–2 GB。

**解决方案**：

- 关闭其他 Android 应用释放内存；
- 添加交换文件（需要 root 或使用 `termux-chroot` 方案）；
- 增加 Cargo 并行编译限制（减少并发内存峰值）：
  ```bash
  export CARGO_BUILD_JOBS=1
  ```
- 对于低端设备，考虑在更强大的机器上交叉编译后复制 wheel。

### 10.8.3 psutil 安装失败

**症状**：`error: platform android is not supported`。

**原因**：psutil 上游 `setup.py` 显式拒绝 Android。

**解决方案**：安装脚本会自动运行 `scripts/install_psutil_android.py` 应用补丁。如果自动处理失败，手动执行：

```bash
cd $HOME/.hermes/hermes-agent
python scripts/install_psutil_android.py --pip "python -m pip"
```

### 10.8.4 网络/镜像问题

**症状**：`pkg install` 或 `pip install` 超时、404、证书错误。

**解决方案**：

1. 更新 CA 证书：
   ```bash
   pkg install ca-certificates curl
   pkg update
   ```
2. 切换 Termux 镜像（默认镜像可能过期或速度慢）：
   ```bash
   termux-change-repo
   ```
3. 验证网络连通性：
   ```bash
   curl -I https://pypi.org/simple/
   curl -I https://duckduckgo.com/
   ```
4. 如需使用 pip 镜像源：
   ```bash
   pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
   ```

### 10.8.5 存储路径问题

**症状**：venv 创建失败、git clone 报错、权限拒绝。

**解决方案**：

- 确保安装路径在 Termux 私有目录内（`~/.hermes/`），不要放在外部存储或 SD 卡上；
- 运行 `termux-setup-storage` 获取共享存储权限；
- 检查磁盘空间：`df -h $HOME`。

### 10.8.6 通知权限

**症状**：Termux 通知不显示，或后台进程频繁被杀。

**解决方案**：

- 在 Android 设置中为 Termux 开启"通知"权限；
- 开启"悬浮窗"权限（部分设备需要）；
- 关闭电池优化（见 10.7.5 节）。

### 10.8.7 termux-all 安装部分失败

**症状**：安装日志显示 `.[termux-all]` 失败后回退到 `.[termux]`。

**说明**：这是**预期行为**。三级回退策略确保即使部分可选 extras 安装失败，基线功能仍可用。如需安装某个失败的 extra，可在安装完成后手动重试：

```bash
cd ~/.hermes/hermes-agent
source venv/bin/activate
python -m pip install -e '.[google]' -c constraints-termux.txt
```

根据错误信息安装缺失的系统依赖后重新尝试。

---

## 10.9 Termux 性能优化建议

### 10.9.1 使用 ripgrep 加速文件搜索

Hermes Agent 的代码搜索功能优先使用 ripgrep，比 grep 快数倍。确保已安装：

```bash
pkg install ripgrep
```

安装脚本会自动检测并安装，但如果跳过了，手动安装可获得更好的搜索性能。

### 10.9.2 限制 Rust 编译并行度

如 10.8.2 节所述，在内存有限的设备上设置：

```bash
export CARGO_BUILD_JOBS=1
```

虽然编译速度变慢，但可避免 OOM killer 中断编译。对于 4 GB 以下内存的设备建议设为 1，6–8 GB 设备可设为 2。

### 10.9.3 定期清理 pip 缓存

编译和安装过程会产生大量缓存：

```bash
pip cache purge
rm -rf ~/.cache/pip
```

### 10.9.4 使用 Termux 最新版

Termux 团队持续优化 Bionic libc 兼容性和包版本。定期更新：

```bash
pkg update && pkg upgrade -y
```

> 注意：大版本升级后可能需要重新创建 venv（删除 `venv/` 目录后重新运行安装脚本）。

### 10.9.5 避免在低端设备上运行 [termux-all]

对于内存 ≤ 4 GB 或 CPU 较弱的设备：

- 安装时可直接使用基线配置而非 termux-all；
- 按需手动启用 extra（如 `[web]` 提供 Dashboard）；
- 避免安装浏览器工具和 Node.js（除非明确需要）。

### 10.9.6 后台运行优化组合

对于需要长时间运行 gateway 的场景，推荐组合：

```bash
# 1. 获取唤醒锁
termux-wake-lock

# 2. 发送持久通知
termux-notification --title "Hermes Gateway" --content "Running" --ongoing

# 3. 后台启动
nohup hermes gateway > ~/.hermes/logs/gateway.log 2>&1 &

# 4. 查看日志
tail -f ~/.hermes/logs/gateway.log
```

配合 Android 系统设置中的电池优化白名单，可达到最佳后台存活率。

### 10.9.7 磁盘空间管理

完整安装（含编译工具链）可能占用 2–4 GB。注意：

- Rust 工具链约占 500 MB–1 GB；
- Python venv 约 500 MB–1.5 GB（取决于安装的 extras）；
- 安装完成后可清理构建缓存释放空间；
- 避免重复克隆多个仓库副本。

---

## 10.10 手动安装参考

如需完全手动安装（不使用 install.sh），按以下步骤操作：

```bash
# 1. 安装系统依赖
pkg update && pkg upgrade -y
pkg install -y python git ripgrep ffmpeg clang rust make pkg-config libffi openssl ca-certificates curl

# 2. 克隆仓库
git clone https://github.com/NousResearch/hermes-agent.git ~/.hermes/hermes-agent
cd ~/.hermes/hermes-agent

# 3. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate

# 4. 升级 pip 工具链
pip install --upgrade pip setuptools wheel

# 5. 设置 Android API Level
export ANDROID_API_LEVEL=$(getprop ro.build.version.sdk)

# 6. 安装 psutil 兼容垫片（如使用官方 Python 3.13+ PEP 738 构建）
python scripts/install_psutil_android.py --pip "python -m pip" || true

# 7. 安装 Hermes Agent（优先 termux-all，失败则 termux）
pip install -e '.[termux-all]' -c constraints-termux.txt || \
pip install -e '.[termux]' -c constraints-termux.txt || \
pip install -e '.' -c constraints-termux.txt

# 8. 验证安装
hermes --version
```

---

> **总结**：Termux 上的 Hermes Agent 安装路径经过专门适配，核心差异在于使用 stdlib venv + pip 替代 uv、应用 `constraints-termux.txt` 版本约束、采用 `[termux]` / `[termux-all]` extras 而非 `[all]`、以及自动处理 psutil 等 Android 兼容性问题。语音、唤醒词、Matrix E2EE、桌面应用和浏览器自动化因原生依赖限制不可用。通过 `termux-wake-lock`、电池优化白名单和 `termux-services` 可实现可靠的后台运行。
