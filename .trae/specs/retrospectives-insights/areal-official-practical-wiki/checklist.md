# AReaL 官方完整实战教程 Wiki - Verification Checklist

## 文档格式验证
- [x] frontmatter 使用 YAML 格式（--- 分隔）
- [x] frontmatter 包含 title、source、date（2026-08-04）、tags、x-toml-ref 字段
- [x] 文件名为 areal-official-practical-wiki.md（kebab-case纯英文）
- [x] 标题层级从 h1 开始，无跳级
- [x] 表格格式正确，列数对齐
- [x] 代码块使用正确的语言标记（bash/yaml/python）
- [x] Markdown 链接格式正确，无断链（与areal-agent-rl-wiki.md双向引用）

## 安装指南验证
- [x] 明确列出硬件要求（GPU型号/数量、CPU、内存、网络、存储）
- [x] 明确列出软件要求（Linux版本、CUDA版本、Python版本、PyTorch版本）
- [x] 提供 Docker 安装方式完整命令
- [x] 提供源码安装方式完整命令（git clone + pip install + uv sync）
- [x] 说明 SGLang 和 vLLM 的切换方法（pyproject.toml替换）
- [x] 包含 flash-attn 预编译 wheel 安装说明
- [x] 提供安装验证命令（validate_installation.py）
- [x] 包含昇腾 NPU 安装指引链接

## 快速开始验证
- [x] 单节点 GSM8K GRPO 训练命令完整正确
- [x] 配置修改方法说明清晰（YAML编辑 + 命令行Hydra覆盖）
- [x] Ray 分布式启动命令示例正确
- [x] Slurm 分布式启动命令示例正确
- [x] SkyPilot 云部署指引清晰
- [x] backend 并行配置语法正确（如 sglang:d12p1t1）
- [x] 训练输出和日志查看方法说明

## 核心概念与架构验证
- [x] Trainer 概念解释清晰（PPOTrainer/SFTTrainer/DPOTrainer/RWTrainer）
- [x] Engine 概念解释清晰（InferenceEngine/TrainEngine）
- [x] Workflow 概念解释清晰（RolloutWorkflow/RLVRWorkflow）
- [x] Rollout 概念解释清晰（三级并发架构）
- [x] Weight Versioning 概念解释清晰（NCCL/磁盘同步）
- [x] 与 v1.0 单体架构的区别说明清楚（v1/v2对比表）

## 算法与引擎矩阵验证
- [x] 至少包含15种RL算法（实际16种：GRPO/GSPO/PPO/DAPO/LitePPO/DrGRPO/REINFORCE++/RLOO/SAPO/IcePop/KPop/M2PO/DPO/RW/SFT/Distillation）
- [x] 每种算法有对应yaml配置文件路径
- [x] 三大训练引擎（FSDP2/Megatron/Archon）并行策略对比表正确
- [x] 模型支持矩阵与areal/models/目录实际一致（Qwen2/3, Qwen3-MoE, Qwen2.5-VL/Qwen3-VL, Gemma3）
- [x] 两大推理后端（SGLang/vLLM）并行支持对比正确
- [x] SGLang/vLLM切换方法说明正确（cp pyproject文件+uv sync）

## v2.0 微服务架构验证
- [x] Agent Service 的 Gateway/Router/DataProxy/Worker 四组件职责清晰（含ASCII架构图）
- [x] Inference Service 组件说明清晰
- [x] Training Service 组件说明清晰
- [x] Weight Update 组件说明清晰
- [x] AgentRunnable 协议代码示例完整（Python Protocol定义）
- [x] 多轮对话流程图文字描述准确
- [x] 各组件 HTTP API 端点列表完整（Gateway/Router/DataProxy/Worker）
- [x] 代码组织目录结构与areal/v2/实际一致

## Online RL 在线训练验证
- [x] 三种模式（inline/subproc/online）对比表清晰
- [x] 架构图文字描述准确（Proxy Gateway/Workers/Inference Servers/Trainer）
- [x] 6步快速开始流程完整（配置→启动服务→创建session→交互→设置奖励→批量采样）
- [x] API 端点完整（start_session/chat/completions/set_reward/refresh机制）
- [x] 双层认证机制说明清楚（admin key / session key）
- [x] 错误码表完整（400/401/403/409/429/500/502）
- [x] Python OpenAI SDK 调用示例正确
- [x] curl 命令示例正确
- [x] 完整Python单key刷新机制示例

## CLI 命令参考验证
- [x] agent ps/run/status/stop 命令说明正确
- [x] inference ps/run/stop 命令说明正确（inf别名）
- [x] training run 命令说明正确（train别名）
- [x] logs 命令说明正确（-f追踪、--component指定）
- [x] 配置覆盖语法说明正确（key=value覆盖和+key=value新增，Hydra风格）
- [x] 状态存储位置说明（~/.areal/）

## 代码仓库结构验证
- [x] areal/ 目录下各子模块说明与实际一致（api/dataset/engine/experimental/infra/models/reward/tools/trainer/utils/workflow/v2 共12个）
- [x] v2/ 微服务代码目录结构正确
- [x] examples/ 分类说明准确（Math/Agentic/VLM/Alignment/TIR/SWE/Tau2/OpenClaw/Hermes等20+个）
- [x] 核心入口文件说明正确
- [x] 关键示例解析（hermes/swe/math/openclaw/tau2/tir）含运行命令和核心特性

## 最佳实践与FAQ验证
- [x] 算法性能诊断指南（同步vs异步、奖励不上升4步诊断、关键监控指标）
- [x] Agent 工作流编写指南（async/await、AsyncRewardWrapper、避免重初始化、复用HTTP客户端）
- [x] 调试指南（持久化推理服务器调试、py-spy死锁诊断、NCCL_DEBUG环境变量）
- [x] OOM 处理方法（生成阶段OOM、训练阶段OOM 6种方案、优化器状态优化）
- [x] 性能 profiling 方法（perf_tracer、Chrome Trace/Perfetto可视化）
- [x] FAQ 包含精选常见问题（安装/训练/分布式/Online RL/v2.0类共20+个）
- [x] 术语表包含核心技术术语（25+个精选术语，覆盖RL算法/架构/并行策略/核心概念）
- [x] 资源链接完整（官方资源/核心算法论文/依赖项目文档/社区资源/快速配置参考）

## 知识库索引验证
- [x] 03-agent-platforms-tools/README.md 中新增条目
- [x] 条目格式与现有条目一致
- [x] tags 准确（areal、rl-training、agentic-rl、online-rl、llm-alignment、distributed-training、pytorch、sglang、vllm、fsdp、megatron）
- [x] 与现有 areal-agent-rl-wiki.md 形成系列链接（概念篇→实战篇双向引用）
- [x] 交叉引用链接正确（README.md学习路径、快速导航均更新）

## 内容准确性验证
- [x] 所有代码示例和命令基于本地仓库实际内容
- [x] 随机抽取的命令/API/配置项与本地代码仓库交叉验证通过（CLI目录结构、API端点、目录结构、算法yaml文件）
- [x] 无编造的API或配置项
- [x] 客观说明系统限制（Linux要求、CUDA 12.8、GPU型号H800/A100推荐、SGLang/vLLM互斥）
- [x] 文档长度约1522行（内容完整，十大章节齐全）
- [x] 技术术语首次出现时给出中文解释
- [x] 工作区临时文件已清理（删除4个AReaL目录下的临时笔记文件）
