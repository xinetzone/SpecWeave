# Caffemodel 批量转换报告

| 项目 | 值 |
|------|-----|
| 扫描目录 | `D:\spaces\SpecWeave\external\chaos\sdk_caffe\models` |
| 目标格式 | **caffe-ffi** |
| 总模型数 | 2 |
| 已转换 | 0 |
| 原生兼容 | 0 |
| 跳过 | 0 |
| 错误 | 0 |
| 总输入大小 | 30.9MB |
| 总输出大小 | 0B |
| 总耗时 | 0.03s |

## 详细结果

| # | 文件 | 格式 | 大小 | 状态 | 耗时 | 备注 |
|---|------|------|------|------|------|------|
| 1 | fgvsirfeature.caffemodel | V2 | 30.7MB | 🔍 scanned | 28.7ms |  |
| 2 | fgvsirfeature_ssd.caffemodel | V2 | 251.8KB | 🔍 scanned | 1.2ms |  |

## 字段映射说明

| 参数字段 | BVLC field | caffe-ffi field | 处理方式 |
|----------|-----------|----------------|---------|
| convolution_param | 106 | 106 | ✅ 一致，无需转换 |
| pooling_param | 121 | 121 | ✅ 一致，无需转换 |
| inner_product_param | 117 | 117 | ✅ 一致，无需转换 |
| relu_param | 123 | 123 | ✅ 一致，无需转换 |
| softmax_param | 125 | 125 | ✅ 一致，无需转换 |
| norm_param | 149 | 190 | 🔄 重映射 |
| dropout_param | 108 | 149 | 🔄 重映射 |
| lrn_param | 118 | 155 | 🔄 重映射 |
| loss_param | 101 | 140 | 🔄 重映射 |
| transform_param | 100 | (不存在) | ⛔ 丢弃 |
| LeakyReLU/L2Norm/InstanceNorm等 | (不存在) | 157/158/159等 | ⛔ 反向转换时跳过 |