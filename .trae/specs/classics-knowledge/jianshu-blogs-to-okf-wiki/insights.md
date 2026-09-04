# 洞察与束结构设计（I 阶段产物）

> 基于 `facts.md`（F-101~F-200 Notebook1 / F-201~F-265 Notebook2 / F-301~F-363 Notebook3）提炼。
> 洞察格式：陈述（Insight）→ 证据（Evidence）→ 反常识（Counter-intuitive）→ 行动（Action）。

## 一、Notebook 1：matplotlib & pillow & networkx 手册

### 洞察 1：旧教程的价值在于"用法叙事"而非"源码架构"
- **陈述**：本套连载（2020 年前后）是面向初学者的"用法手册"，与既有 matplotlib 束（基于 3.x 源码的架构教程）互补——它提供源码束缺失的实战场景（事件处理、形状路径、分形、神经网络图可视化）。
- **证据**：F-101~F-105 分形（Chaos Game 三角形）、F-121~F-128 事件处理、F-161~F-168 patches/path、F-106~F-113 用 NetworkX 画神经网络 DAG。
- **反常识**：架构教程讲"类怎么设计"，旧用法教程讲"函数怎么调"——二者面向不同读者，不能互相替代；给既有束补 examples/ 而非改写 concepts/，保持束内"架构叙述"纯净。
- **行动**：matplotlib 束仅增量扩展 examples/（事件处理、patches/path、分形），networkx/pillow 另立新束。

### 洞察 2：三库同源示例生态——绘图库共用一套"数据→画布→渲染"心智
- **陈述**：matplotlib / Pillow / NetworkX 三类绘图场景（矢量图、位图、图论图）共享"构建数据对象 → 画到画布 → 保存/展示"的流程，但 API 范式迥异（pyplot 状态机 vs ImageDraw 立即模式 vs nx.draw 布局）。
- **证据**：F-110 `nx.draw(G, pos, node_color=..., cmap=plt.cm.Paired)`、F-141 `ImageDraw.Draw(im)`、F-173 `plt.figure(figsize=(10, 10))`。
- **反常识**：NetworkX 的"画图"不是 NetworkX 核心能力——它委托 matplotlib 渲染（F-112 `draw_networkx_nodes/edges/labels`），图论算法与可视化是解耦的两层。
- **行动**：三个束置于同一 `jishu/data/pydata/` 分组，学习路径串联"matplotlib 图形基础 → networkx 图可视化 → pillow 位图处理"。

### 洞察 3：2020 版 API 与现行版本存在漂移，必须标注时点
- **陈述**：教程中不少 API 调用方式（networkx 2.x 的 `nx.draw` 参数形态、matplotlib 老接口）在现行版本（networkx 3.x、matplotlib 3.8+）中行为/签名已变化。
- **证据**：F-110 `node_color=range(node_count)` 这类用法在现行 matplotlib 下需 `vmin/vmax` 或颜色映射调整；F-122 `mpl_connect('motion_notify_event', ...)` 事件名与现行一致但部分回调行为演进。
- **反常识**："旧"不等于"错"——核心心智模型（DAG、事件回调、图着色）十年不变，变的只是参数形态；照抄旧代码会触发 DeprecationWarning。
- **行动**：所有文档 frontmatter 标注 2020 时点；对漂移 API 给出「现状」小节并注明信源，禁止把旧 API 陈述为现行行为。

## 二、Notebook 2：开源的世界

### 洞察 1：开源贡献的"非编码入口"与文档优先
- **陈述**：连载强调贡献开源不限于提交代码——文档、测试、翻译、答疑、社区运营都是贡献形态（F-260~F-265）。
- **证据**：F-262 项目文档（README/贡献指南/许可）被列为项目必备；F-260 贡献原因含学习、署名、社区归属。
- **反常识**：多数初学者以为"开源 = 写代码"，而项目最稀缺的往往是文档与 triage。
- **行动**：opensource 束以"参与路径 + 项目准备（README/许可证/贡献指南）"为主线组织，README 模板独立成篇（F-220~F-222）。

### 洞察 2：Git 团队协作的核心是"分支纪律"而非命令技巧
- **陈述**：Git 相关两篇（F-213~F-219、F-238~F-247）的重心是分支模型（Git Flow、feature/release/hotfix）与团队工作流约定。
- **证据**：F-241 Git Flow 规则表、F-242~F-244 feature/release/hotfix 全流程、F-245 裸库共享、F-246 版本号 x.y.z。
- **反常识**：`--no-ff`（F-217）、`git tag`（F-219）等"技巧"之所以存在，是为了服务可追溯的分支纪律；命令多但纪律缺失则协作失序。
- **行动**：git 束以"学习路线 → 分支模型 → 团队协作 → 下载加速技巧"组织，突出约定即生产力。

