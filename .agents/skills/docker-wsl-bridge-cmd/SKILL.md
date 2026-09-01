---
name: docker-wsl-bridge-cmd
version: 1.0.0
description: "当用户提到'镜像转WSL'、'docker镜像导入WSL'、'把镜像变成WSL发行版'、'wsl --import镜像'、'docker save转wsl'、'镜像转rootfs'、'podman export转wsl'、'镜像恢复为WSL环境'、'docker-wsl-bridge'、'没有Docker Desktop怎么启动镜像'、'WSL重置后恢复开发环境'、'镜像tar.gz转成WSL'时，必须使用此技能。通过Podman运行时桥接将docker save格式的镜像tar.gz转换为可通过wsl -d直接启动的WSL2发行版，完整覆盖：Podman安装→镜像加载→rootfs导出→WSL导入→默认用户配置→环境验证的全流程。不要手动拼接wsl/podman命令——本Skill封装了rootful模式、路径转换、wsl.conf配置、非交互shell初始化、验证清单等最佳实践。"
argument-hint: "<convert|setup-workspace|verify|cleanup> <镜像名> [选项]"
user-invocable: true
paths:
  - ".agents/skills/docker-wsl-bridge-cmd/**"
  - ".agents/scripts/docker-save-to-wsl-rootfs.py"
title: "Docker镜像→WSL2发行版桥接转换 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/docker-wsl-bridge-cmd/SKILL.toml"
---
# Docker镜像→WSL2发行版桥接转换 Skill

> ⚠️ **本Skill是跨Shell编排门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<400行，触发词+决策树+核心步骤+安全清单）
> - L2：操作指南 [docker-cache-wsl-migration-guide.md](../../../docs/knowledge/operations/docker-cache-wsl-migration-guide.md) + 模式库 [oci-image-wsl-rootfs-bridge.md](../../../docs/retrospective/patterns/code-patterns/oci-image-wsl-rootfs-bridge.md) + Python备用脚本 [docker-save-to-wsl-rootfs.py](../../scripts/docker-save-to-wsl-rootfs.py)

## 1. Skill ID
`docker-wsl-bridge-cmd`

## 2. 功能描述

将 `docker save` 格式的镜像tar.gz转换为可通过 `wsl -d <distro>` 直接启动的WSL2发行版。

| 命令 | 推荐场景 | 优势 |
|------|---------|------|
| **convert** | ⭐ 核心：镜像tar.gz→WSL发行版一键完成 | 自动处理Podman安装、路径映射、用户探测、wsl.conf配置 |
| **setup-workspace** | 准备转换工作区（安装Ubuntu+Podman） | 幂等检查，已安装则跳过 |
| **verify** | 验证已转换的WSL发行版是否正常工作 | Smoke Test + 工具链检查 + 文件系统检查 |
| **cleanup** | 清理/删除WSL发行版（安全确认） | 自动清理VHDX残留 |

核心功能：Podman rootful模式桥接转换 → Windows/WSL路径自动映射 → UID=1000用户自动探测 → wsl.conf自动配置 → 非交互shell PATH初始化 → 多级验证清单。

> **为什么用Podman桥接而非纯Python解压？** docker save输出的是OCI分层镜像格式（含whiteout删除标记、多层叠加、Unix特殊文件），纯解压会得到含`.wh.*`垃圾文件的混乱文件树。Podman作为OCI原生运行时，能100%精确处理叠层合并、whiteout语义、权限保留、硬链接等所有OCI格式细节。Python脚本仅作为无WSL环境时的Bootstrap备用方案（见L2文档）。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "镜像转WSL"、"docker镜像导入WSL"、"把镜像变成WSL发行版"、"镜像恢复为WSL环境"
- "wsl --import 镜像"、"docker save转wsl"、"镜像转rootfs"、"podman export转wsl"
- "docker-wsl-bridge"、"镜像tar.gz转成WSL"、"tar.gz转rootfs"
- "没有Docker Desktop怎么启动镜像"、"WSL重置后恢复开发环境"
- 任何涉及将Docker/Podman镜像缓存转换为WSL可启动发行版的需求

