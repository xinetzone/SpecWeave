-- 活动主图绑定（管理侧通道，仅 service_role 可执行）
--
-- 路径前缀固定为 shared/_application/activities/（Application owner 作用域，
-- 仅 admin 可写、全体登录用户可读），因此该通道绑定的主图不依赖任何终端用户。
--
-- 越权防护：
--   1. p_slug 先按字面量校验为安全 slug（^[a-z0-9-]{1,64}$），它只参与等值比较，
--      绝不作为正则模式的一部分拼接（slug 含正则元字符时拼进模式会放宽校验）；
--   2. 路径按 '/' 结构化切分：必须恰好 4 段 shared/_application/activities/<file>；
--      文件名段用捕获组取出 slug 与扩展名后做等值比较；
--   3. 活动行 FOR UPDATE 锁，避免并发下互相覆盖。
--
-- 返回类型只返回路径字符串，不返回 activities 行（含 owner_id）：
--   一旦本函数被误授予 authenticated，创建者标识会经 RPC 响应体下发，
--   绕开列级授权。详见 schema.sql 同名函数的完整说明。
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
