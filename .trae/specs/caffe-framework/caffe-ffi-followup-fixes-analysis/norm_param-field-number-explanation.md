# norm_param 字段编号 190 vs 149 及二进制兼容性解释

> 对应 RQ-1b。解释 caffe-ffi 的 `norm_param` 为何用字段编号 **190**，而 BVLC/caffex 标准用 **149**，
> 以及该差异对**文本 prototxt** 与**二进制 caffemodel** 解析的影响与二进制兼容性结论。

## 1. 事实核查（proto 依据）

**BVLC / caffex 标准**（`vendor/caffe/caffex/src/caffe/proto/caffe.proto`，`LayerParameter` 内）：

```protobuf
optional DropoutParameter     dropout_param = 108;
...
optional NormalizeParameter   norm_param    = 149;   // 标准编号
```

字段 149 是 `LayerParameter` 中*最后一个*（协议注释：next available layer-specific ID: 150）。

**caffe-ffi**（`libs/caffe-ffi/proto/caffe/proto/caffe.proto`，`LayerParameter` 内）：

```protobuf
optional DropoutParameter     dropout_param = 149;   // ← 占用了标准 149
optional L2NormParameter      l2_norm_param = 158;   // caffe-ffi 自有扩展
optional InstanceNormParameter instance_norm_param = 159;
...
optional UpsampleParameter    upsample_param = 189;
optional NormalizeParameter   norm_param    = 190;   // ← caffe-ffi 用 190
```

**关键事实**：caffe-ffi 的 `LayerParameter` 字段编号**并不与 BVLC 对齐**，而是延续了另一套编号谱系
（例如 `dropout_param` 在 caffe-ffi 是 149、在 BVLC 是 108；`pooling_param` 在 caffe-ffi 是 121 等），
并在其末段追加了大量自有扩展字段（158–189）。当需要引入标准 Normalize 层的 `norm_param` 时，
字段 149 已被 caffe-ffi 的 `dropout_param` 占用，因而只能顺延到下一个空闲编号 **190**。

## 2. 为什么是 190（设计逻辑）

- **protobuf 强制字段编号唯一**：同一 message 内字段号不可重复。caffe-ffi 的 `LayerParameter` 已密集占用
  0–189，想要新增 `norm_param` 只能取 190。
- **非刻意不兼容**：190 是"在既有编号谱系上追加新字段"的必然结果，而非有意偏离标准。
- **字段名与消息类型保持一致**：caffe-ffi 用它仍是 `norm_param`（消息类型 `NormalizeParameter`），
  与 BVLC 完全一致——这是文本兼容的根基。

## 3. 兼容性分析

### 3.1 文本 prototxt（✅ 兼容）

protobuf **文本格式按字段名**序列化，**不依赖字段编号**。只要字段名与消息类型一致，
`norm_param` 在两种实现中写法相同：

```prototext
layer {
  name: "norm1"
  type: "Normalize"
  bottom: "data"
  top: "data_norm"
  norm_param { across_spatial: false }
}
```

caffe-ffi 与 BVLC/caffex 都能正确解析该 prototxt，且 `NormalizeParameter` 内部字段一致，
参数语义相同。**文本 prototxt 完全兼容。**

### 3.2 二进制 caffemodel（❌ 不兼容——且更严重）

protobuf **二进制（wire）格式按字段编号**编码。字段号为 N 的长度限字段，其 wire tag = `(N << 3) | 2`：

- 标准 149 → tag = `(149 << 3) | 2 = 1194`（varint `0x8A 0x09`）
- caffe-ffi 190 → tag = `(190 << 3) | 2 = 1522`（varint `0x92 0x0B`）

后果（读取方向，以 caffe-ffi 读 caffex 产出的二进制为例）：

1. **字段错配——比"缺失"更危险**：caffex 在二进制中把 Normalize 层参数编码为字段 149；
   caffe-ffi 却把字段 149 定义为 `dropout_param`。读入时，caffe-ffi 会尝试用 `DropoutParameter`
   的 schema 去解析本应是 `NormalizeParameter` 的字节流，
   → 可能**解析失败**或得到**错位/垃圾参数**。
2. **自己的 190 永远匹配不到**：caffex 产出的二进制从不含字段 190，caffe-ffi 的 `norm_param`
   读不到任何值 → 回退默认参数（`across_spatial` 等默认值），**功能静默丢失**。

> 反向（caffe-ffi 产出二进制给 caffex 读）同理：caffex 在字段 149 读到的是 caffe-ffi 的
> `dropout_param` 内容，同样错配。

**结论：含 Normalize 层的二进制 caffemodel 在两种实现间不可互读。**

### 3.3 非 Normalize 层是否有影响

- **不含 Normalize 的模型**：即使字段编号整体错位，protobuf 对未知字段默认**跳过**（或按
  `unknown fields` 保留），多数情况下仍能解析，只是遇到编号重叠的字段（如 149）存在错配风险。
- **凡涉及编号碰撞的字段**（caffe-ffi 149 `dropout_param` vs 标准 149 `norm_param`）都可能错配，
  风险集中在编号重叠范围。

## 4. 二进制兼容性结论与规避方案

**结论**：
- 文本 prototxt：兼容（字段名一致）。
- 二进制 caffemodel：**不兼容**，且 caffe-ffi 的字段 149 与标准 149 是**不同消息类型**，
  存在解析错配风险，不能仅靠"未知字段跳过"兜底。

**规避/修复建议**：
1. **优先用文本 prototxt 作为交换格式**：Normalize 模型用 `.prototxt` 传递，最稳妥。
2. **字段迁移工具**：写一个一次性的 protobuf 迁移脚本——用标准 schema 反序列化二进制，
   再按 caffe-ffi schema 重新序列化（或反之），把 `norm_param` 从 149 重写到 190。
3. **根治（长期）**：protobuf 字段编号一经发布即不可改（改号即破坏 wire 兼容）。要彻底兼容，
   需将 caffe-ffi 整个 `LayerParameter` 的字段编号**重排为与 BVLC/caffex 完全一致**，
   再把 caffe-ffi 的自有扩展字段追加到标准最大编号之后。这是破坏性变更，需评估既有模型的迁移成本。
4. **避免字段错配**：在 caffe-ffi 侧对 KnownNormalize 层做读取时的类型/字段校验，失败时明确报错
   而非静默回退，便于发现问题。

## 5. 一句话总结

> caffe-ffi 用 190 是因为它沿用了另一套字段编号谱系，149 已被自己的 `dropout_param` 占用，
> 只能追加到 190；字段号差异导致**文本 prototxt 兼容、二进制 caffemodel 不兼容**（且 149 错配为
> 不同消息类型）。规避首选文本 prototxt，根治需全量重排字段编号对齐标准。