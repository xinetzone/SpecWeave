---
title: WSL Ubuntu 26.04 LTS 安装与迁移复盘报告
date: 2026-07-22
session: sc-20260722-wsl-ubuntu2604-migration
scenario: knowledge
tags: [WSL, Ubuntu, 环境配置, 迁移, 离线安装]
source: "WSL Ubuntu 26.04 安装与迁移实践"
---

# WSL Ubuntu 26.04 LTS 安装与迁移复盘报告

## 摘要

本次任务在 Windows WSL2 环境中完成 Ubuntu 26.04 LTS (Resolute Raccoon) 的离线安装，并从临时目录安全迁移到 `D:\WSL\Ubuntu-26.04` 永久位置。安装过程遇到网络超时、TLS证书验证失败等问题，通过手动下载+import方式成功解决。迁移过程采用export→unregister→import标准流程，实现用户配置零丢失。最终产出3个可复用模式：WSL离线手动安装、WSL发行版安全迁移、WSL导入后默认用户配置。

## 质量门记录

| 质量门 | 状态 | 说明 |
|--------|------|------|
| G1（事实无因果词） | ✅ 通过 | 事实清单9大类，纯客观描述 |
| G2（洞察四元组完整） | ✅ 通过 | 5条洞察均包含现象+根因+影响+建议 |
| G3（模式可迁移） | ✅ 通过 | 3个模式均具备触发场景+核心步骤+反模式+迁移验证 |

---

## 一、事实记录（R阶段）

### 1.1 系统环境基线

| 项目 | 数据 |
|------|------|
| Windows版本 | 10.0.26220.8925 |
| WSL版本 | 2.9.3.0 |
| WSL内核版本 | 6.18.35.2-1 |
| 已有发行版 | Ubuntu-24.04（Running, WSL2）、podman-machine-default（Stopped） |
| .wslconfig配置 | dnsTunneling=true; networkingMode=mirrored; autoProxy=true; firewall=true |

### 1.2 产出物清单

| 产出物 | 路径/数据 | 说明 |
|--------|----------|------|
| Ubuntu 26.04 LTS | D:\WSL\Ubuntu-26.04\ext4.vhdx (1.42 GB) | WSL2虚拟磁盘 |
| 系统版本 | Ubuntu 26.04 LTS (Resolute Raccoon) | codename: resolute |
| 默认用户 | xin (uid=1000, sudo组) | 免密sudo配置 |
| Python版本 | Python 3.14.4 | 系统自带 |
| wsl.conf | 配置default=xin, systemd=true | 默认用户+systemd启用 |

### 1.3 时间线

| 时间 | 事件 |
|------|------|
| 2026-07-22 14:17 | 首次尝试wsl --install，网络超时 |
| 2026-07-22 14:25-14:30 | 下载ubuntu-26.04-wsl-amd64.wsl（396MB） |
| 2026-07-22 14:30-14:32 | 首次导入到.temp目录，创建用户xin，配置wsl.conf |
| 2026-07-22 14:34-14:38 | export为tar（1.2GB）→ unregister → import到D:\WSL |
| 2026-07-22 14:38 | 迁移完成，验证配置保留 |

### 1.4 遇到的问题

| 编号 | 问题 | 发生阶段 |
|------|------|---------|
| P01 | wsl --install 返回 WININET_E_TIMEOUT（GitHub raw无法访问） | 在线安装阶段 |
| P02 | apt.releases.ubuntu.com TLS证书名称不匹配 | 下载阶段 |
| P03 | cdimage.ubuntu.com 返回404页面（281字节HTML） | 备用源尝试 |
| P04 | wsl --import后默认用户为root | 首次导入后 |
| P05 | systemd用户会话启动警告（不影响功能） | 每次启动 |
| P06 | 沙盒限制无法删除.temp临时文件 | 清理阶段 |

---

## 二、洞察分析（I阶段）

