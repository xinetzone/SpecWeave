---
source:
  - ../../../.github/workflows/ci-quality-gates.yml
  - ../../../.github/workflows/docs-pages.yml
  - ../../../docs/tasks.py
  - ../../scripts/ci-check.ps1
  - ../../scripts/ci-check.sh
  - ../../scripts/docgen.py
  - ../../../apps/ai-agents/eve-minimal-agent/README.md
  - ../../../apps/ai-agents/eve-minimal-agent/package.json
  - ../../../apps/docker-images/jupyter-ssh-base/README.md
  - ../../../apps/tests/onnx_adaround/README.md
  - ../../../projects/xuanspace/README.md
  - ../../../projects/xuanspace/.github/workflows/ci.yml
  - ../../../vendor/flexloop/README.md
  - ../../../vendor/flexloop/apps/chaos/mise.toml
status: stable
updated_at: 2026-08-23
---

# 运行与验证指南

## 运行分层

这个仓库没有单一“启动命令”，常见运行入口分成 5 类：

1. 仓库治理命令
2. 文档站构建命令
3. `apps/` 中示例或应用命令
4. `projects/` 中子项目命令
5. `vendor/` 中外部协作项目命令

## 环境矩阵

| 场景 | 必需工具 | 依据 |
|---|---|---|
| 运行主仓脚本 | Python、Git | `.agents/scripts/` |
| 跑全仓检查 | Python、PowerShell 7 或 Bash | [`ci-check.ps1`](../../scripts/ci-check.ps1) / [`ci-check.sh`](../../scripts/ci-check.sh) |
| 构建文档站 | Python、Sphinx、invoke | [docs/tasks.py](../../../docs/tasks.py#L54-L128) |
| 运行 Node 应用 | Node.js 24+ | [eve-minimal-agent/package.json](../../../apps/ai-agents/eve-minimal-agent/package.json#L26-L28) |
| 运行 Docker 镜像示例 | Docker / Podman / Compose | `apps/docker-images/*` |
| 运行子项目 | 各子项目自己的 Python/工具链 | `projects/`、`vendor/` |

## 仓库级常用命令

### 全量检查

Windows PowerShell 7:

```powershell
.\.agents\scripts\ci-check.ps1
```

Linux / macOS:

```bash
bash ./.agents/scripts/ci-check.sh
```

这两条命令分别来自：

- [ci-check.ps1](../../scripts/ci-check.ps1#L1-L357)
- [ci-check.sh](../../scripts/ci-check.sh#L1-L219)

### 文档导航与看板生成

```powershell
python .agents\scripts\docgen.py nav
python .agents\scripts\docgen.py dashboard
python .agents\scripts\docgen.py apps
python .agents\scripts\docgen.py all
```

来源见 [docgen.py](../../scripts/docgen.py#L1-L17)。

### 常用检查器

```powershell
python .agents\scripts\repo-check.py all
python .agents\scripts\check-links.py
python .agents\scripts\build-ref-index.py --stats
```

## 文档站构建

### 安装依赖

```powershell
python -m pip install -r docs\requirements.txt
```

来源见 [docs-pages.yml](../../../.github/workflows/docs-pages.yml#L35-L39)。

### 本地构建

```powershell
cd docs
invoke html
invoke linkcheck
invoke doctest
invoke clean
```

这些任务最终都转发到 [docs/tasks.py](../../../docs/tasks.py#L54-L128) 中的 `build/html/linkcheck/doctest/clean`。

## 测试与 CI

### 主仓脚本测试

CI 中运行的测试命令是：

```powershell
python -m pytest tests/ -v --tb=short --cov=. --cov-report=term
```

其工作目录是 `.agents/scripts/`，来源见 [ci-quality-gates.yml](../../../.github/workflows/ci-quality-gates.yml#L61-L64)。

### CI 中的其他关键检查

CI 还会运行：

```powershell
python .agents\scripts\repo-check.py all
python .agents\scripts\check-links.py
python .agents\scripts\docgen.py all
python .agents\scripts\generate-readme.py --check
```

来源见 [ci-quality-gates.yml](../../../.github/workflows/ci-quality-gates.yml#L65-L138)。

## `apps/` 代表性运行方式

### `eve-minimal-agent`

```bash
cd apps/ai-agents/eve-minimal-agent
npm install
npm run dev
npm run build
npm run start
npm run typecheck
```

来源：

- [README.md](../../../apps/ai-agents/eve-minimal-agent/README.md#L22-L36)
- [package.json](../../../apps/ai-agents/eve-minimal-agent/package.json#L10-L15)

### `jupyter-ssh-base`

```bash
cd apps/docker-images/jupyter-ssh-base
bash scripts/build.sh
./run.sh run
docker compose up -d
docker compose logs -f
docker compose down
```

来源：

- [README.md](../../../apps/docker-images/jupyter-ssh-base/README.md#L42-L109)
- `scripts/build.sh`
- `run.sh`

### `onnx_adaround`

```powershell
cd apps\tests\onnx_adaround
pip install -e .
pip install -e ".[dev]"
python -m onnx_adaround --help
pytest --cov=onnx_adaround
ruff check onnx_adaround
```

来源见 [onnx_adaround/README.md](../../../apps/tests/onnx_adaround/README.md#L21-L79)。

## `projects/` 代表性运行方式

### `xuanspace`

常见安装方式：

```bash
cd projects/xuanspace
pdm install
pdm run xs --help
```

或：

```bash
pip install -e ".[dev]"
xs --help
```

或：

```bash
uv pip install -e ".[dev]"
xs --help
```

常见命令：

```bash
xs list
xs doctor
xs build
xs docs build
xs docs linkcheck
```

来源：

- [projects/xuanspace/README.md](../../../projects/xuanspace/README.md#L61-L91)
- [projects/xuanspace/.github/workflows/ci.yml](../../../projects/xuanspace/.github/workflows/ci.yml#L83-L133)

## `vendor/` 代表性运行方式

### `flexloop/apps/chaos`

```bash
cd vendor/flexloop/apps/chaos
uv sync --group dev --group docs
uv run pytest
mise run docs-html
mise run test
mise run lint
```

更完整的初始化序列：

```bash
mise trust
mise install
mise run sync
mise run init
mise run check-env
```

来源：

- [vendor/flexloop/README.md](../../../vendor/flexloop/README.md#L66-L81)
- `vendor/flexloop/docs/tech/quickstart.md`
- [mise.toml](../../../vendor/flexloop/apps/chaos/mise.toml#L19-L125)

## 按改动区域选择验证命令

| 你修改了哪里 | 建议优先运行 |
|---|---|
| `.agents/docs/` | `python .agents\scripts\check-links.py` |
| `.agents/scripts/` | `cd .agents\scripts && python -m pytest tests/ -v --tb=short` |
| `docs/` | `cd docs && invoke html && invoke linkcheck` |
| `.trae/specs/` | `python .agents\scripts\check-spec-consistency.py` |
| `apps/tests/onnx_adaround/` | `pytest --cov=onnx_adaround` |
| `projects/xuanspace/` | `xs doctor && xs docs build` |

## 使用提醒

- `apps/`、`projects/`、`vendor/` 各自有独立运行方式，不要假设全仓统一用同一套包管理器。
- 对于 submodule，先确认目录已初始化并与当前 checkout 同步。
- 运行仓库级脚本时，默认从仓库根目录执行最稳妥。
