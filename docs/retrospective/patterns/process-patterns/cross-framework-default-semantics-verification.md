---
id: "cross-framework-default-semantics-verification"
title: "跨框架默认语义先验核实与下游自洽反证模式"
type: "process-pattern"
date: "2026-10-09"
maturity: "L1-draft"
source: "retro-20261009-caffe-pool-ceil-shape"
related_patterns: ["import-path-priori-verification", "validation-semantic-gap"]
tags: ["deep-learning", "shape-inference", "caffe", "pytorch", "onnx", "cross-framework", "verification", "falsification"]
domain: "process"
layer: "process"
---

# 跨框架默认语义先验核实与下游自洽反证模式

跨框架手工推导模型行为（张量 shape、对齐、舍入等）时，先逐个核实目标框架的**默认参数语义**，再用下游约束（末端维度、零尺寸、多分支一致性）对推导结果做反向证伪；禁止把 A 框架的"默认值直觉"迁移为 B 框架的断言。

## 触发场景

- 在 Caffe / PyTorch / ONNX / TensorFlow 等框架间移植模型、转换前端或做逐层精度对齐，需要手工推导中间张量 shape
- 算子存在**同名但默认值相反/不同**的参数：池化取整方向（ceil/floor）、padding 语义、dilation、插值坐标对齐（`align_corners` / `half_pixel_centers`）、量化舍入模式等
- 推导链较长（卷积、池化交错多层），末端接 InnerProduct/Reshape/Concat 等对尺寸敏感的层
- 手头没有可直接运行的目标框架环境，只能做静态推导

**不适用于**：

- 单一框架内、官方文档明确且已被本项目多次验证的常识性推导
- 与框架默认值无关的纯算术（如已知全部参数后的恒等计算）
- 有权威 shape inference 工具可直接给出逐节点结果且已验证可信的场景（此时应以工具输出为准）

## 核心做法

### 1. 枚举"默认值决策点"

沿推导链逐层列出所有依赖框架默认值的位置：池化取整方向（ceil/floor）、卷积/池化 pad 默认、stride 默认、数据布局（NCHW/NHWC）、InnerProduct 的 `axis` 等；另把 dilation 这类各框架默认虽相同（均为 1）、但手工推导时极易漏带进公式的参数单列核查。显式写出的参数也要确认其在目标框架中的语义（例如 Caffe 池化的 floor/ceil 并非显式参数，而是编译进实现的固定行为）。

### 2. 证据核实每个默认值（断言之前）

对每个决策点，按证据等级查**目标框架**的权威来源：**框架源码 > 官方文档/API 契约 > 第三方教程 > 个人记忆**。

- 源码锚点示例（BVLC Caffe）：
  - Convolution（`base_conv_layer.cpp`）：`out = (H + 2·pad − kernel) / stride + 1`，C++ 整数除法，正数下等价 **floor**；
  - Pooling（`pooling_layer.cpp`）：`pooled = ceil((H + 2·pad − kernel) / stride) + 1`，即**默认 ceil**；仅当 pad>0 且末窗完全落在 padding 区时部分版本会减 1。
- 跨框架默认值对照（截至沉淀时的主流版本，使用前仍须按第 2 步复核）：

| 框架 | Convolution 输出 | MaxPool 输出取整 |
|------|------------------|------------------|
| Caffe（BVLC） | floor（整数除法） | **ceil**（默认即 ceil 模式） |
| PyTorch | floor | floor（`ceil_mode=False` 默认） |
| ONNX | floor（Conv） | floor（MaxPool `ceil_mode=0` 默认） |

### 3. 逐层推导并标注公式

每一层输出后同时记录所用公式与取整方向，整除与不整除的层分别标记（整除时 floor/ceil 结果相同，问题只会在出现余数时暴露）。

### 4. 下游自洽性反证（不可省略）

用末端结构对推导结果做反向校验，任一不满足即回查：

- 末端 InnerProduct 的展平维 `K`（Caffe 默认从 `axis=1` 起展平，`K = ∏` 后置维度）是否与**权重的输入维**一致——Caffe 权重形状为 `[num_output, K]`、PyTorch `nn.Linear` 为 `[out_features, in_features]`，`K` 均对应**第二维**而非第一维；
- 全链路是否出现 0 或负的空间尺寸；
- 共享同一 bottom 的多个分支（双头网络）看到的 shape 是否一致；
- Reshape/Concat 层的目标形状是否与推导值匹配。

### 5. 条件允许时做最小 shape spike

