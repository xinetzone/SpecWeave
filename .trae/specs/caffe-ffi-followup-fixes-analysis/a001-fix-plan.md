# A-001 修复方案：read_net 未加载 caffemodel 真实权重

> **缺陷**：A-001 — `read_net(prototxt, caffemodel)` 构造网络时未把 caffemodel 的真实权重复制进 layer blobs，导致所有可学习层权重为默认填充值（constant=1.0），网络级推理指数放大至 Inf/NaN。
>
> **状态**：方案已定 + 代码已落地（`net.cpp` 已修改）；**native 扩展尚未重编译**（构建环境为 WSL 容器 `caffe-ffi-jupyter`，本机 Docker 不可用）。

---

## 1. 根因描述

**数据流**：
- Python 入口 `python/caffe_ffi/io.py::read_net()`：当提供 `caffemodel_path` 时，`_merge_weights(param, weights)` 把 caffemodel 每层的 `layer.blobs` 合并进 prototxt 解析出的 `param.layer`，随后 `_merge_weights` 后的 `param` 被 `text_format.MessageToString` 序列化，经 `caffe_ffi.NewNetFromProtoString(proto_text)` 进入 native 层。
- Native 层 `src/caffe_ffi/net.cpp` 的 `Net::Init()`：`param.layer(layer_id)` 的 `layer_param` 中**确实携带** `layer_param.blobs(i)`（含 `data`/`double_data` 与 `shape`），但初始化循环只做了：
  1. `layers_[layer_id]->SetUp(...)` —— 创建 layer blobs 并用**默认 filler（constant=1.0）**填充；
  2. 仅把 `layer_param.param(id).name()` 写进 blob 名称；
  3. **从未把 `layer_param.blobs(i).data / double_data` 复制进 `layers_[layer_id]->blobs()[i]`**。

**后果**：conv/fc 等可学习层的权重永远是默认填充值（constant=1.0 / std=0），caffemodel 真实权重被静默丢弃。net 级推理因此逐层累加放大，最终 Inf/NaN，且与 caffex（原生 Caffe）输出完全不对齐。

**关键证据（改造前 `net.cpp` 468-499 行）**：
```cpp
layers_[layer_id]->SetUp(bottom_vecs_[layer_id], top_vecs_[layer_id]);

auto& layer_blobs = layers_[layer_id]->blobs();
for (int param_id = 0; param_id < layer_param.param_size(); ++param_id) {
  if (param_id < static_cast<int>(layer_blobs.size())) {
    layer_blobs[param_id]->set_name(layer_param.param(param_id).name());  // 只写名称，未写权重
  }
}
```

---

## 2. 修复位置与逻辑

### 2.1 改动文件
- `projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/net.cpp` —— `Net::Init()` 中、`SetUp()` 之后（约 491-538 行）。

### 2.2 修复逻辑
在 `SetUp()` 之后、遍历 `layer_param.blobs_size()` 复制权重：

1. **数量校验**：若 `layer_param.blobs_size() > layer_blobs.size()`（网络参数提供的 blob 数多于层实际创建的 blob），抛出明确运行时错误，而非越界或静默。
2. **形状校验（先校验后复制）**：计算 `layer_param.blobs(i)` 提供的元素数 `proto_count`（优先 `data_size`，其次 `double_data_size`），与 `SetUp` 后该 blob 的 `count()` 比对；**不一致则抛出明确报错**（提示 prototxt 与 caffemodel 不一致），绝不静默。
3. **复制**：形状一致时调用已有且成熟的方法 `blob->FromProto(blob_proto, /*reshape=*/false)`。`FromProto` 内部处理 `data`（float 直接拷贝）与 `double_data`（double→float 转换）；`reshape=false` 保留层 `SetUp` 解析出的形状，避免用 caffemodel 形状覆盖层形状——形状一致性已在上一步保证。
4. **保留原有 param 名称回填**逻辑不变（`param_size()` 循环）。

复用点：`Blob::FromProto`（`src/caffe_ffi/blob.cpp:648`）与 `Net::CopyTrainedLayersFrom`（`net.cpp:855`，对已构造网络回灌权重）中已有的同一套校验/复制语义，本修复在构造期一次性内联复用，保持一致。

### 2.3 落地代码（`net.cpp`，已写入）
```cpp
layers_[layer_id]->SetUp(bottom_vecs_[layer_id], top_vecs_[layer_id]);

// Copy learned weights from the network parameter (prototxt + merged
// caffemodel blobs) into the layer's blobs. Without this, SetUp() only
// fills blobs with the default filler (constant = 1.0), silently
// discarding the real caffemodel weights and producing blown-up
// (Inf/NaN) activations during inference.
auto& layer_blobs = layers_[layer_id]->blobs();
for (int param_id = 0; param_id < layer_param.blobs_size(); ++param_id) {
  if (param_id >= static_cast<int>(layer_blobs.size())) {
    CAFFE_FFI_CHECK_RUNTIME(false)
        << "Layer '" << layer_param.name() << "' provides "
        << layer_param.blobs_size() << " blob(s) in the network parameter "
        << "but the layer only has " << layer_blobs.size() << " blob(s).";
  }

  const caffe::BlobProto& blob_proto = layer_param.blobs(param_id);
  Blob* blob = layer_blobs[param_id].get();

  // Number of weight elements the network parameter provides.
  const int64_t proto_count = blob_proto.data_size() > 0
      ? static_cast<int64_t>(blob_proto.data_size())
      : (blob_proto.double_data_size() > 0
             ? static_cast<int64_t>(blob_proto.double_data_size())
             : 0);

  if (proto_count > 0) {
    // Validate shape consistency: the layer's SetUp-resolved shape must
    // match the parameter's element count. Fail loudly instead of silently
    // producing a corrupted / default-filled weight blob.
    CAFFE_FFI_CHECK_RUNTIME_EQ(blob->count(), proto_count)
        << "Layer '" << layer_param.name() << "' blob[" << param_id
        << "] shape mismatch: layer expects " << blob->count()
        << " elements but the network parameter provides " << proto_count
        << ". The prototxt and caffemodel are inconsistent.";

    // Copy data/double_data into the blob. reshape=false keeps the layer's
    // SetUp-resolved shape; count equality is validated above.
    blob->FromProto(blob_proto, /*reshape=*/false);
  }
}

// Set per-parameter learning-rate multiplier names (if declared).
for (int param_id = 0; param_id < layer_param.param_size(); ++param_id) {
  if (param_id < static_cast<int>(layer_blobs.size())) {
    layer_blobs[param_id]->set_name(layer_param.param(param_id).name());
  }
}
```

