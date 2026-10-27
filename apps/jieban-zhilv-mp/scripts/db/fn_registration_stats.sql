-- 只统计已发布活动；未发布（下架）活动的报名人数不外泄给匿名调用方。
CREATE OR REPLACE FUNCTION public.registration_stats()
RETURNS TABLE(activity_id BIGINT, signed_up BIGINT)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path TO 'public'
AS $fn$
  SELECT r.activity_id, COALESCE(sum(r.companions), 0)::BIGINT
  FROM public.registrations r
  JOIN public.activities a ON a.id = r.activity_id
  WHERE r.status = 'confirmed' AND a.published = TRUE
  GROUP BY r.activity_id
$fn$;