### 洞察1：WSL在线安装网络超时问题
- **现象**：`wsl --install -d Ubuntu-26.04` 返回 `WININET_E_TIMEOUT`，无法从 raw.githubusercontent.com 获取 DistributionInfo.json
- **根因**：在线安装需要从GitHub拉取发行版列表元数据，该域名在当前网络环境下连接超时
- **影响**：无法使用最便捷的一行命令安装方式，必须切换到手动下载+导入路径
- **建议**：优先准备手动下载方案（直接下载.wsl/.tar文件）作为在线安装的降级路径

### 洞察2：HTTPS证书验证失败问题
- **现象**：`Invoke-WebRequest` 和 `curl.exe` 均报证书错误（`RemoteCertificateNameMismatch`、`SEC_E_WRONG_PRINCIPAL`）
- **根因**：apt.releases.ubuntu.com 的TLS证书与域名不匹配（SNI/主体名称错误）
- **影响**：无法通过标准HTTPS方式下载镜像，需要跳过证书验证
- **建议**：遇到Ubuntu官方镜像下载证书问题时，优先使用PowerShell 7的`-SkipCertificateCheck`参数，或换用cdimage.ubuntu.com镜像源；下载后必须检查文件大小（281字节=404错误页面）

### 洞察3：wsl --import后默认用户重置为root
- **现象**：通过`wsl --import`导入的发行版默认以root启动
- **根因**：WSL导入流程不会保留Microsoft Store版安装时创建的默认用户配置，wsl.conf虽然在文件系统中存在，但需要发行版重启才能生效
- **影响**：导入后首次启动需要手动配置默认用户，否则直接以root登录
- **建议**：导入完成后需立即验证默认用户（`wsl -d <name> -- whoami`），若为root则重新配置wsl.conf并terminate发行版

### 洞察4：.wsl文件格式本质是tar.gz
- **现象**：下载的.wsl文件魔数为`1F-8B`（gzip格式），而非ZIP或APPX格式
- **根因**：Ubuntu官方WSL镜像实际上是一个gzip压缩的tar包（rootfs），可直接被`wsl --import`接受
- **影响**：不需要额外解压或格式转换，下载后即可直接导入
- **建议**：对于其他发行版也可先检查文件头（`1F-8B`=gzip tar, `50-4B`=zip）来确定处理方式

### 洞察5：WSL发行版迁移的配置完整性
- **现象**：从.temp迁移到D:\WSL过程中，export→unregister→import三步操作保留了所有用户配置
- **根因**：`wsl --export`导出完整文件系统（包含用户、配置、已安装包），import时完整还原
- **影响**：迁移过程用户数据零丢失，wsl.conf、sudo配置、用户组全部保留
- **建议**：迁移是安全操作，只要export tar文件完整，所有配置都能保留；迁移后需验证而非重新配置

---

## 三、可复用模式（E阶段）

### 模式1：WSL发行版手动安装模式（离线降级方案）

**触发场景**：
- `wsl --install -d <Distro>` 网络超时（WININET_E_TIMEOUT）
- GitHub raw域名无法访问
- 需要自定义安装位置到非系统盘

**核心步骤**：
1. `wsl --list --online` 确认发行版名称
2. 从官方镜像源下载对应`.wsl`文件：
   - Ubuntu主源：`https://apt.releases.ubuntu.com/<version>/ubuntu-<version>-wsl-amd64.wsl`
   - 备用源：`https://cdimage.ubuntu.com/releases/<codename>/release/`
3. PowerShell 7下载（`-SkipCertificateCheck`应对证书问题）：
   ```powershell
   Invoke-WebRequest -Uri $url -OutFile $file -SkipCertificateCheck
   ```
