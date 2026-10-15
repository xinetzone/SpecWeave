/* 管理后台：总览指标 / 意图分布 / 会话明细 / 知识库维护 */

const INTENT_LABELS = {
  refund: '退款退货',
  order_query: '订单查询',
  tech_support: '技术支持',
  human: '转人工',
  smalltalk: '寒暄问候',
  other: '通用咨询'
};

let token = localStorage.getItem('cs_admin_token') || '';

function api(path, options) {
  const opts = Object.assign({ headers: { 'X-Admin-Token': token } }, options || {});
  return fetch(path, opts).then(async (resp) => {
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(data.message || data.error || ('HTTP ' + resp.status));
    return data;
  });
}

function setStatus(text, ok) {
  const badge = document.getElementById('status-badge');
  badge.className = 'badge ' + (ok ? 'ok' : 'warn');
  badge.textContent = text;
}

function renderKpis(stats) {
  const cards = [
    ['会话总数', stats.sessions],
    ['消息总数', stats.messages],
    ['转人工率', stats.transfer_rate + '%'],
    ['平均满意度', stats.avg_rating || '—'],
    ['问题解决率', stats.resolved_rate + '%'],
    ['评价数', stats.feedback_count]
  ];
  document.getElementById('kpis').innerHTML = cards.map(([label, num]) =>
    `<div class="kpi"><div class="num">${num}</div><div class="label">${label}</div></div>`
  ).join('');

  const hint = document.getElementById('storage-hint');
  hint.textContent = `存储后端：${stats.backend}${stats.degraded ? '（已降级，最近一次错误：' + (stats.last_error || '未知') + '）' : ''} · 大模型：${stats.llm_ready ? '已接入' : '未接入'} · 知识库条目：${stats.faq_count}`;
}

function renderBars(dist) {
  const entries = Object.entries(dist || {});
  const max = Math.max(1, ...entries.map(([, v]) => v));
  document.getElementById('bars').innerHTML = entries.length
    ? entries.map(([k, v]) => `
      <div class="bar-row">
        <span>${INTENT_LABELS[k] || k}</span>
        <div class="bar"><i style="width:${Math.round(100 * v / max)}%"></i></div>
        <span class="hint">${v}</span>
      </div>`).join('')
    : '<div class="empty">暂无数据</div>';
}

function renderSessions(rows) {
  const tbody = document.getElementById('sessions');
  document.getElementById('sessions-empty').style.display = rows.length ? 'none' : 'block';
  tbody.innerHTML = rows.map(s => `
    <tr class="link" data-id="${s.id}">
      <td class="mono">${s.id}</td>
      <td>${INTENT_LABELS[s.last_intent] || '—'}</td>
      <td>${s.status}</td>
      <td>${s.transferred ? '<span class="tag human">已转人工</span>' : '—'}</td>
      <td class="hint">${(s.updated_at || '').replace('T', ' ').slice(0, 19)}</td>
    </tr>`).join('');
  tbody.querySelectorAll('tr.link').forEach(tr => {
    tr.addEventListener('click', () => openDetail(tr.dataset.id));
  });
}

function renderFaq(rows) {
  document.getElementById('faq-list').innerHTML = (rows || []).map(f => `
    <tr>
      <td>${INTENT_LABELS[f.category] || f.category}</td>
      <td>${escapeHtml(f.question)}</td>
      <td class="hint">${escapeHtml(f.answer)}</td>
    </tr>`).join('');
}

function escapeHtml(text) {
  return String(text || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function openDetail(id) {
  const panel = document.getElementById('detail');
  panel.classList.add('open');
  document.getElementById('detail-id').textContent = id;
  document.getElementById('detail-lines').innerHTML = '<div class="hint">加载中…</div>';
  document.getElementById('detail-feedback').innerHTML = '';

  api('/api/admin/sessions/' + encodeURIComponent(id)).then(data => {
    document.getElementById('detail-lines').innerHTML = data.messages.map(m => `
      <div class="line ${m.role}">
        <div class="who">${m.role === 'user' ? '用户' : '客服'} · ${INTENT_LABELS[m.intent] || ''} · ${m.source}${m.needs_human ? ' · 已转人工' : ''}</div>
        <div>${escapeHtml(m.content)}</div>
      </div>`).join('') || '<div class="empty">无消息</div>';

    document.getElementById('detail-feedback').innerHTML = data.feedback.length
      ? `<h3 style="margin-top:16px">满意度</h3>` + data.feedback.map(f =>
          `<div class="line"><div class="who">评分 ${f.rating} 星 · ${f.resolved ? '已解决' : '未解决'}</div><div>${escapeHtml(f.comment) || '—'}</div></div>`
        ).join('')
      : '';
  }).catch(err => {
    document.getElementById('detail-lines').innerHTML = '<div class="error">' + err.message + '</div>';
  });
}

document.getElementById('btn-close-detail').addEventListener('click', () => {
  document.getElementById('detail').classList.remove('open');
});

function loadAll() {
  const q = document.getElementById('q').value.trim();
  Promise.all([
    api('/api/admin/overview'),
    api('/api/admin/sessions?limit=100' + (q ? '&q=' + encodeURIComponent(q) : '')),
    api('/api/admin/faq')
  ]).then(([stats, sessions, faq]) => {
    setStatus('已登录 · ' + stats.backend, !stats.degraded);
    renderKpis(stats);
    renderBars(stats.intent_distribution);
    renderSessions(sessions.sessions || []);
    renderFaq(faq.faq || []);
  }).catch(err => {
    setStatus('加载失败', false);
    document.getElementById('storage-hint').textContent = err.message;
  });
}

document.getElementById('btn-login').addEventListener('click', () => {
  token = document.getElementById('token').value.trim();
  if (!token) return;
  localStorage.setItem('cs_admin_token', token);
  api('/api/admin/overview').then(() => {
    document.getElementById('login-card').style.display = 'none';
    document.getElementById('dash').style.display = '';
    setStatus('已登录', true);
    loadAll();
  }).catch(err => {
    document.getElementById('login-error').textContent = err.message;
  });
});

document.getElementById('btn-refresh').addEventListener('click', loadAll);
document.getElementById('btn-search').addEventListener('click', loadAll);
document.getElementById('q').addEventListener('keydown', (e) => { if (e.key === 'Enter') loadAll(); });

document.getElementById('btn-faq').addEventListener('click', () => {
  const question = document.getElementById('faq-q').value.trim();
  const answer = document.getElementById('faq-a').value.trim();
  if (!question || !answer) return;
  api('/api/admin/faq', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': token },
    body: JSON.stringify({
      question,
      answer,
      keywords: document.getElementById('faq-k').value.trim(),
      category: document.getElementById('faq-c').value
    })
  }).then(() => {
    document.getElementById('faq-q').value = '';
    document.getElementById('faq-a').value = '';
    document.getElementById('faq-k').value = '';
    loadAll();
  }).catch(err => alert(err.message));
});

if (token) {
  api('/api/admin/overview').then(() => {
    document.getElementById('login-card').style.display = 'none';
    document.getElementById('dash').style.display = '';
    loadAll();
  }).catch(() => setStatus('令牌失效', false));
}
