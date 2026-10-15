import { withApi, ok, fail, getQuery } from './_lib/http.js';
import { llmConfigFrom } from './_lib/config.js';
import * as store from './_lib/store.js';
import { chatJson } from './_lib/llm.js';
import { TODO_SYSTEM, todoUser } from './_lib/prompts.js';
import { formatItems } from './_lib/pipeline.js';

const ORDER = { high: 0, medium: 1, low: 2, P0: 0, P1: 1, P2: 2 };

export default withApi(async (req, res) => {
  if (req.method !== 'GET') return fail(res, 405, '仅支持 GET');

  const query = getQuery(req);
  const includeDone = query.get('done') === '1';
  const cfg = llmConfigFrom(req);

  const all = await store.listItems({ limit: 500 });
  const raw = all.filter((i) => i.kind === 'todo' && (includeDone || i.status !== 'done'));

  const todos = raw.sort((a, b) => {
    const pa = ORDER[a.priority] ?? 9;
    const pb = ORDER[b.priority] ?? 9;
    if (pa !== pb) return pa - pb;
    return String(b.created_at).localeCompare(String(a.created_at));
  });

  if (!cfg.key || !todos.length) {
    return ok(res, {
      groups: [
        {
          level: 'P1',
          items: todos.map((t) => ({
            title: t.title,
            reason: t.due_date ? `截止 ${t.due_date}` : '来自你的记录',
            next_step: t.summary || '直接开始执行',
            source_ids: [t.id],
            id: t.id,
            status: t.status,
            priority: t.priority,
            due_date: t.due_date,
          })),
        },
      ],
      advice: cfg.key ? [] : ['接入大模型 API Key 后，可自动去重合并并生成建议下一步。'],
      degraded: !cfg.key,
      storage: store.storageMode(),
    });
  }

  const context = formatItems(todos.slice(0, 60));
  let data;
  try {
    data = await chatJson({
      messages: [
        { role: 'system', content: TODO_SYSTEM },
        { role: 'user', content: todoUser(context) },
      ],
      temperature: 0.2,
      cfg,
    });
  } catch {
    data = null;
  }

  const byId = new Map(todos.map((t) => [t.id, t]));
  const groups = (Array.isArray(data?.groups) ? data.groups : []).map((g) => ({
    level: String(g.level || 'P1'),
    items: (Array.isArray(g.items) ? g.items : []).map((it) => {
      const matched = (it.source_ids || []).map(String).map((id) => byId.get(id)).filter(Boolean);
      return {
        title: it.title,
        reason: it.reason || '',
        next_step: it.next_step || '',
        source_ids: (it.source_ids || []).map(String),
        status: matched[0]?.status ?? 'open',
        priority: matched[0]?.priority ?? null,
        due_date: matched[0]?.due_date ?? null,
        id: matched[0]?.id ?? null,
      };
    }),
  }));

  return ok(res, {
    groups: groups.length
      ? groups
      : [
          {
            level: 'P1',
            items: todos.map((t) => ({
              title: t.title,
              reason: '来自你的记录',
              next_step: '直接开始执行',
              source_ids: [t.id],
              id: t.id,
              status: t.status,
              priority: t.priority,
              due_date: t.due_date,
            })),
          },
        ],
    advice: Array.isArray(data?.advice) ? data.advice.slice(0, 3) : [],
    storage: store.storageMode(),
  });
});
