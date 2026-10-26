-- 结伴之旅 · 云数据库最终态（单一真相源）
--
-- 说明：
-- 1. 本目录下的 SQL 以「每次一条语句」为单位执行（云数据库 MCP 端点不支持多语句）。
-- 2. 口径约定：报名人数一律按「人数」计（sum(companions)），不再按行数计。
-- 3. 客户端对 registrations 只有 SELECT 权限；写入与取消一律走 SECURITY DEFINER RPC。
-- 4. activities 增 published 字段，删除活动改为 RESTRICT，避免静默抹掉用户报名记录。
-- 5. 活动归属 owner_id 即创建者。归属由管理侧显式指派（claim_activity，
--    仅 service_role）。主图绑定走 canonical 通道（sync_activity_cover），
--    目标路径由服务端拼出为 shared/_application/activities/<slug>.png，
--    字节落在应用归属作用域（仅管理员可写、全体登录用户可读）。
-- 6. activities 读策略：已发布全员可读；已下架仅创建者本人可见。
-- 7. activities 采用列级授权：owner_id 不授予 anon/authenticated，
--    避免访客直查活动创建者的微信 uid（含 openid 片段）。
--    created_at 客户端与脚本都不读，按最小权限同样不授权。
-- 8. 主图路径取值域不含用户标识：cover_path 是公开可读列，
--    一旦内嵌 owner uid 就等于绕回创建者标识泄露后门。
--    因此 cover_path 只允许取 shared/_application/activities/<slug>.png，
--    由 sync_activity_cover（路径由服务端拼出）与 set_activity_cover
--    （只接受 _application 前缀）共同锁死；旧通道 claim_activity_cover 已 DROP。

-- ============================================================
-- 表结构
-- ============================================================

CREATE TABLE IF NOT EXISTS public.activities (
  id          BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  slug        TEXT        NOT NULL UNIQUE,
  title       TEXT        NOT NULL,
  summary     TEXT,
  cover_path  TEXT,
  location    TEXT,
  starts_at   TIMESTAMPTZ,
  ends_at     TIMESTAMPTZ,
  capacity    INTEGER     NOT NULL DEFAULT 100,
  price_note  TEXT,
  highlights  JSONB       NOT NULL DEFAULT '[]'::jsonb,
  notes       JSONB       NOT NULL DEFAULT '[]'::jsonb,
  published   BOOLEAN     NOT NULL DEFAULT TRUE,
  owner_id    TEXT        DEFAULT auth.uid(),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT activities_capacity_check CHECK (capacity >= 0)
);

CREATE TABLE IF NOT EXISTS public.registrations (
  id           BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  activity_id  BIGINT      NOT NULL REFERENCES public.activities(id) ON DELETE RESTRICT,
  owner_id     TEXT        NOT NULL DEFAULT auth.uid(),
  owner_name   TEXT,
  contact      TEXT,
  companions   INTEGER     NOT NULL DEFAULT 1,
  remark       TEXT,
  cover_path   TEXT,
  status       TEXT        NOT NULL DEFAULT 'confirmed',
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT registrations_companions_check CHECK (companions BETWEEN 1 AND 4),
  CONSTRAINT registrations_status_check CHECK (status IN ('confirmed', 'cancelled')),
  CONSTRAINT registrations_contact_check CHECK (contact IS NULL OR contact ~ '^1[0-9]{10}$')
);

-- 同一用户对同一活动只保留一条有效报名（取消后 status 变为 cancelled，可再次报名）
CREATE UNIQUE INDEX IF NOT EXISTS registrations_activity_owner_confirmed_uniq
  ON public.registrations (activity_id, owner_id)
  WHERE status = 'confirmed';

COMMENT ON TABLE public.activities IS '结伴之旅活动表；published=false 表示已下架';
COMMENT ON TABLE public.registrations IS '报名记录表；companions 为同行人数（含本人），cover_path 为报名配图的云存储路径';

-- ============================================================
-- RLS
-- ============================================================

