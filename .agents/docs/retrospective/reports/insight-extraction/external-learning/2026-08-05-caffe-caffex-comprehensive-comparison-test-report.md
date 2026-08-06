---
title: Caffe 两实现（caffe-ffi / caffex）综合对比测试报告
date: 2026-08-05
source: .trae/specs/caffe-comprehensive-comparison-test
type: insight-extraction/external-learning
---

# Caffe 两实现（caffe-ffi / caffex）综合对比测试报告

## 1. 测试配置与环境信息

| 项目 | caffe-ffi | caffex |
|------|-----------|--------|
| 目标库 | `projects/xuanspace/libs/caffe-ffi` | `projects/xuanspace/vendor/caffe/caffex` |
| 基准环境 | `apps/caffe-ffi-jupyter`（`caffe-ffi-jupyter:latest` 镜像） | `vendor/caffe/docker/origin`（`caffe-cpu:origin-runtime` 镜像） |
| Python | 3.14.6（conda env `caffe-ffi`） | 3.10（pycaffe） |
| numpy | 2.5.1 | 1.26.4 |
| caffe_ffi 版本 | 0.1.0 | — |
| tvm_ffi 版本 | 0.1.13.post2（本地源码 editable） | — |
| C++ 扩展 | `_caffe_ffi.so` 已加载（native=True） | `build/tools/caffe` |
| 推理接口 | `caffe_ffi.read_net` / `net_from_param` / `net.forward()` | `caffe.Net` / `net.forward()` |
| 计算后端 | CPU | CPU |

> 说明：两实现运行于不同 Docker 容器，绝对延迟受容器 CPU 调度影响，**性能数据仅作相对参考**。GPU 均不可用，未采集 GPU 占用。

## 2. 执行摘要

| 测试套件 | 结果 | 通过 | 失败 | 跳过 | 关键备注 |
|----------|------|------|------|------|----------|
| caffe-ffi 核心功能（tests/python） | ✅ PASS | 2107 | 0 | 3 | 3 跳过为已知设计/平台项 |
| caffe-ffi 算子（tests/python/ops，31 算子） | ✅ PASS | 102 | 0 | 3 | Permute 未实现跳过 |
| caffe-ffi 网络（预训练模型） | ⚠️ PARTIAL | 1 | 3 | 0 | **权重未加载缺陷**（异常 A-001） |
| caffex 网络（预训练模型） | ⚠️ PARTIAL | 3 | 1 | 0 | AlexNet 下载中断（环境问题） |
| 跨实现算子精度对比（19 算子） | ✅ PASS | 19 | 0 | 0 | 14 个精确一致，5 个误差≤1e-6 |
| 性能基准（11 算子 × 30 迭代） | ✅ PASS | 11 | 0 | 0 | 见第 4 节 |

**核心结论**：
1. **算子级功能与精度两实现一致**：19 个常用算子全部通过，14 个精确一致，5 个浮点误差 ≤1e-6（由不同累加顺序/实现引起，属正常）。
2. **发现高优先级缺陷 A-001**：caffe-ffi 的 `read_net(proto, caffemodel)` 未加载真实权重，导致网络级推理输出垃圾值/NaN。算子级测试不受影响（见第 6 节）。
3. **CPU 资源占用**：caffex 利用 OpenMP 多核并行（峰值 ~870%），caffe-ffi 以单/低线程为主（峰值 ~71%），两者资源利用特征显著不同（见第 4.2 节）。
4. **Top-K 分类一致性**：caffex 输出有效分类概率（Top-1=#904）；caffe-ffi 因 A-001 导致 Top-5 概率全 NaN，分类结果无效（见第 3.2 节）。

## 3. 精度对比数据（跨实现算子）

