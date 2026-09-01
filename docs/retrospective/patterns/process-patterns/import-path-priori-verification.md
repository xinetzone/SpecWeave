---
id: "import-path-priori-verification"
title: "导入路径先验验证模式"
type: "process-pattern"
date: "2026-07-23"
maturity: "L1-draft"
source: "retrospective-pycaffe-image-preprocessing-optimization-20260723"
related_patterns: ["fail-loud-over-silent-fallback", "format-evidence-over-memory-pattern"]
tags: ["import", "verification", "dependencies", "ci-cd", "debugging", "best-practice"]
---

# 导入路径先验验证模式

写新模块前，先用最小验证脚本测试第三方库的导入路径和 API，避免长构建链末端才发现依赖配置错误。

## 触发场景

- 新建模块依赖第三方库，对库的 API 结构记忆不确定
- CI/CD 构建链较长（编译 + 打包 + Docker 构建），构建失败返工成本高
- 库有多个版本，不同版本 API 路径可能不同
- 跨平台开发，不同平台下库的可用性不同

**不适用于**：
- 已经在项目中广泛使用的成熟依赖（路径已知正确）
- 纯标准库模块，无第三方依赖
- 一次性脚本，写完就扔

## 核心做法

### 1. 三行验证脚本

写完整模块前，先写最小验证脚本确认导入路径正确：

```python
# 验证三步：导入 → 调用核心 API → 输出结果
import the_library           # 1. 路径对不对？
result = the_library.core_func()  # 2. API 叫什么？
print(type(result), result)       # 3. 返回什么？
```

耗时：30 秒 ~ 2 分钟。节省：5 ~ 30 分钟的构建返工。

### 2. 优先使用基础 API

优先选择更底层、更稳定、更少依赖的 API 实现：

| 场景 | 高级 API（易变） | 基础 API（稳定） |
|------|-----------------|-----------------|
| 图像归一化 | `skimage.img_as_float()` | 手动 `img.astype(np.float32) / 255.0` |
| 数组深拷贝 | `copy.deepcopy(arr)` | `np.array(arr, copy=True)` |
| 时间格式化 | `pandas.Timestamp().strftime()` | `datetime.strftime()` |

选择标准：基础 API 是否能在 3 行内完成相同功能？能 → 用基础的。

### 3. try-except + fallback

可选依赖必须放在 try-except 中，提供降级方案：

```python
try:
    import cv2
    _HAS_CV2 = True
except ImportError:
    _HAS_CV2 = False
    from skimage.transform import resize as _sk_resize

def resize_image(im, new_dims):
    if _HAS_CV2:
        return cv2.resize(im, ...)  # 快速路径
    else:
        return _sk_resize(im, ...)  # 降级路径
```

### 4. CI 早期 smoke test

在 CI 流水线最早阶段执行 import smoke test：
- 只做 import，不跑完整功能测试
- 失败立即终止，不浪费后续构建时间
- 测试所有可选依赖的导入路径

## 反模式

- ❌ **凭记忆写导入路径**："应该是 xxx 吧" → 等构建验证 → 失败 → 返工
- ❌ **一次写完整模块再测试**：写了几百行才发现 import 路径错了
- ❌ **没有 fallback**：库不可用时整个模块崩溃，而非优雅降级
- ❌ **import 全堆在文件顶部**：可选依赖和必选依赖混在一起，出错难以定位
- ❌ **依赖版本不锁定**：开发环境和 CI 环境库版本不一致，导入路径可能不同

## 检验标准

做完之后怎么知道做对了？

1. **导入成功率**：新模块第一次构建时 import 相关失败率 < 5%
2. **优雅降级**：缺少可选依赖时，模块仍能正常 import（功能降级而非崩溃）
3. **早期发现**：import 相关构建失败在 CI 早期阶段（< 2 分钟）被发现
4. **有验证记录**：写模块前有验证步骤，不是写完才发现 import 错了

## 迁移示例

这个模式还能用在什么其他场景？

- **API 集成**：接入新 API 前，先用 curl 测试鉴权和核心端点，再写完整客户端
- **数据库接入**：接入新数据库前，先测试连接 + 最简单查询，再写完整 DAO
- **云服务配置**：配置新云服务前，先测试 key 是否有效 + 核心操作，再做完整部署
- **硬件驱动**：接入新硬件前，先测试基本通信是否正常，再写完整控制逻辑
- **第三方 SDK**：集成新 SDK 前，先跑通 hello world 示例，再做深度集成
