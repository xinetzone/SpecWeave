-- 个人信息管家 Agent —— 云端数据库 DDL（Supabase / PostgreSQL）
--
-- 用法：Supabase 控制台 → SQL Editor → 粘贴执行。可重复执行（IF NOT EXISTS）。
-- 三张表：items（条目）、item_links（关联及理由）、summaries（阶段总结存档）。

create extension if not exists "pgcrypto";

-- 条目 ---------------------------------------------------------------------
create table if not exists items (
    id          uuid primary key default gen_random_uuid(),
    kind        text        not null default 'idea'
                check (kind in ('idea', 'material', 'todo')),
    title       text        not null,
    content     text        not null,
    summary     text        not null default '',
    tags        text[]      not null default '{}',
    status      text        not null default 'open'
                check (status in ('open', 'done', 'archived')),
    priority    smallint    not null default 2 check (priority between 1 and 3),
    due_date    date,
    source      text        not null default 'web',
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);

create index if not exists items_created_at_idx on items (created_at desc);
create index if not exists items_kind_idx       on items (kind);
create index if not exists items_status_idx     on items (status);
create index if not exists items_tags_idx       on items using gin (tags);

-- 关联：score 是相似度分数，reason 是给人看的理由 ----------------------------
create table if not exists item_links (
    id         uuid primary key default gen_random_uuid(),
    src_id     uuid not null references items (id) on delete cascade,
    dst_id     uuid not null references items (id) on delete cascade,
    score      real not null default 0,
    reason     text not null default '',
    created_at timestamptz not null default now(),
    constraint item_links_no_self check (src_id <> dst_id),
    constraint item_links_unique  unique (src_id, dst_id)
);

create index if not exists item_links_src_idx on item_links (src_id);
create index if not exists item_links_dst_idx on item_links (dst_id);

-- 阶段总结存档 ---------------------------------------------------------------
create table if not exists summaries (
    id           uuid primary key default gen_random_uuid(),
    period_start date not null,
    period_end   date not null,
    title        text not null default '',
    content      text not null,
    actions      jsonb not null default '[]'::jsonb,
    created_at   timestamptz not null default now()
);

create index if not exists summaries_created_at_idx on summaries (created_at desc);

-- PostgREST（Supabase REST 层）需要 schema 缓存刷新后才能看见新表
notify pgrst, 'reload schema';

-- ===========================================================================
-- 多用户隔离（可选，MVP 默认单用户）
--
-- 若要多人共用同一个 Supabase 项目：加 user_id 列，开启 RLS，并让后端在写入时
-- 带上 user_id。下面是可直接执行的骨架。
-- ===========================================================================
--
-- alter table items      add column if not exists user_id uuid references auth.users (id);
-- alter table item_links add column if not exists user_id uuid references auth.users (id);
-- alter table summaries  add column if not exists user_id uuid references auth.users (id);
--
-- alter table items      enable row level security;
-- alter table item_links enable row level security;
-- alter table summaries  enable row level security;
--
-- create policy items_owner on items
--     using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- create policy item_links_owner on item_links
--     using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- create policy summaries_owner on summaries
--     using (auth.uid() = user_id) with check (auth.uid() = user_id);
--
-- 注意：后端用的是 service role key，RLS 对它不生效。若后端要代表多用户写入，
-- 应改用用户的 access token 调用 PostgREST，或在应用层自行隔离 user_id。