| 算子 | caffe-ffi | caffex | 最大绝对误差 | 平均绝对误差 | 最大相对误差 | 精确一致 |
|------|-----------|--------|-------------|-------------|-------------|---------|
| convolution | OK | OK | 9.54e-07 | 1.52e-07 | 1.25e-05 | N |
| pooling(MAX) | OK | OK | 0 | 0 | 0 | Y |
| pooling(AVE) | OK | OK | 0 | 0 | 0 | Y |
| relu | OK | OK | 0 | 0 | 0 | Y |
| sigmoid | OK | OK | 5.96e-08 | 1.19e-08 | 1.36e-07 | N |
| tanh | OK | OK | 5.96e-08 | 1.39e-08 | 1.38e-07 | N |
| softmax | OK | OK | 0 | 0 | 0 | Y |
| eltwise_sum | OK | OK | 0 | 0 | 0 | Y |
| eltwise_max | OK | OK | 0 | 0 | 0 | Y |
| inner_product | OK | OK | 1.19e-07 | 5.96e-08 | 1.02e-07 | N |
| batchnorm | OK | OK | 0 | 0 | 0 | Y |
| lrn | OK | OK | 0 | 0 | 0 | Y |
| prelu | OK | OK | 0 | 0 | 0 | Y |
| elu | OK | OK | 0 | 0 | 0 | Y |
| swish | OK | OK | 2.38e-07 | 1.03e-08 | 2.06e-07 | N |
| dropout | OK | OK | 0 | 0 | 0 | Y |
| flatten | OK | OK | 0 | 0 | 0 | Y |
| concat | OK | OK | 0 | 0 | 0 | Y |
| slice | OK | OK | 0 | 0 | 0 | Y |

**精度分析**：多输入算子（Eltwise SUM/MAX、Concat）经 numpy 参考验证，两实现均与参考值完全一致；激活/规约类算子精确一致。仅 conv/sigmoid/tanh/inner_product/swish 存在 1e-7 量级浮点误差，源于不同 MAC 累加顺序与近似实现，属正常精度容差（float32 ULP 级别）。

### 3.2 Top-K 分类一致性（网络级）

在真实预训练 InceptionV1 上，对同一固定输入（seed=42，ImageNet 均值预处理）分别推理，取第一个 batch 样本计算 Top-K（`topk_analysis.py`）：

| 指标 | caffex | caffe-ffi |
|------|--------|-----------|
| 权重 | 真实预训练权重（copy_from） | 占位权重（A-001，未加载） |
| 输出 blob / 形状 | prob / (10,1000) | prob / (1,1000) |
| Top-1 类别索引 | **904** | 672 |
| Top-5 类别索引 | [904, 741, 885, 611, 911] | [672, 657, 658, 659, 660] |
| Top-1 概率 | 0.0012（有限） | **NaN** |
| Top-5 概率 | 全有限（~0.0011） | **全 NaN** |
| 输入含 NaN/Inf | 否 | 否 |
| 输出含 NaN/Inf | 否 | **是（NaN）** |

**结论**：caffex 基于真实权重产生有效分类概率，Top-1 概率为 0.0012（随机输入下接近均匀分布，符合预期）；caffe-ffi 因异常 A-001（权重未加载）输出概率全为 **NaN**，其 Top-K 类别索引无意义、与 caffex 不一致（Top-1 命中 0/1，Top-5 命中 0/5）。这从**分类任务层面**再次证实 A-001 的严重性：不仅数值溢出，还直接破坏最终分类输出可用性。

## 4. 性能对比数据

延迟（mean_ms，30 次迭代，容器内 CPU）：

| 算子 | caffe-ffi | caffex | 比值(ffi/cx) | caffe-ffi FPS | caffex FPS |
|------|-----------|--------|--------------|---------------|------------|
| convolution | 0.618 | 0.608 | 1.02x | 1618 | 1644 |
| pooling | 5.006 | 0.450 | 11.14x | 200 | 2225 |
| relu | 0.456 | 0.303 | 1.51x | 2193 | 3303 |
| sigmoid | 0.435 | 0.518 | 0.84x | 2301 | 1930 |
| tanh | 0.453 | 0.552 | 0.82x | 2208 | 1810 |
| softmax | 0.459 | 0.346 | 1.32x | 2179 | 2886 |
| inner_product | 4.646 | 1.020 | 4.56x | 215 | 981 |
| batchnorm | 0.610 | 0.328 | 1.86x | 1638 | 3047 |
| lrn | 0.644 | 0.397 | 1.62x | 1552 | 2521 |
| eltwise_sum | 8.015 | 0.554 | 14.46x | 125 | 1805 |
| concat | 0.805 | 0.532 | 1.51x | 1242 | 1878 |

**性能分析**：
- caffe-ffi 在计算密集型算子（pooling、inner_product、eltwise_sum）上慢 4~14 倍，与 FFI 边界开销及容器资源差异相关；caffex 为原生 C++ 直接调用，开销更低。
- 元素级算子（sigmoid/tanh）caffe-ffi 略快（0.82~0.84x），可能受容器调度抖动影响。
- `eltwise_sum` 与 `pooling` 在 caffe-ffi 中延迟的 std 较大（2.5~2.7ms），存在偶发长尾，建议关注分配/GC。

