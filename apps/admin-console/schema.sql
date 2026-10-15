-- ---------------------------------------------------------------------------
-- admin-console —— Supabase（Postgres）表结构
-- 用法：Supabase 控制台 → SQL Editor → 粘贴执行
-- 说明：全部表使用 ac_ 前缀，避免与同库其他应用冲突
-- ---------------------------------------------------------------------------

-- 管理员：只存 PBKDF2 哈希与盐，明文口令永不落库
create table if not exists ac_admins (
  id            text primary key,
  email         text not null unique,
  password_hash text not null,
  salt          text not null,
  display_name  text not null default '',
  role          text not null default 'admin',   -- admin | editor
  created_at    timestamptz not null default now(),
  last_login_at timestamptz
);

create table if not exists ac_categories (
  id         text primary key,
  name       text not null,
  slug       text not null default '',
  sort_order integer not null default 100,
  created_at timestamptz not null default now()
);

create table if not exists ac_tags (
  id         text primary key,
  name       text not null,
  slug       text not null default '',
  created_at timestamptz not null default now()
);

create table if not exists ac_items (
  id           text primary key,
  title        text not null,
  slug         text not null default '',
  summary      text not null default '',
  body         text not null default '',
  status       text not null default 'draft',    -- draft | published | archived
  category_id  text references ac_categories(id) on delete set null,
  cover_url    text not null default '',
  published_at timestamptz,
  created_by   text not null default '',
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create index if not exists idx_ac_items_status on ac_items (status);
create index if not exists idx_ac_items_category on ac_items (category_id);
create index if not exists idx_ac_items_created on ac_items (created_at desc);
create index if not exists idx_ac_items_updated on ac_items (updated_at desc);

create table if not exists ac_item_tags (
  item_id text not null references ac_items(id) on delete cascade,
  tag_id  text not null references ac_tags(id) on delete cascade,
  primary key (item_id, tag_id)
);

create index if not exists idx_ac_item_tags_tag on ac_item_tags (tag_id);

create table if not exists ac_attachments (
  id           text primary key,
  item_id      text references ac_items(id) on delete set null,
  filename     text not null,
  path         text not null,
  url          text not null default '',
  content_type text not null default 'application/octet-stream',
  size         bigint not null default 0,
  created_by   text not null default '',
  created_at   timestamptz not null default now()
);

create index if not exists idx_ac_attachments_item on ac_attachments (item_id);

create table if not exists ac_audit_logs (
  id         text primary key,
  actor      text not null default 'system',
  action     text not null default '',
  target     text not null default '',
  detail     text not null default '',
  created_at timestamptz not null default now()
);

create index if not exists idx_ac_logs_created on ac_audit_logs (created_at desc);

-- 初始分类（可自行调整）
insert into ac_categories (id, name, slug, sort_order)
values
  ('cat-general',  '未分类', 'uncategorized', 10),
  ('cat-news',     '资讯',   'news',          20),
  ('cat-tutorial', '教程',   'tutorial',      30)
on conflict (id) do nothing;

-- ---------------------------------------------------------------------------
-- 安全建议（按需执行）
-- 1) 启用 RLS：service_role key 会绕过 RLS，anon key 则被完全拒绝，避免误用 anon 暴露数据。
-- ---------------------------------------------------------------------------
alter table ac_admins      enable row level security;
alter table ac_categories  enable row level security;
alter table ac_tags        enable row level security;
alter table ac_items       enable row level security;
alter table ac_item_tags   enable row level security;
alter table ac_attachments enable row level security;
alter table ac_audit_logs  enable row level security;

-- 2) Storage：在 Supabase 控制台创建 bucket `ac-uploads`（名称需与 SUPABASE_BUCKET 一致）。
--    公开桶可直接用 public URL；私有桶请在 bucket 策略中允许 service_role 读写，
--    应用会自动改用签名 URL。