> **关于触发**：即使没有明确说"用skill"，只要涉及将docker save格式的镜像tar.gz转为WSL发行版，就应该使用本Skill。不要手动拼接wsl/podman命令——那会绕过rootful模式配置、路径转换、用户探测、wsl.conf配置和验证清单。

## 4. 方案选择决策树

```
需要将镜像tar.gz转为WSL发行版？
├─ 已有可用的WSL Linux发行版（wsl -l -v 有非Stopped的Ubuntu等）？
│   ├─ 是，且已安装Podman → convert命令直接转换（第5.2节）
│   └─ 是，但未安装Podman → setup-workspace（第5.1节）然后convert
├─ 没有任何WSL发行版？
│   └─ setup-workspace安装Ubuntu+Podman → convert（第5.1+5.2节）
└─ 完全无法安装WSL（极罕见）？
    └─ 使用Python备用脚本（L2文档方案B）
```

**转换不可逆提醒**：`wsl --import` 会创建VHDX文件占用磁盘空间（≈镜像虚拟大小），`wsl --unregister` 会彻底删除发行版数据。转换前确认磁盘空间充足。

> **为什么需要rootful Podman？** WSL中默认的rootless Podman使用uid/gid映射，导出的rootfs文件所有权会发生偏移（容器内root映射为宿主机高uid），导致WSL导入后文件权限异常。使用`sudo podman`（rootful模式）可避免此问题，导出的rootfs uid/gid与容器内完全一致。

## 5. 核心步骤（快速开始）

### 5.1 准备转换工作区（setup-workspace）

> **幂等检查**：执行前先检测Ubuntu是否已安装、Podman是否已安装，已就绪则跳过对应步骤。

```powershell
# 步骤1：检查已有WSL发行版
wsl -l -v

# 如果没有Ubuntu（或其他Linux发行版），安装一个
wsl --install -d Ubuntu
# ⚠️ 安装后重启终端！首次启动Ubuntu会要求设置Linux用户名和密码
#    记住这个密码——后续sudo需要用到

# 步骤2：在Ubuntu中安装Podman（rootful模式）
wsl -d Ubuntu -u root -- bash -c "apt-get update && apt-get install -y podman"

# 步骤3：验证Podman可用
wsl -d Ubuntu -u root -- bash -c "podman info 2>&1 | head -5"
# 应显示版本和存储信息，而非"cannot connect"错误
```

> **如果已有其他WSL发行版（如Debian）**：可以用其替代Ubuntu，只需将命令中的`Ubuntu`替换为对应发行版名称，并确保能`apt-get install podman`（或对应包管理器）。

### 5.2 核心转换（convert）

> **前置条件**：工作区已就绪（5.1完成），镜像tar.gz文件存在。

