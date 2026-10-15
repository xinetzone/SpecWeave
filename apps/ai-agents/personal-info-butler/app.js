/**
 * 个人信息管家 Agent —— 前端（零构建，原生 ES Module）。
 */

const $ = (sel) => document.querySelector(sel);
const viewEl = $('#view');

const SETTINGS_KEY = 'personal-info-butler.settings';
const THEME_KEY = 'personal-info-butler.theme';

const state = {
  view: 'inbox',
  items: [],
  tags: [],
  stats: {},
  filters: { kind: '', tag: '', status: '' },
  keyword: '',
  captureKind: 'auto',
  lastCapture: null,
  ask: { answer: '', citations: [], thread: [] },
  extract: { md: '', days: 7, scope: 'days' },
  todos: { groups: [], advice: [] },
  summary: { md: '', days: 7, history: [] },
  health: null,
};

// ------------------------------------------------------------------ 工具
function loadSettings() {
  try {
    return JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}');
  } catch {
    return {};
  }
}
function saveSettings(s) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify({ ...loadSettings(), ...s }));
}

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function inlineMd(s) {
  return s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code>$1</code>');
}

function renderMd(text) {
  const lines = String(text || '').split(/\r?\n/);
  let out = '';
  let inList = false;
  for (const raw of lines) {
    const line = raw.trimEnd();
    if (/^#{1,6}\s/.test(line)) {
      if (inList) { out += '</ul>'; inList = false; }
      out += `<h3>${inlineMd(esc(line.replace(/^#+\s*/, '')))}</h3>`;
      continue;
    }
    if (/^[-*]\s/.test(line)) {
      if (!inList) { out += '<ul>'; inList = true; }
      out += `<li>${inlineMd(esc(line.replace(/^[-*]\s*/, '')))}</li>`;
      continue;
    }
    if (!line.trim()) {
      if (inList) { out += '</ul>'; inList = false; }
      continue;
    }
    if (inList) { out += '</ul>'; inList = false; }
    out += `<p>${inlineMd(esc(line))}</p>`;
  }
  if (inList) out += '</ul>';
  return out;
}

function fmtTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

const KIND_LABEL = { idea: '想法', material: '资料', todo: '待办' };

let toastTimer = null;
function toast(msg) {
  const el = $('#toast');
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 2600);
}

// ------------------------------------------------------------------ 接口
async function api(path, { method = 'GET', body } = {}) {
  const s = loadSettings();
  const headers = { 'Content-Type': 'application/json' };
  if (s.token) headers['x-app-token'] = s.token;
  if (s.llmKey) headers['x-llm-key'] = s.llmKey;
  if (s.llmBase) headers['x-llm-base'] = s.llmBase;
  if (s.llmModel) headers['x-llm-model'] = s.llmModel;

  const res = await fetch(path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  let data = {};
  try {
    data = await res.json();
  } catch {
    throw new Error('服务端返回了非 JSON 响应');
  }
  if (!res.ok || data.ok === false) throw new Error(data.error || `请求失败（${res.status}）`);
  return data;
}

async function refreshMeta() {
  try {
    const data = await api('/api/tags');
    state.tags = data.tags || [];
    state.stats = data.stats || {};
    renderSidebarMeta();
  } catch {
    /* 静默 */
  }
}

async function refreshHealth() {
  try {
    state.health = await api('/api/health');
  } catch {
    state.health = null;
  }
  const badge = $('#storageBadge');
  if (badge) {
    badge.textContent = state.health
      ? `存储：${state.health.storage === 'supabase' ? '云端' : '内存'} · ${state.health.llmReady ? '已接大模型' : '待接大模型'}`
      : '服务未连接';
  }
}

// ------------------------------------------------------------------ 侧栏
function renderSidebarMeta() {
  const s = state.stats;
  $('#stats').innerHTML = [
    ['全部', s.total ?? 0],
    ['想法', s.idea ?? 0],
    ['资料', s.material ?? 0],
    ['待办', s.openTodo ?? 0],
  ]
    .map(([label, n]) => `<div class="stat-pill"><b>${n}</b><span>${label}</span></div>`)
    .join('');

  $('#tagCloud').innerHTML = state.tags.length
    ? state.tags
        .slice(0, 24)
        .map(
          (t) =>
            `<button class="tag-chip ${state.filters.tag === t.name ? 'is-active' : ''}" data-tag="${esc(t.name)}">${esc(t.name)} ${t.count}</button>`
        )
        .join('')
    : '<span class="small muted">暂无标签</span>';

  document.querySelectorAll('.tag-chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      const tag = btn.dataset.tag;
      state.filters.tag = state.filters.tag === tag ? '' : tag;
      state.keyword = '';
      go('library');
    });
  });
}

