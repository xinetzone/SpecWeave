/**
 * 轻量中文/英文混合文本相似度：CJK 二元组 + 英文词元，余弦相似 + 标签加成。
 * 免向量、免外部依赖，适合个人规模（数千条）的关联与检索排序。
 */

const STOP = new Set(['的', '了', '是', '在', '我', '有', '和', '就', '不', '也', '要', '一个']);

export function tokens(text) {
  const out = [];
  const lower = String(text || '').toLowerCase();

  for (const m of lower.matchAll(/[a-z0-9][a-z0-9_.-]{1,}/g)) out.push(m[0]);

  const cjkOnly = lower.replace(/[^\u4e00-\u9fa5]+/g, ' ');
  for (const seg of cjkOnly.split(/\s+/)) {
    if (!seg) continue;
    if (seg.length === 1) {
      out.push(seg);
      continue;
    }
    for (let i = 0; i < seg.length - 1; i += 1) out.push(seg.slice(i, i + 2));
  }
  return out.filter((t) => !STOP.has(t));
}

function counts(list) {
  const m = new Map();
  for (const t of list) m.set(t, (m.get(t) || 0) + 1);
  return m;
}

export function itemText(item) {
  return [item.title, item.summary, item.content, (item.tags || []).join(' ')]
    .filter(Boolean)
    .join('\n');
}

/** 余弦相似度（0~1） */
export function cosine(a, b) {
  const ca = counts(tokens(a));
  const cb = counts(tokens(b));
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (const [, v] of ca) na += v * v;
  for (const [, v] of cb) nb += v * v;
  for (const [k, v] of ca) dot += v * (cb.get(k) || 0);
  if (!na || !nb) return 0;
  return dot / Math.sqrt(na * nb);
}

function tagOverlap(a, b) {
  const ta = new Set((a.tags || []).map((t) => String(t).toLowerCase()));
  const tb = new Set((b.tags || []).map((t) => String(t).toLowerCase()));
  if (!ta.size || !tb.size) return 0;
  let hit = 0;
  for (const t of ta) if (tb.has(t)) hit += 1;
  return hit / Math.min(ta.size, tb.size);
}

/** 条目间综合相关度：文本余弦 0.8 + 标签重合 0.2 */
export function relatedness(a, b) {
  return cosine(itemText(a), itemText(b)) * 0.8 + tagOverlap(a, b) * 0.2;
}

/** 给查询词对条目的匹配打分（含标题/标签加权） */
export function matchScore(item, query) {
  const q = String(query || '').trim();
  if (!q) return 0;
  const base = cosine(itemText(item), q);
  const titleBoost = cosine(String(item.title || ''), q) * 0.5;
  const tagBoost = tagOverlap({ tags: item.tags }, { tags: tokens(q) }) * 0.4;
  return base + titleBoost + tagBoost;
}

/** 生成命中片段，便于列表展示上下文 */
export function snippet(item, query, len = 90) {
  const text = String(item.content || item.summary || item.title || '').replace(/\s+/g, ' ');
  if (!text) return '';
  const q = String(query || '').trim();
  if (!q) return text.slice(0, len);
  const key = tokens(q)[0];
  const at = key ? text.toLowerCase().indexOf(key) : -1;
  if (at < 0) return text.slice(0, len);
  const start = Math.max(0, at - 30);
  return `${start > 0 ? '…' : ''}${text.slice(start, start + len)}${start + len < text.length ? '…' : ''}`;
}

/** 取与目标条目最相关的 N 条（排除自身与已存在关联） */
export function topRelated(target, items, { limit = 5, threshold = 0.1 } = {}) {
  return items
    .filter((it) => it.id !== target.id)
    .map((it) => ({ item: it, score: relatedness(target, it) }))
    .filter((r) => r.score >= threshold)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}