```powershell
# ===== 配置参数（根据实际情况修改）=====
$imageTar = "D:\spaces\SpecWeave\.docker-cache\images\devcontainer-base_latest.tar.gz"  # docker save格式的tar.gz
$distroName = "devcontainer-base"                                                      # WSL发行版名称
$installDir = "D:\WSL\$distroName"                                                     # VHDX安装目录（推荐非系统盘）
$workspaceDistro = "Ubuntu"                                                            # 转换用工作区发行版
# =============================================

# 步骤1：路径转换（Windows路径 → WSL /mnt/路径）
$wslImageTar = "/mnt/" + $imageTar.Substring(0,1).ToLower() + ($imageTar.Substring(2) -replace '\\','/')
$rootfsPath = Split-Path $imageTar -Parent
$wslRootfsOut = "/mnt/" + $rootfsPath.Substring(0,1).ToLower() + ($rootfsPath.Substring(2) -replace '\\','/') + "/$distroName-rootfs.tar.gz"
$rootfsLocal = "$rootfsPath\$distroName-rootfs.tar.gz"

# 步骤2：WSL内加载镜像→创建容器→导出rootfs（核心转换）
wsl -d $workspaceDistro -u root -- bash -c "podman load -i '$wslImageTar' && IMAGE_NAME=\$(podman images --format '{{.Repository}}:{{.Tag}}' | head -1) && echo 'Loaded image:' \$IMAGE_NAME && podman create --name wsl-export \$IMAGE_NAME && podman export wsl-export | gzip -1 > '$wslRootfsOut' && podman rm wsl-export && echo '=== RootFS export done ===' && ls -lh '$wslRootfsOut'"

# 步骤3：创建安装目录并导入WSL
New-Item -ItemType Directory -Path $installDir -Force | Out-Null
wsl --import $distroName $installDir $rootfsLocal --version 2
echo "=== WSL import done ==="

# 步骤4：自动探测默认用户（UID=1000）
$defaultUser = wsl -d $distroName -u root -- sh -c 'awk -F: "\$3==1000 {print \$1}" /etc/passwd'
echo "Detected default user: $defaultUser"

# 步骤5：配置wsl.conf
wsl -d $distroName -u root -- sh -c "printf '[user]\ndefault=$defaultUser\n[boot]\nsystemd=false\n' > /etc/wsl.conf"
echo "=== wsl.conf configured ==="

# 步骤6：重启使配置生效
wsl --terminate $distroName

# 步骤7：验证
wsl -d $distroName -- sh -l -c "echo OK && whoami && cat /etc/os-release | grep PRETTY_NAME"
```

**成功标志**：最后一条命令输出 `OK` + 非root用户名 + OS版本信息。

> **镜像名\<none\>处理**：如果`podman images`显示REPOSITORY/TAG为`<none>/<none>`（旧版docker save格式可能丢失tag），脚本中的`podman images --format`会取到`<none>:<none>`。此时需手动处理：`wsl -d Ubuntu -u root -- bash -c "IMAGE_ID=\$(podman images -q | head -1) && podman tag \$IMAGE_ID $distroName:latest"`，然后重新执行步骤2。

**VOLUME警告**：`podman export`不包含Dockerfile中VOLUME声明的挂载点内容。开发环境镜像（Python/Node/GCC等）通常不受影响，但数据库镜像（MySQL/PostgreSQL等）的数据目录会是空的。

### 5.3 验证发行版（verify）

```powershell
$distroName = "devcontainer-base"

# === Smoke Test（必做，30秒）===
echo "=== Smoke Test ==="
wsl -d $distroName -- sh -l -c "echo '1. Startup:' && echo OK"
wsl -d $distroName -- sh -l -c "echo '2. User:' && whoami"
wsl -d $distroName -- sh -l -c "echo '3. Writable:' && touch /tmp/test && rm /tmp/test && echo WRITABLE"
wsl -d $distroName -- sh -l -c "echo '4. D-drive:' && ls /mnt/d/ > /dev/null && echo D-MOUNT-OK"
wsl -d $distroName -- sh -l -c "echo '5. Python:' && python3 --version 2>&1 || echo 'no python3'"
```

### 5.4 清理发行版（cleanup）

```powershell
$distroName = "devcontainer-base"
$installDir = "D:\WSL\$distroName"

# 步骤1：注销发行版（⚠️ 不可恢复！）
wsl --unregister $distroName

# 步骤2：删除VHDX文件（wsl --unregister不会自动删除物理文件）
Remove-Item -Recurse -Force $installDir -ErrorAction SilentlyContinue

# 步骤3：验证清理完成
wsl -l -v
```

## 6. 输入参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| image_tar | string | 是 | - | docker save格式的镜像tar.gz绝对路径 |
| distro_name | string | 是 | - | 目标WSL发行版名称（如`devcontainer-base`） |
| install_dir | string | 否 | D:\WSL\<distro_name> | VHDX安装目录，推荐非系统盘 |
| workspace_distro | string | 否 | Ubuntu | 转换用工作区WSL发行版名称 |
| default_user | string | 否 | 自动探测UID=1000 | 默认用户名，不填则自动探测 |
| conda_init | boolean | 否 | false | 是否配置conda全局激活（检测/opt/conda或~/miniconda3） |

