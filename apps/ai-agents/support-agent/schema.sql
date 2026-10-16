-- ---------------------------------------------------------------------------
-- 智能客服 Agent —— Supabase（Postgres）表结构
-- 用法：Supabase 控制台 → SQL Editor → 粘贴执行
-- 说明：全部表使用 cs_ 前缀，避免与同库其他应用冲突
-- ---------------------------------------------------------------------------

create table if not exists cs_sessions (
  id          text primary key,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  status      text not null default 'open',       -- open | transferred | closed
  last_intent text default '',
  transferred boolean not null default false,
  channel     text not null default 'web'
);

create table if not exists cs_messages (
  id             bigserial primary key,
  session_id     text not null references cs_sessions(id) on delete cascade,
  role           text not null,                   -- user | assistant
  content        text not null,
  intent         text default '',
  confidence     double precision default 0,
  source         text default 'llm',              -- llm | faq | human
  needs_human    boolean not null default false,
  low_confidence boolean not null default false,
  faq_ids        text default '',
  latency_ms     integer default 0,
  created_at     timestamptz not null default now()
);

create index if not exists idx_cs_messages_session_time
  on cs_messages (session_id, created_at);

create table if not exists cs_feedback (
  id         bigserial primary key,
  session_id text not null,
  rating     integer not null,                    -- 1..5
  resolved   boolean not null default true,
  comment    text default '',
  created_at timestamptz not null default now()
);

create index if not exists idx_cs_feedback_session on cs_feedback (session_id);

create table if not exists cs_tickets (
  id         text primary key,
  session_id text not null,
  intent     text default '',
  reason     text default '',
  status     text not null default 'pending',     -- pending | processing | closed
  created_at timestamptz not null default now()
);

create table if not exists cs_faq (
  id         text primary key,
  category   text not null default 'other',       -- refund | order_query | tech_support | other
  question   text not null,
  answer     text not null,
  keywords   text default '',
  updated_at timestamptz not null default now()
);

-- 示例：人工坐席视角的常用查询
-- select s.id, s.last_intent, s.status, count(m.id) as turns
--   from cs_sessions s left join cs_messages m on m.session_id = s.id
--  group by s.id order by s.updated_at desc limit 50;
