# 通道故障排查矩阵

> 按「症状 → 真实原因 → 处置」组织。用于 §11 快速定位与 §12 Gotchas 的展开依据。
> 全部条目来自 sc-20261026-workbuddy-contest-submit 实测，非推测。

## 通道能力总表

| 通道 | 前缀 | 带登录态 | 读 schema | 读记录 | 写记录 | 备注 |
|------|------|:---:|:---:|:---:|:---:|------|
| view | `/space/api/view/*` | ✅ | 需 pageId | 需 pageId | 需 pageId | **本次成功通道** |
| share | `/space/api/page/share/*` | ❌ | ✅ 可读 | ❌ | ❌ | 只用于读 schema |
| agent-gateway | `/space/api/agent/v1/*` | ✅ | 对第三方表无权 | 无权 | 无权 | `space_api.py` 走这条 |
| 宿主 SDK | `sp.database.*` | ✅ | ✅ | ✅ | ✅ | 仅页面上下文内可用 |

## 症状索引

| 症状 | 真实原因 | 处置 |
|------|---------|------|
| `code=12607; msg=spaceengine/database: permission denied` | 缺 `pageId`（最常见）；或走了无权通道 | ①补 `pageId` 重试 ②换通道（view→SDK→agent-gateway→share） |
| `code=12607; msg=spaceengine: permission denied` | agent-gateway 访问页面节点 | 改走 view 通道 |
| `401 not login` | 用了 share 通道的写接口 | share 无登录态，写必须走 view |
| `json: cannot unmarshal string into Go struct field AddRecordReq.properties of type database.PropertyValue` | properties 值传裸字符串 | 按 oneof 形状重写 |
| `E_BAD_REQUEST: path must be relative and start with /` | 直接 `pipe.invoke('http.fetch', {'url': 绝对URL})` | 改用 `workbuddy_ipc.http_request` |
| `INVALID_PARAMS; msg=stdin JSON must be an object` | CLI 批量接口要对象 | 传对象或走 HTTP 直调 |
| `INVALID_RESPONSE` | 端点不存在（如 `listRecords`） | 用 `query` 代替 |
| 写入 `code=0`，回读 `作品截图` 为空 | 图片项缺 `title`，被页面侧 `^https://` 过滤整组丢弃 | 每项补 `title` |
| 上传接口返回 url 但记录里没有 | base64 带 `data:` 前缀 | 去前缀重传 |
| `PermissionError` / `Device or resource busy` / `CreateFileW err 32` | Electron Cookies 被宿主进程独占 | 放弃 cookie 路线，改走 IPC 管道 |
| `resolve_cli.sh` 报平台不匹配；`.ps1` 被执行策略拦截 | Windows 缺屏幕自动化小助手 | UI 自动化降为最后手段 |

## 排查顺序（实战验证有效）

1. **读 schema**（`share` 通道 `database/get`）——确认表结构与字段名，别猜
2. **读登录态**（`view` 通道 `user/current`）——确认账号与 UserID 类字段取值
3. **试写探针**（`view` 通道 `addRecord` 带 `pageId`）——确认写权限，验证后立即删
4. **正式写入** → **回读复核**（`view` 通道 `getRecord` 带 `pageId`）
5. 任一步失败 → 换下一条通道，回到步骤 1

> **第 3 步为什么用探针而非正式记录？** 探针一次性区分「通道不通」与「字段形状不对」两类失败模式。用正式记录做探针会把脏数据留进审核池。

## 已验证的端点清单

```
POST /space/api/page/share/database/get
    body: {"databaseId": "<id>", "pageId": "<pageId>"}
    → {"code":0,"data":{"id":...,"title":...,"properties":[...]}}   # schema

POST /space/api/view/user/current
    → {"code":0,"userInfo":{"nickName":...,"id":...}}

POST /space/api/view/upload/image
    body: {"data":"<去前缀base64>","contentType":"image/png","fileName":"x.png","pageId":"<pageId>"}
    → {"code":0,"data":{"url":"https://...","width":1280,"height":720}}

POST /space/api/view/database/addRecord
    body: {"databaseId":"<id>","pageId":"<pageId>","properties":{...oneof...}}
    → {"code":0,"data":{"id":"<recordId>"}}

POST /space/api/view/database/getRecord
    body: {"databaseId":"<id>","recordId":"<rid>","pageId":"<pageId>"}
    → {"code":0,"data":{"result":{...}}}

POST /space/api/view/database/query
    body: {"databaseId":"<id>","pageId":"<pageId>"}
    → {"code":0,"data":{"results":[...]}}

POST /space/api/view/database/deleteRecord
    body: {"recordId":"<rid>"}
    → {"code":0,"data":{}}
```

## 实战案例指针

完整案例见 `references/verified-case.md`——含 18 字段的 oneof 组装、两次写入与逐字段回读结果。
