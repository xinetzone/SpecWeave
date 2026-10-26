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
AS $fn$
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
$fn$;
