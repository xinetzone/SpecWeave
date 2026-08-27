# 容器化技术产业链分析

## 核心判断

容器化技术产业链已从"微服务编排"演变为"AI 工作负载统一调度平台"，核心链条为：OCI 标准规范层 → 镜像仓库分发层 → Kubernetes 编排调度层 → AI 工作负载层。OCI Distribution 规范（v1.1.0）使镜像仓库从纯容器存储扩展为通用制品枢纽，连接了构建、安全签名、策略治理和部署分发多个相邻环节 [3][4]；GPU 资源获取与利用率成为全链路最大瓶颈——82% 的容器用户在生产中运行 Kubernetes，66% 的 GenAI 托管组织使用 Kubernetes 执行推理工作负载，但标准 K8s 调度原语无法原生处理细粒度 GPU 切分和批量调度，催生了 Kueue、DAS、GAIE 等专用组件 [1][2]。

## 产业链结构与关键参与者

```visual
type: chain
title: 容器化技术产业链关键环节与参与者
source: [1]
item: OCI 标准规范层 | Runtime Spec、Image Spec、Distribution Spec v1.1.0，定义运行时、镜像格式和仓库推拉协议 | 厂商中立互操作基座，使运行时、仓库和工具跨厂商兼容
item: 容器运行时层 | containerd（K8s 生产默认）、Podman（无守护进程安全）、runc、gVisor 与 Kata Containers（沙箱隔离） | 运行时从 Docker 垄断分裂为场景化工具矩阵
item: 镜像仓库分发层 | Harbor、ZOT（自托管）、Amazon ECR、Azure ACR、Google Artifact Registry、GHCR（云厂商） | OCI 仓库扩展为通用制品枢纽，承载 Helm charts、SBOM、签名等
item: 编排调度层 | Kubernetes、K3s（边缘）、Karpenter（弹性供给）、KEDA（事件驱动伸缩） | K8s 成为 AI 工作负载统一平台，etcd 在超大规模下成为控制面瓶颈
item: AI 工作负载层 | Kueue 与 Volcano（批量调度）、DAS（GPU 切分）、GAIE（推理路由）、KServe 与 vLLM（推理服务） | AI 工作负载催生专用 K8s 原生组件，GPU 获取与利用率是全链路最大瓶颈
```

## OCI 标准在产业链互操作性中的角色

OCI 定义三项规范——Runtime Spec（容器运行方式）、Image Spec（容器内容描述）和 Distribution Spec（仓库推拉协议） [4]。在存储层，OCI 仓库仅处理两个原语——manifest（JSON 文档，通过 SHA-256 摘要引用 blob）和 blob（不透明二进制内容），标签为指向 manifest 的可读名称 [4]。这种简单性使其成为通用分发基座。

OCI Spec v1.1.0（2024 年 2 月）新增了 `artifactType` 字段（声明 manifest 描述的制品类型，使仓库可区分 Helm chart 与容器镜像）和 `subject` 字段（允许一个制品引用另一个制品，实现签名和 SBOM 附加） [3][4]。Harbor 等仓库通过 referrers API 实现关联制品发现 [3]。

OCI 标准的互操作性角色体现在三个层面：

第一，所有主流云厂商均运行 OCI 兼容仓库——Amazon ECR、Azure Container Registry、Google Artifact Registry、GitHub Container Registry，自托管方案 Harbor 和 ZOT 也已成熟 [4]。这意味着镜像和制品可跨厂商环境无缝迁移。

第二，ORAS（OCI Registry As Storage）作为 CNCF 项目抽象了多步 OCI 上传流程，Helm、Flux、Crossplane 和 Sigstore 签名工具均使用 ORAS 或底层 OCI 客户库 [4]。ORAS 将异构工具统一到同一分发原语上。

第三，Kubernetes v1.33 的 ImageVolume beta 特性可将任意 OCI 镜像或制品直接挂载为 Pod 只读卷，适用于静态配置、AI/ML 模型、插件或脚本 [3]。这使 OCI 仓库直接接入运行时层的数据供给通道。

## 镜像仓库分发层在产业链中的地位

镜像仓库已从产业链末端的"存储后端"演变为分发链路的核心节点。Harbor 提出的"Gitless GitOps"模型将 OCI 仓库作为唯一事实来源，取代 Git 仓库用于跨多区域分发已签名的容器镜像和相关制品 [3]。仓库内置复制、制品签名和集群内 OCI 镜像挂载，无需 Git 即可实现加密保证和多区域部署 [3]。

多个 CNCF 和 LF 工具已原生支持 OCI 仓库 [3]：

- **Helm** v3 起支持通过 `helm push` 将 charts 推送到 OCI 仓库，消除独立 chart 仓库需求；Azure CLI 于 2025 年 9 月停用旧版 Helm 仓库支持 [3][4]
- **Flux CD** 长期支持 OCI 仓库作为源类型，可自动协调存储为 OCI 制品的 manifest [3]
- **Argo CD** v3.1.0 起可引用和部署 OCI 仓库中定义的应用 [3]
- **Tekton Bundles** 将 Task 和 Pipeline 定义存储为 OCI 制品 [3]
- **OpenTofu** v1.10.0 起可从 OCI 仓库获取模块和 provider [3]
- **Sigstore/Cosign** 将签名和验证直接存储在 OCI 仓库内 [3]

仓库层的价值集中体现在三个方面 [3][4]：

- **内置复制**：跨区域/跨可用区同步，保持镜像、charts、配置和附件的一致性
- **制品签名与附件**：通过 `subject` 字段链接签名、SBOM 和 attestation，使用 Cosign（Sigstore）或 Notation（Notary 项目）签名
- **内容寻址存储**：SHA-256 摘要去重（相同 blob 只存一份）和完整性验证（摘要匹配即字节相同）

