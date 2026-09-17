# jupyter-podman-client 变更日志（原子提交汇总）

> 本文件只记录消费端特有改动；SpecWeave 工作区根级、apps/containers 组级、构建端（jupyter-podman-rootless）的改动
> 不在本文件范围内。按七概念方法论每次 C（原子提交）阶段完成后追加一条；每条必须：
> ①可追溯（对应根工作区 git commit hash）②关联七概念场景（里程碑复盘/问题解决/重构优化/知识沉淀/创新突破）③说明验收点

## [Unreleased]

### 2026-09-17 · `fix:` load 时 Podman 未启动被误报"镜像版本不符"——双脚本新增守护可达性预检与 load 退出码检查

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260917-load-daemon-down，未提交，commit hash 待补）。

**现象与根因**：真机执行 `./xmnnctl.ps1 load`，sha256 校验通过后报 `Cannot connect to Podman... dial tcp 127.0.0.1:60432 actively refused`，随即脚本以 `[ERR] 导入的镜像中没有 localhost/xmnn-runtime:...；请核对 XMNN_VERSION` 收场——把客户引向错误的排障方向（改版本号）。取证：`podman machine list` 显示默认机器 LAST UP 为 Never，CLI 已安装但后台虚拟机从未启动。5-Why 系统性根因——脚本把"CLI 在 PATH 中"（Detect-Runtime 只做 Get-Command/command -v）等同于"守护进程可达"，且 `load` 退出码从未检查：load 对 1.2GB 包失败后继续走镜像 inspect 重试（5×2s），最终用"版本不符"这一唯一被预设的失败模式兜底，掩盖 socket 连不上的真实原因。

**修复（双脚本对等 + 测试锁行为）**：① bash 新增 `assert_runtime_alive()`、ps1 新增 `Assert-RuntimeAlive`：以 `podman/docker info` 探测守护，失败即 fail-fast 并按运行时给出可操作指引（podman→`podman machine start`/Podman Desktop；docker→启动 Docker Desktop 等托盘就绪）；② 在 `load`（sha256 之前，避免对 1.2GB 包做无用哈希）、`up`、`smoke` 三处调用，`init` 保持免守护特性（生成凭证不依赖后台）；③ `load` 调用后立即检查退出码，失败时 die"镜像导入失败，请查看上方原始报错（常见磁盘空间不足），导入幂等可重试"，不再落入误导性版本排查；④ README §7 排障表新增连接失败行与"次生误报版本不符"说明行，§9.2 FAQ 新增 `Cannot connect to Podman` 条目；⑤ test_release_bundle.py 新增 2 例：bash 真实行为测试（stub podman 的 info 恒失败，断言 exit 1、输出含 `podman machine start`、不进入后续流程）与双脚本静态对等断言（预检函数定义+三处调用、load 失败文案）。

**V 对抗审查（四视角）**：① 魔鬼——机器处于 starting 中间态时 `info` 也失败，报错同样指向 start，语义正确；预检误杀风险仅限 load/up/smoke，init/down/ps/logs 行为不变；② 新人——错误信息直接给出可复制命令，无需知道"虚拟机/daemon"概念；③ 老板——改动局限 xmnnctl 双脚本/README/测试，无契约面变更；④ 未来——"安装探测 ≠ 可达性探测"作为预检分层原则固化在注释中，新增运行时命令时按此模板加预检。

**C 同步**：预防措施 `[prevent: daemon-preflight]`——可达性预检前置到重操作之前，同类"未启动机器"故障被结构性拦截，且不再产生误导性次生报错；眼前解困：已执行 `podman machine start`（started successfully），用户重跑 `./xmnnctl.ps1 load` 即可。

### 2026-09-17 · `docs:` release/README 小白化——零基线读者的环境准备、第 0 步、预期输出与词典 FAQ

**关联七概念场景**：场景5「知识沉淀」（E→C，session sc-20260917-readme-newbie，未提交，commit hash 待补）。

**背景**：客户交付文档的真实读者是完全不懂技术的终端用户（只会复制粘贴），旧版 README 默认读者已知"终端/PowerShell/容器/localhost/Token"等概念，且从不描述"成功时长什么样"，用户见到红字即恐慌、不知道播放器后台需先启动。

**修复（纯文档，零行为变更）**：① 开头新增"30 秒建立印象"块（软件电脑 + 播放器类比、红字不等于失败的语义）；② §1 增"开始前三样东西"（Podman Desktop/Docker Desktop 官方链接、PowerShell 7 自检命令 `$PSVersionTable.PSVersion`、解压双层同名目录避坑）；③ §2 新增"第 0 步：在正确文件夹打开终端"（Shift+右键/地址栏 pwsh、`dir` 核对、托盘启动检查、终端粘贴常识）；④ init/load/up 预期输出与耗时表（16 位密码/32 位 Token、1.2 GB 约 1-5 分钟、`====` 方框为成功标志、蓝绿黄红四色语义）；⑤ 首次登录 JupyterLab 指引（Token 从 .env 获取、URL 直登法、内核必须选 Python 3.14 (xmnn runtime)）；⑥ 新增 §9 小白词典（9 条）与高频问题（8 条，含重启后只需 up、可关终端、执行策略 Bypass、Linux chmod）；⑦ 顺带修正事实矛盾：`workspace/` 首次 `up` 才创建，不能作为刚解压时的位置判别标志。

**V 对抗审查**：所有耗时/位数/颜色/命令事实逐行对照 xmnnctl 双脚本源码核实；check-links 通过；纯文档无契约面变更。

**C 同步**：预防措施 `[prevent: zero-baseline-docs]`——五件套（类比开场→环境自检→动作级第 0 步→预期输出表→词典/FAQ）作为客户交付文档基线模板。

### 2026-09-17 · `fix:` 根目录新增 xmnnctl 薄转发壳，`./xmnnctl` 在叠加层根直接可用

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260917-readme-block-unrunnable，未提交，commit hash 待补）。

**现象与根因**：文档接缝条目（同日稍早）发布后，同一用户在叠加层根目录执行 `./xmnnctl init` 仍报"术语不会被识别"——文档提醒被实证无效。5-Why 重估的不可削减事实：①IDE 终端 cwd 固定为叠加层根，是用户不可改变的工作习惯；②用户连续三次均在根目录直接敲命令，真实意图是"当前位置直接可用"而非"读文档换目录"；③根目录与 `release/` 同名文件并列，位置语义只能靠主动阅读文档获得。系统性根因：跨布局执行缺一个**在错误位置可见的可执行入口**，文档是被动信息，无法拦截直觉行为。

**修复（薄转发壳，结构性预防）**：①叠加层根新增 `xmnnctl.ps1`（pwsh）与无扩展名 `xmnnctl`（bash）两个零逻辑壳：ps1 壳 `& release\xmnnctl.ps1 @args; exit $LASTEXITCODE`，bash 壳 `exec .../release/xmnnctl "$@"`（退出码透传）；②真实脚本启动即 `Set-Location`/`cd` 自身目录，`.env`、`workspace`、compose project 操作全部落在 `release/` 侧，根目录零写入；③.gitattributes 规则由 `**/release/xmnnctl` 泛化为 `**/xmnnctl`，覆盖新 bash 壳的 LF 行尾；④两 README 执行位置指引改为"根目录直接 `./xmnnctl`"，排障行同步。

**V 对抗审查（推翻同日早先的否决）**：早先魔鬼视角否决"根目录加壳"的三条理由经重新取证均不成立——①"双脚本漂移"：壳零业务逻辑（4 行转发），真实脚本仍是唯一事实源，无漂移面；②"根目录被 .env/workspace 污染、与同名 compose project 冲突"：真实脚本自定位 `release/`，写入全在客户侧；两套 compose 的 project 名/容器名/端口（2225/8893）本就相同，开发栈与交付栈天然互斥，壳不引入任何新冲突；③"壳误入客户包"：relpack 只取 `release/`，壳永远不到达客户。实测 PowerShell 对无扩展名调用自动补 `.ps1`（`./xmnnctl` 可命中 `xmnnctl.ps1`），与用户截图中的敲法完全吻合。

**C 同步**：预防措施 `[prevent: convenience-shim]`——以可见的可执行入口替代被动文档，同类"位置直觉"故障被结构性消除；眼前解困 `./xmnnctl init` 从叠加层根直接执行。

### 2026-09-17 · `fix:` 叠加层根目录执行 `.\xmnnctl.ps1` 报"不会被识别"——双布局位置接缝补引导

**关联七概念场景**：场景2「问题解决」（F→V→C，session sc-20260917-xmnnctl-ps1-missing，未提交，commit hash 待补）。

**现象与根因**：在 `overlays/xmnn-runtime` 根目录执行 `.\xmnnctl.ps1 init`，PowerShell 报"术语不会被识别为 cmdlet"。取证：脚本物理路径为 `release/xmnnctl.ps1`（客户交付包根），根目录只有开发栈同名文件 `compose.yaml`/`.env.example`。5-Why 系统性根因——开发态栈（根目录，`invoke xmnnrt.*`，extends 仓库 `_shared`）与客户交付态栈（`release/`，自包含、零仓库知识、xmnnctl）两套布局同构、同名文件并列且仅隔一层目录；客户文档 §2 的命令文本隐含"cwd=交付包根"却不携带位置信息，"厂商 pack 后在开发仓库内演练交付脚本"这一高频场景无任一文档覆盖，跨布局执行时错误点零引导。

**修复（文档接缝，零行为变更）**：① release/README.md §2 开头加「执行位置」块（交付包根判别标志：同目录含 `xmnnctl.ps1`+`artifacts/`+`workspace/`；仓库演练给 `cd release` 与 `.\release\xmnnctl.ps1` 两条可复制路径）；② §7 排障表新增行覆盖原始报错关键词"不会被识别"；③ 叠加层根 README §客户独立交付包补厂商演练指引（经 release/，开发态仍走 invoke）。

**V 对抗审查（四视角）**：① 魔鬼——评估"根目录加转发/提示脚本"后否决：双脚本漂移违背单一事实源，且会在 staging 写入 `.env`/`workspace` 并与同名 compose project 的容器/卷互相干扰；② 新人——"交付包根"首次接触不可懂，已给判别标志与可复制命令；③ 老板——改动 2 README + 本条 CHANGELOG，无代码/测试面变更，不破坏 release 契约（零 Python/零仓库知识测试不受影响）；④ 未来——排障行按原始报错词书写，搜索即命中。实测从叠加层根 `.\release\xmnnctl.ps1 version/init` 均成功（脚本 `Set-Location $PSScriptRoot` 自定位，artifacts tar 1.2 GB 与 release.json 完整、git 忽略有效）。

**C 同步**：预防措施 `[prevent: doc-seam]`——双布局边界在客户文档与开发文档两侧显式表达；眼前解困命令 `.\release\xmnnctl.ps1 init` 已实测通过。

### 2026-09-17 · `fix:` xmnnctl 预检在 WSL 非登录 shell 误报"缺少 compose"——PATH 外用户级 companion 回退探测

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260917-preflight-companion，未提交，commit hash 待补）。

**现象与根因**：重打包后真机跑 `./xmnnctl load` 交付链路时，预检 2 秒即死：`[ERR] Podman 已安装但缺少 compose 支持`。取证：`podman compose` 插件在本机确实不可用（5.7.1 未装 provider），但 `podman-compose` 实际已由 pip `--user` 安装在 `~/.local/bin`；登录 shell 经 `~/.profile` 自动包含该目录故一切正常，而 WSL 非登录调用（`wsl -- bash -c`、自动化/最小 PATH 环境）不读 profile，`command -v podman-compose` 失败——"已安装"被误判为"未安装"。原 die 信息只给一句笼统指引，客户无法区分"没装"与"装了但 PATH 没有"。

**修复（双脚本对等 + 测试锁行为）**：① bash `xmnnctl` 新增 `find_companion()`：compose 插件与 PATH 均未命中后，依次回退探测 `$HOME/.local/bin`、`$HOME/bin`（pipx 链接 / pip --user / 旧发行版落点），命中即以绝对路径自动启用并打 WARN 指引加 PATH；彻底缺失时 `compose_missing_die` 输出多行可操作信息（pipx/pip --user 两条安装命令 + WSL 非登录 shell 的 `export PATH` 自救）；docker 分支对 docker-compose 做对等回退。② `xmnnctl.ps1` 对等新增 `Find-UserCompanion`：`%USERPROFILE%\.local\bin`（pipx）+ `%APPDATA%\Python\Python3xx\Scripts`（pip --user，递归深度 2 不穿 site-packages），命中自动启用并 WARN，失败时同样多行可操作报错。③ test_release_bundle.py 新增 3 例：双脚本回退/提示静态对等断言；bash 真实行为测试（隔离 HOME/PATH + stub podman，stdin 喂入脚本源码剥掉末行 main 后 source 调用 detect_runtime），正例断言选中 `~/.local/bin/podman-compose` 并告警、负例断言 exit 1 且报错含安装命令与 PATH 自救；无 bash 环境自动 skip。④ README 排障表同步。

**V 对抗审查（踩坑实证）**：① 行为测试经 WSL 互操作执行连踩三坑并固化为注释：`bash -c` 内联多行/`$()` 被互操作 argv 重组吞掉（须落盘 `bash <file>`）、Windows 路径反斜杠被吞（须传 `/mnt/<drive>` 原生路径）、Windows 文本管道把 `\n` 翻成 `\r\n`（bash 报 `pipefail\r: invalid option`——须以字节喂 stdin，恰与本交付包 CRLF 天敌同源）；② `set -u` 下 `${HOME:-}` 兜底；③ 回退只认 `-x` 可执行文件，不用 PATH 改写全局污染（COMPOSE 数组持绝对路径，作用域仅限本进程）；④ ps1 递归限定 Depth 2，避免每次预检遍历 site-packages；⑤ 行为测试 stub 全部在 WSL 原生 /tmp（exec 位真实），不依赖 9p 元数据。

