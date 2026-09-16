# XMNN Runtime 离线交付包

面向客户的**完全独立**运行环境：解压即用，**无需联网、无需 Python、
不依赖任何其他软件包**。内含 XMNN 推理/编译运行时（含 JupyterLab 与
SSH），通过随包控制脚本一键管理。

## 1. 系统要求

| 项 | 要求 |
|---|---|
| 容器运行时（二者任选其一） | **Podman** 5.0+（推荐 Linux 客户）或 **Docker** 24.0+（含 Compose v2 插件） |
| 磁盘空间 | ≥ 5 GB 可用空间 |
| 内存 | ≥ 4 GB |
| Windows 客户 | Windows 10/11 + **PowerShell 7.0+**（运行 `xmnnctl.ps1`），使用 Podman Machine 或 Docker Desktop |
| Linux / macOS 客户 | bash 4.0+（运行 `xmnnctl`） |

> 交付过程**不需要安装 Python**；Windows 上的 PowerShell 仅用于随包脚本。

## 2. 五分钟上手

### Windows（PowerShell 7）

```powershell
# 如提示执行策略被拦截：
# pwsh -ExecutionPolicy Bypass -File .\xmnnctl.ps1 <命令>
.\xmnnctl.ps1 init      # 生成 .env，自动创建登录密码与 Jupyter Token（请保存输出）
.\xmnnctl.ps1 load      # 校验并导入随包镜像（约需 1-3 分钟），自动运行交付守卫
.\xmnnctl.ps1 up        # 启动服务，就绪后自动打印访问地址
```

### Linux / macOS

```bash
chmod +x xmnnctl
./xmnnctl init          # 生成 .env 与随机凭证（请保存输出）
./xmnnctl load          # 校验并导入随包镜像，自动运行交付守卫
./xmnnctl up            # 启动服务，就绪后自动打印访问地址
```

启动成功后访问：

| 服务 | 地址 | 凭证 |
|---|---|---|
| **JupyterLab** | http://localhost:8893 | `.env` 中的 `JUPYTER_TOKEN`；新建笔记本时内核选择 **Python 3.14 (xmnn runtime)** |
| **SSH** | `ssh -p 2225 devuser@localhost` | `.env` 中的 `USER_PASSWORD` |

> 如端口 8893/2225 已被占用，可修改 `.env` 中的 `XMNN_JUPYTER_PORT` /
> `XMNN_SSH_PORT` 后重新 `up`。

## 3. 常用命令

| 操作 | Windows | Linux / macOS |
|---|---|---|
| 初始化配置与凭证 | `.\xmnnctl.ps1 init` | `./xmnnctl init` |
| 导入镜像 | `.\xmnnctl.ps1 load` | `./xmnnctl load` |
| 启动 | `.\xmnnctl.ps1 up` | `./xmnnctl up` |
| 停止（保留工作区与凭证） | `.\xmnnctl.ps1 down` | `./xmnnctl down` |
| 查看状态 | `.\xmnnctl.ps1 ps` | `./xmnnctl ps` |
| 查看日志 | `.\xmnnctl.ps1 logs` | `./xmnnctl logs` |
| 运行 10 项运行时守卫 | `.\xmnnctl.ps1 smoke` | `./xmnnctl smoke` |
| 查看版本与镜像摘要 | `.\xmnnctl.ps1 version` | `./xmnnctl version` |

重新生成凭证：`init --force`（需随后 `down` 再 `up` 生效）。

## 4. 数据与目录

| 目录 / 文件 | 说明 |
|---|---|
| `workspace/` | 持久工作区，映射到容器内 `/workspace`；笔记本、模型输入输出请放此处，`down` 不删除 |
| `.env` | 配置与凭证（版本、端口、密码、Token）；请妥善保管，勿随日志外发 |
| `artifacts/` | 随包镜像 `xmnn-runtime-<版本>.tar.gz` 与清单 `release.json` |

## 5. 完整性校验

镜像导入前，`load` 会自动比对镜像文件的 **SHA256** 与 `artifacts/release.json`
中记录的摘要；不一致将拒绝导入（文件可能在拷贝中损坏，请重新获取交付包）。

如需手工校验：

```powershell
# Windows
(Get-FileHash .\artifacts\xmnn-runtime-*.tar.gz -Algorithm SHA256).Hash.ToLower()
```

```bash
# Linux / macOS
sha256sum artifacts/xmnn-runtime-*.tar.gz   # 或 shasum -a 256
```

## 6. 离线与网络说明

- 启动与运行**全程不访问网络**：脚本已设置禁止镜像在线拉取；如误删本地
  镜像，请重新执行 `load`。
- 服务默认仅绑定本机回环地址。需要对局域网开放时，请通过宿主防火墙/反向
  代理自行管控。

## 7. 排障

| 现象 | 处理 |
|---|---|
| `load` 提示 sha256 不符 | 镜像文件损坏，重新拷贝/获取交付包后再试 |
| `load` 后提示镜像不存在 | 核对 `.env` 中 `XMNN_VERSION` 与 `artifacts/` 内文件名版本是否一致 |
| `up` 后 Jupyter 暂时打不开 | 首次启动约需 1 分钟初始化，脚本会自动等待；超时可用 `logs` 查看进度 |
| 忘记密码 / Token | 查看 `.env`；或 `init --force` 后 `down`、`up` |
| 端口被占用 | 修改 `.env` 的端口后重新 `up` |
| Podman 提示找不到 compose | 安装 podman-compose，或升级到内置 compose 的 Podman 版本 |
| SSH 客户端提示主机指纹不符 | 通常因在其他机器使用过同端口；确认安全后执行 `ssh-keygen -R "[localhost]:2225"` |

## 8. Windows 使用注意

- 请始终使用 `xmnnctl.ps1`；**不要**在 Git Bash 中运行同名 bash 脚本
  （路径转换会导致容器参数错误）。
- 建议交付包放置在**不含空格与中文**的路径下。
- 使用 Docker Desktop 或 Podman Machine 时，请确保对应后台程序已启动。
