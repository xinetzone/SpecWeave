---
id: "task5-output"
title: "Minitest Ecosystem Deep Analysis - Task 5: DevOps Infrastructure & Development Standards"
source: "task5"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task5-output.toml"
---
# Minitest 生态系统深度分析 - Task 5: DevOps 基础设施与开发规范

## 1. renovate-config 依赖更新配置分析

### 1.1 文件结构

```
renovate-config/
├── .git/
├── .gitignore
├── README.md
└── default.json
```

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/renovate-config/](file:///d:/AI/.chaos/libs/minitap-ai/renovate-config/)*

### 1.2 default.json 完整配置

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/renovate-config/default.json](file:///d:/AI/.chaos/libs/minitap-ai/renovate-config/default.json)*

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:best-practices",
    "group:monorepos",
    "group:recommended",
    ":automergeMinor",
    ":automergeDigest",
    ":automergeBranch"
  ],
  "prConcurrentLimit": 5,
  "minimumReleaseAge": "14 days",
  "schedule": [
    "before 12pm on tuesday",
    "before 12pm on wednesday",
    "before 12pm on thursday"
  ],
  "vulnerabilityAlerts": {
    "prPriority": 10,
    "schedule": [],
    "minimumReleaseAge": null,
    "labels": ["security"]
  },
  "packageRules": [
    {
      "description": "Automerge patch, pin and digest updates",
      "matchUpdateTypes": ["patch", "pin", "digest"],
      "automerge": true
    },
    {
      "description": "Automerge minor and patch devDependency updates",
      "matchDepTypes": ["devDependencies"],
      "matchUpdateTypes": ["minor", "patch"],
      "automerge": true
    },
    {
      "description": "Automerge GitHub Actions updates",
      "matchManagers": ["github-actions"],
      "automerge": true
    },
    {
      "description": "Never automerge majors; flag for manual review",
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "addLabels": ["breaking-change-review"]
    }
  ]
}
```

### 1.3 extends 配置分析

继承了 6 个预设配置：

| 预设 | 说明 |
|------|------|
| `config:best-practices` | Renovate 官方最佳实践配置集 |
| `group:monorepos` | Monorepo 包分组更新策略 |
| `group:recommended` | 推荐的包分组规则 |
| `:automergeMinor` | 次要版本自动合并预设 |
| `:automergeDigest` | Docker digest 更新自动合并预设 |
| `:automergeBranch` | 自动合并分支而非直接提交到主分支 |

### 1.4 prConcurrentLimit: 5 并发限制

将每个仓库的并发 Renovate PR 上限设置为 **5 个**（默认为 10 个），避免 PR 队列堆积，保持代码审查队列可控。

### 1.5 minimumReleaseAge: 14 天冷却期

- **常规更新**：依赖发布后等待 **14 天** 才提出更新 PR，有效规避 day-0 发布版本中可能存在的 bug
- **安全更新**：在 `vulnerabilityAlerts` 配置中设置 `minimumReleaseAge: null`，绕过冷却期立即处理

### 1.6 schedule: 周二至周四开窗

```json
"schedule": [
  "before 12pm on tuesday",
  "before 12pm on wednesday",
  "before 12pm on thursday"
]
```

仅在**周二、周三、周四中午 12 点前**创建更新 PR：
- 周一保持安静（避免周末堆积的更新周一涌入）
- 周五不创建 PR（避免周五合并后周末出问题无人处理）
- 为团队预留充足的工作日时间进行审查和验证

### 1.7 automerge 分级策略

采用四级风险分级自动合并策略：

| 风险级别 | 更新类型 | 自动合并 | 说明 |
|---------|---------|---------|------|
| **极低风险** | `patch` / `pin` / `digest` | ✅ 是 | 补丁版本、版本锁定、Docker digest 更新 |
| **低风险** | devDependencies 的 `minor` + `patch` | ✅ 是 | 开发依赖的小版本和补丁更新（不影响生产运行时） |
| **低风险** | GitHub Actions 更新 | ✅ 是 | CI/CD Action 更新 |
| **高风险** | `major` 主版本更新 | ❌ 否 | 添加 `breaking-change-review` 标签，人工审查 |

### 1.8 安全漏洞高优先级策略

`vulnerabilityAlerts` 配置：
- `prPriority: 10`：最高优先级 PR
- `schedule: []`：不受常规时间窗口限制，立即创建
- `minimumReleaseAge: null`：绕过 14 天冷却期
- `labels: ["security"]`：标记安全标签便于识别

### 1.9 major 版本不自动合并 + breaking-change-review 标签

主版本（major）更新策略：
- `automerge: false`：禁止自动合并
- `addLabels: ["breaking-change-review"]`：自动添加标签，提醒团队进行破坏性变更审查

---

## 2. devops-common 共享 DevOps 资源分析

### 2.1 完整文件结构

```
devops-common/
├── .git/
├── .github/
│   └── actions/
│       ├── affected-pytest/
│       │   └── action.yml
│       ├── argocd-deploy/
│       │   └── action.yml
│       ├── aws-codeartifact-token/
│       │   └── action.yml
│       ├── check-tag-version/
│       │   └── action.yml
│       ├── deployment-setup/
│       │   └── action.yml
│       ├── dockerhub-build-push/
│       │   └── action.yml
│       ├── gcp-docker-build-push/
│       │   └── action.yml
│       ├── gcp-helm-chart-publish/
│       │   └── action.yml
│       ├── latest-tag-info/
│       │   └── action.yml
│       ├── python-migrate/
│       │   └── action.yml
│       ├── setup-go-private/
│       │   └── action.yml
│       └── update-chart-app-version/
│           └── action.yml
├── .gitignore
├── README.md
└── renovate.json
```

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/)*

### 2.2 README.md 概览

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/README.md](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/README.md)*

devops-common 仓库包含 Minitap 项目间共享的 DevOps 资源，主要是可复用的 GitHub Actions。所有 Action 均使用 `composite` 类型实现。

### 2.3 GitHub Actions 完整清单

| Action 名称 | 功能说明 | 文件引用 |
|------------|---------|---------|
| setup-go-private | 配置 Go 环境并设置私有模块访问 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/setup-go-private/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/setup-go-private/action.yml) |
| gcp-docker-build-push | GCP Artifact Registry Docker 构建推送 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/gcp-docker-build-push/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/gcp-docker-build-push/action.yml) |
| dockerhub-build-push | DockerHub 镜像构建推送 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/dockerhub-build-push/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/dockerhub-build-push/action.yml) |
| affected-pytest | 受影响测试选择性执行 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/affected-pytest/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/affected-pytest/action.yml) |
| aws-codeartifact-token | AWS CodeArtifact 认证令牌获取 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/aws-codeartifact-token/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/aws-codeartifact-token/action.yml) |
| argocd-deploy | ArgoCD 部署同步与健康等待 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/argocd-deploy/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/argocd-deploy/action.yml) |
| python-migrate | Python 数据库迁移执行 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/python-migrate/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/python-migrate/action.yml) |
| check-tag-version | 标签版本与预期版本校验 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/check-tag-version/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/check-tag-version/action.yml) |
| deployment-setup | 基于 Git ref 确定部署环境和标签 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/deployment-setup/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/deployment-setup/action.yml) |
| gcp-helm-chart-publish | GCP Helm Chart 发布 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/gcp-helm-chart-publish/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/gcp-helm-chart-publish/action.yml) |
| latest-tag-info | 获取最新标签及其作者信息 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/latest-tag-info/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/latest-tag-info/action.yml) |
| update-chart-app-version | 更新 ArgoCD 仓库 Chart 版本 | [file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/update-chart-app-version/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/update-chart-app-version/action.yml) |

### 2.4 affected-pytest 选择性测试策略深度分析

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/affected-pytest/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/affected-pytest/action.yml)*

#### 2.4.1 核心机制

基于 [`pytest-impacted`](https://github.com/promptromp/pytest-impacted) 插件，通过 **git diff + AST 导入图分析** 仅运行 PR 变更影响的测试用例。

#### 2.4.2 双模式运行策略

| 事件类型 | 测试范围 | 行为 |
|---------|---------|------|
| **`pull_request`** | 受影响测试 | 使用 `--impacted` 模式，基于 base ref 进行分支差异分析 |
| **其他事件**（如 push 到 main） | 全量测试 | 安全网策略，运行完整测试套件 |

**关键代码（全量测试分支）：**
```yaml
- name: Run full test suite (non-PR safety net)
  if: github.event_name != 'pull_request'
  shell: bash
  run: |
    set -euo pipefail
    echo "::notice::Running FULL pytest suite (event: ${{ github.event_name }})"
    ${{ inputs.pre-test || 'true' }}
    uv run pytest ${{ inputs.pytest-args }}