**C 同步**：预防措施 `[prevent: test-case]`——正/负行为测试使"PATH 外已安装 companion"回归永久锁定；客户侧报错信息从一句话升级为"安装命令 + PATH 自救"自描述。

### 2026-09-16 · `fix:` 客户首跑 `./xmnnctl` 报 `/usr/bin/env: 'bash\r'`——无扩展名 POSIX CLI 漏出 gitattributes LF 保护

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260916-xmnnctl-crlf，未提交，commit hash 待补）。

**现象与根因**：客户控制台执行随包 `xmnnctl` 即报 `/usr/bin/env: 'bash\r': No such file or directory`。取证：仓库 index/工作区该文件均为 LF（本机 core.autocrlf=false），但 `git ls-files --eol` 显示其属性仅为 `text=auto`——脚本无 `.sh` 扩展名，不匹配根 .gitattributes 的 `*.sh text eol=lf`；在 core.autocrlf=true 的 Windows 检出/打包机上工作区被写成 CRLF，拷贝/压缩通道只搬运字节，交付副本首跑即死。shebang 由内核在解释器启动前按字节解析（`bash\r` ≠ `bash`），脚本内既有的 `tr -d '\r'`（防 .env CRLF）无法自救。同类事故 2026-08 已在 `**/bin/jpman` 发生并加过单点规则，但未泛化——`release/xmnnctl` 作为新无扩展名 CLI 漏网；既有测试锁了 `.env.example` 的 LF 与脚本对 .env 的去 CR，唯独没锁脚本文件自身字节。

**修复（三层防御 + 客户自救）**：① 根 .gitattributes 把 jpman 单点升级为「无扩展名 POSIX CLI 清单」，新增 `**/release/xmnnctl text eol=lf`（任何 autocrlf 配置下 checkout 强制 LF）；② relpack 新增纯函数 `find_crlf_shebang_scripts()`（跳过 .ps1/.bat/.cmd 等规范即 CRLF 的 Windows 原生脚本与 artifacts/ GB 级归档），`pack_release()` 打包前 fail-fast 并提示 `git add --renormalize`；③ test_release_bundle.py 新增两例：交付骨架 shebang 脚本零 CR、纯函数命中 CRLF bash/放过 CRLF ps1 与 artifacts；④ release/README 排障表加客户自助行（Linux/WSL `sed -i 's/\r$//'`、macOS BSD sed 变体）。

**V 对抗审查（四视角）**：① 魔鬼——仓库文件已是 LF 为何仍改：故障副本来自 autocrlf=true 的其他检出/交付通道，jpman 前科实证该路径真实存在，规则不可省；② 边界——xmnnctl.ps1 首行同为 shebang 但规范行尾即 CRLF，扫描必须按后缀排除（测试锁定）；③ 边界——artifacts/ 含 GB 级镜像 tar.gz，全量 read_bytes 会爆，按目录跳过；④ 新人——未来新增无扩展 CLI 漏配规则时骨架测试自动红，不依赖人记住 gitattributes；⑤ 未来——pack 是厂商交付唯一 choke point，守卫挂此使坏字节不出门。自有 overlays/bin 全量扫描确认无第二条漏网 POSIX 脚本。

**C 同步**：预防措施 `[prevent: test-case, build-gate]`——gitattributes 源头强制 LF、relpack 打包 fail-fast、shebang-LF 双测试回归锁；客户侧 README 排障行提供存量坏副本自救。

### 2026-09-16 · `feat:` xmnn-runtime 内置 torch 2.14.0+cpu——pytorch 前端工具链固化（稳定版）

**关联七概念场景**：场景3「重构优化」（I→F→V→C，session sc-20260916-runtime-torch-builtin，未提交，commit hash 待补）。

**背景**：torch CPU 此前为容器内手工 `podman exec pip install`（down/重建即丢、默认 PyPI 易拉 CUDA 变体、版本浮动），与"工具链稳定"诉求冲突。

**方案（三层稳定性）**：Containerfile 新增独立 Layer 1（无 COPY 输入、置于 whl 层之前，重打 whl 增量构建复用）：`ARG TORCH_VERSION=2.14.0` 精确 pin + `ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu` 固定官方 CPU 索引（构建日志实证依赖仅 sympy/networkx/fsspec/mpmath/filelock，零 nvidia 包）；只装 torch 不装 torchvision（compile_api 仅 torch.jit.load+relay 前端，四 demo 实测不需要）；builder 镜像与 wheel pyproject 不动（torch 为函数内 lazy import，Nuitka 不 follow）。守卫新增第 10 项硬断言 `torch.version.cuda is None` + jit 可用 + CUDA 不可用 + CPU 张量算子，root/devuser 双身份构建期执行。

**V 验证**：`inv xmnnrt.build --no-cache` 真机构建成功（torch 196 MB 下载层），构建期 10/10 PASS；**全新容器零手装** `xmflow pipeline -n demo.pytorch.resnet18 -t compile,accuracy` 与 `demo.two_inputs` 均 2/2 成功，输出余弦 0.9989583 / 0.9998791，与手装 torch 时逐位一致；独立 `podman run` 守卫复跑 10/10。镜像体积 2.29→3.18 GB（torch CPU 解压约 0.9 GB，仍小于 xmnn-dev 4.69 GB）。daemon-free 95 passed/1 skipped（smoke docstring 黄金断言 9→10 项同步）。

**C 同步**：xmnnrt-overlay.md §4 新增 torch 内置层契约（版本 pin/索引禁令/层序/升级双点）；runtime README「PyTorch 前端说明（torch 已内置）」+ 体积取舍 + torchvision 薄层层叠范式 + 排障（旧镜像/CUDA 变体）；docs/13 改为开箱即用说明；预防措施 `[prevent: build-gate]`——第 10 项守卫使 CUDA 变体/缺失 torch 在构建期即失败。

### 2026-09-16 · `feat:` xmnnrt.\* wheel 消费运行时栈——builder/runtime 镜像分离（第四声明式栈）

**关联七概念场景**：场景3「重构优化」（I→F→A→V→C，session sc-20260916-xmnn-wheel-split，未提交，commit hash 待补）。

**洞察与方案**：`inv xmnn.wheel` 原在重型开发镜像内完成构建后，verify-wheel.sh 仅以同镜像 `--system-site-packages` venv + `--no-deps` 验证（证明"开发镜像里能 import"，从未证明干净客户机从零安装）；且 [xmnn-overlay.md §9](../.agents/rules/xmnn-overlay.md) 早已裁决 wheel 消费型 scratch 栈"不回流 xmnn-dev"但从未落地。第一性原理：wheel 是构建器→运行时唯一制品契约（cp314 GIL、`_libs` RPATH `$ORIGIN` 自包含、内置 `.pth`、19 依赖元数据），两镜像 FROM 同一 rootless 基底即 ABI 同源。新增第四栈 `overlays/xmnn-runtime`（namespace `xmnnrt`，形态 A，2225/8893）：whl 装 base env `/opt/conda` + 补 ipykernel + 注册 `Python 3.14 (xmnn runtime)` 交付内核（env 仅 PATH 白名单）；零 LLVM/Nuitka 工具链、零源码挂载。

**whl 暂存契约**：`xmnnrt.build/up` 调内核构建前把 whl 暂存进 overlay `wheels/`（显式 `--wheel` > workspace/dist 最新 mtime > 已暂存复用 > Exit 1 指引；暂存区同时只留一个 whl；whl 不入 git、.dockerignore 反放行）。build/up 为 ≤160 行声明模块中的薄封装（与 build-tvm/wheel 长任务同性质豁免），不复制任何编排函数（C14）。

**V 验证**：daemon-free 79 passed/1 skipped（surface 黄金清单新增 xmnnrt 任务集/docstring/签名/短选项/模块边界，compose-merge GOLDEN 新增 xmnnrt 渲染断言）；真机 podman-machine-default：`invoke xmnnrt.build --pip-mirror tuna` 桥接构建 COMMIT 成功（169.6 MB whl），构建期 9 项守卫 root+devuser 双身份 9/9 PASS（cp314 GIL ABI、site-packages 路径黑名单 /workspace|/opt/xmnn-builder、_libs/libtvm+libLLVM、干净环境 ctypes 加载、tvm.build llvm 向量乘 2、relay 数据、bootstrap .pth、数据三目录、内核可见）；`podman run --rm --entrypoint /opt/conda/bin/python localhost/xmnn-runtime:latest /opt/xmnnrt-smoke/_runtime_smoke.py` 独立容器复跑 9/9 PASS；真机 E2E：裸 `podman-compose up -d` 起栈（2225/8893 Up，标签 project=xmnn-runtime/service=xmnnrt 正确），HostConfig 与 xmnn-dev 同族一致（SEC label=disable、privileged=false；devices/cgroupns 为 podman-compose 1.6 既有空操作，容器内 /dev/fuse 节点由 crun 默认提供），Jupyter HTTP 302、`xmnn-runtime` kernelspec 对 main env 可见、compose exec 守卫 9/9，`podman-compose down` 后残留计数 0。镜像体积实测 rootless 1.19 GB → runtime 2.29 GB（xmnn-dev 4.69 GB，省 51%；约 170 MB whl COPY 层为单阶段已知冗余）。

**V 对抗审查（四视角）**：① P0 同名 whl 陈旧——dev0 wheel 文件名恒定，旧逻辑只比文件名会在重打包后复用旧暂存 whl，修正为 name+size+mtime_ns 三全等才跳过（copy2 保 mtime 保证二次运行正确复用），新增 tests/test_xmnnrt_stage.py 7 例锁定选择顺序；② 依赖开放区间版本漂移、③ whl COPY 层体积两项记录为已知设计边界（README「已知边界」+ 规则 §4），版本锁定归属 wheel 打包端。

**C 同步**：新增规则 [xmnnrt-overlay.md](../.agents/rules/xmnnrt-overlay.md)（7 节特有契约）；docs/13 + docs 索引、client AGENTS/.agents README/apps AGENTS 路由登记；根 .env.example 加 XMNNRT 段；预防措施 `[prevent: test-case, build-gate]`——黄金两表锁定栈表面与 compose 渲染，9 项守卫构建期硬失败，暂存选择顺序 7 例单测锁定；全量 95 passed/1 skipped。

### 2026-09-16 · `fix:` `inv xmnn.wheel` 构建成功却 exit 1——invoke 3.0.3 × Python 3.14 stdin 线程 FIONREAD 缓冲溢出（假失败）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260916-xmnn-wheel-stdin，未提交，commit hash 待补）。

**现象与根因**：Windows 原生 `inv xmnn.wheel > error.log` 经透明桥接执行，容器内 build-wheel.sh 全流程成功（🎉 WHEEL BUILD COMPLETE，170M whl 已产出），WSL 内 invoke 收尾却抛 `ThreadException(SystemError: buffer overflow)`，桥接层 Exit(1) 报「WSL 桥接命令失败」。取证链：① 崩溃点 `invoke/runners.py::handle_stdin → read_our_stdin → terminals.bytes_to_read → fcntl.ioctl(input_, termios.FIONREAD, b"  ")`；② invoke 3.0.3 对 TTY stdin 用 **2 字节**缓冲做 FIONREAD（按 signed short 解析），而 Linux 内核固定写回 `sizeof(int)`=4 字节；③ Python 3.14 加固 fcntl 后越界写直接 `SystemError: buffer overflow`——pty 真机探针证明**与队列字节数无关（queued=0 也必崩，py3.14.2）**；④ 桥接 stdin 是 console 中继 pty（isatty=真），`pty=True` 默认启动 stdin 转发线程，长任务收尾时中继 fd 半关闭/可读，线程必崩。影响面覆盖全部 `run_cmd(pty=True)` 路径（build/up/down/logs/wheel/build-tvm）及 py3.14 下的真交互命令（首次按键即崩）。

**修复（共享包 `apps/containers/shared/src/jpman_common/proc.py`，builder/client 同族生效）**：① `run_cmd` 新增 `forward_stdin: bool = False`，默认向 `c.run` 注入 invoke 钦定的 `in_stream=False`——invoke 因此根本不创建 stdin 转发线程（`runners.py::create_io_threads` 对 falsy in_stream 直接跳过），编排命令全部非交互、零行为损失，Ctrl+C 仍经 KeyboardInterrupt→send_interrupt 信号路径传播；② 新增 `apply_invoke_stdin_compat()`，用 4 字节缓冲重做 FIONREAD 的兼容函数幂等替换 **两处绑定**（`invoke.terminals.bytes_to_read` 定义点 + `invoke.runners` 顶部 `from .terminals import bytes_to_read` 的名字绑定——三态 pty 探针实证只改定义点无效），进程导入 proc 时自动应用（仅 POSIX，Windows 静默跳过）；③ 仅真交互式入口 `env.shell` 与 builder `interact.shell`/`_exec_via_cli`（`podman run/exec -it … bash`）显式 `forward_stdin=True` opt-in，其 py3.14 键盘输入由兼容补丁兜底。

**V 验证（三态 pty 真机探针 + 双平台单测）**：在 podman-machine-default（invoke 3.0.3 / py3.14.2）以 pty.fork 注入 stdin 事件——原生 invoke 必现 ThreadException（crash 复现）、`in_stream=False` 干净退出、兼容补丁保留转发也干净退出；先证明 2 字节 `fcntl.ioctl(FIONREAD, b"  ")` 在该环境 queued=0 即抛 SystemError，再断言 4 字节实现返回正整数。新增 5 例单测（默认注入断言、opt-in 不注入、非 fileno/非 tty 回退 1、POSIX tty 不溢出、双绑定幂等）：Windows py314 185 passed/2 skipped（POSIX 用例跳过），WSL 全量 205 中 proc/桥接/内核 80 passed/1 skipped（另 6 个失败经 stash 基线对比为改动前既有的 Windows 专属测试 Linux 平台错配，与本修复无关）。真机重跑 `invoke xmnn.wheel` 退出码 0、日志无 ThreadException。

