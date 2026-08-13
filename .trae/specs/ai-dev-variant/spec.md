---
status: completed
updated_at: 2026-08-13
completion_note: "通过七概念方法论(R→I→E→C)复盘更新，同步Spec与实际实现"
---

# Spec: ai-dev 变体萃取

## 背景

从 `external/chaos/ai/portable.Dockerfile` 和 `docker-compose.yml` 中萃取通用的 AI/ML 全栈开发环境，作为 `devcontainer-base` 的新变体 `ai-dev`。

**实际实现完成状态**：已完成，test-ai-dev.sh 通过全部25项测试。

## 架构决策记录（实现与原规划差异）

| 规划项 | 实际实现 | 原因 |
|--------|---------|------|
| Jupyter 内核双注册（/opt/venv + /opt/conda） | 仅注册到 /opt/conda/share/jupyter/kernels/ai-dev/ | 从 onnx-quantized 变体开始，整个变体链已演进为 conda-only 架构，/opt/venv 已被移除 |
| 升级 /opt/venv 的 jupyterlab/notebook | 仅在 /opt/conda 环境安装 JupyterLab >=4.4 + notebook >=7.3 | conda-only 架构下无 /opt/venv |
| build.sh 验证命令用 `;` 分隔 | 使用 `\|\|\|`（三管道）分隔 | `;` 与 Python `-c "a;b"` 代码冲突导致解析错误，已演进为强制规范 |

## 源文件分析

### portable.Dockerfile 的通用能力（已萃取）
1. **Python AI/ML/NLP 生态系统**：50+ 个包，分14组安装（G1-G14），覆盖构建工具、NLP、数据处理、可视化、文档处理、数据库客户端、Web 框架
2. **PIP_USER 构建/运行时分离模式**：构建期 `PIP_USER=0` 写入 /opt/conda，最终层 `ENV PIP_USER=1` 支持用户级安装
3. **OpenMP 性能调优**：`OMP_NUM_THREADS=4`、`OPENBLAS_NUM_THREADS=1`、`OMP_WAIT_POLICY=PASSIVE`、`KMP_DUPLICATE_LIB_OK=TRUE`
4. **pip 镜像源配置**：支持 aliyun/tuna/official
5. **JupyterLab 升级**：>=4.4 + notebook>=7.3 解决 httpx 兼容性
6. **Jupyter 内核注册模式**：注册到 /opt/conda/share/jupyter/kernels/ai-dev/（conda-only 架构）
7. **BuildKit 缓存挂载**：conda/pkgs + root/.cache/pip
8. **pip_install_group() 可观测性安装**：分组安装+计时+冲突检测+失败诊断
9. **二进制优化**：strip 可执行文件 + 清理 __pycache__/.pyc
10. **[TIMER] 阶段计时**：每个Stage输出耗时，最终输出 BUILD TIMING SUMMARY 表

### portable.Dockerfile 的项目特有逻辑（不萃取）
1. 用户重命名 devuser→ai（项目特有用户策略）
2. NPU 专用 Jupyter 内核（PYTHONPATH 指向 /workspace/npu_tvm）
3. supervisord/sshd_config/docker daemon.json 配置修改
4. start.sh / chaos-ai-init.sh / fix-permissions.sh 脚本
5. umask 0027 安全策略
6. ENTRYPOINT=[] / CMD 覆盖（违反变体约定，实际实现未覆盖ENTRYPOINT）
7. /workspace/npu_tvm /workspace/npuusertools 项目目录
8. Docker-in-Docker 数据卷配置
9. sudoers NOPASSWD 配置（基础镜像已有）

### docker-compose.yml 的参考价值
- 资源限制（CPU/内存/shm_size）属于运行时编排，不属于变体镜像
- 卷挂载、端口映射、环境变量属于部署配置，不属于镜像构建
- 日志轮转配置属于运维编排

## 变体定义

