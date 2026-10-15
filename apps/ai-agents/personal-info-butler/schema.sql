-- 个人信息管家 Agent · 云端数据库 Schema（Supabase / PostgreSQL）
-- 使用方式：Supabase 控制台 → SQL Editor → 粘贴执行
-- 说明：服务端使用 service_role key 访问，绕过 RLS；若需多用户隔离，请接入 Supabase Auth
--       并将 items 增加 user_id 列 + RLS 策略（见文件末尾注释）。

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- 条目主表
create table if not exists public.items (
  id          uuid primary key default gen_random_uuid(),
  kind        text        not null default 'idea',          -- idea | material | todo
  title       text        not null,
  content     text        not null default '',
  summary     text        not null default '',
  tags        text[]      not null default '{}',
  status      text        not null default 'open',          -- open | doing | done
  priority    text,                                         -- high | medium | low
  due_date    date,
  source      text,
  parent_id   uuid references public.items (id) on delete cascade,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create index if not exists items_created_at_idx  on public.items (created_at desc);
create index if not exists items_kind_idx        on public.items (kind);
create index if not exists items_status_idx      on public.items (status);
create index if not exists items_tags_idx        on public.items using gin (tags);
create index if not exists items_parent_idx      on public.items (parent_id);

-- ------------------------------------------------------------- 条目关联表
create table if not exists public.item_links (
  id         uuid primary key default gen_random_uuid(),
  from_id    uuid not null references public.items (id) on delete cascade,
  to_id      uuid not null references public.items (id) on delete cascade,
  score      real not null default 0,
  reason     text not null default '',
  created_at timestamptz not null default now(),
  constraint item_links_no_self check (from_id <> to_id),
  constraint item_links_unique  unique (from_id, to_id)
);

create index if not exists item_links_from_idx on public.item_links (from_id);
create index if not exists item_links_to_idx   on public.item_links (to_id);

-- ------------------------------------------------------------- 阶段总结表
create table if not exists public.summaries (
  id         uuid primary key default gen_random_uuid(),
  range_days int  not null default 7,
  item_count int  not null default 0,
  content_md text not null,
  created_at timestamptz not null default now()
);

create index if not exists summaries_created_at_idx on public.summaries (created_at desc);

-- ------------------------------------------------------------------- 可选
-- 多用户隔离（接入 Supabase Auth 后启用）：
--
-- alter table public.items      add column if not exists user_id uuid references auth.users (id);
-- alter table public.item_links add column if not exists user_id uuid references auth.users (id);
-- alter table public.summaries  add column if not exists user_id uuid references auth.users (id);
--
-- alter table public.items      enable row level security;
-- alter table public.item_links enable row level security;
-- alter table public.summaries  enable row level security;
--
-- create policy "own items" on public.items
--   for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- create policy "own links" on public.item_links
--   for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- create policy "own summaries" on public.summaries
--   for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