**C 同步**：docs/04 新增 W-I13（成功却 exit 1 的判别要点 + 勿重跑长任务）；docs/03 新增「透明桥接 stdin 契约」节；预防措施 `[prevent: test-case]`——默认 `in_stream=False`、opt-in 边界与 FIONREAD 兼容路径全部由 daemon-free/pty 单测锁定。

### 2026-09-16 · `fix:` `inv <ns>.build` 桥接被 enterns 劫持进交互 shell + VM 回收后 `/run/user/<uid>` 丢失 podman exit 125

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260916-xmnn-build-shell，未提交，commit hash 待补）。

**现象与根因（双根因同日实证）**：① 用户在 Windows 原生执行 `inv xmnn.build`，任务未运行却进入一个交互 shell（伴随 wslmotd *nested process namespace... exit twice* 文案）。取证：桥接器 `utils.run_in_wsl_bridge` 用 `wsl.exe -d podman-machine-default -- bash -lc <任务>` 启动**登录** shell；Fedora-WSL 系发行版 `/etc/profile.d/enterns.sh` 检测到嵌套 systemd（`/lib/systemd/systemd` 非 PID 1）即无参执行 `/usr/local/bin/enterns`，其对普通用户走 `sudo nsenter -m -p -t <pid> su -l $USER`——一个全新交互登录 shell，原任务命令串在命名空间切换中被丢弃；同目录 `docker-host.sh` 登录时执行 `podman info`，podman 未就绪还会污染 `DOCKER_HOST=unix://`。② VM 被 WSL 回收重启后（容器呈 `Exited (0) 292 years ago`），tmpfs 上的 `/run/user/1000`（正常由 systemd-logind/pam 会话创建）未重建，rootless podman 任意命令报 `creating events dirs: mkdir /run/user/1000: permission denied`（exit 125）；实测仅 `export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir` 不能替代该目录（events dir 硬编码回退 /run/user/<uid>）。

**修复（编排层，`src/jpman_client/tasks/utils.py` + `overlay_core.py`，三栈同族生效）**：① 桥接由登录 `bash -lc` 改为非登录 `bash -c`（与实证可靠的 `.temp/xmnn-launch/run-inv.sh` 同构），PATH 显式前置 `~/.local/bin`、LANG 兜底 `C.UTF-8`，profile 的 enterns/docker-host 两个副作用均不触发；② 新增 `ensure_wsl_rootless_runtime()`（仅 `/proc/version` 含 microsoft 时动作：XDG 空且 `/mnt/wslg/runtime-dir` 可写则兜底；`/run/user/<uid>` 缺失则 `sudo -n` 幂等 mkdir/chown/chmod 700，免密不可用仅警告不阻断），在 `gate_platform` 的 Linux 放行路径调用——Windows 桥接重入与 WSL 内原生 invoke 两个入口同时覆盖；③ 顺带修正桥接失败 `Exit(rc, msg)` 参数反序（invoke 签名 `Exit(message, code=None)`，旧写法退出码恒为 1、rc 被当消息），改为 `Exit(message, code=rc)`。

**V 验证**：daemon-free 新增 `tests/test_wsl_bridge.py` 9 例（非登录 argv 断言、空 argv 不裸开 shell、rc 原样上抛、运行时自愈的平台判定/幂等/sudo 失败不阻断/XDG 兜底），client 全套 84 passed/1 skipped。真机（podman-machine-default）：模拟回收 `sudo rm -rf /run/user/1000` 后 Windows `inv xmnn.ps` 自动自愈且无登录污染 warning；`inv xmnn.build --pip-mirror tuna --conda-mirror tuna` 直接进入 podman build 流并 COMMIT 成功（90s，不再进 shell）；`inv xmnn.up --skip-build` 恢复被回收栈（up_preflight 再次收敛 Exited 残留与孤儿 rootlessport），单会话浸泡 80s 后 exec OK、Jupyter 302、`xmnn.smoke` 全过（双 ABI/LLVM 22.1.8/Nuitka 4.1.3/挂载源码/tvm.build 向量加）。

**独立事件记录（非本项目缺陷）**：验证期间 08:53:04 一个外部 Go-http-client 经 `podman.sock` 发起 `POST /v5.7.0/libpod/system/prune`（all=false），删除了两个 Exited 容器（含跨项目的 jupyter-podman 单容器）、空 pod 与 6 个悬空镜像（journald user journal 取证；Windows 侧无 Podman Desktop/gvproxy 进程，bash/root history 无 prune 记录）。有 tag 镜像与命名卷无损，`inv up` 秒级恢复；预防措施是避免在共享该 socket 的 UI/自动化中执行 system prune。

**C 同步**：docs/04 新增 W-I11/W-I12；windows-wsl.md 新增 §8「透明桥接硬契约：非登录 shell + rootless 运行时自愈」；预防措施 `[prevent: test-case]`（非登录 argv 与自愈分支全部 daemon-free 单测锁定）。

### 2026-09-16 · `fix:` WSL 回收循环假 Up 自动识别：`up_preflight` 新增 init PID 活体判据与 stale conmon 定点回收

**关联七概念场景**：场景2「问题解决」（I→F→A→V→C，session sc-20260915-fake-up-auto-heal，未提交，commit hash 待补）。

**背景与根因**：W-I8 记录的假 Up（WSL 发行版回收循环后 daemon libpod sqlite 仍记 running，但容器 init 进程在宿主已死——`ps`/端口/HTTP 302 均为孤儿 conmon/rootlessport 制造的假象，exec 报 `crun ... status: No such file`）首版只有手工五步定向清理；跨平面反复交替还会累积已删容器的 stale conmon（不持端口、不阻断 up 但是进程垃圾）。daemon 单视角探测必然被假象欺骗。

**修复（编排层 `src/jpman_client/tasks/overlay_core.py`，三栈同族生效）**：① 新增 `_container_init_pid`（`inspect --format {{.State.Pid}}`）+ `_host_process_alive`（宿主 `ps -p <pid> -o pid=`，零双引号探针）+ `_container_truly_alive` 双重活体判据；`up_preflight` 在 reconcile 之后、config_files 标签比对之前检测假 Up，命中先 `compose down` 清除失实记录再进入孤儿回收；② 新增 `parse_conmon_process`/`_list_stale_conmons`/`reap_stale_conmons`——双门判定（进程名 conmon + `-n` 为本栈容器名 + 64 位 ID 不在 `podman ps -aq` 运行集合），TERM→0.5s→复检→KILL，活 conmon 与他栈 conmon 绝不触碰，与 rootlessport 回收同一前置条件；③ `require_running`（build-tvm/wheel/build-native 长任务前置）从 daemon 视角收紧为真活体，假 Up 直接 Exit(1) 并提示重新 up，不自动重建以免破坏长任务现场。

**V 验证**：daemon-free 单测新增 6 例——真实 conmon 命令行解析、双门只收本栈 stale（活/他栈不动）、rootlessport 与 stale conmon 同轮分别精确点名 kill、假 Up 强制 down 后再回收、真活体 no-op、`require_running` 拒绝假 Up；FakeRunner 的 TERM 模拟改为按点名 PID 从各自数据源移除（对齐真机语义）。

**C 同步**：本条为 W-I8（症状矩阵/手工五步清理）与 compose-overlay-ops v1.0.2「exec 是唯一活体判据」的自动化代码落地；预防措施 `[prevent: test-case]`——活体判据、双门回收与拦截路径全部由 daemon-free 单测锁定。

### 2026-09-15 · `fix:` 跨控制平面标签分歧致 `up -d` 强制 recreate + 孤儿 rootlessport 占 2223：`up_preflight` 三道自愈

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260915-xmnn-2223-bind，未提交，commit hash 待补）。

**现象与根因（三次确定性复现）**：在 overlay 目录裸跑 Windows 原生 `podman-compose up -d` 报 `conmon exited prematurely: conmon process killed` 后接 `rootlessport listen tcp4 0.0.0.0:2223: bind: address already in use`（exit 125）。取证链：`podman inspect` 活体容器标签——裸 compose 写 `com.docker.compose.project.config_files=D:\spaces\...\compose.yaml`，WSL 桥接 invoke 固定下发 `--file /mnt/d/.../compose.yaml`；podman-compose 把该标签**原文**纳入 config-hash，两平面交替操作即判配置漂移强制 recreate；podman-compose 1.6「每项目一 pod」模式强拆 infra conmon 时，rootlessport 已被 WSL `/init` 收养成为孤儿继续监听 2223/8890，新 pod bind 必败（**真机实证：先优雅 down 同样可能留下该孤儿**，②③两道都必须存在）。反证：同一平面连续两次 `podman-compose up -d` 幂等无重建。

**修复（编排层，`src/jpman_client/tasks/overlay_core.py`，三栈同族生效）**：`up_stack` 在 `up -d` 前改调新增 `up_preflight`，顺序三道——① Created/Exited 项目残留（旧 `reconcile_stale_containers` 保留）先 `compose down`（不带 --volumes）；② 活体容器 config_files 标签原文与本平面 `--file` 不一致先优雅 down（对抗审查曾误写成 `/mnt/d`↔`D:\` 路径等价归一，被 V 阶段真机探针证伪：compose hash 按原文算，等价归一无效，已改回原文比较 `config_paths_diverge`）；③ 无活体项目容器时 `ss -ltnp` 解析本栈端口持有者，仅对进程名 **rootlessport** 的 PID 定点 TERM→复检→KILL（他栈 pasta/conmon 绝不触碰；ss 缺失静默跳过不阻断）。纯逻辑（`parse_ss_port_holders`/`config_paths_diverge`）抽出做 daemon-free 单测。

**V 真机验收（podman-machine-default，jupyter-podman 2222/8888 全程零影响）**：V-1 破损现场（Created 残留+孤儿 pid=111397）`invoke xmnn.up --skip-build` 自动 down→定点 kill→up 成功；V-2 干净状态 Windows 裸 compose up 成功；V-3 裸 compose 同平面二次执行无重建（幂等）；V-4 Windows py314 `invoke xmnn.up` 桥接触发跨平面分支（打印分歧标签→优雅 down，down 过程如期出现 conmon 竞态→分支③回收孤儿 126644→up 成功）；V-5 invoke 同平面二次执行无警告无重建。终验：浸泡 80s 后 exec OK、Jupyter 302、SSH banner 正常；离线单测 69 passed/1 skipped，ruff 全过。

**C 同步**：docs/04 新增 W-I10；xmnn-overlay.md「up 残留自愈契约」升级为「up 三道 preflight 自愈契约」（含量化根因链与单一控制平面纪律）；compose-overlay-ops 技能错误表新增跨平面根因行与 v1.0.3 changelog；overlays/xmnn-dev/README.md 排障段同步。

### 2026-09-15 · `feat:` xmnn wheel 首次在重建栈内全流程打包成功（170M，10/10 隔离验证）；`fix:` 排除假 Up 容器与桥接发行版缺工具两个阻断

**关联七概念场景**：场景2「问题解决」（I→F→A→V→C，session sc-20260915-xmnn-wheel-build，未提交，commit hash 待补）。

**任务**：`invoke xmnn.wheel`——容器内 Nuitka 串行编译 tvm → 并行 vta/xmnn → scikit-build/CMake 组装 wheel，产物落宿主 `workspace/dist/`。

**阻断①（W-I9）桥接发行版未备 client 环境**：Windows 原生 invoke 透明桥接 podman-machine-default 后报 `bash: line 1: invoke: command not found`（exit 127）。该发行版为 Fedora 43 Container Image，自带 python3 3.14 但**无 pip**（`No module named pip`）；直接装 client 又报 `No matching distribution found for jpman-common`（jpman-common 是 `apps/containers/shared` 纯本地兄弟包，PyPI 无发布）。修复（发行版内，均 `--user`）：`python3 -m ensurepip --user` → `pip install -e ../shared` → `pip install -e '.[compose]'`（tuna 源），invoke/podman-compose 1.6.0 落 `~/.local/bin`（桥接器已自动 PATH 前置）。

**阻断②（W-I8）容器假 Up**：重装环境后 exec 报 `crun: container <id> does not exist: open /mnt/wslg/runtime-dir/crun/<id>/status: No such file`（127），但 `podman ps` 显示 Up、`inspect .State=running`、Jupyter 8890 仍 302。取证：inspect 的 PID 在宿主已不存在、`crun/` 下仅剩 `.cache`/`.empty-directory`，stale conmon(67549) 与孤儿 rootlessport(67532, 持有 2223/8890 LISTEN) 仍存活——libpod sqlite 与内核进程在发行版回收循环后脱节，ps/HTTP 均为假象。修复（**免 `wsl --shutdown` 的定向清理**，不影响同发行版健康的 jupyter-podman 栈）：`invoke xmnn.down`（容忍 conmon prematurely/netavark netns ENOENT 告警）→ `ss -ltnp` 定位并 kill 孤儿 rootlessport → `ps -ef | grep <容器ID>` kill stale conmon → 复查端口 free → `invoke xmnn.up --skip-build`，浸泡 75s 后 exec/Jupyter 302/libtvm.so 三验证通过。

**V 真机验收**：V-1 wheel 全流程 exit 0，tvm 串行 + vta/xmnn 并行 Nuitka 编译（编译期 7 clang 满载 + ccache 活跃实证）→ wheel 组装成功；V-2 产物 `workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（169.6MB，宿主 bind 目录可见）；V-3 `verify-wheel.sh` 隔离 venv **10 passed, 0 failed**（含真实 `tvm.build(llvm)` 向量加、relay/std 数据、bootstrap .pth、autolibs/tools_cpp/fonts 打包，base env 零污染）。

**C 同步**：docs/04 新增 W-I8（假 Up 症状矩阵/五步定向清理/活体探针预防）、W-I9（桥接发行版三步安装序）；compose-overlay-ops 技能升 v1.0.2（错误表新增"假 Up"行、端口占用行两因扩三因——新增 `ss -ltnp` 可见显式 rootlessport 持有者的可定向 kill 变体并置于 wslrelay 粘滞/wsl --shutdown 裁决之前、步骤 1 安装序修正、Gotchas 第 9 条"exec 是唯一活体判据"）。

