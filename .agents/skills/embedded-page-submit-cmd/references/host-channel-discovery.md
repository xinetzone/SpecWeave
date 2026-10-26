# 宿主通道重新发现协议（详细版）

> 配套 `../SKILL.md` §7.0。**先做这一步，再谈逆向。**
>
> **为什么放在最前面**：本次实战中"通道不存在"的错误结论，是在**只试了一条通道**的前提下写下的。若先做一次完整的通道重发现，旧结论就会被推翻。

## 步骤 1｜定位宿主安装目录（不要写死路径）

```bash
# 找 app.asar.unpacked 所在位置（Windows 常见 D:/<Vendor>/Install/<App>/）
ls -d "D:/"*/Install/*/resources/app.asar.unpacked 2>/dev/null
# 用户级插件缓存（CLI/Agent 场景的 skill 库）
ls -d ~/.workbuddy/plugins/cache/workbuddy-builtin/*/skills 2>/dev/null
```

`probe_channels.py` 的 `find_library_root()` 已把这套逻辑自动化（环境变量 → 父目录回溯 → 用户级缓存 → 盘根扫描），并对无权限目录做 `PermissionError` 兜底（Windows 盘根有 `System Volume Information`）。

## 步骤 2｜解包 / 检索 asar

```bash
# 若已装 asar 工具：npx asar extract app.asar ./asar-extract
# 未安装时的只读替代：直接用 grep 在二进制里搜关键字（asar 未压缩时可读）
grep -a -o -m 20 "/space/api/view/database/[a-zA-Z]*" app.asar | sort -u
```

> **asar 的关键性质**：`app.asar` 是一个可随机访问的归档，**未压缩**。因此 `grep -a` 直接在二进制上搜字符串是可行且最快的路径；只有需要读完整 JS 时才值得解包。

## 步骤 3｜chunk 权威性裁决规则

asar 内通常有多个 chunk 都含同一段路径映射。裁决顺序：

1. **运行时代码优先**：`main` / `renderer` / `preload` 段 > 静态资源段；
2. **时间戳新者优先**（文件 mtime 大的更可能是当前线上版本）；
3. **命中次数多者未必更权威**（可能是旧版残留）——若两个 chunk 给出不同 baseUrl，**两个都试**，用返回值裁决。

## 步骤 4｜baseUrl 穷举规则

若映射写成 `post("xxx", "/database/yyy")` 这类相对路径，说明 baseUrl 由调用方注入，**必须穷举候选前缀**，每个都实测：

| 候选前缀 | 实测角色 |
|---------|---------|
| `/space/api/view` | 页面访问者身份，读写可（本次成功通道） |
| `/space/api/page/share` | 分享链接身份，通常只读 |
| `/space/api/agent/v1` | agent-gateway，对主办方表常无权 |
| `/space/api/page` | 页面通用面，需实测 |

## 步骤 5｜host 不得写死

本次页面域是 `www.workbuddy.link`（分享链接域），而 API host 是 `www.workbuddy.cn`（平台域），**两者跨域**。API host 的正确来源：

- 从 chunk 里 grep 出的 baseURL 常量；
- 或页面 HTML 里的 `<meta>` / `window.__CONFIG__`；
- **不要**把「页面 URL 的域」当成 API host。

用环境变量承载：`WB_SPACE_HOST=https://www.workbuddy.cn`。

## 步骤 6｜跑只读探针确认

```bash
python scripts/probe_channels.py --page-id <pageId> --database-id <dbId>
```

输出：通道可达性矩阵 + 登录态 + 目标表 schema + 目标表身份判定。**这一步是只读的，绝不写库。**

## 页面 HTML 来源交代

本次页面 HTML 是宿主 webview 加载后的产物，落地为 `.contest-page.html`（约 210 KB）。来源三选一，按可靠度排序：

1. 宿主 webview 的 devtools 另存（最全，含运行时注入的 `window.__CONFIG__`）；
2. `workbuddy_ipc` 发的 GET 请求响应体（带登录态，但可能只拿到 SPA 壳）；
3. 公开分享链接的匿名 GET（最弱，静态资源与配置可能不全）。

**无论哪条来源，取完必须落盘并记录字节数**，避免后续"这个 HTML 从哪来的"变成新的记忆负担。

## 逆向入口定位法（实操顺序）

1. 从页面 HTML 找 SDK 方法名 → 拿到 `addRecord` / `uploadImage` 等；
2. 在宿主 asar 里正则搜这些字符串，定位映射表所在 chunk（按步骤 3 裁决权威性）；
3. 在 chunk 里找 `post("xxx", "/database/yyy", n)` 这类调用，取出后端路径与前缀（按步骤 4 穷举 baseUrl）；
4. 前缀有多个（`/space/api/view` 与 `/space/api/page/share`）时**分别试**，权限不同。

## 参考

宿主 SDK 契约文档（随宿主安装分发，只读）：

```
<宿主安装目录>/resources/app.asar.unpacked/resources/plugins/workbuddy-builtin/skills/library/page/database-sdk-contract.md
```

其中 §2 列出方法集、§3 给出 PropertyValue oneof 全表、§4 给出 query 的 filter/sorts 精确形状、§4.5 给出 aggregate。**逆向遇到形状问题时先读这份契约，比猜快得多。**
