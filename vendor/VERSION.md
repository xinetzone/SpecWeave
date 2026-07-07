+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖版本清单

| 库名称 | 版本号 | 来源地址 | 引入日期 | 许可证 | 类型 | 跟踪分支 | 备注 |
|---|---|---|---|---|---|---|---|
| flexloop | main@d618849a (v0.7.2-125-gd618849) | git@gitcode.com:flexloop/flexloop.git | 2026-06-27 | Apache-2.0 | owned_collab | main | 自有协作子模块，AgentForge AI Agent 协作框架 |
| ark-cli | main@88313923 (v1.0.3-1-g8831392) | git@github.com:volcengine/ark-cli.git | 2026-07-07 | Apache-2.0 | third_party | main | 第三方只读依赖，火山引擎方舟大模型平台 CLI 工具 |

## 更新记录

- 2026-06-29 | 修复 flexloop 遗留反向依赖链接（9处失效外链），推送到 flexloop main 分支
- 2026-06-29 | 调整 flexloop 治理模式为 owned_collab（自有协作），跟踪 main 分支
- 2026-06-29 | 完善 flexloop 元数据（版本号、commit、来源、许可证 Apache-2.0）
- 2026-06-27 | 初始化版本清单
- 2026-07-07 | 引入 ark-cli 子模块（third_party，Apache-2.0，跟踪 main 分支）
