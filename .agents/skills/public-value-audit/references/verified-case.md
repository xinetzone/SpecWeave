# 实证案例：微信小程序「结伴之旅」主图路径泄露

> 本 Skill 的来源案例。会话 `sc-20261026-jieban-zhilv-milestone`，两轮对抗审查共 27 条发现。
> 下面只保留与本方法直接相关的证据链，完整复盘见
> `docs/retrospective/reports/2026-10-26-jieban-zhilv-mp-miniprogram-milestone-retro.md`。

## 1. 背景

项目：微信小程序「结伴之旅」（活动报名），云端用 PostgREST + PostgreSQL + RLS + 私有对象存储。
数据模型两张表：`activities`（活动）、`registrations`（报名记录）。

活动主图要放在对象存储，客户端按 `activities.cover_path` 签发 URL 取图。

## 2. 缺陷一：表级授权让访客直查创建者标识（P1-14）

**现象**：`activities.owner_id` 存的是微信 uid（形态 `wx:<openid>`）。
客户端字段白名单里**没有** `owner_id`，但服务端给的是**表级** `GRANT SELECT`：

```sql
GRANT SELECT ON TABLE public.activities TO anon, authenticated;
```

**实测**（匿名会话，只带公开 publishableKey）：

```
GET /.cloud/database/rest/activities?select=owner_id&limit=1
→ 200  [{"owner_id":"wx:..."}]
```

**根因**：安全边界被放在了客户端层。访客不必用客户端，直接打数据面 REST 即可。

**收口**：

```sql
REVOKE ALL ON TABLE public.activities FROM anon, authenticated;
REVOKE SELECT ON TABLE public.activities FROM anon, authenticated;
GRANT SELECT (id, slug, title, summary, cover_path, location, starts_at, ends_at,
               capacity, price_note, highlights, notes, published)
  ON TABLE public.activities TO anon, authenticated;
```

**关键实测（反直觉点）**：`owner_id` 不在列级授权里，但 RLS 策略
`USING (published = TRUE OR owner_id = auth.uid())` 仍在用它——
**RLS 策略以表属主权限求值，不受调用角色的列级权限约束**。
探针验证（`published=false` + `owner_id='wx:TESTUSER'`）：

```
seen_by_owner=1  seen_by_other=0  anon_total=3  auth_total=4
```

⇒ 「收回 owner_id 的列授权」与「RLS 用 owner_id 判归属」**可以共存**。

**另一个实测（破坏面）**：列级授权下，请求未授权列会让**整表**失败：

```
GET …/activities?select=id,owner_id&limit=1  → 401 DATABASE_42501
GET …/activities?select=*&limit=1             → 401 DATABASE_42501
```

⇒ 客户端白名单必须与服务端授权清单**逐列对齐**，并加双向断言防漂移。

## 3. 缺陷二：列挡住了，值又从另一列漏出去（P1-15，本 Skill 的核心来源）

**现象**：整改完缺陷一后自查发现——`activities.cover_path` 的值里嵌着 owner uid：

```
cover_path = shared/2114562052432330752/activities/dawn-trek.png
             └────────── 就是 activities.owner_id ──────────┘
```

而 `cover_path` 是在**公开可读**的业务列里（客户端要用它签发图片地址）：

```
GET /.cloud/database/rest/activities?select=id,slug,title,cover_path&limit=2
→ 200  [{"cover_path":"shared/2114562052432330752/activities/dawn-trek.png", …}]
```

**为什么之前没发现**：缺陷一的整改只盯着 `owner_id` 这一列，
没有追问「**同一个标识是不是还从别处漏出去**」。
⇒ 同一张表两列可见性不一致，等于自己打自己。

**根因是建模错误**：活动主图是**应用资产**，却被放进了「终端用户归属」作用域
`shared/<uid>/activities/`。作用域模型决定了路径第 2 段必然是归属标识，于是必然带 uid。

**收口（从取值域根除，不是堵入口）**：