| 属性 | 值 |
|------|-----|
| 变体名称 | `ai-dev` |
| 基础变体 | `onnx-quantized`（继承 conda→conda-llvm→onnx-pytorch→onnx-quantized 全链路） |
| 描述 | onnx-quantized + 完整AI/ML/NLP全栈Python生态（50+包）+ JupyterLab 4.x + 通用AI内核（conda-only架构） |
| 镜像名 | `devcontainer-base:ai-dev-${BASE_TAG}` |
| 架构 | conda-only（无/opt/venv） |

## 需求规格（已实现）

### R1: Dockerfile 结构
- ✅ 遵循变体共享约定（variant-conventions.md）
- ✅ 使用 3 层追加阶段
- ✅ 首行 `# syntax=docker/dockerfile:1.7-labs`
- ✅ FROM 后重置 SHELL `["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- ✅ 不覆盖 ENTRYPOINT/CMD/WORKDIR/USER/VOLUME/EXPOSE
- ✅ 每个阶段有 [TIMER] 标记
- ✅ 末尾有 [VALIDATION CHECKPOINT]
- ✅ 包含 LABEL maintainer/description/variant/ecosystem

### R2: Stage 1/3 - 基础验证 + 计时器
- ✅ 验证 onnx-quantized 基础组件（torch/onnx/onnxruntime/quantization）
- ✅ 验证 devuser 和基础服务（docker/supervisord）
- ✅ 验证 /opt/venv 已移除（conda-only架构）
- ✅ 初始化计时器文件 /tmp/.ai-dev-variant-build-timer

### R3: Stage 2/3 - Python 包安装
- ✅ 构建期设置 `PIP_USER=0`（确保写入 /opt/conda）
- ✅ 升级 pip/setuptools/wheel（带 --timeout 120 --retries 5）
- ✅ 使用 pip_install_group() 辅助函数分14组安装（G1-G14），含计时/冲突检测/诊断
- ✅ 包列表：
  - 构建工具：scikit-build-core, nuitka, invoke, build
  - 核心工具：decorator, attrs, cloudpickle, typing_extensions, pytest, psutil
  - Jupyter：ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3
  - 数据处理：pyarrow, pandas, scikit-learn, natsort
  - NLP/Transformers：datasets, transformers, sentencepiece, sentence-transformers, evaluate, tiktoken, onnx2torch
  - 可视化：matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich
  - AI/ML：einops, open_clip_torch, numba
  - 音频：librosa
  - 中文NLP：jieba, nltk, pypinyin
  - 文档处理：PyMuPDF, EbookLib, beautifulsoup4, openpyxl
  - Web/API：fastapi, uvicorn, httpx>=0.28, pydantic
  - 序列化：toml, typer, xmltodict, pyyaml
  - 数据库：psycopg2-binary, pymongo, elasticsearch, minio
  - 工具：icecream
- ✅ 使用 `--mount=type=cache` 缓存（conda/pkgs + pip cache）
- ✅ 二进制 strip 优化 + __pycache__/.pyc 清理
- ✅ 清理 conda/pip 缓存
- ✅ 输出33个核心包版本列表
- ✅ 最终执行 pip check 依赖一致性验证

### R4: Stage 3/3 - 配置 + 元数据 + 验证
- ✅ 最终层 `ENV PIP_USER=1`（运行时用户级安装）
- ✅ 注册通用 "Python 3 (AI Dev)" Jupyter 内核（单注册，conda-only）
  - 内核使用 /opt/conda/bin/python
  - 注册到 /opt/conda/share/jupyter/kernels/ai-dev/
  - 内核 env 包含 PATH 优先级和 OpenMP 配置
  - 权限设置：chown devuser -R，chmod 644
- ✅ 设置 OpenMP 环境变量（OMP_NUM_THREADS=4, OPENBLAS_NUM_THREADS=1, OMP_WAIT_POLICY=PASSIVE, KMP_DUPLICATE_LIB_OK=TRUE）
- ✅ 写入 build-info 到 /etc/devcontainer-variant-ai-dev-build-info（含24个字段：版本、镜像源、服务、配置等）
- ✅ 清理临时文件
- ✅ [VALIDATION CHECKPOINT] 包含8项验证：
  1. 核心包导入验证（8组栈：NLP/Web/数据/Viz/中文NLP/文档/数据库/工具）
  2. /opt/conda 保留，/opt/venv 已移除
  3. Jupyter 可用且版本 >=4.4
  4. Docker/supervisord 服务继承
  5. devuser 可访问 conda 包
  6. onnx-quantized 继承验证（quantization API）
  7. Jupyter 内核注册验证
  8. PATH 优先级验证
- ✅ 输出 BUILD TIMING SUMMARY 表（3个追加阶段耗时+总耗时）

### R5: .env.example
- ✅ 基础镜像标签配置（BASE_TAG）
- ✅ 镜像源配置（APT_MIRROR/CONDA_MIRROR/PIP_MIRROR）
- ✅ 无额外变体特有参数（包版本不固定，使用最新）

### R6: README.md
- ✅ 变体描述和特性列表
- ✅ 构建命令（标准 + 国内源）
- ✅ 运行示例
- ✅ 验证命令
- ✅ 完整包列表表格
- ✅ 构建参数说明

### R7: .agents/rules/dockerfile.md
- ✅ 基础信息（基础镜像、安装环境、PATH优先级）
- ✅ 核心组件表
- ✅ 构建参数表
- ✅ Stage 结构说明
- ✅ Jupyter 内核注册说明（conda-only）
- ✅ 服务继承说明
- ✅ build-info 路径和字段

### R8: build.sh 注册
- ✅ VARIANTS 数组添加条目，依赖 onnx-quantized
- ✅ 使用 `|||` 三管道作为验证命令分隔符（强制规范）
- ✅ 验证命令覆盖6组核心包导入和内核注册
- ✅ 通过 validate_delimiter_convention() 规范检查

### R9: variants/README.md 注册
- ✅ 在可用变体表格中添加 ai-dev 条目

### R10: 测试脚本 test-ai-dev.sh
- ✅ L1: 核心工具版本（python/pip/conda/jupyterlab/transformers）5项
- ✅ L2: 功能测试（25+包导入+pandas/fastapi/jieba）4项
- ✅ L3: 深度组件验证（内核注册/配置/量化继承/build-info）4项
- ✅ L4: 5项基础服务继承（ssh/supervisord/docker/jupyter/devuser）
- ✅ L5: PATH优先级和环境隔离（conda默认/venv移除/环境变量/devuser访问）4项
- ✅ L6: 配置文件验证（kernel.json/PIP_USER/Entrypoint继承）3项
- ✅ **增强特性（超出原规划）**：
  - pre-flight checks（Docker daemon、镜像存在性、元数据检查）
  - 结构化 JSONL 事件日志（/tmp/test-ai-dev-events.jsonl）
  - 首次失败自动收集8类诊断信息（环境、Python路径、包版本、内核、build-info、服务、磁盘、pip check）
  - per-test timing 计时
  - 彩色输出和格式化总结
  - JupyterLab版本提取使用 `tail -1 | tr -d '[:space:]'`（防御性设计）
  - Entrypoint检查使用正确Go模板语法 `{{json .Config.Entrypoint}}`
- ✅ 总计25个测试用例
- ✅ 脚本通过 bash -n 语法检查
- ✅ 全部25项测试通过（exit code 0）

## 约束

1. 不修改现有变体文件（仅新增）
2. 不覆盖基础镜像 ENTRYPOINT/CMD/WORKDIR
3. 所有包安装到 conda base 环境
4. 构建脚本修改遵循最小变更原则
5. Dockerfile 必须通过语法检查
6. 测试脚本遵循 testing.md 规范（L1-L6分层+可观测性增强）
7. build.sh VARIANTS数组使用 `|||` 作为验证命令分隔符（强制规范，禁止使用 `;`）
8. 采用 conda-only 架构（不保留/opt/venv）
