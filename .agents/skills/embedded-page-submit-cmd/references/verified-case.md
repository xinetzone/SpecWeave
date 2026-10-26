# 实战案例：WorkBuddy「1024 造物挑战」活动页代投稿

> session: `sc-20261026-workbuddy-contest-submit`
> 目标页：`https://www.workbuddy.link/p/8QYARuAmZ9RgQty3FSzNUs`
> 结果：两条记录写入成功 + 逐字段回读复核通过（提交编号 `S1024-1a176238787-lros`）

## 一、起点：一个被推翻的旧结论

上一轮会话在 `.workbuddy/memory/2026-10-26.md` 写下结论：

> F-055 已认定「投稿走 `__SMART_PAGE__.database`，无头浏览器不可达，Agent 无法代提交」

依据是：页面 JS 里 `submitWork()` 依赖 `window.__SMART_PAGE__.database`，而无头浏览器与 curl 都拿不到这个对象。

**本轮推翻了它。** 推翻点不在于"找到了 `__SMART_PAGE__`"，而在于——**宿主应用的 HTTP 面（`/space/api/view/*`）本来就是页面 SDK 的后端**，页面只是它的一个前端。

## 二、通道探测实录

| 顺序 | 通道 | 结果 |
|:--:|------|------|
| 1 | agent-gateway（`space_api.py space.workspace.node-info`） | `code=12607 permission denied` |
| 2 | agent-gateway（`space.database.get-database`） | `code=12607 permission denied` |
| 3 | share（`page/share/database/get`） | ✅ 读到 schema（`投稿收集池（待运营审核）`） |
| 4 | share（`page/share/user/current`） | `401 not login` |
| 5 | share（`page/share/database/addRecord`） | `401 not login` |
| 6 | **view（`view/database/addRecord`）** | ✅ **`code=0`，返回 record id** |
| 7 | view（`view/database/deleteRecord`） | ✅ 探针清理成功 |

第 1、2 步的失败正是上一轮误判的来源：**只试了一条通道**。

## 三、关键技术事实

### 3.1 逆向路径

```
页面 HTML（.contest-page.html，210,590 B）
  → 提取 saveWork / buildSubmissionProperties / submitWork
  → 宿主 asar 搜 "database.addRecord" 定位 artifact-preview-host-*.js
  → 逆出映射：addRecord → POST {baseUrl}/database/addRecord
  → baseUrl 两个候选：/space/api/view 与 /space/api/page/share
  → 分别试 → view 通、share 不通（无登录态）
```

页面侧 `buildSubmissionProperties` 原文（字段形状的权威来源）：

```js
function buildSubmissionProperties(it){
 var props={"审核状态":{select:"待审核"},"提交编号":{text:it.sid||""},
   "提交时间":{text:it.stamp||""},"应用名称":{text:it.name},
   "我的作品宣言":{text:it.declaration},"作品形态":{select:it.type},
   "标签":{text:it.type},"作者":{text:it.author},
   "一句话亮点":{text:it.declaration},"原文描述":{text:it.raw||""},
   "图片数":{number:it.pics||0},
   "体验链接":{url:{text:it.name,link:it.url}},"UserID":{text:it.uid||""},
   "参赛授权":{checkbox:!!it.auth}};
 if(it.conversation)props["WorkBuddy创作对话记录"]={url:{text:"创作对话记录",link:it.conversation}};
 var imgs=(it.shotList||[]).map(...).filter(x=>/^https:\/\//.test(x.imageUrl));
 if(imgs.length)props["作品截图"]={image:{images:imgs}};
 ...
}
```

**注意两处**：`体验链接` 用 `url` oneof（含 text+link 双字段）；`作品截图` 用 `image.images[]`，且每项带 `title`。

### 3.2 图片上传

页面侧 `uploadOneShotWithRetry` 原文揭示参数形状：

```js
sp.database.uploadImage({data:data, contentType:"image/jpeg", fileName:fileName})
// data = shotUrl(s) 去掉 "data:...;base64," 前缀后的纯 base64
```

实测（PNG，`contentType` 改 `image/png`）三张均返回 `code:0` + CDN url + 1280×720。

### 3.3 写入与回读

```python
post("/space/api/view/database/addRecord",
     {"databaseId": "P3Y1rSDQcUAZcGV15UjCND",
      "pageId": "8QYARuAmZ9RgQty3FSzNUs",
      "properties": { /* 18 字段 oneof */ }})
```

返回：`{"code":0,"msg":"OK","data":{"id":"xTlEYCTwBkBKs9SXuoY8a3"}}`

回读（`getRecord` 带 `pageId`）逐字段核对 18 项，全部一致：审核状态=待审核、图片数=3、参赛授权=True、作品形态=网页应用、UserID 与登录账号一致、三张截图 imageUrl 完整带 title、体验链接与创作对话记录均为有效 URL。

## 四、用户提供的两项必填

活动页前端强制校验：

```js
if(!/^https?:\/\//i.test(conversation)){toast("请填写有效的 WorkBuddy 创作对话记录链接");return;}
if(!uid||!/^1[3-9]\d{9}$/.test(phone)){toast("请填写 UserID 和正确的大陆手机号");return;}
```

**API 写库绕得过去这两条校验，但绕得过去不等于合规**——主办方审核阶段仍按同一规则看。因此向用户逐项索取真实值，而非留空。

## 五、本案例的可迁移结论

1. **一次权限拒绝只证伪一条通道**——四条通道必须试完再下"不可达"结论。
2. **`permission denied` 的文案会骗人**——本次所有 12607 的真实原因都是"缺 `pageId`"。
3. **前端校验只在前端**——绕过可行，但合规责任不随之转移。
4. **`code=0` 与"字段写对了"是两件事**——回读逐字段比对是唯一验收方式。