function go(view) {
  state.view = view;
  document.querySelectorAll('.nav-item').forEach((b) => {
    b.classList.toggle('is-active', b.dataset.view === view);
  });
  render();
}

// ------------------------------------------------------------------ 视图
function render() {
  const map = {
    inbox: renderInbox,
    library: renderLibrary,
    ask: renderAsk,
    todos: renderTodos,
    extract: renderExtract,
    summary: renderSummary,
    settings: renderSettings,
  };
  viewEl.innerHTML = (map[state.view] || renderInbox)();
  bindView();
}

function viewHead(title, desc) {
  return `<div class="view-head"><h1>${title}</h1><p>${desc}</p></div>`;
}

function itemCard(item) {
  const tags = (item.tags || []).map((t) => `<span class="mini-tag">${esc(t)}</span>`).join('');
  const score = item._score ? `<span class="mini-tag">相关度 ${item._score}</span>` : '';
  const text = item._snippet || item.summary || item.content || '';
  return `<article class="item" data-id="${esc(item.id)}">
    <div class="item-head">
      <span class="kind-tag kind-${esc(item.kind)}">${KIND_LABEL[item.kind] || item.kind}</span>
      <span class="item-title">${esc(item.title)}</span>
      ${item.status && item.kind === 'todo' ? `<span class="mini-tag">${item.status === 'done' ? '已完成' : '进行中'}</span>` : ''}
      ${score}
    </div>
    <div class="item-text">${esc(String(text).slice(0, 160))}</div>
    <div class="item-meta">
      <span>${fmtTime(item.created_at)}</span>
      ${item.due_date ? `<span>截止 ${esc(item.due_date)}</span>` : ''}
      ${item.priority ? `<span>优先级 ${esc(item.priority)}</span>` : ''}
      <span>${tags}</span>
    </div>
  </article>`;
}

function renderInbox() {
  const kinds = [['auto', '自动判断'], ['idea', '想法'], ['material', '资料'], ['todo', '待办']];
  const recent = state.items.filter((i) => !i.parent_id).slice(0, 12);
  return `
    ${viewHead('随手记一笔', '粘贴任何想法、资料或待办，Agent 自动分类、摘要、打标签并关联已有内容')}
    <div class="card">
      <textarea id="captureInput" rows="5" placeholder="例如：下周三前要把季度复盘整理成文档发给团队；另外看到一篇 RAG 评估方法的资料 https://..."></textarea>
      <div class="row" style="margin-top:10px">
        <div class="chips" id="kindChips">
          ${kinds
            .map(
              ([v, label]) =>
                `<button class="chip ${state.captureKind === v ? 'is-active' : ''}" data-kind="${v}">${label}</button>`
            )
            .join('')}
        </div>
        <div class="spacer"></div>
        <button class="btn primary" id="captureBtn">记录并整理</button>
      </div>
      <div class="hint" style="margin-top:10px">快捷键 Ctrl / ⌘ + Enter 直接提交</div>
    </div>
    <div id="captureResult"></div>
    ${viewHead('最近记录', '点击任意条目查看关联内容与派生待办')}
    <div id="recentList">${recent.length ? recent.map(itemCard).join('') : '<div class="empty">还没有记录，从上面写第一条开始</div>'}</div>
  `;
}

