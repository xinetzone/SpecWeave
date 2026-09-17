# XMNN Runtime 离线交付包

面向客户的**完全独立**运行环境：解压即用，**无需联网、无需 Python、
不依赖任何其他软件包**。内含 XMNN 推理/编译运行时（含 JupyterLab 与
SSH），通过随包控制脚本一键管理。

> 👉 **第一次接触、完全不懂技术？** 先花 30 秒建立一个印象：
>
> - 这个交付包可以理解成**一台封装好的"软件电脑"**：里面已经装好 XMNN
>   运行环境、JupyterLab（网页版编程工具）和 SSH（远程登录通道），你无需
>   自己安装配置任何软件依赖。
> - "Podman"或"Docker"是运行这台"软件电脑"的**播放器**（二者装一个即可），
>   就像视频文件需要播放器才能打开。
> - 你要做的只有一件事：把命令**逐条复制粘贴**到一个叫"终端"的窗口里按回车。
>   下文会讲终端怎么打开、每条命令成功时长什么样。
> - 全程不需要联网、不需要懂编程。**红字不一定是报错**（黄字是提醒；只有
>   `[ERR ]` 红字且命令提前结束才是失败），拿不准就截图问对接人员。

## 1. 系统要求

| 项 | 要求 |
|---|---|
| 容器运行时（二者任选其一） | **Podman** 5.0+（推荐 Linux 客户）或 **Docker** 24.0+（含 Compose v2 插件） |
| 磁盘空间 | ≥ 5 GB 可用空间 |
| 内存 | ≥ 4 GB |
| Windows 客户 | Windows 10/11 + **PowerShell 7.0+**（运行 `xmnnctl.ps1`），使用 Podman Machine 或 Docker Desktop |
| Linux / macOS 客户 | bash 4.0+（运行 `xmnnctl`） |

> 交付过程**不需要安装 Python**；Windows 上的 PowerShell 仅用于随包脚本。

### 开始前，你需要准备三样东西

