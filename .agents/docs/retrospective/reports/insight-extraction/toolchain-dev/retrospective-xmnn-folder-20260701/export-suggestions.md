---
id: "retrospective-xmnn-folder-20260701-export"
date: "2026-07-01"
type: "export-suggestions"
source: "external: 不存在-server/libs/notebook/xmnn 目录结构与打包系统静态分析"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/toolchain-dev/retrospective-xmnn-folder-20260701/export-suggestions.toml"
---
# 导出建议 — XMNN 目录的改进方向与行动项

## 一、行动项（按优先级）

| 优先级 | 行动项 | 验收口径 |
|---:|---|---|
| P0 | 明确 `xmnn` 的“包形态”边界（module vs package） | 文档与实际 import 行为一致；不再出现“同名但语义不同”的歧义 |
| P1 | 拆分依赖为 runtime/dev/extras 三层 | `pip install xmnn` 安装体积与依赖数量显著降低；`pip install xmnn[frontends]` 仍可获得完整前端能力 |
| P1 | 离线闭环制度化：运行镜像支持可开关的 optional deps 安装策略 | 纯离线环境可构建或可运行（明确二选一策略）；有网络时可启用 extras |
| P2 | 为 wheel 与 runtime image 增加“运行时基线/兼容性声明”与自动校验 | 构建产物能自描述其绑定的 LLVM/系统库基线；运行时启动阶段能检测出明显不匹配 |
| P2 | 统一与校准交付文档引用路径 | `client/README.md` 等文档的链接不指向不存在路径；交付入口清晰可追溯 |

## 二、建议落地草案（可选实现思路）

### 2.1 依赖拆分建议（pyproject 结构）

- `project.dependencies`：仅保留运行时最小集（如 `numpy`、`psutil`、`cloudpickle` 等）
- `project.optional-dependencies.dev`：放入 `pytest`、`pandas`、`openpyxl`、`matplotlib` 等
- `project.optional-dependencies.frontends`：保持现有前端组合（onnx/pytorch/tensorflow）

### 2.2 离线交付策略建议（client/）

- 引入显式策略变量（例如 `INSTALL_EXTRAS=0/1` 或 `OFFLINE_MODE=1`）
- 若目标是“离线可构建”：准备本地 wheels 缓存目录并在 Containerfile 中优先 `--find-links`
- 若目标是“离线可运行”：将 extras 统一预装到镜像，构建时不再访问网络

### 2.3 包形态边界建议（xmnn 数据目录）

可选方向：
- 把 `site-packages/xmnn/` 数据目录改为 `site-packages/xmnn_data/`（避免与扩展模块同名）
- 或保留 `xmnn/` 目录，但让其成为明确的 Python package（含 `__init__.py`），并把扩展模块更名为 `xmnn_core`（避免 import 歧义）

## 三、复用验证状态（以 `npu-project-hub` 为参照）

本节不是说 `xmnn` 已经完成了这些动作，而是记录本建议集在另一个真实项目中的复用验证情况，用于区分“已被工程实践证实有效”的建议与“仍待验证”的建议。

| 建议项 | 在 `npu-project-hub` 中的映射动作 | 复用验证状态 | 备注 |
|---|---|---|---|
| 统一打包/构建入口 | 建立 `pyproject.toml`，收敛到 `scikit-build-core` + `CMake` + `Ninja` | 已验证 | 证明该建议可跨项目迁移 |
| 依赖分层 | 后端运行依赖与 dev 依赖收敛 | 已验证 | 说明“最小运行时 + 开发附加依赖”策略有效 |
| 离线闭环制度化 | Dockerfile/Compose/健康检查 + 离线基础镜像导入 | 已验证 | 从 Python 包场景扩展到全栈镜像场景 |
| 交付文档路径统一 | README / deploy / CI 路径统一 | 已验证 | 说明文档入口统一具有直接收益 |
| 运行时基线/兼容性声明 | 尚未形成显式基线文件或自动校验 | 未验证完成 | 仍是下一阶段优先保留项 |
| 用户侧操作闭环 | 项目页补齐完整性、备份恢复、Git 历史 | 已验证扩展 | 属于在原建议基础上的落地增强 |

## 四、建议的下一步更新方向

- 若继续推进 `xmnn` 本体，优先保留原表中的 P0/P1/P2，不因其它项目已验证而降级。
- 若继续把本目录作为“方法论资产”使用，建议新增一条维护规则：
  每当某条建议在其它真实工程中完成落地，应回写“复用验证状态”，把文档从一次性复盘升级为持续演进的模式库。
