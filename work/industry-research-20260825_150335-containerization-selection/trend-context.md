# macro（macro.md）

## 核心判断
全球容器化技术选型正被两大政策力量重塑：欧盟以 CRA、NIS-2、DORA 和 Data Act 构成的数字主权法规体系，将 SBOM 透明度、漏洞报告时限和管辖权控制平面隔离作为市场准入与合规条件，直接驱动容器安全工具链选型和 Kubernetes 平台架构决策[1][3]；美国 EO 14028 通过联邦采购推动 SBOM 与安全开发实践，但 OMB M-26-05（2026年1月）已将统一的自我证明要求转为风险导向的分散审计[3]。中国以信创政策推动容器技术国产化，但本土生态在 CNCF 仅主导2个项目，安全市场碎片化严重，尚无厂商具备全链条云原生安全产品[4]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [From data residency to digital sovereignty: Architectural patterns for cloud native platforms](https://www.cncf.io/blog/2026/06/16/from-data-residency-to-digital-sovereignty-architectural-patterns-for-cloud-native-platforms/) — Hrittik Roy, CNCF Ambassador，2026-06-16
3. [State of the art - Supply Chain & GRC](https://github.com/RedHatResearch/sbom-security/issues/2) — J2kub（RedHatResearch），2026-07-02
4. [进一步筑牢云原生安全底座](http://www.rmlt.com.cn/2025/0418/728055.shtml) — 魏亮（中国信息通信研究院副院长），引自《学习时报》，2025-04-18

# market（market.md）

## 核心判断
全球 Kubernetes 市场在 2026 年估计为 31.3 亿美元，2026-2031 年复合年增长率（CAGR）为 21.85%，预计 2031 年达 84.1 亿美元[1]；更广义的容器编排市场 2026 年估计为 27 亿美元，2025-2030 年 CAGR 为 31.8%[4]。目前尚无单一权威来源覆盖"容器化技术"全口径市场规模，已有数据集中于编排/管理层。Kubernetes 生产采用率达 82%（CNCF 2025 年度调查[3]），行业已跨越早期采用阶段进入规模化渗透期。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [Kubernetes Market - Mordor Intelligence](https://www.mordorintelligence.com/es/industry-reports/kubernetes-market) — Mordor Intelligence，2026
3. [Kubernetes Established as the De Facto 'Operating System' for AI as Production Use Hits 82% in 2025 CNCF Annual Cloud Native Survey](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/) — Cloud Native Computing Foundation (CNCF)，2026-01-20
4. [Container Orchestration Market Size Report, 2025-2030](https://www.grandviewresearch.com/industry-analysis/container-orchestration-market-report) — Grand View Research，2025

# 容器化技术产业链分析（chain.md）

## 核心判断
容器化技术产业链已从"微服务编排"演变为"AI 工作负载统一调度平台"，核心链条为：OCI 标准规范层 → 镜像仓库分发层 → Kubernetes 编排调度层 → AI 工作负载层。OCI Distribution 规范（v1.1.0）使镜像仓库从纯容器存储扩展为通用制品枢纽，连接了构建、安全签名、策略治理和部署分发多个相邻环节 [3][4]；GPU 资源获取与利用率成为全链路最大瓶颈——82% 的容器用户在生产中运行 Kubernetes，66% 的 GenAI 托管组织使用 Kubernetes 执行推理工作负载，但标准 K8s 调度原语无法原生处理细粒度 GPU 切分和批量调度，催生了 Kueue、DAS、GAIE 等专用组件 [1][2]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [The great migration: Why every AI platform is converging on Kubernetes](https://www.cncf.io/blog/2026/03/05/the-great-migration-why-every-ai-platform-is-converging-on-kubernetes/) — Vara Bonthu, Amazon Web Services Inc.（CNCF Member Post），2026-03-05
2. [Kubernetes meets GenAI: evaluating performance for AI inference workloads](https://research.redhat.com/blog/article/kubernetes-meets-genai-evaluating-performance-for-ai-inference-workloads/) — Sai Sindhur Malleni 等，Red Hat Research Quarterly（Summer 2026），2026
3. [Gitless GitOps: Using OCI Registries as a Secure, Trusted Hub for Multi-Zone Replication of Signed Artifacts](https://goharbor.io/blog/harbor-as-universal-oci-hub/) — Stéphane Este-Gracias（CNCF Ambassador），Harbor，2025-07-08
4. [What Package Registries Could Borrow from OCI](https://nesbitt.io/2026/02/18/what-package-registries-could-borrow-from-oci/) — Nesbitt（引自 OCI 官方规范与发布说明），2026-02-18

# 容器化技术行业竞争格局分析（competition.md）

## 核心判断
容器运行时与编排市场的竞争格局已从Docker单一主导演变为场景化分层结构：运行时层面，containerd占据Kubernetes生产集群（95%的K8s集群），Docker保留开发者桌面（67%开发者使用），Podman切入安全与CI/CD场景（19%），34%的组织采用多运行时混合策略；编排层面，Kubernetes形成准垄断（82%生产部署率，较2023年增长24.2%），边缘K8s成为新竞争前沿（38亿美元市场，Red Hat、SUSE、Microsoft三足鼎立）。WebAssembly与传统容器以互补关系为主而非直接替代。

## 关键证据
容器运行时市场经历三个关键转折，终结了Docker的无可争议主导地位：第一，2021年Docker Desktop许可变更，大型企业（250人以上或年收入超1000万美元）须付费使用，驱动企业用户寻求替代方案[4]；第二，2022年Kubernetes 1.24移除dockershim，Docker不再作为K8s直接运行时，containerd成为K8s默认选择[4]；第三，开放容器计划（OCI）标准化推进，打破Docker对容器镜像格式的私有控制，为containerd、CRI-O、Podman等替代运行时的崛起铺平道路[4]。
**成本驱动**：Docker Desktop的付费门槛（Pro版$9/用户/月、Team版$15/用户/月、Business版$24/用户/月）促使大型企业评估替代方案[4]。Docker在2024至2025年间将Docker Hub、Build Cloud、Scout和Testcontainers Cloud打包为单一订阅，并引入消费定价（针对Docker Hub镜像拉取和存储），影响头部3%商业账户[4]。然而Docker通过扩展市场（100+插件，含Lens和Snyk）、macOS VirtioFS文件同步和WSL集成维持其开发者生态锁定[4]。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
4. [Docker vs Podman in 2026: Which Container Runtime Should You Use](https://daily.dev/blog/docker-vs-podman-container-runtime-which-to-use) — daily.dev（Nimrod Kramer），2026年4月9日

# 容器化技术行业重点企业研究（companies.md）

## 核心判断
容器生态已从早期 Docker 单一主导格局分化为场景化工具矩阵。Docker Inc. 锁定开发者桌面市场并以按席位订阅模式变现，Sacra 估算 2024 年 ARR 达 $207M [1]；Red Hat 以 Podman/Buildah 工具链替代 Docker 在 RHEL 中的位置，并通过 OpenShift 平台提供零 CVE 镜像和安全扫描 [1][2]；SUSE/Rancher 以 K3s 覆盖边缘场景、RKE2 覆盖政府合规场景，RKE2 是唯一获得 DISA STIG 认证的 Kubernetes 发行版 [3]；Sidero Labs 以 Talos Linux 不可变 API 驱动操作系统开辟容器 OS 创新路线 [4]；Cosmonic 基于 CNCF 沙箱项目 wasmCloud 探索 WebAssembly 替代/互补技术路径 [5]。五家企业分别代表容器生态的开发者桌面、企业运行时安全、边缘与合规编排、容器 OS 创新和 Wasm 运行时五个关键环节，差异化策略围绕安全合规、资源效率、开发者体验和架构范式四个维度展开。

## 资料限制
专题稿未单列资料限制。

## 上述段落引用的参考资料
1. [Docker](https://sacra.com/c/docker/) — Sacra，2025 年 12 月 7 日更新
2. [What's new for developers in Red Hat OpenShift 4.22](https://developers.redhat.com/articles/2026/07/14/whats-new-developers-red-hat-openshift-4-22) — Red Hat Developer，2026 年 7 月 14 日
3. [When to Use K3s and RKE2](https://www.suse.com/c/zh-hans/rancher_blog/when-to-use-k3s-and-rke2/) — SUSE，2022 年 12 月 14 日
4. [Hiro Capital Leads $4.0 Million Investment in Sidero Labs to Accelerate Development of Kubernetes Solutions](https://www.vcaonline.com/news/2024102306/hiro-capital-leads-4-0-million-investment-in-sidero-labs-to-accelerate-development-of-kubernetes-solutions/) — VCA Online（引自 Sidero Labs），2024 年 10 月 23 日
5. [Cosmonic](https://startupintros.com/orgs/cosmonic) — StartupIntros，2026 年 7 月 13 日更新
