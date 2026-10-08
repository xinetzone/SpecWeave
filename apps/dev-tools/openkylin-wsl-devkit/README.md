# openkylin-wsl-devkit（okw）

openKylin WSL 开发工具包：**以 WSL 作为切入点**的 openKylin 开发与应用工具。把知识库
`docs/knowledge/tech/openkylin-docs-wiki/` 中已验证的实操经验（本机实测安装、五步验收、
E_UNEXPECTED 排障、OKBS 编译流程）封装为可执行 CLI，降低 openKylin 开发入门摩擦。

## 定位

| 能力 | 命令 | 依据（知识库） |
|---|---|---|
| WSL 发行版生命周期 | `okw list / status / import / export / unregister / exec` | F-017/F-018、S26 |
| openKylin 环境五步验收 | `okw verify <name>` | §3.3 实测口径 |
| deb 打包骨架 | `okw scaffold deb --project ... --series ...` | F-015 系列代号纪律 |
| OKBS dput 上传配置 | `okw scaffold dput --openkylin-id ...` | D-F-027 |
| rootless Podman 预检/安装/验收 | `okw podman preflight / install / verify` | 见下文「Podman 入门」 |
| 知识库快速参考 | `okw ref series / wsl-troubleshoot / okbs / verify` | 全部概念页 |

## 安装

要求：Windows + WSL2、Python ≥ 3.10（无第三方运行时依赖）。

```powershell
# 开发安装（仓库内）
cd apps\dev-tools\openkylin-wsl-devkit
python -m pip install -e .
# 或构建 wheel
python -m build
```

## 用法

```text
okw list                          # 列出 WSL 发行版（含默认星标）
okw status <name>                 # 单个发行版状态
okw import <镜像.wsl> --name openKylin-3.0 --location D:\wsl\ok30 --version 2
okw verify <name>                 # 五步环境验收（os-release/用户/UID/systemd/包数）
okw exec <name> -- <cmd...>       # 发行版内执行命令（透传）
okw export <name> --output <tar>
okw unregister <name> --yes       # 破坏性操作，必须显式 --yes
okw scaffold deb --project demo --series huanghe --version 0.1.0
okw scaffold dput --openkylin-id <你的ID> [--output ~/.dput.cf]
okw ref <主题>                     # series / wsl-troubleshoot / okbs / verify
okw podman preflight <name>        # 只读检查 rootless Podman 前置条件
okw podman install <name> --yes    # 刷新 APT、安装 Podman 并配置用户映射
```

示例（验收已导入的发行版）：

```powershell
okw verify openKylin-3.0
```

## Podman 入门

三步流程（均只针对指定发行版，不改变 WSL 默认发行版，不修改软件源与 `wsl.conf`）：

```text
okw podman preflight <name>              # 1. 只读预检（不 apt update、不写文件）
okw podman install <name> --yes          # 2. 安装并幂等配置 subuid/subgid
okw podman verify <name>                 # 3. 以默认非 root 用户验收 rootless 上下文
okw podman verify <name> --smoke-image <本地镜像>   # 可选：本地镜像一次性容器冒烟
```

**为什么推荐 rootless 而不是 `sudo podman`**：rootless 模式以普通用户身份运行容器，
容器进程不持有 root 权限、镜像与存储位于用户目录、利用 `/etc/subuid` 与 `/etc/subgid`
做 UID/GID 映射（标准区间 `[100000, 165536)`），即便容器逃逸也被限制在从属 ID 区间内；
`sudo podman` 等价于 rootful，容器进程拥有真实 root 能力，仅建议在 rootless 无法满足的
极少数场景（特定内核文件系统操作）下使用。

`install` 必须显式提供 `--yes`；省略时只打印 4 条副作用清单并以退出码 2 中止，不做任何写入：

1. 以 root 身份在发行版内执行 `apt update` 刷新 APT 索引；
2. 以 root 身份 `apt install` 安装 4 个直接包：`podman` / `uidmap` / `slirp4netns` / `fuse-overlayfs`；
3. 仅当默认用户缺少映射且区间无冲突时，向 `/etc/subuid` 与 `/etc/subgid` 各追加一行
   `默认用户:100000:65536`（两文件先共同校验、原子写入，失败自动回滚）；
4. 以默认用户身份执行 rootless 验收子集（`podman --version` 与 `podman info` 的 Rootless 字段）。

安装或验收时填写的发行版名称，可用 `okw list`（带默认星标）或 Windows 侧 `wsl -l -v` 查询。

