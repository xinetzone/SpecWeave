---
id: "data-model-extraction-signal"
source: "../../reports/insight-extraction/standalone/insight-dockerfile-caching-20260703.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/data-model-extraction-signal.toml"
---
# 数据模型提取信号：代码跨越"脚本→应用"边界

## 模式概述

当一个项目开始出现独立的 `models.py`（或 `types.py`、`schemas.py`），将原始元组/字典替换为带类型的结构化数据对象时，这是代码从"过程式脚本集合"跨越到"类型安全应用"边界的明确信号。数据模型提取不仅仅是代码组织优化，更是架构成熟度跃迁的标志。

## 问题现象

脚本阶段常见的"原始数据"问题：

| 反模式 | 表现 | 风险 |
|--------|------|------|
| 返回裸元组 | `return (uid, gid, mode)` | 调用方需记住位置语义，易混淆 |
| 传递字典 | `{"uid": 1000, "gid": 1000}` | 无类型检查，键名拼写错误运行时才暴露 |
| 内联数据结构 | 每个函数自己解析返回值 | 修改数据结构需改多处 |
| 缺少格式化方法 | 散落的 `f"uid={uid}"` | 输出格式不一致 |

## 解决方案

### 提取信号识别

当出现以下任一信号时，应考虑提取数据模型：

1. **同一个元组/字典被3+个函数传递**：数据流跨越多个函数边界
2. **调用方需要记住字段顺序或键名**：认知负担转移到调用方
3. **多处代码手动格式化相同数据**：重复的展示逻辑
4. **类型注释开始出现 `dict[str, Any]`**：类型安全缺失

### 提取方法

```python
# 之前：裸元组
def stat_container(name: str) -> tuple[int, int, int]:
    return (uid, gid, mode)

# 调用方需记住位置
uid, gid, mode = stat_container("web")
print(f"uid={uid}")  # 如果误写 uid, mode, gid = ... 呢？

# 之后：结构化数据模型
from dataclasses import dataclass

@dataclass(frozen=True)
class StatInfo:
    uid: int
    gid: int
    mode: int

    def format(self) -> str:
        return f"uid={self.uid},gid={self.gid},mode={self.mode}"

def stat_container(name: str) -> StatInfo:
    return StatInfo(uid, gid, mode)

# 调用方按字段名访问
info = stat_container("web")
print(info.format())  # 统一格式化
```

### frozen dataclass 的三重价值

| 价值 | 说明 |
|------|------|
| 类型安全 | IDE 自动补全 + 静态类型检查 |
| 不可变性 | `frozen=True` 防止意外修改 |
| 自带方法 | `format()` 等展示逻辑内聚到数据本身 |

## 适用场景

- **脚本项目模块化**：从散落脚本重构为结构化应用时
- **API 边界定义**：函数间传递复杂数据时
- **配置管理**：从字典配置迁移到类型化配置时
- **测试数据构造**：需要构造结构化测试数据时

## 实际案例

### 案例1：llvm-dev 工具链 models.py 提取（首次验证）

**提取前**：
- `stat_container` 返回 `tuple[int, int, int]`
- 调用方需记住位置是 uid/gid/mode
- 多处手动格式化输出

**提取后**：
- 新增 `utils/models.py`，定义 `StatInfo`（frozen dataclass）、`Config` 等结构化类型
- `stat_container` 返回 `StatInfo(uid, gid, mode)`
- 有字段名、类型、`format()` 方法

**信号意义**：这个看似不起眼的文件是代码架构成熟的重要信号——项目正在从"过程式脚本集合"跨越到"类型安全的应用"边界。

## 反模式

### 反模式1：过早提取
```
只有1个函数使用该数据 → 提取为 dataclass → 过度设计
```
提取数据模型的成本应在3+个使用点后才能回收。

### 反模式2：提取为可变类
```python
@dataclass
class StatInfo:  # 缺少 frozen=True
    uid: int
    gid: int

info = stat_container("web")
info.uid = 0  # 意外修改！
```
数据传递过程中应保持不可变，使用 `frozen=True`。

### 反模式3：提取后仍用字典访问
```python
@dataclass
class StatInfo:
    uid: int

info = stat_container("web")
print(info["uid"])  # dataclass 不支持字典访问，会报错
```
提取后应统一使用属性访问 `info.uid`，而非混合使用。

## 与其他模式的关系

- **作为 toolchain-five-stage-evolution 的阶段1→2信号**：数据模型提取是模块化成熟的标志
- **与 defensive-attribute-access 互补**：数据模型提供类型安全，防御性访问处理外部数据
- **与 structured-doc-diff-semver 衔接**：结构化数据模型便于版本管理和差异比较

## 边界与选型

本模式适用于**从脚本向应用演进的项目**。判断信号：
- ✅ 项目有3+个函数传递相同的复合数据
- ✅ 调用方需要记住元组位置或字典键名
- ✅ 多处代码手动格式化相同数据
- ✅ 类型注释出现 `dict[str, Any]` 或 `tuple[int, ...]`
- ❌ 一次性脚本（数据结构简单，提取成本不划算）
- ❌ 已有 ORM/Schema 框架的项目（框架已提供数据模型）