function renderLibrary() {
  const f = state.filters;
  const filtered = state.items.filter(
    (i) => (!f.kind || i.kind === f.kind) && (!f.tag || (i.tags || []).includes(f.tag)) && (!f.status || i.status === f.status)
  );
  const kinds = [['', '全部'], ['idea', '想法'], ['material', '资料'], ['todo', '待办']];
  return `
    ${viewHead('资料库', state.keyword ? `关键词「${esc(state.keyword)}」命中 ${filtered.length} 条` : `共 ${filtered.length} 条记录`)}
    <div class="card">
      <div class="row">
        <div class="chips" id="kindFilter">
          ${kinds
            .map(([v, l]) => `<button class="chip ${f.kind === v ? 'is-active' : ''}" data-kind="${v}">${l}</button>`)
            .join('')}
        </div>
        <div class="spacer"></div>
        ${f.tag ? `<button class="btn sm" id="clearTag">标签：${esc(f.tag)} ✕</button>` : ''}
        ${state.keyword ? `<button class="btn sm" id="clearKeyword">关键词：${esc(state.keyword)} ✕</button>` : ''}
      </div>
    </div>
    <div id="itemList">${filtered.length ? filtered.map(itemCard).join('') : '<div class="empty">没有匹配的记录</div>'}</div>
  `;
}

function renderAsk() {
  const { answer, citations, thread } = state.ask;
  return `
    ${viewHead('智能问答', '基于你自己的记录回答，答案附来源引用')}
    <div class="card">
      <textarea id="askInput" rows="3" placeholder="例如：我最近在推进的事情有哪些？关于 RAG 评估我记过什么？"></textarea>
      <div class="row end" style="margin-top:10px">
        <button class="btn primary" id="askBtn">提问</button>
      </div>
    </div>
    ${answer ? `<div class="card"><div class="answer">${renderMd(answer)}</div>${
      citations.length
        ? `<div class="cite">${citations.map((c) => `<button class="cite-item" data-id="${esc(c.id)}">[${c.index}] ${esc(c.title)}</button>`).join('')}</div>`
        : ''
    }</div>` : ''}
    ${thread.length ? viewHead('本次会话', '') : ''}
    ${thread
      .map(
        (t) => `<div class="card"><div class="small muted">问：${esc(t.q)}</div><div style="margin-top:8px">${renderMd(t.a)}</div></div>`
      )
      .join('')}
  `;
}

function renderTodos() {
  const { groups, advice } = state.todos;
  return `
    ${viewHead('待办整理', '自动去重合并、按优先级分组，并给出建议下一步')}
    <div class="row" style="margin-bottom:14px">
      <button class="btn primary" id="todoRefresh">重新整理</button>
      <span class="small muted">整理会调用大模型分析你当前的全部待办</span>
    </div>
    ${advice.length ? `<div class="card">${advice.map((a) => `<div>• ${esc(a)}</div>`).join('')}</div>` : ''}
    ${
      groups.length
        ? groups
            .map(
              (g) => `<div class="todo-group">
        <div class="group-title"><span class="level-${String(g.level).toLowerCase()}">${esc(g.level)}</span><span class="small muted">${g.items.length} 项</span></div>
        ${g.items
          .map(
            (it) => `<div class="todo ${it.status === 'done' ? 'done' : ''}">
          <button class="checkbox ${it.status === 'done' ? 'on' : ''}" data-toggle="${esc(it.id || '')}" ${it.id ? '' : 'disabled'}>${it.status === 'done' ? '✓' : ''}</button>
          <div>
            <div class="todo-title">${esc(it.title)}</div>
            ${it.reason ? `<div class="small muted">依据：${esc(it.reason)}</div>` : ''}
            ${it.next_step ? `<div class="small">下一步：${esc(it.next_step)}</div>` : ''}
            ${it.due_date ? `<div class="small muted">截止：${esc(it.due_date)}</div>` : ''}
          </div>
        </div>`
          )
          .join('')}
      </div>`
            )
            .join('')
        : '<div class="empty">点击「重新整理」生成待办视图</div>'
    }
  `;
}

