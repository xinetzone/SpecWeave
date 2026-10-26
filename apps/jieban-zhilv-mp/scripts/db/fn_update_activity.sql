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
