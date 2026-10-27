-- 夹具：整改后的状态（列级授权 + 路径由服务端拼出 + RPC 只返回路径）
CREATE TABLE public.activities (
  id        BIGSERIAL PRIMARY KEY,
  slug      TEXT NOT NULL UNIQUE,
  title     TEXT NOT NULL,
  cover_path TEXT,
  owner_id  TEXT
);

CREATE TABLE public.registrations (
  id          BIGSERIAL PRIMARY KEY,
  activity_id BIGINT NOT NULL,
  owner_id    TEXT NOT NULL,
  cover_path  TEXT
);

REVOKE ALL ON TABLE public.activities FROM anon, authenticated;
REVOKE SELECT ON TABLE public.activities FROM anon, authenticated;
GRANT SELECT (id, slug, title, summary, cover_path)
  ON TABLE public.activities TO anon, authenticated;

REVOKE ALL ON TABLE public.registrations FROM anon, authenticated;
GRANT SELECT ON TABLE public.registrations TO anon, authenticated;

-- canonical 通道：目标路径由服务端拼出，调用方不传路径
CREATE OR REPLACE FUNCTION public.sync_activity_cover(p_slug TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_path TEXT;
BEGIN
  IF p_slug IS NULL OR p_slug !~ '^[a-z0-9-]{1,64}$' THEN
    RAISE EXCEPTION '活动参数无效' USING ERRCODE = '22023';
  END IF;
  v_path := 'shared/_application/activities/' || p_slug || '.png';
  UPDATE public.activities SET cover_path = v_path WHERE slug = p_slug;
  RETURN v_path;
END;
$$;

REVOKE ALL ON FUNCTION public.sync_activity_cover(TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.sync_activity_cover(TEXT) TO authenticated, service_role;

-- 管理侧通道：只返回路径，不返回整行
CREATE OR REPLACE FUNCTION public.set_activity_cover(p_slug TEXT, p_path TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE public.activities SET cover_path = p_path WHERE slug = p_slug;
  RETURN p_path;
END;
$$;

REVOKE ALL ON FUNCTION public.set_activity_cover(TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.set_activity_cover(TEXT, TEXT) TO service_role;

-- 行级隔离到本人（RLS）——工具据此自动判定「该表的行他人看不到」
CREATE POLICY registrations_read_own ON public.registrations
  FOR SELECT TO anon, authenticated
  USING (owner_id = auth.uid());
