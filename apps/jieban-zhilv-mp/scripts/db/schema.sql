-- 结伴之旅 · 云数据库最终态（单一真相源）
--
-- 说明：
-- 1. 本目录下的 SQL 以「每次一条语句」为单位执行（云数据库 MCP 端点不支持多语句）。
-- 2. 口径约定：报名人数一律按「人数」计（sum(companions)），不再按行数计。
-- 3. 客户端对 registrations 只有 SELECT 权限；写入与取消一律走 SECURITY DEFINER RPC。
-- 4. activities 增 published 字段，删除活动改为 RESTRICT，避免静默抹掉用户报名记录。
-- 5. 活动归属 owner_id 即创建者。2026-10-26 起归属语义翻转：
--    owner_id 由「管理侧显式指派」改为「发布者本人，服务端取 auth.uid()」——
--    真实活动由真人自己发布，归属是发布行为的结果而不是管理动作。
--    管理侧归属指派通道 claim_activity 已随之废止（见文件末尾 DROP）。
-- 6. activities 读策略：已发布全员可读；已下架仅创建者本人可见。
-- 7. activities 采用列级授权：owner_id 不授予 anon/authenticated，
--    避免访客直查活动创建者的微信 uid（含 openid 片段）。
--    created_at 客户端与脚本都不读，按最小权限同样不授权。
-- 8. 主图路径取值域不含用户标识：cover_path 是公开可读列，
--    一旦内嵌 owner uid 就等于绕回创建者标识泄露后门。
--    因此 cover_path 只允许取 shared/_application/activities/<slug>.png，
--    由 sync_activity_cover（路径由服务端拼出）与 set_activity_cover
--    （只接受 _application 前缀）共同锁死；旧通道 claim_activity_cover 已 DROP。
-- 9. 模板与活动分表（2026-10-26）：
--    activity_templates 存「活动骨架」（标题范式/亮点/须知/封面风格/默认名额与时长），
--    不承载报名、没有归属人、由平台维护；activities 存真实发生的活动实例，
--    有时间地点、有归属人、可报名。
--    混在一张表里会让「模板是否可报名」「模板有没有归属人」变成靠 published 猜的隐式约定。
-- 10. 活动封面改为内置素材白名单（activities.cover_slug）：
--    端用户可写的存储作用域只有 users/<uid>/（私有）与 shared/<uid>/（路径内嵌 uid），
--    而不含用户标识的 shared/_application/ 仅管理员可写（端用户会话一律 403）。
--    因此「用户上传封面 + 所有人可见 + 路径不含创建者标识」三者在当前平台约束下
--    不可兼得——封面改走随包分发的内置素材，路径不含任何用户标识，匿名访客也能看到。
-- 11. 真人发布活动的写入通道：create_activity / update_activity / my_activities。
--    归属、slug 生成、封面白名单、活动数上限全部在服务端裁决，
--    客户端既不传也不读 owner_id。

-- ============================================================
-- 表结构
-- ============================================================

CREATE TABLE IF NOT EXISTS public.activities (
  id          BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  slug        TEXT        NOT NULL UNIQUE,
  title       TEXT        NOT NULL,
  summary     TEXT,
  cover_path  TEXT,
  cover_slug  TEXT        NOT NULL DEFAULT 'default',
  location    TEXT,
  starts_at   TIMESTAMPTZ,
  ends_at     TIMESTAMPTZ,
  capacity    INTEGER     NOT NULL DEFAULT 100,
  price_note  TEXT,
  highlights  JSONB       NOT NULL DEFAULT '[]'::jsonb,
  notes       JSONB       NOT NULL DEFAULT '[]'::jsonb,
  published   BOOLEAN     NOT NULL DEFAULT TRUE,
  owner_id    TEXT        DEFAULT auth.uid(),
  template_id BIGINT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT activities_capacity_check CHECK (capacity >= 0),
  CONSTRAINT activities_cover_slug_check CHECK (cover_slug ~ '^[a-z0-9-]{1,64}$')
);

-- 活动模板：活动的骨架参考，不承载报名、无归属人、由平台维护。
CREATE TABLE IF NOT EXISTS public.activity_templates (
  id                     BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  slug                   TEXT        NOT NULL UNIQUE,
  title                  TEXT        NOT NULL,
  summary                TEXT,
  cover_slug             TEXT        NOT NULL DEFAULT 'default',
  highlights             JSONB       NOT NULL DEFAULT '[]'::jsonb,
  notes                  JSONB       NOT NULL DEFAULT '[]'::jsonb,
  default_capacity       INTEGER     NOT NULL DEFAULT 20,
  default_duration_minutes INTEGER   NOT NULL DEFAULT 180,
  published              BOOLEAN     NOT NULL DEFAULT TRUE,
  sort_order             INTEGER     NOT NULL DEFAULT 0,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT activity_templates_capacity_check CHECK (default_capacity >= 0),
  CONSTRAINT activity_templates_duration_check CHECK (default_duration_minutes > 0),
  CONSTRAINT activity_templates_cover_slug_check
    CHECK (cover_slug ~ '^[a-z0-9-]{1,64}$')
);

