---
id: "offline-delivery-docs-index"
title: "offline-delivery 文档索引"
source: "../README.md"
---
# offline-delivery 文档

`apps/containers/` 下的**厂商侧离线交付链路**：把基镜像构建为**底座镜像**（依赖面 + torch，
**不含 XMNN**），再打包成客户可自持的离线交付物（客户侧零 Python、零联网、零仓库外引用）。
镜像按**底座 / 载荷分离**组织：底座在厂商侧构建归档，载荷 wheel 随交付包发出、
由客户侧 `xmnnctl load` 派生装入。

本应用完全自包含，**禁止**依赖 `client/` 与 `shared/`；外部输入仅
`../workspace/dist/xmnn-*.whl`（预构建**载荷** wheel）与基镜像 `localhost/jupyter-podman-rootless:latest`
（底座基座）。

## 文档目录

| 文档 | 说明 |
|------|------|
| [00-overview.md](00-overview.md) | 定位、制品流（载荷 wheel + 基镜像 → 底座镜像 → 交付包）、与组内其它应用的边界、目录结构 |
| [01-quickstart.md](01-quickstart.md) | 前置条件 → `stage`/`deps`/`build`/`pack`/`smoke` 逐命令与预期输出 → 常见失败与处置 → 更新交付（只换 whl）→ 新增第二个交付产品 |

## AI 协作者规范

- 应用级路由与 P0 约束速览：[../AGENTS.md](../AGENTS.md)
- 交付流水线硬约束（骨架纯移动、CRLF 守卫、版本语义、形态 tag、归档原子性、`release.json`、禁依赖、pwsh7）：[../.agents/rules/delivery-pipeline.md](../.agents/rules/delivery-pipeline.md)
- 资产容器索引与父级回退链：[../.agents/README.md](../.agents/README.md)

## 快速开始

```bash
cd apps/containers/offline-delivery
bin/relpack stage && bin/relpack deps && bin/relpack build && bin/relpack pack && bin/relpack smoke
```

`build` 产出**底座**镜像（`localhost/xmnn-runtime:base-cpu`，不含 XMNN），`pack` 导出底座归档与
校验清单；载荷 wheel 随交付包发出，客户侧 `./xmnnctl load` 幂等导入底座后**派生构建**交付镜像。
逐步说明与失败处置见 [01-quickstart.md](01-quickstart.md)。

## 变更日志

完整变更历史见 [../.agents/CHANGELOG.md](../.agents/CHANGELOG.md)。