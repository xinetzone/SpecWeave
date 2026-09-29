---
id: "wechat-mp-archiver-docs-index"
title: "wechat-mp-archiver 文档索引"
source: "../README.md"
---
# wechat-mp-archiver 文档

`apps/dev-tools/` 下的**微信公众号全量内容归档工具**：私有部署采集服务（R2 主路线）提供文章列表，本机 Python 薄管线（`mp-archiver` CLI）完成正文/富媒体下载、元数据管理、断点续采与增量更新，产出离线归档、RAG 语料与分析报表三种形态。

**仅供个人学习研究与本地存档使用**，请勿商用或公开再分发归档内容。

## 文档目录

| 文档 | 说明 |
|------|------|
| [00-overview.md](00-overview.md) | 定位、三种产出形态、架构图（采集服务 ↔ 管线职责边界） |
| [01-quickstart.md](01-quickstart.md) | 安装 → 从零到单篇演练（七步）→ 账号准备与凭证管理 |
| [02-commands.md](02-commands.md) | 命令总览、`sync`/`run` 编排语义与退出码契约、`list`/`fetch`/`export-rag`/`report` 详解 |
| [03-operations.md](03-operations.md) | 默认限速（保守档与核定依据）、故障处置与断点续跑、故障排查速查 |
| [04-storage-and-layout.md](04-storage-and-layout.md) | 存储布局（archive/data/exports/logs）与源码结构 |
| [05-compliance.md](05-compliance.md) | 合规声明六条（含 24 小时删除义务） |
| [06-credential-probe-2026-09-29.md](06-credential-probe-2026-09-29.md) | 微信凭证联调实测记录：探针分阶段结果、IP 白名单阻塞、环境缺口与绕过版本门槛的跑法 |
| [07-40164-blocker-followup.md](07-40164-blocker-followup.md) | 40164 第二轮排查：IPv6 误判纠正、微信校验顺序实测推导、已排除项与处置顺序 |
| [08-48001-auth-gate-and-path-decision.md](08-48001-auth-gate-and-path-decision.md) | 白名单通过后 48001：发布能力接口需微信认证（单接口无权限的判定证据）、R1/R2 路径定位与决策 |

## AI 协作者规范

- 应用级路由与 P0 约束速览：[../AGENTS.md](../AGENTS.md)
- 归档管线硬约束（限速/回环绑定/幂等续跑/熔断矩阵/结构感知风控/退出码/合规落地）：[../.agents/rules/archive-pipeline.md](../.agents/rules/archive-pipeline.md)
- 资产容器索引与父级回退链：[../.agents/README.md](../.agents/README.md)

## 快速开始

```bash
cd apps/dev-tools/wechat-mp-archiver
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cd deploy && docker compose up -d                  # 采集服务仅绑 127.0.0.1:5000
cd .. && mp-archiver init-db && mp-archiver doctor
mp-archiver sync -a 意识食谱                        # 日常增量（幂等、可中断续跑）
```

逐步说明与失败处置见 [01-quickstart.md](01-quickstart.md) 与 [03-operations.md](03-operations.md)。

## 变更日志

完整变更历史见 [../.agents/CHANGELOG.md](../.agents/CHANGELOG.md)。