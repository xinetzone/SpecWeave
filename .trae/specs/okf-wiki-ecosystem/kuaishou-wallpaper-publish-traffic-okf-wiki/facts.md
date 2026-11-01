# 事实登记：快手发布壁纸作品引流教程（F-001~F-053）

> 本表登记「快手发布壁纸作品引流教程」信源中可直接回溯的事实，**不含执行者推断**。
> 口径类型枚举：`page_fact`（源页面 HTML 直接实测）/ `meta`（本包自身元事实，如采集通道、核验结论）/ `video_claim`（源视频音轨 ASR 转写中讲解者的陈述，一律视为「讲师口径」而非官方规则）/ `official_doc`（官方文档）/ `third_party`（第三方来源）。
> 本包**无 `reporter_test`**（无记者一手实测环节）。
> 核验结论、勘误与缺口见 bundle 内 [references/verification.md](../../../../projects/awesome-okf-xs/doc/bundles/sheke/industry/kuaishou-wallpaper-publish-traffic/references/verification.md)。

- **一手信源**：微信公众号图文 `https://mp.weixin.qq.com/s/Cvyuyo6uNV0zhfl2_ybEAw?scene=1`（标题《快手发布-视频教程》，公众号「特级班班资料小屋」）
- **采集时间**：2026-11-01
- **采集通道**：页面 HTML 直取（`js_content` 实测）＋ 内嵌视频音轨本地离线 ASR 转写（`local-asr`，Intel AIPC）
- **信源距离**：第三方综述 / 讲师口播教程（非官方发布、非本包执行者实测）；页面正文无文字，唯一知识载体为 4 分 02 秒视频音轨
- **外部核验信源**：快手开放平台官方文档（`open.kuaishou.com`）、第三方来源族（Bilibili 简介、微头条话题、非凡软件站、newrank、`privacy.kuaishou.com/policy`、php.cn）

## A. 源文元信息（F-001~F-005）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 信源图文标题为《快手发布-视频教程》（页面 `msg_title`） | page_fact | S1 | 页面 HTML `msg_title` | 页面实测 |
| F-002 | 信源公众号昵称为「特级班班资料小屋」（页面 `var nickname`） | page_fact | S1 | 页面 HTML `nickname` | 页面实测 |
| F-003 | 信源图文页微信号为 `gh_dea7fd7c569a`，摘要 `msg_desc` 为「👉点击此处进入，即可查看」 | page_fact | S1 | 页面 HTML `user_name` / `msg_desc` | 页面实测 |
| F-004 | 页面 DOM 时间戳 `ct = 1788787853`，换算为北京时间 **2026-09-07 21:30** | meta | S1 | 页面 HTML `ct` | 元事实（发布时点；与另一次 WebFetch 记录的 13:30 存在口径差异，见 verification E-4） |
| F-005 | 图文正文无知识性文字，`js_content` 仅约 3588 字符，唯一内容为一个 242.67 秒（4 分 02 秒）的视频 `video_iframe`（`data-mpvid=wxv_4684122996708737027`，544×308）与两则红字警示（「教学步骤里面只看上面的学习资料」「下面的任何广告都不要点！！！」） | meta | S1 | 页面 HTML `js_content` | 元事实（说明本包须以视频音轨为唯一信源） |

## B. 前置·口令获取（F-006~F-010）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-006 | 操作起点是先从「推图社」小程序取得属于自己（发布者）的「口令」 | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-007 | 口令获取入口之一：在快手 App 顶部搜索（放大镜）中搜「推图社」进入小程序 | video_claim | S2 | ASR 全片首段 / 桥接段 | 讲师口径 |
| F-008 | 口令获取入口之二：点快手左上角「三横杠」菜单，从「常用小程序」进入 | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-009 | 进入小程序后输入口令完成身份绑定，且该口令对应的是发布者本人 | video_claim | S2 | ASR 桥接段 | 讲师口径 |
| F-010 | 小程序内含壁纸库，取图前应先核对壁纸库内容 | video_claim | S2 | ASR 全片首段 | 讲师口径 |

## C. 快手端入口·发快手（F-011~F-014）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-011 | 在壁纸库界面右上角「三个小点」（更多菜单）中触发「发快手」 | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-012 | 「发快手」是小程序内提供的、跳转到快手发布页的挂载能力 | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-013 | 进入发布页后默认落在「随手拍」模式 | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-014 | 图集发布应只点「相册」进入本地相册选图，不使用「随手拍」 | video_claim | S2 | ASR 全片首段 | 讲师口径 |

## D. 发布流程·选图与编辑（F-015~F-019）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-015 | 在本地相册中选取壁纸图片，讲解者实际演示选取约 9~15 张 | video_claim | S2 | ASR 全片首段 | 讲师口径（演示值，非平台上限，见 F-050/F-051） |
| F-016 | 讲解者对图片数量的表述为「9~15 张」（讲师口径） | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-017 | 选图完成后点右下角「下一步」进入编辑页 | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-018 | 编辑页背景音乐默认可直接使用，也可另行更换 | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-019 | 编辑页处理完成后再次点「下一步」进入发布信息填写页 | video_claim | S2 | ASR 全片首段 | 讲师口径 |