function renderExtract() {
  const e = state.extract;
  return `
    ${viewHead('重点信息提取', '从一批记录中抽出核心观点、决策、风险、待确认问题与关键实体')}
    <div class="card">
      <div class="row">
        <div class="chips" id="extractScope">
          <button class="chip ${e.scope === 'days' ? 'is-active' : ''}" data-scope="days">按时间范围</button>
          <button class="chip ${e.scope === 'all' ? 'is-active' : ''}" data-scope="all">全部记录</button>
        </div>
        <select class="input" id="extractDays" style="width:auto">
          ${[7, 14, 30, 90].map((d) => `<option value="${d}" ${e.days === d ? 'selected' : ''}>最近 ${d} 天</option>`).join('')}
        </select>
        <div class="spacer"></div>
        <button class="btn primary" id="extractBtn">提取重点</button>
      </div>
    </div>
    ${e.md ? `<div class="card md">${renderMd(e.md)}</div>` : '<div class="empty">选择范围后开始提取</div>'}
  `;
}

function renderSummary() {
  const s = state.summary;
  return `
    ${viewHead('阶段总结', '基于已有内容生成阶段总结与后续行动建议，并自动存档')}
    <div class="card">
      <div class="row">
        <select class="input" id="summaryDays" style="width:auto">
          ${[7, 14, 30, 90].map((d) => `<option value="${d}" ${s.days === d ? 'selected' : ''}>最近 ${d} 天</option>`).join('')}
        </select>
        <div class="spacer"></div>
        <button class="btn primary" id="summaryBtn">生成阶段总结</button>
      </div>
    </div>
    ${s.md ? `<div class="card md">${renderMd(s.md)}</div>` : ''}
    ${viewHead('历史总结', '每次生成都会保存在云端')}
    <div id="summaryHistory">${
      s.history.length
        ? s.history
            .map(
              (h) => `<div class="history-item">
          <div class="row"><strong>最近 ${h.range_days} 天 · ${h.item_count} 条记录</strong><div class="spacer"></div><span class="small muted">${fmtTime(h.created_at)}</span></div>
          <div class="md" style="margin-top:8px">${renderMd(h.content_md)}</div>
        </div>`
            )
            .join('')
        : '<div class="empty">暂无历史总结</div>'
    }</div>
  `;
}

function renderSettings() {
  const s = loadSettings();
  const h = state.health;
  return `
    ${viewHead('设置', '凭据保存在本机浏览器，不会上传到任何第三方')}
    <div class="card">
      <div class="kv" style="grid-template-columns:96px 1fr">
        <b>存储模式</b><span>${h ? (h.storage === 'supabase' ? 'Supabase 云端数据库' : '内存（未配置云端，重启即失）') : '未知'}</span>
        <b>大模型</b><span>${h ? (h.llmReady ? `服务端已配置（${esc(h.llmModel)}）` : '服务端未配置，可用下方 BYOK') : '未知'}</span>
        <b>访问令牌</b><span>${h ? (h.tokenRequired ? '已启用' : '未启用') : '未知'}</span>
      </div>
    </div>
    <div class="card">
      <h3 style="margin-top:0">访问令牌（APP_TOKEN）</h3>
      <input class="input" id="setToken" value="${esc(s.token || '')}" placeholder="服务端设置了 APP_TOKEN 时必填" />
      <h3>大模型 Base URL</h3>
      <input class="input" id="setBase" value="${esc(s.llmBase || '')}" placeholder="https://api.deepseek.com/v1" />
      <h3>API Key</h3>
      <input class="input" id="setKey" type="password" value="${esc(s.llmKey || '')}" placeholder="sk-..." />
      <h3>模型</h3>
      <input class="input" id="setModel" value="${esc(s.llmModel || '')}" placeholder="deepseek-chat" />
      <div class="row end" style="margin-top:14px">
        <button class="btn" id="clearSettings">清空</button>
        <button class="btn primary" id="saveSettings">保存</button>
      </div>
      <div class="hint" style="margin-top:12px">
        支持任何 OpenAI 兼容端点：DeepSeek / 通义千问 / 腾讯混元 / Moonshot / OpenAI 等。
        Key 仅随请求头发往本应用后端，由后端转发给模型服务，服务端不落盘。
      </div>
    </div>
  `;
}