### 洞察 3：GitHub 生态资产盘点——Actions 自动化与内容分发的双重价值
- **陈述**：GitHub Actions（F-201~F-212）与 Gist（F-225~F-229）、下载加速（F-256~F-259）共同构成"托管 + 自动化 + 分享"的平台闭环。
- **证据**：F-202 `.github/workflows` 目录约定、F-203 触发事件、F-205 checkout 引用语法、F-207 构建矩阵、F-225 公开/机密 Gist、F-227 GeoJSON 嵌入。
- **反常识**：Actions 的"工作流即代码"让 CI/CD 从外部服务迁入仓库本身——文档与自动化同仓，可审计可版本化。
- **行动**：github 束覆盖 Gist 与 Actions 两主题，将 workflow 语法（on/runs-on/jobs/needs）拆为独立概念文档。

## 三、Notebook 3：无人驾驶

### 洞察 1：2020 年自动驾驶开源栈以 Autoware + ROS2 + DDS 为骨架
- **陈述**：连载以 Autoware.Auto（Autoware 三系：AI/IO/Auto，F-333）为应用载体，以 ROS2（F-324~F-332）与 DDS（F-312~F-318）为通信底座。
- **证据**：F-319~F-323 ADE 构建环境、F-349~F-353 WSL2 部署 autoware.auto、F-336 目标检测演示命令链。
- **反常识**：Autoware 的安装痛点不在 Autoware 本身，而在开发环境（ADE 容器、DDS 网络、显示转发）——安装文档 80% 篇幅在讲环境。
- **行动**：autoware 束按"环境（WSL2/Ubuntu/ADE）→ 基础概念 → 演示"组织，环境篇独立成文。

### 洞察 2：DDS 是 ROS2 的通信抽象，QoS 决定行为
- **陈述**：ROS2 弃用 ROS1 的 master/自研消息层，改为建立在 DDS 上的发布订阅（F-325 发布订阅、F-326 节点、F-312~F-318 DDS QoS/发现/安全）。
- **证据**：F-313 QoS 策略、F-316 动态发现、F-318 DomainParticipant、F-327 多 DDS 供应商。
- **反常识**：ROS2 的"发现机制"不在 ROS2 而在 DDS——更换供应商即可更换底层实现，ROS2 层保持 API 稳定。
- **行动**：dds 束独立成束解释 QoS/发现/安全，ros2 束聚焦节点/话题/客户端库等 ROS2 层概念，二者通过交叉链接关联。

### 洞察 3：数据是无人驾驶的"隐形燃料"，数据集清单即行业地图
- **陈述**：F-301~F-311 列出 KITTI/Cityscapes/comma.ai/Udacity/nuScenes/H3D 等十余个数据集，构成 2020 年行业数据版图。
- **证据**：F-301~F-311 逐数据集条目（规模、任务类型、来源机构）、F-354~F-356 Autonomous 资源（paperswithcode/GitHub/Kaggle）。
- **反常识**：算法模型更新极快，但主流公开数据集的"任务划分"（感知/预测/规划）多年稳定——数据集文档比算法文档更抗过时。
- **行动**：ecosystem 束承载数据集清单、汽车术语（ECU/CAN，F-362~F-363）、资源列表、WSL2 GPU 深度学习环境四类"生态资产"，时点标注到 2020 并给出现状。

## 四、知识地图与束结构

### 放置决策（已定）
| Notebook | 位置 | 束 |
|---|---|---|
| NB1 | `jishu/data/pydata/` | matplotlib（扩展现有束 examples/）、networkx（新束）、pillow（新束） |
| NB2 | `jishu/dev/`（新分组） | git、github、opensource |
| NB3 | `jishu/autonomous/`（新分组） | autoware、ros2、dds、ecosystem |

### 束内文档清单（每束：index.md + log.md + concepts/ + 视内容 examples/ + references/）
- **matplotlib 扩展**（仅 examples/ + log/index 同步）：`examples/event-handling.md`、`examples/patches-and-path.md`、`examples/fractal.md`
- **networkx**：concepts（节点与边、图的可视化与布局、路径、DAG 与有向图）、examples（画神经网络、简单路径）
- **pillow**：concepts（图像基础与处理、缩放与合成、ImageDraw 绘制、图像特效）、examples（手绘石雕油画、电子显示屏）
- **git**：concepts（学习路线、分支模型与团队协作、下载加速）
- **github**：concepts（创建 Gist、GitHub Actions 工作流语法）
- **opensource**：concepts（开源参与指南、开启开源项目、README 模板、无版权图库、程序员网站）
- **autoware**：concepts（WSL2 环境、Ubuntu/ADE 环境、Autoware.Auto 基础）
- **ros2**：concepts（ROS2 概念总览）
- **dds**：concepts（DDS 与 QoS）
- **ecosystem**：concepts（无人驾驶数据集、汽车系统术语、Autonomous 资源、WSL2 GPU 深度学习环境）

### 学习路径
1. pydata：matplotlib examples → networkx（图论 + 可视化）→ pillow（位图处理）
2. dev：git（协作纪律）→ github（托管与自动化）→ opensource（参与与项目准备）
3. autonomous：dds（通信底座）→ ros2（应用框架）→ autoware（整车栈）→ ecosystem（数据/术语/资源）
