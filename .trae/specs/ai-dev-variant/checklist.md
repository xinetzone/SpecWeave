# Checklist: ai-dev 变体萃取

## Dockerfile 规范

- [ ] 首行 `# syntax=docker/dockerfile:1.7-labs`
- [ ] FROM 使用 `devcontainer-base:onnx-quantized-${BASE_TAG}`
- [ ] FROM 后重新声明 ARG BASE_TAG
- [ ] FROM 后有 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- [ ] 未覆盖 ENTRYPOINT
- [ ] 未覆盖 CMD
- [ ] 未覆盖 WORKDIR
- [ ] 未覆盖 USER
- [ ] 未覆盖 VOLUME
- [ ] 未覆盖 EXPOSE
- [ ] 使用 `--mount=type=cache` 缓存挂载（conda/pkgs + pip cache）
- [ ] Stage 1/3 有基础验证和计时器初始化
- [ ] Stage 2/3 有包安装和 [TIMER] 标记
- [ ] Stage 3/3 有 build-info、清理、验证、计时汇总表
- [ ] 构建期 PIP_USER=0，运行时恢复 PIP_USER=1
- [ ] 末尾有 [VALIDATION CHECKPOINT]
- [ ] LABEL 包含 maintainer/description/variant

## Python 包完整性

- [ ] 构建工具：scikit-build-core, nuitka, invoke, build
- [ ] 核心工具：decorator, attrs, cloudpickle, typing_extensions, pytest, psutil
- [ ] Jupyter：ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3
- [ ] 数据处理：pyarrow, pandas, scikit-learn, natsort
- [ ] NLP：datasets, transformers, sentencepiece, sentence-transformers, evaluate, tiktoken
- [ ] 模型转换：onnx2torch
- [ ] 可视化：matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich
- [ ] AI/ML：einops, open_clip_torch, numba
- [ ] 音频：librosa
- [ ] 中文NLP：jieba, nltk, pypinyin
- [ ] 文档处理：PyMuPDF, EbookLib, beautifulsoup4, openpyxl
- [ ] Web/API：fastapi, uvicorn, httpx>=0.28, pydantic
- [ ] 序列化：toml, typer, xmltodict, pyyaml
- [ ] 数据库：psycopg2-binary, pymongo, elasticsearch, minio
- [ ] 工具：icecream

## Jupyter 内核

- [ ] 注册 "Python 3 (AI Dev)" 内核
- [ ] 内核 argv 指向 /opt/conda/bin/python
- [ ] 主注册到 /opt/venv/share/jupyter/kernels/ai-dev/
- [ ] 同步到 /opt/conda/share/jupyter/kernels/ai-dev/
- [ ] 内核文件权限正确（644）
- [ ] 不包含项目特定 PYTHONPATH

## 环境变量

- [ ] CONDA_DIR=/opt/conda
- [ ] PATH 包含 /opt/conda/bin（前置）
- [ ] OMP_NUM_THREADS=4
- [ ] KMP_DUPLICATE_LIB_OK=TRUE
- [ ] PIP_USER=1（运行时）

## 验证检查点

- [ ] 核心包导入验证（transformers, datasets, fastapi, pandas等）
- [ ] /opt/venv 保留
- [ ] Jupyter 可用且版本 >=4.4
- [ ] Docker/supervisord 服务继承
- [ ] devuser 可访问 conda 包
- [ ] onnx-quantized 继承验证
- [ ] Jupyter 内核注册验证
- [ ] PATH 优先级验证

## 文件完整性

- [ ] `variants/ai-dev/Dockerfile` 存在
- [ ] `variants/ai-dev/.env.example` 存在
- [ ] `variants/ai-dev/README.md` 存在
- [ ] `variants/ai-dev/.agents/rules/dockerfile.md` 存在
- [ ] `variants/scripts/test-ai-dev.sh` 存在且可执行

## 注册完整性

- [ ] `variants/build.sh` VARIANTS 数组包含 ai-dev
- [ ] `variants/README.md` 变体表格包含 ai-dev
- [ ] `variants/AGENTS.md` 不需要修改（自动通过目录扫描发现）

## 测试覆盖

- [ ] L1: 核心工具版本检查（5+）
- [ ] L2: 功能测试（包导入+简单操作）
- [ ] L3: 深度组件验证（2+）
- [ ] L4: 基础服务继承（5项：ssh/supervisord/docker/jupyter/devuser）
- [ ] L5: PATH优先级和环境隔离
- [ ] L6: 配置文件验证（build-info、内核）
- [ ] 总计 15+ 测试用例

## 语法检查

- [ ] Dockerfile 无语法错误（通过 docker build 解析或 hadolint）
- [ ] test-ai-dev.sh 通过 `bash -n` 语法检查
- [ ] build.sh 通过 `bash -n` 语法检查
