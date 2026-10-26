# WorkBuddy 智能页数据表端点速查（观测于 2026-10-26）

> **本文件是"端点层"**——记录 WorkBuddy 平台的具体路径、请求体形状与实测行为。
> 通用方法论（通道判定、oneof 形状规律、闸门设计、回读复核）在 `../SKILL.md`。
> **端点是易变资产**：每次使用前请用 `scripts/probe_channels.py` 复核，不要把本表当永久事实。

## 0. 环境与依赖

| 项 | 值 |
|----|----|
| API host | `https://www.workbuddy.cn`（环境变量 `WB_SPACE_HOST` 可覆盖） |
| 页面分享域 | `*.workbuddy.link/p/<pageId>`（**与 API host 跨域**，不要照抄页面域） |
| 内置 skill 库 | `<宿主安装目录>/resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/library/` |
| IPC 入口 | `import workbuddy_ipc; workbuddy_ipc.http_request("POST", url, body={...})` |
| Python | 3.14+（禁 `from __future__ import annotations`） |

**库路径自动定位**（`probe_channels.py` 的 `find_library_root()`）依次尝试：
1. `WORKBUDDY_SKILLS_ROOT` 环境变量
2. `WORKBUDDY_APP_DIR` 环境变量 + `/resources/app.asar.unpacked/...`
3. 从脚本自身路径向上回溯各级父目录
4. `~/.workbuddy/plugins/cache/workbuddy-builtin/*/skills`
5. 扫描 `D:/`、`C:/` 下 `<Vendor>/Install/<App>/` 结构

> Windows 盘根存在无权限目录（如 `System Volume Information`），遍历时必须捕获 `PermissionError`。

## 1. 端点清单

| 用途 | 路径 | 必带参数 | 实测返回 |
|------|------|---------|---------|
| 读 schema | `POST /space/api/page/share/database/get` | `databaseId`（`pageId` 可选） | `{code:0, data:{title, properties:[...]}}` |
| 读 schema（登录态兜底） | `POST /space/api/view/database/get` | `databaseId`, `pageId` | 同上 |
| 读当前用户 | `POST /space/api/view/user/current` | 无 | `{code:0, data:{userInfo:{nickName,id,name,avatar,accountType}}}` |
| 新增记录 | `POST /space/api/view/database/addRecord` | `databaseId`, `pageId`, `properties` | `{code:0, data:{id}}` |
| 更新记录 | `POST /space/api/view/database/updateRecord` | `databaseId`, `pageId`, `recordId`, `properties` | `{code:0, data:{id}}` |
| 回读记录 | `POST /space/api/view/database/getRecord` | `databaseId`, `pageId`, `recordId` | `{code:0, data:{result:{...}}}` |
| 查记录 | `POST /space/api/view/database/query` | `databaseId`, `pageId` | `{code:0, data:{results:[...], nextCursor, hasMore}}` |
| 删除记录 | `POST /space/api/view/database/deleteRecord` | `recordId`（实测 `pageId` 非必需） | `{code:0}` |
| 上传图片 | `POST /space/api/view/upload/image` | `data`(去前缀 base64), `contentType`, `fileName`, `pageId` | `{code:0, data:{url,width,height,...}}` |

**不可用**：`POST /space/api/view/database/listRecords` → `INVALID_RESPONSE`（端点不存在）。

## 2. PropertyValue oneof 形状

```
text        → {"text": "..."}
number      → {"number": 3}
select      → {"select": "选项文本"}
multi_select→ {"multi_select": ["a","b"]}
date        → {"date": "2026-10-26"}
url         → {"url": {"text": "显示文本", "link": "https://..."}}
image       → {"image": {"images": [{"title": "...", "imageUrl": "https://...", "width": 1280, "height": 720}]}}
checkbox    → {"checkbox": true}
attachment  → {"attachment": [...]}
```

**裸字符串会失败**：`cannot unmarshal string into Go struct field AddRecordReq.properties`。

**图片项必须带 `title`**：缺失时页面侧 `^https://` 过滤会丢弃整组，且写入仍返回 `code=0`（静默丢失）。

**base64 必须去 `data:` 前缀**。

## 3. query 的 filter 形状（查重关键）

