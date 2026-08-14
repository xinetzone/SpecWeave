---
id: "devcontainer-base-structure"
title: "devcontainer-base 项目结构导航"
source: "AGENTS.md#嵌套路由关系"
---
# devcontainer-base - 项目目录结构

本文件提供 devcontainer-base 项目的完整目录结构导航，帮助 AI 协作者快速定位文件。

## 完整目录树

```
devcontainer-base/
├── AGENTS.md              ← 本文件（AI协作者入口，启动协议必读）
├── README.md              ← 人类可读：使用文档
├── CHANGELOG.md           ← 版本变更日志
├── Dockerfile             ← 多阶段构建定义（v2.2单镜像7Stage架构）
├── entrypoint.sh          ← 容器启动脚本（tini init + supervisord）
├── docker-compose.yml     ← Compose 编排配置
├── .env.example           ← 环境变量模板（APT_MIRROR/PIP_MIRROR等）
├── .dockerignore          ← 构建上下文排除规则
├── .gitignore             ← Git忽略规则
│
├── .agents/               ← AI资产容器（本项目特有规范，详见 README.md）
│   ├── README.md          ← .agents 目录索引和加载顺序
│   ├── rules/             ← 项目特有规则（单一职责，按主题拆分）
│   │   ├── dockerfile.md  ← Dockerfile 多阶段构建规范（7 Stage/BuildKit缓存/清理）
│   │   ├── entrypoint.md  ← Entrypoint 启动脚本规范（tini/日志/信号）
│   │   ├── services.md    ← 服务管理规范（supervisord/SSH/Docker/Podman/Jupyter）
│   │   └── build-test.md  ← 构建与测试流程（build.sh/start.sh/Compose/验证）
│   ├── workflows/         ← CI/CD工作流设计文档
│   │   └── variants-ci.md ← 变体构建CI + ONNX量化门禁设计
│   ├── roles/             ← 角色定义（预留，回退到父级）
│   ├── skills/            ← 技能（预留，回退到父级）
│   ├── scripts/           ← 自动化脚本（预留）
│   ├── templates/         ← 模板（预留）
│   └── docs/              ← AI知识库（预留）
│
├── conda-lock/            ← Conda 环境锁定管理
│   ├── environment.yml    ← Python 3.14 cp314t 精确版本锁定模板
│   └── generate-locks.sh  ← 锁文件生成/验证/安装脚本
│
├── config/                ← 配置文件目录
│   ├── supervisord.conf   ← supervisord 主配置
│   ├── sshd_config         ← SSH 服务配置（ED25519优先/禁用root登录）
│   ├── jupyter_notebook_config.py ← Jupyter 基础配置（token/CORS/工作目录）
│   └── supervisor/        ← supervisord 服务配置目录
│       └── conf.d/        ← 各服务独立配置文件
│           ├── sshd.conf       ← sshd 服务配置
│           ├── dockerd.conf    ← dockerd 服务配置（DinD模式）
│           └── jupyter.conf    ← jupyter 服务配置
│
├── scripts/               ← 辅助脚本库
│   ├── lib/               ← 脚本共享库
│   │   └── logging.sh     ← 结构化日志函数（log_info/log_ok/log_error等）
│   ├── build.sh           ← 一键构建基础镜像脚本
│   ├── start.sh           ← 一键启动/停止/状态查询脚本
│   ├── local-build.sh     ← WSL2本地构建脚本（变体依赖链处理）
│   ├── healthcheck.sh     ← 容器健康检查脚本（端口探测）
│   ├── verify-deployment.py ← 部署验证脚本（多维度检查）
│   ├── ci_quantization_gate.py ← CI量化门禁脚本（cosine_sim≥0.90）
│   ├── ci-requirements.txt ← CI Python依赖清单
│   ├── verify-services.sh ← 服务验证脚本
│   ├── ft-benchmark.sh    ← Free-threading性能基准测试
│   ├── verify-cext.sh     ← C扩展验证脚本
│   ├── onnx-quantize.py   ← ONNX量化命令行工具
│   ├── batch_quantize.py  ← 批量量化脚本
│   ├── benchmark_quantization.py ← 量化性能基准
│   ├── analyze_benchmark.py ← 基准结果分析
│   ├── analyze-diagnostics.py ← 诊断分析脚本
│   ├── compare_qdq_vs_qoperator.py ← QDQ vs QOperator对比
│   ├── run_full_benchmark.py ← 完整基准测试运行器
│   ├── run-benchmark-docker.sh ← Docker内基准测试脚本
│   ├── ci_alert.py        ← CI告警脚本
│   ├── EXERCISES.md       ← 练习/实验记录
│   ├── QUICKSTART.md      ← ONNX量化工具包快速入门
│   │
│   ├── onnx_quantize_kit/ ← ONNX量化工具包（onnxruntime.quantization封装）
│   │   ├── __init__.py
│   │   ├── quantize.py        ← 高层量化API（auto_quantize/动态/静态/FP16）
│   │   ├── accuracy.py        ← 精度验证（cosine_sim/L2误差）
│   │   ├── benchmark.py       ← 性能基准测试
│   │   ├── calibration.py     ← 校准数据读取（CalibrationDataReader）
│   │   ├── model_detect.py    ← 模型类型检测（Conv/Gemm主导）
│   │   ├── cli.py             ← 命令行接口
│   │   └── reporting.py       ← 量化报告生成
│   │
│   ├── test_quantize_kit.py   ← 工具包单元测试
│   ├── test_ort_quantization_regression.py ← ORT回归测试（G1-G11门禁）
│   ├── test_onnxruntime_quantization.py    ← ORT API单元测试
│   ├── test_neural_compressor.py           ← Neural Compressor兼容性测试（可选）
│   │
│   ├── models/             ← 测试用ONNX模型
│   │   ├── mlp.onnx
│   │   ├── cnn.onnx
│   │   └── transformer.onnx
│   │
│   └── experiments/        ← 实验性脚本（非稳定API）
│       ├── cext-test/      ← C扩展测试实验
│       ├── micromamba/     ← Micromamba对比实验
│       └── compare-micromamba.sh ← Micromamba vs Miniforge对比脚本
│
├── docs/                  ← 人类可读技术文档（最佳实践/指南/公告/发布说明）
│   ├── best-practices.md            ← Docker DinD/Compose/镜像源最佳实践
│   ├── CONDA-PERF-INTEGRATION-GUIDE.md ← Conda 性能优化集成指南
│   ├── PY314T-C-EXTENSION-GUIDE.md  ← Python 3.14t C 扩展编译指南
│   ├── TECH-ADVISORY-defaults-channel-abi-risk.md ← defaults channel ABI风险公告
│   ├── RELEASE-v2.md                ← v2.2 版本详细发布说明
│   └── v2.2-build-pipeline-optimization.md ← v2.2 构建流水线优化方案（七概念方法论记录）
│
├── examples/              ← 示例代码
│   └── free_threading_demo.py ← Free-threading 多线程性能演示（GIL vs nogil）
│
├── templates/             ← 可复用模板
│   └── cmake-cext/        ← CMake C 扩展标准模板（Python 3.14t兼容）
│       ├── src/ft_extension.c
│       ├── CMakeLists.txt
│       ├── README.md
│       ├── build.sh
│       └── test-in-docker.sh
│
└── variants/              ← 镜像变体系列（子系统，有独立AGENTS.md）
    ├── AGENTS.md          ← 变体系列路由入口（进入variants/必读）
    ├── README.md          ← 人类可读：变体索引和使用指南
    ├── build.sh           ← 变体统一构建脚本（拓扑排序+依赖处理+计时+验证）
    │
    ├── .agents/           ← 变体管理子系统AI资产容器
    │   ├── README.md      ← 子系统.agents索引
    │   └── rules/         ← 变体管理规则
    │       ├── build-orchestration.md  ← 构建编排规范（VARIANTS格式/拓扑排序）
    │       ├── variant-conventions.md  ← 变体Dockerfile共享约定
    │       ├── testing.md              ← 6层测试策略
    │       └── new-variant-guide.md    ← 新增变体7步指南
    │
    ├── shared/            ← 变体间共享组件（禁止复制粘贴）
    │   ├── lib/logging.sh ← 共享结构化日志库（双格式text+JSON）
    │   ├── scripts/
    │   │   ├── conda-mirror-setup.sh ← conda/pip镜像源配置（环境变量驱动）
    │   │   └── conda-perf-setup.sh   ← Conda性能优化配置
    │   ├── config/condarc/ ← Conda镜像源配置
    │   └── templates/conda-perf/ ← Conda性能方案模板
    │
    ├── scripts/           ← 单变体辅助脚本
    │   ├── build-conda-llvm.sh    ← conda-llvm一键构建
    │   ├── build-onnx-pytorch.sh  ← onnx-pytorch一键构建
    │   ├── test-conda-llvm.sh     ← conda-llvm单元测试
    │   ├── test-conda-llvm-smoke.sh ← conda-llvm冒烟测试
    │   ├── test-onnx-pytorch.sh   ← onnx-pytorch单元测试（20项）
    │   ├── test-onnx-quantized.sh ← onnx-quantized单元测试
    │   ├── test-ai-dev.sh         ← ai-dev变体测试
    │   └── test-timer-parser.sh   ← [TIMER]日志解析单元测试
    │
    ├── _template/         ← 新变体模板（复制→替换占位符→注册）
    │   ├── Dockerfile
    │   ├── .env.example
    │   ├── README.md
    │   └── .agents/rules/dockerfile.md
    │
    ├── conda/             ← Miniconda3 基础环境变体（Miniforge3 + Python 3.14.6 cp314t）
    │   ├── Dockerfile
    │   ├── .env.example
    │   ├── README.md
    │   └── .agents/rules/dockerfile.md
    │
    ├── conda-llvm/        ← conda+LLVM 22.1.8/clang/cmake/ninja 编译工具链
    │   ├── Dockerfile
    │   ├── .env.example
    │   ├── README.md
    │   ├── DEPENDENCIES.md
    │   ├── RELEASE.md
    │   ├── RELEASE-GUIDE.md
    │   └── .agents/rules/dockerfile.md
    │
    ├── ai-dev/            ← AI开发全栈工具链变体
    │   ├── Dockerfile
    │   ├── .env.example
    │   ├── README.md
    │   └── .agents/rules/dockerfile.md
    │
    ├── onnx-pytorch/      ← PyTorch CPU + ONNX Runtime 深度学习运行时
    │   ├── Dockerfile
    │   ├── .env.example
    │   ├── README.md
    │   └── .agents/rules/dockerfile.md
    │
    └── onnx-quantized/    ← ONNX量化工具链变体（INT8/FP16，onnxruntime.quantization）
        ├── Dockerfile
        ├── .env.example
        ├── README.md
        ├── ADVANCED-QUANTIZATION-GUIDE.md
        ├── QUANTIZATION-BEST-PRACTICES.md
        └── .agents/rules/dockerfile.md
```

