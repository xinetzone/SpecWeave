/* 智能客服对话端：多轮对话 + 意图标签 + 知识库引用 + 满意度评价 + BYOK */

const stream = document.getElementById('stream');
const input = document.getElementById('input');
const btnSend = document.getElementById('btn-send');
const btnHuman = document.getElementById('btn-human');
const badge = document.getElementById('status-badge');

let sessionId = '';
let pending = false;

const byok = {
  get() {
    try { return JSON.parse(localStorage.getItem('cs_byok') || '{}'); } catch { return {}; }
  },
  set(data) {
    localStorage.setItem('cs_byok', JSON.stringify(data));
  },
  clear() { localStorage.removeItem('cs_byok'); }
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function addMessage(role, content, extras) {
  extras = extras || {};
  const wrap = el('div', 'msg ' + (role === 'user' ? 'user' : ''));
  const avatar = el('div', 'avatar ' + (role === 'user' ? 'me' : 'bot'), role === 'user' ? '我' : 'AI');
  const box = el('div');
  box.appendChild(el('div', 'bubble', content));

  const meta = el('div', 'meta');
  if (extras.intent_label) meta.appendChild(el('span', 'tag', '意图：' + extras.intent_label));
  if (extras.source === 'faq') meta.appendChild(el('span', 'tag', '知识库直答'));
  if (extras.source === 'human') meta.appendChild(el('span', 'tag human', '已转人工'));
  if (extras.needs_human && extras.ticket_id) meta.appendChild(el('span', 'tag human', '工单 ' + extras.ticket_id));
  if (extras.latency_ms) meta.appendChild(el('span', 'hint', extras.latency_ms + 'ms'));
  if (meta.childNodes.length) box.appendChild(meta);

  if (extras.faq && extras.faq.length) {
    const refs = el('div', 'refs');
    refs.textContent = '参考知识：' + extras.faq.map(f => f.question).join(' / ');
    box.appendChild(refs);
  }

  wrap.appendChild(avatar);
  wrap.appendChild(box);
  stream.appendChild(wrap);
  stream.scrollTop = stream.scrollHeight;
  return wrap;
}

async function send(text) {
  text = (text || '').trim();
  if (!text || pending) return;
  pending = true;
  btnSend.disabled = true;

  addMessage('user', text);
  input.value = '';
  const typing = addMessage('assistant', '正在思考…');

  try {
    const payload = { message: text };
    if (sessionId) payload.session_id = sessionId;
    const cfg = byok.get();
    if (cfg.base) payload.llm_base_url = cfg.base;
    if (cfg.key) payload.llm_api_key = cfg.key;
    if (cfg.model) payload.llm_model = cfg.model;

    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    sessionId = data.session_id || sessionId;
    typing.remove();
    addMessage('assistant', data.reply || '（无回复）', data);
  } catch (err) {
    typing.remove();
    addMessage('assistant', '网络异常，请稍后重试：' + err, {});
  } finally {
    pending = false;
    btnSend.disabled = false;
    input.focus();
  }
}

btnSend.addEventListener('click', () => send(input.value));
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input.value); }
});
btnHuman.addEventListener('click', () => send('转人工'));
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => send(chip.dataset.q));
});

/* 满意度评价 */
let rating = 0;
document.querySelectorAll('#stars .star').forEach(star => {
  star.addEventListener('click', () => {
    rating = parseInt(star.dataset.v, 10);
    document.querySelectorAll('#stars .star').forEach(s => {
      s.classList.toggle('on', parseInt(s.dataset.v, 10) <= rating);
    });
  });
});
document.getElementById('btn-rate').addEventListener('click', async () => {
  const hint = document.getElementById('rate-hint');
  if (!rating) { hint.textContent = '请先点选星星再提交'; return; }
  try {
    const resp = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rating,
        resolved: rating >= 4,
        comment: document.getElementById('comment').value || '',
        session_id: sessionId
      })
    });
    const data = await resp.json();
    hint.textContent = data.ok ? '感谢您的评价！' : (data.message || '提交失败');
  } catch (err) {
    hint.textContent = '提交失败：' + err;
  }
});

/* BYOK 设置 */
const modal = document.getElementById('settings');
document.getElementById('btn-settings').addEventListener('click', () => {
  const cfg = byok.get();
  document.getElementById('set-base').value = cfg.base || '';
  document.getElementById('set-key').value = cfg.key || '';
  document.getElementById('set-model').value = cfg.model || '';
  modal.classList.remove('hidden');
});
document.getElementById('btn-close').addEventListener('click', () => modal.classList.add('hidden'));
document.getElementById('btn-save').addEventListener('click', () => {
  byok.set({
    base: document.getElementById('set-base').value.trim(),
    key: document.getElementById('set-key').value.trim(),
    model: document.getElementById('set-model').value.trim()
  });
  modal.classList.add('hidden');
  loadHealth();
});
document.getElementById('btn-clear').addEventListener('click', () => {
  byok.clear();
  modal.classList.add('hidden');
  loadHealth();
});

async function loadHealth() {
  try {
    const resp = await fetch('/api/health');
    const data = await resp.json();
    const local = byok.get();
    const llm = data.llm_ready || !!local.key;
    const cloud = data.cloud_ready;
    badge.className = 'badge ' + (cloud && llm ? 'ok' : 'warn');
    badge.textContent = (cloud ? '云端存储已连接' : '本地降级存储') + ' · ' + (llm ? '大模型已接入' : '未接入大模型');
  } catch {
    badge.className = 'badge warn';
    badge.textContent = '服务未就绪';
  }
}

loadHealth();
