/**
 * 存储层：Supabase（云端 PostgreSQL via PostgREST）为主，未配置时回退内存存储。
 * 两套驱动暴露同一组异步方法，上层业务无感知。
 */
import { serverConfig } from './config.js';

const TABLE_ITEMS = 'items';
const TABLE_LINKS = 'item_links';
const TABLE_SUMMARIES = 'summaries';

/** 内存回退存储（进程内，重启即失；仅用于未配置云端时的本地演示） */
const memory = { items: new Map(), links: [], summaries: [] };

export function usingCloud() {
  return Boolean(serverConfig.supabaseUrl && serverConfig.supabaseKey);
}

export function storageMode() {
  return usingCloud() ? 'supabase' : 'memory';
}

function byCreatedDesc(a, b) {
  return String(b.created_at || '').localeCompare(String(a.created_at || ''));
}

async function rest(path, { method = 'GET', search = '', body, prefer } = {}) {
  const base = serverConfig.supabaseUrl.replace(/\/+$/, '');
  const url = `${base}/rest/v1/${path}${search ? `?${search}` : ''}`;
  const headers = {
    apikey: serverConfig.supabaseKey,
    Authorization: `Bearer ${serverConfig.supabaseKey}`,
    Accept: 'application/json',
  };
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (prefer) headers['Prefer'] = prefer;

  const res = await fetch(url, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = (await res.text().catch(() => '')).slice(0, 300);
    throw new Error(`云端存储请求失败（${res.status}）：${detail}`);
  }
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

const search = (params) => new URLSearchParams(params).toString();

// ------------------------------------------------------------------ items

export async function listItems({ limit = 500 } = {}) {
  if (!usingCloud()) {
    return [...memory.items.values()].sort(byCreatedDesc).slice(0, limit);
  }
  const rows = await rest(TABLE_ITEMS, {
    search: search({ select: '*', order: 'created_at.desc', limit: String(limit) }),
  });
  return Array.isArray(rows) ? rows : [];
}

export async function getItem(id) {
  if (!usingCloud()) return memory.items.get(id) || null;
  const rows = await rest(TABLE_ITEMS, { search: search({ select: '*', id: `eq.${id}` }) });
  return Array.isArray(rows) && rows.length ? rows[0] : null;
}

export async function createItem(item) {
  if (!usingCloud()) {
    memory.items.set(item.id, { ...item });
    return { ...item };
  }
  const rows = await rest(TABLE_ITEMS, {
    method: 'POST',
    body: item,
    prefer: 'return=representation',
  });
  return Array.isArray(rows) && rows.length ? rows[0] : item;
}

export async function updateItem(id, patch) {
  const next = { ...patch, updated_at: new Date().toISOString() };
  if (!usingCloud()) {
    const cur = memory.items.get(id);
    if (!cur) return null;
    const merged = { ...cur, ...next };
    memory.items.set(id, merged);
    return merged;
  }
  const rows = await rest(TABLE_ITEMS, {
    method: 'PATCH',
    search: search({ id: `eq.${id}` }),
    body: next,
    prefer: 'return=representation',
  });
  return Array.isArray(rows) && rows.length ? rows[0] : null;
}

export async function deleteItem(id) {
  if (!usingCloud()) {
    memory.items.delete(id);
    return true;
  }
  await rest(TABLE_ITEMS, { method: 'DELETE', search: search({ id: `eq.${id}` }) });
  return true;
}

// ------------------------------------------------------------------ links

export async function listLinks() {
  if (!usingCloud()) return [...memory.links];
  const rows = await rest(TABLE_LINKS, { search: search({ select: '*' }) });
  return Array.isArray(rows) ? rows : [];
}

export async function linksOf(id) {
  if (!usingCloud()) return memory.links.filter((l) => l.from_id === id || l.to_id === id);
  const s = search({ select: '*', or: `(from_id.eq.${id},to_id.eq.${id})` });
  const rows = await rest(TABLE_LINKS, { search: s });
  return Array.isArray(rows) ? rows : [];
}

/** 用新计算的关联关系整体替换某条目的出边（保证重复录入幂等） */
export async function replaceLinks(fromId, links) {
  if (!usingCloud()) {
    memory.links = memory.links.filter((l) => l.from_id !== fromId);
    for (const l of links) memory.links.push({ id: l.id, ...l });
    return links;
  }
  await rest(TABLE_LINKS, { method: 'DELETE', search: search({ from_id: `eq.${fromId}` }) });
  if (!links.length) return [];
  const rows = await rest(TABLE_LINKS, {
    method: 'POST',
    body: links,
    prefer: 'return=representation',
  });
  return Array.isArray(rows) ? rows : links;
}

// -------------------------------------------------------------- summaries

export async function createSummary(row) {
  if (!usingCloud()) {
    memory.summaries.push({ ...row });
    return { ...row };
  }
  const rows = await rest(TABLE_SUMMARIES, {
    method: 'POST',
    body: row,
    prefer: 'return=representation',
  });
  return Array.isArray(rows) && rows.length ? rows[0] : row;
}

export async function listSummaries({ limit = 20 } = {}) {
  if (!usingCloud()) {
    return [...memory.summaries].sort(byCreatedDesc).slice(0, limit);
  }
  const rows = await rest(TABLE_SUMMARIES, {
    search: search({ select: '*', order: 'created_at.desc', limit: String(limit) }),
  });
  return Array.isArray(rows) ? rows : [];
}
