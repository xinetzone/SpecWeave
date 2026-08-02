# Caffe-FFI 层性能埋点 C++ 模板

> **P0/P1级性能监控统一模板** — 适用于所有Layer的Forward/Backward性能埋点
> 
> **设计原则**：
> - 计时与统计分离：计算阶段用RAII或手动chrono计时，统计阶段循环外一次性reduce
> - 单次遍历融合：逐元素算子（如BN/Activation）将计算+统计融合到单一循环
> - GEMM后独立reduce：矩阵乘算子（Conv/IP）在GEMM后cache-hot状态下遍历统计
> - double累加L2范数：≥100K元素时float精度丢失，必须用double累加平方和
> - col_buffer单缓冲复用：Conv反向传播中im2col→col2im时间不重叠，无需双缓冲
> - caffe_set清零纳入计时：梯度缓冲区清零是实际开销，必须计入total_us

---

## 1. 头文件依赖（必备Include）

```cpp
#include <algorithm>
#include <chrono>
#include <cmath>
#include <limits>
#include <sstream>
#include <vector>

#include "caffe_ffi/fill.hpp"         // caffe_set_fp32, caffe_copy_fp32, caffe_exp_fp32, caffe_cpu_axpby_fp32
#include "caffe_ffi/log.hpp"          // CAFFE_FFI_LOG_INFO, CAFFE_FFI_LAYER_LOG
#include "caffe_ffi/error.hpp"        // CAFFE_FFI_CHECK_VALUE_*
#include "caffe_ffi/math_utils.hpp"   // caffe_cpu_gemm_fp32, caffe_cpu_gemv_fp32, im2col/col2im_fp32
```

---

## 2. P0级模板：GEMM类算子（Conv/InnerProduct）Forward

适用于：卷积层(Conv)、全连接层(InnerProduct/IP)、反卷积层(Deconv)

```cpp
void YourLayer::Forward_cpu(const std::vector<Blob*>& bottom,
                             const std::vector<Blob*>& top) {
  const float* bottom_data = bottom[0]->cpu_data();
  float* top_data = top[0]->cpu_mutable_data();
  const float* weight = this->blobs_[0]->cpu_data();
  const float* bias = bias_term_ ? this->blobs_[1]->cpu_data() : nullptr;

  const int64_t top_count = top[0]->count();
  const int64_t weight_count = this->blobs_[0]->count();

  CAFFE_FFI_LAYER_LOG << "YourLayer Forward: M=" << M_ << " N=" << N_ << " K=" << K_
                      << " bias_term=" << bias_term_;

  using clock = std::chrono::high_resolution_clock;
  auto t_total_start = clock::now();

  // ===== 统计变量初始化 =====
  float out_min = std::numeric_limits<float>::max();
  float out_max = -std::numeric_limits<float>::max();
  float w_min = std::numeric_limits<float>::max();
  float w_max = -std::numeric_limits<float>::max();
  float b_min = std::numeric_limits<float>::max();
  float b_max = -std::numeric_limits<float>::max();
  double w_norm_sq = 0.0;  // double累加防精度丢失

  double t_gemm_us = 0, t_bias_us = 0;

  // ===== 子阶段1：GEMM计算 =====
  auto t_gemm_start = clock::now();
  // === 你的GEMM调用在这里 ===
  // caffe_cpu_gemm_fp32(TransA, TransB, M, N, K, alpha, A, B, beta, C);
  auto t_gemm_end = clock::now();
  t_gemm_us = std::chrono::duration<double, std::micro>(t_gemm_end - t_gemm_start).count();

  // ===== 子阶段2：Bias添加 =====
  if (bias_term_) {
    auto t_bias_start = clock::now();
    // === 你的bias添加逻辑在这里 ===
    // 例如用GEMM或broadcast循环添加
    auto t_bias_end = clock::now();
    t_bias_us = std::chrono::duration<double, std::micro>(t_bias_end - t_bias_start).count();
  }

  // ===== Post-GEMM独立reduce统计（cache-hot，开销<1%） =====
  // 1. 输出值域（GEMM刚写完，L1/L2 cache-hot）
  for (int64_t i = 0; i < top_count; ++i) {
    out_min = std::min(out_min, top_data[i]);
    out_max = std::max(out_max, top_data[i]);
  }
  // 2. 权重值域+L2范数（double累加）
  for (int64_t i = 0; i < weight_count; ++i) {
    float w = weight[i];
    w_min = std::min(w_min, w);
    w_max = std::max(w_max, w);
    w_norm_sq += static_cast<double>(w) * static_cast<double>(w);
  }
  float w_norm = static_cast<float>(std::sqrt(w_norm_sq));
  // 3. 偏置值域（小，channels量级）
  if (bias_term_) {
    int64_t bias_count = this->blobs_[1]->count();
    for (int64_t i = 0; i < bias_count; ++i) {
      b_min = std::min(b_min, bias[i]);
      b_max = std::max(b_max, bias[i]);
    }
  }

  double total_us = std::chrono::duration<double, std::micro>(clock::now() - t_total_start).count();

  // ===== 结构化日志输出 =====
  CAFFE_FFI_LOG_INFO() << "[YOURLAYER-PERF] " << this->name()
                       << " YourLayer forward: M=" << M_ << " N=" << N_ << " K=" << K_
                       << " bias_term=" << bias_term_
                       << " out=[" << out_min << ", " << out_max << "]"
                       << " w=[" << w_min << ", " << w_max << "]"
                       << " w_norm=" << w_norm
                       << (bias_term_ ? " b=[" + std::to_string(b_min) + ", " + std::to_string(b_max) + "]" : "")
                       << " t_gemm=" << t_gemm_us << "us"
                       << (bias_term_ ? " t_bias=" + std::to_string(t_bias_us) + "us" : "")
                       << " time=" << total_us << "us";
}
```

