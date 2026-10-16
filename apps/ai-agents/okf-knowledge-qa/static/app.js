/**
 * OKF 知识库问答前端（零构建，原生 ES Module）。
 *
 * 安全约定：大模型输出一律先经 escapeHtml 转义再套 Markdown 语法，
 * 因此返回的 HTML 不可能注入脚本——模型输出被视为不可信输入。
 */

const EXAMPLES = [
  'OKF 知识包的三层结构是什么？',
  '道家思想中「道法自然」指什么？',
  'Python 3.14 有哪些重要新特性？',
  '容器镜像构建有哪些最佳实践？',
  '中医里「治未病」的含义是什么？',
];

const el = {
  form: document.getElementById('ask-form'),
  input: document.getElementById('question'),
  submit: document.getElementById('submit-btn'),
  chips: document.getElementById('example-chips'),
  alert: document.getElementById('alert'),
  result: document.getElementById('result'),
  empty: document.getElementById('empty'),
  answer: document.getElementById('answer-body'),
  sources: document.getElementById('sources-list'),
  hitCount: document.getElementById('hit-count'),
  degraded: document.getElementById('degraded-badge'),
  pillKb: document.getElementById('pill-kb'),
  pillLlm: document.getElementById('pill-llm'),
  footerStats: document.getElementById('footer-stats'),
};

/* ---------------- 工具函数 ---------------- */

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/** 行内语法：代码、加粗、引用编号。输入必须已转义。 */
function inlineMd(str) {
  return str
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(\d{1,2})\]/g, '<sup class="cite" data-idx="$1">$1</sup>');
}

/** 极简 Markdown 渲染器：仅支持标题、列表、代码块、引用、分割线。 */
function renderMarkdown(src) {
  const lines = escapeHtml(src).split('\n');
  const out = [];
  let list = null;
  let code = null;

  const closeList = () => {
    if (list) {
      out.push(`</${list}>`);
      list = null;
    }
  };

  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      if (code === null) {
        closeList();
        code = [];
      } else {
        out.push(`<pre><code>${code.join('\n')}</code></pre>`);
        code = null;
      }
      continue;
    }
    if (code !== null) {
      code.push(line);
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      closeList();
      const level = heading[1].length + 1;
      out.push(`<h${level}>${inlineMd(heading[2])}</h${level}>`);
      continue;
    }

    const bullet = line.match(/^\s*[-*]\s+(.*)$/);
    const numbered = line.match(/^\s*\d+[.、)]\s+(.*)$/);
    if (bullet || numbered) {
      const type = numbered ? 'ol' : 'ul';
      if (list !== type) {
        closeList();
        out.push(`<${type}>`);
        list = type;
      }
      out.push(`<li>${inlineMd((bullet || numbered)[1])}</li>`);
      continue;
    }

    closeList();
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (/^(-{3,}|\*{3,})$/.test(trimmed)) {
      out.push('<hr>');
      continue;
    }
    out.push(`<p>${inlineMd(trimmed)}</p>`);
  }

  closeList();
  if (code !== null) out.push(`<pre><code>${code.join('\n')}</code></pre>`);
  return out.join('');
}

function showAlert(message, kind = 'err') {
  el.alert.hidden = false;
  el.alert.className = `alert alert--${kind}`;
  el.alert.textContent = message;
}

function clearAlert() {
  el.alert.hidden = true;
  el.alert.textContent = '';
}

function setPill(node, text, kind) {
  node.textContent = text;
  node.className = `pill pill--${kind}`;
}

/* ---------------- 健康检查 ---------------- */

async function loadHealth() {
  try {
    const res = await fetch('/api/health');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.db_ready) {
      const chunks = data.stats?.chunk_count ?? '?';
      const bundles = data.stats?.bundle_count ?? '?';
      setPill(el.pillKb, `知识库就绪 · ${bundles} 束 / ${chunks} 片段`, 'ok');
      el.footerStats.textContent = `索引构建于 ${(data.stats?.built_at ?? '').slice(0, 10) || '—'}`;
    } else {
      setPill(el.pillKb, '知识库未就绪', 'err');
      showAlert(data.error || '检索索引缺失，请执行 python scripts/build_index.py 构建索引。', 'err');
    }

    if (data.llm_ready) {
      setPill(el.pillLlm, `大模型就绪 · ${data.llm_model}`, 'ok');
    } else {
      setPill(el.pillLlm, '未配置大模型 · 降级为原文直出', 'warn');
    }
  } catch (err) {
    setPill(el.pillKb, '服务不可达', 'err');
    setPill(el.pillLlm, '服务不可达', 'err');
    showAlert(`健康检查失败：${err.message}`, 'err');
  }
}

/* ---------------- 提问 ---------------- */

function renderSources(citations) {
  el.sources.innerHTML = citations
    .map(
      (c) => `
      <li class="source" id="src-${c.index}">
        <div class="source__head">
          <span class="source__idx">${c.index}</span>
          <span class="source__title">${escapeHtml(c.title)}</span>
        </div>
        <div class="source__meta">${escapeHtml(c.bundle || '—')}${c.group ? ' · ' + escapeHtml(c.group) : ''}</div>
        <div class="source__text">${escapeHtml(c.snippet)}</div>
      </li>`
    )
    .join('');
}

function renderResult(data) {
  el.empty.hidden = true;
  el.result.hidden = false;

  el.answer.innerHTML = renderMarkdown(data.answer);
  el.hitCount.textContent = data.hit_count ? `${data.hit_count} 条` : '无命中';
  el.degraded.hidden = !data.degraded;
  renderSources(data.citations || []);

  if (data.error) {
    showAlert(`大模型调用失败，已降级为原文片段直出：${data.error}`, 'warn');
  }
}

/** 点击答案中的引用编号，高亮并滚动到对应出处卡片。 */
function bindCitationClicks() {
  el.answer.querySelectorAll('.cite').forEach((node) => {
    node.addEventListener('click', () => {
      const target = document.getElementById(`src-${node.dataset.idx}`);
      if (!target) return;
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      target.classList.add('source--flash');
      setTimeout(() => target.classList.remove('source--flash'), 1200);
    });
  });
}

async function ask(question) {
  clearAlert();
  el.submit.disabled = true;
  el.submit.textContent = '检索中…';
  el.empty.hidden = true;
  el.result.hidden = false;
  el.answer.innerHTML =
    '<div class="skeleton"><div class="skeleton__bar" style="width:92%"></div>' +
    '<div class="skeleton__bar" style="width:78%"></div>' +
    '<div class="skeleton__bar" style="width:85%"></div>' +
    '<div class="skeleton__bar" style="width:60%"></div></div>';
  el.sources.innerHTML = '';
  el.hitCount.textContent = '';
  el.degraded.hidden = true;

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const detail = data?.detail || `HTTP ${res.status}`;
      throw new Error(detail);
    }
    renderResult(data);
    bindCitationClicks();
  } catch (err) {
    el.result.hidden = true;
    el.empty.hidden = false;
    showAlert(`提问失败：${err.message}`, 'err');
  } finally {
    el.submit.disabled = false;
    el.submit.textContent = '提问';
  }
}

/* ---------------- 初始化 ---------------- */

function init() {
  el.chips.innerHTML = EXAMPLES.map((q) => `<button type="button" class="chip">${escapeHtml(q)}</button>`).join('');
  el.chips.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    el.input.value = chip.textContent;
    el.input.focus();
    ask(chip.textContent);
  });

  el.form.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = el.input.value.trim();
    if (!q) return;
    ask(q);
  });

  el.input.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      el.form.requestSubmit();
    }
  });

  loadHealth();
}

init();
