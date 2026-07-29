---
id: "retrospective-caffe-forward-pass-notebook-20260727"
title: "Caffe 神经网络前向传播测试 Notebook 开发复盘"
source: "projects/xuanspace/vendor/caffe/workspace/01_caffe_forward_pass.ipynb"
date: "2026-07-27"
category: "retrospective"
scope: "task"
tags: ["caffe", "jupyter-notebook", "python", "deep-learning", "forward-pass", "docker", "netspec", "prototxt"]
---

# Caffe 神经网络前向传播测试 Notebook 开发复盘

> **生成日期**：2026-07-27
> **分析范围**：Caffe 前向传播示例 Jupyter Notebook 的设计、开发、调试与验证全流程
> **方法论**：R→I→E 三阶段（复盘事实→洞察根因→萃取模式）
> **场景类型**：知识沉淀（任务完成复盘 + Bug修复复盘）

---

## 执行摘要

本次任务完成了 Caffe 深度学习框架前向传播测试 Jupyter Notebook 的开发与全量验证。Notebook 包含 12 个代码单元和 13 个 Markdown 单元，共 440 行内容，覆盖环境验证、NetSpec 网络定义、prototxt 定义、网络创建、前向传播、自定义数据注入、特征图可视化、批量处理、ReLU/Softmax 手动验证等完整流程。过程中发现并修复了 3 个关键 Bug（Docker 挂载路径覆盖、Softmax axis 维度错误、Notebook 代码换行符丢失），最终 12/12 代码单元全部正确执行，输出验证通过。

| 指标 | 数值 |
|------|------|
| Notebook 大小 | 183,095 bytes（~179 KB） |
| 代码单元 | 12 个（360 行代码） |
| Markdown 单元 | 13 个（80 行文档） |
| 执行验证 | 12/12 cells 全部通过 |
| 发现并修复 Bug | 3 个 |
| 萃取可复用模式 | 4 个 |
| Docker 容器 | `caffe-jupyter`（healthy，端口 8888/2222） |

---

## 第1章 · 过程复盘（R阶段）

### 1.1 任务背景

| 属性 | 值 |
|------|-----|
| 任务来源 | 用户主动请求（承接前序 Docker 环境搭建任务） |
| 任务目标 | 编写简单 Caffe 神经网络示例 Notebook，测试模型前向传播功能 |
| 工作目录 | `projects/xuanspace/vendor/caffe/workspace/` |
| 运行环境 | Docker 容器 `caffe-jupyter`（Ubuntu 22.04 + Caffe CPU + Jupyter） |
| 前序依赖 | [Caffe Jupyter Docker 镜像构建复盘](../retrospective-caffe-jupyter-docker-build-20260726/README.md) |

### 1.2 时间线（含前序会话）

| 阶段 | 事件 | 结果 |
|------|------|------|
| T+0 | 环境准备：修改 `run-jupyter.sh` 挂载路径 | 修复挂载点从 `/workspace` 改为 `/workspace/notebooks`，避免覆盖 Caffe 源码 |
| T+1 | 首次编写 Notebook：NetSpec 定义 LeNet + Softmax | ❌ Softmax 输出概率和不为 1.0 |
| T+2 | 定位 Softmax Bug：axis 维度错误 | 修复：输入形状改为 `(1,5,1,1)`，显式指定 `softmax_param { axis: 1 }` |
| T+3 | 使用 Python 脚本程序化生成 Notebook JSON | ✅ 解决手动编写 JSON 的语法错误问题 |
| T+4 | Windows 权限问题：无法直接写入 vendor 目录 | 解决：先输出到临时目录，WSL 复制到目标路径 |
| T+5 | 用户请求运行前几个 cell 验证输出 | 发现 Notebook 代码 cell 换行符丢失 Bug |
| T+6 | 定位换行符 Bug：`lines()` 函数缺失导致代码单行化 | 根因：build_notebook.py 直接将多行字符串作为 source 单元素列表写入 |
| T+7 | 修复 `lines()` 函数，重新生成 Notebook | ✅ 代码正确分行 |
| T+8 | 全量执行 12 个 cells | ✅ 12/12 全部通过，所有输出验证正确 |