-- 模板被删除时活动仍保留（SET NULL），不连带抹掉真人发布的活动与报名
ALTER TABLE public.activities
  DROP CONSTRAINT IF EXISTS activities_template_id_fkey;
ALTER TABLE public.activities
  ADD CONSTRAINT activities_template_id_fkey
    FOREIGN KEY (template_id) REFERENCES public.activity_templates(id) ON DELETE SET NULL;

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
ALTER TABLE public.activity_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.registrations ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS activities_read_all ON public.activities;
-- 已发布活动全员可读；已下架活动仅创建者本人可见（避免报名记录页丢失活动元信息）
CREATE POLICY activities_read_all ON public.activities
  FOR SELECT TO authenticated, anon
  USING (published = TRUE OR owner_id = auth.uid());

DROP POLICY IF EXISTS activity_templates_read_published ON public.activity_templates;
-- 模板是平台内容：只有已发布的模板对全员可读；无任何客户端写权限
CREATE POLICY activity_templates_read_published ON public.activity_templates
  FOR SELECT TO authenticated, anon
  USING (published = TRUE);

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
-- cover_slug 与 template_id 是模板化改造新增的业务列，必须与客户端白名单同步。
GRANT SELECT (id, slug, title, summary, cover_path, cover_slug, location, starts_at, ends_at,
               capacity, price_note, highlights, notes, published, template_id)
  ON TABLE public.activities TO anon, authenticated;

-- 模板表同样列级授权：客户端只读模板内容，无任何写权限。
-- published 不授权（客户端不需要按状态过滤，服务端已用 RLS 过滤）；
-- created_at 不授权（客户端与脚本都不读）。
REVOKE ALL ON TABLE public.activity_templates FROM anon, authenticated;
REVOKE SELECT ON TABLE public.activity_templates FROM anon, authenticated;
GRANT SELECT (id, slug, title, summary, cover_slug, highlights, notes,
               default_capacity, default_duration_minutes, sort_order)
  ON TABLE public.activity_templates TO anon, authenticated;

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

-- 创建活动（真人发布活动的唯一入口）
--
-- 公理：
--   A1 身份唯一来源 = 服务端会话 uid。客户端【不得】自报身份，
--      因此本函数不接受任何归属参数，owner_id 恒取 auth.uid()。
--   A2 所有业务写入必须经服务端函数完成；客户端对业务表只有读权限。
--   A8 活动的归属者就是发布者本人——这是「真实活动由真人发布」的服务端保证。
--
-- 为什么 slug 由服务端生成、且不接受客户端传入：
--   slug 是公开可读列的取值的一部分，客户端若能指定，就能：
--     ① 抢占模板 slug（把模板顶掉或制造同名的假模板）；
--     ② 填入含正则元字符 / 路径穿越片段的 slug；
--     ③ 与他人已发布活动撞名后产生难以排查的覆盖与混淆。
--   服务端生成 'act-' + 随机串，从取值域上消除这类输入。
--
-- 状态：活动创建后立即 published=TRUE（先发布、后治理）。
--   平台尚无审核流程，若默认不发布会让「发布」变成空动作。
--   滥用治理靠「同一用户进行中活动数上限」（见下）+ 归属人可自行下架。
--
-- 并发安全：
--   同一用户的并发创建会同时通过「进行中活动数 ≤ 10」的检查，
--   造成实际数量超限。用事务级咨询锁按 uid 串行化同一用户的创建。
--   pg_advisory_xact_lock 在事务结束时自动释放，无需清理。
CREATE OR REPLACE FUNCTION public.create_activity(
  p_template_id   BIGINT,
  p_title         TEXT,
  p_summary       TEXT,
  p_location      TEXT,
  p_starts_at     TIMESTAMPTZ,
  p_ends_at       TIMESTAMPTZ,
  p_capacity      INTEGER,
  p_price_note    TEXT,
  p_highlights    JSONB,
  p_notes         JSONB,
  p_cover_slug    TEXT
)
RETURNS TABLE(activity_id BIGINT, activity_slug TEXT)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_uid          TEXT;
  v_slug         TEXT;
  v_template     public.activity_templates;
  v_active_count INTEGER;
  v_cover        TEXT;
