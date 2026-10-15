import { withApi, ok, fail, readBody } from './_lib/http.js';
import { llmConfigFrom } from './_lib/config.js';
import * as store from './_lib/store.js';
import { chatText } from './_lib/llm.js';
import { ASK_SYSTEM, askUser } from './_lib/prompts.js';
import { matchScore } from './_lib/similarity.js';

export default withApi(async (req, res) => {
  if (req.method !== 'POST') return fail(res, 405, '仅支持 POST');

  const body = await readBody(req);
  const question = String(body.question || '').trim();
  if (!question) return fail(res, 400, '问题不能为空');

  const topK = Math.min(Math.max(Number.parseInt(body.topK, 10) || 8, 1), 20);
  const cfg = llmConfigFrom(req);

  const items = await store.listItems({ limit: 500 });
  const hits = items
    .map((i) => ({ item: i, score: matchScore(i, question) }))
    .filter((r) => r.score > 0.02)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);

  const citations = hits.map((r, idx) => ({
    index: idx + 1,
    id: r.item.id,
    title: r.item.title,
    kind: r.item.kind,
    score: Number(r.score.toFixed(3)),
  }));

  if (!cfg.key) {
    return ok(res, {
      answer:
        '未接入大模型，暂时只能做关键词匹配。以下条目与你的问题相关，接入 API Key 后可直接给出带引用的回答。',
      citations,
      degraded: true,
    });
  }

  const chunks = hits
    .map((r, idx) => `[${idx + 1}] ${r.item.title}\n${String(r.item.content || r.item.summary || '').slice(0, 900)}`)
    .join('\n\n');

  const answer = await chatText({
    messages: [
      { role: 'system', content: ASK_SYSTEM },
      { role: 'user', content: askUser(question, chunks || '（无相关条目）') },
    ],
    temperature: 0.3,
    cfg,
  });

  return ok(res, { answer, citations, storage: store.storageMode() });
});