```sql
-- ① canonical 通道：目标路径由服务端拼出，调用方不传路径
CREATE OR REPLACE FUNCTION public.sync_activity_cover(p_slug TEXT)
RETURNS TEXT LANGUAGE plpgsql SECURITY DEFINER SET search_path TO 'public' AS $$
DECLARE
  v_path TEXT;
BEGIN
  IF p_slug IS NULL OR p_slug !~ '^[a-z0-9-]{1,64}$' THEN
    RAISE EXCEPTION '活动参数无效' USING ERRCODE = '22023';
  END IF;
  v_path := 'shared/_application/activities/' || p_slug || '.png';
  -- 目标对象必须已存在，否则不绑定（避免客户端拿到「能签发但 404」的地址）
  IF NOT EXISTS (SELECT 1 FROM storage.objects o
                 WHERE o.bucket_id = 'runtime' AND o.name = v_path
                   AND o.owner_id LIKE 'wbapp:%') THEN
    RAISE EXCEPTION '主图尚未上传到应用共享空间' USING ERRCODE = '22023';
  END IF;
  UPDATE public.activities SET cover_path = v_path WHERE slug = p_slug;
  RETURN v_path;
END;
$$;

-- ② 旧通道显式废止：它是唯一能写入含 uid 路径的入口
REVOKE ALL ON FUNCTION public.claim_activity_cover(TEXT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.claim_activity_cover(TEXT, TEXT) FROM anon, authenticated, service_role;
DROP FUNCTION IF EXISTS public.claim_activity_cover(TEXT, TEXT);
```

**配套（堵住同族漏点）**：`set_activity_cover` 原先 `RETURNS SETOF public.activities`，
响应体带 `owner_id`——一旦被误授权给 `authenticated`，就会绕开列级授权。
改为 `RETURNS TEXT`，让这个坑在结构上消失。

**为什么 `_application` 作用域是对的**：它是平台定义的应用归属作用域，
属主是应用身份 `wbapp:<applicationId>`，而 `applicationId` 本就硬编码在客户端
`publishableKey` 里 → **路径不含任何新增信息**。

**迁移成本**：字节上传需走 WorkBuddy 管理页（`shared/_application/` 仅管理员可写，
实测端用户会话四种写法全 `403 STORAGE_ACCESS_DENIED`）。
迁移按「先传字节 → 再切路径 → 再删旧对象」排序，**中间态不影响可用性**。

## 4. 反模式实例（本 Skill §6 的来源）

| 反模式 | 本案实例 |
|---|---|
| 只把列从客户端拿掉 | 缺陷一：客户端白名单去掉 `owner_id`，但表级授权让访客直查 |
| 只挡列、不挡值 | 缺陷二：列级授权挡住 `owner_id`，`cover_path` 又把它发出去 |
| RPC 返回整行 | `set_activity_cover` 返回 `SETOF activities`（含 `owner_id`） |
| 收紧权限只看「能不能」 | 把 `claim_activity` 收归 `service_role` 后其函数体依赖 `auth.uid()` → 运维链路当场断裂 |
| 值域由入参决定 | `claim_activity_cover(p_slug, p_path)` 把路径交给调用方决定 |

## 5. 修复前后对照

| 项 | 整改前 | 整改后 |
|---|---|---|
| `activities` 对外授权 | 表级 SELECT（15 列全给） | 列级 SELECT（13 列，无 `owner_id`/`created_at`） |
| 主图路径取值域 | `shared/<uid>/activities/<slug>.png`（含 uid） | `shared/_application/activities/<slug>.png`（无标识） |
| 主图绑定通道 | `claim_activity_cover(slug, path)`，入参决定路径 | `sync_activity_cover(slug)`，服务端拼装；旧通道 DROP |
| 管理侧绑定函数返回值 | `SETOF activities`（带 `owner_id`） | `TEXT` |
| 断言器判定 | FAIL 3 · WARN 4 | **FAIL 0**（WARN 逐条确认后登记豁免） |

