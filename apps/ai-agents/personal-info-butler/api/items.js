import { withApi, ok, fail, getQuery, readBody } from './_lib/http.js';
import { llmConfigFrom } from './_lib/config.js';
import { storageMode } from './_lib/store.js';
import * as store from './_lib/store.js';
import { capture } from './_lib/pipeline.js';
import { matchScore, snippet } from './_lib/similarity.js';

const clamp = (n, min, max) => Math.min(max, Math.max(min, n));

export default withApi(async (req, res) => {
  if (req.method === 'POST') {
    const body = await readBody(req);
    const cfg = llmConfigFrom(req);
    const result = await capture({
      text: body.text,
      kind: body.kind,
      tags: body.tags,
      source: body.source,
      cfg,
    });
    return ok(res, { ...result, storage: storageMode() });
  }

  if (req.method === 'GET') {
    const q = getQuery(req);
    const keyword = (q.get('q') || '').trim();
    const kind = (q.get('kind') || '').trim();
    const tag = (q.get('tag') || '').trim();
    const status = (q.get('status') || '').trim();
    const limit = clamp(Number.parseInt(q.get('limit') || '50', 10) || 50, 1, 200);

    let items = await store.listItems({ limit: 500 });
    if (kind) items = items.filter((i) => i.kind === kind);
    if (status) items = items.filter((i) => i.status === status);
    if (tag) items = items.filter((i) => (i.tags || []).includes(tag));

    if (keyword) {
      items = items
        .map((i) => ({ item: i, score: matchScore(i, keyword) }))
        .filter((r) => r.score > 0.02)
        .sort((a, b) => b.score - a.score)
        .map((r) => ({ ...r.item, _score: Number(r.score.toFixed(3)), _snippet: snippet(r.item, keyword) }));
    }

    return ok(res, {
      items: items.slice(0, limit),
      total: items.length,
      keyword,
      storage: storageMode(),
    });
  }

  return fail(res, 405, '方法不被支持');
});