### 1.3 产出物清单

| 产出物 | 位置 | 说明 |
|--------|------|------|
| Jupyter Notebook | [01_caffe_forward_pass.ipynb](../../../../../../projects/xuanspace/vendor/caffe/workspace/01_caffe_forward_pass.ipynb) | 183KB，25 cells，Caffe 前向传播完整示例 |
| Docker 容器 | `caffe-jupyter` | healthy，端口 8888(Jupyter)/2222(SSH) |
| 启动脚本 | [run-jupyter.sh](../../../../../../projects/xuanspace/vendor/caffe/docker/origin/run-jupyter.sh) | 已修复挂载路径问题 |

### 1.4 Notebook 章节结构

| # | 章节 | 类型 | cells | 核心内容 |
|---|------|------|-------|---------|
| 1 | 环境验证与导入 | 代码+文档 | 2 | Python/NumPy/Caffe 版本检查，CPU 模式设置 |
| 2 | Caffe 核心概念 | 文档 | 1 | Blob/Layer/Net 概念说明，(N,C,H,W) 维度约定 |
| 3 | NetSpec 程序化定义网络 | 代码+文档 | 2 | 使用 `caffe.NetSpec()` 定义简化 LeNet-5 |
| 4 | prototxt 字符串定义网络 | 代码+文档 | 2 | 直接编写 prototxt 定义简单 MLP |
| 5 | 创建网络并前向传播 | 代码 | 2 | `caffe.Net()` 创建、`net.forward()` 执行、Blob/Param 形状检查 |
| 6 | 自定义输入数据 | 代码+文档 | 2 | 修改 `net.blobs['data'].data` 注入自定义图像 |
| 7 | 中间特征图可视化 | 代码+文档 | 1 | matplotlib 可视化 conv1/pool1 特征图 |
| 8 | 批量输入处理 | 代码+文档 | 1 | batch=4 并行推理，Top-3 预测展示 |
| 9 | 手动验证计算 | 代码+文档 | 1 | NumPy 手动计算 ReLU/Softmax 对比 Caffe 输出 |
| 10 | 层类型参考 | 代码 | 1 | 6 大类 30+ 常用层类型列表 |
| 总结 | 关键要点总结 | 文档 | 1 | 6 条核心要点回顾 |

### 1.5 关键 Bug 清单

| Bug ID | 描述 | 影响 | 根因 | 修复方式 |
|--------|------|------|------|---------|
| BUG-1 | Docker 挂载路径覆盖 Caffe 源码 | Caffe 无法导入 | 本地目录挂载到 `/workspace` 覆盖了镜像内 `/workspace/caffex` | 修改挂载点为 `/workspace/notebooks` |
| BUG-2 | Softmax 概率和不为 1.0 | 分类结果无效 | 输入形状 `(1,1,1,5)` 导致 Softmax 在 H 维计算而非 C 维 | 改为 DummyData 层形状 `(1,5,1,1)` + `axis: 1` |
| BUG-3 | Notebook 代码 cell 无换行符 | Python 无法正确解析多行代码 | 生成脚本直接将多行字符串作为 JSON 数组单元素，未按 `\n` 拆分 | 新增 `lines()` 函数，每行一个字符串元素，末行无尾 `\n` |

---

## 第2章 · 洞察分析（I阶段）

```
[CMD-LOG] | level=INFO | cmd=insight | step=S0 | event=CMD_START | session=ins-20260727-caffe-notebook | msg=开始洞察分析：Caffe Notebook开发Bug根因分析
```

### 2.1 根因分析：Notebook JSON 格式陷阱（BUG-3 深度分析）

