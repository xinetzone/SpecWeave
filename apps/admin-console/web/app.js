/* admin-console 后台单页逻辑（零构建，原生 JS）
   · 所有写请求携带 CSRF 双提交头
   · 所有用户内容渲染前经 esc() 转义，杜绝 XSS
   · 401 统一跳转登录页 */

(function () {
  'use strict';

  var state = {
    view: 'dashboard',
    page: 1,
    page_size: 20,
    total: 0,
    items: [],
    categories: [],
    tags: [],
    selected: {},
    selectedCount: 0,
    editing: null,
    formTags: [],
    user: null,
    degraded: false
  };

  var VIEWS = {
    dashboard: '数据看板',
    items: '内容列表',
    categories: '分类管理',
    tags: '标签管理',
    attachments: '云端附件',
    logs: '操作日志'
  };

  // ---------- 基础工具 ----------

  function $(id) { return document.getElementById(id); }

  function cookie(name) {
    var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[1]) : '';
  }

  function esc(value) {
    return String(value === null || value === undefined ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function fmtDate(text) {
    if (!text) return '—';
    var raw = String(text).replace('T', ' ').slice(0, 16);
    return esc(raw);
  }

  function fmtBytes(size) {
    var value = Number(size) || 0;
    if (value < 1024) return value + ' B';
    if (value < 1024 * 1024) return (value / 1024).toFixed(1) + ' KB';
    return (value / 1024 / 1024).toFixed(1) + ' MB';
  }

  function toast(message, kind) {
    var node = document.createElement('div');
    node.className = 'toast ' + (kind || '');
    node.textContent = message;
    $('toasts').appendChild(node);
    setTimeout(function () { node.remove(); }, 3200);
  }

  function api(path, options) {
    options = options || {};
    var headers = options.headers || {};
    headers['X-CSRF-Token'] = cookie('ac_csrf');
    if (options.json && options.body) headers['Content-Type'] = 'application/json';
    return fetch(path, {
      method: options.method || 'GET',
      credentials: 'same-origin',
      headers: headers,
      body: options.body
    }).then(function (response) {
      if (response.status === 401) {
        window.location.href = '/login';
        return Promise.reject(new Error('unauthorized'));
      }
      return response.json().catch(function () { return {}; }).then(function (data) {
        return { status: response.status, data: data };
      });
    });
  }

  function requestOk(result, fallback) {
    if (result.status >= 200 && result.status < 300) return true;
    toast((result.data && result.data.message) || fallback || '操作失败', 'err');
    return false;
  }

  // ---------- 视图切换 ----------

  function switchView(view) {
    state.view = view;
    Object.keys(VIEWS).forEach(function (key) {
      $('view-' + key).classList.toggle('hidden', key !== view);
    });
    Array.prototype.forEach.call(document.querySelectorAll('.nav-item'), function (node) {
      node.classList.toggle('active', node.getAttribute('data-view') === view);
    });
    $('view-title').textContent = VIEWS[view] || '';
    $('new-item').classList.toggle('hidden', view !== 'items' && view !== 'dashboard');
    $('refresh').classList.remove('hidden');
    closeSidebar();
    loadView();
  }

  function closeSidebar() { $('sidebar').classList.remove('open'); }

  function loadView() {
    if (state.view === 'dashboard') return loadDashboard();
    if (state.view === 'items') return loadItems();
    if (state.view === 'categories') return loadCategories();
    if (state.view === 'tags') return loadTags();
    if (state.view === 'attachments') return loadAttachments();
    if (state.view === 'logs') return loadLogs();
    return null;
  }

  // ---------- 看板 ----------

  function loadDashboard() {
    return api('/api/dashboard').then(function (result) {
      if (!requestOk(result, '看板加载失败')) return;
      var data = result.data;
      state.degraded = !!data.degraded;
      var byStatus = data.by_status || {};
      var attachments = data.attachments || {};
      var cards = [
        { label: '内容总数', value: data.total || 0, sub: (data.categories || 0) + ' 个分类 · ' + (data.tags || 0) + ' 个标签' },
        { label: '已发布', value: byStatus.published || 0, sub: '对外可见' },
        { label: '草稿 / 归档', value: (byStatus.draft || 0) + ' / ' + (byStatus.archived || 0), sub: '未发布内容' },
        { label: '云端附件', value: attachments.count || 0, sub: fmtBytes(attachments.bytes || 0) + ' 已用' }
      ];
      $('metrics').innerHTML = cards.map(function (card) {
        return '<div class="card metric"><div class="label">' + esc(card.label) +
          '</div><div class="value">' + esc(card.value) +
          '</div><div class="sub">' + esc(card.sub) + '</div></div>';
      }).join('');

      renderTrend(data.trend || []);
      renderDist(data.by_category || []);
      renderRecentLogs(data.logs || []);
      if (data.degraded) {
        var banner = $('banner');
        banner.textContent = '云端未配置或不可达，当前为内存降级模式：功能可演示，但数据不会持久化。';
        banner.classList.remove('hidden');
      } else {
        $('banner').classList.add('hidden');
      }
    });
  }

  function renderTrend(trend) {
    if (!trend.length) { $('trend-chart').innerHTML = ''; return; }
    var width = 560, height = 168, baseline = 148, gap = 8;
    var barWidth = (width - gap * (trend.length - 1)) / trend.length;
    var max = Math.max.apply(null, trend.map(function (p) { return p.count; }).concat([1]));
    var parts = [];
    trend.forEach(function (point, index) {
      var barHeight = Math.round((point.count / max) * 118);
      if (point.count > 0 && barHeight < 3) barHeight = 3;
      var x = index * (barWidth + gap);
      parts.push('<rect class="bar" x="' + x.toFixed(1) + '" y="' + (baseline - barHeight) +
        '" width="' + barWidth.toFixed(1) + '" height="' + barHeight + '" rx="3"><title>' +
        esc(point.date) + '：' + point.count + '</title></rect>');
      if (index % 3 === 0 || index === trend.length - 1) {
        parts.push('<text class="tick" x="' + (x + barWidth / 2).toFixed(1) + '" y="163" text-anchor="middle">' +
          esc(String(point.date).slice(5)) + '</text>');
      }
    });
    parts.push('<line class="axis" x1="0" y1="' + baseline + '" x2="' + width + '" y2="' + baseline + '"/>');
    $('trend-chart').innerHTML = parts.join('');
  }

  function renderDist(rows) {
    if (!rows.length) { $('dist').innerHTML = '<div class="empty">暂无分类数据</div>'; return; }
    var max = Math.max.apply(null, rows.map(function (r) { return r.count; }).concat([1]));
    $('dist').innerHTML = rows.map(function (row) {
      var percent = Math.round((row.count / max) * 100);
      return '<div class="dist-row"><span class="name">' + esc(row.name) +
        '</span><span class="dist-track"><span class="dist-fill" style="width:' + percent + '%"></span></span>' +
        '<span class="count">' + row.count + '</span></div>';
    }).join('');
  }

  function renderRecentLogs(logs) {
    if (!logs.length) { $('recent-logs').innerHTML = '<div class="empty">暂无操作记录</div>'; return; }
    $('recent-logs').innerHTML = logs.map(function (log) {
      return '<div style="display:flex;gap:10px;padding:7px 0;border-bottom:1px solid var(--border)">' +
        '<span class="mono" style="color:var(--muted);flex:none">' + fmtDate(log.created_at) + '</span>' +
        '<span style="flex:1;min-width:0">' + esc(log.detail || log.action) + '</span></div>';
    }).join('');
  }

  // ---------- 内容列表 ----------

  function loadItems() {
    var sort = $('sort').value.split(':');
    var query = {
      q: $('q').value.trim(),
      status: $('filter-status').value,
      category_id: $('filter-category').value,
      tag: $('filter-tag').value,
      sort: sort[0],
      order: sort[1],
      page: state.page,
      page_size: state.page_size
    };
    var params = Object.keys(query).filter(function (key) { return query[key]; }).map(function (key) {
      return encodeURIComponent(key) + '=' + encodeURIComponent(query[key]);
    }).join('&');
    return api('/api/items' + (params ? '?' + params : '')).then(function (result) {
      if (!requestOk(result, '列表加载失败')) return;
      state.items = result.data.items || [];
      state.total = result.data.total || 0;
      renderItems();
    });
  }

  function renderItems() {
    var body = $('items-body');
    body.innerHTML = state.items.map(function (item) {
      var tags = (item.tags || []).map(function (name) {
        return '<span class="tag-chip">' + esc(name) + '</span>';
      }).join('');
      return '<tr data-id="' + esc(item.id) + '">' +
        '<td class="col-check" data-label="选择"><input type="checkbox" class="row-check" data-id="' + esc(item.id) + '"' +
        (state.selected[item.id] ? ' checked' : '') + '></td>' +
        '<td class="title-cell" data-label="标题"><strong>' + esc(item.title) + '</strong>' +
        (item.summary ? '<small>' + esc(item.summary) + '</small>' : '') +
        (tags ? '<div style="margin-top:4px">' + tags + '</div>' : '') + '</td>' +
        '<td data-label="分类">' + esc(item.category_name || '—') + '</td>' +
        '<td data-label="状态"><span class="badge ' + esc(item.status) + '">' + statusLabel(item.status) + '</span></td>' +
        '<td data-label="更新时间">' + fmtDate(item.updated_at) + '</td>' +
        '<td class="col-actions" data-label="操作">' +
        '<button class="btn sm" data-edit="' + esc(item.id) + '">编辑</button> ' +
        '<button class="btn sm danger" data-del="' + esc(item.id) + '">删除</button></td>' +
        '</tr>';
    }).join('');
    $('items-empty').classList.toggle('hidden', state.items.length > 0);

    var pages = Math.max(Math.ceil(state.total / state.page_size), 1);
    $('pager-info').textContent = '共 ' + state.total + ' 条 · 第 ' + state.page + ' / ' + pages + ' 页';
    $('prev').disabled = state.page <= 1;
    $('next').disabled = state.page >= pages;
    updateBulk();
  }

  function statusLabel(value) {
    return { draft: '草稿', published: '已发布', archived: '已归档' }[value] || value;
  }

  function updateBulk() {
    var ids = Object.keys(state.selected).filter(function (id) { return state.selected[id]; });
    state.selectedCount = ids.length;
    $('bulkbar').classList.toggle('hidden', ids.length === 0);
    $('bulk-count').textContent = '已选 ' + ids.length + ' 条';
  }

  function selectedIds() {
    return Object.keys(state.selected).filter(function (id) { return state.selected[id]; });
  }

  // ---------- 分类 / 标签 ----------

  function loadCategories() {
    return api('/api/categories').then(function (result) {
      if (!requestOk(result, '分类加载失败')) return;
      state.categories = result.data.categories || [];
      $('cat-body').innerHTML = state.categories.map(function (category) {
        return '<tr data-id="' + esc(category.id) + '">' +
          '<td data-label="名称"><strong>' + esc(category.name) + '</strong></td>' +
          '<td data-label="别名" class="mono">' + esc(category.slug) + '</td>' +
          '<td data-label="排序">' + esc(category.sort_order) + '</td>' +
          '<td class="col-actions" data-label="操作">' +
          '<button class="btn sm" data-cat-edit="' + esc(category.id) + '">重命名</button> ' +
          '<button class="btn sm danger" data-cat-del="' + esc(category.id) + '">删除</button></td>' +
          '</tr>';
      }).join('');
      $('cat-empty').classList.toggle('hidden', state.categories.length > 0);
    });
  }

  function loadTags() {
    return api('/api/tags').then(function (result) {
      if (!requestOk(result, '标签加载失败')) return;
      state.tags = result.data.tags || [];
      $('tag-list').innerHTML = state.tags.map(function (tag) {
        return '<span class="chip" style="padding:5px 6px 5px 11px">' + esc(tag.name) +
          '<button data-tag-del="' + esc(tag.id) + '" title="删除">✕</button></span>';
      }).join('');
      $('tag-empty').classList.toggle('hidden', state.tags.length > 0);
    });
  }

  // ---------- 附件 ----------

  function loadAttachments() {
    return api('/api/attachments').then(function (result) {
      if (!requestOk(result, '附件加载失败')) return;
      var rows = result.data.attachments || [];
      $('attachment-grid').innerHTML = rows.map(function (file) {
        var isImage = String(file.content_type || '').indexOf('image/') === 0;
        var preview = isImage
          ? '<img src="' + esc(file.url) + '" alt="' + esc(file.filename) + '">'
          : esc(file.content_type || '文件');
        return '<div class="attachment-card"><div class="preview">' + preview + '</div>' +
          '<div class="meta"><span class="name" title="' + esc(file.filename) + '">' + esc(file.filename) + '</span>' +
          '<span class="muted">' + fmtBytes(file.size) + '</span> ' +
          '<button class="btn sm danger" data-att-del="' + esc(file.id) + '" style="margin-top:6px">删除</button></div></div>';
      }).join('');
      $('att-empty').classList.toggle('hidden', rows.length > 0);
    });
  }

  // ---------- 日志 ----------

  function loadLogs() {
    return api('/api/logs?limit=50').then(function (result) {
      if (!requestOk(result, '日志加载失败')) return;
      var rows = result.data.logs || [];
      $('logs-body').innerHTML = rows.map(function (log) {
        return '<tr><td data-label="时间">' + fmtDate(log.created_at) + '</td>' +
          '<td data-label="操作者">' + esc(log.actor) + '</td>' +
          '<td data-label="动作">' + esc(log.action) + '</td>' +
          '<td data-label="说明">' + esc(log.detail) + '</td></tr>';
      }).join('');
      $('logs-empty').classList.toggle('hidden', rows.length > 0);
    });
  }

  // ---------- 抽屉表单 ----------

  function openDrawer(item) {
    state.editing = item || null;
    state.formTags = item ? (item.tags || []).slice() : [];
    $('drawer-title').textContent = item ? '编辑内容' : '新建内容';
    $('f-title').value = item ? item.title : '';
    $('f-slug').value = item ? (item.slug || '') : '';
    $('f-summary').value = item ? (item.summary || '') : '';
    $('f-body').value = item ? (item.body || '') : '';
    $('f-tags').value = '';
    renderTagChips();
    renderStatusOptions(item ? item.status : 'draft');
    renderCategoryOptions(item ? item.category_id : '');
    renderCover(item ? item.cover_url : '');
    $('form-files').innerHTML = '';
    $('drawer').classList.add('open');
    $('drawer-mask').classList.add('open');
  }

  function closeDrawer() {
    $('drawer').classList.remove('open');
    $('drawer-mask').classList.remove('open');
    state.editing = null;
  }

  function renderStatusOptions(current) {
    var options = [['draft', '草稿'], ['published', '已发布'], ['archived', '已归档']];
    $('f-status').innerHTML = options.map(function (pair) {
      return '<option value="' + pair[0] + '"' + (pair[0] === current ? ' selected' : '') + '>' + pair[1] + '</option>';
    }).join('');
  }

  function renderCategoryOptions(current) {
    $('f-category').innerHTML = '<option value="">未分类</option>' + state.categories.map(function (category) {
      return '<option value="' + esc(category.id) + '"' +
        (category.id === current ? ' selected' : '') + '>' + esc(category.name) + '</option>';
    }).join('');
  }

  function renderTagChips() {
    $('f-tag-chips').innerHTML = state.formTags.map(function (name, index) {
      return '<span class="chip">' + esc(name) +
        '<button data-chip-remove="' + index + '">✕</button></span>';
    }).join('');
  }

  function renderCover(url) {
    var row = $('cover-row');
    if (!url) { row.classList.add('hidden'); return; }
    row.classList.remove('hidden');
    $('cover-preview').src = url;
    $('cover-url').textContent = url;
  }

  function saveItem() {
    var payload = {
      title: $('f-title').value.trim(),
      slug: $('f-slug').value.trim(),
      summary: $('f-summary').value.trim(),
      body: $('f-body').value,
      status: $('f-status').value,
      category_id: $('f-category').value || null,
      cover_url: $('cover-url').textContent || '',
      tags: state.formTags
    };
    if (!payload.title) { toast('标题不能为空', 'err'); return; }
    var editing = state.editing;
    if (editing) payload.expected_updated_at = editing.updated_at || '';
    var body = JSON.stringify(payload);
    var target = editing ? '/api/items/' + encodeURIComponent(editing.id) : '/api/items';
    api(target, { method: editing ? 'PATCH' : 'POST', body: body, json: true }).then(function (result) {
      if (!requestOk(result, '保存失败')) return;
      toast(editing ? '已保存' : '已创建', 'ok');
      closeDrawer();
      loadMeta().then(function () {
        if (state.view === 'items') return loadItems();
        return loadDashboard();
      });
    });
  }

  // ---------- 上传 ----------

  function uploadFiles(files, itemId, listNode) {
    Array.prototype.forEach.call(files, function (file) {
      var headers = {
        'Content-Type': file.type || 'application/octet-stream',
        'X-File-Name': encodeURIComponent(file.name)
      };
      if (itemId) headers['X-Item-Id'] = itemId;
      api('/api/uploads', { method: 'POST', body: file, headers: headers }).then(function (result) {
        if (!requestOk(result, '上传失败')) return;
        var attachment = result.data.attachment || {};
        toast('已上传：' + file.name, 'ok');
        if (listNode) {
          var node = document.createElement('div');
          node.className = 'file-item';
          node.innerHTML = '<span class="name">' + esc(attachment.filename || file.name) + '</span>' +
            '<span class="size">' + fmtBytes(attachment.size || file.size) + '</span>';
          listNode.appendChild(node);
        }
        if (String(file.type || '').indexOf('image/') === 0 && attachment.url) {
          renderCover(attachment.url);
        }
        if (state.view === 'attachments') loadAttachments();
      });
    });
  }

  // ---------- 元数据 ----------

  function loadMeta() {
    return api('/api/meta').then(function (result) {
      if (!requestOk(result, '元数据加载失败')) return;
      var meta = result.data;
      state.categories = meta.categories || [];
      state.tags = meta.tags || [];
      state.user = meta.user || null;
      $('who').textContent = state.user
        ? (state.user.display_name || state.user.email) + '（' + state.user.role + '）'
        : '—';
      var statuses = meta.statuses || [];
      $('filter-status').innerHTML = '<option value="">全部状态</option>' + statuses.map(function (item) {
        return '<option value="' + esc(item.value) + '">' + esc(item.label) + '</option>';
      }).join('');
      $('filter-category').innerHTML = '<option value="">全部分类</option>' +
        '<option value="__none__">未分类</option>' + state.categories.map(function (category) {
          return '<option value="' + esc(category.id) + '">' + esc(category.name) + '</option>';
        }).join('');
      $('filter-tag').innerHTML = '<option value="">全部标签</option>' + state.tags.map(function (name) {
        return '<option value="' + esc(name) + '">' + esc(name) + '</option>';
      }).join('');
      var limit = (meta.upload && meta.upload.max_bytes) || 0;
      $('upload-limit').textContent = '单文件上限 ' + fmtBytes(limit) +
        (meta.upload && meta.upload.enabled ? '' : '（云端存储未启用）');
    });
  }

  // ---------- 事件绑定 ----------

  function bind() {
    Array.prototype.forEach.call(document.querySelectorAll('.nav-item'), function (node) {
      node.addEventListener('click', function () { switchView(node.getAttribute('data-view')); });
    });

    $('menu-toggle').addEventListener('click', function () { $('sidebar').classList.toggle('open'); });
    $('refresh').addEventListener('click', function () { loadMeta().then(loadView); });
    $('new-item').addEventListener('click', function () { openDrawer(null); });

    $('logout').addEventListener('click', function () {
      api('/api/auth/logout', { method: 'POST', body: '{}', json: true }).then(function () {
        window.location.href = '/login';
      });
    });

    $('search').addEventListener('click', function () { state.page = 1; loadItems(); });
    $('q').addEventListener('keydown', function (event) {
      if (event.key === 'Enter') { state.page = 1; loadItems(); }
    });
    ['filter-status', 'filter-category', 'filter-tag', 'sort'].forEach(function (id) {
      $(id).addEventListener('change', function () { state.page = 1; loadItems(); });
    });
    $('prev').addEventListener('click', function () {
      if (state.page > 1) { state.page -= 1; loadItems(); }
    });
    $('next').addEventListener('click', function () { state.page += 1; loadItems(); });

    $('check-all').addEventListener('change', function (event) {
      state.items.forEach(function (item) { state.selected[item.id] = event.target.checked; });
      renderItems();
    });

    document.addEventListener('click', function (event) {
      var target = event.target;
      if (!(target instanceof HTMLElement)) return;

      if (target.classList.contains('row-check')) {
        state.selected[target.getAttribute('data-id')] = target.checked;
        updateBulk();
        return;
      }
      var editId = target.getAttribute('data-edit');
      if (editId) {
        var found = state.items.filter(function (item) { return item.id === editId; })[0];
        if (found) openDrawer(found);
        return;
      }
      var delId = target.getAttribute('data-del');
      if (delId) {
        if (!window.confirm('确认删除这条内容？')) return;
        api('/api/items/' + encodeURIComponent(delId), { method: 'DELETE', body: '{}', json: true })
          .then(function (result) { if (requestOk(result, '删除失败')) { toast('已删除', 'ok'); loadItems(); } });
        return;
      }
      var bulk = target.getAttribute('data-bulk');
      if (bulk) {
        var ids = selectedIds();
        if (!ids.length) return;
        if (bulk === 'delete' && !window.confirm('确认删除选中的 ' + ids.length + ' 条内容？')) return;
        api('/api/items/bulk', {
          method: 'POST', json: true,
          body: JSON.stringify({ ids: ids, action: bulk })
        }).then(function (result) {
          if (!requestOk(result, '批量操作失败')) return;
          state.selected = {};
          toast('已处理 ' + ids.length + ' 条', 'ok');
          loadItems();
        });
        return;
      }
      var catDel = target.getAttribute('data-cat-del');
      if (catDel) {
        api('/api/categories/' + encodeURIComponent(catDel), { method: 'DELETE', body: '{}', json: true })
          .then(function (result) { if (requestOk(result, '删除失败')) { toast('已删除', 'ok'); loadCategories(); } });
        return;
      }
      if (target.getAttribute('data-cat-edit')) {
        var id = target.getAttribute('data-cat-edit');
        var current = state.categories.filter(function (c) { return c.id === id; })[0];
        var name = window.prompt('重命名分类', current ? current.name : '');
        if (!name) return;
        api('/api/categories/' + encodeURIComponent(id), {
          method: 'PATCH', json: true, body: JSON.stringify({ name: name })
        }).then(function (result) { if (requestOk(result, '重命名失败')) { toast('已更新', 'ok'); loadCategories(); } });
        return;
      }
      var tagDel = target.getAttribute('data-tag-del');
      if (tagDel) {
        api('/api/tags/' + encodeURIComponent(tagDel), { method: 'DELETE', body: '{}', json: true })
          .then(function (result) { if (requestOk(result, '删除失败')) { toast('已删除', 'ok'); loadTags(); } });
        return;
      }
      var attDel = target.getAttribute('data-att-del');
      if (attDel) {
        if (!window.confirm('确认删除该附件（云端对象一并删除）？')) return;
        api('/api/attachments/' + encodeURIComponent(attDel), { method: 'DELETE', body: '{}', json: true })
          .then(function (result) { if (requestOk(result, '删除失败')) { toast('已删除', 'ok'); loadAttachments(); } });
        return;
      }
      var chipRemove = target.getAttribute('data-chip-remove');
      if (chipRemove !== null && chipRemove !== undefined) {
        state.formTags.splice(Number(chipRemove), 1);
        renderTagChips();
      }
    });

    $('cat-add').addEventListener('click', function () {
      var name = $('cat-name').value.trim();
      if (!name) { toast('请输入分类名称', 'err'); return; }
      api('/api/categories', { method: 'POST', json: true, body: JSON.stringify({ name: name }) })
        .then(function (result) {
          if (!requestOk(result, '添加失败')) return;
          $('cat-name').value = '';
          toast('已添加', 'ok');
          loadMeta().then(loadCategories);
        });
    });

    $('tag-add').addEventListener('click', function () {
      var name = $('tag-name').value.trim();
      if (!name) { toast('请输入标签名称', 'err'); return; }
      api('/api/tags', { method: 'POST', json: true, body: JSON.stringify({ name: name }) })
        .then(function (result) {
          if (!requestOk(result, '添加失败')) return;
          $('tag-name').value = '';
          toast('已添加', 'ok');
          loadTags();
        });
    });

    // 附件上传
    var dropzone = $('dropzone');
    var fileInput = $('file-input');
    dropzone.addEventListener('click', function () { fileInput.click(); });
    fileInput.addEventListener('change', function () { uploadFiles(fileInput.files, '', null); fileInput.value = ''; });
    ['dragenter', 'dragover'].forEach(function (type) {
      dropzone.addEventListener(type, function (event) { event.preventDefault(); dropzone.classList.add('drag'); });
    });
    ['dragleave', 'drop'].forEach(function (type) {
      dropzone.addEventListener(type, function (event) { event.preventDefault(); dropzone.classList.remove('drag'); });
    });
    dropzone.addEventListener('drop', function (event) {
      if (event.dataTransfer) uploadFiles(event.dataTransfer.files, '', null);
    });

    // 表单内上传
    var formDrop = $('form-dropzone');
    var formFile = $('form-file');
    formDrop.addEventListener('click', function () { formFile.click(); });
    formFile.addEventListener('change', function () {
      uploadFiles(formFile.files, state.editing ? state.editing.id : '', $('form-files'));
      formFile.value = '';
    });

    // 标签输入
    $('f-tags').addEventListener('keydown', function (event) {
      if (event.key !== 'Enter' && event.key !== ',') return;
      event.preventDefault();
      var values = $('f-tags').value.split(/[,，]/).map(function (v) { return v.trim(); }).filter(Boolean);
      values.forEach(function (value) {
        if (state.formTags.indexOf(value) === -1) state.formTags.push(value);
      });
      $('f-tags').value = '';
      renderTagChips();
    });
    $('f-tags').addEventListener('blur', function () {
      var value = $('f-tags').value.trim();
      if (!value) return;
      if (state.formTags.indexOf(value) === -1) state.formTags.push(value);
      $('f-tags').value = '';
      renderTagChips();
    });

    $('cover-clear').addEventListener('click', function () { renderCover(''); });
    $('drawer-close').addEventListener('click', closeDrawer);
    $('drawer-cancel').addEventListener('click', closeDrawer);
    $('drawer-mask').addEventListener('click', closeDrawer);
    $('drawer-save').addEventListener('click', saveItem);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeDrawer();
    });
  }

  // ---------- 启动 ----------

  api('/api/auth/me').then(function (result) {
    if (result.status !== 200) { window.location.href = '/login'; return; }
    loadMeta().then(function () {
      bind();
      switchView('dashboard');
    });
  }).catch(function () { window.location.href = '/login'; });
})();
