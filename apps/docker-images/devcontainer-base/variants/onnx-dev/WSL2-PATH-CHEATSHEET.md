# WSL2 路径映射 & 权限策略速查卡片

> 📋 复制即用，覆盖 Windows ↔ WSL2 ↔ Docker 三层路径与权限全场景

---

## 一、路径映射速查表

| 场景 | Windows 路径 | WSL2 路径 | Docker 容器内路径 | 备注 |
|------|-------------|-----------|------------------|------|
| D盘项目根 | `D:\spaces\SpecWeave` | `/mnt/d/spaces/SpecWeave` | `/workspace` | ⭐ 推荐挂载点 |
| C盘用户目录 | `C:\Users\xinzo` | `/mnt/c/Users/xinzo` | 不建议挂载 | 权限复杂，性能差 |
| 当前脚本目录 | (脚本所在位置) | `$(cd "$(dirname "$0")" && pwd)` | 自动检测 | start-dev.sh 已内置 |
| WSL home | - | `~` 或 `/home/xinzo` | 可挂载 | Linux 原生性能最佳 |
| Docker 命名卷 | - | - | `/var/lib/docker/volumes/...` | 持久化数据首选 |

### 🔧 快速转换命令

```bash
# Windows → WSL 路径（在 WSL 中执行）
wslpath -u 'D:\spaces\SpecWeave'
# → /mnt/d/spaces/SpecWeave

# WSL → Windows 路径（在 WSL 中执行）
wslpath -w /mnt/d/spaces/SpecWeave
# → D:\spaces\SpecWeave

# 检查当前是否在 WSL2 中
grep -qi microsoft /proc/version && echo "WSL2" || echo "Native Linux"
```

---

## 二、三模式路径挂载策略

### 🟢 Ephemeral（一次性模式）
```bash
# 自动挂载当前工作目录到 /workspace
docker run --rm -it \
  -v "$(pwd):/workspace" \
  -w /workspace \
  devcontainer-base:onnx-dev-latest \
  python your_script.py
```
- **特点**：退出即删，代码在宿主，容器只提供运行环境
- **适用**：快速验证、单次脚本运行、CI 任务
- **权限**：自动继承宿主 uid/gid（通常 1000:1000）

### 🔵 Persistent（长期后台模式）
```bash
# 后台启动 + 端口映射 + 命名容器
docker run -d \
  --name onnx-dev \
  --privileged \
  -p 2222:22 -p 8888:8888 \
  -v "$PWD:/workspace" \
  -e WORKSPACE_CHOWN_MODE=named-only \
  devcontainer-base:onnx-dev-latest
```
- **特点**：容器常驻，可 SSH/Jupyter 连接，支持 DinD
- **适用**：日常开发、IDE 远程连接、长期实验
- **权限**：`named-only` 模式仅对已知目录 chown，不递归全目录

### 🟣 IDE Integrated（DevContainer 模式）
```json
{
  "workspaceMount": "source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=cached",
  "workspaceFolder": "/workspace",
  "remoteUser": "devuser",
  "containerEnv": {
    "WORKSPACE_CHOWN_MODE": "named-only"
  }
}
```
- **特点**：VS Code 自动管理，一键 "Reopen in Container"
- **适用**：VS Code 重度用户、团队统一开发环境
- **一致性**：`consistency=cached` 提升 macOS/Windows 挂载性能

---

## 三、权限策略四选一

| 策略 | 环境变量值 | 行为 | 适用场景 | 风险 |
|------|-----------|------|---------|------|
| 🔴 自动 chown（全目录） | `WORKSPACE_CHOWN_MODE=auto` | 启动时递归 `chown -R devuser:devuser /workspace` | 空目录、首次初始化 | ⚠️ 大目录极慢（>10万文件）、可能破坏宿主权限 |
| 🟡 仅命名目录 chown | `WORKSPACE_CHOWN_MODE=named-only` | 只对 `autolibs/`, `tools_cpp/`, `fonts/`, `.vscode/` 等已知目录 chown | 已有代码仓库、日常开发 | ✅ 安全快速，推荐默认 |
| 🟢 只读挂载 | `:ro` 后缀 | `-v /host/path:/workspace:ro` 只读挂载 | 生产环境、代码只读场景 | 无法在容器内修改文件 |
| ⚫ 关闭自动 chown | `WORKSPACE_CHOWN_MODE=none` | 完全不处理权限，依赖宿主 uid/gid 匹配 | Linux 原生、uid 一致时 | 可能出现 Permission denied |