**现象**：Notebook 中 cells 3-11 的 Python 代码被压缩为单行（用 4 空格缩进代替换行），导致代码无法正确执行。

**根因链（5-Whys）**：

1. **Why 代码执行无输出？** → Python 将多行代码解析为单行，函数体仅第一行有效，其余成为注释
2. **Why 代码是单行？** → Notebook JSON 的 `source` 字段是一个单元素列表 `["def foo():    x = 1    # comment    y = 2"]`，没有换行符
3. **Why source 是单元素？** → 生成脚本中直接将 Python 多行字符串传入 code_cell，未拆分
4. **Why 未拆分？** → 不了解 Jupyter Notebook JSON 格式约定：`source` 应为按行分割的字符串数组
5. **为什么不了解？** → Jupyter Notebook JSON 格式（nbformat）是一个隐含约定，没有在首次生成时查阅规范

**根因本质**：**格式假设错误**——假设 Jupyter 接受单个多行字符串作为 source，但实际上 nbformat 4.x 要求 source 是按行分割的字符串数组，每个字符串是一行（通常以 `\n` 结尾，最后一行除外）。

**修复关键代码**：

```python
def lines(*args):
    """Split multi-line strings into a list of lines, each ending with \\n."""
    result = []
    for arg in args:
        for line in arg.split('\n'):
            result.append(line + '\n')
    # Remove trailing \\n from last line (Jupyter convention)
    if result and result[-1].endswith('\n'):
        result[-1] = result[-1][:-1]
    return result
```

### 2.2 根因分析：Softmax axis 维度问题（BUG-2 深度分析）

**现象**：使用 MemoryData 层 + input_shape 设置为 `(1,1,1,5)` 时，Softmax 输出概率和不为 1.0。

**根因**：

- Caffe Blob 维度顺序为 **(N, C, H, W)** = (批大小, 通道数, 高度, 宽度)
- Softmax 层默认在 **axis=1**（通道维 C）上计算概率分布
- 当输入形状为 `(1,1,1,5)` 时，C=1（只有1个通道），Softmax 在 C 维计算，每个像素独立做 Softmax → 每个位置的概率必然为 1.0
- 正确做法：类别数必须放在 **C 维度**，即 `(1, num_classes, 1, 1)`

**教训**：Caffe 的维度语义与 PyTorch 一致但与 TensorFlow/NHWC 不同，在使用分类层（Softmax/SoftmaxWithLoss）时必须确认类别维度在 axis=1。

### 2.3 根因分析：Docker 挂载覆盖问题（BUG-1 深度分析）

**现象**：将本地 workspace 挂载到容器 `/workspace` 后，Caffe 无法导入（`ModuleNotFoundError: No module named 'caffe'`）。

**根因**：Docker 卷挂载会**完全覆盖**目标目录（shadow），而非合并。镜像内 `/workspace/caffex`（Caffe 源码编译目录）被本地空目录覆盖后完全不可见。

**正确做法**：
- 将用户工作目录挂载到**子路径**（如 `/workspace/notebooks`），避免覆盖镜像内已有内容
- 或在 Dockerfile 中将应用安装到非挂载路径（如 `/opt/caffe`）

### 2.4 关键发现

| # | 发现 | 类别 | 重要性 |
|---|------|------|--------|
| F1 | Jupyter Notebook nbformat 4.x 的 source 字段必须是按行分割的字符串数组 | 格式约定 | 🔴 高 |
| F2 | Caffe Softmax 默认 axis=1（通道维），类别数必须在 C 维度 | API 语义 | 🔴 高 |
| F3 | Docker 卷挂载是完全覆盖（shadow），不是合并 | 容器行为 | 🟡 中 |
| F4 | `in_place=True` 可以让 ReLU 等激活层直接覆盖输入 blob，节省内存 | Caffe 特性 | 🟢 低 |
| F5 | NetSpec 的 `L.DummyData(shape=dict(dim=list(shape)))` 是零数据依赖定义网络的最简方式 | Caffe 技巧 | 🟢 低 |
| F6 | 程序化生成 Notebook（Python 脚本写 JSON）比手动编辑 JSON 更可靠 | 工程实践 | 🟡 中 |
| F7 | 在容器中通过 `exec()` 逐 cell 执行 + stdout 重定向是验证 Notebook 正确性的有效方法 | 测试方法 | 🟡 中 |