---

## 3. P0级模板：GEMM类算子Backward

适用于：Conv/IP/Deconv的反向传播

```cpp
void YourLayer::Backward_cpu(const std::vector<Blob*>& top,
                              const std::vector<bool>& propagate_down,
                              const std::vector<Blob*>& bottom) {
  const float* weight = this->blobs_[0]->cpu_data();
  const float* top_diff = top[0]->cpu_diff();
  const float* bottom_data = bottom[0]->cpu_data();
  float* weight_diff = this->param_propagate_down_[0] ? this->blobs_[0]->cpu_mutable_diff() : nullptr;
  float* bottom_diff = propagate_down[0] ? bottom[0]->cpu_mutable_diff() : nullptr;

  const int64_t weight_count = this->blobs_[0]->count();
  const int64_t bottom_count = bottom[0]->count();

  CAFFE_FFI_LAYER_LOG << "YourLayer Backward: M=" << M_ << " N=" << N_ << " K=" << K_
                      << " bias_term=" << bias_term_
                      << " prop_down=" << (propagate_down[0] ? "true" : "false");

  using clock = std::chrono::high_resolution_clock;
  auto t_total_start = clock::now();

  // ===== 阶段0：清零梯度缓冲区（必须纳入计时！） =====
  double t_zero_us = 0;
  {
    auto t0 = clock::now();
    if (this->param_propagate_down_[0]) {
      caffe_set_fp32(static_cast<size_t>(weight_count), 0.0f, weight_diff);
    }
    if (bias_term_ && this->param_propagate_down_[1]) {
      caffe_set_fp32(static_cast<size_t>(this->blobs_[1]->count()), 0.0f,
                     this->blobs_[1]->cpu_mutable_diff());
    }
    t_zero_us = std::chrono::duration<double, std::micro>(clock::now() - t0).count();
  }

  // ===== 统计变量初始化 =====
  float top_diff_min = std::numeric_limits<float>::max();
  float top_diff_max = -std::numeric_limits<float>::max();
  float bottom_diff_min = std::numeric_limits<float>::max();
  float bottom_diff_max = -std::numeric_limits<float>::max();
  float w_diff_min = std::numeric_limits<float>::max();
  float w_diff_max = -std::numeric_limits<float>::max();
  float b_diff_min = std::numeric_limits<float>::max();
  float b_diff_max = -std::numeric_limits<float>::max();

  double t_gemm_filter_us = 0, t_gemm_data_us = 0, t_gemm_bias_us = 0;

  // ===== 注意beta参数选择 =====
  // - InnerProduct：一次GEMM处理所有M样本 → beta=0（直接写）
  // - Conv：逐n/g循环处理每个样本/分组 → beta=1（跨batch累积）
  //
  // ===== backward_filter: dW（权重梯度） =====
  if (this->param_propagate_down_[0]) {
    auto tgf = clock::now();
    // === 你的权重梯度GEMM在这里 ===
    // 对于逐batch循环的Conv：beta=1.0f 累积
    // 对于一次性计算的IP：beta=0.0f 直接写
    // caffe_cpu_gemm_fp32(..., 1.0f/0.0f, weight_diff);
    t_gemm_filter_us = std::chrono::duration<double, std::micro>(clock::now() - tgf).count();
  }

  // ===== backward_bias: db（偏置梯度） =====
  if (bias_term_ && this->param_propagate_down_[1]) {
    auto tgb = clock::now();
    // === 你的偏置梯度GEMV/GEMM在这里 ===
    // beta参数同上：逐batch循环用1.0f，一次性计算用0.0f
    t_gemm_bias_us = std::chrono::duration<double, std::micro>(clock::now() - tgb).count();
  }

  // ===== backward_data: dX（bottom梯度） =====
  if (propagate_down[0]) {
    auto tgd = clock::now();
    // === 你的bottom梯度GEMM在这里 ===
    // beta=0.0f（bottom_diff不会被多层共享，不需要累积）
    t_gemm_data_us = std::chrono::duration<double, std::micro>(clock::now() - tgd).count();
  }

  // ===== Post-loop reduce统计 =====
  // 1. bottom_diff值域（刚写完，cache-hot）
  if (propagate_down[0]) {
    for (int64_t i = 0; i < bottom_count; ++i) {
      bottom_diff_min = std::min(bottom_diff_min, bottom_diff[i]);
      bottom_diff_max = std::max(bottom_diff_max, bottom_diff[i]);
    }
  }
  // 2. weight_diff值域+L2范数（double累加）
  double w_diff_norm_sq = 0.0;
  float w_diff_norm = 0.0f;
  if (this->param_propagate_down_[0]) {
    for (int64_t i = 0; i < weight_count; ++i) {
      float dw = weight_diff[i];
      w_diff_min = std::min(w_diff_min, dw);
      w_diff_max = std::max(w_diff_max, dw);
      w_diff_norm_sq += static_cast<double>(dw) * static_cast<double>(dw);
    }
    w_diff_norm = static_cast<float>(std::sqrt(w_diff_norm_sq));
  }
  // 3. top_diff值域（多次读取，L3可能有残留）
  {
    int64_t top_count = top[0]->count();
    const float* td = top_diff;
    for (int64_t i = 0; i < top_count; ++i) {
      top_diff_min = std::min(top_diff_min, td[i]);
      top_diff_max = std::max(top_diff_max, td[i]);
    }
  }
  // 4. bias_diff值域（小，channels量级）
  if (bias_term_ && this->param_propagate_down_[1]) {
    int64_t bd_count = this->blobs_[1]->count();
    const float* bd = this->blobs_[1]->cpu_diff();
    for (int64_t i = 0; i < bd_count; ++i) {
      b_diff_min = std::min(b_diff_min, bd[i]);
      b_diff_max = std::max(b_diff_max, bd[i]);
    }
  }

  double total_us = std::chrono::duration<double, std::micro>(clock::now() - t_total_start).count();

  // ===== 结构化日志输出 =====
  std::string w_diff_str;
  if (this->param_propagate_down_[0]) {
    w_diff_str = " w_diff=[" + std::to_string(w_diff_min) + ", " + std::to_string(w_diff_max) + "]"
               + " w_diff_norm=" + std::to_string(w_diff_norm);
  }
  std::string b_diff_str;
  if (bias_term_ && this->param_propagate_down_[1]) {
    b_diff_str = " b_diff=[" + std::to_string(b_diff_min) + ", " + std::to_string(b_diff_max) + "]";
  }
  std::string bottom_diff_str;
  if (propagate_down[0]) {
    bottom_diff_str = " bottom_diff=[" + std::to_string(bottom_diff_min) + ", " + std::to_string(bottom_diff_max) + "]"
                    + " t_gemm_data=" + std::to_string(t_gemm_data_us) + "us";
  }
  std::string b_bias_str;
  if (bias_term_ && this->param_propagate_down_[1]) {
    b_bias_str = " t_gemm_bias=" + std::to_string(t_gemm_bias_us) + "us";
  }

  CAFFE_FFI_LOG_INFO() << "[YOURLAYER-PERF] " << this->name()
                       << " YourLayer backward: M=" << M_ << " N=" << N_ << " K=" << K_
                       << " bias_term=" << bias_term_
                       << " prop_down=" << (propagate_down[0] ? "true" : "false")
                       << " prop_w=" << this->param_propagate_down_[0]
                       << " top_diff=[" << top_diff_min << ", " << top_diff_max << "]"
                       << bottom_diff_str
                       << w_diff_str
                       << b_diff_str
                       << " t_zero=" << t_zero_us << "us"
                       << " t_gemm_filter=" << t_gemm_filter_us << "us"
                       << b_bias_str
                       << " time=" << total_us << "us";
}
```