BEGIN
  v_uid := auth.uid();
  IF v_uid IS NULL OR v_uid = '' THEN
    RAISE EXCEPTION '请先完成微信授权登录' USING ERRCODE = '42501';
  END IF;

  -- 同一用户的创建串行化：先取锁，再做「进行中活动数」检查。
  -- 哈希函数只用于派生锁键，不参与任何路径/标识拼接。
  PERFORM pg_advisory_xact_lock(hashtext(v_uid));

  -- 模板必须存在且已发布：模板是平台维护的内容，用户不能引用未发布模板
  SELECT * INTO v_template FROM public.activity_templates
    WHERE id = p_template_id AND published = TRUE;
  IF NOT FOUND THEN
    RAISE EXCEPTION '活动模板不可用' USING ERRCODE = '22023';
  END IF;

  -- 标题：必填、长度受限、去除首尾空白
  IF p_title IS NULL OR length(btrim(p_title)) < 2 THEN
    RAISE EXCEPTION '请填写活动名称（至少 2 个字）' USING ERRCODE = '22023';
  END IF;
  IF length(btrim(p_title)) > 40 THEN
    RAISE EXCEPTION '活动名称不能超过 40 字' USING ERRCODE = '22023';
  END IF;

  IF p_summary IS NOT NULL AND length(p_summary) > 200 THEN
    RAISE EXCEPTION '活动简介不能超过 200 字' USING ERRCODE = '22023';
  END IF;

  IF p_location IS NULL OR length(btrim(p_location)) < 2 THEN
    RAISE EXCEPTION '请填写活动地点' USING ERRCODE = '22023';
  END IF;
  IF length(btrim(p_location)) > 60 THEN
    RAISE EXCEPTION '活动地点不能超过 60 字' USING ERRCODE = '22023';
  END IF;

  -- 时间：必须开始时间在未来；结束时间必须晚于开始时间
  IF p_starts_at IS NULL THEN
    RAISE EXCEPTION '请选择活动开始时间' USING ERRCODE = '22023';
  END IF;
  IF p_starts_at <= now() THEN
    RAISE EXCEPTION '活动开始时间必须晚于当前时间' USING ERRCODE = '22023';
  END IF;
  IF p_ends_at IS NOT NULL AND p_ends_at <= p_starts_at THEN
    RAISE EXCEPTION '活动结束时间必须晚于开始时间' USING ERRCODE = '22023';
  END IF;

  -- 名额：0 表示不限名额（与既有 activities 口径一致）
  IF p_capacity IS NULL OR p_capacity < 0 THEN
    RAISE EXCEPTION '名额不能为负数' USING ERRCODE = '22023';
  END IF;
  IF p_capacity > 10000 THEN
    RAISE EXCEPTION '名额不能超过 10000 人' USING ERRCODE = '22023';
  END IF;

  IF p_price_note IS NOT NULL AND length(p_price_note) > 40 THEN
    RAISE EXCEPTION '费用说明不能超过 40 字' USING ERRCODE = '22023';
  END IF;

  -- 亮点与须知：必须是数组，且【每一项都必须是 JSON 字符串】。
  --
  -- 为什么必须校验元素类型：
  --   jsonb_array_elements_text 会把对象/数组元素转成它的 JSON 文本，
  --   例如 {"a":1} 会变成字符串 '{"a":1}'（长度 7，能通过 60 字限制）。
  --   那样就能把结构化内容塞进 highlights/notes，
  --   而客户端按字符串数组渲染，结构化内容会渲染成乱码或破坏布局。
  --   所以先用 jsonb_typeof 逐项确认是字符串，再校验长度。
  IF p_highlights IS NOT NULL THEN
    IF jsonb_typeof(p_highlights) <> 'array' THEN
      RAISE EXCEPTION '活动亮点格式不正确' USING ERRCODE = '22023';
    END IF;
    IF jsonb_array_length(p_highlights) > 8 THEN
      RAISE EXCEPTION '活动亮点最多 8 条' USING ERRCODE = '22023';
    END IF;
    IF EXISTS (
      SELECT 1 FROM jsonb_array_elements(p_highlights) t
      WHERE jsonb_typeof(t.value) <> 'string'
    ) THEN
      RAISE EXCEPTION '每条活动亮点都必须是文字' USING ERRCODE = '22023';
    END IF;
    IF EXISTS (
      SELECT 1 FROM jsonb_array_elements_text(p_highlights) t
      WHERE length(btrim(t)) = 0 OR length(t) > 60
    ) THEN
      RAISE EXCEPTION '每条活动亮点需在 60 字以内' USING ERRCODE = '22023';
    END IF;
  END IF;

  IF p_notes IS NOT NULL THEN
    IF jsonb_typeof(p_notes) <> 'array' THEN
      RAISE EXCEPTION '报名须知格式不正确' USING ERRCODE = '22023';
    END IF;
    IF jsonb_array_length(p_notes) > 8 THEN
      RAISE EXCEPTION '报名须知最多 8 条' USING ERRCODE = '22023';
    END IF;
    IF EXISTS (
      SELECT 1 FROM jsonb_array_elements(p_notes) t
      WHERE jsonb_typeof(t.value) <> 'string'
    ) THEN
      RAISE EXCEPTION '每条报名须知都必须是文字' USING ERRCODE = '22023';
    END IF;
    IF EXISTS (
      SELECT 1 FROM jsonb_array_elements_text(p_notes) t
      WHERE length(btrim(t)) = 0 OR length(t) > 60
    ) THEN
      RAISE EXCEPTION '每条报名须知需在 60 字以内' USING ERRCODE = '22023';
    END IF;
  END IF;

  -- 文本字段不得含控制字符（含换行、制表符）。
  --
  -- 长度检查挡不住换行：btrim 只去首尾空白，中间的 \n 会保留，
  -- 而客户端在标题、费用说明等位置按单行/紧凑布局渲染，
  -- 中间插入换行会破坏排版（标题换行、费用说明撑高两行）。
  IF has_control_chars(p_title) OR has_control_chars(p_summary)
     OR has_control_chars(p_location) OR has_control_chars(p_price_note) THEN
    RAISE EXCEPTION '内容中不能包含换行或控制字符' USING ERRCODE = '22023';
  END IF;

  -- 封面：只能取内置素材白名单。
  --
  -- 为什么不接受用户上传的图片路径：
  --   端用户可写的存储作用域只有 users/<uid>/（私有）与 shared/<uid>/（路径内嵌 uid），
  --   而不含用户标识的 shared/_application/ 仅管理员可写（端用户会话一律 403）。
  --   因此「用户上传封面 + 所有人可见 + 路径不含创建者标识」三者不可兼得。
  --   封面改为内置素材白名单：路径不含任何用户标识，随包分发，匿名访客也能看到。
  -- 白名单与 assets/covers/ 下的素材由结构测试逐项对齐（防止两侧漂移）。
  v_cover := COALESCE(NULLIF(p_cover_slug, ''), v_template.cover_slug);
  IF v_cover IS NULL OR v_cover NOT IN (
    'dawn-trek', 'night-market', 'island-week', 'city-walk', 'co-reading', 'default'
  ) THEN
    RAISE EXCEPTION '封面选择无效' USING ERRCODE = '22023';
  END IF;

  -- 滥用治理：同一用户「进行中」活动数上限。
  -- 「进行中」= 已发布且尚未结束。已下架与已结束的活动不占额度。
  SELECT count(*)::INTEGER INTO v_active_count
    FROM public.activities a
    WHERE a.owner_id = v_uid
      AND a.published = TRUE
      AND (a.ends_at IS NULL OR a.ends_at > now());
  IF v_active_count >= 10 THEN
    RAISE EXCEPTION '你同时进行的活动过多，请先结束或下架部分活动' USING ERRCODE = '22023';
  END IF;

  -- slug 由服务端生成：客户端无法指定，撞名概率可忽略，
  -- 且仍以 UNIQUE 约束兜底（万一真撞了会抛唯一约束冲突，不会静默覆盖）。
  v_slug := 'act-' || substr(replace(gen_random_uuid()::text, '-', ''), 1, 16);

  INSERT INTO public.activities (
    slug, title, summary, cover_slug, location, starts_at, ends_at,
    capacity, price_note, highlights, notes, published, owner_id, template_id
  )
  VALUES (
    v_slug, btrim(p_title), NULLIF(btrim(COALESCE(p_summary, '')), ''), v_cover,
    btrim(p_location), p_starts_at, p_ends_at, p_capacity,
    NULLIF(btrim(COALESCE(p_price_note, '')), ''),
    COALESCE(p_highlights, '[]'::jsonb), COALESCE(p_notes, '[]'::jsonb),
    TRUE, v_uid, p_template_id
  )
  RETURNING id, slug INTO activity_id, activity_slug;

  RETURN NEXT;