### 2.4 可行性/正确性静态核查（已完成）
- `Blob::FromProto(caffe::BlobProto, bool reshape)` 存在于 `blob.cpp:648`，已实现 `data` 拷贝与 `double_data`→`float` 转换，并对元素数做 `CAFFE_FFI_CHECK_RUNTIME_EQ` 校验。
- `Layer::blobs()` 返回 `std::vector<ObjectPtr<Blob>>&`（`layer.hpp:75`），`layer_blobs[param_id].get()` 合法。
- `caffe::LayerParameter::blobs(i)` 返回 `const caffe::BlobProto&`，字段 `data`/`double_data`/`shape` 均确认存在（`build/caffe_proto_gen/caffe/proto/caffe.pb.h`）。
- `InsertSplits` 变换只插入 Split 层、改写 bottom/top 引用，不影响既有层 `blobs`，权重在变换后的 `param` 中保留。
- 修复后 `GetDiagnostics` 对 `net.cpp` 无诊断错误。

---

## 3. 是否需要重编译 native 扩展

**需要**。权重复制逻辑位于 C++ `Net::Init()`，必须重编译 `_caffe_ffi.so` 才能生效。Python 层（`io.py`）无需改动——`_merge_weights` 已正确把 caffemodel blobs 合并进 `param`，native 层此前只是没消费这些 blobs。

- 构建方式（容器内）：`pip install -e . --no-build-isolation`，需本地 tvm-ffi 源码 `projects/xuanspace/vendor/tvm-ffi`。
- 构建环境：WSL Docker 容器 `caffe-ffi-jupyter`（conda env `caffe-ffi`，Python 3.14）。
- **本机限制**：宿主 Windows 无 Docker；WSL Ubuntu-24.04 内无该 conda env / python3.14。**重编译与运行级验证在本环境不可行**，需回到容器环境执行（见 §5 残留限制）。

---

## 4. 验证方法

### 4.1 单测/最小复现（静态层面已能确认修复命中）
修复点即 `Net::Init()` 中 `SetUp` 后新增的复制循环；`FromProto` 逻辑已被 `CopyTrainedLayersFrom` 长期使用，属成熟路径。

### 4.2 运行级验证（需容器重编译后执行，脚本已提供 `a001_verify_fix.py`）
用预训练 InceptionV1（`test-assets/models/inceptionv1.caffemodel` / `inceptionv1.prototxt`）：

1. **权重真实性**：`caffe_ffi.read_net(proto, caffemodel)` 后取 `conv1/7x7_s2` 的权重 blob，断言 `std > 0` 且 `abs(max) != 1.0`（修复前该权重重置为 constant=1.0，std=0；修复后为真实小数值）。
2. **无 NaN/Inf**：对随机/真实输入 `forward()`，遍历所有 blob 断言无 NaN/Inf。
3. **与 caffex 对齐**：用原生 `caffe.Net`（caffex）加载同一模型 + 同一输入，对比各层输出（尤其 `inception_3a/output` … `inception_5a/output` 与最终 `prob`）的 max-abs / first8 数值，容差内一致。

---

## 5. 残留限制与补验路径

| 项 | 状态 | 说明 |
|---|---|---|
| `net.cpp` 修复落地 | ✅ 已完成 | `Init()` 中 SetUp 后复制 blob data |
| Python 层调整 | ✅ 无需 | `_merge_weights` 已正确，无需改动 `io.py` |
| 静态正确性核查 | ✅ 已完成 | 类型/字段/宏确认，无诊断错误 |
| native 重编译 | ⚠️ 未执行 | 构建环境为容器 `caffe-ffi-jupyter`（Python 3.14），本机无 Docker、WSL 无该 conda env |
| 运行级推理验证 | ⚠️ 未执行 | 依赖重编译后的 `_caffe_ffi.so`；宿主 Windows Python 3.13 无法加载 Linux `.so` |
| 验证脚本 | ✅ 已提供 | `a001_verify_fix.py`（权重真实性 / 无 NaN / caffex 对齐） |

**补验路径**（在容器 `caffe-ffi-jupyter` 内）：
```bash
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi
pip install -e . --no-build-isolation   # 需本地 tvm-ffi 源码
python /SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/a001_verify_fix.py
```
预期：`conv1/7x7_s2` 权重 std>0 且非全 1.0；全网络无 NaN/Inf；与 caffex 各层输出对齐。