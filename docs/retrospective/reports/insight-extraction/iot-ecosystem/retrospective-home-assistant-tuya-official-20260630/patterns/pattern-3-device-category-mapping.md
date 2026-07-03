---
id: "tuya-official-pattern-3-device-category-mapping"
title: "模式 3：设备分类到平台映射模式"
source: "insight-extraction.md#知识点-7设备分类到平台的映射"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/iot-ecosystem/retrospective-home-assistant-tuya-official-20260630/patterns/pattern-3-device-category-mapping.toml"
---
# 模式 3：设备分类到平台映射模式

**模式名称**：设备分类到平台映射模式

**核心理念**：
> 通过设备分类（DeviceCategory）映射到 Home Assistant 平台，实现设备的自动发现和实体创建，支持大规模设备类型的灵活扩展。

**适用场景**：
- 需要支持大量设备类型的 IoT 平台集成
- 设备类型到应用层实体的自动映射
- 模块化的平台扩展

**实现步骤**：

```markdown
1. **定义设备分类**
   - 使用枚举定义设备分类（DeviceCategory）
   - 每个分类对应一类设备（dj=灯光, cz=插座, sp=摄像头）
   - 支持复合分类（如 fs/fsd=风扇）

2. **定义实体描述**
   - 为每个平台定义实体描述（EntityDescription）
   - 包含 key、name、icon、device_class 等属性
   - 映射到具体的 DP Code

3. **建立分类到平台的映射**
   - 使用字典映射 DeviceCategory 到 EntityDescription 元组
   - 支持一个分类对应多个实体（如复合设备）
   - 支持平台间复用实体描述

4. **设备发现流程**
   - 获取设备分类
   - 查找对应平台的实体描述
   - 创建实体并注册到 Home Assistant
```

**关键代码示例**：

```python
# light.py - 定义映射
LIGHTS: dict[DeviceCategory, tuple[TuyaLightEntityDescription, ...]] = {
    DeviceCategory.DJ: (
        TuyaLightEntityDescription(
            key=DPCode.SWITCH_LED,
            color_mode=DPCode.WORK_MODE,
            brightness=DPCode.BRIGHT_VALUE,
        ),
    ),
}

# 发现流程
if descriptions := LIGHTS.get(device.category):
    entities.extend(TuyaLightEntity(device, manager, description, definition) 
                   for description in descriptions)
```

**设备分类映射表示例**：

| 设备分类 | Home Assistant 平台 | 说明 |
|---------|---------------------|------|
| `dj` | `light` | 灯光 |
| `cz/pc/kg` | `switch` | 开关/插座 |
| `sp` | `camera` | 摄像头 |
| `fs/fsd` | `fan` | 风扇 |
| `kt/ktkzq` | `climate` | 空调 |
| `sd` | `vacuum` | 扫地机器人 |

**效果验证**：
- 支持 100+ 设备分类
- 新设备类型只需添加映射
- 自动发现和实体创建

**局限性**：
- 需要维护完整的分类映射表
- 设备分类可能重叠或不明确
- 需要处理未知设备分类

**可复用场景**：
- IoT 平台设备发现
- 多设备类型支持
- 模块化平台扩展

---

**[返回洞察萃取索引](../insight-extraction.md)**