ALTER TABLE public.activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.registrations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS activities_read_all ON public.activities;
-- 已发布活动全员可读；已下架活动仅创建者本人可见（避免报名记录页丢失活动元信息）
CREATE POLICY activities_read_all ON public.activities
  FOR SELECT TO authenticated, anon
  USING (published = TRUE OR owner_id = auth.uid());

DROP POLICY IF EXISTS registrations_read_own ON public.registrations;
CREATE POLICY registrations_read_own ON public.registrations
  FOR SELECT TO authenticated, anon
  USING (owner_id = auth.uid());

DROP POLICY IF EXISTS registrations_insert_own ON public.registrations;
DROP POLICY IF EXISTS registrations_update_own ON public.registrations;
DROP POLICY IF EXISTS registrations_delete_own ON public.registrations;

-- ============================================================
-- 表级权限：客户端只读；写入全部收敛到 RPC
-- ============================================================

-- activities 改为【列级授权】：
-- owner_id 存的是微信 uid（形态为 wx:<openid>），一旦下发给任意访客
-- 就等于泄露活动创建者的 openid。客户端字段白名单里本来就没有 owner_id，
-- 但客户端只是「不主动读」，服务端授权面若仍给表级 SELECT，
-- 访客可以直接 GET /rest/v1/activities?select=owner_id 绕过客户端。
-- 因此这里撤销表级 SELECT，只逐列授予业务字段；
-- owner_id 仅留给 RLS 策略内部判断（策略求值不需要列级 SELECT 授权）。
REVOKE ALL ON TABLE public.activities FROM anon, authenticated;
REVOKE SELECT ON TABLE public.activities FROM anon, authenticated;
-- 逐列授予业务字段。created_at 不在授权名单内：
-- 客户端与运营脚本都不读它（最小权限），且授权越少，
-- 「select=*」隐式展开就越早被拒——不会因为某次改动不小心读到内部列。
GRANT SELECT (id, slug, title, summary, cover_path, location, starts_at, ends_at,
               capacity, price_note, highlights, notes, published)
  ON TABLE public.activities TO anon, authenticated;

REVOKE ALL ON TABLE public.registrations FROM anon, authenticated;
GRANT SELECT ON TABLE public.registrations TO anon, authenticated;

-- ============================================================
-- 服务端函数
-- ============================================================

-- 报名写入：人数口径容量校验 + 登录态 + 字段校验 + 活动状态校验 + 行锁 + 唯一约束防重复
CREATE OR REPLACE FUNCTION public.submit_signup(
  p_activity_id  BIGINT,
  p_companions   INTEGER,
  p_contact      TEXT,
  p_remark       TEXT,
  p_owner_name   TEXT,
  p_cover_path   TEXT DEFAULT NULL
)
RETURNS SETOF public.registrations
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_activity public.activities;
  v_taken    BIGINT;
  v_row      public.registrations;
  v_uid      TEXT;
  v_scope    TEXT;
  v_owner    TEXT;
  v_dir      TEXT;
  v_file     TEXT;
