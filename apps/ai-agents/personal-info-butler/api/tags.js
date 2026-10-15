import { withApi, ok } from './_lib/http.js';
import * as store from './_lib/store.js';

export default withApi(async (req, res) => {
  if (req.method !== 'GET') return ok(res, { tags: [] });

  const items = await store.listItems({ limit: 500 });
  const counter = new Map();
  for (const item of items) {
    for (const tag of item.tags || []) {
      counter.set(tag, (counter.get(tag) || 0) + 1);
    }
  }
  const tags = [...counter.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));

  const stats = {
    total: items.length,
    idea: items.filter((i) => i.kind === 'idea').length,
    material: items.filter((i) => i.kind === 'material').length,
    todo: items.filter((i) => i.kind === 'todo').length,
    openTodo: items.filter((i) => i.kind === 'todo' && i.status !== 'done').length,
  };

  return ok(res, { tags, stats, storage: store.storageMode() });
});
