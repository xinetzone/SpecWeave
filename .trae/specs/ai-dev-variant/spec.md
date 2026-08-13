# Spec: ai-dev 变体萃取

## 背景

从 `external/chaos/ai/portable.Dockerfile` 和 `docker-compose.yml` 中萃取通用的 AI/ML 全栈开发环境，作为 `devcontainer-base` 的新变体 `ai-dev`。

## 源文件分析

### portable.Dockerfile 的通用能力（可萃取）
1. **Python AI/ML/NLP 生态系统**：50+ 个包，覆盖构建工具、NLP、数据处理、可视化、文档处理、数据库客户端、Web 框架
2. **PIP_USER 构建/运行时分离模式**：构建期 `PIP_USER=0` 写入 /opt/conda，运行时 `PIP_USER=1` 支持用户级安装
3. **OpenMP 性能调优**：`OMP_NUM_THREADS=4`、`KMP_DUPLICATE_LIB_OK=TRUE`
4. **pip 镜像源配置**：支持 aliyun/tuna/official
5. **JupyterLab 升级**：>=4.4 + notebook>=7.3 解决 httpx 兼容性
6. **Jupyter 内核注册模式**：注册到 /opt/venv/share/jupyter/kernels（UI可见）+ /opt/conda/share/jupyter/kernels（CLI可见）
7. **BuildKit 缓存挂载**：conda/pkgs + root/.cache/pip

### portable.Dockerfile 的项目特有逻辑（不萃取）
1. 用户重命名 devuser→ai（项目特有用户策略）
2. NPU 专用 Jupyter 内核（PYTHONPATH 指向 /workspace/npu_tvm）
3. supervisord/sshd_config/docker daemon.json 配置修改
4. start.sh / chaos-ai-init.sh / fix-permissions.sh 脚本
5. umask 0027 安全策略
6. ENTRYPOINT=[] / CMD 覆盖（违反变体约定）
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
| 描述 | onnx-quantized + 完整AI/ML/NLP全栈Python生态（50+包）+ JupyterLab 4.x + 通用AI内核 |
| 镜像名 | `devcontainer-base:ai-dev-${BASE_TAG}` |

## 需求规格

### R1: Dockerfile 结构
- 遵循变体共享约定（variant-conventions.md）
- 使用 3 层追加阶段（参考 onnx-quantized 的 3-stage 模式）
- 首行 `# syntax=docker/dockerfile:1.7-labs`
- FROM 后重置 SHELL
- 不覆盖 ENTRYPOINT/CMD/WORKDIR/USER/VOLUME/EXPOSE
- 每个阶段有 [TIMER] 标记
- 末尾有 [VALIDATION CHECKPOINT]

### R2: Stage 1/3 - 基础验证 + 计时器
- 验证 onnx-quantized 基础组件（torch/onnx/onnxruntime/quantization）
- 验证 devuser 和基础服务
- 初始化计时器文件

### R3: Stage 2/3 - Python 包安装
- 构建期设置 `PIP_USER=0`（确保写入 /opt/conda）
- 升级 pip/setuptools/wheel
- 安装完整包列表（分类组织）：
  - 构建工具：scikit-build-core, nuitka, invoke, build
  - 核心工具：decorator, attrs, cloudpickle, typing_extensions, pytest, psutil
  - Jupyter：ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3
  - 数据处理：pyarrow, pandas, scikit-learn, natsort
  - NLP/Transformers：datasets, transformers, sentencepiece, sentence-transformers, evaluate, tiktoken
  - 模型转换：onnx2torch
  - 可视化：matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich
  - AI/ML：einops, open_clip_torch, numba
  - 音频：librosa
  - 中文NLP：jieba, nltk, pypinyin
  - 文档处理：PyMuPDF, EbookLib, beautifulsoup4, openpyxl
  - Web/API：fastapi, uvicorn, httpx>=0.28, pydantic
  - 序列化：toml, typer, xmltodict, pyyaml
  - 数据库：psycopg2-binary, pymongo, elasticsearch, minio
  - 工具：icecream
- 使用 `--mount=type=cache` 缓存
- 安装后升级 /opt/venv 的 jupyterlab/notebook
- 清理 conda/pip 缓存

### R4: Stage 3/3 - 配置 + 元数据 + 验证
- 恢复 `PIP_USER=1`（运行时用户级安装）
- 注册通用 "Python 3 (AI Dev)" Jupyter 内核
  - 内核使用 /opt/conda/bin/python
  - 注册到 /opt/venv/share/jupyter/kernels/ai-dev/（UI可见）
  - 同步到 /opt/conda/share/jupyter/kernels/ai-dev/（CLI可见）
  - 不设置项目特定 PYTHONPATH
- 设置 OpenMP 环境变量（OMP_NUM_THREADS=4, KMP_DUPLICATE_LIB_OK=TRUE）
- 写入 build-info 到 /etc/devcontainer-variant-ai-dev-build-info
- 清理临时文件
- [VALIDATION CHECKPOINT] 包含：
  1. 核心包导入验证（transformers, datasets, fastapi, pandas等）
  2. /opt/venv 保留
  3. Jupyter 可用且版本 >=4.4
  4. Docker/supervisord 服务继承
  5. devuser 可访问 conda 包
  6. onnx-quantized 继承验证（quantization API）
  7. Jupyter 内核注册验证
  8. PATH 优先级验证
- 输出 BUILD TIMING SUMMARY 表

### R5: .env.example
- 基础镜像标签配置
- 镜像源配置（APT/CONDA/PIP）
- 无额外变体特有参数（包版本不固定，使用最新）

### R6: README.md
- 变体描述和特性列表
- 构建命令（标准 + 国内源）
- 运行示例（DinD/DooD/命令模式）
- 验证命令
- 完整包列表表格
- 构建参数说明

### R7: .agents/rules/dockerfile.md
- 基础信息（基础镜像、安装环境、PATH优先级）
- 核心组件表
- 构建参数表
- Stage 结构说明
- Jupyter 内核注册说明
- 服务继承说明
- build-info 路径和字段

### R8: build.sh 注册
- VARIANTS 数组添加条目，依赖 onnx-quantized
- 验证命令覆盖核心包导入和服务继承

### R9: variants/README.md 注册
- 在可用变体表格中添加 ai-dev 条目

### R10: 测试脚本 test-ai-dev.sh
- L1: 核心工具版本（python/pip/conda/jupyter）
- L2: 至少1个功能测试（包导入+简单操作）
- L3: 深度组件验证（Jupyter内核、环境变量、包完整性）
- L4: 5项基础服务继承（ssh/supervisord/docker/jupyter/devuser）
- L5: PATH优先级和环境隔离
- L6: 配置文件验证（build-info、内核注册）

## 约束

1. 不修改现有变体文件（仅新增）
2. 不覆盖基础镜像 ENTRYPOINT/CMD/WORKDIR
3. 所有包安装到 conda base 环境
4. 构建脚本修改遵循最小变更原则
5. Dockerfile 必须通过 `bash -n` 等价的语法检查
6. 测试脚本遵循 testing.md 规范
