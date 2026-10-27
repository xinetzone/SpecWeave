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