镜像仓库因此同时连接构建层（BuildKit/Buildah 推送镜像）、安全层（Cosign/Notation 签名）、策略层（Kubewarden/OPA）和部署层（Flux/Argo CD 拉取），成为产业链中多环节交汇的枢纽节点。安全生态系统（cosign、notation、Kyverno、OPA Gatekeeper、Ratify）代表多年投资，使策略引擎可以统一执行"所有制品必须签名后部署"的规则，无需区分容器镜像或 RubyGem [4]。

## GPU/AI 工作负载如何重塑容器编排需求

AI 工作负载正在根本性重塑 Kubernetes 编排层的需求结构。根据 CNCF 2026 年 1 月发布的年度调查，82% 的容器用户在生产中运行 Kubernetes，66% 的托管生成式 AI 模型组织使用 Kubernetes 执行部分或全部推理工作负载 [1]。

### 从微服务到 AI 工作负载的需求断层

标准 Kubernetes 调度和资源管理 API 为微服务设计，不原生支持 AI 推理所需的细粒度 GPU 资源切分、复杂批量调度和模型服务端点的特定流量模式 [2]。具体需求断层包括：

- **批量调度与帮派调度**：AI 训练任务需要 gang scheduling——请求 120 个 GPU 但仅 100 个可用时，100 个 GPU 空闲等待，浪费成本并阻塞工作。Volcano 和 Apache Yunikorn 开创了多节点训练任务仅在所有请求资源就绪时才启动的模式 [1]。
- **GPU 动态切分**：静态预切分 GPU 导致碎片化和低利用率。DAS（Dynamic Accelerator Slicer）提供按需、即时的 GPU 切片分配，使用 NVIDIA MIG 技术动态创建和销毁 GPU 分区以匹配工作负载需求 [2]。
- **推理感知路由**：Gateway API Inference Extension（GAIE）在标准 Gateway API 上引入模型版本管理、自适应后端选择和 prefix-cache-aware 路由，基于实时模型和加速器指标路由请求 [2]。

### 编排层的新增子链路

AI 工作负载催生的 K8s 原生组件形成了编排层内部的新子链路：

| 组件 | 产业链角色 | 价值/效率影响 |
|---|---|---|
| Kueue | 批量调度与队列管理 | 总完成时间降低 15%，99 分位准入延迟低于 25ms [2] |
| DAS | GPU 动态切分 | 利用 NVIDIA MIG 按需分配 GPU 切片，减少空闲成本 [2] |
| GAIE | 推理感知网络路由 | 基于队列长度、prefix cache 命中率和 LoRA 适配器可用性路由 [2] |
| KServe | 标准化模型服务 | 自动伸缩、版本管理和流量切分；集成 Knative 实现 GPU 工作负载缩容至零 [1] |
| Karpenter | 基础设施弹性供给 | 精确配置节点类型并积极释放空闲容量以优化成本 [1] |
| SOCI | 镜像启动加速 | 减少大型镜像（模型服务容器）启动时间 [1] |

GPU 获取与利用率是当前全链路最大瓶颈——"瓶颈不是 CPU 或内存，而是在需要时获取 GPU 并最大化利用率" [1]。GPU 共享技术已演进出多种模式：多实例 GPU（MIG）分区、时间分片交错执行、多进程服务（MPS）并发内核和 Kubernetes 动态资源分配（DRA）运行时 GPU 分区与重分配 [1]。

在控制面层面，标准 etcd 在超大规模下成为瓶颈——虽然 etcd v3.6.0 实现了 50% 内存降低，但 10 万+ 节点集群需要重新思考控制面数据存储 [1]。多集群调度成为关键，Armada（CNCF Sandbox）将多个集群视为单一资源池进行智能工作负载分发和全局队列管理 [1]。

## 价值与瓶颈传导

产业链价值向两个方向集中：一是镜像仓库分发层因 OCI 制品泛化而成为多环节交汇枢纽，二是编排调度层因 AI 工作负载而扩展出批量调度、GPU 切分和推理路由等高价值子链路。瓶颈传导路径为：GPU 供给短缺 → 调度层需要专用组件（Kueue/DAS/GAIE） → 镜像层需要启动加速（SOCI） → 控制面需要超越 etcd 的可扩展性方案。CNCF 社区已启动 Kubernetes "AI 一致性"认证计划，旨在定义跨一致性集群运行 AI 工作负载的基线能力 [1]。

## 参考资料

1. [The great migration: Why every AI platform is converging on Kubernetes](https://www.cncf.io/blog/2026/03/05/the-great-migration-why-every-ai-platform-is-converging-on-kubernetes/) — Vara Bonthu, Amazon Web Services Inc.（CNCF Member Post），2026-03-05
2. [Kubernetes meets GenAI: evaluating performance for AI inference workloads](https://research.redhat.com/blog/article/kubernetes-meets-genai-evaluating-performance-for-ai-inference-workloads/) — Sai Sindhur Malleni 等，Red Hat Research Quarterly（Summer 2026），2026
3. [Gitless GitOps: Using OCI Registries as a Secure, Trusted Hub for Multi-Zone Replication of Signed Artifacts](https://goharbor.io/blog/harbor-as-universal-oci-hub/) — Stéphane Este-Gracias（CNCF Ambassador），Harbor，2025-07-08
4. [What Package Registries Could Borrow from OCI](https://nesbitt.io/2026/02/18/what-package-registries-could-borrow-from-oci/) — Nesbitt（引自 OCI 官方规范与发布说明），2026-02-18