END;
$$;

-- 更新活动（仅归属人可编辑 / 下架 / 重新上架）
--
-- 越权防护：
--   归属判定完全在服务端：owner_id = auth.uid()。
--   客户端既不传 owner_id，也不传任何「我是谁」参数；
--   归属判定不接受客户端声称，等价于 A4（归属判定完全在服务端）。
--   归属不匹配时抛 42501，且不区分「活动不存在」与「不是你的活动」——
--   区分会形成存在性探测接口（可用来枚举他人活动的 id）。
--
-- 名额下调的额外约束：
--   已有人报名的活动，capacity 不得下调到低于当前已报名人数，
--   否则会出现「已报名人数 > 名额」的矛盾状态（isFull 恒真、名额进度条溢出）。
--   校验与更新在同一事务内完成，配合 FOR UPDATE 行锁防并发。
CREATE OR REPLACE FUNCTION public.update_activity(
  p_activity_id   BIGINT,
  p_title         TEXT,
  p_summary       TEXT,
  p_location      TEXT,
  p_starts_at     TIMESTAMPTZ,
  p_ends_at       TIMESTAMPTZ,
  p_capacity      INTEGER,
  p_price_note    TEXT,
  p_highlights    JSONB,
  p_notes         JSONB,
  p_cover_slug    TEXT,
  p_published     BOOLEAN
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_uid    TEXT;
  v_taken  BIGINT;
  v_hit    INTEGER;
  v_origin public.activities;
BEGIN
  v_uid := auth.uid();
  IF v_uid IS NULL OR v_uid = '' THEN
    RAISE EXCEPTION '请先完成微信授权登录' USING ERRCODE = '42501';
  END IF;

  -- 归属校验 + 行锁：FOR UPDATE 早于后续所有校验，
  -- 避免两人同时编辑同一活动时后写覆盖前写。
  SELECT * INTO v_origin FROM public.activities
    WHERE id = p_activity_id AND owner_id = v_uid
    FOR UPDATE;
  IF NOT FOUND THEN
    -- 不区分「不存在」与「非归属人」：区分会形成 id 存在性探测接口
    RAISE EXCEPTION '活动不存在或无权修改' USING ERRCODE = '42501';
  END IF;

  -- 下架走短路：归属人随时可以下架自己的活动，不受任何内容校验约束。
  --
  -- 为什么必须短路：内容校验里包含「开始时间必须晚于当前时间」，
  -- 而已结束/已开始的活动的开始时间天然早于当前时间。
  -- 若不短路，归属人将无法下架已经结束的活动——这是必须保留的处置手段，
  -- 不能被内容校验挡住。
  IF p_published = FALSE THEN
    UPDATE public.activities SET published = FALSE
      WHERE id = p_activity_id AND owner_id = v_uid;
    GET DIAGNOSTICS v_hit = ROW_COUNT;
    RETURN v_hit > 0;
  END IF;

  IF p_title IS NULL OR length(btrim(p_title)) < 2 THEN
    RAISE EXCEPTION '请填写活动名称（至少 2 个字）' USING ERRCODE = '22023';
  END IF;
  IF length(btrim(p_title)) > 40 THEN
    RAISE EXCEPTION '活动名称不能超过 40 字' USING ERRCODE = '22023';
  END IF;

  IF p_summary IS NOT NULL AND length(p_summary) > 200 THEN
    RAISE EXCEPTION '活动简介不能超过 200 字' USING ERRCODE = '22023';
  END IF;

  IF p_location IS NULL OR length(btrim(p_location)) < 2 THEN
    RAISE EXCEPTION '请填写活动地点' USING ERRCODE = '22023';
  END IF;
  IF length(btrim(p_location)) > 60 THEN
    RAISE EXCEPTION '活动地点不能超过 60 字' USING ERRCODE = '22023';
  END IF;

  -- 时间校验。
  --
  -- 判定「活动是否已开始」必须用【原值】v_origin.starts_at，不能用传入值 p_starts_at：
  -- 若用 p_starts_at 判定，把 p_starts_at 传成未来时刻就能整块跳过检查，
  -- 从而把已开始活动的开始时间改到未来——等于单方面变更已报名者的约定。
  IF p_starts_at IS NULL THEN
    RAISE EXCEPTION '请选择活动开始时间' USING ERRCODE = '22023';
  END IF;

  -- 未开始的活动：开始时间必须仍在未来
  IF v_origin.starts_at > now() AND p_starts_at <= now() THEN
    RAISE EXCEPTION '活动开始时间必须晚于当前时间' USING ERRCODE = '22023';
  END IF;

  -- 已开始的活动：不允许改开始时间（但允许改地点、须知等其余内容）
  IF v_origin.starts_at <= now()
     AND p_starts_at IS DISTINCT FROM v_origin.starts_at THEN
    RAISE EXCEPTION '活动已开始，不能再改开始时间' USING ERRCODE = '22023';
  END IF;

  -- 结束时间必须晚于开始时间，且不得被改到早于原开始时间
  IF p_ends_at IS NOT NULL AND p_ends_at <= p_starts_at THEN
    RAISE EXCEPTION '活动结束时间必须晚于开始时间' USING ERRCODE = '22023';
  END IF;
  IF p_ends_at IS NOT NULL AND v_origin.starts_at IS NOT NULL
     AND p_ends_at < v_origin.starts_at THEN
    RAISE EXCEPTION '活动结束时间不能早于原开始时间' USING ERRCODE = '22023';
  END IF;

  -- 重新上架一个已经结束的活动：内容不变、仅恢复可见。
  -- 走短路返回，避免「开始时间必须晚于当前时间」把重新上架挡掉。
  -- 判定方式：原状态下架 + 目标状态上架 + 全部内容字段与原值一致。
  --
  -- 为什么用 (a = b OR (a IS NULL AND b IS NULL)) 而不是 IS NOT DISTINCT FROM：
  --   `x IS NOT DISTINCT FROM y` 在多行 AND 链里与后续 AND 组合时，
  --   PostgreSQL 的语法解析会产生歧义（实测报 42601 syntax error）。
  --   显式展开成「相等或同为 NULL」，语义等价且解析无歧义。
  IF p_published = TRUE AND v_origin.published = FALSE
     AND (p_starts_at = v_origin.starts_at
          OR (p_starts_at IS NULL AND v_origin.starts_at IS NULL))
     AND (p_title = btrim(v_origin.title)
          OR (p_title IS NULL AND v_origin.title IS NULL))
     AND (p_location = btrim(v_origin.location)
          OR (p_location IS NULL AND v_origin.location IS NULL))
     AND (p_capacity = v_origin.capacity
          OR (p_capacity IS NULL AND v_origin.capacity IS NULL))
     AND (p_cover_slug = v_origin.cover_slug
          OR (p_cover_slug IS NULL AND v_origin.cover_slug IS NULL))
     AND (p_summary = v_origin.summary
          OR (p_summary IS NULL AND v_origin.summary IS NULL))
     AND (p_price_note = v_origin.price_note
          OR (p_price_note IS NULL AND v_origin.price_note IS NULL))
     AND (p_highlights = v_origin.highlights
          OR (p_highlights IS NULL AND v_origin.highlights IS NULL))
     AND (p_notes = v_origin.notes
          OR (p_notes IS NULL AND v_origin.notes IS NULL))
     AND (p_ends_at = v_origin.ends_at
          OR (p_ends_at IS NULL AND v_origin.ends_at IS NULL)) THEN
    UPDATE public.activities SET published = TRUE
      WHERE id = p_activity_id AND owner_id = v_uid;
    GET DIAGNOSTICS v_hit = ROW_COUNT;
    RETURN v_hit > 0;
  END IF;

  IF p_capacity IS NULL OR p_capacity < 0 THEN
    RAISE EXCEPTION '名额不能为负数' USING ERRCODE = '22023';
  END IF;
  IF p_capacity > 10000 THEN
    RAISE EXCEPTION '名额不能超过 10000 人' USING ERRCODE = '22023';
  END IF;

  IF p_price_note IS NOT NULL AND length(p_price_note) > 40 THEN
    RAISE EXCEPTION '费用说明不能超过 40 字' USING ERRCODE = '22023';
  END IF;

  IF p_highlights IS NOT NULL THEN
    IF jsonb_typeof(p_highlights) <> 'array' THEN
      RAISE EXCEPTION '活动亮点格式不正确' USING ERRCODE = '22023';
    END IF;
    IF jsonb_array_length(p_highlights) > 8 THEN
      RAISE EXCEPTION '活动亮点最多 8 条' USING ERRCODE = '22023';
    END IF;
    IF EXISTS (
      SELECT 1 FROM jsonb_array_elements(p_highlights) t
      WHERE jsonb_typeof(t.value) <> 'string'
    ) THEN
      RAISE EXCEPTION '每条活动亮点都必须是文字' USING ERRCODE = '22023';
    END IF;
    IF EXISTS (
      SELECT 1 FROM jsonb_array_elements_text(p_highlights) t
      WHERE length(btrim(t)) = 0 OR length(t) > 60
    ) THEN
      RAISE EXCEPTION '每条活动亮点需在 60 字以内' USING ERRCODE = '22023';
    END IF;
  END IF;

  IF p_notes IS NOT NULL THEN
    IF jsonb_typeof(p_notes) <> 'array' THEN
      RAISE EXCEPTION '报名须知格式不正确' USING ERRCODE = '22023';
    END IF;
    IF jsonb_array_length(p_notes) > 8 THEN
      RAISE EXCEPTION '报名须知最多 8 条' USING ERRCODE = '22023';
    END IF;
    -- 元素必须是字符串：jsonb_array_elements_text 会把对象转成 JSON 文本，
    -- 那样能把结构化内容塞进 highlights/notes，破坏客户端的字符串渲染。
    IF EXISTS (
      SELECT 1 FROM jsonb_array_elements(p_notes) t
      WHERE jsonb_typeof(t.value) <> 'string'
    ) THEN
      RAISE EXCEPTION '每条报名须知都必须是文字' USING ERRCODE = '22023';
    END IF;
    IF EXISTS (
      SELECT 1 FROM jsonb_array_elements_text(p_notes) t
      WHERE length(btrim(t)) = 0 OR length(t) > 60
    ) THEN
      RAISE EXCEPTION '每条报名须知需在 60 字以内' USING ERRCODE = '22023';
    END IF;
  END IF;

  -- 文本字段不得含控制字符（含换行、制表符）
  IF has_control_chars(p_title) OR has_control_chars(p_summary)
     OR has_control_chars(p_location) OR has_control_chars(p_price_note) THEN
    RAISE EXCEPTION '内容中不能包含换行或控制字符' USING ERRCODE = '22023';
  END IF;

  IF p_cover_slug IS NULL OR p_cover_slug NOT IN (
    'dawn-trek', 'night-market', 'island-week', 'city-walk', 'co-reading', 'default'
  ) THEN
    RAISE EXCEPTION '封面选择无效' USING ERRCODE = '22023';
  END IF;

  IF p_published IS NULL THEN
    RAISE EXCEPTION '发布状态无效' USING ERRCODE = '22023';
  END IF;

  -- 名额不得下调到已报名人数之下（人数口径：sum(companions)，含本人）
  IF p_capacity > 0 THEN
    SELECT COALESCE(sum(r.companions), 0)::BIGINT INTO v_taken
      FROM public.registrations r
      WHERE r.activity_id = p_activity_id AND r.status = 'confirmed';
    IF v_taken > p_capacity THEN
      RAISE EXCEPTION '名额不能少于已报名人数' USING ERRCODE = '22023';
    END IF;
  END IF;

  UPDATE public.activities SET
    title         = btrim(p_title),
    summary       = NULLIF(btrim(COALESCE(p_summary, '')), ''),
    location      = btrim(p_location),
    starts_at     = p_starts_at,
    ends_at       = p_ends_at,
    capacity      = p_capacity,
    price_note    = NULLIF(btrim(COALESCE(p_price_note, '')), ''),
    highlights    = COALESCE(p_highlights, '[]'::jsonb),
    notes         = COALESCE(p_notes, '[]'::jsonb),
    cover_slug    = p_cover_slug,
    published     = p_published
  WHERE id = p_activity_id AND owner_id = v_uid;

  GET DIAGNOSTICS v_hit = ROW_COUNT;
  RETURN v_hit > 0;
END;
$$;

-- 我发布的活动列表（仅归属人本人可见）
--
-- 为什么需要独立函数而不是让客户端查 activities：
--   activities 的读策略是「已发布全员可读 + 创建者可见自己下架的活动」，
--   客户端能读到自己的活动，但【无法判断某一行是不是自己的】——
--   owner_id 出于防泄露被移出了列级授权，客户端拿不到归属字段，
--   也就无法在结果集里区分「我的」与「别人的」。
--   若靠「客户端拿自己的 uid 去比 owner_id」来识别，就等于把 owner_id
--   又下发了一遍（哪怕只是自己那一列），这条后门不能开。
--   因此由服务端按 auth.uid() 直接过滤并返回。
--
-- 返回列刻意【不含 owner_id】：响应体里带出归属字段没有意义，
-- 且一旦将来有人把本函数误授权给 anon，
-- 带 owner_id 的响应体会绕过列级授权直接泄露创建者 uid。
--
-- 人数口径：signed_up = sum(companions)（含本人），与 submit_signup 的
-- 容量校验、registration_stats 的聚合三处同源。
-- 这里的聚合不过滤 published：下架的活动也要让归属人看到真实报名数，
-- 否则归属人无法判断「要不要先处理报名再下架」。
CREATE OR REPLACE FUNCTION public.my_activities()
RETURNS TABLE(
  activity_id  BIGINT,
  slug         TEXT,
  title        TEXT,
  summary      TEXT,
  cover_slug   TEXT,
  location     TEXT,
  starts_at    TIMESTAMPTZ,
  ends_at      TIMESTAMPTZ,
  capacity     INTEGER,
  price_note   TEXT,
  highlights   JSONB,
  notes        JSONB,
  published    BOOLEAN,
  signed_up    BIGINT
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path TO 'public'
AS $$
DECLARE
  v_uid TEXT;
BEGIN
  v_uid := auth.uid();
  IF v_uid IS NULL OR v_uid = '' THEN
    RAISE EXCEPTION '请先完成微信授权登录' USING ERRCODE = '42501';
  END IF;

  RETURN QUERY
  SELECT
    a.id,
    a.slug,
    a.title,
    a.summary,
    a.cover_slug,
    a.location,
    a.starts_at,
    a.ends_at,
    a.capacity,
    a.price_note,
    a.highlights,
    a.notes,
    a.published,
    COALESCE((
      SELECT sum(r.companions)::BIGINT
      FROM public.registrations r
      WHERE r.activity_id = a.id AND r.status = 'confirmed'
    ), 0)::BIGINT AS signed_up
  FROM public.activities a
  WHERE a.owner_id = v_uid
  ORDER BY a.starts_at DESC;
END;
$$;

-- 判断文本是否含控制字符（换行、制表符等）。
--
-- 长度检查挡不住控制字符：btrim 只去首尾空白，中间的 \n 会保留，
-- 而客户端按单行/紧凑布局渲染，含换行的标题会破坏排版。
--
-- 正则只用字面量模式，不拼接任何用户输入（uid 拼进正则会放宽校验）。
--
-- IMMUTABLE：纯函数，不读表不受 RLS 影响，可在 CHECK 与函数体内自由调用。
CREATE OR REPLACE FUNCTION public.has_control_chars(p_text TEXT)
RETURNS BOOLEAN
LANGUAGE sql
IMMUTABLE
AS $$
  SELECT p_text IS NOT NULL AND p_text ~ '[\x00-\x1F\x7F]';
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

-- 归属建立通道已废止（2026-10-26 模板化改造）：
-- 活动归属语义从「管理侧显式指派」翻转为「发布者本人」——
-- 真实活动由真人自己发布，owner_id 恒等于服务端取到的 auth.uid()。
-- claim_activity 存在的唯一目的是让管理侧把 owner_id 指向某个账号，
-- 这个语义已不存在，保留它只会多留一条「把归属写给别人」的写入通道。
REVOKE ALL ON FUNCTION public.claim_activity(BIGINT, TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.claim_activity(BIGINT, TEXT) FROM anon, authenticated, service_role;
DROP FUNCTION IF EXISTS public.claim_activity(BIGINT, TEXT);

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

-- 真人发布活动的写入通道（2026-10-26）：授予 authenticated。
-- 归属、slug 生成、封面白名单、活动数上限全部在函数体内裁决，
-- 客户端既不传也不读 owner_id。
REVOKE ALL ON FUNCTION public.create_activity(BIGINT, TEXT, TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ, INTEGER, TEXT, JSONB, JSONB, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.create_activity(BIGINT, TEXT, TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ, INTEGER, TEXT, JSONB, JSONB, TEXT) TO authenticated;

REVOKE ALL ON FUNCTION public.update_activity(BIGINT, TEXT, TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ, INTEGER, TEXT, JSONB, JSONB, TEXT, BOOLEAN) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.update_activity(BIGINT, TEXT, TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ, INTEGER, TEXT, JSONB, JSONB, TEXT, BOOLEAN) TO authenticated;

REVOKE ALL ON FUNCTION public.my_activities() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.my_activities() TO authenticated;

COMMENT ON FUNCTION public.submit_signup IS '提交报名：服务端完成人数口径容量校验、登录态与字段校验';
COMMENT ON FUNCTION public.cancel_registration IS '取消本人报名（软取消）';
COMMENT ON FUNCTION public.registration_stats IS '各活动已报名人数（人数口径聚合）';
COMMENT ON FUNCTION public.set_activity_cover IS '管理侧绑定活动主图，仅 service_role 可执行；只返回路径字符串';
COMMENT ON FUNCTION public.sync_activity_cover IS '把活动主图绑定到应用共享空间的规范路径 shared/_application/activities/<slug>.png；路径不可由调用方指定';
COMMENT ON FUNCTION public.create_activity IS '发布活动：归属取 auth.uid()、slug 服务端生成、封面白名单校验、同一用户进行中活动数上限';
COMMENT ON FUNCTION public.update_activity IS '编辑/下架/重新上架本人活动：归属在服务端校验，下架走短路不受内容校验约束';
COMMENT ON FUNCTION public.my_activities IS '我发布的活动列表：服务端按 auth.uid() 过滤，返回列不含 owner_id';