// ------------------------------------------------------------------ 抽屉
async function openDetail(id) {
  const drawer = $('#drawer');
  const mask = $('#drawerMask');
  drawer.hidden = false;
  mask.hidden = false;
  drawer.innerHTML = '<div class="empty">加载中…</div>';
  try {
    const { item, related, children } = await api(`/api/item?id=${encodeURIComponent(id)}`);
    drawer.innerHTML = `
      <div class="row"><h2>${esc(item.title)}</h2><div class="spacer"></div><button class="btn sm" id="closeDrawer">关闭</button></div>
      <div class="item-meta" style="margin-bottom:10px">
        <span class="kind-tag kind-${esc(item.kind)}">${KIND_LABEL[item.kind] || item.kind}</span>
        <span>${fmtTime(item.created_at)}</span>
        ${item.due_date ? `<span>截止 ${esc(item.due_date)}</span>` : ''}
        ${item.priority ? `<span>优先级 ${esc(item.priority)}</span>` : ''}
      </div>
      ${item.summary ? `<div class="card" style="margin:12px 0"><b class="small muted">摘要</b><div>${esc(item.summary)}</div></div>` : ''}
      <div class="card" style="white-space:pre-wrap">${esc(item.content)}</div>
      ${(item.tags || []).length ? `<div class="chips" style="margin-bottom:12px">${item.tags.map((t) => `<span class="mini-tag">${esc(t)}</span>`).join('')}</div>` : ''}
      ${
        item.kind === 'todo'
          ? `<div class="row" style="margin-bottom:12px">
              <button class="btn" id="toggleStatus">${item.status === 'done' ? '标记为进行中' : '标记为已完成'}</button>
              <button class="btn" id="deleteItem">删除</button>
            </div>`
          : `<div class="row" style="margin-bottom:12px"><button class="btn" id="deleteItem">删除</button></div>`
      }
      <h3>关联内容</h3>
      ${
        related.length
          ? related
              .map(
                (r) => `<div class="item" data-id="${esc(r.id)}"><div class="item-head"><span class="kind-tag kind-${esc(r.kind)}">${KIND_LABEL[r.kind] || r.kind}</span><span class="item-title">${esc(r.title)}</span></div><div class="item-text">${esc(r.reason || '')}</div></div>`
              )
              .join('')
          : '<div class="small muted">暂无关联</div>'
      }
      ${children.length ? `<h3>派生待办</h3>${children.map((c) => `<div class="item" data-id="${esc(c.id)}"><div class="item-head"><span class="kind-tag kind-todo">待办</span><span class="item-title">${esc(c.title)}</span></div></div>`).join('')}` : ''}
    `;
    $('#closeDrawer').onclick = closeDrawer;
    $('#deleteItem').onclick = async () => {
      await api(`/api/item?id=${encodeURIComponent(item.id)}`, { method: 'DELETE' });
      closeDrawer();
      await reloadItems();
      toast('已删除');
    };
    const toggle = $('#toggleStatus');
    if (toggle) {
      toggle.onclick = async () => {
        await api(`/api/item?id=${encodeURIComponent(item.id)}`, {
          method: 'PATCH',
          body: { status: item.status === 'done' ? 'open' : 'done' },
        });
        await reloadItems();
        openDetail(item.id);
        toast('状态已更新');
      };
    }
    drawer.querySelectorAll('[data-id]').forEach((el) => {
      el.onclick = () => openDetail(el.dataset.id);
    });
  } catch (err) {
    drawer.innerHTML = `<div class="empty">${esc(err.message)}</div>`;
    const btn = document.createElement('button');
    btn.className = 'btn';
    btn.textContent = '关闭';
    btn.onclick = closeDrawer;
    drawer.appendChild(btn);
  }
}

function closeDrawer() {
  $('#drawer').hidden = true;
  $('#drawerMask').hidden = true;
}

