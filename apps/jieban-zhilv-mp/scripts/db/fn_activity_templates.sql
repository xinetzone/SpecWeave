-- 活动模板：活动骨架模板（不含报名、不含时间地点）
--
-- 为什么要把模板从 activities 拆成独立表：
--   模板是「活动长什么样」的骨架（标题范式、亮点、须知、封面风格、名额与时长默认值），
--   不承载报名、也没有「谁发布」的概念；活动是某一次真实发生的、有时间地点、
--   有归属人的实例。两者生命周期、权限面、可见性规则都不同，混在一张表里
--   会让「模板是否可报名」「模板有没有归属人」变成靠 published 猜的隐式约定。
--
-- 模板表的客户端权限面比 activities 更窄：
--   - 只读，且只暴露 published=TRUE 的模板；
--   - 没有任何客户端写权限（模板是平台内容，由管理侧维护）；
--   - created_at 不授权（客户端与脚本都不读它，按最小权限处理）。
CREATE TABLE IF NOT EXISTS public.activity_templates (
  id                     BIGINT      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  slug                   TEXT        NOT NULL UNIQUE,
  title                  TEXT        NOT NULL,
  summary                TEXT,
  cover_slug             TEXT        NOT NULL DEFAULT 'default',
  highlights             JSONB       NOT NULL DEFAULT '[]'::jsonb,
  notes                  JSONB       NOT NULL DEFAULT '[]'::jsonb,
  default_capacity       INTEGER     NOT NULL DEFAULT 20,
  default_duration_minutes INTEGER   NOT NULL DEFAULT 180,
  published              BOOLEAN     NOT NULL DEFAULT TRUE,
  sort_order             INTEGER     NOT NULL DEFAULT 0,
  created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT activity_templates_capacity_check CHECK (default_capacity >= 0),
  CONSTRAINT activity_templates_duration_check CHECK (default_duration_minutes > 0),
  CONSTRAINT activity_templates_cover_slug_check
    CHECK (cover_slug ~ '^[a-z0-9-]{1,64}$')
);

COMMENT ON TABLE public.activity_templates IS
  '活动模板表：活动的骨架参考（标题范式/亮点/须知/封面风格/默认名额与时长）；不承载报名，无归属人';

ALTER TABLE public.activity_templates ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS activity_templates_read_published ON public.activity_templates;
-- 已发布模板全员可读；未发布模板仅管理侧可见（客户端无任何写权限，无人会读到未发布模板）
CREATE POLICY activity_templates_read_published ON public.activity_templates
  FOR SELECT TO authenticated, anon
  USING (published = TRUE);

REVOKE ALL ON TABLE public.activity_templates FROM anon, authenticated;
REVOKE SELECT ON TABLE public.activity_templates FROM anon, authenticated;
-- 列级授权：不含 published（客户端不需要按发布状态过滤，服务端已用 RLS 过滤）
-- 与 created_at（客户端与脚本都不读，按最小权限同样不授权）。
GRANT SELECT (id, slug, title, summary, cover_slug, highlights, notes,
               default_capacity, default_duration_minutes, sort_order)
  ON TABLE public.activity_templates TO anon, authenticated;
