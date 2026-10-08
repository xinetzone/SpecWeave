---
type: "Reference"
title: "okw WSL 与开发命令参考"
source: "../../../../apps/dev-tools/openkylin-wsl-devkit/README.md#用法"
---

# okw WSL 与开发命令参考

`okw` 封装 WSL 发行版操作、环境验收、deb/dput 脚手架和 openKylin 知识参考。`unregister` 会注销发行版，必须显式提供 `--yes`。

## 发行版生命周期

| 命令 | 用途 |
|---|---|
| `okw list` | 列出 WSL 发行版并标出默认项 |
| `okw status <name>` | 查看单个发行版状态 |
| `okw import <image> --name <name> --location <path> [--version 2]` | 导入镜像 |
| `okw export <name> --output <tar>` | 导出发行版 |
| `okw unregister <name> --yes` | 确认并注销发行版 |
| `okw exec <name> -- <cmd...>` | 在目标发行版内执行命令 |
| `okw verify <name>` | 执行 openKylin 环境五步验收 |

示例：

```powershell
okw import .\openKylin-3.0-wsl-amd64.wsl --name openKylin-3.0 --location D:\wsl\ok30 --version 2
okw exec openKylin-3.0 -- uname -a
okw export openKylin-3.0 --output .\openKylin-3.0.tar
```

发行版名称可用 `okw list` 或 Windows 侧 `wsl -l -v` 查询。导入时若失败，工具会提示按知识库中的排障三问检查镜像/导入位置、空闲内存和纯 tar 导入路径；详见 [WSL 安装与稀疏 VHD 实操指南](../../../knowledge/tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md)。

## 开发脚手架

生成 deb 打包骨架：

```text
okw scaffold deb --project demo --series huanghe --version 0.1.0
```

支持 `yangtze`、`nile`、`huanghe` 系列代号，也可按工具说明使用 `1.0`、`2.0`、`3.0`。生成后编辑 `control`/`changelog`、将源码放入项目根目录，再按提示运行 `dpkg-buildpackage -us -uc`。

生成 OKBS dput 配置片段：

```text
okw scaffold dput --openkylin-id <你的ID> [--output ~/.dput.cf]
```

默认只打印配置；指定 `--output` 才写入文件。上传由开发者自行执行，命令会提示 `dput okbs:~<你的ID>/ppa <source.changes>`；上传需要自行安装 `paramiko` 或 `dput-ng`。

## 知识库参考

```text
okw ref
okw ref series
okw ref wsl-troubleshoot
okw ref okbs
okw ref verify
```

`okw ref` 不修改知识库。openKylin 版本代号和开发流程见[知识库对应页面](../../../knowledge/tech/openkylin-docs-wiki/concepts/02-release-lifecycle.md)与[开发者基础设施](../../../knowledge/tech/openkylin-docs-wiki/concepts/06-developer-infrastructure.md)。
