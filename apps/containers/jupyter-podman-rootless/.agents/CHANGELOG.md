---
id: jupyter-podman-rootless-changelog
title: jupyter-podman-rootless 变更日志
source: 从 apps/containers/jupyter-podman-rootless/AGENTS.md 拆分归档
---

# 变更日志

## 2026-09-10

| 类型 | 变更 |
|------|------|
| fix | 宿主透传挂载源**禁止自动创建**（long syntax + `bind: {create_host_path: false}`）：`compose.yaml`（`HOST_PODMAN_SOCK`）、`compose.dev.yaml`（SSH agent / gitconfig / `.ssh` / X11 / pip cache 共 5 处）、`compose.passthrough.yaml`（D-Bus）、`compose.passthrough.gui.yaml`（Wayland）共 **8 处**宿主绝对路径挂载源由 short syntax 改为 long syntax 并加该字段。**动因**：podman-compose 的 short syntax 只填 `bind.propagation`（`podman_compose.py:209`），故 `assert_volume()` 必走 `os.makedirs()` 分支——Windows 下 `/run/...` 被 `ntpath` 按盘符解析为 `D:\run\...` 后即尝试在宿主建目录。实测**加固前**手敲 `podman-compose -f compose.yaml -f compose.dev.yaml up` 会在宿主留下 `D:\run`、`D:\dev`、`D:\home` 等错误目录；**加固后**同一命令（`--dry-run`）直接抛 `ValueError: invalid mount config for type 'bind': bind source path does not exist: <path>`，宿主零残留。**行为变更（显式声明）**：原先依赖自动创建的源（尤指 `~/.cache/pip`）须由宿主预先具备，否则该报错会命中它；`./workspace` 等相对路径源保持不变（自动创建仍启用）。已实证 `create_host_path` 在 4 种叠加组合的 `config` 合并结果中逐层保留；同步 `.agents/rules/compose.md`（基础约定 + 分层硬约束 + 验证清单 2 项）、`docs/07-toolbx-passthrough.md`、`docs/09-three-tier-backend.md`（预防措施：以「静默修补」代替「显式失败」的隐式副作用未收敛 + 第三方组件的默认值语义未在配置层显式化） |
| fix | `podman-compose` 后端在 Windows 原生宿主**从「文档标注」升级为「工具层门禁」**（承接同日 docs 条目）：`tasks/client.py::compose_available()` 改为宿主感知——新增 `_COMPOSE_HOST_SUPPORTED = os.name != "nt"`，Windows 原生恒返回 `False`，使全部 `_should_use_compose()` 判据失效，三层降级自动落到 Tier 2 SDK / Tier 3 CLI（二者把 Linux 绝对路径原样交给 podman，Windows 上 podman 为远程客户端、路径由 machine 内 daemon 解析，**路径语义才一致**）；新增 `compose_unavailable_reason()` 并在 `invoke build` 跳过 Tier 1 时输出一行可执行原因（含 WSL / `podman machine ssh` 两条替代路径）。**根因**：`podman-compose` 是运行在宿主进程内的路径处理器——Windows 下 `ntpath` 把以 `/` 开头的组件当作「驱动器根」，`/run/user/1000/bus` 被解析为当前盘符下的 `D:\run\user\1000\bus`；随后 `assert_volume()`（1.6.0 `podman_compose.py` L591 做 `os.path.join`/`abspath`、L600 调 `os.makedirs`）见该路径不存在便试图在宿主创建目录，实测 `PermissionError [WinError 5]` 并触发沙箱 `Not allow operate files: D:\run`；该失败被 `except OSError: pass` 吞掉后 podman 仍收到被篡改的挂载源（宿主残留风险：`D:\run`、`D:\dev`、`D:\home`、`D:\tmp`）（预防措施：跨平台路径语义假定未收敛到单一判据 + 第三方组件的宿主耦合行为未在工具层门禁化） |
| fix | 修正 toolbox 验证探针假阳性与能力声明过宽：Containerfile aux 阶段与 Layer 5 两处探针由 `toolbox --help >/dev/null 2>&1`（cobra 在 `PersistentPreRunE` 前短路 `--help`，且重定向吞掉 stderr，致使容器内裸跑 `toolbox` 报 `Error: TOOLBOX_PATH not set` 时仍打印 [OK]）改为**无重定向**的 `toolbox --version` 活性探针，标签由 "available" 改为 "binary present (liveness only)"；同步 docs/17-upstream-tools.md、docs/04-image-architecture.md、.agents/rules/containerfile.md、.agents/rules/build-test.md，明确 toolbox 的容器创建/进入能力由宿主侧 Toolbx 启动器提供，普通 podman 会话中裸跑 `toolbox` 按上游设计报错，镜像内仅声明二进制活性（预防措施：验证探针类型=假阳性探针 + 声明-事实不一致） |
| fix | toolbox 运行时错误优雅降级 + 对齐官方镜像：补装 `flatpak-xdg-utils` 并提供 `/usr/bin/flatpak-spawn` symlink（`ForwardToHost` 宿主回调前提，对齐官方 `images/ubuntu/26.04/Containerfile`）；真二进制移位至 `/usr/local/libexec/toolbox`，`/usr/local/bin/toolbox` 改由新增的 `scripts/toolbox-wrapper.sh` 承担——有 `TOOLBOX_PATH` 时 `exec` 真二进制、`-h/--help/--version` 短路透传（注意 `-v` 是上游 verbose 计数标志，不属短路型，故不透传），其余情况输出中文可执行指引并保持退出码 1（不再暴露上游裸错误 `Error: TOOLBOX_PATH not set`）；Layer 4/5 [VALIDATE] 6→7 项，Layer 5/5 [OK] 23→25 项（新增 `flatpak-spawn` 存在性与裸跑降级双向断言）；同步 AGENTS.md、docs/04-image-architecture.md、docs/07-toolbx-passthrough.md、docs/17-upstream-tools.md、.agents/rules/containerfile.md、.agents/rules/build-test.md（预防措施：能力声明的运行前提未随资产一并搬运 + 裸错误无可执行指引） |
| fix | 构建上下文排除宿主缓存目录：`.containerignore` 新增 `.wsl-cache/`、`.temp/`、`.image-cache/`、`.ipynb_checkpoints/`——podman 构建上下文**不读取 `.gitignore`**，此前约 15.3G 缓存被全量上传（`.wsl-cache` 11.7G + `.temp` 3.2G + `.image-cache` 355M），`invoke build` 事实上不可用；排除后构建上下文降至约 121M（预防措施：构建忽略清单与 `.gitignore` 语义不同步） |
| fix | Miniforge3 安装包解析改为「本地缓存优先 + 镜像优先多源回退」：新增 `local-cache/miniforge/`（Containerfile `COPY` 至 `/tmp/local-cache/`，命中即跳过全部网络下载，支持离线构建）；显式指定 tuna/aliyun 时按 首选镜像 → 备用镜像 → USTC → GitHub 排序（原实现恒将 GitHub 置于首位，国内大文件下载实测 120s 仅收 9.9MB/124MB 即超时或连接重置，镜像源紧随其后遇瞬时抖动即双源全灭）；curl 增加 `--retry-all-errors`、单源 `--max-time` 由 900s 收紧至 600s、失败打印 curl 退出码，全灭时输出可执行 `[HINT]`（预防措施：外部下载源单点依赖 + 镜像源未按可达性排序） |
| feat | 运行时透传分层覆盖与专用镜像 tag：新增 `compose.passthrough.yaml`（主层 `network_mode: host` + `ports: !reset []` + D-Bus 会话总线，镜像切至 `jupyter-podman-rootless:passthrough`）与 `compose.passthrough.{gui,gpu,usb}.yaml` 三个独立开关，替代原先散落于 `compose.yaml`/`compose.dev.yaml` 的注释式 opt-in（预防措施：交付物形态与运行时约束不匹配——5 项均为运行期参数，无法烘焙进镜像层，且 podman 对缺失挂载源/设备节点硬失败（退出码 125、不自动创建），故各覆盖文件头部内置前置检查命令） |
| fix | 新增 `SSHD_PORT` 环境变量支持：entrypoint `configure_sshd()` 读取 `SSHD_PORT`（默认 22、非法值报错退出）并重写 `sshd_config` 的 `Port`，主层透传覆盖设 2222。host 网络模式下 rootless Podman 容器 root 映射为宿主非特权 UID，绑定特权端口 22 被拒绝（实测 `Bind to port 22 on 0.0.0.0 failed: Permission denied`，sshd 随即 FATAL 退出），原文档承诺的 `localhost:22` 不成立（同场景 Jupyter 8888 正常返回 HTTP 200）（预防措施：能力声明未校验其运行前提在目标网络模式下是否成立） |
| docs | 标注 `podman-compose` 执行环境边界：`docs/07-toolbx-passthrough.md` 与 `.agents/rules/compose.md` 补充说明该命令须在 WSL / podman machine 内执行——Windows 原生 shell 下 podman-compose 会把 Linux 绝对挂载源（`/run/user/1000/bus` 等）按当前盘符解析为 `D:\run\...` 并操作本地文件，报 `Not allow operate files: D:\run`（对照测试确认仅基座 + `compose.dev.yaml` 即已复现，非分层覆盖引入） |
| fix | `olot_car.py` 构建期探针假阳性修正：Layer 5 原用 `python /usr/local/bin/olot_car.py --help >/dev/null 2>&1` 断言 "CLI functional"，但该脚本把 `from olot.basics` / `from olot.backend.oras_py` 置于 `cmd_pack()`/`cmd_extract()` 函数体内**延迟导入**，`--help` 走完 argparse 即退出、从未触达真实依赖，且重定向吞掉 stderr，致使依赖缺失时仍打印 `[OK]`；改为同构于 toolbox 探针修正的**无重定向**实质探针——断言 `olot` + `oras_py.is_oras_py()` 可导入并校验 `--help` 声明 `pack`/`extract` 子命令（预防措施：验证探针类型=假阳性探针） |