---

## 4. P1级模板：逐元素算子（BatchNorm/Scale）

适用于：BatchNorm、Scale、逐元素Activation（ReLU/Sigmoid/Tanh等）
**核心：单次遍历融合计算+值域统计，避免二次遍历**

```cpp
void YourElementwiseLayer::Forward_cpu(const std::vector<Blob*>& bottom,
                                        const std::vector<Blob*>& top) {
  const float* bottom_data = bottom[0]->cpu_data();
  float* top_data = top[0]->cpu_mutable_data();
  const int64_t count = bottom[0]->count();

  // 参数指针
  const float* gamma = this->blobs_[0]->cpu_data();  // scale
  const float* beta = bias_term_ ? this->blobs_[1]->cpu_data() : nullptr;  // bias

  using clock = std::chrono::high_resolution_clock;
  auto t_start = clock::now();

  // ===== 单次遍历：计算 + in/out值域统计（融合，O(N)无二次遍历） =====
  float in_min = std::numeric_limits<float>::max();
  float in_max = -std::numeric_limits<float>::max();
  float out_min = std::numeric_limits<float>::max();
  float out_max = -std::numeric_limits<float>::max();

  // 如果有参数（gamma/beta/mean/var等），可额外统计它们的值域
  float param_min = std::numeric_limits<float>::max();
  float param_max = -std::numeric_limits<float>::max();

  for (int64_t i = 0; i < count; ++i) {
    float x = bottom_data[i];
    // === 你的逐元素计算在这里 ===
    float y = x;  // 替换为实际计算
    top_data[i] = y;
    in_min = std::min(in_min, x);
    in_max = std::max(in_max, x);
    out_min = std::min(out_min, y);
    out_max = std::max(out_max, y);
  }

  // 参数值域统计（O(channels)，远小于count，独立遍历可接受）
  int channels = channels_;
  for (int c = 0; c < channels; ++c) {
    float p = gamma[c];  // 替换为实际参数
    param_min = std::min(param_min, p);
    param_max = std::max(param_max, p);
  }

  auto t_end = clock::now();
  double elapsed_us = std::chrono::duration<double, std::micro>(t_end - t_start).count();

  // ===== 结构化日志输出 =====
  CAFFE_FFI_LOG_INFO() << "[YOURLAYER-PERF] " << this->name()
                       << " YourLayer forward: count=" << count
                       << " channels=" << channels
                       << " in=[" << in_min << ", " << in_max << "]"
                       << " out=[" << out_min << ", " << out_max << "]"
                       << " param=[" << param_min << ", " << param_max << "]"
                       << " time=" << elapsed_us << "us";
}
```

