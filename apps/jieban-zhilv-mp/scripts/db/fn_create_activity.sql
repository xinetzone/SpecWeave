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
