# 历史人物交互地图课件合集

本目录收纳「历史人物生平足迹交互地图课件」，每个人物一个子目录，互不干扰。
根目录 `index.html` 是**合集总览首页**，带人物切换入口。

## 目录结构
```
history-map-courseware/
├── index.html         ← 合集总览首页（人物卡片入口，双击打开）
├── manifest.js        ← 人物清单（首页据此动态渲染卡片）
├── README.md          ← 本说明
├── laozi/             ← 老子课件
│   ├── index.html         课件主文件（双击打开）
│   ├── app.js             交互逻辑（地图/时间线/巡览）
│   ├── laozi_data.js      内嵌数据（坐标·讲稿·依据）
│   ├── laozi_data.json    数据 JSON 版（便于查看/二次编辑）
│   └── 打开说明.md
├── zhuangzi/          ← 庄子课件（同结构）
└── kongzi/            ← 孔子课件（同结构）
```

## 打开方式
- **总览首页**：双击根目录 `index.html` → 看到人物卡片，点任一卡片进入该人物的交互地图。
- **单独课件**：也可直接双击某人物目录下的 `index.html`。

## 已有课件
| 人物 | 目录 | 打开方式 |
|---|---|---|
| 老子 | `laozi/` | 双击 `laozi/index.html` |
| 庄子 | `zhuangzi/` | 双击 `zhuangzi/index.html` |
| 孔子 | `kongzi/` | 双击 `kongzi/index.html` |

## 新增人物课件的约定
1. 在本目录下新建 `<人物拼音>/` 子目录（如 `kongzi/`、`zhuangzi/`）。
2. 每个子目录内保持同样的四件套：`index.html` + `app.js` + `<name>_data.js` + 可选 `_data.json`。
3. 数据以 `window.<NAME> = {...}` 形式内嵌为 JS，保证 `file://` 双击即可打开，无需本地服务器。
4. 统一使用 Leaflet + OpenStreetMap 真实底图；每个地图点含「时间·古今地名·经纬度·事件·定位方法·置信度·史料依据」，存疑处标注「存疑」。
5. **在 `manifest.js` 的 `people` 数组追加一项**（name/aka/era/role/quote/points/region/accent/entry），总览首页会自动多出一张卡片，无需改首页代码。

