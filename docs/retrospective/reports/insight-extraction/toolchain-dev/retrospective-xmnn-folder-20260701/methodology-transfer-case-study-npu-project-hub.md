---
id: "retrospective-xmnn-folder-20260701-transfer-case-npu-project-hub"
date: "2026-07-02"
type: "case-study"
source: "retrospective-xmnn-folder-20260701 方法论对 npu-project-hub 的迁移验证"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/toolchain-dev/retrospective-xmnn-folder-20260701/methodology-transfer-case-study-npu-project-hub.toml"
---
# XMNN 方法论对 npu-project-hub 的迁移案例总结

## 一、案例定位

本报告不是对 `xmnn` 目录本体的再次审计，而是记录 `retrospective-xmnn-folder-20260701/` 这组复盘资产如何被迁移到另一个真实工程 `workspace/apps/npu-project-hub/apps/project-hub`，并驱动一条连续的现代化改造链路。

案例目标：

- 验证 `xmnn` 复盘中提炼出的建议，是否具备跨项目可迁移性
- 区分“只适用于预编译 runtime wheel”的局部经验，与“适用于更广泛工程治理”的通用方法论
- 为后续类似项目提供一份可直接复用的迁移样板

## 二、原始方法论输入

本次迁移主要复用了 [export-suggestions.md](export-suggestions.md) 中的五类建议：

| 原建议 | 在 `npu-project-hub` 中的解释 |
|---|---|
| 明确包形态/交付边界 | 明确后端 Python 包、前端静态构建产物、镜像交付件、Compose 编排入口的边界 |
| 拆分依赖为 runtime/dev/extras 三层 | 收敛后端运行依赖与开发依赖，避免继续使用分散的 `requirements*.txt` |
| 离线闭环制度化 | 同时考虑 Python 依赖、npm 依赖、基础镜像、Compose 运行与健康检查 |
| 增加运行时基线/兼容性声明 | 将“运行时约束”从隐含知识提升为健康检查、容器约定和后续待补的基线文件 |
| 统一与校准交付文档引用路径 | 保证 README、deploy、CI、Compose、Dockerfile 等入口相互一致 |

## 三、迁移过程

### 3.1 阶段映射

| 阶段 | `xmnn` 方法论关键词 | `npu-project-hub` 实际动作 | 结果 |
|---|---|---|---|
| T1 | 构建入口统一 | 建立 `pyproject.toml`，迁移到 `scikit-build-core` + `CMake` + `Ninja` | 完成 |
| T2 | 依赖边界收敛 | 删除 `server/requirements.txt`、`server/requirements-dev.txt`，统一到 `project.dependencies` 与 `optional-dependencies.dev` | 完成 |
| T3 | 交付入口统一 | 对齐 README、CI、Dockerfile、Compose、Nginx 代理与环境变量前缀 | 完成 |
| T4 | 离线闭环制度化 | 使用本地基础镜像 tar 做离线导入，修复前端镜像构建源超时问题 | 完成 |
| T5 | 运行态可验证 | 新增 `/api/health`、Compose `healthcheck`、UI 等待 API 健康 | 完成 |
| T6 | 用户侧最小闭环 | 项目页补齐完整性、备份恢复、Git 历史操作面板 | 完成 |
| T7 | 运行时基线显式声明 | 尚未新增独立“兼容性/基线声明文件”与自动校验 | 待完成 |

### 3.2 关键适配

`xmnn` 原始建议在迁移到 `npu-project-hub` 时做了三类扩展：

1. 从“wheel 分发”扩展到“全栈交付”
   - `xmnn` 更偏 Python runtime wheel 与运行镜像
   - `npu-project-hub` 额外包含 React 前端、Nginx 代理、Compose 编排
   - 因此“交付边界”必须扩展到前端构建产物与服务间依赖关系

2. 从“离线安装”扩展到“离线部署”
   - `xmnn` 更关注 wheel 与容器的离线交付
   - `npu-project-hub` 还要处理 `node:20-alpine`、`nginx:1.27-alpine`、`python:3.13-slim` 的基础镜像导入
   - 还暴露出 npm registry 在 BuildKit 场景下的超时与误报问题

3. 从“运行时自举”扩展到“运维操作闭环”
   - `xmnn` 的重点是 import 与运行时库路径自举
   - `npu-project-hub` 的重点变成：用户是否能在 Web 上完成完整性扫描、备份恢复、Git 历史查看
   - 这说明“闭环”不只发生在构建链，也发生在产品界面层

## 四、迁移结果

### 4.1 已验证有效的建议

| 建议类型 | 验证结果 | 说明 |
|---|---|---|
| 入口统一 | 有效 | 构建、运行、部署、CI 的认知负担显著下降 |
| 依赖分层 | 有效 | 删除冗余 `requirements*.txt` 后，依赖入口更清晰 |
| 离线闭环 | 有效 | 离线镜像导入 + Compose 验证证明“受限网络下仍可交付” |
| 文档对齐 | 有效 | README / deploy / CI / Dockerfile 一致后，排障路径更短 |
| 最小闭环导向 | 有效 | 通过项目页操作台补齐“看状态 -> 执行动作 -> 查看结果”链路 |

### 4.2 暂未完全闭环的建议

| 建议类型 | 当前状态 | 后续方向 |
|---|---|---|
| 运行时基线/兼容性声明 | 仅有健康检查和容器约束，未形成独立基线文件 | 增加版本/系统库/Node 与 Python 运行时基线清单 |
| 权限治理 UI | 后端已有模型与接口，前端尚未补齐 | 增加角色分配与项目授权页面 |
| 配置中心可视化 | 仍偏配置文件驱动 | 增加 Web 配置管理界面 |

## 五、迁移价值

本案例说明：`xmnn` 复盘中真正可迁移的，不是某个具体文件写法，而是以下四类“工程判断框架”：

- 先统一入口，再谈局部优化
- 先划清运行时与开发态边界，再谈依赖扩展
- 先把离线/受限网络场景制度化，再谈交付完成
- 先补最小操作闭环，再扩展高级能力

换言之，`retrospective-xmnn-folder-20260701/` 已经从“一次针对特定目录的静态审计”升级为“一套可迁移的现代化改造方法论资产”。

## 六、给后续项目的复用清单

若后续要把本方法论再次迁移到其它项目，可优先套用以下顺序：

1. 确认交付边界：源码、包、镜像、前端产物、运维入口分别是什么
2. 收敛依赖入口：尽量保留单一事实来源，删除历史残留入口
3. 建立离线闭环：依赖源、基础镜像、健康检查、可验证路径一次性打通
4. 统一文档入口：README、CI、deploy、Dockerfile、Compose 不允许各说各话
5. 补齐最小用户闭环：至少做到“查看状态 + 执行动作 + 获取结果”
6. 最后再补运行时基线声明：把环境兼容性从隐式知识变成显式契约