---

## 5. P1级模板：概率分布算子（Softmax）

适用于：Softmax、SoftmaxWithLoss等输出概率分布的算子
**核心：avg_max_prob + avg_entropy，监控分类置信度和分布均匀性**

```cpp
void YourProbLayer::Forward_cpu(const std::vector<Blob*>& bottom,
                                 const std::vector<Blob*>& top) {
  const float* bottom_data = bottom[0]->cpu_data();
  float* top_data = top[0]->cpu_mutable_data();
  int channels = static_cast<int>(bottom[0]->shape(softmax_axis_));
  int dim = channels * inner_num_;
  const int64_t count = bottom[0]->count();

  using clock = std::chrono::high_resolution_clock;
  auto t_start = clock::now();

  // === 你的概率计算逻辑在这里（max subtraction → exp → normalization）===
  caffe_copy_fp32(static_cast<size_t>(count), bottom_data, top_data);
  // ... (max subtract, exp, normalize per sample) ...

  // ===== 概率分布统计（计算完成后，cache-hot） =====
  float out_min = std::numeric_limits<float>::max();
  float out_max = -std::numeric_limits<float>::max();
  double sum_max_prob = 0.0;   // double累加防精度丢失
  double sum_entropy = 0.0;    // double累加防精度丢失
  int n_samples = outer_num_ * inner_num_;

  for (int i = 0; i < outer_num_; ++i) {
    const float* top_data_i = top_data + i * dim;
    for (int k = 0; k < inner_num_; ++k) {
      float sample_max = 0.0f;
      double sample_entropy = 0.0;
      for (int j = 0; j < channels; ++j) {
        float p = top_data_i[j * inner_num_ + k];
        out_min = std::min(out_min, p);
        out_max = std::max(out_max, p);
        sample_max = std::max(sample_max, p);
        if (p > 0.0f) {
          // entropy = -sum(p * log(p))，double计算
          sample_entropy -= static_cast<double>(p) * std::log(static_cast<double>(p));
        }
      }
      sum_max_prob += sample_max;
      sum_entropy += sample_entropy;
    }
  }
  float avg_max_prob = static_cast<float>(sum_max_prob / static_cast<double>(n_samples));
  float avg_entropy = static_cast<float>(sum_entropy / static_cast<double>(n_samples));
  float max_entropy = std::log(static_cast<float>(channels));  // 均匀分布时的最大熵
  float confidence = avg_max_prob;  // 越高越自信（越容易过拟合）
  float uncertainty = avg_entropy / max_entropy;  // 0=确定，1=均匀分布

  auto t_end = clock::now();
  double elapsed_us = std::chrono::duration<double, std::micro>(t_end - t_start).count();

  // ===== 结构化日志输出 =====
  CAFFE_FFI_LOG_INFO() << "[YOURLAYER-PERF] " << this->name()
                       << " YourProbLayer forward: outer_num=" << outer_num_
                       << " channels=" << channels
                       << " inner_num=" << inner_num_
                       << " axis=" << softmax_axis_
                       << " out=[" << out_min << ", " << out_max << "]"
                       << " avg_max_prob=" << avg_max_prob
                       << " avg_entropy=" << avg_entropy
                       << " max_entropy=" << max_entropy
                       << " uncertainty=" << uncertainty
                       << " time=" << elapsed_us << "us";
}
```