## 7. 依赖与前置准备

- **WSL2**：必须启用WSL2（`wsl --version` 应显示WSL版本信息）
- **工作区WSL**：至少一个可用的Linux发行版（Ubuntu 24.04+推荐）
- **Podman**：在工作区WSL中安装（本Skill的setup-workspace可自动安装）
- **磁盘空间**：目标安装盘需有 ≈镜像虚拟大小（通常1.5-2x压缩rootfs大小）的可用空间
- **镜像缓存**：由 [docker-cache-cmd](../docker-cache-cmd/SKILL.md) 或手动 `docker save` 产出的tar.gz文件
- **Python备用脚本**：`.agents/scripts/docker-save-to-wsl-rootfs.py`（无WSL环境时使用，见L2文档方案B）

> **为什么需要磁盘空间约为镜像虚拟大小？** WSL2使用VHDX动态磁盘，初始大小很小但会随使用增长到镜像的虚拟大小（即解压后的rootfs大小）。1.4GB镜像→约1.5GB VHDX。

## 8. 配置默认用户与Shell环境

转换完成后，wsl.conf和shell环境需要正确配置才能非交互使用：

### 8.1 自动探测用户

```powershell
# 优先找UID=1000（标准Linux首个普通用户）
$user = wsl -d $distro -u root -- sh -c 'awk -F: "\$3==1000 {print \$1}" /etc/passwd'
# 如果找不到，找第一个UID>=1000的用户
if (-not $user) {
    $user = wsl -d $distro -u root -- sh -c 'awk -F: "\$3>=1000 && \$3<65534 {print \$1; exit}" /etc/passwd'
}
```

### 8.2 配置wsl.conf

```powershell
wsl -d $distro -u root -- sh -c @"
printf '[user]\ndefault=$user\n[boot]\nsystemd=false\n' > /etc/wsl.conf
"@
```

> **systemd=true还是false？** Docker基础镜像通常不含systemd（容器里不需要init系统），用`systemd=false`。如果转换的是完整操作系统镜像（如官方Ubuntu rootfs、含systemd的定制镜像），改为`systemd=true`。判断依据：`wsl -d $distro -u root -- ls /usr/lib/systemd/systemd`是否存在。

### 8.3 Conda全局激活（可选）

如果镜像中安装了conda，需要配置非交互shell也能激活：

```powershell
# 检测conda路径
wsl -d $distro -u root -- sh -c "ls /opt/conda/etc/profile.d/conda.sh 2>/dev/null || ls /root/miniconda3/etc/profile.d/conda.sh 2>/dev/null || ls /home/*/miniconda3/etc/profile.d/conda.sh 2>/dev/null || echo 'conda not found'"

# 写入全局激活脚本（根据上面探测的路径调整）
wsl -d $distro -u root -- sh -c 'echo ". /opt/conda/etc/profile.d/conda.sh && conda activate base" > /etc/profile.d/conda.sh'
```

> **为什么需要/etc/profile.d/而非~/.bashrc？** `wsl -d distro -- command`是非交互非login shell，不加载`~/.bashrc`。`/etc/profile.d/*.sh`会被login shell（`sh -l -c`/`bash -l -c`）加载。因此执行WSL命令时统一用`wsl -d distro -- sh -l -c "..."`或`bash -l -c "..."`。

## 9. 安全检查清单（转换完成前逐项确认）

- [ ] 磁盘空间充足（目标盘可用空间 ≥ 镜像虚拟大小）
- [ ] 镜像tar.gz路径正确（是docker save/podman save产出的，不是手动打包的）
- [ ] WSL2已启用（`wsl --version`正常）
- [ ] 工作区WSL发行版可正常启动（`wsl -d Ubuntu -- echo OK`）
- [ ] Podman使用rootful模式（`wsl -d Ubuntu -u root -- podman info`）
- [ ] 安装目录在非系统盘（避免占满C盘）
- [ ] 同名旧发行版已处理（存在则先`wsl --unregister`或用不同名称）
- [ ] podman export完成后验证rootfs文件大小合理（30-40%压缩比）
- [ ] wsl.conf已写入且default用户正确
- [ ] `wsl --terminate`后验证默认用户是非root
- [ ] Smoke Test全部通过（启动/用户/可写/D盘挂载）
- [ ] 核心工具版本检查通过（python3/gcc/node等镜像中的关键工具）

