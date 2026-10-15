import { withApi, ok, fail, readBody } from './_lib/http.js';
import { llmConfigFrom } from './_lib/config.js';
import * as store from './_lib/store.js';
import { chatText } from './_lib/llm.js';
import { EXTRACT_SYSTEM, extractUser } from './_lib/prompts.js';
import { formatItems } from './_lib/pipeline.js';
import { matchScore } from './_lib/similarity.js';

export default withApi(async (req, res) => {
  if (req.method !== 'POST') return fail(res, 405, '仅支持 POST');

  const body = await readBody(req);
  const cfg = llmConfigFrom(req);
  const limit = Math.min(Math.max(Number.parseInt(body.limit, 10) || 30, 1), 100);

  let items = await store.listItems({ limit: 500 });

  if (Array.isArray(body.ids) && body.ids.length) {
    const wanted = new Set(body.ids.map(String));
    items = items.filter((i) => wanted.has(String(i.id)));
  } else if (body.q) {
    const keyword = String(body.q);
    items = items
      .map((i) => ({ item: i, score: matchScore(i, keyword) }))
      .filter((r) => r.score > 0.02)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map((r) => r.item);
  } else if (body.days) {
    const since = Date.now() - Number(body.days) * 86400000;
    items = items.filter((i) => new Date(i.created_at).getTime() >= since);
  }

  items = items.slice(0, limit);
  if (!items.length) return fail(res, 400, '没有可提取的条目');

  if (!cfg.key) {
    const fallback = items
      .map((i) => `- **${i.title}**（${i.kind}）${i.summary || String(i.content || '').slice(0, 80)}`)
      .join('\n');
    return ok(res, {
      markdown: `## 重点信息（未接入大模型，按摘要直出）\n\n${fallback}`,
      count: items.length,
      degraded: true,
    });
  }

  const markdown = await chatText({
    messages: [
      { role: 'system', content: EXTRACT_SYSTEM },
      { role: 'user', content: extractUser(formatItems(items)) },
    ],
    temperature: 0.2,
    cfg,
  });

  return ok(res, { markdown, count: items.length, storage: store.storageMode() });
});