## 目录职责说明

| 目录 | 职责 | 修改频率 |
|------|------|---------|
| `.agents/` | AI协作者规范容器（rules/workflows） | 中（规范迭代时） |
| `config/` | 服务配置文件（supervisord/SSH/Jupyter/Docker） | 低（配置变更时） |
| `scripts/` | 构建/测试/验证/量化工具脚本 | 高（功能开发时） |
| `scripts/onnx_quantize_kit/` | ONNX量化工具包核心库 | 中高 |
| `docs/` | 人类可读技术文档（指南/公告/发布说明） | 低（文档更新时） |
| `examples/` | 示例代码 | 低 |
| `templates/` | 可复用项目模板 | 低 |
| `variants/` | 镜像变体系列（独立子系统） | 中（新增/更新变体时） |
| `conda-lock/` | Conda环境锁定文件 | 低（Python版本变更时） |

## 快速定位指南

| 你要找什么 | 去哪里找 |
|-----------|---------|
| Dockerfile怎么写 | `.agents/rules/dockerfile.md` |
| 启动脚本怎么改 | `.agents/rules/entrypoint.md` |
| 服务配置（SSH/Docker/Jupyter/Podman） | `.agents/rules/services.md` |
| 怎么构建/测试/启动 | `.agents/rules/build-test.md` |
| 怎么构建变体 | `variants/AGENTS.md` |
| CI流水线怎么工作 | `.agents/workflows/variants-ci.md` |
| 量化工具包怎么用 | `scripts/QUICKSTART.md` |
| 项目约束速查 | `.agents/README.md#核心约束速查` |
| 最佳实践/性能优化 | `docs/` 目录 |