## 2026-09-09

| 类型 | 变更 |
|------|------|
| fix | jpman `rebuild`/`rebuild-all` 补 `--format docker`：OCI 格式忽略 SHELL 指令，导致 Stage 2 的 bash 数组语法在 dash 下报 Syntax error |
| fix | 宿主 socket 直通 B-scheme：entrypoint `setup_podman()` 用 `stat -Lc '%G'` 读取宿主直通 socket 属组并以 `usermod -aG` 叠加（须早于 `exec /usr/bin/supervisord`），解决容器内 devuser 访问宿主 socket 报 EACCES（C-I2）；严禁 `chmod 666`/`chown` 宿主 socket |
| fix | Jupyter devuser 与 libpod/tmp 目录准备：容器内 podman 运行所需运行时目录在启动阶段创建 |
| fix | 宿主直连 socket 挂载绕开嵌套 userns 映射带来的权限错位 |
| chore | vendor/ 三上游子模块 pin commit 更新 |

## 2026-09-08

| 类型 | 变更 |
|------|------|
| feat | vendor/ 登记三个容器编排上游 third_party 子模块并 pin commit（github.com/containers/*）：podman-compose `e3df10472`、podman-py `5dd81b49`、toolbox `81401f64`（gitlink 固定，禁止本地修改） |
| feat | 镜像内嵌三容器编排工具：新增 toolbox-builder aux 阶段（golang:1.26-bookworm + libsubid-dev，go build `/out/toolbox`，仅二进制 COPY 进 final 的 /usr/local/bin/toolbox）；conda-builder 内以本地源 pip 安装 podman-py/podman-compose 进 main env（cp314t 直装失败降级 mamba deps + pip --no-deps）；最终验证块新增三项内嵌工具 [OK] 检查（共 23 项） |
| feat | 构建前置 stage 机制：src/jpman_builder/tasks/stage_upstream.py 将 SpecWeave 根 vendor/ 三子模块源树复制到 `<app>/upstream/<name>`（git-ignored 临时目录；.containerignore 反白放行其根 README.md），Containerfile 据此 COPY 本地安装/构建 |
| feat | invoke build 与 jpman rebuild/rebuild-all 构建前自动 stage 上游源树；invoke build 构建上下文根改为向上查找含 Containerfile 的应用根（修复任意 cwd 下上下文与 upstream/ 定位错误） |
| docs | 新增 docs/17-upstream-tools.md（上游工具引入/升级流程/stage 机制/容器内用法）；同步 .agents/rules/containerfile.md、build-test.md、docs/04、08、README.md、AGENTS.md、.agents/README.md 等（构建架构章节由 7 层改述为 3 阶段 + aux + final 运行时分层） |

## 2026-08-29

| 类型 | 变更 |
|------|------|
| feat | passt 固化进 Containerfile（Stage 1 apt 清单 + 版本回显 + Layer 5 最终验证），修复 DinP 场景 rootless 网络命名空间 pasta 缺失报错 |
| fix | jpman rebuild-all/rebuild 补 `--format docker`：OCI 格式忽略 SHELL 指令导致 Stage 2 bash 数组语法在 dash 下报 Syntax error |
| fix | Containerfile Miniforge 下载 `--max-time` 300s→900s：慢速链路（~200KB/s）拉取 124MB 安装包双源 4 次尝试全部超时 |
| refactor | 合并 Containerfile.hidden 至主 Containerfile 并删除：Layer 4 吸收 root 配置权限与 allow_hidden 校验（VALIDATE 5/5→6/6）；jpman rebuild 改为主 Containerfile 层缓存构建（配置变更仅重建 Layer 4/5）；同步 AGENTS/README/docs/14/16、.agents/README、jpman-podman-ops SKILL.md 共 8 处引用 |

## 2026-08-28

| 类型 | 变更 |
|------|------|
| feat | jupyter-podman-rootless 任务系统 Windows 环境适配：任务定义适配 pwsh shell、构建与容器任务补充环境变量传递、manage 任务兼容 Windows 路径、build/container 增加运行时检测；xmnn 四模型组验证 |

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
