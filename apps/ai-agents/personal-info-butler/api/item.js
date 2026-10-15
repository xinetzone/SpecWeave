import { withApi, ok, fail, getQuery, readBody } from './_lib/http.js';
import * as store from './_lib/store.js';

const ALLOWED_PATCH = ['kind', 'title', 'content', 'summary', 'tags', 'status', 'priority', 'due_date'];

export default withApi(async (req, res) => {
  const id = (getQuery(req).get('id') || '').trim();
  if (!id) return fail(res, 400, '缺少 id 参数');

  if (req.method === 'GET') {
    const item = await store.getItem(id);
    if (!item) return fail(res, 404, '条目不存在');
    const links = await store.linksOf(id);
    const others = await store.listItems({ limit: 500 });
    const byId = new Map(others.map((i) => [i.id, i]));
    const related = links
      .map((l) => {
        const otherId = l.from_id === id ? l.to_id : l.from_id;
        const other = byId.get(otherId);
        return other
          ? { id: otherId, title: other.title, kind: other.kind, score: l.score, reason: l.reason }
          : null;
      })
      .filter(Boolean);
    const children = others.filter((i) => i.parent_id === id);
    return ok(res, { item, related, children, storage: store.storageMode() });
  }

  if (req.method === 'PATCH') {
    const body = await readBody(req);
    const patch = {};
    for (const key of ALLOWED_PATCH) {
      if (body[key] !== undefined) patch[key] = body[key];
    }
    if (!Object.keys(patch).length) return fail(res, 400, '没有可更新的字段');
    const item = await store.updateItem(id, patch);
    if (!item) return fail(res, 404, '条目不存在');
    return ok(res, { item });
  }

  if (req.method === 'DELETE') {
    await store.deleteItem(id);
    return ok(res, { id });
  }

  return fail(res, 405, '方法不被支持');
});