## E. 引流文案（F-020~F-023）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-020 | 描述区（文案区）须填入固定引流文案 | video_claim | S2 | ASR 全片首段 | 讲师口径 |
| F-021 | 引流文案中须包含口令引导语（引导观众输入口令获取同款壁纸） | video_claim | S2 | ASR 全片首段 / 桥接段 | 讲师口径 |
| F-022 | 文案格式由讲师统一提供，学员照抄即可 | video_claim | S2 | ASR 全片首段 / 桥接段 | 讲师口径 |
| F-023 | 文案目的是把观众引导至自己的壁纸库/小程序口令 | video_claim | S2 | ASR 全片首段 / 桥接段 | 讲师口径 |

## F. 话题（F-024~F-028）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-024 | 在描述区点「#」（井号键）插入话题 | video_claim | S2 | ASR 桥接段 | 讲师口径 |
| F-025 | 话题须选播放量高的，讲解者举例「五点几亿」「一点几亿」量级 | video_claim | S2 | ASR 桥接段 | 讲师口径 |
| F-026 | 建议添加 2~3 个高播放量话题以蹭热点 | video_claim | S2 | ASR 全片首段 / 桥接段 | 讲师口径 |
| F-027 | 话题添加完毕后「碰一下空格」即可结束话题输入 | video_claim | S2 | ASR 全片首段 / 桥接段 | 讲师口径 |
| F-028 | 话题区以外的其他编辑入口在本流程中「都不用点」 | video_claim | S2 | ASR 全片首段 | 讲师口径 |

## G. 发布前设置（F-029~F-036）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-029 | 本节全部条目均来自讲师真机演示的界面状态，非平台官方规则文本 | meta | S2 | ASR 全片首段 / 桥接段 / 尾段 | 元事实（口径声明） |
| F-030 | 「位置（定位）」不点选/不公开 | video_claim | S2 | ASR 桥接段 | 讲师口径 |
| F-031 | 可见范围设为「公开可见」 | video_claim | S2 | ASR 桥接段 | 讲师口径 |
| F-032 | 「关联小程序」开关不点（不使用该功能） | video_claim | S2 | ASR 桥接段 | 讲师口径 |
| F-033 | 需进入「更多设置」调整一项设置 | video_claim | S2 | ASR 桥接段 | 讲师口径 |
| F-034 | 在「更多设置」中须把「允许下载」**关闭**（呈灰色即为关闭状态） | video_claim | S2 | ASR 尾段 | 讲师口径（无官方口径，见 F-049） |
| F-035 | 「允许下载」关闭后，他人无法下载该作品 | video_claim | S2 | ASR 尾段 | 讲师口径（推论性陈述，未获官方口径） |
| F-036 | 设置完成后点「叉掉」关闭「更多设置」面板 | video_claim | S2 | ASR 尾段 | 讲师口径 |

## H. 发布后与作业交付（F-037~F-046）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-037 | 设置完成后点「发布」按钮提交作品 | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-038 | 发布完成后停留在发布成功界面 | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-039 | 发布后应关掉（退出）该成功界面 | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-040 | 从快手右下角「我的」进入查看自己已发布的作品 | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-041 | 作业交付方式为**截图** | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-042 | 可在「我的」中对已发布作品截图交作业 | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-043 | 也可点进作品详情页截图后发给老师 | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-044 | 作业交付禁止随意转发作品 | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-045 | 作业约束：当天只发布一条 | video_claim | S2 | ASR 尾段 | 讲师口径 |
| F-046 | 「今天只发一个」为讲师对学员的作业约束（非平台规则） | video_claim | S2 | ASR 尾段 | 讲师口径 |

## I. 外部核验（F-047~F-053）

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-047 | 小程序名称「**推图社**」经多源确认（Bilibili 简介、微头条话题 #壁纸屏保分享#、非凡软件站）；ASR 转写中的「推图设」「推流社」均为音近误识 | third_party | S4 | 多源交叉 | 第三方多源一致 |
| F-048 | 快手开放平台官方文档提供「发快手」能力说明（`https://open.kuaishou.com/docs/develop/functionAccessGuide/fksVideoMount.html`） | official_doc | S3 | 官方文档页 | 官方文档（确认能力存在，未给图片数量与权限开关口径） |
| F-049 | 「允许下载」类权限开关仅有第三方来源提及（newrank / `privacy.kuaishou.com/policy` / php.cn），**未取得快手官方规则文档口径** | third_party | S4 | 第三方来源族 | 第三方单源族，无官方口径 |
| F-050 | 图片数量存在**三口径冲突**：9 张 / 12 张 / 31 张，均无官方口径 | third_party | S4 | 第三方来源族 | 第三方口径冲突，未裁决 |
| F-051 | 第三方未见「9~15 张」为平台上限的表述，该数字仅为讲解者演示值 | third_party | S4 | 第三方来源族 | 第三方（用于否定「上限」表述） |
| F-052 | 「发快手」为快手向第三方小程序开放的挂载能力，非本教程独创 | third_party | S4 | 第三方来源族 | 第三方（与 F-048 互证） |
| F-053 | 本包未取得讲师身份、课程归属与「推图社」运营方的官方确认，信源为视频 ASR 转写而非原始文本 | meta | S2 | 本包核验过程 | 元事实（局限声明，决定 `status: flagged`） |

---

**合计：53 条（F-001~F-053，连续无跳号）**