## 10. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| `wsl --import`报"系统找不到指定路径" | 安装目录不存在 | 先`New-Item -ItemType Directory -Path $installDir -Force` |
| `wsl --import`成功但启动报错 | rootfs格式错误（直接用了docker save tar.gz） | 确保经过Podman export转换，不要直接import docker save格式 |
| 导入后有大量`.wh.`开头文件 | 未经过OCI运行时转换 | 使用本Skill的Podman桥接流程重新转换 |
| Podman报"VM does not exist" | Windows Podman Desktop的podman machine损坏 | 在WSL Ubuntu内用`sudo podman`（rootful），不使用podman machine |
| `podman load`报"unrecognized image format" | tar.gz不是有效的OCI/docker save格式 | 确认是`docker save`/`podman save`产出的文件 |
| podman load后镜像名显示`<none>` | 旧版docker save格式丢失tag | `sudo podman tag <IMAGE-ID> <name>:<tag>`手动打tag |
| WSL启动后默认是root | wsl.conf未配置或未生效 | 检查wsl.conf内容，先`wsl --terminate`，不行则`wsl --shutdown` |
| `wsl -d distro -- command`找不到python/conda | 非交互shell不加载.bashrc | 通过`/etc/profile.d/*.sh`配置，用`sh -l -c`/`bash -l -c`执行 |
| 导出的rootfs文件权限全是nobody | rootless podman uid映射问题 | 使用`sudo podman`（rootful模式） |
| VHDX占用空间过大 | WSL2自动扩容不自动缩容 | `wsl --export`→`wsl --unregister`→`wsl --import`压缩VHDX |
| `wsl -l -v`显示发行版但无法启动 | VHDX被删除但注册表残留 | `wsl --unregister <distro>`清除残留后重新导入 |
| Windows路径在WSL中找不到 | 路径转换错误 | 盘符小写、反斜杠改正斜杠、前缀`/mnt/` |

> 完整故障排查（17项）见L2操作指南。

## 11. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 这些是不会报错但结果不符合预期的隐性陷阱。

- **wsl命令在PowerShell中执行，podman命令在WSL中执行**：本Skill是跨Shell编排——PowerShell侧负责WSL管理（import/terminate/unregister/配置），WSL侧负责Podman操作（load/create/export）。不要在PowerShell中直接调用podman（除非安装了Windows Podman Desktop，但那有VM问题）。
- **`wsl -d Ubuntu -u root`避免sudo密码提示**：用`-u root`直接以root身份进入WSL执行podman命令，避免sudo交互式密码提示阻塞自动化流程。
- **`wsl --terminate`有时不生效**：WSL可能缓存了旧的wsl.conf配置。如果terminate后默认用户仍是root，执行`wsl --shutdown`完全关闭WSL子系统再重试。
- **gzip -1而非-9**：rootfs是临时中转文件（import后即不再需要），高压缩率节省的空间相对于增加的CPU时间不划算。gzip -1速度最快。
- **Alpine镜像无bash**：Alpine基础镜像使用busybox，没有bash。所有`wsl -d`命令需用`sh -l -c`替代`bash -l -c`。
- **podman create不启动容器**：`podman create`只注册容器元数据不启动进程，因此不需要镜像有可执行的ENTRYPOINT/CMD，任何镜像都可以create+export。
- **VHDX不会自动删除**：`wsl --unregister`只注销发行版注册信息，不会删除磁盘上的VHDX文件。必须手动`Remove-Item`删除安装目录。
- **Windows路径转WSL路径规则**：`D:\foo\bar.tar.gz` → `/mnt/d/foo/bar.tar.gz`。盘符小写，冒号去掉，反斜杠改正斜杠，前缀`/mnt/`。
- **wsl.conf中的systemd=false是Docker镜像的正确设置**：Docker容器里不运行systemd，所以从Docker镜像导出的rootfs也没有systemd。设为true会导致WSL启动失败或卡死。
- **Python脚本备用方案有whiteout残留**：`.agents/scripts/docker-save-to-wsl-rootfs.py`在完全无WSL环境时可用，但whiteout处理不完整，多约15%冗余文件（不影响功能但占用额外空间）。优先使用Podman方案。

