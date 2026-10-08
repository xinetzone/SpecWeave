# openkylin-wsl-devkit（okw）

openKylin WSL 开发工具包：通过 `okw` 管理 WSL 发行版、验收 openKylin 环境、生成 deb/dput 脚手架，并查询知识库快速参考。

## 文档

完整使用手册已迁入 SpecWeave 文档中心：

- [openKylin WSL 开发工具包指南](../../../docs/tech/guides/openkylin-wsl-devkit/index.md)
- [安装与快速开始](../../../docs/tech/guides/openkylin-wsl-devkit/01-getting-started.md)
- [WSL 与开发命令参考](../../../docs/tech/guides/openkylin-wsl-devkit/02-command-reference.md)
- [rootless Podman 指南](../../../docs/tech/guides/openkylin-wsl-devkit/03-podman-rootless.md)
- [开发、测试与边界](../../../docs/tech/guides/openkylin-wsl-devkit/04-development-and-boundaries.md)

## 快速安装

要求 Windows + WSL2、Python 3.10 或更高版本；运行时不依赖第三方包。

```powershell
python -m pip install -e .
okw list
okw verify <name>
```

rootless Podman 操作从只读预检开始，安装必须显式确认：

```text
okw podman preflight <name>
okw podman install <name> --yes
okw podman verify <name>
```

`okw podman verify --smoke-image` 仅使用发行版内已存在的镜像，不会隐式拉取。完整约束与操作说明见[工具包指南](../../../docs/tech/guides/openkylin-wsl-devkit/index.md)。
