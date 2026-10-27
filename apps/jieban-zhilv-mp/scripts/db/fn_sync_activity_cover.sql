-- 活动主图绑定（canonical 通道，authenticated + service_role）
--
-- 目标路径由服务端拼出、调用方不可指定：
--   cover_path 的取值域被锁死为 shared/_application/activities/<slug>.png，
--   路径中不含任何用户标识（旧版允许写 shared/<uid>/activities/，
--   使公开可读的 cover_path 内嵌 owner uid，等于绕回创建者标识泄露后门）。
--
-- 目标对象必须已存在于云存储且属应用身份，否则拒绝绑定：
--   避免 cover_path 指向缺失对象，让客户端拿到「能签发但 404」的地址。
--
-- 本函数返回路径字符串，不返回 activities 行，不会经响应体泄露 owner_id。
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
