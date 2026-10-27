-- 活动表结构变更：模板化 + 真人发布
--
-- 变更点：
--   1. 新增 cover_slug TEXT：封面改为内置素材键（随包分发，路径不含任何用户标识）。
--      为什么不用 cover_path 承载用户上传的封面：端用户可写的存储作用域只有
--      users/<uid>/（私有）与 shared/<uid>/（路径内嵌 uid），
--      而不含用户标识的 shared/_application/ 仅管理员可写（端用户会话 403）。
--      因此「用户上传封面 + 所有人可见 + 不暴露创建者标识」三者在当前平台
--      约束下不可兼得，封面改走内置素材白名单。
--   2. 新增 template_id BIGINT：记录该活动由哪个模板发起（可空：用户也可自由发起）。
--   3. cover_path 列保留但不再作为用户主图通道：
--      它仍是平台侧已发布主图的规范路径（shared/_application/activities/<slug>.png），
--      由 sync_activity_cover 服务端拼出，调用方不可指定。
--      保留而不删除，是为了不破坏既有云端主图资产与 AC-13 的取值域约束。
--
-- 注意：activities.owner_id 语义不变（归属人），但建立方式从
--   「管理侧显式指派」改为「发布者本人，服务端取 auth.uid()」。

ALTER TABLE public.activities
  ADD COLUMN IF NOT EXISTS cover_slug TEXT NOT NULL DEFAULT 'default';

ALTER TABLE public.activities
  ADD COLUMN IF NOT EXISTS template_id BIGINT;

-- cover_slug 取值域必须是内置素材键（不含用户标识、不含路径分隔符）
ALTER TABLE public.activities
  DROP CONSTRAINT IF EXISTS activities_cover_slug_check;
ALTER TABLE public.activities
  ADD CONSTRAINT activities_cover_slug_check
    CHECK (cover_slug ~ '^[a-z0-9-]{1,64}$');

-- 模板外键：模板被删除时活动仍保留（SET NULL），不连带抹掉真人发布的活动与报名
ALTER TABLE public.activities
  DROP CONSTRAINT IF EXISTS activities_template_id_fkey;
ALTER TABLE public.activities
  ADD CONSTRAINT activities_template_id_fkey
    FOREIGN KEY (template_id) REFERENCES public.activity_templates(id) ON DELETE SET NULL;

COMMENT ON COLUMN public.activities.cover_slug IS
  '内置封面素材键；取值域为 assets/covers/ 下的素材名，路径不含任何用户标识';
COMMENT ON COLUMN public.activities.template_id IS
  '发起该活动所用的模板；NULL 表示用户自由发起（非套用模板）';