## 12. 典型工作流

### 12.1 完整流程：从镜像缓存到可用WSL环境

```powershell
# 假设docker-cache-cmd已保存了镜像tar.gz
# 一键完成：准备工作区→转换→验证
# （将参数替换为实际值）
$imageTar = "D:\spaces\SpecWeave\.docker-cache\images\devcontainer-base_latest.tar.gz"
$distroName = "devcontainer-base"
$installDir = "D:\WSL\$distroName"
$wsDistro = "Ubuntu"

# 1. 安装工作区（如果需要）
wsl -l -v  # 检查是否已有Ubuntu
# 如果没有：wsl --install -d Ubuntu（重启终端后继续）

# 2. 安装Podman（如果需要）
wsl -d $wsDistro -u root -- bash -c "which podman || (apt-get update && apt-get install -y podman)"

# 3. 执行转换（按5.2节完整步骤）
# ...

# 4. 进入环境开始使用
wsl -d $distroName
```

### 12.2 WSL重置后快速恢复

```powershell
# WSL重置导致所有发行版丢失后：
# 1. 先安装Ubuntu
wsl --install -d Ubuntu
# 重启终端

# 2. 在Ubuntu中安装Podman并转换所有缓存镜像
# （对每个缓存镜像执行5.2节convert步骤）
```

### 12.3 与docker-cache-cmd协同

```text
docker-cache-cmd save/build  →  .docker-cache/images/<name>_<tag>.tar.gz
                                        ↓
                            docker-wsl-bridge-cmd convert
                                        ↓
                            wsl -d <distro-name>（可用开发环境）
```

## 13. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| **操作指南（完整SOP）** | L2 | [docker-cache-wsl-migration-guide.md](../../../docs/knowledge/operations/docker-cache-wsl-migration-guide.md) | 查看完整分步说明、深度验证脚本、Free-Threading测试 |
| **模式库（原理）** | L2 | [oci-image-wsl-rootfs-bridge.md](../../../docs/retrospective/patterns/code-patterns/oci-image-wsl-rootfs-bridge.md) | 理解OCI分层→flat rootfs的原理、反模式、迁移示例 |
| **Python备用脚本** | L2 | [docker-save-to-wsl-rootfs.py](../../scripts/docker-save-to-wsl-rootfs.py) | 无WSL环境时的纯Python离线转换方案 |
| **镜像缓存Skill** | L1 | [docker-cache-cmd](../docker-cache-cmd/SKILL.md) | 管理Docker镜像tar.gz缓存（save/load/build） |
| **复盘报告** | L2 | [retrospective-docker-cache-to-wsl-migration-20260818](../../../docs/retrospective/reports/environment-setup/retrospective-docker-cache-to-wsl-migration-20260818/README.md) | 验证过程、性能数据、问题排查记录 |

## 14. Changelog

- **v1.0.0** (2026-08-18): 初始版本。封装Podman运行时桥接转换方案为Skill，支持convert/setup-workspace/verify/cleanup四个子命令，包含路径自动映射、UID=1000用户自动探测、wsl.conf配置、conda非交互shell初始化、Smoke Test验证清单、12项错误处理、10个Gotchas陷阱。与docker-cache-cmd形成缓存→转换链路。在devcontainer-base:latest（26层/1.41GB/Python 3.14t）上验证通过。