### 2.5 验证结果数据

| 验证项 | 期望 | 实际 | 结果 |
|--------|------|------|------|
| Caffe 导入 | 无报错 | Python 3.10.12 / NumPy 1.26.4 / Caffe 1.0.0 | ✅ |
| CPU 模式设置 | 无报错 | Caffe 运行模式: CPU | ✅ |
| 网络 Blob 形状 | 符合 LeNet-5 设计 | data(1,1,28,28)→conv1(1,20,24,24)→pool1(1,20,12,12)→conv2(1,50,8,8)→pool2(1,50,4,4)→fc3(1,500)→fc4(1,10)→prob(1,10) | ✅ |
| 参数形状 | conv1:[20,1,5,5], conv2:[50,20,5,5], fc3:[500,800], fc4:[10,500] | 完全匹配 | ✅ |
| Softmax 概率和 | 1.0 | [1.] | ✅ |
| 自定义输入形状 | (1,1,28,28) | (1,1,28,28) 值范围[0.0,1.0] | ✅ |
| 自定义预测 | 10类概率 | 类别7(15.88%)，概率和≈1.0 | ✅ |
| Conv1 特征图 | (20,24,24) | (20,24,24) | ✅ |
| Pool1 特征图 | (20,12,12) | (20,12,12) | ✅ |
| Batch=4 输出 | (4,10) | (4,10)，4个样本Top-3预测正常 | ✅ |
| ReLU 手动验证 | max(0,x) | [0,0,0,1,2] vs [0,0,0,1,2] | ✅ |
| Softmax 手动验证 | NumPy计算一致 | [0.076,0.076,0.076,0.207,0.564] (atol<1e-6) | ✅ |
| 概率和 | 1.0 | 1.000000 | ✅ |

---

## 第3章 · 模式萃取（E阶段）

```
[CMD-LOG] | level=INFO | cmd=extraction | step=S0 | event=CMD_START | session=ext-20260727-caffe-notebook | msg=开始模式萃取：Jupyter Notebook生成与Caffe前向传播测试模式
```

### 3.1 模式一：Jupyter Notebook 程序化生成模式

**模式名称**：`jupyter-notebook-programmatic-generation`

**触发场景**：需要通过 AI/脚本自动生成 Jupyter Notebook 文件时

**问题本质**：手动编辑 Notebook JSON 容易出错（语法错误、格式不符合 nbformat 规范）；直接将多行代码字符串放入 source 字段会导致换行符丢失。

**解决方案**：

1. 使用 Python 脚本程序化构建 Notebook JSON
2. 关键工具函数 `lines()` 将多行字符串拆分为 Jupyter 规范的行数组
3. 每个 code/markdown cell 分别用 `code_cell()` / `md_cell()` 工厂函数创建
4. 生成后立即验证：读取 JSON 检查 source 行格式正确性

**核心代码模板**：

```python
def lines(*args):
    """Split multi-line strings into Jupyter-compliant source lines."""
    result = []
    for arg in args:
        for line in arg.split('\n'):
            result.append(line + '\n')
    if result and result[-1].endswith('\n'):
        result[-1] = result[-1][:-1]  # Last line: no trailing \n
    return result

def md_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": lines(source)}

def code_cell(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": lines(source)}
```

**注意事项**：
- Python 代码中包含 `'''` 三引号字符串时，需要用转义（`\'\'\'`）处理嵌套
- `%matplotlib inline` 等 IPython magic 命令在非 IPython 环境执行时需要注释掉
- 生成后必须在真实 Jupyter/内核环境中验证执行

