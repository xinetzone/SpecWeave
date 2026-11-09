# WecomTeam 子模块分组

本目录为企业微信（WeCom）官方开源生态的 vendor 子模块分组目录，仅承载 git 子模块与元数据，不存放自行修改的源码。

## 元数据

- **名称**：WecomTeam 企业微信生态（wecom-cli、wecom-unified、wecom-aibot-python-sdk）
- **版本**：固定 commit 检出（wecom-cli@1d48b6c、wecom-unified@cae8a5b、wecom-aibot-python-sdk@6bcb59a，均为短 hash，完整 hash 见 [../VERSION.md](../VERSION.md)）
- **来源**：git@github.com:WecomTeam/<repo>.git（3 个仓库，均为 third_party）
- **引入日期**：2026-11-09
- **用途**：企业微信办公能力（CLI + Skill 套件）与智能机器人 Python SDK 的只读信源，供后续技能/文档引用与源码分析
- **许可证**：均为 MIT，以各仓库 LICENSE 文件为准

## 仓库清单

| 仓库 | 版本基线 | 默认分支 | 定位 |
|---|---|---|---|
| wecom-cli | 1.3.4（npm `@wecom/cli`） | main | 企业微信官方 CLI（Rust 实现），覆盖消息/邮件/文档/表格/待办/日程/会议/微盘/通讯录，内置 14 个 Agent Skills |
| wecom-unified | 无独立版本号 | main | 企业微信全能 Skill 套件，依赖 wecom-cli ≥ 1.2.1，含业务域 references 与辅助脚本 |
| wecom-aibot-python-sdk | 1.0.1（pyproject） | master | 企业微信智能机器人 Python SDK，WebSocket 长连接、流式回复、模板卡片、事件回调、文件下载解密 |

## 管理说明

- 3 个仓库均为 **Git 子模块（third_party）**：第三方只读依赖，gitlink 固定 commit，禁止本地修改
- 分组内各子模块的固定 hash、远程 URL 与许可证详情以 [../VERSION.md](../VERSION.md) 为准
- 子模块的元数据统一登记在 [../README.md](../README.md) 与 [../VERSION.md](../VERSION.md)，不在子模块目录内创建 README.md（避免 submodule dirty）