```

**关键代码（受影响测试分支）：**
```yaml
- name: Run affected tests (pull request)
  if: github.event_name == 'pull_request'
  shell: bash
  run: |
    # ... 确保 base ref 存在 ...
    uv run pytest \
      --impacted \
      --impacted-module="${{ inputs.impacted-module }}" \
      --impacted-git-mode=branch \
      --impacted-base-branch="origin/${BASE_REF}" \
      $TESTS_DIR_ARG \
      ${{ inputs.pytest-args }}
```

#### 2.4.3 Force-all 强制全量触发条件

`pytest-impacted` 插件内置智能强制全量运行规则：

| 触发条件 | 行为 | 原因 |
|---------|------|------|
| 依赖文件变更（`uv.lock`、`pyproject.toml` 等） | 运行**所有**测试 | 依赖变更可能影响所有模块 |
| `conftest.py` 变更 | 运行该目录下**所有**测试 | conftest.py 影响目录内所有测试的 fixture 配置 |

#### 2.4.4 无受影响测试处理

退出码 `5` 表示"未收集到测试"（即没有受影响的测试），Action 将其视为成功：

```bash
if [ "$code" -eq 5 ]; then
  echo "::notice::No affected tests for this change (pytest exit 5) — passing."
  exit 0
fi
```

#### 2.4.5 Inputs 参数

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `impacted-module` | ✅ 是 | — | 目标模块路径：src-layout 需带 `src/` 前缀，flat-layout 用包名 |
| `tests-dir` | ❌ 否 | `tests` | 测试目录 |
| `base-ref` | ❌ 否 | `main` | PR 对比基准分支 |
| `pytest-args` | ❌ 否 | 空 | 附加 pytest 参数（如 marker 过滤） |
| `pre-test` | ❌ 否 | 空 | 测试前执行的 shell 命令（如环境准备） |

### 2.5 gcp-docker-build-push 分支/标签 tagging 策略深度分析

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/gcp-docker-build-push/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/gcp-docker-build-push/action.yml)*

#### 2.5.1 自动标签策略逻辑

镜像标签基于 Git 引用类型自动确定：

```bash
if [ ! -z "$IMAGE_TAG" ]; then
  # 1. 显式指定 image-tag input：使用用户提供的标签（支持多行多标签）
