-- 夹具：整改前的状态（表级授权 + 入参可决定主图路径 + RPC 返回整行）
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

-- 表级授权：隐含所有列，owner_id 一并下发
GRANT SELECT ON TABLE public.activities TO anon, authenticated;
GRANT SELECT ON TABLE public.registrations TO anon, authenticated;

-- 归属者绑定通道：路径由调用方传入
CREATE OR REPLACE FUNCTION public.claim_activity_cover(p_slug TEXT, p_path TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE public.activities SET cover_path = p_path WHERE slug = p_slug;
  RETURN TRUE;
END;
$$;

REVOKE ALL ON FUNCTION public.claim_activity_cover(TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.claim_activity_cover(TEXT, TEXT) TO authenticated, service_role;

-- 返回整行 registrations（含 owner_id）
CREATE OR REPLACE FUNCTION public.submit_signup(p_activity_id BIGINT, p_owner_name TEXT)
RETURNS SETOF public.registrations
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY SELECT * FROM public.registrations WHERE activity_id = p_activity_id;
END;
$$;

GRANT EXECUTE ON FUNCTION public.submit_signup(BIGINT, TEXT) TO authenticated;

-- 列级授权清单里直接写了 owner_id
REVOKE ALL ON TABLE public.activities FROM anon, authenticated;
GRANT SELECT (id, slug, title, cover_path, owner_id)
  ON TABLE public.activities TO anon, authenticated;

-- 行级隔离到本人（RLS）——工具据此自动判定「该表的行他人看不到」
CREATE POLICY registrations_read_own ON public.registrations
  FOR SELECT TO anon, authenticated
  USING (owner_id = auth.uid());