filter 是**递归树**，三种节点：

```jsonc
// 单字段条件
{"property": {"property": "字段名", "text": {"equals": "值"}}}
// AND
{"and": [filter1, filter2]}
// OR
{"or": [filter1, filter2]}
```

类型字段与操作符：

| 字段类型 | 条件字段 | 操作符 |
|---------|---------|--------|
| text / url / email / phone_number | `text` | `equals`、`contains` |
| number | `number` | `equals`、`greater_than`、`less_than`、`greater_than_or_equal`、`less_than_or_equal`、`is_empty` |
| select / multi_select | `select` | `equals`、`does_not_equal` |
| date | `date` | `equals`、`before`、`after` |
| checkbox | `checkbox` | `equals`、`does_not_equal` |

**实测样例（一次命中）**：

```json
{"databaseId": "P3Y1rSDQcUAZcGV15UjCND", "pageId": "8QYARuAmZ9RgQty3FSzNUs",
 "filter": {"property": {"property": "提交编号", "text": {"equals": "S1024-1a176238787-lros"}}}}
```

→ `results` 长度 1，`hasMore=false`。

**翻页参数**：SDK 契约为 `startCursor`；HTTP 端点实测响应回 `nextCursor`，再次请求时以 `nextCursor` 作为游标传入可续页。

### ⚠️ 翻页查重不可靠（静默失败）

- 该投稿池首页仅返回 **50 条**，`hasMore=true`，`nextCursor` 非空。
- 翻 10 页（累计 500 条）**仍未命中**已于当日写入的记录——记录按提交时间落位，不在首页。
- **结论：查重必须走服务端 `filter`；翻页遍历会给出"无重复"的假结论，且失败是静默的。**

## 4. 权限与错误码

| code / 错误 | 含义 | 处置 |
|-----------|------|------|
| `0` | 成功 | 注意：`code=0` ≠ 字段写对，仍须回读比对 |
| `12607 permission denied` | 缺 `pageId`（文案误导，实为缺上下文参数） | 补 `pageId` 重试 |
| `11607 empty filter: ...` | filter 子树缺失 | 给 `{property:{...}}` / `{and:[...]}` / `{or:[...]}` |
| `11607 property filter: property name is empty` | 叶子 `property` 键值不是字段名 | 叶子须为 `{"property":"字段名", <类型字段>:{...}}` |
| `11607 cannot unmarshal array into ... PropertyFilter` | `property` 传成数组 | 传单个对象 |
| `401 not login` | 用了 share 通道的写接口 | 写必须走 view 通道 |
| `E_BAD_REQUEST: path must be relative` | 直接 `pipe.invoke('http.fetch', {'url': 绝对URL})` | 改用 `workbuddy_ipc.http_request` |

## 5. 通道权限矩阵（实测）

| 通道前缀 | 读 schema | 读记录 | 写记录 |
|---------|----------|--------|--------|
| `/space/api/view/*` | ✅ | ✅ | ✅（需 `pageId`） |
| `/space/api/page/share/*` | ✅（无需登录态） | ⚠️ 部分 | ❌（无登录态时 401） |
| `/space/api/agent/v1/*` | ❌ 对主办方表 | ❌ | ❌ |
| 宿主 SDK `__SMART_PAGE__.database` | ✅（仅页面上下文内） | ✅ | ✅ |

## 6. 记录结构细节

- 记录主键字段名是 **`_id`**，不是 `id`。
- `query` 返回的每条记录形态与 `getRecord` 的 `data.result` 一致。
- URL / 附件类字段是数组：`{"url":[{"text":"...","link":"..."}]}`。
- 图片字段是数组：`{"image":[{"title":"...","imageUrl":"...","width":...,"height":...}]}`。

## 7. 失效自检清单

每次复用本表前，依次确认：

1. `python scripts/probe_channels.py --page-id <pid> --database-id <dbid>` 退出码为 0（依赖可定位、通道可达）。
2. schema 能读出，且字段名与目标表一致（表结构可能已被主办方调整）。
3. `filter` 查重能返回预期条数（用一条已知存在的记录验证查重本身有效）。
4. 目标表 title 仍属收集/待审核类（若已改为「已发布」则判定转 RISK）。