## 6. 本案沉淀的额外经验

- **别把「值看起来不敏感」当放行理由**：本案的 uid 是数字串，但它仍是用户标识，
  且归属人一旦换成微信用户就会变成 `wx:<openid>` 形态——风险是**潜在的**而非当前的。
- **先修授权面，再问「同一个值还从哪儿漏」**：整改一处泄露后必须重跑全量扫描，
  否则会带着「自己打的自己」进入下一个里程碑。
- **把结论写成断言**：本 Skill 的 `check_public_value_invariants.py` 之所以能守住，
  是因为结论被固化成了 6 条可回归的不变量，而不是留在某次对话里。

## 7. 工具自身的能力边界（v1.1.0 对抗审查后的诚实交代）

4 视角对抗审查（50 条意见）对本 Skill 的工具做了实测攻击，发现并修复了若干**真实缺陷**，
也暴露了**仍然存在的能力边界**。如实记录：

### 已修复的真实缺陷

| 缺陷 | 后果 | 修复 |
|---|---|---|
| 表名不归一化（SQL 写 `public.activities`、客户端写 `activities`） | 「客户端请求列 ⊆ 服务端授权」这条不变量**恒不触发** | 表名双向归一化 |
| 列名解析用 `strip("()")` | 前导空格导致首个列名变成 `(id` → 同上不变量恒不触发 | 改用标识符正则提取 |
| RLS `USING (...)` 用非贪婪捕获 | `auth.uid()` 的右括号被吃掉 → 行隔离检测恒为 0 → 本该豁免的全被报高危 | 改贪婪捕获 |
| H6 只认 `SET col = p_x` 字面形态 | 「中间变量中转」与 `INSERT` 形态全漏——**本 Skill 开的处方自己检不出** | 加 4 轮污点传播 + INSERT 支持 |
| 函数体只认 `$$` 分隔符 | 本项目 7 个 `fn_*.sql` 里 4 个用 `$fn$` → 同一函数两个文件两个结论 | 支持任意 dollar-quote 标签 |
| 扫描器无 `--allow-row-isolated` | 规则说「本人私有目录不是泄露面」，脚本却判高危 → 用户被逼去改正确的代码 | 两脚本对称支持豁免 |
| 零覆盖报「全绿」 | 空目录输出 6 条 ✅、退出码 0 → 「没扫到」被当成「没问题」 | 覆盖率输出 + 空目录退出码 3 |
| 原 pre-fix 夹具复现的是 P1-14 | 夹具证明了能检出 P1-14，却与 Skill 名字指向的 P1-15 无关 | 补 `p115-only` 夹具并纳入自检 |

### 仍然存在的能力边界

- **不检查实际数据值**：脚本做的是源码形状分析。「公开值里到底有没有标识」
  仍需取真实值人工核对（SKILL.md §8 检验标准 1~3 全部是手工步骤）。
- **不解析角色组间接授予**（`GRANT <role> TO anon`）：静态不可判定，报中危。
- **不解析 `.ts` / `.js` 内嵌的 SQL 模板**：给出显式告警但不逐条解析。
- **H3 依赖 PostgREST 语义**（`?select=` 白名单列）：非 PostgREST 后端需人工确认，
  故 H3 已从高危降为中危。
- **收口三件套的第三件（客户端白名单对齐）只覆盖「请求列 ⊆ 授权列」**，
  不覆盖「授权列 ⊆ 业务需要列」这一反向最小化。

### 一次被否掉的「看起来很对」的结论

审查意见指出：Skill 一边把「哈希脱敏」列为合法收口手法，一边在案例的洞察里
拿「别用哈希」当错误直觉来反驳——**立了个域外的靶子**。
已改为：I-002 的论证只保留「路径型归属段在用户作用域下必然携带标识 →
应用资产必须换作用域」，删除与脱敏的优劣比较。