容器冒烟（`--smoke-image`）默认关闭、验收全程不联网：执行前先用 `podman image exists`
确认镜像在本地已存在，运行时固定追加 `--pull=never` 禁止任何隐式拉取。因此需要先在
发行版内自行准备镜像：`podman pull <镜像>`（或 `podman load -i <镜像包>`）；镜像缺失时
verify 直接 FAIL 并给出上述提示，不会尝试联网。

退出码：`0` 全部通过；`1` 存在 FAIL（报告附中文修复指引）；`2` 用法错误、仅 UNKNOWN，
或 install 未提供 `--yes`。

## 常见问题 FAQ

- **rootless Podman 与 `sudo podman` 怎么选？** 日常开发一律用默认用户的 rootless
  Podman：无 root 权限、用户级存储、subuid/subgid 隔离；rootful（`sudo podman`）只在
  rootless 确实无法支撑的特权场景使用。`okw podman verify` 在 root 身份下不会给出 rootless PASS。
- **`okw podman install` 到底会改什么？** 仅在显式 `--yes` 后执行 4 项副作用（见上文
  「Podman 入门」清单）：apt update、安装 4 个直接包、幂等追加 subuid/subgid、rootless 自检；
  不加第三方源、不改 `wsl.conf`、不切换默认发行版。安装流程不宣称事务回滚，中断后可直接
  重跑——apt 与映射写入均按幂等设计。
- **怎么确认发行版名称？** 运行 `okw list` 查看名称与默认星标，或在 PowerShell 运行
  `wsl -l -v` 对照 `NAME` 列。
- **`--smoke-image` 报镜像不存在怎么办？** verify 不会替你拉取镜像。先进入发行版手动
  `podman pull <镜像>` 或 `podman load -i <镜像包>`，确认 `podman image exists <镜像>`
  返回 0 后再带 `--smoke-image` 重跑；冒烟固定 `--pull=never`，无远程拉取。
- **APT 报错「候选缺失」**：确认当前软件源是否提供该包。不要添加第三方源；如需启用官方
  backports 或 proposed 组件，请手动编辑发行版的 `sources.list`。
- **APT 报网络错误**：检查发行版的网络连接和 DNS 解析；网络恢复后在发行版内重跑
  `sudo apt update`，再重试 `okw podman install <name> --yes`。
- **APT 报哈希校验失败**：镜像源元数据与软件包校验不一致时，可切换到官方镜像，或清理
  `/var/lib/apt/lists` 后重新执行 `sudo apt update`。

## 设计要点

- **零第三方运行时依赖**：标准库 subprocess/argparse/pathlib；WSL 调用统一封装
  （全路径 wsl.exe、`WSL_UTF8=1`、非零退出码归一为受控结果）。
- **安全边界**：任何命令都不会改变默认发行版（星标保护快照对比）；`unregister` 必须
  显式 `--yes`；`import` 前校验镜像 gzip 头（魔数 `1F 8B`）；不自动写用户系统
  （dput 配置默认打印、`--output` 才写文件）；不修改知识库。
- **验收口径**：五步与知识库 §3.3 一致；包数对照 S26 实测基准 405（注明 `dpkg -l`
  含表头差 5 行的口径差异）。
- **弱口令提示**：预置账号 `openkylin/openkylin` 为弱口令（F-018），首次进入请立即
  `passwd`；本工具在 import/ref 中提示。

## 与知识库的映射

- 排障三问（E_UNEXPECTED/E_ABORT）→ `docs/knowledge/tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md`
- 双镜像选型与桌面版 xrdp → `.../references/wsl-dual-image-selection.md`
- 版本代号（yangtze/nile/huanghe）→ `.../concepts/02-release-lifecycle.md`
- OKBS 编译流程 → `.../concepts/06-developer-infrastructure.md`

## 开发与测试

```powershell
python -m pip install -e . pytest pytest-cov build
pytest            # 全部 mock，不触发真实 WSL；覆盖率：整体 ≥80%，关键模块 ≥90%
```

- WSL 调用全部 mock（`tests/conftest.py` 注入假输出），CI/本机均可安全运行。
- 真实冒烟仅对只读路径：`okw list` / `okw verify <已有发行版>`。

## 已知边界（不承诺项）

- 不替代 `wsl --install` 系统级安装；不自动下载镜像。
- Desktop WSL（6.14GiB）运行时结论在知识库中仍为【待实测】，本工具不固化未验证建议。
- 不调用 OKBS/factory API；dput 配置生成后由开发者自行上传。
