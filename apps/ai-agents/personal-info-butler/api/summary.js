import { withApi, ok, fail, getQuery, readBody } from './_lib/http.js';
import { llmConfigFrom } from './_lib/config.js';
import * as store from './_lib/store.js';
import { chatText } from './_lib/llm.js';
import { SUMMARY_SYSTEM, summaryUser } from './_lib/prompts.js';
import { formatItems } from './_lib/pipeline.js';
import { newId, nowIso } from './_lib/pipeline.js';

export default withApi(async (req, res) => {
  if (req.method === 'GET') {
    const limit = Math.min(Math.max(Number.parseInt(getQuery(req).get('limit') || '20', 10) || 20, 1), 50);
    return ok(res, { summaries: await store.listSummaries({ limit }), storage: store.storageMode() });
  }

  if (req.method !== 'POST') return fail(res, 405, '仅支持 GET/POST');

  const body = await readBody(req);
  const cfg = llmConfigFrom(req);
  const days = Math.min(Math.max(Number.parseInt(body.days, 10) || 7, 1), 365);
  const since = Date.now() - days * 86400000;

  const all = await store.listItems({ limit: 500 });
  const items = all.filter((i) => new Date(i.created_at).getTime() >= since);

  if (!items.length) {
    return fail(res, 400, `最近 ${days} 天没有记录，先去「录入」写点什么吧`);
  }

  if (!cfg.key) {
    return ok(res, {
      markdown: `## 阶段概览（未接入大模型 · 统计直出）\n\n- 最近 ${days} 天共 **${items.length}** 条记录\n- 想法 ${items.filter((i) => i.kind === 'idea').length} 条 ｜ 资料 ${items.filter((i) => i.kind === 'material').length} 条 ｜ 待办 ${items.filter((i) => i.kind === 'todo').length} 条\n\n> 接入大模型 API Key 后可生成完整的阶段总结与后续行动建议。`,
      days,
      itemCount: items.length,
      degraded: true,
    });
  }

  const markdown = await chatText({
    messages: [
      { role: 'system', content: SUMMARY_SYSTEM },
      { role: 'user', content: summaryUser(days, formatItems(items.slice(0, 120))) },
    ],
    temperature: 0.4,
    cfg,
  });

  const row = {
    id: newId(),
    range_days: days,
    item_count: items.length,
    content_md: markdown,
    created_at: nowIso(),
  };
  if (body.save !== false) await store.createSummary(row);

  return ok(res, {
    markdown,
    days,
    itemCount: items.length,
    summaryId: body.save === false ? null : row.id,
    storage: store.storageMode(),
  });
});
