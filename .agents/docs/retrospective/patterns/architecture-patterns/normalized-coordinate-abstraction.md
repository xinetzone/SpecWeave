---
id: "normalized-coordinate-abstraction"
source: "../../reports/competitive-analysis/retrospective-sunlogin-cli-wiki-20260706/insight-extraction.md#洞察2"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/architecture-patterns/normalized-coordinate-abstraction.toml"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"
related_patterns: ["multi-agent-closed-loop"]
validations:
  - source: "向日葵CLI桌面控制"
    date: "2026-07-06"
    context: "远程桌面鼠标/触摸控制"
  - source: "mobile-use移动自动化框架"
    date: "2026-07-07"
    context: "Android/iOS多分辨率设备UI自动化（PercentagesSelectorRequest→CoordinatesSelectorRequest）"
---
> **来源**：从向日葵企业CLI桌面控制功能复盘萃取，经向日葵CLI远程桌面控制和mobile-use移动自动化框架双重验证

# 归一化坐标抽象模式（Normalized Coordinate Abstraction Pattern）

## 模式类型

架构模式（交互协议抽象层设计）

## 成熟度

L2 双重验证（向日葵CLI桌面控制 + mobile-use移动自动化）

## 适用场景

需要对具有不同尺寸/分辨率/配置的目标发送统一控制指令：
- 远程桌面控制（鼠标移动/点击/拖拽）
- UI自动化测试（跨分辨率测试脚本）
- RPA机器人流程自动化（跨设备操作）
- 跨设备鼠标/触摸控制（手机/平板/PC统一控制协议）
- 远程演示/协作工具

## 问题背景

在远程控制或UI自动化场景中，如果使用绝对像素坐标：
1. **分辨率依赖**：不同分辨率（1920x1080、2560x1440、3840x2160）需要不同的坐标指令
2. **脚本不可移植**：在一台设备上编写的自动化脚本无法在另一台不同分辨率设备上运行
3. **AI认知负担**：AI Agent需要先查询目标分辨率，再根据分辨率计算目标位置坐标
4. **多显示器复杂**：多显示器布局导致坐标空间更加复杂
5. **缩放问题**：Windows DPI缩放、macOS Retina缩放导致逻辑像素与物理像素不一致

## 核心规则

归一化坐标抽象通过将坐标空间统一映射到[0.0, 1.0]区间，从控制协议中剥离"屏幕尺寸/分辨率"这一变量，使控制指令具有分辨率无关性。

**核心公式**：
```
归一化坐标 = 绝对坐标 / 目标维度尺寸
范围：x ∈ [0.0, 1.0], y ∈ [0.0, 1.0]
原点：(0.0, 0.0) = 左上角，(1.0, 1.0) = 右下角
映射责任：被控端负责将归一化坐标映射为实际像素坐标
```

### 三大核心要素

| 要素 | 规则 | 解决的问题 |
|------|------|-----------|
| 区间约束 | 坐标值必须在[0.0, 1.0]范围内，超出为非法输入 | 消除分辨率差异，统一坐标空间 |
| 协议无尺寸 | 控制协议中不携带分辨率/尺寸信息，指令完全归一化 | 控制端不需要知道目标尺寸，简化协议 |
| 被控端映射 | 实际像素坐标 = 归一化坐标 × 目标实际尺寸（宽/高） | 缩放/分辨率适配责任下沉到被控端 |

### 设计思想类比

- CSS百分比布局：使用`width: 50%`而非`width: 960px`，跨屏幕自适应
- 向量图形：相对坐标描述，渲染时缩放到目标分辨率
- 归一化数据库设计：将数据缩放到[0,1]区间，消除量纲影响

## 实现示例

### 示例1：向日葵CLI桌面控制（远程桌面场景）

```bash
# 向日葵CLI桌面点击 - 使用归一化坐标
# 点击屏幕中心（无论什么分辨率都是正中心）
awesun-cli desktop mouse click --x 0.5 --y 0.5 --button left

# 点击左上角（约10%位置）
awesun-cli desktop mouse click --x 0.1 --y 0.1 --button left

# 鼠标移动到右下角
awesun-cli desktop mouse move --x 0.9 --y 0.9
```

### 示例2：mobile-use移动自动化（手机UI控制场景）

mobile-use框架的UnifiedController同时支持绝对坐标和百分比坐标两种模式，百分比坐标运行时转换为像素：

```python
# PercentagesSelectorRequest: 使用百分比（0-100）
@dataclass
class PercentagesSelectorRequest:
    x_percent: int  # 0-100
    y_percent: int  # 0-100

    def to_coords(self, width: int, height: int) -> CoordinatesSelectorRequest:
        return CoordinatesSelectorRequest(
            x=int(self.x_percent / 100 * width),
            y=int(self.y_percent / 100 * height),
        )

# 使用方式：点击屏幕中间
await controller.tap_percentage(x_percent=50, y_percent=50)
# 在720x1280设备上 → 点击(360, 640)
# 在1440x2560设备上 → 点击(720, 1280)
# 同一指令跨分辨率语义一致
```

mobile-use的设计洞察：
- **LLM友好**：百分比比绝对像素更容易让LLM正确生成（"点击中间"=50%，"点击右上角"=90%,10%）
- **双模式并存**：对于已知精确位置的场景仍支持绝对坐标，百分比为默认推荐
- **滑动操作**：swipe_percentage同样使用百分比方向（右滑→左页：start=(90,50), end=(10,50)）

### 示例3：通用伪代码

```python
# 伪代码：被控端坐标映射
def normalized_to_pixel(norm_x: float, norm_y: float, screen_w: int, screen_h: int):
    """将归一化坐标转换为实际像素坐标"""
    px = int(norm_x * screen_w)
    py = int(norm_y * screen_h)
    # 边界钳制
    px = max(0, min(px, screen_w - 1))
    py = max(0, min(py, screen_h - 1))
    return px, py

# 示例：1920x1080屏幕中心 → (960, 540)
# 示例：3840x2160屏幕中心 → (1920, 1080)
# 同一指令(0.5, 0.5)在两种分辨率下都指向屏幕正中心
```

## 反模式（应避免）

- ❌ 协议中强制要求携带分辨率参数
- ❌ 控制端负责计算绝对像素坐标
- ❌ 坐标范围不做边界检查（允许>1.0或<0.0的值导致未定义行为）
- ❌ 滚轮/拖拽等操作不使用归一化增量
- ❌ 多显示器场景下不为每个显示器维护独立的归一化空间

## 扩展：拖拽与滚轮的归一化

- **鼠标拖拽**：起点和终点均使用归一化坐标，拖拽路径可以用归一化向量表示
- **滚轮滚动**：滚动量使用归一化增量（如0.1表示向下滚动10%的页面高度），而非固定行数
- **多显示器**：先选择显示器（索引或ID），在选定的显示器内使用归一化坐标

## 验证清单

- [ ] 控制指令中不含分辨率/尺寸参数
- [ ] 坐标值约束在[0.0, 1.0]区间
- [ ] 同一指令在不同分辨率下指向语义相同的位置（中心→中心，角→角）
- [ ] 被控端负责坐标映射，控制端无需知道目标尺寸
- [ ] 边界情况处理（0.0、1.0、接近边界值）