用目标框架构造仅含相关算子的最小网络，喂一个最小输入跑一遍，打印输出 shape。30 秒的 spike 可以替代整轮口头争论；无法运行时，至少以源码片段作为证据留存。

### 6. 修正时连锁重算

某个中间层被纠正后，必须从该层开始把**所有下游层**全部重推一遍，禁止只改被质疑的那一层或最终结论。

## 反模式

- ❌ **跨框架默认值平移**：用 PyTorch `MaxPool2d` 的 floor 直觉给 Caffe 池化下"默认 floor"的断言——两者默认方向恰好相反。
- ❌ **只前向推导、不做下游反证**：推出"特征图 2×2 上再做 k3 卷积→0×0"这种结论时，末端 FC 维度矛盾与零尺寸本应当场触发回查，却反向输出"网络无法前向"的错误警告。
- ❌ **整除层给出虚假安全感**：前几个池化窗口恰好整除（floor/ceil 同值），便默认后续层规则相同；余数一出现，每层静默偏差 1 并层层累积。
- ❌ **被质疑后才查源码**：证据核实发生在首次断言之后，等于把未经核实的假设当成结论交付。
- ❌ **点状修正不连锁**：纠正一个池化层尺寸后不重算后续卷积/池化/FC，留下新的不一致。
- ❌ **以博客或记忆替代契约**：引用过时二手公式，不区分框架版本与变体分支。

## 检验标准

做完之后怎么知道做对了？

1. **证据完备**：每个默认值决策点都能指向目标框架的源码或官方文档，无"我记得是……"式断言。
2. **下游闭合**：末端 FC 输入维、空间尺寸正性、多分支 shape 一致性、Reshape/Concat 目标形状四项反证全部通过。
3. **可复算**：逐层公式与取整方向成文，第三人可按记录独立复算出相同 shape。
4. **修正有连锁**：任何中间层更正后，全下游 shape 表已同步更新并再次通过第 2 项。
5. **（可选）运行期证据**：关键层有最小 spike 或真实网络的 shape 打印佐证。

## 源案例（2026-10-09）

> 完整事实链与四元组洞察见复盘报告：[2026-10-09-caffe-pool-ceil-shape-inference-retro.md](../../reports/2026-10-09-caffe-pool-ceil-shape-inference-retro.md)

对一个 VGG 式三段卷积池化 + 双头 FC 的 Caffe 网络（输入 1×3×120×120，全部卷积 k3/s1/pad0、池化 k2/s2）做静态 shape 推导时，初轮误用 floor 计算 Caffe 池化，得到 pool1=12、pool2=4、conv3_1 输出 2×2，并据此错误判定最后一个 k3 卷积输出尺寸为 0、网络不可前向。经源码核实改为 Caffe ceil 规则后连锁重算：

| 层 | 初轮（错误 floor） | 修正（Caffe ceil） |
|----|--------------------|--------------------|
| pool1（入 25×25） | 12×12（⌊23/2⌋+1） | **13×13**（⌈23/2⌉+1） |
| conv2_1 / conv2_2（k3, s1） | 10×10 / 8×8 | **11×11 / 9×9** |
| pool2（入 8×8 vs 9×9） | 4×4（⌊6/2⌋+1） | **5×5**（⌈7/2⌉+1） |
| conv3_1（k3, s1） | 2×2 | **3×3** |
| conv3_2（k3, s1, pad0）输入/输出 | 2×2 / **0×0**（错误警告） | **3×3 / 1×1**，即 1×80×1×1 |
| 末端两 FC 的展平维 K | 自相矛盾 | **80**，双分支一致，网络自洽 |

## 迁移示例

这个模式还能用在什么其他场景？

- **量化参数推导**：跨框架校准时对称/非对称量化默认、截断与四舍五入（round-to-nearest vs truncate）、zero-point 约定不同，须以目标工具链实现核实。
- **图像预处理对齐**：resize 的 `align_corners` / `half_pixel_centers`、像素归一化区间在 OpenCV/PIL/TorchVision/TF 间默认值不同，精度对齐前先核实。
- **ONNX 前端转换**：MaxPool `ceil_mode`、Pad 的默认坐标模式、Resize 的 `coordinate_transformation_mode` 等跨版本差异。
- **跨数据库/语言迁移**：SQL 隔离级别、字符串 collation、时区与编码默认值跨系统迁移时的行为推导。
- **序列化与文件格式**：换行符（LF/CRLF）、字节序、压缩算法默认窗口大小等跨平台默认值假设。