// ------------------------------------------------------------------ 数据
async function reloadItems() {
  try {
    const data = await api('/api/items?limit=200');
    state.items = data.items || [];
  } catch (err) {
    toast(err.message);
  }
  render();
  await refreshMeta();
}

// ------------------------------------------------------------------ 绑定
function bindView() {
  viewEl.querySelectorAll('.item[data-id]').forEach((el) => {
    el.addEventListener('click', () => openDetail(el.dataset.id));
  });

  // 录入
  const input = $('#captureInput');
  if (input) {
    input.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') submitCapture();
    });
    viewEl.querySelectorAll('#kindChips .chip').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.captureKind = btn.dataset.kind;
        render();
      });
    });
    $('#captureBtn').addEventListener('click', submitCapture);
  }

  // 资料库筛选
  viewEl.querySelectorAll('#kindFilter .chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.filters.kind = btn.dataset.kind;
      render();
    });
  });
  const clearTag = $('#clearTag');
  if (clearTag) clearTag.onclick = () => { state.filters.tag = ''; reloadItems(); };
  const clearKeyword = $('#clearKeyword');
  if (clearKeyword) clearKeyword.onclick = () => { state.keyword = ''; $('#globalSearch').value = ''; reloadItems(); };

  // 问答
  const askBtn = $('#askBtn');
  if (askBtn) {
    askBtn.onclick = async () => {
      const question = $('#askInput').value.trim();
      if (!question) return toast('请输入问题');
      askBtn.disabled = true;
      askBtn.textContent = '思考中…';
      try {
        const data = await api('/api/ask', { method: 'POST', body: { question } });
        state.ask.answer = data.answer;
        state.ask.citations = data.citations || [];
        state.ask.thread.unshift({ q: question, a: data.answer });
        $('#askInput').value = '';
        render();
      } catch (err) {
        toast(err.message);
      } finally {
        askBtn.disabled = false;
        askBtn.textContent = '提问';
      }
    };
  }
  viewEl.querySelectorAll('.cite-item[data-id]').forEach((el) => {
    el.addEventListener('click', () => openDetail(el.dataset.id));
  });

  // 待办
  const todoRefresh = $('#todoRefresh');
  if (todoRefresh) {
    todoRefresh.onclick = async () => {
      todoRefresh.disabled = true;
      todoRefresh.textContent = '整理中…';
      try {
        const data = await api('/api/todos');
        state.todos = { groups: data.groups || [], advice: data.advice || [] };
        render();
      } catch (err) {
        toast(err.message);
      } finally {
        todoRefresh.disabled = false;
        todoRefresh.textContent = '重新整理';
      }
    };
  }
  viewEl.querySelectorAll('[data-toggle]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.toggle;
      if (!id) return;
      const cur = btn.classList.contains('on');
      await api(`/api/item?id=${encodeURIComponent(id)}`, {
        method: 'PATCH',
        body: { status: cur ? 'open' : 'done' },
      });
      btn.classList.toggle('on', !cur);
      btn.textContent = cur ? '' : '✓';
      await refreshMeta();
    });
  });

  // 重点提取
  viewEl.querySelectorAll('#extractScope .chip').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.extract.scope = btn.dataset.scope;
      render();
    });
  });
  const extractDays = $('#extractDays');
  if (extractDays) extractDays.onchange = () => { state.extract.days = Number(extractDays.value); };
  const extractBtn = $('#extractBtn');
  if (extractBtn) {
    extractBtn.onclick = async () => {
      extractBtn.disabled = true;
      extractBtn.textContent = '提取中…';
      try {
        const body = state.extract.scope === 'all' ? { limit: 60 } : { days: state.extract.days };
        const data = await api('/api/extract', { method: 'POST', body });
        state.extract.md = data.markdown;
        render();
      } catch (err) {
        toast(err.message);
      } finally {
        extractBtn.disabled = false;
        extractBtn.textContent = '提取重点';
      }
    };
  }

  // 阶段总结
  const summaryDays = $('#summaryDays');
  if (summaryDays) summaryDays.onchange = () => { state.summary.days = Number(summaryDays.value); };
  const summaryBtn = $('#summaryBtn');
  if (summaryBtn) {
    summaryBtn.onclick = async () => {
      summaryBtn.disabled = true;
      summaryBtn.textContent = '生成中…';
      try {
        const data = await api('/api/summary', { method: 'POST', body: { days: state.summary.days } });
        state.summary.md = data.markdown;
        await loadSummaryHistory();
        render();
      } catch (err) {
        toast(err.message);
      } finally {
        summaryBtn.disabled = false;
        summaryBtn.textContent = '生成阶段总结';
      }
    };
  }

  // 设置
  const saveBtn = $('#saveSettings');
  if (saveBtn) {
    saveBtn.onclick = async () => {
      saveSettings({
        token: $('#setToken').value.trim(),
        llmBase: $('#setBase').value.trim(),
        llmKey: $('#setKey').value.trim(),
        llmModel: $('#setModel').value.trim(),
      });
      await refreshHealth();
      render();
      toast('已保存');
    };
    $('#clearSettings').onclick = () => {
      localStorage.removeItem(SETTINGS_KEY);
      render();
      toast('已清空本机设置');
    };
  }
}

