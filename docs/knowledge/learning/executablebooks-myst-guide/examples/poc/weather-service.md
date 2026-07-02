---
source: "MyST MCP Server PoC示例 - Weather Service"
name: "weather-service"
version: "2.0.0"
description: "天气查询与出行建议MCP服务，提供实时天气、多日预报、城市搜索和出行提示生成"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/executablebooks-myst-guide/examples/poc/weather-service.toml"
id: "poc-weather-service"
title: "Weather Service MCP Server"
---
# Weather Service MCP Server

这是一个天气服务 MCP Server 示例，演示如何通过 MyST 指令定义：
- **Tools**（工具）：查询天气、预报、搜索城市
- **Resources**（资源）：城市信息、天气预警
- **Prompts**（提示词）：天气报告生成、出行建议

本文件既可作为人类阅读的 API 文档，也可直接被 `myst_mcp_server.py` 解析并运行。

````{mcp:server} weather-service
:version: 2.0.0
:transport: stdio

Weather Service 提供全球城市天气查询、多日天气预报、城市搜索和智能出行建议能力。
支持摄氏度/华氏度切换，可按语言返回结果。

## 工具

```{mcp:tool} get_current_weather
:description: 获取指定城市的当前实时天气

根据城市名称查询实时天气信息，包括温度、湿度、风速、天气状况等。
城市名称支持中英文，可指定返回温度单位。

```{mcp:param} city
:type: string
:required: true
城市名称，如 "Beijing"、"上海"、"Tokyo"
```

```{mcp:param} units
:type: string
:required: false
:default: metric
:enum: metric,imperial
温度单位：metric（摄氏度）、imperial（华氏度）
```

```{mcp:param} language
:type: string
:required: false
:default: zh
:enum: zh,en,ja
返回结果的语言
```
```

```{mcp:tool} get_weather_forecast
:description: 获取指定城市未来多日天气预报

查询指定城市未来 N 天的天气预报，包括每日最高/最低温度、降水概率、天气状况。

```{mcp:param} city
:type: string
:required: true
城市名称
```

```{mcp:param} days
:type: integer
:required: false
:default: 3
预报天数，1-7天
```

```{mcp:param} units
:type: string
:required: false
:default: metric
:enum: metric,imperial
温度单位
```
```

```{mcp:tool} search_cities
:description: 按关键词搜索匹配的城市列表

根据关键词模糊搜索城市，返回匹配的城市列表及其基本信息（国家、经纬度）。

```{mcp:param} query
:type: string
:required: true
搜索关键词，支持城市名拼音、中文、英文
```

```{mcp:param} limit
:type: integer
:required: false
:default: 5
返回结果数量上限，1-20
```
```

```{mcp:tool} compare_weather
:description: 对比多个城市的天气

同时查询多个城市的当前天气，便于对比分析。适用于出行决策、旅行规划等场景。

```{mcp:param} cities
:type: array[string]
:required: true
要对比的城市名称列表，如 ["北京", "上海", "广州"]
```

```{mcp:param} units
:type: string
:required: false
:default: metric
:enum: metric,imperial
温度单位
```
```

## 资源

```{mcp:resource} city-info
:uri: weather://cities/{city_id}
:name: 城市详情信息
:mime-type: application/json
{
  "id": "{city_id}",
  "name": "示例城市",
  "country": "CN",
  "timezone": "Asia/Shanghai",
  "coordinates": {"lat": 39.9, "lon": 116.4},
  "population": 21540000
}
```

```{mcp:resource} weather-alerts
:uri: weather://alerts/{region}
:name: 天气预警信息
:mime-type: application/json
{
  "region": "{region}",
  "alerts": [
    {
      "type": "暴雨预警",
      "level": "橙色",
      "issued_at": "2026-07-02T08:00:00+08:00",
      "description": "预计未来6小时内将出现大到暴雨，请注意防范。"
    }
  ],
  "updated_at": "2026-07-02T10:30:00+08:00"
}
```

```{mcp:resource} weather-icon-legend
:uri: weather://legend/icons
:name: 天气图标图例
:mime-type: text/markdown
# 天气图标图例

| 图标 | 含义 |
|------|------|
| ☀️ | 晴天 |
| ⛅ | 多云 |
| ☁️ | 阴天 |
| 🌧️ | 小雨 |
| ⛈️ | 雷阵雨 |
| ❄️ | 雪 |
| 🌫️ | 雾 |
```

## 提示词

```{mcp:prompt} daily-weather-report
:description: 生成每日天气简报

为指定城市生成一份结构化的每日天气简报，包含天气概况、穿衣建议、出行提醒。

```{mcp:arg} city
:type: string
:required: true
:description: 要生成天气报告的城市名称
```

```{mcp:arg} style
:type: string
:required: false
:default: concise
:enum: concise,detailed,humorous
:description: 报告风格：简洁/详细/幽默
```

# 🌤️ {city} 天气日报

## 当前天气概况
[此处将填充实时天气数据]

## 穿衣建议
[根据温度和天气状况给出建议]

## 出行提醒
[根据降水概率、风速等给出提醒]

---
*由 Weather Service 自动生成*
```

```{mcp:prompt} travel-packing-list
:description: 根据目的地天气生成行李打包清单

根据目的地的天气预报，智能生成出行打包建议清单，考虑天气、行程天数和活动类型。

```{mcp:arg} destination
:type: string
:required: true
:description: 目的地城市
```

```{mcp:arg} days
:type: integer
:required: false
:default: 3
:description: 旅行天数
```

```{mcp:arg} activities
:type: array[string]
:required: false
:description: 计划的活动类型，如 ["hiking", "business", "beach"]
```

# 🧳 {destination} 出行打包清单

## 📅 行程信息
- 目的地：{destination}
- 天数：{days} 天
- 活动：{activities}

## 👕 衣物建议
[根据天气预报推荐合适的衣物]

## 🎒 必备物品
[根据活动类型推荐必备物品]

## ⚠️ 特别提醒
[根据天气预警等信息给出特别注意事项]
```
````