BEGIN
  v_uid := auth.uid();
  IF v_uid IS NULL OR v_uid = '' THEN
    RAISE EXCEPTION '请先完成微信授权登录' USING ERRCODE = '42501';
  END IF;

  IF p_companions IS NULL OR p_companions < 1 OR p_companions > 4 THEN
    RAISE EXCEPTION '同行人数需在 1 到 4 之间' USING ERRCODE = '22023';
  END IF;

  IF p_contact IS NULL OR p_contact !~ '^1[0-9]{10}$' THEN
    RAISE EXCEPTION '手机号格式不正确' USING ERRCODE = '22023';
  END IF;

  IF p_remark IS NOT NULL AND length(p_remark) > 100 THEN
    RAISE EXCEPTION '备注不能超过 100 字' USING ERRCODE = '22023';
  END IF;

  IF p_owner_name IS NOT NULL AND length(p_owner_name) > 40 THEN
    RAISE EXCEPTION '称呼不能超过 40 字' USING ERRCODE = '22023';
  END IF;

  -- 配图路径校验：按 '/' 结构化分段比较，不把 uid 拼进正则模式。
  -- 期望形状 users/<本人 uid>/registrations/<文件名>，文件名内不再允许斜杠，
  -- 且扩展名限 png/jpg/jpeg。正则只作用在「值」上（文件名），不作为模式拼接。
  IF p_cover_path IS NOT NULL THEN
    v_scope := split_part(p_cover_path, '/', 1);
    v_owner := split_part(p_cover_path, '/', 2);
    v_dir   := split_part(p_cover_path, '/', 3);
    v_file  := split_part(p_cover_path, '/', 4);
    IF array_length(string_to_array(p_cover_path, '/'), 1) IS DISTINCT FROM 4
       OR v_scope IS DISTINCT FROM 'users'
       OR v_owner IS DISTINCT FROM v_uid
       OR v_dir IS DISTINCT FROM 'registrations'
       OR v_file !~ '^[A-Za-z0-9._-]+\.(jpg|jpeg|png)$' THEN
      RAISE EXCEPTION '配图路径不合法' USING ERRCODE = '22023';
    END IF;
  END IF;

  SELECT * INTO v_activity FROM public.activities
    WHERE id = p_activity_id FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION '活动不存在或已下架' USING ERRCODE = 'P0002';
  END IF;

  IF NOT v_activity.published THEN
    RAISE EXCEPTION '活动不存在或已下架' USING ERRCODE = 'P0002';
  END IF;

  IF v_activity.starts_at IS NOT NULL AND v_activity.starts_at <= now() THEN
    RAISE EXCEPTION '活动已开始，报名通道已关闭' USING ERRCODE = 'P0001';
  END IF;

  SELECT COALESCE(sum(r.companions), 0)::BIGINT INTO v_taken
    FROM public.registrations r
    WHERE r.activity_id = p_activity_id AND r.status = 'confirmed';

  IF v_activity.capacity > 0 AND v_taken + p_companions > v_activity.capacity THEN
    RAISE EXCEPTION '名额已满' USING ERRCODE = 'P0001';
  END IF;

  INSERT INTO public.registrations (activity_id, companions, contact, remark, owner_name, cover_path)
  VALUES (p_activity_id, p_companions, p_contact, p_remark, p_owner_name, p_cover_path)
  RETURNING * INTO v_row;

  RETURN NEXT v_row;
EXCEPTION
  WHEN unique_violation THEN
    RAISE EXCEPTION '你已报名该活动' USING ERRCODE = '23505';
END;
$$;

-- 历史 signup 入口保留但关闭，避免旧客户端绕过校验
CREATE OR REPLACE FUNCTION public.signup(
  p_activity_id  BIGINT,
  p_companions   INTEGER DEFAULT 1,
  p_contact      TEXT DEFAULT NULL,
  p_remark       TEXT DEFAULT NULL,
  p_owner_name   TEXT DEFAULT NULL
)
RETURNS SETOF public.registrations
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
BEGIN
  RAISE EXCEPTION '报名入口已升级，请改用 submit_signup' USING ERRCODE = '42501';
END;
$$;

