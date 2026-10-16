/* 个人信息管家 —— 前端行为层（零依赖、零构建）。
 *
 * 与后端只通过 /api/* 契约耦合。五条必须记住的约定：
 *   1. API 基址优先取「设置」，其次取构建期注入的 window.BUTLER_API_BASE；
 *   2. BYOK 凭据只活在 localStorage 与当次请求头里，后端不落盘；
 *   3. 连接状态是**全局事实**，只在上方横幅呈现一次，不往四个面板里各糊一遍；
 *   4. 任何接口失败都要显式呈现，绝不能静默——静默失败的按钮会被用户当成
 *      「点了没反应」，那是本产品最不能犯的错；
 *   5. 失败必须**可归因**：用户要能一眼分清「我没配」「配了但连不上」「后端说不行」，
 *      三者对应三种完全不同的动作。把后端返回的原始 HTML 原样糊到脸上，等于把
 *      归因责任推给用户——所以这里统一归一化，并把原始响应收进折叠块备查。
 */
(() => {
  'use strict';

  var STORAGE_KEY = 'butler.settings.v1';
  var DEFAULTS = {
    apiBase: '', token: '', llmBaseUrl: '', llmApiKey: '', llmModel: ''
  };
  var TIMEOUT_MS = 12000;

  /* 连接状态机：checking / ok / unconfigured / failed。
   * 「未配置」与「连接失败」必须分开：前者用户自己能修，后者要查环境。 */
  var state = { connection: 'checking', error: null };

  var byId = function (id) { return document.getElementById(id); };

  var ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  var esc = function (value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) { return ESCAPES[c]; });
  };

  var settings = Object.assign({}, DEFAULTS);
  try {
    settings = Object.assign(settings, JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'));
  } catch (err) { /* 本机设置损坏时静默回默认值，不阻塞界面 */ }

  var filterKind = '';

  function explicitBase() {
    return String(settings.apiBase || window.BUTLER_API_BASE || '').trim();
  }

  var apiBase = function () {
    var raw = explicitBase();
    if (!raw) { return ''; }
    raw = raw.replace(/\/+$/, '');
    // 高频配错：把后端的 /api 前缀也写进基址，请求会打到 /api/api/items
    if (/\/api$/i.test(raw)) { raw = raw.slice(0, -4); }
    return raw;
  };

  function persist() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(settings)); } catch (err) { /* 隐私模式下可能不可写 */ }
  }

  function headers() {
    var h = { 'Content-Type': 'application/json' };
    if (settings.token) { h['X-App-Token'] = settings.token; }
    if (settings.llmApiKey) {
      h['X-LLM-Api-Key'] = settings.llmApiKey;
      if (settings.llmBaseUrl) { h['X-LLM-Base-Url'] = settings.llmBaseUrl; }
      if (settings.llmModel) { h['X-LLM-Model'] = settings.llmModel; }
    }
    return h;
  }

  /* -- 错误归一化 ---------------------------------------------------------- */

  function apiError(message, info) {
    var err = new Error(message);
    err.info = info || {};
    return err;
  }

  function looksLikeHtml(text) {
    return /^\s*<(?:!doctype|html|head|body|title)/i.test(text || '');
  }

  function pageIsHttps() {
    return typeof location !== 'undefined' && location.protocol === 'https:';
  }

  function networkError(url, err) {
    var message;
    if (err && err.name === 'AbortError') {
      message = '请求超过 ' + (TIMEOUT_MS / 1000) + ' 秒没有响应，后端可能没有在运行。';
    } else if (!explicitBase()) {
      message = '还没有配置后端地址。';
    } else {
      message = '请求没有发出去（' + ((err && err.message) || '网络错误') + '）。'
        + '常见原因：地址写错、后端没启动、或后端没有允许本站跨域（CORS）。';
    }
    return apiError(message, { network: true, url: url, raw: (err && err.message) || '' });
  }

  function httpError(reply) {
    var html = looksLikeHtml(reply.text);
    var detail = '';
    var message;
    if (html) {
      message = explicitBase()
        ? '请求打到的是一个网页，不是接口（HTTP ' + reply.status + '）。'
          + '多半是「API 基址」指向了静态站点，请填后端服务地址。'
        : '还没有配置后端地址，这次请求落到了本站的静态文件上（HTTP ' + reply.status + '）。';
    } else {
      try { detail = (JSON.parse(reply.text) || {}).detail || ''; } catch (e) { detail = ''; }
      if (reply.status === 401) {
        message = '后端拒绝了这次请求（401）：访问令牌不对或没填。';
      } else if (reply.status === 404) {
        message = '接口不存在（404）：请确认后端已启动，且「API 基址」后面不需要再加 /api。';
      } else if (reply.status >= 500) {
        message = '后端出错了（HTTP ' + reply.status + '）' + (detail ? '：' + detail : '。');
      } else {
        message = detail || ('请求失败（HTTP ' + reply.status + '）。');
      }
    }
    return apiError(message, { status: reply.status, html: html, raw: reply.text });
  }

  function rawBlock(err) {
    var raw = (err && err.info && err.info.raw) || '';
    if (!raw || raw === err.message) { return ''; }
    return '<details class="butler-details"><summary>后端原始响应</summary><pre>'
      + esc(String(raw).slice(0, 800)) + '</pre></details>';
  }

  function call(path, options) {
    options = options || {};
    var url = apiBase() + path;

    // 混合内容要在发请求之前拦下：浏览器给的报错信息完全指不到点子上。
    if (pageIsHttps() && /^http:\/\//i.test(url)) {
      return Promise.reject(apiError(
        'HTTPS 页面不能请求 HTTP 后端（浏览器会按混合内容拦截）。请把后端换成 https:// 地址。',
        { mixed: true, url: url }
      ));
    }

    var controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
    var timer = controller ? setTimeout(function () { controller.abort(); }, TIMEOUT_MS) : null;
    var clear = function () { if (timer) { clearTimeout(timer); timer = null; } };

    return fetch(url, {
      method: options.method || 'GET',
      headers: headers(),
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: controller ? controller.signal : undefined
    })
      .then(
        function (res) {
          return res.text().then(function (text) {
            return { ok: res.ok, status: res.status, text: text };
          });
        },
        function (err) { throw networkError(url, err); }
      )
      .then(function (reply) {
        clear();
        if (!reply.ok) { throw httpError(reply); }
        if (!reply.text) { return {}; }
        try {
          return JSON.parse(reply.text);
        } catch (err) {
          throw apiError(
            '后端返回的不是 JSON（HTTP ' + reply.status + '），更像一个网页。请确认 API 基址指向的是后端服务。',
            { status: reply.status, html: true, raw: reply.text }
          );
        }
      })
      .catch(function (err) { clear(); throw err; });
  }

  /* -- 渲染工具 ------------------------------------------------------------ */

  function inline(text) {
    return esc(text).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  }

  /* 极简 Markdown：只支持标题、无序列表、加粗、段落。后端返回的 Markdown
   * 结构固定，没必要为此引入解析器。 */
  function renderMarkdown(src) {
    var out = [];
    var listOpen = false;
    var closeList = function () { if (listOpen) { out.push('</ul>'); listOpen = false; } };
    String(src || '').split(/\r?\n/).forEach(function (raw) {
      var line = raw.replace(/\s+$/, '');
      if (/^#{1,4}\s+/.test(line)) {
        closeList();
        out.push('<h4>' + inline(line.replace(/^#{1,4}\s+/, '')) + '</h4>');
      } else if (/^[-*]\s+/.test(line)) {
        if (!listOpen) { out.push('<ul>'); listOpen = true; }
        out.push('<li>' + inline(line.replace(/^[-*]\s+/, '')) + '</li>');
      } else if (!line.trim()) {
        closeList();
      } else {
        closeList();
        out.push('<p>' + inline(line) + '</p>');
      }
    });
    closeList();
    return out.join('');
  }

  function setResult(id, html) {
    var node = byId(id);
    if (node) { node.innerHTML = html; }
  }

  function showError(id, err) {
    var node = byId(id);
    if (!node) { return; }
    node.innerHTML = '<p class="butler-error">' + esc((err && err.message) || String(err)) + '</p>'
      + rawBlock(err);
  }

  function clearResult(id) {
    setResult(id, '');
  }

  function busy(button, on) {
    if (!button) { return; }
    button.disabled = !!on;
    if (on) { button.setAttribute('aria-busy', 'true'); } else { button.removeAttribute('aria-busy'); }
  }

  function setChip(node, text, modifier) {
    if (!node) { return; }
    node.textContent = text;
    node.className = 'butler-chip' + (modifier ? ' ' + modifier : '');
  }

  function openSettings() {
    var panel = byId('settings-panel');
    if (!panel) { return; }
    panel.hidden = false;
    var field = byId('set-api-base');
    if (field) { field.focus(); }
  }

  /* -- 全局连接横幅 -------------------------------------------------------- */
  /* 连接状态是全局事实。之前它被写进「① 随手录入」的结果区，用户会以为入库失败——
   * 这是把基础设施问题伪装成业务问题，必须升级为页面级单一事实源。 */

  function renderBanner(health) {
    var node = byId('butler-banner');
    if (!node) { return; }
    var notes = [];
    var body;

    if (state.connection === 'ok') {
      if (health && health.storage === 'memory') {
        notes.push('当前用内存存储，进程重启后记录会消失——接上 Supabase 才能长期保留。');
      }
      if (health && !health.llm_ready) {
        notes.push('没有接入大模型，分类、关联、问答等能力正以启发式规则运行，结果依旧可用。');
      }
      if (!notes.length) {
        node.hidden = true;
        node.innerHTML = '';
        return;
      }
      node.hidden = false;
      node.className = 'butler-banner is-info';
      node.innerHTML = '<strong>后端已连接</strong><span>' + esc(notes.join(' ')) + '</span>';
      return;
    }

    if (state.connection === 'checking') {
      node.hidden = false;
      node.className = 'butler-banner is-info';
      node.innerHTML = '<strong>正在连接后端…</strong>';
      return;
    }

    var unconfigured = state.connection === 'unconfigured';
    body = '<strong>' + (unconfigured ? '还没有连接后端' : '连不上后端') + '</strong>';
    if (state.error) {
      body += '<p class="butler-banner-msg">' + esc(state.error.message) + '</p>';
    }
    body += '<p class="butler-banner-hint">'
      + (unconfigured
        ? '把「API 基址」填成你部署好的后端地址即可，例如 <code>https://info-butler-api.example.com</code>；本地开发时是 <code>http://127.0.0.1:8787</code>。'
        : '确认后端进程在运行、地址可达；跨域部署时后端需把本站域名加入 <code>CORS_ORIGINS</code>。')
      + '</p>';
    body += '<div class="butler-row">'
      + '<button type="button" class="butler-btn" data-action="open-settings">填写后端地址</button>'
      + '<button type="button" class="butler-btn butler-btn-ghost" data-action="retry">重新连接</button>'
      + '</div>';
    body += rawBlock(state.error);

    node.hidden = false;
    node.className = 'butler-banner is-error';
    node.innerHTML = body;
  }

  function refreshStatus() {
    var storage = byId('status-storage');
    var llm = byId('status-llm');
    setChip(storage, '存储：检测中', '');
    setChip(llm, '模型：检测中', '');
    state.connection = 'checking';
    state.error = null;
    renderBanner();

    call('/api/health').then(function (data) {
      state.connection = 'ok';
      var cloud = data.storage === 'cloud';
      var ready = !!data.llm_ready;
      setChip(storage, cloud ? '存储：云端' : '存储：内存（重启即失）', cloud ? 'is-ok' : 'is-warn');
      // 说清模型来自哪里：页面 BYOK 与服务端配置是两条完全不同的运维路径
      var origin = data.llm_source === 'byok' ? '（页面 BYOK）' : (data.llm_source === 'server' ? '（服务端）' : '');
      setChip(llm, ready ? '模型：已接入' + origin : '模型：未接入（降级运行）', ready ? 'is-ok' : 'is-warn');
      renderBanner(data);
      search();
    }, function (err) {
      // 有显式基址说明「配了连不上」；没有则是「还没配」——两种动作不同。
      state.connection = explicitBase() ? 'failed' : 'unconfigured';
      state.error = err;
      setChip(storage, '存储：未连接', 'is-warn');
      setChip(llm, '模型：未知', 'is-warn');
      renderBanner();
      renderItems([]);
      setResult('item-list', '<p class="butler-muted">连接后端之后，你的记录会出现在这里。</p>');
    });
  }

  /* -- 条目渲染 ------------------------------------------------------------ */

  var KIND_LABEL = { idea: '想法', material: '资料', todo: '待办' };

  function renderItems(items) {
    var box = byId('item-list');
    if (!box) { return; }
    if (!items || !items.length) {
      box.innerHTML = '<p class="butler-muted">没有匹配的记录。</p>';
      return;
    }
    box.innerHTML = items.map(function (item) {
      var score = item.score ? '<span class="butler-badge">相关度 ' + Number(item.score).toFixed(2) + '</span>' : '';
      var tags = (item.tags || []).map(function (t) { return '<span class="butler-badge">#' + esc(t) + '</span>'; }).join('');
      return '<div class="butler-item">'
        + '<div class="butler-item-head">'
        + '<span class="butler-item-title">' + esc(item.title || '(无标题)') + '</span>'
        + '<span class="butler-badge">' + esc(KIND_LABEL[item.kind] || item.kind || '记录') + '</span>'
        + score
        + '</div>'
        + '<p class="butler-item-summary">' + esc(item.summary || item.content || '') + '</p>'
        + '<div class="butler-tags">' + tags + '</div>'
        + '</div>';
    }).join('');
  }

  function search() {
    var box = byId('item-list');
    if (state.connection !== 'ok') {
      renderItems([]);
      if (state.connection !== 'checking') {
        setResult('item-list', '<p class="butler-muted">连接后端之后，你的记录会出现在这里。</p>');
      }
      return;
    }
    var query = (byId('search-input') || {}).value || '';
    var params = '?limit=50';
    if (query.trim()) { params += '&q=' + encodeURIComponent(query.trim()); }
    if (filterKind) { params += '&kind=' + encodeURIComponent(filterKind); }
    if (box) { box.innerHTML = '<p class="butler-muted">检索中…</p>'; }
    call('/api/items' + params).then(function (data) {
      renderItems(data.items || []);
    }, function (err) {
      renderItems([]);
      showError('item-list', err);
    });
  }

  /* -- 动作 ---------------------------------------------------------------- */

  function capture() {
    var button = byId('btn-capture');
    var text = ((byId('composer') || {}).value || '').trim();
    if (!text) {
      setResult('capture-result', '<p class="butler-error">先写点什么再入库。</p>');
      return;
    }
    busy(button, true);
    clearResult('capture-result');
    call('/api/items', { method: 'POST', body: { content: text } }).then(function (data) {
      var item = data.item || {};
      var html = '<p>已入库：<strong>' + esc(item.title) + '</strong>'
        + ' <span class="butler-badge">' + esc(KIND_LABEL[item.kind] || item.kind) + '</span></p>'
        + '<p class="butler-muted">' + esc(item.summary || '') + '</p>';
      if ((item.tags || []).length) {
        html += '<div class="butler-tags">' + item.tags.map(function (t) {
          return '<span class="butler-badge">#' + esc(t) + '</span>';
        }).join('') + '</div>';
      }
      if ((data.links || []).length) {
        html += '<h4>关联到已有内容</h4><ul>' + data.links.map(function (l) {
          return '<li>' + esc(l.title) + ' —— ' + esc(l.reason) + '</li>';
        }).join('') + '</ul>';
      }
      if ((data.todos || []).length) {
        html += '<h4>派生待办</h4><ul>' + data.todos.map(function (t) {
          return '<li>P' + esc(t.priority) + ' ' + esc(t.title) + '</li>';
        }).join('') + '</ul>';
      }
      setResult('capture-result', html);
      if (byId('composer')) { byId('composer').value = ''; }
      search();
    }, function (err) {
      showError('capture-result', err);
    }).then(function () { busy(button, false); });
  }

  function ask() {
    var question = ((byId('ask-input') || {}).value || '').trim();
    if (!question) {
      setResult('ask-result', '<p class="butler-error">先输入一个问题。</p>');
      return;
    }
    busy(byId('btn-ask'), true);
    clearResult('ask-result');
    call('/api/ask', { method: 'POST', body: { question: question } }).then(function (data) {
      var html = renderMarkdown(data.answer);
      if ((data.citations || []).length) {
        html += '<h4>引用</h4><ul>' + data.citations.map(function (c, i) {
          return '<li>[' + (i + 1) + '] ' + esc(c.title) + '</li>';
        }).join('') + '</ul>';
      }
      setResult('ask-result', html);
    }, function (err) {
      showError('ask-result', err);
    }).then(function () { busy(byId('btn-ask'), false); });
  }

  function extract() {
    busy(byId('btn-extract'), true);
    clearResult('extract-result');
    call('/api/extract', { method: 'POST', body: { limit: 40, scope: 'recent' } })
      .then(function (data) { setResult('extract-result', renderMarkdown(data.markdown)); },
        function (err) { showError('extract-result', err); })
      .then(function () { busy(byId('btn-extract'), false); });
  }

  function todos() {
    busy(byId('btn-todos'), true);
    clearResult('todos-result');
    call('/api/todos').then(function (data) {
      var groups = data.groups || [];
      if (!groups.length) {
        setResult('todos-result', '<p class="butler-muted">当前没有未完成的待办。</p>');
        return;
      }
      var html = groups.map(function (g) {
        var items = (g.todos || []).map(function (t) {
          return '<li>P' + esc(t.priority) + ' ' + esc(t.title)
            + (t.reason ? ' <span class="butler-muted">（' + esc(t.reason) + '）</span>' : '') + '</li>';
        }).join('');
        return '<h4>' + esc(g.theme) + '</h4><ul>' + items + '</ul>';
      }).join('');
      if ((data.suggestions || []).length) {
        html += '<h4>推进建议</h4><ul>' + data.suggestions.map(function (s) {
          return '<li>' + esc(s) + '</li>';
        }).join('') + '</ul>';
      }
      setResult('todos-result', html);
    }, function (err) {
      showError('todos-result', err);
    }).then(function () { busy(byId('btn-todos'), false); });
  }

  function summary() {
    busy(byId('btn-summary'), true);
    clearResult('summary-result');
    call('/api/summary', { method: 'POST', body: { days: 7, limit: 200 } })
      .then(function (data) { setResult('summary-result', renderMarkdown(data.markdown)); },
        function (err) { showError('summary-result', err); })
      .then(function () { busy(byId('btn-summary'), false); });
  }

  /* -- 大模型卡片（BYOK） --------------------------------------------------- */
  /* 卡片的存在意义不是「填三个框」，而是把「我填的对不对」变成一次可验证的闭环。
   * 验证走后端代理而非浏览器直连：各家 provider 几乎都不允许浏览器跨域，
   * 直连只会得到一个分不清是 CORS 还是 Key 错的失败。 */

  function readLlmFields() {
    return {
      base: ((byId('set-llm-base') || {}).value || '').trim(),
      key: ((byId('set-llm-key') || {}).value || '').trim(),
      model: ((byId('set-llm-model') || {}).value || '').trim()
    };
  }

  function applyLlmFields(fields) {
    settings.llmBaseUrl = fields.base;
    settings.llmApiKey = fields.key;
    settings.llmModel = fields.model;
    persist();
  }

  function testLlm() {
    var fields = readLlmFields();
    if (!fields.base) {
      // 示例地址只写在输入框的 placeholder 里，脚本里不再抄一份——
      // 抄了就会让「前端不得硬编码域名」的守卫失效，且两处容易走样。
      setResult('llm-result', '<p class="butler-error">先填 Base URL（照输入框示例填，注意以 /v1 结尾）。</p>');
      return;
    }
    if (!fields.key) {
      setResult('llm-result', '<p class="butler-error">先填 API Key 再验证。</p>');
      return;
    }
    // 先落盘再请求：探针的凭据是靠请求头带出去的，而请求头读的是 settings
    applyLlmFields(fields);
    busy(byId('btn-llm-test'), true);
    setResult('llm-result', '<p class="butler-muted">正在用你填的凭据打一条 1 token 的探针…</p>');

    call('/api/llm/test', { method: 'POST' }).then(function (data) {
      if (data.ok) {
        setResult('llm-result', '<p>可用：模型 <strong>' + esc(data.model || '默认模型') + '</strong> 已就绪，'
          + '录入、问答、提取、整理与总结将由此模型接管。</p>');
        setChip(byId('status-llm'), '模型：已接入（页面 BYOK）', 'is-ok');
      } else {
        setResult('llm-result',
          '<p class="butler-error">' + esc(data.reason || '验证失败') + '</p>'
          + '<p class="butler-muted">凭据已存在本机浏览器，改完可以直接再验证一次。</p>');
        setChip(byId('status-llm'), '模型：未接入（降级运行）', 'is-warn');
      }
    }, function (err) {
      showError('llm-result', err);
    }).then(function () { busy(byId('btn-llm-test'), false); });
  }

  function clearLlm() {
    settings.llmBaseUrl = '';
    settings.llmApiKey = '';
    settings.llmModel = '';
    if (byId('set-llm-base')) { byId('set-llm-base').value = ''; }
    if (byId('set-llm-key')) { byId('set-llm-key').value = ''; }
    if (byId('set-llm-model')) { byId('set-llm-model').value = ''; }
    persist();
    setResult('llm-result', '<p class="butler-muted">已清除本机模型凭据，能力退回启发式规则，录入与检索不受影响。</p>');
    setChip(byId('status-llm'), '模型：未接入（降级运行）', 'is-warn');
  }

  /* -- 设置 ---------------------------------------------------------------- */

  function fillSettings() {
    if (byId('set-api-base')) { byId('set-api-base').value = settings.apiBase || ''; }
    if (byId('set-token')) { byId('set-token').value = settings.token || ''; }
    if (byId('set-llm-base')) { byId('set-llm-base').value = settings.llmBaseUrl || ''; }
    if (byId('set-llm-key')) { byId('set-llm-key').value = settings.llmApiKey || ''; }
    if (byId('set-llm-model')) { byId('set-llm-model').value = settings.llmModel || ''; }
  }

  function saveSettings() {
    // 设置面板只管「连到哪个后端」；模型凭据归大模型卡片自己管。
    // 两套凭据写在同一个按钮里，会让「清除模型凭据」变成一次猜谜。
    settings.apiBase = ((byId('set-api-base') || {}).value || '').trim();
    settings.token = ((byId('set-token') || {}).value || '').trim();
    persist();
    refreshStatus();
  }

  /* -- 绑定 ---------------------------------------------------------------- */

  function bind() {
    var on = function (id, event, handler) {
      var node = byId(id);
      if (node) { node.addEventListener(event, handler); }
    };

    on('btn-capture', 'click', capture);
    on('btn-search', 'click', search);
    on('search-input', 'keydown', function (e) { if (e.key === 'Enter') { search(); } });
    on('btn-ask', 'click', ask);
    on('ask-input', 'keydown', function (e) { if (e.key === 'Enter') { ask(); } });
    on('btn-extract', 'click', extract);
    on('btn-todos', 'click', todos);
    on('btn-summary', 'click', summary);
    on('btn-save-settings', 'click', saveSettings);
    on('btn-llm-test', 'click', testLlm);
    on('btn-llm-clear', 'click', clearLlm);
    on('btn-reconnect', 'click', refreshStatus);
    on('btn-toggle-settings', 'click', function () {
      var panel = byId('settings-panel');
      if (panel) { panel.hidden = !panel.hidden; }
    });
    on('btn-clear-settings', 'click', function () {
      settings = Object.assign({}, DEFAULTS);
      try { localStorage.removeItem(STORAGE_KEY); } catch (err) { /* 忽略 */ }
      fillSettings();
      clearResult('llm-result');
      refreshStatus();
    });

    // 横幅是动态重绘的，用事件委托，避免每次渲染后重新绑事件
    on('butler-banner', 'click', function (e) {
      var action = e.target && e.target.getAttribute
        ? e.target.getAttribute('data-action')
        : null;
      if (action === 'open-settings') { openSettings(); }
      if (action === 'retry') { refreshStatus(); }
    });

    var filters = byId('filter-kind');
    if (filters) {
      filters.addEventListener('click', function (e) {
        var tag = e.target.closest ? e.target.closest('.butler-tag') : null;
        if (!tag) { return; }
        Array.prototype.forEach.call(filters.querySelectorAll('.butler-tag'), function (node) {
          node.classList.remove('is-on');
        });
        tag.classList.add('is-on');
        filterKind = tag.getAttribute('data-kind') || '';
        search();
      });
    }
  }

  function init() {
    if (!byId('butler-app')) { return; }  // 非工作台页面不挂载
    // 工作台需要比阅读型页面更宽的内容区，用 body 类让 CSS 只在这一页生效
    document.body.classList.add('butler-page');
    fillSettings();
    bind();
    refreshStatus();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