---

## 6. 关键设计决策与避坑指南

| 坑点 | 正确做法 | 错误后果 |
|------|----------|----------|
| L2范数float累加 | **必须用double**累加`w_norm_sq`，最后sqrt转float | ≥100K权重时精度丢失，范数偏小甚至为0 |
| caffe_set清零 | **必须纳入t_total_start**计时，单独记录t_zero_us | 报告的total_us比实际偏短，无法解释性能 |
| col_buffer双缓冲 | Conv反向传播**复用单col_buffer**：im2col→GEMM(filter)读完→GEMM(data)覆盖→col2im读 | 内存占用翻倍，分配延迟增加 |
| beta参数选择 | 逐n循环（Conv）→ **beta=1**累积；一次性GEMM（IP）→ **beta=0**直接写 | beta=0导致Conv梯度被覆盖，只有最后一个batch的梯度 |
| propagate_down判断 | 所有bottom_diff访问**必须在propagate_down[0]**保护内 | 不需要梯度时仍进行计算，浪费算力；空指针访问崩溃 |
| param_propagate_down判断 | 所有weight/bias_diff访问**必须检查param_propagate_down_** | 冻结层仍计算梯度，浪费算力；空指针访问崩溃 |
| 1x1 Conv特殊路径 | is_1x1_时跳过im2col/col2im，直接用bottom_data/bottom_diff | 不必要的im2col/col2im开销 |
| 熵计算用float | p*log(p)用**double**计算后累加 | 小概率值p<1e-6时log(p)约-14，float精度丢失导致熵计算不准 |
| 日志tag命名 | 使用统一`[LAYERNAME-PERF]`大写标签 | 日志无法grep，难以聚合分析 |

---

## 7. 各层日志标签对照表

