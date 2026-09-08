+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖版本清单

| 库名称 | 版本号 | 来源地址 | 引入日期 | 许可证 | 类型 | 跟踪分支 | 备注 |
|---|---|---|---|---|---|---|---|
| flexloop | main@d618849a (v0.7.2-125-gd618849) | git@gitcode.com:flexloop/flexloop.git | 2026-06-27 | Apache-2.0 | owned_collab | main | 自有协作子模块，AgentForge AI Agent 协作框架 |
| ark-cli | main@88313923 (v1.0.3-1-g8831392) | git@github.com:volcengine/ark-cli.git | 2026-07-07 | Apache-2.0 | third_party | main | 第三方只读依赖，火山引擎方舟大模型平台 CLI 工具 |
| awesome-okf | main@f6c70627 | https://github.com/yzfly/awesome-okf.git | 2026-08-06 | MIT | third_party | main | 中文OKF生态第三方只读依赖，含7个零依赖插件与Skill集 |
| awesome-okf-bundle | main@ebe906b7 | git@github.com:linyiru/awesome-okf.git | 2026-08-06 | CC0-1.0 | third_party | main | linyiru/awesome-okf 上游 OKF 列表与 bundle 构建器 |
| awesome-okf-kit | main@5e862eeb | git@github.com:vinodborole/awesome-okf-kit.git | 2026-08-06 | MIT | third_party | main | OKF bundle 注册表工具集 |
| okf-bundle-template | main@a0883c7b | git@github.com:vinodborole/okf-bundle-template.git | 2026-08-06 | 未声明 | third_party | main | OKF bundle 发布模板 |
| knowledge-catalog | main | git@github.com:GoogleCloudPlatform/knowledge-catalog.git | 2026-08-06 | Apache-2.0 | third_party | — | Google Cloud Knowledge Catalog 元数据管理平台 |
| jira-skill | v3.29.0@b0dba28 | git@github.com:netresearch/jira-skill.git | 2026-08-28 | MIT AND CC-BY-SA-4.0 | third_party | — | Netresearch Jira MCP Skill 工具集（Jira CLI 与 Agent Skills） |
| veadk-python | 1.0.10@ffbf295 | git@github.com:volcengine/veadk-python.git | 2026-08-29 | Apache-2.0 | third_party | — | 火山引擎 Agent 开发框架（Volcengine Agent Development Kit），veadk-python Wiki 信源 |
| podman-compose | main@e3df1047 | git@github.com:containers/podman-compose.git | 2026-09-08 | GPL-2.0-only | third_party | — | containers 官方容器编排工具链：podman-compose 声明式编排（只读依赖，gitlink pin commit e3df10472e194ab6d547b5ad25542c5c79e1a5fb） |
| podman-py | main@5dd81b49 | git@github.com:containers/podman-py.git | 2026-09-08 | Apache-2.0 | third_party | — | containers 官方容器编排工具链：podman-py SDK（只读依赖，gitlink pin commit 5dd81b49f35733a27b8051c47e23d3b4c85ea716） |
| toolbox | main@81401f64 | git@github.com:containers/toolbox.git | 2026-09-08 | Apache-2.0 | third_party | — | containers 官方容器编排工具链：toolbox 工具（只读依赖，gitlink pin commit 81401f64b3865129ea66f2a5e02a7eb40edd4fb8） |

## 更新记录

- 2026-09-08 | 引入 containers 上游三仓库 third_party 子模块：podman-compose（main@e3df1047，GPL-2.0-only）、podman-py（main@5dd81b49，Apache-2.0）、toolbox（main@81401f64，Apache-2.0），容器编排工具链只读依赖，gitlink pin commit

- 2026-08-29 | 引入 veadk-python 子模块（1.0.10@ffbf295，third_party，Apache-2.0，火山引擎 Agent 开发框架；信源稳定性门修复：Wiki 41个文件800处引用从 .chaos 临时克隆迁移至 vendor）
- 2026-08-28 | 引入 jira-skill 子模块（v3.29.0，third_party，MIT AND CC-BY-SA-4.0，Netresearch Jira MCP Skill 工具集）
- 2026-08-06 | 引入 awesome-okf-bundle、awesome-okf-kit、okf-bundle-template 子模块（从 .chaos/libs/ 迁移至 vendor/，修复架构边界）
- 2026-08-06 | 引入 awesome-okf 子模块（从根目录迁移至 vendor/，修复架构边界）
- 2026-06-29 | 修复 flexloop 遗留反向依赖链接（9处失效外链），推送到 flexloop main 分支
- 2026-06-29 | 调整 flexloop 治理模式为 owned_collab（自有协作），跟踪 main 分支
- 2026-06-29 | 完善 flexloop 元数据（版本号、commit、来源、许可证 Apache-2.0）
- 2026-06-27 | 初始化版本清单
- 2026-07-07 | 引入 ark-cli 子模块（third_party，Apache-2.0，跟踪 main 分支）