### 2026-09-15 · `fix:` `build-tvm.sh` 配置阶段 rmtree(build/CMakeFiles) EACCES：9p 跨上下文无主旧产物 + 清理函数零容错

**关联七概念场景**：场景2「问题解决」（I→F→A→V→C，session sc-20260915-tvm-build-rmtree-eacces，未提交）。

**根因（双叠加）**：`podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-tvm.sh` 在 `inv config -f` 清空 build/ 时 `shutil.rmtree` → `os.unlink` 报 `PermissionError [Errno 13] CMakeFiles`。实证：挂载为 9p drvfs（`D:\ → /workspace/npu_tvm,uid=1000`），build/ 内 10:42 旧产物属主 `65534:65534`、目录 755（其他映射上下文生成），而 build/ 本身 0:0 777；容器内 root 对无主文件 chmod 直接 EPERM（9p 服务端在 Windows 侧判权、root 无 DAC 绕过），devuser(1000) 写 CMakeFiles 同样 denied；root/1000 新建文件恒为 0:0 777 且可互删——只有这批旧文件卡死。npu_tvm `tasks.py::_clear_directory_contents` 旧实现为裸 `shutil.rmtree(child)`，无 onexc 容错与指引。

**修复（F 裁决）**：①一次性解封走宿主 NTFS（ACL 允许、9p 即时同步）：PowerShell `Remove-Item -Recurse -Force <NPU_TVM_PATH>\build`，容器内随即可见目录消失；②`external/chaos/npu_tvm/tasks.py`（**属用户自有 pu_tvm.git 仓，非 SpecWeave 文件，需另行提交到该仓**）`_clear_directory_contents` 加 `onexc`：PermissionError 先 chmod 0777 重试（覆盖只读位场景，含文件 unlink 同构处理），再失败抛带宿主清理命令的中文 PermissionError。否决：容器内 chmod/chown/换 uid1000 执行（实测均被 9p 拒绝/仍非属主）、改 build 目录到 named volume（破坏 build/ 在源码树复用 libtvm.so 的调试设计，属大改）。

**V 真机验收（xmnn-dev，podman 5.7.0-rc3）**：V-1 清理后容器内确认 build/ 消失；V-2 `py_compile tasks.py` OK；V-3 真机重跑 build-tvm.sh：config -f 通过原失败点、ninja -j16 全量成功（ccache 热），产出 `libtvm.so`(78MB)/`libtvm_runtime.so`/VTA 双库，符号隐藏+18462 导出守卫全过，exit 0；V-4 **二次执行**验证重复强制清理闭环：887 目标重建 101.7s 成功、末次 `ninja: no work to do`（证明新建 0:0 777 文件的清空-重建幂等）。

**C 同步**：docs/04 新增 W-I7；.agents/rules/xmnn-overlay.md 新增「9p 无主旧产物清理契约」（容器内无解、必须宿主侧清理、tasks.py 外部仓归属说明）；builder/scripts/build-tvm.sh 头注更正——原「容器内 rm -rf build 强制全量」在该场景会失败，改为宿主 PowerShell 删除指引。

### 2026-09-15 · `fix:` 裸 `podman-compose up -d` 双根因修复：僵尸 editable 安装 + 1.6.0 Windows 盘符误判 git URL 丢失 `-f`

**关联七概念场景**：场景2「问题解决」（I→F→A→V→C，session sc-20260915-podman-compose-broken，本次按用户要求未提交，commit hash 待补）。

**根因（双叠加，均在宿主 Windows 原生 py314）**：① **僵尸 editable**——`pip show podman-compose` 1.6.0 的 `Editable project location` 指向已删除的 `D:\spaces\SpecWeave\external\dao\action\Containers\podman-compose`，finder MAPPING 死路径 → 入口垫片 `podman-compose.exe` 存在但 `import podman_compose` 必失败（`ModuleNotFoundError`），另有 pip 中断残留 `~odman_compose-1.6.0.dist-info`；② **上游盘符误判 bug**——重装后 `up -d` 稳定报 `no Containerfile or Dockerfile specified or found in context directory`，进程内 monkeypatch 抓真实 build argv 证实**缺失 `-f`**：1.6.0 `podman_compose.py::is_context_git_url()` 对 Windows 绝对路径 `D:\...` 经 `urllib.parse.urlparse` 得到 `scheme='d'`，L3245 `r.scheme != "" and r.netloc == "" and r.path != ""` 误判 git URL → L3297 分支跳过自定义 dockerfile 的 `-f` 注入；自定义 `Containerfile.xmnn-dev` 必现，默认名 Containerfile 的栈不受影响。同形态手工 `podman build -f <abs> <abs ctx>` 正常（对照实证排除 podman 本体问题）。