### 4.2 CPU 资源占用率

通过 `/proc/<pid>/stat` 与 `/proc/stat` 采样推理进程 CPU 占用（`cpu_monitor.py`，不依赖外部库），结果（% 相对整机多核）：

| 指标 | caffe-ffi | caffex |
|------|-----------|--------|
| 物理/vCPU | 16 | 16 |
| 采样时长 | 8.69 s | 16.35 s |
| 平均 CPU 占用 | **10.08%** | **25.89%** |
| 峰值 CPU 占用 | 70.89% | **870%** |
| 采样方式 | linux /proc | linux /proc |
| 基准算子/迭代 | 11 算子 × 30 | 11 算子 × 800 |

**分析**：
- **并行特征差异显著**：caffex 峰值占用达 870%（~8.7 核），证实其 OpenMP 多核并行在算子级基准中生效；caffe-ffi 峰值仅 ~71%（单/低线程），主要受 FFI 串行桥接及单线程推理限制。
- **稳态平均占用**：caffex（25.89%）高于 caffe-ffi（10.08%），与 caffex 持续利用多核并行一致；caffe-ffi 因算子耗时中大量为 FFI/分配开销，纯计算占比低，CPU 占用更分散。
- **GPU**：两容器均无 GPU，未采集 GPU 占用率。
- **说明**：绝对 CPU% 受容器调度与并发负载影响，峰值反映并行能力上限，平均值反映稳态利用，二者结合解读。

## 5. 算子与网络表现差异分析

### 5.1 算子维度
- **功能一致性**：两实现 19 个算子输出一致（精确或 ≤1e-6），形状全部匹配。
- **实现差异**：caffex 具备 COW 恒等层零拷贝共享、OpenMP 并行、dtype 守卫等优化；caffe-ffi 通过 FFI 桥接，算子逻辑等价但性能路径不同。

### 5.2 网络维度
| 模型 | caffe-ffi | caffex | 差异 |
|------|-----------|--------|------|
| ResNet50 | "PASS"(无NaN) | PASS | ⚠️ caffe-ffi 实为无效输出（权重未加载假阳性） |
| InceptionV1 | FAIL(NaN) | PASS | caffe-ffi 权重未加载 → 指数放大上溢 |
| MobileNetV2 | FAIL(NaN) | PASS | 同上 |
| AlexNet | FAIL(proto损坏) | FAIL(下载中断) | 均为环境/下载问题 |

**关键洞察**：网络级差异**根因是权重加载缺陷（A-001）而非算子精度**。caffex 用真实预训练权重输出正常；caffe-ffi 用占位权重（全 1）推理，activations 逐层指数放大（~10^3/层），最终 float32 上溢（>3.4e38）成 Inf，下游转 NaN。

## 6. 异常情况记录与问题定位建议

### 异常 A-001（高优先级）：caffe-ffi 未加载 caffemodel 真实权重

**现象**：`read_net(prototxt, caffemodel)` 构建的网络，conv1 权重全为 1.0（std=0）、bias 全为 0.2；而 caffex 加载同一 caffemodel 后权重真实（max=1.20, min=-1.04, std=0.196）。

**受控验证**（同一固定输入 seed=42，逐层 max-abs 追踪）：

| 层 | caffe-ffi | caffex | 比值 |
|----|-----------|--------|------|
| data | 2.57 | 2.57 | 1.0 |
| conv1/7x7_s2 | 86.3 | 22.0 | 3.9x |
| conv2/3x3 | 1.97e6 | 39.9 | 49000x |
| inception_3a/output | 1.8e5 | 71.7 | 2500x |
| inception_5a/1x1 | Inf(全12544) | 有限(~70) | ∞ |

**放大链**：conv1(4x) → conv2/3x3(49000x) → inception_3a(2500x) → … → inception_5a float32 上溢 → Inf → NaN。

**为何算子测试通过**：`net_from_param` 从 proto 字符串构建无 caffemodel，权重由 C++ 随机初始化，故算子逻辑本身正确；缺陷仅在带 caffemodel 的 `read_net` 路径暴露。

