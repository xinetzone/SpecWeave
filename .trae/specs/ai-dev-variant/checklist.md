---
status: completed
updated_at: 2026-08-13
completion_note: "所有检查项已通过验证"
---

# Checklist: ai-dev 变体萃取

## Dockerfile 规范

- [x] 首行 `# syntax=docker/dockerfile:1.7-labs`
- [x] FROM 使用 `devcontainer-base:onnx-quantized-${BASE_TAG}`
- [x] FROM 后重新声明 ARG BASE_TAG
- [x] FROM 后有 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- [x] 未覆盖 ENTRYPOINT
- [x] 未覆盖 CMD
- [x] 未覆盖 WORKDIR
- [x] 未覆盖 USER
- [x] 未覆盖 VOLUME
- [x] 未覆盖 EXPOSE
- [x] 使用 `--mount=type=cache` 缓存挂载（conda/pkgs + pip cache）
- [x] Stage 1/3 有基础验证和计时器初始化（含/opt/venv移除验证）
- [x] Stage 2/3 有包安装和 [TIMER] 标记（含pip_install_group()可观测性）
- [x] Stage 3/3 有 build-info、清理、验证、计时汇总表
- [x] 构建期 PIP_USER=0，运行时恢复 PIP_USER=1
- [x] 末尾有 [VALIDATION CHECKPOINT]（8项验证）
- [x] LABEL 包含 maintainer/description/variant/ecosystem
- [x] 二进制 strip 优化
- [x] OpenMP 环境变量完整（OMP_NUM_THREADS=4, OPENBLAS_NUM_THREADS=1, OMP_WAIT_POLICY=PASSIVE, KMP_DUPLICATE_LIB_OK=TRUE）

## Python 包完整性（14组，50+包）

- [x] G1-构建工具：scikit-build-core, nuitka, invoke, build
- [x] G2-核心工具：decorator, attrs, cloudpickle, typing_extensions, pytest, psutil
- [x] G3-Jupyter：ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3
- [x] G4-数据处理：pyarrow, pandas, scikit-learn, natsort
- [x] G5-NLP：datasets, transformers, sentencepiece, sentence-transformers, evaluate, tiktoken, onnx2torch
- [x] G6-可视化：matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich
- [x] G7-AI/ML：einops, open_clip_torch, numba
- [x] G8-音频：librosa
- [x] G9-中文NLP：jieba, nltk, pypinyin
- [x] G10-文档处理：PyMuPDF, EbookLib, beautifulsoup4, openpyxl
- [x] G11-Web/API：pydantic, fastapi, uvicorn, httpx>=0.28
- [x] G12-序列化：toml, typer, xmltodict, pyyaml
- [x] G13-数据库：psycopg2-binary, pymongo, elasticsearch, minio
- [x] G14-工具：icecream
- [x] 末尾 pip check 依赖一致性验证

## Jupyter 内核（conda-only 单注册架构）

- [x] 注册 "Python 3 (AI Dev)" 内核
- [x] 内核 argv 指向 /opt/conda/bin/python
- [x] 注册到 /opt/conda/share/jupyter/kernels/ai-dev/（单注册，conda-only架构）
- [x] ~~同步到 /opt/venv/share/jupyter/kernels/ai-dev/~~（架构调整：conda-only，无/opt/venv）
- [x] 内核文件权限正确（644，devuser属主）
- [x] 不包含项目特定 PYTHONPATH
- [x] 内核env包含PATH优先级和OpenMP配置

## 环境变量

- [x] CONDA_DIR=/opt/conda
- [x] PATH 包含 /opt/conda/bin（前置优先）
- [x] OMP_NUM_THREADS=4
- [x] OPENBLAS_NUM_THREADS=1
- [x] OMP_WAIT_POLICY=PASSIVE
- [x] KMP_DUPLICATE_LIB_OK=TRUE
- [x] PIP_USER=1（运行时最终层）

## 验证检查点（[VALIDATION CHECKPOINT] 8项）

- [x] 核心包导入验证（8组栈：NLP/Web/数据/Viz/中文NLP/文档/数据库/工具）
- [x] /opt/conda 保留，/opt/venv 已移除（conda-only架构）
- [x] Jupyter 可用且版本 >=4.4
- [x] Docker/supervisord 服务继承
- [x] devuser 可访问 conda 包
- [x] onnx-quantized 继承验证（quantization API）
- [x] Jupyter 内核注册验证
- [x] PATH 优先级验证

## 文件完整性

- [x] `variants/ai-dev/Dockerfile` 存在
- [x] `variants/ai-dev/.env.example` 存在
- [x] `variants/ai-dev/README.md` 存在
- [x] `variants/ai-dev/.agents/rules/dockerfile.md` 存在
- [x] `variants/scripts/test-ai-dev.sh` 存在且可执行

## 注册完整性

- [x] `variants/build.sh` VARIANTS 数组包含 ai-dev
- [x] 使用 `|||` 三管道作为验证命令分隔符（强制规范）
- [x] 6条验证命令覆盖核心功能
- [x] `variants/README.md` 变体表格包含 ai-dev
- [x] `variants/AGENTS.md` 不需要修改（自动通过目录扫描发现）

## 测试覆盖（test-ai-dev.sh，共25项）

- [x] L1: 核心工具版本检查（5项：python/conda/pip/jupyterlab/transformers）
- [x] L2: 功能测试（4项：25+包全导入/pandas/fastapi/jieba）
- [x] L3: 深度组件验证（4项：内核注册/内核配置/量化继承/build-info）
- [x] L4: 基础服务继承（5项：ssh/supervisord/docker/jupyter/devuser）
- [x] L5: PATH优先级和环境隔离（4项：conda默认/venv移除/环境变量/devuser访问）
- [x] L6: 配置文件验证（3项：kernel.json有效性/PIP_USER=1/Entrypoint继承）
- [x] 总计 25 个测试用例（超出原规划15+要求）
- [x] 增强：pre-flight checks（Docker daemon/镜像存在/元数据）
- [x] 增强：结构化JSONL事件日志
- [x] 增强：首次失败自动收集8类诊断信息
- [x] 增强：per-test timing计时
- [x] 增强：JupyterLab版本tail -1提取（防御性设计）
- [x] 增强：Go模板语法修正（Entrypoint检查）
- [x] 全部25项测试通过（exit code 0）

## 语法检查

- [x] Dockerfile 语法正确（docker build 解析通过）
- [x] test-ai-dev.sh 通过 `bash -n` 语法检查
- [x] build.sh 通过 `bash -n` 语法检查
- [x] build.sh 通过 validate_delimiter_convention() 分隔符规范检查

## 架构决策检查

- [x] 采用 conda-only 架构（/opt/venv 已移除）
- [x] build.sh 使用 `|||` 作为验证命令分隔符（禁止`;`）
- [x] pip_install_group() 提供安装可观测性（分组/计时/冲突检测/诊断）
- [x] build-info 包含24个元数据字段