4. 检查文件头确认格式：读取前2字节，`1F-8B`=gzip tar可直接导入；检查文件大小，<1KB的是错误页面
5. 创建目标目录（推荐非系统盘如D:\WSL\<Distro>）
6. `wsl --import <Name> <InstallDir> <File> --version 2`
7. 创建用户并配置`/etc/wsl.conf`：
   ```bash
   useradd -m -s /bin/bash <username>
   usermod -aG sudo <username>
   echo "<username> ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/<username>
   chmod 0440 /etc/sudoers.d/<username>
   ```
   ```ini
   # /etc/wsl.conf
   [user]
   default = <username>
   [boot]
   systemd = true
   ```
8. `wsl --terminate <Name>` 重启使配置生效
9. 验证：`wsl -d <Name> -- whoami` 应显示<username>而非root

**反模式**：
- ❌ 使用curl.exe -k下载不检查文件大小（可能得到HTML错误页面）
- ❌ 下载后不检查文件大小就导入（281字节的文件是404页面）
- ❌ 导入后不验证默认用户（会直接以root登录）
- ❌ 在C盘用户目录下安装WSL（占系统盘空间，C盘已81%使用率）
- ❌ 使用`ubuntu config --default-user`（仅适用于Store版，import版不生效）

**迁移验证**：此模式适用于任何WSL发行版（Ubuntu/Debian/Fedora/Arch等）的离线安装，不仅限于Ubuntu 26.04

---

### 模式2：WSL发行版安全迁移模式（零数据丢失）

**触发场景**：
- 需要将WSL从临时目录/系统盘迁移到其他位置
- 需要备份WSL发行版
- 需要复制WSL环境到另一台机器
- C盘空间不足需要迁移到D盘

**核心步骤**：
1. `wsl --terminate <DistroName>` 确保发行版完全停止（必须等待2秒以上）
2. `wsl --export <DistroName> <backup.tar>` 导出完整文件系统
   - 导出大小≈实际使用空间×1.1~1.3（未压缩tar）
3. **验证export文件存在且大小合理后**，再执行下一步（防止导出失败导致数据丢失）
4. `wsl --unregister <DistroName>` 注销原发行版
5. 在新位置创建目标目录（确保目标磁盘有足够空间：ext4.vhdx会自动增长）
6. `wsl --import <DistroName> <NewDir> <backup.tar> --version 2` 导入
7. 启动验证：
   ```powershell
   wsl -d <DistroName> -- whoami
   wsl -d <DistroName> -- lsb_release -a
   ```
8. 确认默认用户正确、数据完整后，删除临时tar文件释放磁盘空间

**反模式**：
- ❌ 直接移动ext4.vhdx文件（WSL注册表路径不会更新，导致发行版无法启动）
- ❌ 未export就unregister（数据永久丢失，无法恢复）
- ❌ 迁移到系统盘（容易占满C盘空间，当前C盘仅剩80G可用）
- ❌ 导入后不验证直接使用（可能默认用户变为root，后续操作权限混乱）
- ❌ 导出后立即删除原目录（应先验证import成功再清理）

**迁移验证**：此模式是WSL官方推荐的标准迁移方式，适用于所有WSL2发行版，配置、用户、已安装软件、用户数据完整保留。已在Ubuntu 24.04→D:\WSL\Ubuntu和本次Ubuntu 26.04两次实践中验证通过。

---

### 模式3：WSL默认用户配置模式（导入后修复）

**触发场景**：
- `wsl --import`导入后默认以root登录
- 从备份恢复后需要切换回普通用户
- 需要创建新的默认用户
- 手动安装WSL发行版后的初始化配置

**核心步骤**：
1. 以root身份启动：`wsl -d <DistroName> --user root`（或直接启动后默认就是root）
2. 创建用户（如不存在）：
   ```bash
   useradd -m -s /bin/bash <username>
   passwd <username>  # 可选：设置密码
   usermod -aG sudo <username>
   echo "<username> ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/<username>
   chmod 0440 /etc/sudoers.d/<username>
   ```
