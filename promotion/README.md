# Promotion 推广运营资产目录

本目录用于存放所有推广运营相关的内容资产，结构可复用，适用于各类产品/项目的推广。

---

## 目录结构

```
promotion/
├── methodology/                # 推广方法论与可复用模式
│   └── README.md               # 方法论索引
└── <project-name>/              # 按推广项目/产品分子目录
    ├── articles/                # 推广文章（按发布平台分子目录）
    │   ├── zhihu/              # 知乎文章
    │   ├── juejin/             # 掘金/CSDN/思否等技术社区
    │   ├── xiaohongshu/        # 小红书图文
    │   ├── wechat/             # 公众号/朋友圈/微信群文案
    │   ├── douyin/             # 抖音/B站短视频脚本（按需添加）
    │   └── other/              # 其他平台
    ├── assets/                  # 推广素材
    │   ├── images/             # 截图、海报、配图
    │   ├── videos/             # 视频素材
    │   └── qrcodes/            # 二维码素材
    ├── scripts/                 # 话术模板
    │   ├── private-msg/        # 1对1私信话术
    │   ├── group-chat/         # 群聊话术
    │   ├── comment/            # 评论区回复模板
    │   └── live/               # 直播/线下分享话术
    └── data/                    # 数据追踪
        ├── links.md            # 推广链接汇总
        ├── results/            # 推广效果记录
        └── analytics/          # 数据分析
```

---

## 现有资产

| 目录 | 说明 |
|---------|------|
| [methodology/](methodology/) | 推广运营方法论与可复用模式库 |
| [miaowu-ambassador/](miaowu-ambassador/) | 秒悟Meoo推广大使相关内容 |

---

## 文件命名规范

### 文章命名
格式：`YYYY-MM-DD-<topic>-<platform>.md`

示例：
- `2026-07-31-zhujian-wudao-zero-code-tutorial-zhihu.md`
- `2026-08-01-miaowu-quick-start-juejin.md`
- `2026-08-05-first-app-tutorial-xiaohongshu.md`

### 素材命名
格式：`<project>-<type>-<description>-<date>.<ext>`

示例：
- `miaowu-screenshot-homepage-20260731.png`
- `miaowu-poster-launch-v1.png`

---

## 文章内容规范

### 通用原则
1. **真实优先**：基于真实使用体验，不夸大宣传
2. **价值先行**：先提供价值（教程、案例、经验），再自然带出推广链接
3. **必要提醒**：涉及关联规则（如二次点击）必须明确说明
4. **免责声明**：涉及收益参考时需注明"不构成收益承诺"

### 平台适配
- **知乎**：深度长文，逻辑清晰，有干货，语气真诚不硬推
- **掘金/CSDN**：技术教程为主，步骤清晰，可贴代码/配置
- **小红书**：图文并茂，语气轻松，多用emoji，首图吸引人
- **微信生态**：更口语化、有温度，适合熟人/私域传播

---

## 新推广项目创建流程

1. 在 `promotion/` 下创建项目子目录：`mkdir -p promotion/<project-name>/{articles,assets,scripts,data}`
2. 按需要在 `articles/` 下创建对应平台子目录
3. 开始创作第一篇文章，遵循命名规范
4. 推广链接、素材、话术分别放入对应目录

---

**最后更新**：2026-07-31