**成熟度**：L2（已在本任务中验证，可复用）

### 3.2 模式二：Caffe 零外部数据依赖网络定义模式

**模式名称**：`caffe-netspec-dummydata-zerodependency`

**触发场景**：需要创建 Caffe 网络用于测试/教学/验证，不希望依赖外部数据集或模型文件

**问题本质**：Caffe 传统网络定义需要 lmdb/leveldb/hdf5 数据源，编写测试网络时配置繁琐。

**解决方案**：
1. 使用 `caffe.NetSpec()` 程序化定义网络
2. 数据层使用 `L.DummyData(shape=dict(dim=list(input_shape)))` 生成指定形状的随机数据
3. 权重初始化使用 `weight_filler=dict(type='xavier')` 和 `bias_filler=dict(type='constant', value=0.1)`
4. Softmax 层必须确保类别数在 C 维度（axis=1）

**标准网络结构**：
```
DummyData(shape) → Conv(kernel,num_output) → ReLU(in_place) → MaxPool(kernel,stride)
→ InnerProduct(num_output) → ReLU(in_place) → ... → Softmax(axis=1)
```

**关键约束**：
- 输入形状必须是 `(N, C, H, W)` 四元组
- 卷积后尺寸计算公式：`out = (in - kernel + 2*pad) / stride + 1`
- 全连接层前需确保 C×H×W 乘积匹配 `num_output` 的输入维度
- Softmax 必须有 `axis=1`（通道维），类别数放在 C 维度

**成熟度**：L2（已通过手动计算验证 ReLU/Softmax 正确性）

### 3.3 模式三：容器内无头 Notebook 执行验证模式

**模式名称**：`container-headless-notebook-verification`

**触发场景**：需要在无浏览器的 Docker/服务器环境中批量验证 Jupyter Notebook 执行正确性

**解决方案**：
1. 设置 `matplotlib.use('Agg')` 非交互式后端
2. Monkey-patch `plt.show()` 为 no-op（或输出标记）
3. 使用 `contextlib.redirect_stdout/stderr` 捕获每个 cell 的输出
4. 通过 `exec(code, namespace)` 在共享命名空间中逐 cell 执行
5. 替换 IPython magic（`%matplotlib inline` → 注释）
6. 检查关键输出（形状、数值和、异常）

**核心验证脚本结构**：
```python
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.show = lambda *a, **kw: print("[plot displayed]")

for i, cell in enumerate(code_cells):
    source = ''.join(cell['source'])
    source = source.replace('%matplotlib inline', '# skipped')
    try:
        exec(source, namespace)
        if 'plt' in namespace:
            namespace['plt'].show = lambda *a, **kw: None
    except Exception as e:
        print(f"Cell {i+1} FAILED: {e}")
```

**成熟度**：L2（已验证 12/12 cells 全部通过）

### 3.4 模式四：Caffe Blob 维度与 Softmax axis 配置模式

**模式名称**：`caffe-blob-dimension-softmax-axis`

**触发场景**：使用 Caffe 定义分类网络时配置 Softmax 层

**核心规则**：
1. Blob 维度顺序固定为 **(N, C, H, W)**
2. Softmax 默认 `axis=1`（沿通道维 C 计算），类别数 = C
3. 分类网络输入标签也需对应 axis=1
4. 验证方法：`prob.sum(axis=1)` 应全为 1.0

**常见错误配置**：
| 错误形状 | 错误原因 | 正确形状 |
|---------|---------|---------|
| `(1,1,1,C)` | C 放在 W 维，Softmax 在 C=1 的通道上做 | `(1,C,1,1)` |
| 忘记设置 axis | 多层级网络时可能 Softmax 在错误维度 | 显式设置 `softmax_param { axis: 1 }` |
| FC 输出维度≠类别数 | Softmax 输出维度不匹配类别 | InnerProduct num_output=num_classes |