| 层类型 | 日志标签 | 特有统计字段 |
|--------|----------|--------------|
| Convolution | `[CONV-PERF]` | w_norm/w_diff_norm, t_im2col, t_col2im, t_zero(caffe_set), kernel/stride/pad, prop_down/prop_w |
| InnerProduct | `[IP-PERF]` | w_norm/w_diff_norm, transpose, t_zero, prop_down/prop_w |
| BatchNorm | `[BN-PERF]` | mean/var值域, eps, use_global_stats, 单次遍历融合 |
| Softmax | `[SOFTMAX-PERF]` | avg_max_prob, avg_entropy, max_entropy, uncertainty |
| SoftmaxWithLoss | `[LOSS-PERF]` | prob值域, avg_max_prob, avg_entropy, uncertainty, avg_loss, valid_count |
| ReLU | `[ACTIVATION-PERF]` | in/out值域, diff_in/diff_out值域, dead_ratio(死区神经元比例), negative_slope |
| Sigmoid | `[ACTIVATION-PERF]` | in/out值域, diff_in/diff_out值域, saturate_ratio(饱和神经元比例) |
| PReLU/ELU/Tanh | `[ACTIVATION-PERF]` | input/output range, alpha/negative_slope参数 |
| Pooling | `[POOL-PERF]` | in/out值域, kernel/stride/pad, pool_method(MAX/AVE) |
| Eltwise | `[ELTWISE-PERF]` | out值域, coeffs值域, operation(SUM/PROD/MAX), num_bottoms |
| Bias | `[BIAS-PERF]` | in/out值域, bias值域, outer/bias/inner dim, 单次遍历融合copy+bias+统计 |
| Scale | `[SCALE-PERF]` | in/out值域, scale值域, bias值域(可选), outer/scale/inner dim, 单次遍历融合scale+bias+统计 |
| Dropout | `[DROPOUT-PERF]` | dropout_ratio, inplace(推理时透传) |
| Concat | `[CONCAT-PERF]` | out值域, num_bottoms, concat_axis |
| Split | `[SPLIT-PERF]` | COW phase, blob counts（WARN级别） |

---

## 8. 已实现层状态清单

| 层 | Forward | Backward | 日志标签 | 备注 |
|----|---------|----------|----------|------|
| Convolution | ✅ | ✅ | `[CONV-PERF]` | col_buffer单缓冲复用，beta=1累积，6子阶段计时，prop完整判断 |
| InnerProduct | ✅ | ✅ | `[IP-PERF]` | beta=0直接写(一次GEMM)，4子阶段计时，double累加w_diff_norm |
| BatchNorm | ✅ | ⏳ | `[BN-PERF]` | 单次遍历融合normalize+in/out值域，mean/var参数独立reduce |
| Softmax | ✅ | ⏳ | `[SOFTMAX-PERF]` | avg_max_prob/avg_entropy/uncertainty，double累加熵 |
| SoftmaxWithLoss | ✅ | ⏳ | `[LOSS-PERF]` | 概率分布统计+avg_loss+valid_count |
| ReLU | ✅ | ✅ | `[ACTIVATION-PERF]` | dead_ratio死区神经元统计，negative_slope参数 |
| Sigmoid | ✅ | ✅ | `[ACTIVATION-PERF]` | saturate_ratio饱和神经元统计，y*(1-y)梯度 |
| ELU/Tanh/PReLU | ✅ | ⏳ | `[ACTIVATION-PERF]` | in/out值域统计，alpha/negative_slope参数 |
| Pooling | ✅ | ⏳ | `[POOL-PERF]` | in值域融合计算中统计，out值域独立reduce，MAX/AVE方法 |
| Eltwise | ✅ | ⏳ | `[ELTWISE-PERF]` | coeffs值域独立reduce，out值域独立reduce，SUM/PROD/MAX |
| Bias | ✅ | ⏳ | `[BIAS-PERF]` | 单次遍历融合copy+bias+in/out值域统计（比caffe_copy+三重循环更高效） |
| Scale | ✅ | ⏳ | `[SCALE-PERF]` | 单次遍历融合scale+bias+in/out值域统计（比caffe_copy+两重循环更高效） |
| Dropout | ✅ | ⏳ | `[DROPOUT-PERF]` | 推理时透传(identity copy)，inplace检测 |
| Concat | ✅ | ⏳ | `[CONCAT-PERF]` | memcpy+out值域统计 |
| Split | ✅ | ⏳ | `[SPLIT-PERF]` | COW phase统计（WARN级别） |

---

**版本**: v1.1.0
**最后更新**: 2026-08-01
**适用范围**: caffe-ffi CPU算子性能监控
**覆盖范围**: 17个层中14个层已有Forward性能埋点（覆盖率82%），其中2个核心GEMM层(Conv/IP)双向埋点，2个激活层(ReLU/Sigmoid)双向埋点