async function submitCapture() {
  const input = $('#captureInput');
  const btn = $('#captureBtn');
  const text = input.value.trim();
  if (!text) return toast('请输入内容');
  btn.disabled = true;
  btn.textContent = '整理中…';
  try {
    const data = await api('/api/items', {
      method: 'POST',
      body: { text, kind: state.captureKind === 'auto' ? undefined : state.captureKind },
    });
    input.value = '';
    state.lastCapture = data;
    await reloadItems();
    $('#captureResult').innerHTML = `
      <div class="result-card">
        <h3>已归档为「${KIND_LABEL[data.item.kind] || data.item.kind}」${data.ai ? '' : '（启发式，未接大模型）'}</h3>
        <div class="kv">
          <b>标题</b><span>${esc(data.item.title)}</span>
          ${data.item.summary ? `<b>摘要</b><span>${esc(data.item.summary)}</span>` : ''}
          <b>标签</b><span>${(data.item.tags || []).map((t) => `<span class="mini-tag">${esc(t)}</span>`).join(' ')}</span>
          ${data.todos.length ? `<b>待办</b><span>${data.todos.map((t) => esc(t.title)).join(' ｜ ')}</span>` : ''}
          ${
            data.related.length
              ? `<b>关联</b><span>${data.related.map((r) => `<span class="mini-tag" data-id="${esc(r.id)}">${esc(r.title)}</span>`).join(' ')}</span>`
              : ''
          }
        </div>
      </div>`;
    $('#captureResult').querySelectorAll('[data-id]').forEach((el) => {
      el.addEventListener('click', () => openDetail(el.dataset.id));
    });
    toast('已记录并整理');
  } catch (err) {
    toast(err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = '记录并整理';
  }
}

async function loadSummaryHistory() {
  try {
    const data = await api('/api/summary?limit=10');
    state.summary.history = data.summaries || [];
  } catch {
    state.summary.history = [];
  }
}

// ------------------------------------------------------------------ 启动
function initTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  const dark = saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
}

async function boot() {
  initTheme();

  $('#themeBtn').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem(THEME_KEY, next);
  });

  document.querySelectorAll('[data-view]').forEach((el) => {
    el.addEventListener('click', () => go(el.dataset.view));
  });

  $('#drawerMask').addEventListener('click', closeDrawer);

  let timer = null;
  $('#globalSearch').addEventListener('input', (e) => {
    clearTimeout(timer);
    const value = e.target.value.trim();
    timer = setTimeout(async () => {
      state.keyword = value;
      state.items = (await api(`/api/items?limit=100${value ? `&q=${encodeURIComponent(value)}` : ''}`)).items || [];
      go('library');
    }, 320);
  });

  await refreshHealth();
  await refreshMeta();
  await reloadItems();
  await loadSummaryHistory();
}

boot();