**成熟度**：L2（已通过手动计算对比验证）

---

## 第4章 · 改进建议（Action Items）

| # | 建议 | 优先级 | 验收标准 | 关联模式 |
|---|------|--------|---------|---------|
| ACT-1 | 将 `lines()`/`code_cell()`/`md_cell()` 工具函数沉淀为 `.agents/scripts/` 共享库，供后续 Notebook 生成任务复用 | 中 | 存在可 import 的 Python 模块，包含上述函数 | 模式一 |
| ACT-2 | 为 Caffe 相关 Notebook 添加训练（backward pass）示例章节（`caffe.Solver` + SGD 训练） | 低 | Notebook 新增章节，包含 solver 定义、训练循环、loss 下降曲线 | 模式二 |
| ACT-3 | 将无头 Notebook 验证脚本沉淀为通用工具（支持参数化 notebook 路径和 cell 范围） | 中 | 可命令行调用的 Python 脚本，支持 `--notebook`、`--cells`、`--backend` 参数 | 模式三 |
| ACT-4 | 在 Caffe workspace 创建 `examples/` 目录结构，组织多个 Notebook（01_forward_pass、02_training、03_feature_extraction 等） | 低 | 目录结构清晰，每个 Notebook 独立 | - |

---

## 附录A · 关键代码片段索引

### A.1 最小 Caffe 前向传播网络（NetSpec方式）

```python
import caffe
from caffe import layers as L, params as P

ns = caffe.NetSpec()
ns.data = L.DummyData(shape=dict(dim=[1, 1, 28, 28]))
ns.conv1 = L.Convolution(ns.data, kernel_size=5, num_output=20, stride=1,
    weight_filler=dict(type='xavier'), bias_filler=dict(type='constant', value=0.1))
ns.relu1 = L.ReLU(ns.conv1, in_place=True)
ns.pool1 = L.Pooling(ns.relu1, kernel_size=2, stride=2, pool=P.Pooling.MAX)
ns.fc = L.InnerProduct(ns.pool1, num_output=10,
    weight_filler=dict(type='xavier'), bias_filler=dict(type='constant', value=0.1))
ns.prob = L.Softmax(ns.fc)

net = caffe.Net.from_string(str(ns.to_proto()), caffe.TEST)
output = net.forward()
print(output['prob'])
```

### A.2 最小 Caffe 前向传播网络（prototxt方式）

```python
prototxt = '''name: "MinimalNet"
layer { name: "data" type: "DummyData" top: "data"
  dummy_data_param { shape { dim: 1 dim: 5 dim: 1 dim: 1 } } }
layer { name: "relu" type: "ReLU" bottom: "data" top: "relu" }
layer { name: "prob" type: "Softmax" bottom: "relu" top: "prob"
  softmax_param { axis: 1 } }'''

import tempfile, os
with tempfile.NamedTemporaryFile(mode='w', suffix='.prototxt', delete=False) as f:
    f.write(prototxt); path = f.name
net = caffe.Net(path, caffe.TEST)
os.unlink(path)
out = net.forward()
```

### A.3 自定义数据注入与预测

```python
import numpy as np
net.blobs['data'].data[...] = my_input_array  # shape: (N,C,H,W)
output = net.forward()
prob = output['prob']
pred_class = np.argmax(prob, axis=1)
pred_conf = np.max(prob, axis=1)
```

---

## 附录B · 访问方式

| 资源 | 地址/命令 |
|------|---------|
| Jupyter Notebook | http://localhost:8888/notebooks/01_caffe_forward_pass.ipynb?token=mysecret |
| Jupyter Tree | http://localhost:8888/tree/notebooks?token=mysecret |
| 容器启动 | `cd projects/xuanspace/vendor/caffe/docker/origin && bash run-jupyter.sh start` |
| 容器状态 | `bash run-jupyter.sh status` |
| 容器日志 | `bash run-jupyter.sh logs` |
