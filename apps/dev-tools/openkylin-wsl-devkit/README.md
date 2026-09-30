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
```

示例（验收已导入的发行版）：

```powershell
okw verify openKylin-3.0
```

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