elif [[ "${GITHUB_REF_TYPE}" == "tag" && "${GITHUB_REF_NAME}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  # 2. SemVer 标签（如 v1.2.3）：使用标签名作为镜像标签
  TAGS="$IMAGE:${GITHUB_REF_NAME}"
elif [[ "${GITHUB_REF_NAME}" == "main" ]]; then
  # 3. main 分支：标签为 latest
  TAGS="$IMAGE:latest"
elif [[ "${GITHUB_REF_NAME}" == "development" ]]; then
  # 4. development 分支：标签为 dev
  TAGS="$IMAGE:dev"
else
  # 5. 其他分支：跳过构建
  echo "No matching condition for build, skipping."
  exit 0
fi
```

#### 2.5.2 标签策略总结

| Git 引用 | 镜像标签 | 环境 | 说明 |
|---------|---------|------|------|
| 显式 `image-tag` input | 用户自定义 | 任意 | 支持多行（换行分隔）指定多个标签 |
| SemVer tag (`vX.Y.Z`) | `vX.Y.Z` | 生产 | 正式发布版本 |
| `main` 分支 | `latest` | 生产候选 | 主分支最新代码 |
| `development` 分支 | `dev` | 开发 | 开发分支最新代码 |
| 其他分支 | （跳过） | — | 不构建，避免镜像泛滥 |

#### 2.5.3 构建缓存策略

使用 GCP Artifact Registry 作为构建缓存源：
- `cache-from: type=registry,ref=${{ steps.vars.outputs.cache-image }}`：从 registry 拉取缓存
- `cache-to: type=registry,ref=${{ steps.vars.outputs.cache-image }},mode=max`：缓存所有层到 registry
- 缓存镜像名为 `<image>:buildcache`（可通过 `cache-key` 添加后缀区分）

#### 2.5.4 私有模块访问

构建时创建临时 `.netrc` 文件用于访问私有 Go 模块：
```bash
echo -e "machine github.com\nlogin ${GITHUB_ACTOR}\npassword ${GITHUB_TOKEN}" > $HOME/.netrc
chmod 600 $HOME/.netrc
```
通过 BuildKit secret 挂载到构建中，构建结束后自动清理。

### 2.6 其他 Action 简要分析

#### 2.6.1 setup-go-private

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/setup-go-private/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/setup-go-private/action.yml)*

- 使用 `actions/setup-go@v5`，从 `go.mod` 读取 Go 版本
- 配置 Git `insteadOf` 将 GitHub URL 替换为带 token 的认证 URL
- 设置 `GOPRIVATE=github.com/minitap-ai/*` 跳过私有模块的公共校验和数据库

#### 2.6.2 dockerhub-build-push

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/dockerhub-build-push/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/dockerhub-build-push/action.yml)*

- 与 GCP 版本类似的标签策略
- 默认支持多平台构建：`linux/amd64,linux/arm64`
- 默认额外推送 `latest` 标签（可通过 `push-latest: false` 关闭）

#### 2.6.3 deployment-setup

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/deployment-setup/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/deployment-setup/action.yml)*

智能确定部署环境：
- **Tag 推送**：`environment=prod`，`image_tag=<tag>`，从标签提取作者信息
- **分支推送**：`environment=dev`，`image_tag=<commit-sha>`，从 commit 提取作者信息
- 输出 `commit_author` 和 `commit_email` 用于 ArgoCD 提交

#### 2.6.4 argocd-deploy

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/argocd-deploy/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/argocd-deploy/action.yml)*

完整 GitOps 部署流程：
1. Checkout ArgoCD 配置仓库
2. 使用 `yq` 更新 `Chart.yaml` 的 `appVersion`
3. 对于 subchart 模式，更新 `values.yaml` 中的 `<app-name>.image.tag`
4. 提交并推送变更（如有）
5. 安装 ArgoCD CLI
6. 触发 `argocd app sync` 并等待健康状态（默认超时 300 秒）
7. 输出部署摘要到 GitHub Step Summary

#### 2.6.5 python-migrate

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/python-migrate/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/python-migrate/action.yml)*

Python 项目数据库迁移标准化：
1. 安装 uv
2. `uv python install` 安装 Python
3. `uv sync` 同步依赖（支持私有包索引 token）
4. 执行 `uv run migrate` 运行迁移
5. 支持 `extra-env` 传入多行环境变量

#### 2.6.6 gcp-helm-chart-publish

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/gcp-helm-chart-publish/action.yml](file:///d:/AI/.chaos/libs/minitap-ai/devops-common/.github/actions/gcp-helm-chart-publish/action.yml)*

Helm Chart 发布到 GCP Artifact Registry（OCI 格式）：
1. 认证 GCP
2. 安装 Helm 3
3. `helm dependency update` 更新依赖
4. `helm package` 打包 Chart
5. `helm push` 推送到 OCI 仓库

---

## 3. minitest-cli 与 minitest-trigger 开发规范汇总

### 3.1 minitest-cli (Python) 开发规范

*来源：[file:///d:/AI/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task2-output.md](file:///d:/AI/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task2-output.md)*

#### 3.1.1 代码质量工具链

| 工具 | 用途 | 配置 |
|------|------|------|
| **ruff** | Lint + Format | line-length=100, indent-width=4, target-version=py312, quote-style="double" |
| **pyright** | 静态类型检查 | pyrightconfig.json 严格配置 |
| **pytest** | 单元测试 | 测试覆盖率要求 80%+，关键模块 90%+ |

常用命令：
```bash
uv run ruff check .      # Lint
uv run ruff format .     # Format
uv run pyright           # Type check
uv run pytest            # Test
```

#### 3.1.2 导入规范

- **绝对导入强制**：ruff 配置 `ban-relative-imports = "all"`，禁止相对导入
- **导入顺序**：标准库 → 第三方 → 本地导入
- 所有导入位于文件顶部

#### 3.1.3 文件长度限制

- **目标：文件 < 150 行**（"Keep files under 150 lines when possible"）
- 实现方式：业务逻辑拆分到 `*_helpers.py` 文件
- 示例：`run.py` 保持精简（约 190 行），核心逻辑拆分到 `run_helpers.py`、`run_display.py`、`run_targets.py`

#### 3.1.4 类型注解规范

- 使用 `X | None` 语法（Python 3.10+ 风格，而非 `Optional[X]`）
- Typer 参数使用 `Annotated[Type, ...]` 包装
- 枚举继承自 `str, Enum`（即 `StrEnum`）

#### 3.1.5 命名规范

| 类型 | 规范 |
|------|------|
| 文件/模块 | `snake_case.py` |
| 类 | `PascalCase` |
| 函数/变量 | `snake_case` |
| 常量 | `UPPER_SNAKE_CASE` |
| 测试文件 | `test_*.py` |
| 测试函数 | `test_<action>_<scenario>` |

#### 3.1.6 输出约定

- `--json` 模式：JSON 到 stdout，诊断到 stderr
- 非 `--json` 模式：Rich 表格到 stdout，诊断到 stderr
- stdout/stderr 分离：`err_console = Console(stderr=True)` 用于诊断，`console = Console()` 用于数据
- 禁止交互式提示，所有输入通过 flags、env vars 或 stdin

### 3.2 minitest-trigger (TypeScript) 开发规范

*来源：[file:///d:/AI/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task3-output.md](file:///d:/AI/.trae/specs/retrospectives-insights/minitest-ecosystem-deep-analysis/task3-output.md)*

#### 3.2.1 TypeScript 严格模式

- 启用 TypeScript `strict` 模式
- 编译目标：ES2022
- 模块系统：CommonJS
- Runtime：Node.js 20

#### 3.2.2 ESLint flat config

- 使用 ESLint 新版 flat config（`eslint.config.mjs`）
- 配合 `typescript-eslint` 进行 TypeScript 代码检查
- 命令：`npm run lint` 执行检查

#### 3.2.3 Prettier 格式化

- **无分号**（semicolons: false）
- **单引号**（single quotes: true）
- 格式化命令：`npm run format`（写入）、`npm run format:check`（检查）

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/.prettierrc](file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/.prettierrc)*

#### 3.2.4 ncc 单文件打包

- 使用 `@vercel/ncc` 将所有代码和依赖打包为单文件 `dist/index.js`
- 打包命令：`ncc build src/main.ts --source-map --license licenses.txt`
- `dist/` 目录在 `.gitignore` 中忽略，仅由 release workflow 在发布时构建提交
- 发布时自动构建并强制提交 dist 目录，同时更新主版本标签（v1）

#### 3.2.5 npm scripts 完整流水线

| Script | 命令 | 说明 |
|--------|------|------|
| `build` | `tsc` | TypeScript 编译 |
| `bundle` | `ncc build src/main.ts --source-map --license licenses.txt` | ncc 单文件打包 |
| `lint` | `eslint src/` | ESLint 检查 |
| `format` | `prettier --write 'src/**/*.ts'` | Prettier 格式化 |
| `format:check` | `prettier --check 'src/**/*.ts'` | Prettier 格式检查 |
| `all` | `build && lint && format:check && bundle` | 全量检查+打包（CI 使用） |

---

## 4. 生态系统一致性总结

### 4.1 工具链标准化

| 领域 | 工具选择 | 应用范围 |
|------|---------|---------|
| Python 包管理 | uv | minitest-cli, devops-common (python-migrate) |
| Python Lint/Format | ruff | minitest-cli |
| Python 类型检查 | pyright | minitest-cli |
| Python 测试 | pytest + pytest-impacted | minitest-cli, affected-pytest Action |
| TypeScript 编译 | tsc (strict) | minitest-trigger |
| TypeScript Lint | ESLint flat config | minitest-trigger |
| TypeScript Format | Prettier (无分号单引号) | minitest-trigger |
| TypeScript 打包 | @vercel/ncc | minitest-trigger |
| 依赖更新 | Renovate (14天冷却期, 分级自动合并) | 所有仓库 |

### 4.2 DevOps 最佳实践

1. **测试优化**：PR 选择性测试 + main 全量测试的双层策略，兼顾速度与安全
2. **镜像标签**：基于 Git ref 自动化标签策略，语义化版本 + 环境区分（latest/dev）
3. **依赖更新**：分级自动合并 + 冷却期 + 安全漏洞高优先级，平衡更新频率与稳定性
4. **发布流程**：ncc 单文件打包 + 自动 dist 提交 + 主版本浮动标签，GitHub Action 用户体验友好
5. **GitOps**：ArgoCD 标准化部署流程，支持 subchart 模式，自动同步等待健康状态

### 4.3 代码质量门禁

| 检查项 | Python 项目 | TypeScript 项目 |
|--------|------------|----------------|
| 编译/类型检查 | pyright | tsc --strict |
| Lint | ruff check | eslint |
| 格式检查 | ruff format --check | prettier --check |
| 打包 | - | ncc bundle |
| 测试 | pytest (affected/full) | - |
| 执行顺序 | ruff → pyright → pytest | tsc → eslint → prettier:check → ncc |
