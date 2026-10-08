---
type: "Reference"
title: "okw 开发、设计与边界"
source: "../../../../apps/dev-tools/openkylin-wsl-devkit/README.md#设计要点"
---

# okw 开发、设计与边界

## 设计要点

- **零第三方运行时依赖**：使用 Python 标准库 `subprocess`、`argparse` 和 `pathlib`。
- **统一 WSL 调用**：封装全路径 `wsl.exe` 调用、`WSL_UTF8=1` 环境设置与非零退出码归一化。
- **保护默认发行版**：命令执行前后检查默认发行版星标，避免意外切换。
- **显式确认破坏性操作**：`unregister` 必须提供 `--yes`。
- **校验导入镜像**：`import` 前检查 gzip 头魔数 `1F 8B`。
- **避免隐式写系统配置**：dput 配置默认打印，只有指定 `--output` 才写文件；工具不修改 openKylin 知识库。
- **弱口令提示**：对预置账号 `openkylin/openkylin` 提示首次进入后立即修改密码。

## 验收口径

`okw verify <name>` 的五步验收与 openKylin 知识库 §3.3 的实测口径一致。包数以实测基准 405 为参考；`dpkg -l` 输出含表头，需注意与软件包数量统计口径相差 5 行。

## 开发与测试

在应用目录安装测试和构建工具并运行测试：

```powershell
python -m pip install -e . pytest pytest-cov build
pytest
```

测试全部 mock WSL 调用，不会触发真实 WSL。覆盖率目标为整体不低于 80%，关键模块不低于 90%。真实冒烟仅针对只读路径，例如 `okw list` 和对已有发行版执行 `okw verify <name>`。

## 已知边界

- 不替代 `wsl --install` 等系统级安装操作，也不自动下载发行版镜像。
- 不调用 OKBS 或 factory API；dput 配置生成后由开发者自行上传。
- Desktop WSL 镜像选型、磁盘占用和运行时实测结果见[双 WSL 镜像对照与选型参考](../../../knowledge/tech/openkylin-docs-wiki/references/wsl-dual-image-selection.md)；本工具不自动下载或导入该镜像。

## 知识库映射

- WSL 导入排障三问（`E_UNEXPECTED`/`E_ABORT`）：[WSL 安装与稀疏 VHD 实操指南](../../../knowledge/tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md)。
- 双 WSL 镜像选型与桌面版启动：[双 WSL 镜像对照与选型参考](../../../knowledge/tech/openkylin-docs-wiki/references/wsl-dual-image-selection.md)。
- 版本代号（`yangtze`/`nile`/`huanghe`）：[版本发布与生命周期](../../../knowledge/tech/openkylin-docs-wiki/concepts/02-release-lifecycle.md)。
- OKBS 编译流程：[开发者基础设施](../../../knowledge/tech/openkylin-docs-wiki/concepts/06-developer-infrastructure.md)。