**定位建议**：
1. 核查 `io.py::read_net` → `_merge_weights` → `caffe_ffi.NewNetFromProtoString` 链路，确认 C++ 端是否读取 `layer.blobs[].data` 并写入层权重。
2. 修复后重跑网络测试（InceptionV1/MobileNetV2/ResNet50），验证输出与 caffex 接近。
3. 附带修复 batch 形状异常：prototxt 输入 batch=10，caffe-ffi 输出 (1,1000) 而 caffex 为 (10,1000)。

### 异常 A-002（环境级）：AlexNet 模型下载
- caffe-ffi：caffemodel 解析报 `Wire format corrupt`（下载损坏）。
- caffex：prototxt 下载 `RemoteDisconnected`（网络中断）。
- **建议**：重新下载并校验 sha1，非实现缺陷。

## 7. 可视化图表

- **性能对比柱状图/FPS 对比/CPU 占用/Top-K**：`test-assets/visualization.html`（ECharts 单文件，6 个图表：延迟对比、FPS 对比、精度误差、CPU 占用、Top-K 分类一致性、异常提示）。
- 关键图：图 1 延迟对比（caffe-ffi 在 pooling/IP/eltwise 显著更高）；图 3 精度误差（多数为 0，conv 等 ≤1e-6）；图 4 CPU 占用（caffex 峰值 870% vs caffe-ffi 71%）；图 5 Top-K（caffex 有效概率 vs caffe-ffi NaN）。

## 8. 复现命令附录

```bash
# 环境
wsl -d Ubuntu-24.04 docker ps -a   # 确认 caffe-ffi-jupyter 运行中

# caffe-ffi 算子精度 + 性能
docker exec caffe-ffi-jupyter bash -lc \
  "export PATH=/opt/conda/envs/caffe-ffi/bin:/usr/bin:/bin && export KMP_DUPLICATE_LIB_OK=TRUE && \
   /opt/conda/envs/caffe-ffi/bin/python .../cross_ops.py .../results all && \
   /opt/conda/envs/caffe-ffi/bin/python .../benchmark_ops.py /tmp/bench_ffi.json 30"

# caffex 算子精度 + 性能（origin-runtime 镜像）
docker run --rm -v .../cross_ops.py:/tmp/cross_ops.py \
  -e PYTHONPATH=/workspace/caffex/python \
  -e LD_LIBRARY_PATH=/workspace/caffex/build/lib:/usr/lib/x86_64-linux-gnu \
  caffe-cpu:origin-runtime bash -lc "python3 /tmp/cross_ops.py /tmp/out all"

# 对比分析与可视化
python .../compare_ops.py
python .../gen_visualization.py

# CPU 占用率测量（caffe-ffi）
docker exec caffe-ffi-jupyter bash -lc \
  "export PATH=/opt/conda/envs/caffe-ffi/bin:/usr/bin:/bin && export KMP_DUPLICATE_LIB_OK=TRUE && \
   cd .../test-assets && /opt/conda/envs/caffe-ffi/bin/python cpu_monitor.py \
   .../benchmark_ops.py .../results/cpu_caffe_ffi.json 30"

# CPU 占用率测量（caffex，见 run_cpu_caffex.sh）
bash .../test-assets/run_cpu_caffex.sh

# Top-K 分类一致性（caffe-ffi）
export NET_NAME=inceptionv1
docker exec caffe-ffi-jupyter bash -lc \
  "export PATH=/opt/conda/envs/caffe-ffi/bin:/usr/bin:/bin && export KMP_DUPLICATE_LIB_OK=TRUE && \
   /opt/conda/envs/caffe-ffi/bin/python .../topk_analysis.py /root/.caffe_test_data/models \
   .../results/topk_input.npy .../results/topk_caffe_ffi.json caffe_ffi"

# Top-K 分类一致性（caffex，见 run_topk_caffex.sh）
bash .../test-assets/run_topk_caffex.sh
```

**测试资产清单**（`test-assets/results/`）：
`caffe_ffi_functional_test.json`、`caffex_functional_test.json`、`cross_ops_caffe_ffi.json`、`cross_ops_caffex.json`、`cross_ops_comparison.json`、`bench_caffe_ffi.json`、`bench_caffex.json`、`cpu_caffe_ffi.json`、`cpu_caffex.json`、`topk_caffe_ffi.json`、`topk_caffex.json`、`topk_input.npy`、`anomaly_A001_weight_loading.json`。

---

*报告数据与原始 JSON 结果文件一致，可追溯、可复现。*