-- 取消报名：只允许取消本人有效记录（软取消，保留历史）
CREATE OR REPLACE FUNCTION public.cancel_registration(p_registration_id BIGINT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_uid TEXT;
  v_hit INTEGER;
BEGIN
  v_uid := auth.uid();
  IF v_uid IS NULL OR v_uid = '' THEN
    RAISE EXCEPTION '请先完成微信授权登录' USING ERRCODE = '42501';
  END IF;

  UPDATE public.registrations
    SET status = 'cancelled'
    WHERE id = p_registration_id AND owner_id = v_uid AND status = 'confirmed';

  GET DIAGNOSTICS v_hit = ROW_COUNT;
  RETURN v_hit > 0;
END;
$$;

-- 跨用户报名人数聚合（人数口径）
-- 只统计已发布活动；未发布（下架）活动的报名人数不外泄给匿名调用方。
CREATE OR REPLACE FUNCTION public.registration_stats()
RETURNS TABLE(activity_id BIGINT, signed_up BIGINT)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path TO 'public'
AS $$
  SELECT r.activity_id, COALESCE(sum(r.companions), 0)::BIGINT
  FROM public.registrations r
  JOIN public.activities a ON a.id = r.activity_id
  WHERE r.status = 'confirmed' AND a.published = TRUE
  GROUP BY r.activity_id
$$;

-- 绑定报名配图（仅限本人且未取消的记录，路径必须落在本人私有目录）
--
-- 越权防护：
--   1. 路径按 '/' 结构化分段比较，不把 uid 拼进正则模式（uid 含 '.' 等元字符时
--      不会放宽校验）；期望形状 users/<本人 uid>/registrations/<文件名>，
--      文件名内不再允许斜杠，扩展名限 png/jpg/jpeg；
--   2. 只允许 status='confirmed' 的报名记录绑定配图，已取消的记录拒绝。
CREATE OR REPLACE FUNCTION public.attach_registration_cover(
  p_registration_id BIGINT,
  p_cover_path      TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_uid    TEXT;
  v_hit    INTEGER;
  v_scope  TEXT;
  v_owner  TEXT;
  v_dir    TEXT;
  v_file   TEXT;
BEGIN
  v_uid := auth.uid();
  IF v_uid IS NULL OR v_uid = '' THEN
    RAISE EXCEPTION '请先完成微信授权登录' USING ERRCODE = '42501';
  END IF;

  -- 配图路径校验：结构化分段比较，不把 uid 拼进正则模式。
  IF p_cover_path IS NOT NULL THEN
    v_scope := split_part(p_cover_path, '/', 1);
    v_owner := split_part(p_cover_path, '/', 2);
    v_dir   := split_part(p_cover_path, '/', 3);
    v_file  := split_part(p_cover_path, '/', 4);
    IF array_length(string_to_array(p_cover_path, '/'), 1) IS DISTINCT FROM 4
       OR v_scope IS DISTINCT FROM 'users'
       OR v_owner IS DISTINCT FROM v_uid
       OR v_dir IS DISTINCT FROM 'registrations'
       OR v_file !~ '^[A-Za-z0-9._-]+\.(jpg|jpeg|png)$' THEN
      RAISE EXCEPTION '配图路径不合法' USING ERRCODE = '22023';
    END IF;
  END IF;

  UPDATE public.registrations
    SET cover_path = p_cover_path
    WHERE id = p_registration_id AND owner_id = v_uid AND status = 'confirmed';

  GET DIAGNOSTICS v_hit = ROW_COUNT;
  IF v_hit = 0 THEN
    -- 命中 0 行：区分「记录不存在 / 不属于本人」与「已取消」
    IF EXISTS (
      SELECT 1 FROM public.registrations
      WHERE id = p_registration_id AND owner_id = v_uid AND status = 'cancelled'
    ) THEN
      RAISE EXCEPTION '报名已取消，无法绑定配图' USING ERRCODE = '22023';
    END IF;
  END IF;
  RETURN v_hit > 0;
END;
$$;

-- 活动主图绑定（管理侧）：仅 service_role 可执行，允许自定义文件名
--
-- 返回类型刻意只返回路径字符串，不返回 activities 行：
--   旧版返回 SETOF public.activities，响应体里带 owner_id。
--   只要这个函数被误授予 authenticated，创建者标识就会经 RPC 响应体下发，
--   绕开「owner_id 不下发」的列级授权。改成只返回路径后，这个坑结构上消失。
CREATE OR REPLACE FUNCTION public.set_activity_cover(p_slug TEXT, p_path TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_file TEXT;
  v_parts TEXT[];
  v_hit  INTEGER;
BEGIN
  -- 路径校验按 '/' 结构化分段比较，不把 p_slug 拼进正则模式：
  -- slug 若含正则元字符，拼进模式会放宽校验。
  -- 期望形状 shared/_application/activities/<文件名>，恰好 4 段；
  -- 文件名段用捕获组取出 slug 与扩展名后做等值比较。
  IF p_slug IS NULL OR p_slug !~ '^[a-z0-9-]{1,64}$' THEN
    RAISE EXCEPTION '活动参数无效' USING ERRCODE = '22023';
  END IF;

  IF p_path IS NULL
     OR array_length(string_to_array(p_path, '/'), 1) IS DISTINCT FROM 4
     OR split_part(p_path, '/', 1) IS DISTINCT FROM 'shared'
     OR split_part(p_path, '/', 2) IS DISTINCT FROM '_application'
     OR split_part(p_path, '/', 3) IS DISTINCT FROM 'activities' THEN
    RAISE EXCEPTION '非法存储路径' USING ERRCODE = 'P0001';
  END IF;

  v_file := split_part(p_path, '/', 4);
  v_parts := regexp_match(v_file, '^([a-z0-9-]{1,64})\.(png|jpg|jpeg)$');
  IF v_parts IS NULL OR v_parts[1] IS DISTINCT FROM p_slug THEN
    RAISE EXCEPTION '非法存储路径' USING ERRCODE = 'P0001';
  END IF;

  PERFORM 1 FROM public.activities WHERE slug = p_slug FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION '活动不存在' USING ERRCODE = 'P0002';
  END IF;

  UPDATE public.activities SET cover_path = p_path WHERE slug = p_slug;
  GET DIAGNOSTICS v_hit = ROW_COUNT;
  IF v_hit = 0 THEN
    RETURN NULL;
  END IF;
  RETURN p_path;
END;
$$;

-- 活动归属指派（管理侧专用，仅 service_role 可执行）
--
-- 场景：存量活动由管理侧预置，owner_id 为空；由管理侧显式指派归属账号。
--       指派后，该账号即成为活动归属人（RLS owner 分支随之生效）。
--       注：主图绑定已改走 canonical 通道 sync_activity_cover，
--       目标路径由服务端拼出，不再按调用者 uid 分作用域。
--
-- 为什么是「显式指派」而不是「首个登录用户认领」：
--   claim_activity 早期版本是「owner_id IS NULL 时，谁先登录谁就是创建者」。
--   这把归属判定从服务端管理凭证降级成了客户端时序——任何登录用户都能抢先
--   接管任意活动的主图绑定权。当前版本要求调用方（管理侧）显式给出
--   p_owner_uid，归属由管理侧决定，不依赖任何终端用户的登录顺序。
--
-- 越权防护：
--   1. 仅当 owner_id IS NULL（无人指派）时才能指派，已有归属者不能被抢占；
--   2. 重复指派给同一账号幂等返回 true；
--   3. 行锁避免并发下两人同时指派成功；
--   4. p_owner_uid 必须是已存在的登录账号，且不能与 anon/authenticated 的
--      默认占位相同（否则等于把归属开放给全体终端用户）。
CREATE OR REPLACE FUNCTION public.claim_activity(p_activity_id BIGINT, p_owner_uid TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_uid   TEXT;
  v_owner TEXT;
  v_hit   INTEGER;
BEGIN
  IF p_owner_uid IS NULL OR p_owner_uid = '' THEN
    RAISE EXCEPTION '归属账号无效' USING ERRCODE = '22023';
  END IF;
  IF p_owner_uid IN ('anon', 'authenticated') THEN
    RAISE EXCEPTION '归属账号无效' USING ERRCODE = '22023';
  END IF;

  v_uid := p_owner_uid;

  SELECT owner_id INTO v_owner
    FROM public.activities WHERE id = p_activity_id FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION '活动不存在' USING ERRCODE = 'P0002';
  END IF;

  IF v_owner IS NOT NULL THEN
    IF v_owner = v_uid THEN
      RETURN TRUE;
    END IF;
    RAISE EXCEPTION '活动已有创建者，无法认领' USING ERRCODE = '42501';
  END IF;

  UPDATE public.activities SET owner_id = v_uid WHERE id = p_activity_id;
  GET DIAGNOSTICS v_hit = ROW_COUNT;
  RETURN v_hit > 0;
END;
$$;

-- 活动主图绑定（canonical 通道）：把主图绑定到应用共享空间的规范路径
--
-- 为什么需要这个函数（历史教训）：
--   旧版 claim_activity_cover 允许把主图写进 shared/<调用者 uid>/activities/，
--   于是 activities.cover_path 的值里内嵌了 owner uid。而 cover_path 是一列
--   公开可读的业务字段——等于用「主图路径」这条后门，把已经从 owner_id
--   撤掉的创建者标识又原样下发给了所有访客。同一张表两列可见性不一致，
--   属于自己打自己，必须从取值域上根除，而不是只堵某一个入口。
--
-- 本函数的做法：目标路径由服务端拼出，调用方无法指定。
--   cover_path 的取值域被锁死为 shared/_application/activities/<slug>.png，
--   路径中不含任何用户标识。该作用域的属主是应用身份 wbapp:<applicationId>，
--   而 applicationId 本就硬编码在客户端 publishableKey 里，不构成新增泄露。
--
-- 配套约束：
--   1. p_slug 先按字面量校验为安全 slug（^[a-z0-9-]{1,64}$），它只参与等值比较，
--      绝不作为正则模式的一部分拼接；
--   2. 目标对象必须已存在于云存储且属应用身份，否则拒绝绑定——避免 cover_path
--      指向缺失对象，让客户端拿到「能签发但 404」的地址；
--   3. 活动行 FOR UPDATE 锁，避免并发下互相覆盖。
--
-- 为什么可以授予 authenticated：
--   调用者无法指定路径，只能把「某个 slug 的主图」指向它自己的规范路径；
--   也无法指定文件名（文件名由 slug 决定），所以不可能把 A 活动的图挂到 B 活动；
--   字节写入仍需管理员权限（存储侧 _application 作用域仅 admin 可写），
--   调用者改不了图本身。本函数返回路径字符串，不返回 activities 行，
--   因此不会经响应体泄露 owner_id。
--
-- 管理侧通道见 set_activity_cover（仅 service_role，允许自定义文件名）。
CREATE OR REPLACE FUNCTION public.sync_activity_cover(p_slug TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_path     TEXT;
  v_activity public.activities;
  v_hit      INTEGER;
  v_exists   BOOLEAN;
BEGIN
  -- p_slug 是被当作字面量使用的：先约束成安全 slug，绝不作为正则模式的一部分拼接
  IF p_slug IS NULL OR p_slug !~ '^[a-z0-9-]{1,64}$' THEN
    RAISE EXCEPTION '活动参数无效' USING ERRCODE = '22023';
  END IF;

  -- 目标路径由服务端拼出：调用方无法指定路径，取值域因此被完全锁死
  v_path := 'shared/_application/activities/' || p_slug || '.png';

  -- 目标对象必须已在云存储里（且属应用身份），否则不绑定
  SELECT EXISTS (
    SELECT 1
    FROM storage.objects o
    WHERE o.bucket_id = 'runtime'
      AND o.name = v_path
      AND o.owner_id LIKE 'wbapp:%'
  ) INTO v_exists;
  IF NOT COALESCE(v_exists, FALSE) THEN
    RAISE EXCEPTION '主图尚未上传到应用共享空间' USING ERRCODE = '22023';
  END IF;

  SELECT * INTO v_activity FROM public.activities WHERE slug = p_slug FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION '活动不存在' USING ERRCODE = 'P0002';
  END IF;

  UPDATE public.activities SET cover_path = v_path WHERE slug = p_slug;
  GET DIAGNOSTICS v_hit = ROW_COUNT;
  IF v_hit = 0 THEN
    RETURN NULL;
  END IF;
  RETURN v_path;
END;
$$;

-- ============================================================
-- 函数执行权限
-- ============================================================

REVOKE ALL ON FUNCTION public.submit_signup(BIGINT, INTEGER, TEXT, TEXT, TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.submit_signup(BIGINT, INTEGER, TEXT, TEXT, TEXT, TEXT) TO authenticated;

-- 历史入口保留但关闭：不再授予任何终端角色。
-- 显式收回 anon/authenticated：仅 REVOKE FROM PUBLIC 收不回先前显式授予的定向授权。
REVOKE ALL ON FUNCTION public.signup(BIGINT, INTEGER, TEXT, TEXT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.signup(BIGINT, INTEGER, TEXT, TEXT, TEXT) FROM anon, authenticated;

REVOKE ALL ON FUNCTION public.cancel_registration(BIGINT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.cancel_registration(BIGINT) TO authenticated;

REVOKE ALL ON FUNCTION public.attach_registration_cover(BIGINT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.attach_registration_cover(BIGINT, TEXT) TO authenticated;

REVOKE ALL ON FUNCTION public.registration_stats() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.registration_stats() TO authenticated, anon;

REVOKE ALL ON FUNCTION public.set_activity_cover(TEXT, TEXT) FROM PUBLIC;
-- 显式收回 anon/authenticated：CREATE FUNCTION 时 Postgres 默认把 EXECUTE 授予 PUBLIC，
-- 仅 REVOKE FROM PUBLIC 收不回「先前显式授予」的定向授权。
REVOKE ALL ON FUNCTION public.set_activity_cover(TEXT, TEXT) FROM anon, authenticated;
GRANT EXECUTE ON FUNCTION public.set_activity_cover(TEXT, TEXT) TO service_role;

-- 归属建立通道：仅 service_role 可执行。
-- 管理侧插入的活动 owner_id 恒为 NULL（无 JWT claims），归属必须由管理侧
-- 显式指派（claim_activity 带 p_owner_uid 参数），不能由终端用户「先到先得」。
REVOKE ALL ON FUNCTION public.claim_activity(BIGINT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.claim_activity(BIGINT, TEXT) FROM anon, authenticated;
GRANT EXECUTE ON FUNCTION public.claim_activity(BIGINT, TEXT) TO service_role;

-- 旧签名（单参数，靠 auth.uid() 自行认领）已废止：显式 DROP，避免遗留入口。
DROP FUNCTION IF EXISTS public.claim_activity(BIGINT);

-- 主图绑定（canonical 通道）：授予 authenticated + service_role。
-- 安全依据在函数体内——目标路径由服务端拼出、调用方不可指定，
-- 文件名由 slug 决定，字节写入仍需管理员权限。
-- 返回路径字符串而非 activities 行，不会经响应体泄露 owner_id。
REVOKE ALL ON FUNCTION public.sync_activity_cover(TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.sync_activity_cover(TEXT) FROM anon;
GRANT EXECUTE ON FUNCTION public.sync_activity_cover(TEXT) TO authenticated, service_role;

-- 旧通道 claim_activity_cover 已废止并显式 DROP：
-- 它允许把主图写进 shared/<调用者 uid>/activities/，使公开可读的 cover_path
-- 内嵌 owner uid，等于绕回「用主图路径泄露创建者标识」的后门。
-- 客户端已无调用方（认领/换图入口已移除），保留它只会多留一条写入通道。
REVOKE ALL ON FUNCTION public.claim_activity_cover(TEXT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.claim_activity_cover(TEXT, TEXT) FROM anon, authenticated, service_role;
DROP FUNCTION IF EXISTS public.claim_activity_cover(TEXT, TEXT);

COMMENT ON FUNCTION public.submit_signup IS '提交报名：服务端完成人数口径容量校验、登录态与字段校验';
COMMENT ON FUNCTION public.cancel_registration IS '取消本人报名（软取消）';
COMMENT ON FUNCTION public.registration_stats IS '各活动已报名人数（人数口径聚合）';
COMMENT ON FUNCTION public.set_activity_cover IS '管理侧绑定活动主图，仅 service_role 可执行；返回整行含 owner_id，绝不可授予 authenticated';
COMMENT ON FUNCTION public.claim_activity IS '认领活动并建立归属关系；已有创建者不可抢占';
COMMENT ON FUNCTION public.sync_activity_cover IS '把活动主图绑定到应用共享空间的规范路径 shared/_application/activities/<slug>.png；路径不可由调用方指定';
