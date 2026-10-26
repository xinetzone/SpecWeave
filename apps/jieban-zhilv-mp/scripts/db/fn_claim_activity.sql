-- 活动归属指派（管理侧专用，仅 service_role 可执行）
--
-- 场景：存量活动由管理侧预置，owner_id 为空；由管理侧显式指派归属账号。
--       指派后，该账号即成为活动归属人（RLS owner 分支随之生效）。
--       注：主图绑定已改走 canonical 通道 sync_activity_cover，
--       目标路径由服务端拼出，不再按调用者 uid 分作用域。
--
-- 为什么是「显式指派」而不是「首个登录用户认领」：
--   早期版本是「owner_id IS NULL 时，谁先登录谁就是创建者」，这把归属判定
--   从服务端管理凭证降级成了客户端时序——任何登录用户都能抢先接管任意
--   活动的主图绑定权。当前版本要求调用方（管理侧）显式给出 p_owner_uid，
--   归属由管理侧决定，不依赖任何终端用户的登录顺序。
--
-- 越权防护：
--   1. 仅当 owner_id IS NULL（无人指派）时才能指派，已有归属者不能被抢占；
--   2. 重复指派给同一账号幂等返回 true；
--   3. 行锁避免并发下两人同时指派成功；
--   4. p_owner_uid 不能为空，也不能是 'anon' / 'authenticated'
--      （否则等于把归属开放给全体终端用户）。
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