**修复（第一性原理裁决：宿主编排器按宿主约定安装；上游 bug 最小语义补丁）**：①卸载僵尸 editable + 清理 `~odman_compose` 残骸，PyPI 常规安装 `podman-compose>=1.0.0`（1.6.0；**不**用 `jupyter-podman-rootless/upstream/podman-compose` 镜像专用固定 commit 快照）；②站点包一行补丁：`is_context_git_url` 条件改 `len(r.scheme) > 1 and r.netloc == "" and r.path != ""`（盘符单字母 vs 真实 scheme 多字母）。vendored 快照不同步修改——镜像内 Linux 构建无盘符不触发。TRAE 沙箱硬保护 conda `Scripts\`，卸载/重装入口 exe 由用户在自有终端完成，site-packages 补丁由 agent 执行。

**V 真机验收（podman 5.7.0-rc3 Windows 远程客户端，xmnn-dev 栈）**：V-1 `podman-compose version`=1.6.0 且 `pip show` 无 Editable；V-2 `podman-compose config` extends 合并正常；V-3 补丁后抓 argv 含 `-f D:\...\Containerfile.xmnn-dev`，补丁语义 8 用例（D:/C: 盘符、相对路径、https/git/ssh/scp）全过；V-4 真机 `podman-compose up -d` 构建（全缓存）+ 起容器成功，`xmnn-dev` Up、`0.0.0.0:2223->22`/`8890->8888` 监听，应用层 HTTP 8890 `/api`=200、SSH 2223 banner `SSH-2.0-OpenSSH_10.2p1`，supervisord sshd/jupyter 双 RUNNING。诊断探针/临时日志/`:probe` 镜像 tag 用后即清。

**C 同步**：docs/04-troubleshooting-guide.md 新增 W-I5（僵尸 editable 症状/清理/PyPI 重装/预防：禁止从临时目录 editable 装编排器）与 W-I6（盘符误判根因/一行补丁/重装后须重打/argv `-f` 验证法）。

### 2026-09-15 · `fix:` `invoke env.build-layer` 叠加镜像构建失败：镜像内缺 jpman-common（No matching distribution found）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260915-env-buildlayer-common）。

**根因**：同日 jpman-common 重构（见下方 refactor 条）把 client 的平台/连接层依赖上移到兄弟包 `apps/containers/shared`（纯本地包，PyPI 无发布），client `pyproject.toml` 已声明 `dependencies=["jpman-common"]`，但镜像构建链路未同步——`Containerfile.client` 的 build context 只有 client 根目录，STEP 8 `pip install -e /opt/apps/containers/client/` 在镜像内解析依赖时无本地源码可装，必报 `ERROR: No matching distribution found for jpman-common`（重构验收当时只覆盖宿主 editable + daemon-free 单测，未重跑镜像构建）。连锁影响：env.shell / env.run-cmd / `invoke run --rebuild-layer` 全断（重建失败后仅回退旧镜像）。

**修复（第一性原理裁决：构建期本质需求 = 两个本地源码树 + 安装顺序）**：采用 podman **命名构建上下文**——① `Containerfile.client` 新增 `COPY --chown=devuser:devuser --from=shared . /opt/apps/containers/shared/`，RUN 内安装顺序改为先 shared 后 client 两个 `pip install -e --no-build-isolation`，构建期自检改为同时 `import jpman_common, jpman_client`，清理段追加 `shared/build`；② `env_in_container.py::rebuild_client_layer()` 自动注入 `--build-context shared=<root.parent>/shared`（main context 仍为 client 根），构建前对 `shared/pyproject.toml` 做存在性中文预检（缺失 return False 不裸跑）。否决方案：父目录 `apps/containers` 作 context（含 builder `.image-cache/` 等 GB 级内容，ignore 脆弱）、task 临时复制源码树（临时目录生命周期）、宿主预构建 wheel（多余构建步骤）。

**V 真机验收（podman 5.7.0-rc3 Windows 远程客户端）**：V-1 `invoke env.build-layer` 全 16 步构建成功并打 tag（命名上下文的宿主绝对路径在客户端侧正确解析打包）；V-2 运行容器内 `pip show jpman-common`=0.1.0、`import jpman_common` 命中 editable 真实目录 `/opt/apps/containers/shared/src/jpman_common/`，jpman_client 同验；V-3 二次构建幂等成功、基底指纹 LABEL 保留；V-4 shared+client 单测 **160 passed / 1 skipped** 零回归。同步：docs/08-env-bootstrap.md（双上下文说明 + 手动 build 必须追加参数）、.agents/rules/invoke-tasks.md §4.3（双构建上下文契约与「新增兄弟包依赖先问构建上下文」预防条款）、Containerfile.client 头注与层注（预防措施：重构移动依赖归属时，必须穷举该依赖的所有安装现场——宿主 editable、镜像构建、CI；只验宿主会漏掉容器链路）。

### 2026-09-15 · `docs:` 固化 Windows shell 引用契约（cmd.exe 通道双引号为正确写法，推翻「3 处双引号遗留」误判）

**关联七概念场景**：场景2「问题解决」（builder `inv run` 修复的 V/C 延伸实证，session sc-20260915-inv-run-stale-container）。

builder 侧 `inv run` 修复后初稿把 client 的 4 处 `--format "..."`（`env_in_container.py` images/digest 2 处、`client_core.py` images/ps 2 处）登记为同款遗留。补验推翻：client 的 invoke **不覆盖** `run.shell`，Windows runner 实测为 `C:\WINDOWS\system32\cmd.exe`（COMSPEC），与 builder 显式锁定的 pwsh 7 是两条相反规则的通道——双引号命令在 cmd.exe 下全部 rc=0 且模板正确展开（含 `|` 分隔模板，Python 解析出 5 行镜像）；单引号会被当字面量传入（实证输出 `'sha256:...'`），将污染 tag 成员判定/digest 指纹比对。故**零代码改动**，仅在 `.agents/rules/invoke-tasks.md` 新增 §3.4「Windows shell 引用契约」固化正反两面规则与现状清单，并同步修正 builder CHANGELOG/规则中的错误遗留描述。验收：诊断脚本 5 用例（images 双/单引号对照、ps table、inspect digest 双/单引号对照）+ 复合模板解析实证，脚本用后即删。

### 2026-09-15 · `refactor:` 学习 OKF 容器知识包重构 apps/containers（jpman-common 共享包 + overlay_core 声明式内核 + compose extends）

**关联七概念场景**：场景3「重构优化」（I→F→A→V→C，V 强制）；用户输入「学习 projects/awesome-okf-xs/doc/bundles/jishu/containers 优化 apps/containers」。规格 `.trae/specs/infra-env/containers-okf-refactor/`（用户已批准）。三项架构裁决：①两端共享包 `apps/containers/shared`，包名 **jpman-common**；②compose 公共段用 **extends 服务级继承**抽 `overlays/_shared/base-rootless.yaml`；③静态等价 + daemon-free 单测验收，真机 E2E 用户环境恢复后后补。

**A 阶段原子交付**：
1. **jpman-common 共享只读层 + 连接层**：新建 `apps/containers/shared/`（scikit-build-core 纯 Python 包）：`proc.py`/`platform_paths.py`/`containers.py` 承载平台/进程/容器只读工具，`connection.py`（653 行，17 导出）承载 SDK 连接层唯一事实源（四级候选/base_url 显式/UTF-16 LE/host_runtime_uid 不硬编码 1000）；client 的 `utils.py`/`client_core.py` 与 builder 的 `tasks/utils.py`/`tasks/client.py` 瘦身为再导出垫片（builder 保留 compose 探测与 sdk_*_kwargs）；两端 pyproject 声明依赖 `jpman-common`，安装顺序先 shared 后两端（`pip install -e shared -e client` / `-e jupyter-podman-rootless`，editable 必须 `--no-build-isolation`）。
2. **overlay_core 数据驱动内核**：`src/jpman_client/tasks/overlay_core.py`（~715 行）：`SourceMount`/`SmokeSpec`/`TaskDocs`/`StackSpec` frozen dataclass + gates/prepare_env/compose_argv/run_compose/reconcile/build/up/down/ps/logs/smoke 内核函数 + `make_stack_tasks()` 六任务工厂；内核零栈知识，只 import 标准库/`.manage`/`.utils`/`jpman_common`。
3. **三栈声明化**：`quant.py` 88 行 / `xmnn.py` 158 行 / `monetize.py` 121 行（均 ≤160），仅 `<NAME>_SPEC` + `TASKS` + 六别名（xmnn/monetize 长任务 build-tvm/wheel、build-native/wheel 例外）；桥接键下沉 `utils._BRIDGE_COMMON_ENV_KEYS`；Grep 三查：同构编排函数与栈名硬编码零命中。
4. **compose extends 公共段**：新建 `overlays/_shared/base-rootless.yaml`（服务 `rootless-base`：network_mode bridge + /dev/fuse + label=disable + cgroupns host + 凭证四变量 + org.specweave.managed-by label + restart unless-stopped；无 volumes/build/env_file/ports/image/container_name）；三栈 compose.yaml 改 `extends: {file: ../_shared/base-rootless.yaml, service: rootless-base}` 只保留差异段。
5. **文档/规则/技能同步**：client `.agents/rules/` 6 文件（quant/xmnn/monetize/invoke-tasks/sdk-connection/windows-wsl）+ docs/10-12 extends 条目 + docs/01 两步安装 + AGENTS.md（9 模块/C14/第四栈路径/文件地图）；builder AGENTS/README/docs 08/09/rules 同步 shared 接线；client-overlay-scaffold 技能升 v1.1.0（SKILL §12/§13、namespace.py.skeleton 声明式重写、compose skeleton extends 形态、delivery-checklist 黄金表门）。

**F 阶段关键实证（知识包 ↔ 本机源码双证）**：
- podman-compose 1.6.0 `_parse_compose_file`（vendor 源码 L2844-L2849）先把 extends.file 按引用文件目录 join 重写绝对路径，`resolve_extends`（L2364）执行 `rec_merge({}, base, current)`——故 run_compose **无需 cd 前缀**；合并语义 dict 递归/普通 list 追加/command、entrypoint 无条件替换；volumes 特例（L2289-L2297）：仅短语法字符串按 target 去重且覆盖方获胜，**长语法 dict bind 不去重**；另有 `!override`/`!reset` 标签（三栈未使用）。
- `podman-compose config` 打印的是 resolve_extends **之前**的 merged_yaml（不含继承字段，勿据此误判失败）；真实继承结果须驱动 `_parse_args(['-f',...,'up','--no-start'])` 后读 `self.containers`。
- 真实渲染黄金结果：quant devices=[/dev/fuse] env 6 键；quant GPU devices=[/dev/fuse,/dev/dri]；xmnn env 11 键 volumes 5 target；monetize env 6 键 volumes 2 target ports 2224/8892；三栈 network_mode=bridge、labels 并集、privileged 缺省。

**⚠️ 已知行为变更（用户可见）**：quant 栈迁移前 compose.yaml **无 network_mode**，现随基文件获得 `network_mode: bridge`。依据：xmnn 旧文件头 2026-09-14 aardvark-dns user scope bus 实证（rootless 下 bridge 是可用配置）；回归风险低，但属语义变化，真机 up 时须确认 quant 服务名解析/出网正常。

**V 等价门（静态，已过）**：shared 92 passed（覆盖 97%）；client 全量 62 passed 1 skipped（含 test_overlay_core 内核黄金快照、test_tasks_surface 命名空间黄金清单、test_compose_merge 23 用例：rec_merge 模拟器 + 真实文件渲染 + **与真实 podman-compose 1.6.0 rec_merge 的对照探针**）；`invoke --list` 与迁移前逐行一致（根 7 + container/env 别名 + quant 6 + xmnn 8 + monetize 8）；红线 Grep（内核 import 栈、栈 import podman、同构函数、_BRIDGE_ENV_KEYS 旧名）零命中。

**R 独立对抗审查（CONDITIONAL PASS → 修复后 PASS，见规格 review.md）**：fresh 子代理以 vendor/podman-compose 1.6.0 源码（只读 submodule）+ 运行探针核对，0 blocker；修复 2 major + 2 minor：① **M1** 合并模拟器 volumes 两处反向语义更正——短语法实为「覆盖方按 target 获胜并移尾部」（vendor L2289-L2297）、长语法 dict bind 真实**不去重**；反转错误自证用例，新增长语法/匿名卷/类型冲突用例与 2 条真实 rec_merge 对照测试（环境无 podman-compose 时 skip）；② **M2** 5+ 处「volumes 按 target 去重」失实表述更正（基文件头/quant 规则 §4 §4.1/xmnn/monetize 规则/SKILL §7.6+G15/compose 骨架/本条 F 阶段实证）；③ M3 模拟器 docstring 声明保真边界（标签/归一化/插值子集/类型冲突 ValueError）；④ M4 删除 tasks/__init__.py 三栈零消费 ns.configure 死配置块（唯一事实源已是 StackSpec）。另处置 N1（行号 L2845-2847→L2844-L2849、resolve_extends L2329→L2364，共 6 处）、N2（模拟器渲染括号改为真实管线「先 -f 合并后 extends」顺序）、N4（standalone 裸 run 加三必需未来守卫注释）；N3/N5 登记。

**V 真机 E2E 后置清单（环境恢复后由用户/值班代理执行，daemon 可用时逐项打勾）**：
前置：恢复定制 WSL 发行版 + rootless podman（`systemctl --user enable --now podman.socket`、`loginctl enable-linger`）；在 apps/containers 下 `pip install --no-build-isolation -e shared -e client -e jupyter-podman-rootless`。
1. [ ] **xmnn 栈**：`inv xmnn.build`（构建成功，AST PREAMBLE trap 还原无残留）→ `inv xmnn.up`（2223/8890 端口可达）→ `inv xmnn.smoke`（双 ABI/SONAME 守卫 PASS）→ `inv xmnn.down`（零残留：容器/网络/匿名卷）。
2. [ ] **quant 栈**：`inv quant.build` → `inv quant.up`（2222/8888 可达；**重点确认 bridge 行为变更后服务名解析与出网正常**）→ `inv quant.smoke`（INT8/FP16/QDQ 三守卫 PASS）→ `inv quant.down`。
3. [ ] **quant GPU 覆盖**：`inv quant.up --gpu`（真实渲染 devices=[/dev/fuse,/dev/dri]；NPU/GPU 透传视硬件）→ smoke → down。
4. [ ] **monetize 栈**：`inv monetize.build`（apt clang + apache-tvm-ffi 0.1.13）→ `inv monetize.up`（2224/8892）→ `inv monetize.smoke` → `inv monetize.build-native`（单 .so，3 处源码适配生效）→ `inv monetize.wheel`（纯 Python wheel 不含 .so）→ down。
5. [ ] **builder 端垫片**：`invoke --list` 正常（已在静态门验证，真机复跑确认环境一致）+ `python -c "from jpman_builder.tasks import client as c, utils as u; print(c.get_client.__module__, u.run_cmd.__module__)"` 应打印 `jpman_common.connection jpman_common.proc`（证明连接/工具符号确实来自共享包，垫片无断链）。
6. [ ] 任一项失败：按「修复即闭环」三阶段处理，更新本清单与对应规则文件。
成功判据：以上全部 PASS 且 `podman ps -a`/`podman network ls` 无栈残留；通过后将本段勾选结果回链至本条与规格 tasks.md T6。

### 2026-09-15 · `docs:` README.md 原子化为 docs/（00-12 文档集 + 索引 + 根入口精简）

**关联七概念场景**：场景3「重构优化」单独 A 子类（A→V→C，等价性验证强制）；用户输入「README.md 原子化为 doc」。

**A 阶段拆分方案**：对齐构建端 jupyter-podman-rootless/docs/ 先例（两位数字序号 + docs/README.md 索引 + 根 README 精简为入口）。642 行 README 的 14 章节按 topic 策略拆为 13 个原子文件：
- `docs/00-overview.md`（定位/构建端关系/jpman 分工/核心能力）
- `docs/01-getting-started.md`（安装/快速开始/镜像备份恢复）
- `docs/02-invoke-reference.md`（命令速查/布尔三态/known_hosts 维护）
- `docs/03-windows-wsl.md`（三路径/连接优先级/逃生舱/A-B 维度分离）
- `docs/04-troubleshooting-guide.md`（W-I1~W-I4 + C-I1~C-I5 速查表，源 §5.4）
- `docs/05-sdk-usage.md`（Python import）/ `docs/06-run-discipline.md`（rootless 三必需）
- `docs/07-environment-variables.md`（容器级/SDK级/透传三表）
- `docs/08-env-bootstrap.md`（env.* 自举/base-digest 防陈旧）
- `docs/09-passthrough.md`（5+1 透传开关/端口语义/宿主前置）
- `docs/10~12-*-overlay.md`（quant/xmnn/monetize 三工作负载栈）

**外部引用同步**：AGENTS.md 三处锚点（§7→docs/06、README→docs/README、5.4→docs/04）；.agents/README.md 人类文档↔AI 规则对应表 5 行锚点全覆盖；构建端 entrypoint.md C-I2 交叉引用；docs/retrospective/patterns/win32-tty-pipe-charset-strategy.md 活模式引用。

**V 等价门**：check-links（30 文件 179 内联链接 0 断链）；check-atomization-duplication（源↔13 模式文件 0 重复）；finalize-atomization.py（断链/导航/看板 PASS）；12 原子文档全部满足单一职责，04/08 因表格与流程语义完整性略超 5000 字符（6182/5467）判定不拆。

**验收点**：根 README 精简为 4 章入口（定位/快速开始/文档导航/AI 规范）；docs/README.md 索引按入门/使用参考/架构高级三组导航；全部原子文件 frontmatter 携带 source 溯源；2026-09-15 未提交的「Windows 原生自动桥接」改动（git diff 9 insertions）已完整保留至 docs/10-12。

### 2026-09-13 · `feat/refactor:` onnx-quantized 迁移至 client（Podman rootless 薄叠加 + podman-compose 声明式栈 + quant.* 命名空间）

**关联七概念场景**：场景3「重构优化」（I→F→A→V→C，Spec Mode 全流程）；用户输入「迁移 apps/docker-images/devcontainer-base/variants/onnx-quantized 到 apps/containers/client，使用 podman-compose 知识包」。四项架构歧义经用户裁决：完整迁移 / FROM rootless:latest / opt-in 独立命名空间 / 源目录保留原样。

**I 阶段洞察（迁移本质）**：源变体的可迁移内容是 ① conda main 环境五包（onnx/onnxruntime/onnx-simplifier/onnxscript/onnxconverter-common）② 3 段纯 ONNX 构建期冒烟 ③ 2 份深度量化文档；Docker 4 层继承链与 variant-framework 是载体不是能力。rootless 基底与 onnx-dev 目标环境**同构**（Ubuntu 26.04 + /opt/conda/envs/main cp314t free-threading + PATH 优先 + SSH/Jupyter/supervisord），薄叠加可行。

**F 阶段设计（知识包裁决）**：以 OKF podman-compose 束（concepts/02/03/06/08/10）为 G1 依据——三必需 1:1 映射标准字段；多文件 list **追加**合并（devices 不去重）决定 GPU 覆盖只写新增设备；compose 写标签/SDK CLI 读标签为接缝；选型「栈生命周期用 compose、单资源命令式留 SDK」，compose 层 opt-in 不回流根 run。

**A 原子交付**：
- `overlays/onnx-quantized/`：Containerfile.quantized（3 层：五包安装 / COPY 守卫与冒烟 / 构建期执行）、compose.yaml（单服务 quant、长语法 bind、三必需、org.specweave 标签）、compose.gpu.yaml（仅追加 /dev/dri，CDI 注释）、.env.example（12 键）、smoke/（_quant_guards.py + 3 逐行等价脚本）
- `src/jpman_client/tasks/quant.py`：build/up/down/ps/logs/smoke 六任务，纯子进程（禁 import podman），复用 _project_root/_load_env_overrides/to_posix_path/detect_runtime/run_cmd/check_runtime_ready；双门禁（Windows 原生 / 缺 podman-compose）
- `__init__.py` 注册 quant 命名空间；pyproject `[compose]` extra；新规则 `.agents/rules/quant-overlay.md`（C11）；AGENTS/README/.agents 索引/.env.example/CHANGELOG 同步

**V 对抗门（实测暴露并修复）**：① RELEASE 写 onnx-simplifier「v0.7.3」但 PyPI 最高发行版 0.5.0——构建实证 0.5.0 sdist 拉取 onnxsim-0.7.3 wheel（包版本≠模块版本串），按索引实证改 pin 并留注释；② buildah 对 shell-form RUN `bash -lc '<body>'` 二次分词切断内联 `python -c "…\"…\""` 嵌套引号（宿主 bash 同写法通过、构建器内失败）——守卫固化为 smoke/_quant_guards.py，RUN 不写内层双引号。

**验收点（podman machine Fedora43 / podman 5.7.1 实测）**：① 构建 exit=0，五包版本打印 + 三守卫 PASS + 构建期 3 冒烟 PASS（INT8 max_diff=0.001914 / FP16 0.000211 / QDQ 节点=10 diff=0.014510）+ devuser 访问 PASS；② 真实 podman-compose config 双文件渲染：默认含 cgroupns/label=disable//dev/fuse，叠加后 devices=[/dev/fuse,/dev/dri] 无重复；③ `inv quant.up` 后 2222 SSH banner / 8888 HTTP 302 可达；④ compose exec 路径冒烟 3/3；down 后容器与网络零残留；栈未运行时 `podman run --rm` 兜底路径 3/3；⑤ 标签接缝 `podman ps --filter label=io.podman.compose.project=onnx-quantized` 命中；⑥ 原 17 任务零回归（总数 23）；Windows 门禁/缺二进制门禁均 Exit(1) 且文案可执行；⑦ 源 variants/onnx-quantized/ 目录零改动。

### 2026-09-12 · `fix:` inv run 在 UID≠1000 的原生 Linux 必现 exit=125（B-scheme UID 动态推导 + socket 预检自愈 + C-I5）

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E，强制 V 门）；原生 Linux（宿主 uid=1006，podman 3.4.4）执行 `python -m invoke run`，CLI 拼出 `-v /run/user/1000/podman/podman.sock:...`，podman 报 `Error: statfs /run/user/1000/podman/podman.sock: no such file or directory` exit=125；随后被 C-I3 透传诊断误分类，提示用户"去掉 --wayland/--gpu 开关"（本次未启用任何透传，指引完全无关）。

**F 阶段根因（三层，逐层实测）**：
1. **UID 硬编码**：`podman_sock_path()`/`host_runtime_dir()` 默认 `PODMAN_RUNTIME_UID=1000`（WSL2 惯例），但本机 `id -u=1006`、`XDG_RUNTIME_DIR=/run/user/1006`；挂载源路径直接不存在。
2. **socket 服务未运行**：即便路径改为 1006，`podman.socket` 用户单元状态为 enabled-but-inactive，socket 文件不存在（本机 podman CLI 直连 daemon 不需要它，但 B-scheme 容器经 REST socket 复用宿主 daemon，必需）。实测 `systemctl --user start podman.socket` 后文件生成（0660）、`_ping` HTTP 200。
3. **诊断误分类**：B-scheme socket 是**必选核心挂载**，却与 wayland/gpu 等 opt-in 透传共用 C-I3 匹配（关键字仅为 statfs+ENOENT），输出无关修复动作。

**V 对抗门（4 视角）关键裁决**：① Windows 原生默认必须保留 1000（本机 UID 无意义，daemon 在 WSL2/Machine 远端），POSIX 才取运行时事实；② 自愈仅限用户级 systemd 单元（免提权、可逆、10s 超时），容器内（`HOST_PODMAN_SOCK` 已注入）、非 Linux、非 podman runtime 一律放行不动作；③ 容器内 entrypoint B-scheme 分支经核实**路径无关**（消费 HOST_PODMAN_SOCK 变量 + userns 属组映射 + devuser 读写自检），UID 1006 实测通过，无需重建镜像；④ C-I3 对 `podman.sock` 路径必须静默，SDK/CLI 两处异常分流先判 C-I5。

**修复点（C 原子交付）**：
- `utils.py`：新增 `host_runtime_uid()`（优先级：显式 `PODMAN_RUNTIME_UID` → POSIX `$XDG_RUNTIME_DIR` 末段 → `os.getuid()` → Windows 1000）作为唯一事实源，`podman_sock_path()`/`host_runtime_dir()` 改为消费它；新增 `ensure_host_podman_socket()`（缺失时自动 `systemctl --user start podman.socket`，返回 `(就绪, 明细, 是否自愈)`）与 `bsock_missing_guidance()`（C-I5 三步指引）；`passthrough_diagnose_hint()` 对 podman.sock 返回空串。
- `client_core.py`：`run_container()` 在 runtime 就绪检查后接入预检（失败 fail-fast，自愈成功打印 `[Run][B-scheme]` 日志）；`_run_via_sdk` 与 CLI except 两处先 C-I5 后 C-I3。

**预防**：规则 `invoke-tasks.md` 新增 S6 硬约束与 §6 第 5 条 B-scheme 回归门（UID 四优先级断言 + 自愈第三元为 True + C-I3 对 podman.sock 必须静默）；`.env.example` 补 `PODMAN_RUNTIME_UID` 文档；README §5.4 新增 C-I5 行。

**验收点**：① 制造 socket 缺失后 `ensure_host_podman_socket()` 返回 `(True, '', True)`；② `invoke run` 端到端 exit=0，挂载 `-v /run/user/1006/podman/podman.sock:...`；③ 容器 entrypoint 日志 `[B-scheme] [OK] devuser can read/write host podman socket`；④ 容器内 devuser 经 socket `_ping` HTTP 200、REST `GET /images/json` 列出宿主 8 个镜像；⑤ C-I3 对 podman.sock 报错返回空串、C-I5 正常输出；⑥ py_compile 与 GetDiagnostics 零告警。

**遗留观察（不在本次范围）**：宿主 podman 3.4.4 的 REST 服务仅响应 Docker 兼容端点（`/images/json` 200），`/libpod/*` 返回 404——这是宿主端 podman-py SDK 恒降级 CLI 的根因；容器内 v5 podman 经 B-scheme 调 libpod 端点可能同样受限，升级宿主 podman ≥4 可解，属环境升级决策（L2）。

### 2026-09-12 · `fix:` inv load 在 POSIX 平台必现 exit=125（CLI 喂入方式平台分流 + C-I4 诊断）

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E，强制 V 门）；Linux 原生（podman 3.4.4）执行 `python -m invoke load`，SDK 按设计降级 CLI 后，CLI 报 `Error: payload does not match any of the supported image formats (oci, oci-archive, dir, docker-archive)`，exit=125。

**F 阶段根因（两层独立故障，G1 事实门 24 条）**：
1. **跨平台命令漂移（主因）**：`_load_via_cli` 无条件拼接 `type "<tar>" | podman load`。`type` 是 Windows cmd.exe 的读文件命令；在 POSIX shell 中是"显示命令类型"内建——zsh 向 stdout 回显路径文本（实测 243B）、bash 向 stderr 报 not found，送给 podman 的根本不是 tar 字节流。该写法违反 `invoke-tasks.md §3.2` 自身契约（规定 `load -i`）。
2. **podman 3.4.x stdin 路径缺陷（次因，排除"把 type 换成 cat 即可"的想当然修复）**：实测同机同归档 `cat <tar> | podman load` 仍在 Copying 4 个 blob 后报同样错误，而 `podman load -i <tar>` 成功（`Loaded image(s)`，1.96GB 归档完好：23 层 + manifest.json docker-archive，外层 tar 遍历无错）。
3. 诊断盲区：失败兜底只输出 `[CLI] load 命令执行失败（exit=125）`，丢弃 podman 原生 stderr，排查者零信息增量。

**V 对抗门（4 视角）关键裁决**：① Windows 原生**不得**跟随改 `-i`——有 Windows→WSL2 远距 daemon 大文件 EOF 历史实测，保留 `type |` 管道；② WSL2 **内部** platform=Linux 走 `-i` 正确（EOF 问题仅限 Windows 原生 CPython）；③ 成功判定子串 "Loaded image" 同时兼容 podman 3.x（"Loaded image(s):"）与 4/5.x（"Loaded image:"）；④ 不触碰 SDK 候选链（C8 A/B 维度分离），SDK 在本机不可用（podman 3.4.4 无 active socket）属设计内降级，CLI 是 C4 承诺的保底路径。

**修复点（C 原子交付）**：
- `utils.py`：新增 `image_load_cli_command(runtime, tar_path)` 作为跨平台 load 命令唯一事实源（Windows=`type |`，POSIX=`load -i`），docstring 固化双向硬约束。
- `client_core.py::_load_via_cli`：改调 helper（消除硬编码 `type`）；新增 **C-I4** "payload does not match" 中文诊断分支（tar tf 自检 → 手动 `-i` 复核 → 升级/重存 三步指引）；最终失败消息携带 podman 原生 stderr 末行，消除诊断盲区。

**预防（为什么下次不会再出现）**：① 平台分流收敛到单一 helper，规则 `invoke-tasks.md §3.2 调用链表 / §3.3 load 专项契约（6 条）/ §5-S5 / §6 第 4 条平台分流回归门` 同步为强制契约并记录"严禁 POSIX 用 type/cat 管道"的实测依据，review 时可直接对照；② 同类错误（归档/喂入/版本三因素同表象）已有 C-I4 自动翻译，不再退回裸 exit=125。

**闭环**：README §5.4 速查表新增 C-I4 行（标题更新为 C-I1~C-I4）；AGENTS.md 变更日志追加摘要。

**验收点**：① `python -m invoke load` 在 Linux + podman 3.4.4 端到端成功（`Loaded image(s): localhost/jupyter-podman-client:latest`）；② `invoke images` CLI 降级表格正常；③ `python -m py_compile` 零告警；④ Windows 路径命令字符串保持 `type ... | podman.exe load` 不变（静态核对）。

### 2026-09-11 · `fix:` inv load 支持 .tar 未压缩产物（save 降级契约同步）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）；`inv load` 报「缓存目录中未找到 tar.gz」，但上轮 `invoke save` 在 Windows 原生（无 gzip）已降级产出 `.tar`——**save 三档降级新增但 load 搜索未同步**，构成 save/load 扩展名契约断裂。

**F 阶段根因**：`find_latest_image_tar()` 仅 glob `*.tar.gz`（构建端 jpman save 时代的单一产物形态）；save 增加 `.tar` 降级后搜索模式未随之扩展 → 缓存中存在有效备份但 load 找不到。

**修复点**：`utils.py::find_latest_image_tar` 改为双扩展名 `("*.tar.gz", "*.tar")` 搜索（跳过 symlink 逻辑保留）；`_load_via_cli` 的 `type <file> | podman load` 管道天然兼容未压缩 tar，无需改动。

**预防**：save 新增产物形态时必须同步 load 搜索契约（save/load 扩展名白名单一致）；README §4.1 已声明双扩展名产物。

**验收点**：① `inv load` 在仅含 `.tar` 缓存时成功加载（实测 `Loaded image: localhost/jupyter-podman-client:latest`）；② py_compile 零告警；③ 双扩展名产物并存时按 mtime 取最新。

> **2026-09-12 更正**：本条「`type <file> | podman load` 管道天然兼容未压缩 tar，无需改动」的判断仅在 Windows 原生成立，在 POSIX 被证伪（`type` 非读文件命令 + podman 3.4.x stdin 缺陷），详见 2026-09-12 C-I4 条目。

### 2026-09-11 · `feat:` 新增 invoke save 导出镜像到缓存（备份/恢复闭环）

**关联七概念场景**：场景3「重构优化」（F→A→V→C）；client 已有 load/run/stop/status/clean 但缺 save（只消费不产出），镜像备份需绕道构建端 jpman。

**F 阶段设计（对齐构建端 `bin/jpman cmd_save` 规范）**：
- 产物命名 `<镜像名>-<short_id>-<YYYYMMDD-HHMMSS>.tar.gz`；无 gzip/pigz 时降级 `.tar` 未压缩（Windows 原生 cmd/PowerShell 无 gzip 命令，`| gzip` 管道 exit 255）
- 写 `manifest.txt` 段（IMAGE_FILE/SIZE/SHA256/SAVED），与 `validate_manifest_integrity` 解析格式互操作
- `gzip -t` 完整性校验 + SHA256 摘要 + `*-latest` 软链接

**修复点**（A 阶段原子拆分）：
- `client_core.py`：`save_image()` + `_save_via_cli()`（pigz>gzip>未压缩三档降级）+ `_image_exists_fast()` + `_check_gzip_integrity()` + `_append_manifest()`
- `manage.py`：`save` 任务（`--tag`/`--cache-dir`，默认 .env IMAGE_TAG）
- `__init__.py`：根命名空间与 `container.*` 别名注册（7 命令）
- README §4 命令表 + §4.1 备份/恢复小节

**V 对抗审查发现的陷阱（均已修复）**：① digest 形如 `sha256:xxx` 含冒号 → 进入文件名/命令在 Windows shell 破坏 → 去前缀取前 12 位；② `Path.with_suffix` 在 `.tar.gz` 上产生 `.tar.tar` 双后缀 → 统一由 save_image 决定扩展名；③ `run_cmd` 文本捕获会损坏二进制 → 压缩走 shell 管道落文件、未压缩走 `podman save -o` 直接落盘。

**验收点**：① `invoke --list` 出现 `save` 与 `container.save`；② `invoke save` 成功落盘 1872MB tar + manifest + SHA256；③ 无 gzip 环境降级 `.tar` 成功；④ 与 `invoke load`/`bin/jpman load` 格式互兼容。

### 2026-09-11 · `feat:` run 新增 --rebuild-layer 自动重建叠加层（基底陈旧一键恢复）

**关联七概念场景**：场景4「知识沉淀」（R→I→E→V→C）+ 场景3「重构优化」混合；上一轮修复了「叠加层基底陈旧」警告的根因（重建镜像消除），本次沉淀机制文档并落地 B 档预防方案。

**F 阶段机制：基底先固定后更新**——镜像 tag 是移动指针，叠加层固化的是 digest（不可变指纹）：`env.build-layer` 构建时经 `--build-arg BASE_DIGEST` 把基底 digest 烤进 LABEL；run 前 `_warn_if_layer_stale` 比对 LABEL 固化值 vs 基底当前值，不一致即中文警告。只警告不阻断（旧基底可能是有意选择）。

**修复点**（B 档半自动）：
- `env_in_container.py`：把 `build_layer` 核心逻辑提取为 `rebuild_client_layer()`（返回 bool，不吞异常）；`build_layer` 任务改为其薄包装（失败仍 Exit）
- `manage.py::_warn_if_layer_stale`：返回值从 None 改为 bool（True=陈旧/无指纹），供调用方决策
- `manage.py::run`：新增 `--rebuild-layer` 标志——检测到陈旧时自动重建叠加层，**重建失败回退旧基底启动**（不因构建失败阻断容器）
- README §10.5：新增「叠加层基底指纹防陈旧机制」文档（三环节闭环 + 一键恢复命令 + JPUMAN_SKIP_BASE_CHECK 静默）
- rules/invoke-tasks.md：run 参数契约表补 `--rebuild-layer`

**V 对抗审查要点**：拒绝 C 档（构建端 post-build 自动重链叠加层）——破坏构建端/消费端解耦、引入构建风暴；B 档保留「检测不阻断、修复可执行」哲学；`run_cmd warn=True` 使重建失败返回 Result 可判，确保回退分支可达。

**验收点**：① `invoke run --help` 出现 `--rebuild-layer`；② `_warn_if_layer_stale` 5 分支单测全过（SKIP=1/陈旧/非叠加/无指纹/新鲜）；③ py_compile 两文件零告警；④ README §10.5 与 rules 参数表同步。

### 2026-09-11 · `fix:` SDK 在 Windows 原生结构性不可用诊断为 W-I4 + P2 显式 Machine SSH URI

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E）；`inv run`/`inv images` 在 Windows 11 原生 CPython（py314t）持续打印「SDK路径不可用（首候选=P1-wsl-9p AttributeError）」且降级原因不明。

**F 阶段根因链（5-Why）**：
1. 现象：首候选 P1-wsl-9p AttributeError → 但实际 `os` 无 `getuid`（`AttributeError: module 'os' has no attribute 'getuid'`）
2. 为什么 from_env 被调用？→ P1/P2 候选 `base_url=None` 时 `get_client` 走 `_podman_sdk.from_env()`
3. 为什么 from_env 崩？→ podman-py `podman/api/path_utils.py::get_runtime_dir()` L20 调 `os.getuid()`（POSIX 专属，Windows 无此属性）
4. 为什么即使显式 ssh:// 仍崩？→ podman-py `podman/api/uds.py::UDSSocket.__init__` L34 调 `socket.socket(socket.AF_UNIX, ...)`（py314t 实测无 `AF_UNIX`）——Windows 原生下 unix/ssh 适配**皆不可用**（结构性，非配置问题）
5. 为什么 P2-machine 也没救？→ 原实现 base_url=None → from_env，撞同一 AttributeError；日志仅笼统显示「首候选=P1-wsl-9p AttributeError」未归因

**修复点**（C 阶段原子拆分）：
- `utils.py`：新增 `machine_connection_uri()`（`podman system connection list --format json` → Default=true 连接 URI，lru_cache）；`sdk_base_url_candidates` 的 P2-machine 候选在 Windows 原生改用显式 ssh://（实测返回 `ssh://user@127.0.0.1:63851/run/user/1000/podman/podman.sock`），规避 from_env 崩溃
- `utils.py::windows_diagnose_hint`：新增 **W-I4** 分支（`AttributeError` + `getuid`/`AF_UNIX`）——明确「结构性不可用、与配置无关、已自动降级 CLI fallback」
- `.env` / `.env.example`：`WSL_DISTRO_NAME=Ubuntu` → `podman-machine-default`（本机 `wsl.exe --list --quiet` 实测发行版名；原值不存在导致 P1 探测失败前置误导）
- README §5.4 / rules/windows-wsl.md §5：W-I1~W-I3 → W-I1~W-I4（三处同步）

**V 对抗审查要点**：改 vendor/podman-py（third_party 只读子模块）被否——即使修复 `os.getuid()`，`AF_UNIX` 依旧缺失，SDK 在任何 scheme 下都不可用，治标不治本；正确闭环是「识别 + 显式提示 + 自动 CLI fallback」。

**验收点**：① `inv images` 在 py314t 正常输出镜像表（降级一行提示，非错误）；② `PODMAN_CLIENT_LOG_LEVEL=DEBUG inv images` 打印 W-I4 全量根因与 30 秒修复；③ `machine_connection_uri()` 返回非空 ssh://；④ README §5.4 / windows-wsl.md §5 / utils.py 三处 W-I4 描述一致；⑤ `py_compile` 两文件零告警。

### 2026-09-11 · `feat:` 新增 --video 透传（UVC 摄像头字符设备）

**关联七概念场景**：场景3「重构优化」（I→F→A→C）；USB 透传仅总线级（容器内 lsusb 可见但无 /dev/video*），摄像头采集（v4l2/OpenCV）需字符设备。

**I 阶段根因**：`--usb` 透传 `/dev/bus/usb`（总线级），UVC 摄像头需 `/dev/video<n>` 字符设备。

**修复点**（A 阶段原子拆分）：
- `utils.py`：`passthrough_paths()` 增 `video_devices`（`VIDEO_DEVICES` env，逗号分隔，默认 `/dev/video0-3`）；`build_passthrough_spec` 增 video 分支（每设备 `--device <d>:<d>` 同名映射）；`ContainerConfig` 增 `video=False`
- `manage.py`：run 增 `--video/--no-video` 三态 + `.env` 键 `PASSTHROUGH_VIDEO` + help
- `client_core.py`：透传摘要打印补 video
- 文档：`.env`/`.env.example` 增 PASSTHROUGH_VIDEO 与 VIDEO_DEVICES 说明；README §11 表格补 ⑥ 行 + §11.3 增 Video 段落（回写原"已知边界"为已支持）

**验收点**：① `inv run --help` 出现 `--video/--no-video`；② 重启后 run 命令含 `--device /dev/video0-3` 四项；③ 容器内 `/dev/video0-3` 字符设备存在，`head -c1` 打开成功（EINVAL 为非协商格式预期行为）；④ 容器内 `fcntl.ioctl(QUERYCAP)` 返回 `driver=uvcvideo card=Integrated RGB Camera`（uvcvideo 驱动探活成功）；⑤ 透传摘要显示 `video`。

### 2026-09-11 · `docs:` 透传部署文档固化（WSLg Wayland / CDI GPU / usbipd USB 前置）

**关联七概念场景**：场景4「知识沉淀」（R→I→E）；三项透传（Wayland/GPU/USB）在 NVIDIA WSL2 podman machine 实测跑通后，把宿主侧前置固化为文档，避免操作者凭记忆重试。

**沉淀内容**：
- README 新增 §11.3「三大透传的宿主侧前置」：WSLg Wayland（`HOST_XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir` 关键路径）、NVIDIA GPU（CDI `nvidia-ctk cdi generate` + `GPU_DEVICE=nvidia.com/gpu=all`）、USB（usbipd-win bind/attach + VM 内确认/排障）
- `.env.example` 同步：WSLg Wayland 注释、GPU 双形态、USB 前提步骤

**验收点**：文档命令与实测路径一致（`/mnt/wslg/runtime-dir/wayland-0`、`/etc/cdi/nvidia.yaml`、`usbipd attach --wsl podman-machine-default`）；container 内验证命令可用（printenv/nvidia-smi/lsusb）。

### 2026-09-11 · `feat:` GPU 透传支持 CDI 设备引用（NVIDIA）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）；`inv run --gpu` 在 NVIDIA WSL2 podman machine 上失败 `stat /dev/dri: no such file or directory`（VM 无 `/dev/dri`，GPU 走 `/dev/dxg` DXCore）。

**I 阶段根因**：client 侧 GPU 透传固定拼 `GPU_DEVICE:/dev/dri`（设备节点路径）。NVIDIA WSL2 下不存在 `/dev/dri`，需走 **CDI**（`nvidia-ctk cdi generate` → `/etc/cdi/nvidia.yaml` → `--device nvidia.com/gpu=all`，自动挂载 `/dev/dxg` + `/usr/lib/wsl/lib/libcuda*`）。

**修复点**：`utils.py::build_passthrough_spec` GPU 分支按形态分派——`GPU_DEVICE` 以 `/` 开头（设备路径，默认 `/dev/dri`）→ 映射容器内 `/dev/dri`；否则视为 CDI 引用（如 `nvidia.com/gpu=all`）→ 原样透传。

**验收点**：① `GPU_DEVICE=nvidia.com/gpu=all inv run --gpu` 启动成功（`--device nvidia.com/gpu=all` 出现在 run 命令）；② 容器内 `nvidia-smi` 输出 `NVIDIA-SMI 580.102.01 / Driver 581.57 / CUDA 13.0`；③ 端口映射模式 jupyter/sshd RUNNING、HTTP 200；④ `/dev/dri` 路径形态分支保持兼容（startswith("/") 判据）。

### 2026-09-11 · `chore:` 基底联动重建（devuser UID 固定 1000 + B-scheme socket 修复 + :toolbx 变体）

**关联七概念场景**：场景2 后置联动（构建端 spec：`.trae/specs/infra-env/toolbx-host-image/`）。

构建端当日交付三项变更（devuser 固定 UID 1000、entrypoint socket 属主穿透修复、`:toolbx` 变体），client 侧经**基底指纹机制**（同日早些时候上线）自然驱动联动：`inv env.build-layer` 重建叠加层，烤入新基底 digest `sha256:2826166e…`（与 rootless:latest 逐字符一致）；`inv stop && inv run` 重启 jupyter-podman（沿用既有 JUPYTER_TOKEN/USER_PASSWORD，浏览器/SSH 零感知）。

**本侧代码改动**：仅文档/注释——`README.md` §10.4「默认用户」改为"固定 UID/GID 1000"；`Containerfile.client` V 阶段注释中"UID 自动分配（如 1001）"改写。无任务代码改动（指纹检测首次实战即正确触发，无陈旧误报/漏报）。

**验收点**：容器内 `id -u devuser`=1000；supervisorctl jupyter/sshd RUNNING；Jupyter HTTP 200；容器内 `toolbox create` 仍为 wrapper 中文指引；`invoke run` 无陈旧告警；base-digest label == 基底 Digest（DIGEST_MATCH）。

### 2026-09-11 · `fix:` 叠加层基底指纹与陈旧检测（toolbox wrapper 缺席事故闭环）

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E 链路）；用户在 client 容器（8eddb24390eb）内执行 `toolbox create` 仍裸报 `Error: TOOLBOX_PATH not set`，而构建端前一日已交付 wrapper 优雅降级。

**F 阶段根因（5-Why 终局）**：client 叠加镜像在构建时刻固化基底（`FROM localhost/jupyter-podman-rootless:latest`）；rootless 基底重建（含 toolbox-wrapper.sh 与 flatpak-spawn 补装）后 tag 移动**不传导**给已存在的 overlay——当日 client:latest（CST 11:29 构建）比新基底（CST 16:22）早 5 小时，容器内 `/usr/local/bin/toolbox` 仍是 11.2 MB 裸 ELF、`/usr/local/libexec/toolbox` 不存在。系统性根因：base→overlay 镜像谱系无基底指纹，「重建基底后必须重建叠加层」只存在于操作者脑中，`run` 只验镜像「存在」不验「新鲜」。

**上游事实（vendor/toolbox/src/cmd/root.go:160-173）**：容器内（`/run/.containerenv` 存在）`TOOLBOX_PATH` 为空即硬错误；该变量由宿主 Toolbx 启动器注入，用于把宿主二进制挂入新容器并经 `flatpak-spawn --host` 回调宿主。**普通 podman 会话内 `toolbox create` 架构上不可用**，wrapper 退出码 1 + 中文指引是正确行为而非失败。

**修复点**：基于新 rootless:latest 重建 client 叠加层并 stop/run 替换容器（保留原 JUPYTER_TOKEN/USER_PASSWORD，浏览器访问与 SSH 凭据不变）；验证 `toolbox --version` 透传输出 `toolbox version 0.3`、`toolbox create` 输出中文指引。

**预防（C10 闭环）**：

1. `Containerfile.client` 末尾新增薄层 `LABEL org.specweave.base-image/base-digest`（置于末尾不使前置 COPY/RUN 缓存失效）
2. `env_in_container.py::build_layer` 构建前自动采集基底 digest 经 `--build-arg BASE_DIGEST` 烤入标签
3. `client_core.py` 新增 `image_inspect_info()`（走原始 JSON 而非 --format 模板，规避 Windows cmd / Linux bash 双 shell 引号与 `$` 展开差异）
4. `manage.py::run` 启动前新增 `_warn_if_layer_stale()`：仅对 `org.specweave.component=jupyter-podman-client` 镜像比对烤入 digest 与基底当前 digest，陈旧/无指纹时中文告警并给出 `invoke env.build-layer && invoke stop && invoke run` 完整命令，**只警告不阻断**；`JPUMAN_SKIP_BASE_CHECK=1` 逃生（`.env.example` 已登记）；`load` 成功后同步一次性提示
5. 任何 inspect 异常静默降级，不影响 run 主流程

**验收点**：① 新镜像 label 中 base-digest 与 rootless 当前 digest 逐字符一致；② 四分支实测：指纹一致静默 / monkeypatch 陈旧正确告警 / skip 静默 / 非 client 镜像静默；③ 重建容器内 wrapper + flatpak-spawn 齐备；④ `py_compile` 三文件全过。

### 2026-09-10 · `fix:` 布尔参数三态化 + `run` 任务关闭自动短选项（含对上一提交声明的更正）

**关联七概念场景**：场景2「问题解决」（I→F→V→C 链路）；I 阶段读 invoke 3.0.3 源码定位根因，F 阶段确立可行解，V 阶段以「单元级 6 场景 + CLI 实跑」逐条证伪

**I 阶段根因（源码 + 实测）**：

1. `invoke/tasks.py:223-231`：`Argument.kind` **仅由 `type(default)` 推断** → 默认写 `None` 会让 kind 退化为 `str`，旗标变成「需取值」而非开关 → **三态哨兵不可行**
2. `invoke/parser/argument.py:127`：`value` 在未赋值时回落 `default` → **「未指定」与「显式 False」不可区分**
3. `invoke/parser/context.py:150`：反向旗标 `--no-<flag>` **仅在 `default is True`** 时自动生成
4. `invoke/tasks.py:215-220`：短名生成 = 「逐字符取首个未被占用字符」，**与参数顺序耦合** → 实测 `-h` 被 `ssh_public_key` 抢走（`invoke run -h` 报 `needed value`）、`host_network` 退化到短名 `-`、`--gpu` 无可用字符

**更正声明**：上一提交（同步运行时透传）中「修复 `GRANT_SUDO=no` 因 `bool("no")` 判真而失效」**实际未生效**——`_env_bool()` 只修正了文本解析，但 `grant_sudo` 的 invoke 默认值为 `True`，未指定时 `Argument.value` 直接回落 `True`，`.env` 根本不被读取。本次才真正闭环。

**验收点**（原子提交单一职责，可独立验证）：

A. **三态解析**：新增 `manage.py::_resolve_bool(on_val, off_val, env, env_key, default, flag)`；每个布尔项配对 `--x` / `--no-x`（`grant-sudo` 的 CLI 面保持 `--grant-sudo` / `--no-grant-sudo` 不变）；同开同关报「参数冲突」
B. **短选项契约**：`run` 任务 `@task(..., auto_shortflags=False)` → `invoke run -h` 恢复输出帮助，自动短名全部取消，长选项成为唯一公开契约
C. **规则固化**：`.agents/rules/invoke-tasks.md` 新增「布尔项三态规则」与「短选项规则」两条**违反打回**约束

**验证证据**：

- 单元级 6 场景全对：未指定取 `.env`（`grant_sudo=False` / `gpu=True`）、`--gpu` 开、**`--no-gpu` 覆盖 `.env` 的 yes**、`--grant-sudo` 覆盖 `.env` 的 no、`--no-grant-sudo` 关、`--gpu --no-gpu` 被拦截
- CLI 实测：`invoke run -h` 输出 Usage（不再报错）；`^\s{2}-[a-z],` 无匹配 = 自动短名已全部消除；`--no-{dbus,gpu,grant-sudo,host-network,usb,wayland}` 六个配对旗标均已注册

### 2026-09-10 · `feat:` 同步构建端运行时透传（5 个开关 + C-I3 诊断）

**关联七概念场景**：场景5「创新突破」（F→V→I→C 链路）；F 阶段确认执行模型不同（构建端 compose 分层覆盖 → 消费端 SDK/CLI 编程式），V 阶段对抗审查产出下述关键约束

**F 阶段公理（V 已逐条验证）**：

1. 透传均为运行期参数 → 只能落在 SDK kwargs / CLI 参数，无法进镜像
2. **挂载源与设备节点由 daemon 宿主（WSL2 / Podman Machine）解析** → 客户端本机 `Path.exists()` 必然为假，**禁止本机预检**（否则误判拒绝正确请求）
3. podman 对缺失源**硬失败**（退出码 125、不自动创建）→ 只能事后把原生报错翻译为 C-I3 指引
4. `--network host` 与端口发布互斥 → 不传 `-p`；rootless 无法绑特权 22 → 自动设 `SSHD_PORT=--ssh-port`
5. 既有 P0 不可破坏：C3 rootless 三必需保留、C8 A/B 维度分离、S1~S5

**验收点**（原子提交单一职责，可独立验证）：

A. **参数构造层（新增单一事实源）**
   - `utils.py`：新增 `PassthroughSpec` + `build_passthrough_spec(cfg)` + `passthrough_paths()`（路径变量与构建端 `compose.passthrough*.yaml` 同名）+ `CONTAINER_RUNTIME_DIR`
   - `ContainerConfig` 新增 5 个布尔字段（默认全关 = 默认隔离）

B. **两条路径等价消费**：`client_core.py::_sdk_run_kwargs`（`network_mode` / `volumes` / `devices` 追加）与 `_run_via_cli`（`--network host` / `-v` / `--device`）均由同一份 spec 驱动，禁止各自拼接

C. **C-I3 诊断**：`utils.py::passthrough_diagnose_hint()` 匹配 `statfs` / `stat ... no such file or directory`，给出缺失路径 + 可覆盖变量 + daemon 侧自检命令；在 `_run_via_sdk` 与 `run_container`（CLI 异常捕获）两处挂载

D. **CLI 面**：`manage.py::run` 新增 `--host-network` / `--wayland` / `--gpu` / `--usb` / `--dbus`；新增 `_env_bool()` 修复 `bool("no")` 判真导致 `GRANT_SUDO=no` 失效的既有缺陷

E. **文档同步**：`README.md` §4 / §5.4 / §8.3 / §11、`.agents/rules/invoke-tasks.md`（§3.2 统一 spec 约束 + §4.4 命令面）、`.agents/rules/windows-wsl.md` §5（C-I3 行）

**验证证据**：单元级 5 组组合参数全部正确（默认组与旧版本零差异）；实跑 `--dbus` 容器内落到 `srw-rw-rw- /tmp/runtime-user/bus` 且两个环境变量就位；实跑 `--gpu` 触发 `Error: stat /dev/dri`（退出码 125）并打印 C-I3 指引

### 2026-09-10 · `fix:` 容器内 Podman socket EACCES（C-I2）根因修复与诊断闭环

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E 链路）；F 根因分析后经**强制 V 对抗审查**（采纳 5 条意见：自验证 / `%G` 空回退 `%g` / 代价与红线声明 / `stat` 失败必 warn / C-I2 分支先于平台守卫）

**验收点**（原子提交单一职责，可独立验证）：

A. **消费端代码改动（SDK 侧诊断能力）**
   - `src/jpman_client/tasks/utils.py`：`podman_sock_path()` 默认 `PODMAN_RUNTIME_UID=1000` 且支持环境变量覆盖（**严禁硬编码容器内 UID**）；`windows_diagnose_hint()` 新增 **C-I2 匹配**（`permission denied` 且 socket 路径存在 → 属组修复引导），与 C-I1（`ENOENT`，socket/目录不存在）语义分离
   - `src/jpman_client/tasks/client_core.py`：异常汇总表叠加 C-I2 诊断文案，`get_client()` 失败路径不回归

B. **消费端文档对齐（三处同步）**
   - `README.md` §5.4：新增 **C-I2**「socket 存在但无权限（EACCES）」条目，与 W-I1/W-I2/W-I3/C-I1 并列（共 5 条口径）
   - `.agents/rules/windows-wsl.md` §5：C-I2 速查表（30 秒修复须为一行命令）
   - `AGENTS.md` + `.agents/README.md`：坑位索引与双向锚点同步

C. **联动修复（构建端 `jupyter-podman-rootless`，跨端引用登记以保证可追溯）**
   - `entrypoint.sh`：B-scheme 分支新增 **socket 属组自适应**——`stat` 宿主 socket 取属组名 → `usermod -aG` 加入非 root 用户 → 复验可读写；`stat` 失败必 `log_warn`（不静默）；UID 动态推导，不硬编码 1000/1001
   - `config/supervisor/conf.d/jupyter.conf`：移除硬编码 UID 1001 漂移，改 `%(ENV_CONTAINER_HOST)s` / `%(ENV_XDG_RUNTIME_DIR)s` 继承 entrypoint 动态导出值
   - `.agents/rules/entrypoint.md`：规则同步

D. **验收证据（verify 全部通过）**
   - `bash -n entrypoint.sh` ✅
   - base 镜像重建 → `701c2e509fd8`（`socket group` 关键字命中 5，旧镜像基线 0）✅
   - client 层重建 → `5ed156783148`（`User=root`；`jpman_client` editable 安装 OK）✅
   - 容器重建 → `41d46c351352` ✅
   - entrypoint 日志：`[B-scheme] Added devuser to socket group 'root' (gid 0)` + `[B-scheme] [OK] devuser can read/write host podman socket` ✅
   - 容器内 `/proc/<jupyter>/status`：`Groups: 0 27 997 1001`（gid 0 已注入）✅
   - `PodmanClient.from_env()` 成功：`podman 5.7.1`、3 容器、**无 PermissionError** ✅
   - devuser 侧 `podman images`（11 镜像）/ `podman info`（`rootless=true`、`RemoteSocket=unix:///run/user/1000/podman/podman.sock`）在显式 `CONTAINER_HOST` 下成功 ✅
   - 反证：无 `CONTAINER_HOST` 时触发 `newuidmap: write to uid_map failed`（WSL 三层 userns 限制），证明 `su -` 登录 shell 丢环境变量是历史误判来源、非 C-I2 修复失败 ✅

**根仓库 git commit**：`[52084da68](#)`

### 2026-09-09 · `fix:` 宿主 socket 直通连通 + 镜像缓存完整性 + known_hosts 维护

**关联七概念场景**：场景2「问题解决」

**验收点**：

A. **宿主 socket 直通（B-scheme）端到端连通**：容器内 devuser 经 userns 映射后可读写宿主直通 socket，`podman images` / `from_env()` 均成功
B. **镜像缓存完整性**：`validation_manifest_integrity` 修正首块误匹配，`inv load` 在缓存损坏时给出明确错误而非静默失败
C. **SSH host key 维护**：`ensure_known_hosts` 修复 Windows 路径失效；`refresh_host_keys` 改为 TCP 探测等待 sshd 就绪，并兼容 OpenSSH 10 KEX 与 host 段规范化

**根仓库 git commit**：（见对应 `fix(containers)` 系列提交）

### 2026-09-08 · `feat:` 默认镜像泛化为 client 管理枢纽 + 容器内 SDK socket ENOENT（C-I1）修复

**关联七概念场景**：场景2「问题解决」（容器内 C-I1）+ 场景3「重构优化」（镜像泛化）

**验收点**：

A. **镜像泛化与瘦身**：默认目标镜像由构建端镜像改为 `localhost/jupyter-podman-client:latest` 通用管理枢纽；叠加镜像体积 2.82 GB → 1.80 GB
B. **非 root entrypoint 修复**：修复 client 镜像以非 root 运行 `entrypoint.sh` 致 `chpasswd` 失败、容器以 `Exited (1)` 退出的问题
C. **容器内 SDK socket ENOENT（C-I1）修复**：bootstrap 路径（`env.run-cmd` / `env.shell`）由 `env_in_container.py::PODMAN_SERVICE_BOOT` 自举 `podman system service --time=0` 并预建 `${XDG_RUNTIME_DIR}/libpod/tmp`；常驻容器由 `entrypoint.sh::setup_podman()` 保证

**根仓库 git commit**：（见对应 `feat/fix(containers)` 系列提交）

### 2026-09-07 · `feat:` Windows 11 WSL2 SDK 全链路支持 + AI 自治规范容器初始化

**关联七概念场景**：场景3「重构优化」（I→F→A→C 链路）+ 场景4「知识沉淀」（从 podman-py OKF v0.2 bundles 萃取跨平台模式）

**验收点**（原子提交 C4 单一职责，可独立验证）：

A. **src/jpman_client/tasks/ 层代码改动（podman-py SDK Windows 兼容）**
   - `utils.py`：新增 SDK 逃生舱常量、`sdk_strategy_from_env()` 归一化、`_has_wsl_host_support()` 双门卫、`wsl_distro_name()` 3 级回退 UTF-16 LE 解析、`_wsl_user_uid()` 探测缓存、`BaseUrlCandidate` 数据类、`sdk_base_url_candidates()` P0→P3 序列生成、`windows_diagnose_hint()` W-I1~W-I3 速查匹配
   - `client_core.py`：重写 `get_client()` 上下文管理器接入多候选 ping 循环、失败汇总表、诊断文案叠加；CLI fallback 行为零回归（全部失败仍 `yield None`）
   - `manage.py`：`_load_env_overrides()` 修复核心 Bug——新增 `load_dotenv(override=False, encoding="utf-8")` 把 .env 同步到 os.environ，保证 SDK 级逃生舱读到 .env 变量；import 清理未使用的常量
   - `tasks/` → `src/jpman_client/tasks/` 布局迁移（消除与构建端 `jpman_builder.tasks` 的命名冲突），根 `tasks.py` 降级为纯转发层，新增 `env_in_container.py`（`env.*` 自举命名空间）
   - 静态验证：`python -m py_compile src/jpman_client/tasks/*.py` exit_code=0；VS Code `GetDiagnostics` 五文件零告警

B. **人类文档层改动（README.md + .env.example）**
   - `README.md` 新增 §5「Windows 11 × WSL2 支持」：§5.1 三路径矩阵、§5.2 四级连接优先级、§5.3 四策略逃生舱、§5.4 W-I1~W-I3 速查表、§5.5 A/B 维度分离表；原 §5→§6 / §6→§7 / §7→§8 / §8→§9 编号顺延
   - `README.md` §8「.env 配置完整清单」拆 8.1 容器级（9 项） + 8.2 SDK 级（4 项）两张表，明确优先级链：命令行 > shell export > .env > 默认
   - `.env.example` 追加 Windows WSL 专属 4 个 SDK 级变量：`PODMAN_CLIENT_SDK_STRATEGY`（含四策略注释）/ `WSL_DISTRO_NAME` / `CONTAINER_HOST` / `DOCKER_HOST`（兜底注释）
   - 双向锚点：README§5.4 ⇄ `utils.py::windows_diagnose_hint` ⇄ `.agents/rules/windows-wsl.md §5` 三处 W-I1~W-I3 条目 1:1 对应

C. **AI 协作者自治规范容器初始化（AGENTS.md + .agents/）**
   - `AGENTS.md`：消费端专属启动协议（嵌套路由 + 文档边界 + 内容敏感度预检）；项目概述；嵌套路由关系树；上下文路由表（10+ 条目）；10 条 P0 硬约束 C1~C10 违反打回清单；快速开始最小验证路径；父级引用声明；变更日志倒排
   - `.agents/README.md`：AI 资产容器索引；6 目录结构 + 3 规则文件；源代码真源表；人类文档↔AI 规则双向对应表；父级继承 7 层；新增规则 4 步流程；变更日志倒排
   - `.agents/rules/invoke-tasks.md`：消费端 invoke 开发规范；模块职责边界 5×5 禁止跨层表；两层后端架构 8 条不可变行为契约；CLI fallback 7 函数等价实现表；三命名空间（根 + `container.*` 别名 + `env.*` 自举）；6 条 P0 安全约束；3 条修改后必跑冒烟
   - `.agents/rules/sdk-connection.md`：6 合法 scheme 白名单 + npipe 严禁；Windows base_url 必显式约束；四策略逃生舱矩阵；多候选优先级序列（strategy × platform）；P1 WSL9P 生成契约（distro 3 级/UID 探测）；P3 tcp 兜底；8 条错误输出格式不可变；ImportError 降级安全
   - `.agents/rules/windows-wsl.md`：A/B 两维度分离表（核心差异）；两种用户画像；WSL 发行版名 3 级回退；UTF-16 LE 编码硬规定；_has_wsl_host_support 双门卫；UID 严禁硬编码 1000；W-I1~W-I3 三处同步对齐；.env 加载语义 override=False 红线；4 条必跑验证脚本
   - `.agents/{CHANGELOG.md,README.md,rules/*}` 其余子目录（roles/skills/scripts/workflows/templates/docs）预留 .gitkeep 占位（父级回退路径）

D. **治理承诺（七概念 G1~G4 质量门）**
   - G1（事实无因果）：所有 podman-py 行为陈述均有 OKF v0.2 bundles 原文锚定，无"应该/可能"类推断
   - G2（洞察四元组）：上一轮 WSL SDK 改造的根因分析四元组见 AGENTS.md 项目约束速览 C1~C10 后附的根因段
   - G3（模式可迁移）：从 bundles 萃取 2 个模式已落地——「Windows Podman 连接多候选自动降级」+「WSL2 发行版名 3 级回退」
   - G4（行动项原子化）：本次变更拆 A/B/C 三大原子块，可单独 revert 任意一块不影响其他块

**根仓库 git commit**：`[91c29c240](#)`