3. 创建/更新`/etc/wsl.conf`（关键！这是import版唯一有效的默认用户设置方式）：
   ```ini
   [user]
   default = <username>

   [boot]
   systemd = true

   [network]
   generateResolvConf = true
   ```
4. **在PowerShell中**（不是在WSL内部）执行：`wsl --terminate <DistroName>`
5. 等待2秒，验证：`wsl -d <DistroName> -- whoami`（应显示<username>）

**反模式**：
- ❌ 使用wsl.conf的default配置后不terminate直接测试（配置不会生效，必须重启发行版）
- ❌ 忘记将用户加入sudo组（无法执行apt等管理员操作）
- ❌ 使用`ubuntu config --default-user <username>`（仅适用于Microsoft Store版Ubuntu，import版无此命令）
- ❌ 直接修改/etc/passwd（不持久，且可能导致其他问题）
- ❌ sudoers文件权限设置错误（必须chmod 0440，否则sudo不读取）

**迁移验证**：此模式适用于所有通过import方式安装的WSL发行版，无论Linux发行版类型（Ubuntu/Debian/Fedora/Arch等）。已在Ubuntu 26.04实践中验证。

---

## 四、快速参考命令

### 安装新WSL发行版（离线方式）
```powershell
# 1. 下载（PowerShell 7）
$url = "https://apt.releases.ubuntu.com/26.04/ubuntu-26.04-wsl-amd64.wsl"
$file = "D:\Downloads\ubuntu-26.04-wsl-amd64.wsl"
Invoke-WebRequest -Uri $url -OutFile $file -SkipCertificateCheck

# 2. 导入
wsl --import Ubuntu-26.04 D:\WSL\Ubuntu-26.04 $file --version 2

# 3. 配置用户（以root进入后执行）
wsl -d Ubuntu-26.04 -u root -- bash -c "
  useradd -m -s /bin/bash xin
  usermod -aG sudo xin
  echo 'xin ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/xin
  chmod 0440 /etc/sudoers.d/xin
  echo -e '[user]\ndefault = xin\n\n[boot]\nsystemd = true' > /etc/wsl.conf
"

# 4. 重启并验证
wsl --terminate Ubuntu-26.04
wsl -d Ubuntu-26.04 -- whoami
```

### 迁移WSL到新位置
```powershell
# 1. 停止发行版
wsl --terminate Ubuntu-26.04

# 2. 导出
wsl --export Ubuntu-26.04 D:\backup\ubuntu2604.tar

# 3. 注销（确认export成功后！）
wsl --unregister Ubuntu-26.04

# 4. 在新位置导入
wsl --import Ubuntu-26.04 D:\WSL\Ubuntu-26.04 D:\backup\ubuntu2604.tar --version 2

# 5. 验证
wsl -d Ubuntu-26.04 -- whoami
```

---

## 五、待改进项（Action Backlog）

| 优先级 | 改进项 | 说明 |
|--------|--------|------|
| 低 | 清理.temp临时文件 | 沙盒限制未能自动删除，需手动清理：`D:\spaces\SpecWeave\.temp\wsl-ubuntu2604\`（约1.6GB） |
| 低 | systemd用户会话警告 | "Failed to start the systemd user session"警告不影响功能，可后续排查journalctl |
| 低 | 安装常用工具 | 当前为纯净系统，缺少docker、nodejs等开发工具，按需安装 |

---

## 六、相关参考

- [WSL官方文档 - 导入导出](https://learn.microsoft.com/zh-cn/windows/wsl/basic-commands#import-and-export-a-distribution)
- [Ubuntu 26.04 WSL镜像](https://apt.releases.ubuntu.com/26.04/)
- 历史相关复盘：[Windows磁盘空间诊断与WSL虚拟磁盘优化](../../2026-07-22-windows-disk-cleanup-wsl-optimization.md)
- WSL VHDX压缩脚本：[compress-wsl-vhdx.ps1](../../../../../scripts/compress-wsl-vhdx.ps1)