### ✅ 推荐配置（devcontainer.json & start-dev.sh）
```bash
# 默认安全策略：仅对必要目录 chown
-e WORKSPACE_CHOWN_MODE=named-only
```

---

## 四、常见权限问题 & 修复

### ❌ Permission denied 写入文件
```bash
# 快速修复：在容器内执行
sudo chown -R devuser:devuser /workspace/your_dir

# 或启动时指定用户映射（Linux 原生）
--user "$(id -u):$(id -g)"
```

### ❌ WSL2 下 Windows 文件权限 777
```bash
# /etc/wsl.conf 配置（在 WSL 中）
[automount]
options = "metadata,umask=022,fmask=113"
mountFsTab = false
```
- 修改后执行 `wsl --shutdown` 生效
- 让 Windows 文件在 WSL 中显示正常权限（而非 777）

### ❌ Docker socket 权限拒绝
```bash
# Persistent 模式已加 --privileged，如仍需：
sudo usermod -aG docker $USER  # 然后重新登录
# 或临时
sudo chmod 666 /var/run/docker.sock
```

### ❌ Git 显示文件全部 modified（权限变化）
```bash
# 仓库级别忽略文件权限变化
git config core.fileMode false
# 或全局
git config --global core.fileMode false
```

---

## 五、PowerShell ↔ WSL ↔ Docker 命令速查

### 🪟 Windows PowerShell 调用
```powershell
# 快速验证（PowerShell）
wsl -d Ubuntu -- bash -c "cd /mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants/onnx-dev && docker run --rm -v \`"$(pwd):/workspace\`" devcontainer-base:onnx-dev-latest python -c 'import onnx; print(onnx.__version__)'"

# 运行推理脚本（PowerShell）
wsl -d Ubuntu -- bash -c "cd /mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants/onnx-dev && ./start-dev.sh inference_demo.py"
```

### 🐧 WSL2 / Linux 直接调用
```bash
cd /mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants/onnx-dev

# 一键启动（自动选模式）
./start-dev.sh                    # Ephemeral Python REPL
./start-dev.sh inference_demo.py  # 运行脚本
./start-dev.sh -d                 # Persistent 后台模式
./start-dev.sh --info             # 查看镜像信息
```

### 🐳 Docker 直接调用（WSL/Linux）
```bash
# 交互式 bash
docker run --rm -it -v "$PWD:/workspace" -w /workspace \
  devcontainer-base:onnx-dev-latest bash

# Jupyter 临时启动
docker run --rm -it -p 8888:8888 -v "$PWD:/workspace" \
  devcontainer-base:onnx-dev-latest \
  jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser
```

---

## 六、性能优化 Tips

| 优化项 | 配置 | 效果 |
|--------|------|------|
| WSL2 内存限制 | `%UserProfile%\.wslconfig` 中设置 `memory=8GB` | 防止 WSL 吃光内存 |
| 挂载一致性 | `:cached` (macOS/Windows) 或 `:delegated` | 提升 IO 性能 2-5x |
| 避免跨 OS 文件监控 | 代码放 WSL 原生文件系统 (`~/projects`) | inotify 正常工作，IO 最快 |
| 大目录不挂载 | 用 `.dockerignore` 排除 `node_modules/`, `__pycache__/`, `.git/` | 减少挂载开销 |
| 命名卷存数据 | `docker volume create onnx-data` | 数据持久化 + 原生 IO 性能 |

---

## 七、环境检测脚本片段

```bash
# 一键检测当前环境（可直接复制到脚本中）
detect_env() {
    if grep -qi microsoft /proc/version 2>/dev/null; then
        echo "🔷 WSL2 环境"
        if [[ "$(pwd)" == /mnt/* ]]; then
            echo "   ⚠️  当前在 Windows 挂载盘（性能较差）"
            echo "   💡 建议: cd ~/projects 然后 ln -s /mnt/d/spaces/SpecWeave"
        else
            echo "   ✅ 在 WSL 原生文件系统（性能最佳）"
        fi
    elif [[ -f /.dockerenv ]]; then
        echo "🐳 已在 Docker 容器内"
    else
        echo "🐧 Native Linux"
    fi
}

detect_env
```

---

> 💡 **提示**：start-dev.sh 已内置自动环境检测，直接调用即可。本卡片用于手动调试或自定义场景参考。
