---
id: "variants-new-variant-guide"
title: "新增镜像变体操南"
source: "variants/_template/, variants/README.md"
---
# 新增镜像变体操南

本文件描述如何基于 `_template/` 模板创建新的镜像变体，以及新增后的注册和验证流程。

## 前置条件

1. 基础镜像 `devcontainer-base:latest` 已成功构建
2. 理解 [变体共享约定](variant-conventions.md)（FROM 模式、PATH 优先级、禁止覆盖项）
3. 理解 [构建编排规范](build-orchestration.md)（VARIANTS 数组格式、验证命令格式）
4. 理解 [测试规范](testing.md)（6层测试策略）

## 新增步骤（7步）

### Step 1: 复制模板目录

```bash
cd apps/docker-images/devcontainer-base
cp -r variants/_template variants/<variant-name>
```

变体命名规范：
- 小写字母 + 连字符（kebab-case）
- 描述主要功能，如 `cuda`、`rocm`、`pytorch`、`nodejs`
- 避免与已有变体重名：`conda`、`conda-llvm`

### Step 2: 修改 Dockerfile

编辑 `variants/<variant-name>/Dockerfile`，替换所有 `__XXX__` 占位符：

| 占位符 | 替换为 | 说明 |
|--------|-------|------|
| `__VARIANT_NAME__` | 变体名称 | 如 `cuda`，用于 ARG/LABEL/元数据 |
| `__VARIANT_DESCRIPTION__` | 一句话中文描述 | 如 `CUDA 12.x GPU计算环境` |
| `__BASE_VARIANT__` | 基础变体前缀 | 直接基于基础镜像留空；基于 conda 填 `conda-`；基于 conda-llvm 填 `conda-llvm-` |
| `__EXTRA_BUILD_ARGS__` | 额外 ARG 声明 | 如 `ARG CUDA_VERSION=12.4.0` |
| `__EXTRA_INSTALL_STEPS__` | 自定义安装 RUN 指令 | 核心安装逻辑，含 [TIMER] 标记 |
| `__EXTRA_VALIDATION__` | 额外验证命令 | 在 [VALIDATION CHECKPOINT] 中追加验证项 |

**Dockerfile 检查清单**：
- [ ] 首行 `# syntax=docker/dockerfile:1.7-labs`
- [ ] FROM 语句正确使用 `${BASE_TAG}` 和 `__BASE_VARIANT__` 前缀
- [ ] FROM 后有 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- [ ] 未覆盖 ENTRYPOINT/CMD/WORKDIR/USER
- [ ] 安装步骤有 `[TIMER]` 标记
- [ ] 使用 `--mount=type=cache` 缓存挂载
- [ ] 末尾有 `[VALIDATION CHECKPOINT]` 包含基础服务继承验证
- [ ] 有构建元数据写入 `/etc/devcontainer-variant-<name>-build-info`

### Step 3: 更新配置文件

**`.env.example`**：添加变体特有参数
```ini
# <variant-name> 变体参数
<PARAM_NAME>=default_value
```

**`README.md`**：更新为变体实际内容
- 变体描述和功能列表
- 构建命令示例
- 验证方式
- 使用说明（如何在容器中激活/使用该变体提供的工具）

### Step 4: 创建变体规则文件

创建/更新 `variants/<variant-name>/.agents/rules/dockerfile.md`，记录变体特有规范：

参考 conda 变体的 dockerfile.md 结构，包含：
- 基础信息（基础镜像、安装路径、核心组件版本）
- 核心约束（PATH 配置、环境变量、激活方式）
- 追加阶段结构（每个 Stage 的详细说明）
- 构建参数表
- 服务继承说明
- 日志/输出规范

### Step 5: 在 build.sh 中注册

在 `variants/build.sh` 的 `VARIANTS` 数组中添加变体定义：

```bash
"<name>|<description>|<deps>|<validation-commands>"
```

**示例**：
```bash
"cuda|CUDA 12.x GPU计算环境||nvidia-smi|||nvcc --version"
"pytorch|PyTorch GPU训练环境|conda,cuda|python -c 'import torch;print(torch.__version__,torch.cuda.is_available())'"
"ai-dev|AI/ML/NLP全栈环境|onnx-quantized|/opt/conda/envs/main/bin/python -c \"import torch;print(torch.__version__)\"|||/opt/conda/envs/main/bin/jupyter lab --version"
```

注意：
- 字段分隔符是 `|`（管道符），不是 `:`
- **验证命令之间用 `|||`（三管道）分隔**，禁止使用 `;`（会被Python `-c "a;b"` 等命令内部分号误分割）
- 依赖变体之间用 `,` 分隔
- 无依赖时第三个字段留空（连续两个 `||`）
- 验证命令中包含Python单行多语句（含`;`）时，`|||`分隔符可正确处理

### Step 6: 创建测试脚本

创建 `variants/scripts/test-<variant-name>.sh`，遵循 [测试规范](testing.md)：
- 至少包含 15+ 测试用例，覆盖 L1-L6 六个层级
- L1: 所有核心工具版本检查
- L2: 至少 1 个 Hello World 功能测试
- L3: 2+ 深度组件验证
- L4: 5 项基础服务继承测试
- L5: PATH 优先级和环境隔离验证
- L6: 配置文件验证

**可选**：创建一键构建脚本 `variants/scripts/build-<variant-name>.sh`，参考 `build-conda-llvm.sh` 模式。

### Step 7: 在 variants/README.md 中注册

在可用变体表格中添加新条目：
```markdown
| <variant-name> | <description> | <base-image> | <extra-components> |
```

## 构建与验证

完成以上步骤后，执行构建验证：

```bash
# 列出变体，确认注册成功
bash variants/build.sh --list

# 构建新变体（国内源）
bash variants/build.sh --variant <variant-name> --cn

# 运行完整测试
bash variants/scripts/test-<variant-name>.sh

# 一键构建+测试（如果有 build-<variant>.sh）
bash variants/scripts/build-<variant>.sh
```

## 新增后检查清单

- [ ] `bash variants/build.sh --list` 显示新变体
- [ ] 构建成功，无错误
- [ ] `[TIMER]` 阶段计时在构建日志中正确显示
- [ ] build.sh 快速验证全部 PASS
- [ ] `test-<variant>.sh` 全部测试 PASS
- [ ] 基础服务测试（ssh/supervisord/docker/jupyter/devuser）通过
- [ ] PATH 优先级验证通过（默认 python 是 /opt/venv/bin/python）
- [ ] README.md 已更新
- [ ] `.agents/rules/dockerfile.md` 已创建
- [ ] 新镜像可通过 docker run 正常启动
- [ ] `bash -n` 语法检查通过（Dockerfile/脚本）
