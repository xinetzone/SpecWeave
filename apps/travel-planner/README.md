# travel-planner · 旅行规划工作台

本地单用户 Web 应用：多行程管理、每日行程编排、预算跟踪、打包清单、JSON 导入导出，以及可选的 **BYOK AI 行程草稿生成**（任意 OpenAI 兼容端点）。

- **Python 3.14+** · FastAPI + Jinja2 服务端渲染 · 原生 CSS/JS 零构建链 · 零数据库
- 仅监听 `127.0.0.1`（本机使用）；CSRF + Origin 校验 + 单实例文件锁
- 运行时数据全部落在 gitignore 私域区 `playground/travel-planner/data/`（本仓库内默认）
- 规格：`.trae/specs/travel-planner/`（spec.md / tasks.md / review.md）

## 功能

| 模块 | 说明 |
|---|---|
| 行程管理 | 创建/编辑/复制/删除/归档；状态：规划中/进行中/已完成/已归档；「今天」高亮与未完成计数 |
| 每日编排 | 按天分组的条目（景点/餐饮/住宿/交通/购物/其他）：时间段、地点、费用、备注、完成态；组内上移/下移 |
| 预算 | 按类型/按天自动汇总，总预算对照、剩余/超支提示（纯加法，不做币种换算） |
| 打包清单 | 每行程独立清单：名称/数量/勾选，随行程复制 |
| 导入导出 | 单行程/全量 JSON 导出；导入先校验预览、确认后写入，id 冲突自动换新 id |
| AI 行程生成 | 可选在线层：按目的地/日期/人数/偏好生成结构化草稿 → 白名单校验 → 预览可剔除微调 → 确认导入（human-in-the-loop，AI 不自动落盘） |

## 安装与启动

```powershell
# Python 3.14+ 环境
python -m venv .venv
.venv\Scripts\pip install .          # 或 pip install -e .[dev]
.venv\Scripts\travel-planner serve   # http://127.0.0.1:8765/
```

```bash
python -m venv .venv && .venv/bin/pip install .
.venv/bin/travel-planner serve
```

常用命令：

| 命令 | 说明 |
|---|---|
| `travel-planner serve` | 启动本地 Web（`--data-dir` / `--host` / `--port` 可选，host 仅允许回环） |
| `travel-planner check` | 自检数据目录、行程数量与 LLM 配置状态 |

环境变量：`TRAVEL_PLANNER_DATA`（数据目录）、`TRAVEL_PLANNER_API_KEY`（LLM 密钥，优先于配置文件）。

## 数据目录

默认 `playground/travel-planner/data/`（仓库相对路径自动推算，亦可 `--data-dir` 指定任意位置）：

```
data/
├── config.yaml     # LLM 配置（可选）
├── trips/<id>.json # 每个行程一个人类可读 JSON
└── backups/        # 每次覆盖写前的滚动备份（保留最近 5 份）
```

所有写入为原子操作（临时文件 + `os.replace`）；行程改坏可从 `backups/` 找回，或用导出的 JSON 恢复。

## AI 行程生成（BYOK，可选）

不配置时除 AI 生成外全部功能离线可用。配置步骤：

1. 编辑 `data/config.yaml`：

```yaml
llm:
  base_url: "https://api.deepseek.com/v1"   # 任意 OpenAI 兼容端点（含本机代理）
  model: "deepseek-chat"
  timeout: 60
```

2. 密钥建议用环境变量（优先级更高，避免落盘）：`TRAVEL_PLANNER_API_KEY=sk-...`
3. 重启应用，顶栏出现「AI 已配置」。

安全与质量边界：

- 密钥只注入请求头，**不出现在任何日志、错误信息与页面响应中**；
- 模型输出按白名单 schema 严格校验（未知字段拒绝、类型枚举、天数边界）；
- 生成的草稿先预览、可剔除微调，点「导入」才写入行程（条目来源标记 `ai`）；
- 超时/断网/返回垃圾时给出中文降级提示，不影响核心功能。

## 导入导出

- 导出：行程详情页「导出」单行程 JSON；顶栏「全量导出」打包全部行程。
- 导入：顶栏「导入」上传 JSON → 校验 → 预览（含 id 冲突说明）→ 确认写入。

## 开发与测试

```powershell
pip install -e .[dev]
pytest --cov=travel_planner --cov-report=term   # 关键模块 ≥90%，整体 ≥80%
ruff check src tests
python -m build --wheel                          # scikit-build-core 纯 Python 包
```

约束：禁止 `__future__` 导入（Python 3.14 全默认，含 PEP 649）；Conventional Commits 中文主体。

## 技术栈与依赖

| 依赖 | 用途 |
|---|---|
| fastapi / uvicorn / jinja2 / python-multipart | Web 框架、SSR、表单解析 |
| httpx | 仅 AI 层（OpenAI 兼容端点调用） |
| pyyaml | 仅配置文件 |

构建后端：scikit-build-core（仓库对 `apps/*` 可安装 Python 子项目的统一约定）。