1. **播放器（Podman 或 Docker，二选一）**
   - Windows：推荐安装 [Podman Desktop](https://podman.io/docs/installation)（自带 Podman Machine）或 [Docker Desktop](https://www.docker.com/products/docker-desktop/)；安装后**先启动一次**，等后台图标显示为运行状态。
   - Linux：按 [Podman 官方指引](https://podman.io/docs/installation)用系统包管理器安装。
   - 不确定装没装？在终端执行 `podman --version`，能显示版本号即可；提示找不到命令就先安装。
2. **PowerShell 7（仅 Windows 需要）**：Windows 自带的旧版 PowerShell 5.1 不能用。安装 [PowerShell 7](https://github.com/PowerShell/PowerShell#get-powershell) 后，开始菜单里会出现 **PowerShell 7**。自检：在终端执行 `$PSVersionTable.PSVersion`，主版本号显示 **7** 即正确。
3. **解压后的交付包**：用系统"全部解压缩"或 7-Zip 解压到一个**路径不含空格和中文**的文件夹（例如 `D:\xmnn-runtime\`）。⚠️ 不要直接在压缩包窗口里双击运行；解压后若出现两层同名文件夹（`xmnn-runtime\xmnn-runtime\`），请进入最内层。

## 2. 五分钟上手

> **执行位置**：以下命令均在**交付包根目录**（本 README 所在目录）执行；
> 判别标志——该目录含 `xmnnctl.ps1` 与 `artifacts/`（`workspace/` 首次 `up`
> 时自动创建，刚解压时可能还没有）。
> **SpecWeave 开发仓库**内可直接在叠加层根执行 `./xmnnctl <命令>`
> （便捷壳自动转发到本目录真实脚本，运行时文件仍全部落在 `release/`）；
> 也可 `cd release` 后按客户方式执行。

### 第 0 步：在正确的文件夹里打开终端（最容易出错）

1. 进入解压后的交付包，找到**能直接看到 `xmnnctl.ps1`（Windows）或 `xmnnctl`（Linux/macOS）文件**的那一层，这就是"交付包根目录"；它旁边应有 `artifacts` 文件夹（`workspace` 首次执行命令时自动创建）。
2. Windows：在文件夹空白处 **按住 Shift 点右键** → 选"在终端中打开"（Win11）或"在此处打开 PowerShell 窗口"；也可点击文件夹地址栏，清空后输入 `pwsh` 回车。macOS：可在"系统设置 → 键盘 → 键盘快捷键 → 服务"中开启"新建位于文件夹位置的终端窗口"，然后在文件夹右键→服务中打开。
3. 核对位置：在终端执行 `dir`（Linux/macOS 为 `ls`），输出列表中能看到 `xmnnctl.ps1` 即正确；看不到说明目录不对，回到第 1 步。
4. Windows 还需确认 **Podman Machine 或 Docker Desktop 已经启动**（任务栏托盘图标处于运行状态）。

> 📋 **终端操作小常识**：粘贴命令通常用**鼠标右键**或 `Ctrl+Shift+V`——注意终端里 `Ctrl+C` 的含义是"终止当前命令"，不是复制。每次只粘贴**一条**命令，按回车，等它执行完再粘贴下一条。

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
chmod +x xmnnctl        # 仅首次需要：赋予脚本可执行权限（执行一次即可）
./xmnnctl init          # 生成 .env 与随机凭证（请保存输出）
./xmnnctl load          # 校验并导入随包镜像，自动运行交付守卫
./xmnnctl up            # 启动服务，就绪后打印访问地址
```

**每条命令执行后，正常情况下你会看到：**

| 命令 | 预期输出与耗时（看到这些就是成功） |
|---|---|
| `init` | 绿字 `[ OK ] 初始化完成`，紧接着打印 **SSH 登录密码（16 位）** 和 **Jupyter Token（32 位）**——立即复制保存。重复执行只提示"已存在，跳过初始化"，不会覆盖 |
| `load` | 先出现绿字"完整性校验通过"，然后显示镜像导入进度条；约 **1-5 分钟**（镜像约 1.2 GB，硬盘持续读写是正常现象）；完成后自动运行 10 项交付守卫并列出检查结果 |
| `up` | 自动创建 `workspace` 文件夹并在后台启动；提示"等待 Jupyter 就绪（冷启动约需 1-3 分钟）"；**最后打印一个 `====` 横线包围的方框**，里面写着访问地址，即代表成功 |
| 任意命令 | 蓝底 `[xmnn]` 是进度，绿色 `[ OK ]` 是成功，黄色 `[WARN]` 是提醒，红色 `[ERR ]` 才是出错 |

启动成功后访问：

| 服务 | 地址 | 凭证 |
|---|---|---|
| **JupyterLab** | http://localhost:8893 | `.env` 中的 `JUPYTER_TOKEN`；新建笔记本时内核选择 **Python 3.14 (xmnn runtime)** |
| **SSH** | `ssh -p 2225 devuser@localhost` | `.env` 中的 `USER_PASSWORD` |

> 如端口 8893/2225 已被占用，可修改 `.env` 中的 `XMNN_JUPYTER_PORT` /
> `XMNN_SSH_PORT` 后重新 `up`。

**第一次打开 JupyterLab**：浏览器地址栏输入 `http://localhost:8893`（"localhost"
就是"本机"，不需要联网）→ 页面要求输入 Token 时，用记事本打开同目录 `.env`
文件，复制 `JUPYTER_TOKEN=` 后面那一长串字符粘贴；也可直接访问
`http://localhost:8893/lab?token=粘贴你的Token`。新建笔记本时内核选择
**Python 3.14 (xmnn runtime)**，这才是交付包内的环境（选错内核会找不到组件）。

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

### 选择容器运行时（Podman / Docker）

默认 `auto`：自动探测，优先 Podman、其次 Docker。需要强制指定时，用
`--runtime`（Windows：`-Runtime`，均可用简写 `-r`）参数，取值
`podman|docker|auto`，参数可放在命令前后：

```bash
./xmnnctl --runtime docker up     # 强制 Docker
./xmnn up -r podman               # 强制 Podman（等价写法）
```

```powershell
.\xmnnctl.ps1 -Runtime docker up
```

也可设置环境变量 `XMNN_RUNTIME=podman|docker|auto`。优先级：命令行参数
> 环境变量 > `auto` 自动探测。显式指定了未安装的运行时时脚本会直接报错，
不会静默回退到另一个运行时。

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
| 报"术语 'xmnnctl' 不会被识别为 cmdlet" | 当前目录既非交付包根、也无便捷壳：进入含本 README 的目录执行；SpecWeave 开发仓库应在 `overlays/xmnn-runtime` 根目录直接 `./xmnnctl <命令>`（见 §2 执行位置） |
| 报 `Cannot connect to Podman` / `unable to connect to Podman socket` | Podman 后台虚拟机未启动：执行 `podman machine start`（或打开 Podman Desktop 等待托盘就绪）后重试原命令；Docker 则启动 Docker Desktop。新版脚本会在导入前直接拦截并给出同样提示 |
| `load` 提示 sha256 不符 | 镜像文件损坏，重新拷贝/获取交付包后再试 |
| 紧连接失败后又提示"导入的镜像中没有/版本不符" | 这是旧版脚本的**误导性次生报错**，真因是后台没连上；先按上一行启动机器并重试，不要改版本号 |
| `load` 后提示镜像不存在 | 核对 `.env` 中 `XMNN_VERSION` 与 `artifacts/` 内文件名版本是否一致 |
| `up` 后 Jupyter 暂时打不开 | 首次启动约需 1 分钟初始化，脚本会自动等待；超时可用 `logs` 查看进度 |
| 忘记密码 / Token | 查看 `.env`；或 `init --force` 后 `down`、`up` |
| 端口被占用 | 修改 `.env` 的端口后重新 `up` |
| Podman 提示找不到 compose | 脚本会自动尝试 `~/.local/bin`（pipx/pip --user 安装位置）；仍失败时按报错提示安装 `podman-compose`（推荐 `pipx install podman-compose`）。WSL 非登录 shell 可先执行 `export PATH="$HOME/.local/bin:$PATH"` |
| Linux/macOS 执行报 `'bash\r': No such file or directory` | 脚本在拷贝中被改成了 Windows 行尾：Linux/WSL 执行 `sed -i 's/\r$//' xmnnctl`（macOS 用 `sed -i '' 's/\r$//' xmnnctl`），重新 `chmod +x xmnnctl` 后再试；或重新获取交付包 |
| SSH 客户端提示主机指纹不符 | 通常因在其他机器使用过同端口；确认安全后执行 `ssh-keygen -R "[localhost]:2225"` |

## 8. Windows 使用注意

- 请始终使用 `xmnnctl.ps1`；**不要**在 Git Bash 中运行同名 bash 脚本
  （路径转换会导致容器参数错误）。
- 建议交付包放置在**不含空格与中文**的路径下。
- 使用 Docker Desktop 或 Podman Machine 时，请确保对应后台程序已启动。

## 9. 小白词典与常见问题

### 9.1 名词小词典

| 你看到的词 | 人话解释 |
|---|---|
| 终端 / PowerShell | 输入文字命令的窗口；PowerShell 是 Windows 上的终端程序，本包要求 7.0 以上 |
| 命令 | 粘贴进终端、按回车执行的一句话，例如 `.\xmnnctl.ps1 up` |
| 容器 | "软件电脑"运行起来后的实例；可以启动（up）、停止（down），停止不影响你的文件 |
| 镜像 | "软件电脑"的模板；`load` 就是把模板从交付包导入 Podman/Docker |
| `.env` | 一个普通文本配置文件，存着版本、端口、登录密码和 Token，记事本即可打开 |
| `workspace` 文件夹 | 交付包里的普通文件夹，等同于容器内的 `/workspace`；笔记本和数据请放这里，`down` 不删除 |
| localhost 与端口（8893） | localhost 指"你自己这台电脑"，8893 是门牌号；浏览器访问 `localhost:8893` 即访问本机上的该服务 |
| Token | 一长串随机字符，相当于网页服务的入场密码 |
| 交付守卫（smoke） | 10 项自动体检，逐项确认环境各组件工作正常 |

### 9.2 高频问题

- **出现红字/黄字是不是失败了？** 黄字 `[WARN]` 是提醒（如"请保存凭证"），可继续；只有红字 `[ERR ]` 且命令提前结束才是失败，对照 §7 排障表处理。
- **`load` 卡住、进度条几分钟不动？** 镜像约 1.2 GB，1-5 分钟正常，期间勿关终端；超过 10 分钟毫无变化再截图询问对接人员。
- **命令跑完后能关终端窗口吗？** 可以。服务在后台运行，关窗口不受影响；下次操作时重新在该文件夹打开终端即可。
- **电脑关机/重启后还要重做哪几步？** 先启动 Podman Machine 或 Docker Desktop，在交付包目录执行 `up` 一条命令即可；**不需要**重新 `init` 或 `load`（除非你删掉了导入的镜像）。
- **浏览器打不开 http://localhost:8893？** 先执行 `ps`，看到容器状态为 `Up`；首次启动请等待 1-3 分钟；仍打不开按 §7 用 `logs` 查看进度。
- **密码/Token 没保存怎么办？** 记事本打开 `.env` 即可查到；想换新的执行 `init --force`，随后依次执行 `down`、`up` 生效。
- **提示"执行策略"被拦截？** 复制代码块上方注释里的替代命令：`pwsh -ExecutionPolicy Bypass -File .\xmnnctl.ps1 <命令>`。这是一次性放行，不修改系统设置。
- **Linux 提示 Permission denied？** 先执行一次 `chmod +x xmnnctl`（仅需一次），再重新执行原命令。
- **报 `Cannot connect to Podman` 怎么办？** 后台虚拟机关着：执行 `podman machine start`，等待提示 started 后重新执行原命令；`init` 不需要后台，`load`/`up` 需要。电脑重启后通常也要先做这一步。
