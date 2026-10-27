-- 夹具：P1-15 形态 —— 列级授权已收紧（owner_id 不在对外清单），
-- 但公开可读的 cover_path 的值里仍内嵌 owner uid。
-- 这正是「挡住列 ≠ 挡住值」的真实形态。
CREATE TABLE public.activities (
  id        BIGSERIAL PRIMARY KEY,
  slug      TEXT NOT NULL UNIQUE,
  title     TEXT NOT NULL,
  cover_path TEXT,
  owner_id  TEXT
);

REVOKE ALL ON TABLE public.activities FROM anon, authenticated;
REVOKE SELECT ON TABLE public.activities FROM anon, authenticated;
GRANT SELECT (id, slug, title, cover_path)
  ON TABLE public.activities TO anon, authenticated;

-- 种子数据：cover_path 的值里带着 owner uid
INSERT INTO public.activities (slug, title, cover_path, owner_id)
VALUES ('dawn-trek', '破晓徒步 · 城市山野线',
        'shared/2114562052432330752/activities/dawn-trek.png', '2114562052432330752');

-- 服务端用调用方标识拼出路径后写入公开列：值域由调用方决定
CREATE OR REPLACE FUNCTION public.bind_activity_cover(p_slug TEXT, p_owner_uid TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_path TEXT;
BEGIN
  v_path := 'shared/' || p_owner_uid || '/activities/' || p_slug || '.png';
  UPDATE public.activities SET cover_path = v_path WHERE slug = p_slug;
  RETURN v_path;
END;
$$;

REVOKE ALL ON FUNCTION public.bind_activity_cover(TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.bind_activity_cover(TEXT, TEXT) TO authenticated, service_role;
