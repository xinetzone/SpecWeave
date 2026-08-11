---
id: "variants-build-orchestration"
title: "镜像变体构建编排规范"
source: "variants/build.sh, variants/shared/lib/logging.sh"
---
# 镜像变体构建编排规范

本文件定义 `variants/build.sh` 统一构建脚本的使用方式、数据格式和行为约定。

## VARIANTS 数组格式

变体定义在 build.sh 顶部的 `VARIANTS` 数组中，使用 **`|` 管道符** 作为字段分隔符（禁止使用 `:`，因为验证命令中可能包含路径）：

```bash
VARIANTS=(
    "<name>|<description>|<dependencies>|<validation-commands>"
)
```

| 字段 | 说明 | 格式 |
|------|------|------|
| name | 变体名称，必须与目录名一致 | 小写+连字符，如 `conda-llvm` |
| description | 一句话中文描述 | 简洁说明，如 `conda+LLVM/clang编译工具链` |
| dependencies | 依赖的变体名 | 逗号分隔多个依赖；无依赖留空字符串 |
| validation-commands | 构建后验证命令 | 分号 `;` 分隔多条 shell 命令 |

**示例**：
```bash
"conda|Miniconda3基础环境||/opt/conda/bin/conda --version;/opt/conda/bin/conda info --envs"
"conda-llvm|conda+LLVM/clang编译工具链|conda|/opt/conda/bin/clang++ --version"
```

### 字段分隔符选择原则

- 首选 `|` 作为字段分隔符（验证命令中的路径不含 `|`）
- 验证命令之间用 `;` 分隔
- 依赖变体之间用 `,` 分隔
- **禁止**使用 `:` 作为字段分隔符（与路径中的 `:` 冲突）

## 构建流程

build.sh 的执行流程：

1. **参数解析**：支持 `--list`/`--variant`/`--all`/`--cn`/`--no-cache`/`--tag`/`--build-arg`
2. **变体注册**：`parse_variants()` 解析 VARIANTS 数组到关联数组
3. **拓扑排序**：`topological_sort()` 基于依赖关系计算构建顺序（Kahn算法）
4. **依赖检查**：`check_dependency_image()` 确认基础镜像或依赖变体镜像已存在
5. **逐变体构建**：`build_variant()` 执行 docker build，输出到日志文件
6. **阶段计时解析**：`parse_timer_logs()` 从日志中提取 `[TIMER]` 标记
7. **逐条验证**：`validate_variant()` 逐条执行验证命令，60s 超时
8. **汇总输出**：构建/验证结果表格

## 构建参数传递

所有构建变体接收统一的构建参数：

| 参数 | 默认值 | --cn 预设 | 说明 |
|------|-------|-----------|------|
| `APT_MIRROR` | `official` | `aliyun` | APT 源 |
| `CONDA_MIRROR` | `official` | `tuna` | Conda 源 |
| `PIP_MIRROR` | `official` | `aliyun` | Pip 源 |
| `BASE_TAG` | `latest` | 同 TAG | 基础镜像标签后缀 |
| `BUILDKIT_INLINE_CACHE` | `1` | 不变 | BuildKit 内联缓存 |

额外参数通过 `--build-arg KEY=VALUE` 传递，透传给所有变体的 docker build。

## 日志与计时规范

### 日志库

所有变体脚本必须 source 共享日志库：
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/shared/lib/logging.sh"
LOG_SERVICE="<service-name>"
```

### Dockerfile [TIMER] 标记

每个变体 Dockerfile 必须在关键阶段输出 `[TIMER]` 标记，格式：

```dockerfile
RUN _STAGE_START=$(date +%s) && \
    echo "[TIMER] Stage N/M: <description> started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    # ... 执行构建步骤 ... && \
    _ELAPSED=$(( $(date +%s) - _STAGE_START )) && \
    echo "[TIMER] Stage N/M: <description> took ${_ELAPSED}s"
```

build.sh 的 `parse_timer_logs()` 会自动解析这些标记，生成阶段耗时表格。

### 构建日志输出

- 使用 `--progress=plain` 输出详细构建日志
- 日志同时输出到控制台和 `/tmp/variants-build-{variant}-{timestamp}.log`
- 构建开始/结束打印 ASCII 横幅（`╔═╗║║╚═╝`）
- 验证逐条输出 `PASS`/`FAIL`/`TIMEOUT`

## 验证机制

### 验证命令格式

验证命令在容器内以 `bash -c "<cmd>"` 执行：
- 命令以分号 `;` 分隔，逐条执行
- 单条命令超时 60 秒（使用 `timeout` 命令）
- 每条命令独立报告结果，不短路
- 最终统计 `pass_count/total_count PASS`

### 镜像命名约定

| 镜像类型 | 标签格式 |
|---------|---------|
| 基础镜像 | `devcontainer-base:<TAG>` |
| 变体镜像 | `devcontainer-base:<variant>-<TAG>` |

默认 TAG 为 `latest`，通过 `--tag` 参数指定。

## 独立构建脚本约定

`variants/scripts/` 目录下可放置单变体一键构建脚本，命名格式 `build-<variant>.sh`：

- 必须 source 共享日志库
- 检查 Docker daemon 可用性
- 链式检查依赖镜像（base → deps → target），缺失时给出明确构建指引
- 支持 `--official`/`--no-cache`/`--tag`/`--skip-build` 参数
- 构建完成后自动运行对应测试脚本 `test-<variant>.sh`
- 输出最终报告（镜像名、大小、快速版本验证）
