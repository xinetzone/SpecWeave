/**
 * 业务流水线：录入归类 → 生成关联 → 派生待办。
 */
import { chatJson, MissingLLMError } from './llm.js';
import { CLASSIFY_SYSTEM, classifyUser, RELATE_SYSTEM, relateUser } from './prompts.js';
import { topRelated } from './similarity.js';
import * as store from './store.js';

export const newId = () => crypto.randomUUID();
export const nowIso = () => new Date().toISOString();

const TODO_HINT =
  /(待办|todo|记得|别忘|要做|需要|安排|计划|明天|下周|本周|截止|deadline|跟进|提交|反馈|回复|准备|约|开会)/i;
const MATERIAL_HINT = /(https?:\/\/|资料|参考|链接|文档|文章|摘录|引用|来源|出处|收藏)/i;

const uniq = (arr) => [...new Set(arr.filter(Boolean).map((x) => String(x).trim()))];

/** 未接入大模型时的启发式归类，保证应用零配置可用 */
export function heuristicClassify(text) {
  const firstLine = String(text).split(/\r?\n/).find((l) => l.trim()) || '';
  const title = firstLine.replace(/\s+/g, ' ').trim().slice(0, 20) || '未命名记录';
  let kind = 'idea';
  if (MATERIAL_HINT.test(text)) kind = 'material';
  if (TODO_HINT.test(text)) kind = 'todo';
  const tags = [];
  if (kind === 'todo') tags.push('待办');
  if (MATERIAL_HINT.test(text)) tags.push('资料');
  const urls = String(text).match(/https?:\/\/\S+/g);
  if (urls) tags.push('链接');
  return {
    kind,
    title,
    summary: String(text).replace(/\s+/g, ' ').trim().slice(0, 60),
    tags: tags.length ? tags : ['未分类'],
    priority: null,
    due_date: null,
    todos: [],
    ai: false,
  };
}

/** 调用大模型做结构化归类，失败或缺失密钥时降级到启发式 */
export async function classify(text, cfg) {
  if (!cfg?.key) return heuristicClassify(text);
  try {
    const data = await chatJson({
      messages: [
        { role: 'system', content: CLASSIFY_SYSTEM },
        { role: 'user', content: classifyUser(text) },
      ],
      temperature: 0.2,
      cfg,
    });
    const kind = ['idea', 'material', 'todo'].includes(data.kind) ? data.kind : 'idea';
    const norm = (v) => (v === null || v === undefined || v === 'null' || v === '' ? null : String(v));
    return {
      kind,
      title: String(data.title || '').slice(0, 60) || heuristicClassify(text).title,
      summary: String(data.summary || '').slice(0, 300),
      tags: uniq(Array.isArray(data.tags) ? data.tags : []).slice(0, 6),
      priority: ['high', 'medium', 'low'].includes(data.priority) ? data.priority : null,
      due_date: /^\d{4}-\d{2}-\d{2}$/.test(String(data.due_date || '')) ? data.due_date : null,
      todos: (Array.isArray(data.todos) ? data.todos : [])
        .filter((t) => t && t.title)
        .slice(0, 5)
        .map((t) => ({
          title: String(t.title).slice(0, 120),
          due_date: /^\d{4}-\d{2}-\d{2}$/.test(String(t.due_date || '')) ? t.due_date : null,
          priority: ['high', 'medium', 'low'].includes(t.priority) ? t.priority : 'medium',
        })),
      ai: true,
    };
  } catch (err) {
    if (err instanceof MissingLLMError) throw err;
    return { ...heuristicClassify(text), degraded: true };
  }
}

/** 关联分析：启发式候选 + 大模型裁决（无密钥时纯启发式） */
export async function relate(target, items, cfg) {
  const heuristic = topRelated(target, items, { limit: 8, threshold: 0.08 });
  if (!heuristic.length) return [];
  const fallback = heuristic.slice(0, 5).map((r) => ({ id: r.item.id, score: r.score, reason: '主题或关键词相近' }));
  if (!cfg?.key) return fallback;
  try {
    const candidates = heuristic
      .map((r) => `- id=${r.item.id} | ${r.item.title} :: ${String(r.item.summary || r.item.content || '').slice(0, 80)}`)
      .join('\n');
    const data = await chatJson({
      messages: [
        { role: 'system', content: RELATE_SYSTEM },
        {
          role: 'user',
          content: relateUser(
            `${target.title}\n${target.summary || target.content}`,
            candidates
          ),
        },
      ],
      temperature: 0.2,
      cfg,
    });
    const picked = new Map(
      (Array.isArray(data.related) ? data.related : []).map((r) => [String(r.id), String(r.reason || '').slice(0, 40)])
    );
    const out = heuristic
      .filter((r) => picked.has(r.item.id))
      .map((r) => ({ id: r.item.id, score: r.score, reason: picked.get(r.item.id) || '内容相关' }));
    return out.length ? out.slice(0, 5) : fallback;
  } catch {
    return fallback;
  }
}

/**
 * 录入一条记录：结构化 → 落库 → 派生待办 → 计算关联。
 * 返回 { item, todos, related }
 */
export async function capture({ text, kind, tags = [], source = 'web', cfg }) {
  const raw = String(text || '').trim();
  if (!raw) throw new Error('内容不能为空');

  const parsed = await classify(raw, cfg);
  const finalKind = ['idea', 'material', 'todo'].includes(kind) ? kind : parsed.kind;

  const item = {
    id: newId(),
    kind: finalKind,
    title: parsed.title,
    content: raw,
    summary: parsed.summary,
    tags: uniq([...(Array.isArray(tags) ? tags : []), ...parsed.tags]),
    status: 'open',
    priority: parsed.priority,
    due_date: parsed.due_date,
    source: source || 'web',
    parent_id: null,
    created_at: nowIso(),
    updated_at: nowIso(),
  };
  await store.createItem(item);

  const todos = [];
  for (const t of parsed.todos || []) {
    const child = {
      id: newId(),
      kind: 'todo',
      title: t.title,
      content: t.title,
      summary: '',
      tags: item.tags.slice(0, 3),
      status: 'open',
      priority: t.priority,
      due_date: t.due_date,
      source: 'auto',
      parent_id: item.id,
      created_at: nowIso(),
      updated_at: nowIso(),
    };
    await store.createItem(child);
    todos.push(child);
  }

  const all = await store.listItems({ limit: 300 });
  const rel = await relate(item, all, cfg);
  const links = rel.map((r) => ({
    id: newId(),
    from_id: item.id,
    to_id: r.id,
    score: r.score,
    reason: r.reason,
    created_at: nowIso(),
  }));
  await store.replaceLinks(item.id, links);

  const byId = new Map(all.map((i) => [i.id, i]));
  return {
    item,
    todos,
    related: rel
      .map((r) => ({ ...r, item: byId.get(r.id) }))
      .filter((r) => r.item)
      .map((r) => ({
        id: r.id,
        score: Number(r.score.toFixed(3)),
        reason: r.reason,
        title: r.item.title,
        kind: r.item.kind,
      })),
    ai: Boolean(parsed.ai),
  };
}

/** 把条目序列化成喂给大模型的紧凑文本 */
export function formatItems(items) {
  return items
    .map(
      (it, i) =>
        `[${i + 1}] id=${it.id} ｜类型=${it.kind} ｜标签=${(it.tags || []).join('/') || '-'} ｜状态=${it.status}\n标题：${it.title}\n内容：${String(it.content || it.summary || '').slice(0, 900)}`
    )
    .join('\n\n');
}
