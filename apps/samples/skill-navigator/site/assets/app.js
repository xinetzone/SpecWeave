/* ===========================================================
   Skill 导航台 · 逻辑层
   - 零网络请求：全部计算在本地完成
   - 推荐 = 策展首选（data.js 的 pain.top）+ 标签加权命中 + 使用量决胜
   - 每次推荐都回显「命中了什么」，不只给结论
   =========================================================== */

(function () {
  'use strict';

  var D = window.SKILL_DATA;
  if (!D) { return; }

  var skillById = {};
  D.skills.forEach(function (s) { skillById[s.id] = s; });

  /* ------------------------- 自由输入 → 标签 ------------------------- */

  var KEYWORDS = [
    { tags: ['web'], words: ['网页', '网站', '官网', '落地页', 'landing', '页面', '前端'] },
    { tags: ['app'], words: ['app', '应用', '小程序', '工具', '软件', '系统'] },
    { tags: ['design', 'ui-polish'], words: ['设计', '界面', 'ui', '视觉', '好看', '好看点', '丑', '美观', '美化', '风格', '配色'] },
    { tags: ['prototype'], words: ['设计稿', 'figma', '截图', '还原', '像素'] },
    { tags: ['slide'], words: ['ppt', '演示', '汇报', '幻灯片', '课件', '路演', '讲稿'] },
    { tags: ['image', 'cover'], words: ['图片', '配图', '海报', '封面', '插画', '出图', '生成图'] },
    { tags: ['video'], words: ['视频', '剪辑', '短片', '口播', '录屏'] },
    { tags: ['animation'], words: ['动画', '白板', '动效'] },
    { tags: ['doc'], words: ['文档', '写文档', '说明书', '方案', '报告'] },
    { tags: ['content', 'xhs'], words: ['文案', '内容', '标题', '笔记', '公众号', '小红书', '选题', '爆款', '热点', '蹭'] },
    { tags: ['teach'], words: ['课程', '教学', '教学生', '培训', '教材', '学生', '阅读应用'] },
    { tags: ['data', 'map'], words: ['数据', '图表', '看板', '统计', '地图', '可视化', '区域'] },
    { tags: ['idea-validate', 'brainstorm'], words: ['想法', '模糊', '值不值得', '有没有需求', '靠谱', '验证', '调研', '没思路', '想不出来', '不知道做不做'] },
    { tags: ['launch', 'audience'], words: ['推广', '没人用', '冷启动', '获客', '引流', '涨粉', '星标', '首发', '发布', '第一批', '没曝光'] },
    { tags: ['growth'], words: ['增长', '留存', '活跃', '转化率', '复购', '卡住'] },
    { tags: ['pricing'], words: ['定价', '收费', '卖钱', '变现', '多少钱', '付费', '订阅'] },
    { tags: ['price-cost'], words: ['成本', '亏', '核算', '烧钱'] },
    { tags: ['code-quality', 'dev'], words: ['bug', '报错', '代码', '测试', '审查', '漏洞', '崩溃', '跑不通'] },
    { tags: ['feedback'], words: ['反馈', '评论', '差评', '问卷', '访谈', '客服'] },
    { tags: ['plan'], words: ['计划', '排期', '拆任务', '项目管理', '实施']
    }
  ];

  function tagsFromText(text) {
    var t = (text || '').toLowerCase();
    var hits = [];
    KEYWORDS.forEach(function (k) {
      var hit = k.words.some(function (w) { return t.indexOf(w.toLowerCase()) !== -1; });
      if (hit) k.tags.forEach(function (g) { if (hits.indexOf(g) === -1) hits.push(g); });
    });
    return hits;
  }

  /* ------------------------- 打分与排序 ------------------------- */

  function score(skill, tags) {
    var matched = skill.tags.filter(function (t) { return tags.indexOf(t) !== -1; });
    return { matched: matched, value: matched.length };
  }

  function rank(skills, tags, pinned) {
    return skills
      .map(function (s) {
        var sc = score(s, tags);
        var pin = (pinned || []).indexOf(s.id);
        return { skill: s, matched: sc.matched, value: sc.value, pin: pin === -1 ? 999 : pin };
      })
      .filter(function (r) { return r.value > 0; })
      .sort(function (a, b) {
        if (a.pin !== b.pin) return a.pin - b.pin;
        if (b.value !== a.value) return b.value - a.value;
        var ua = typeof a.skill.usage === 'number' ? a.skill.usage : -1;
        var ub = typeof b.skill.usage === 'number' ? b.skill.usage : -1;
        if (ub !== ua) return ub - ua;
        return a.skill.name.localeCompare(b.skill.name, 'zh');
      });
  }

  function recommend(pain) {
    var ranked = rank(D.skills, pain.tags, pain.top || []);
    return { ranked: ranked, shown: ranked.slice(0, 2), rest: ranked.slice(2), pain: pain };
  }

  function recommendByText(text) {
    var tags = tagsFromText(text);
    if (!tags.length) return null;
    // 找一张与该输入最接近的痛点卡，用它的策展首选兜底
    var best = null, bestHit = -1;
    D.pains.forEach(function (p) {
      var hit = p.tags.filter(function (t) { return tags.indexOf(t) !== -1; }).length;
      if (hit > bestHit) { bestHit = hit; best = p; }
    });
    var ranked = rank(D.skills, tags, (best && bestHit >= 2) ? best.top : []);
    return { ranked: ranked, shown: ranked.slice(0, 2), rest: ranked.slice(2), tags: tags, pain: null };
  }

  /* ------------------------- 渲染工具 ------------------------- */

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function chip(label, hit) {
    return el('span', 'chip' + (hit ? ' chip-hit' : ''), label);
  }

  function usageText(s) {
    return typeof s.usage === 'number'
      ? '累计使用 ' + s.usage.toLocaleString('en-US') + ' 次'
      : '使用量：事件页未提供';
  }

  function sourceText(s) {
    return s.source === 'market' ? '数据来自 Meoo 技能市场页' : '数据来自赏金广场共创计划页';
  }

  function tagLabels(tags) {
    return tags.map(function (t) { return D.tagLabels[t] || t; });
  }

  /* ------------------------- DOM 引用 ------------------------- */

  var $ = function (id) { return document.getElementById(id); };
  var groupsBox = $('pain-groups');
  var resultSec = $('result');
  var fallbackSec = $('fallback');
  var cardsBox = $('cards');
  var basisEl = $('result-basis');
  var fallbackBasis = $('fallback-basis');
  var fallbackList = $('fallback-list');
  var showMoreBtn = $('show-more');
  var demoLayer = $('demo');
  var demoTitle = $('demo-title');
  var demoSub = $('demo-sub');
  var demoBody = $('demo-body');
  var demoMarket = $('demo-market');
  var lastFocus = null;
  var currentRest = [];
  var hasMore = false;

  /* ------------------------- 渲染：痛点卡 ------------------------- */

  function renderPains() {
    var order = [];
    D.pains.forEach(function (p) { if (order.indexOf(p.group) === -1) order.push(p.group); });

    order.forEach(function (g) {
      var box = el('div', 'pain-group');
      box.appendChild(el('h3', 'pain-group-title', g));
      var list = el('div', 'pain-list');
      D.pains.filter(function (p) { return p.group === g; }).forEach(function (p) {
        var b = el('button', 'pain-card', p.label);
        b.type = 'button';
        b.setAttribute('data-pain', p.id);
        b.addEventListener('click', function () { showPain(p); });
        list.appendChild(b);
      });
      box.appendChild(list);
      groupsBox.appendChild(box);
    });
  }

  /* ------------------------- 渲染：结果卡 ------------------------- */

  function cardNode(rec, index) {
    var s = rec.skill;
    var card = el('article', 'card');

    card.appendChild(el('span', 'card-rank', index === 0 ? '最对得上' : '也可以考虑'));
    card.appendChild(el('h3', null, s.name));
    card.appendChild(el('p', 'card-by', '作者 ' + s.author + ' · ' + usageText(s)));

    card.appendChild(el('p', 'card-solve', s.solve));

    var chips = el('div', 'chips');
    tagLabels(s.tags).forEach(function (label, i) {
      var t = s.tags[i];
      chips.appendChild(chip(label, rec.matched.indexOf(t) !== -1));
    });
    card.appendChild(chips);

    // 匹配理由（回显命中了什么）
    var why = el('div', 'card-grid');
    var dt = el('dt', null, '为什么是它');
    var dd = el('dd', null,
      '命中了你说到的「' + tagLabels(rec.matched).join('」「') + '」——匹配分 ' + rec.value +
      '（每命中 1 个点记 1 分，结果按匹配分从高到低排）。');
    why.appendChild(dt); why.appendChild(dd);
    card.appendChild(why);

    // 折叠详情
    var det = el('details', 'card-details');
    var sum = el('summary', null, '适合谁 · 什么时候不该用它 · 官方简介原文');
    det.appendChild(sum);

    var d1 = el('div', 'detail-block');
    d1.appendChild(el('h4', null, '适合谁（本页整理）'));
    d1.appendChild(el('p', null, s.fit));
    det.appendChild(d1);

    var d2 = el('div', 'detail-block');
    d2.appendChild(el('h4', null, '什么时候不该用它（本页整理）'));
    var p2 = el('p', 'card-note', s.notFor);
    d2.appendChild(p2);
    det.appendChild(d2);

    var d3 = el('div', 'detail-block');
    d3.appendChild(el('h4', null, '官方简介原文（逐字，来源：' + sourceText(s) + '）'));
    d3.appendChild(el('p', 'official', s.desc));
    det.appendChild(d3);

    card.appendChild(det);

    if (s.marketName && s.marketName !== s.name) {
      card.appendChild(el('p', 'card-alias', '打开后会看到它在技能市场页里的名字是「' + s.marketName + '」。'));
    }

    var actions = el('div', 'card-actions');
    var b1 = el('button', 'btn btn-primary btn-mini', '先看看结果');
    b1.type = 'button';
    b1.addEventListener('click', function () { openDemo(s, rec.matched); });
    actions.appendChild(b1);

    var b2 = el('a', 'btn btn-ghost btn-mini', s.url ? '打开这个技能' : '去市场里搜它');
    b2.href = s.url || D.marketUrl;
    b2.target = '_blank';
    b2.rel = 'noopener';
    if (!s.url) b2.title = '这一条没拿到详情页地址，先到技能市场里搜它的名字';
    actions.appendChild(b2);

    card.appendChild(actions);
    return card;
  }

  function renderResult(res) {
    cardsBox.innerHTML = '';
    var basis = document.createDocumentFragment();

    if (res.pain) {
      basis.appendChild(document.createTextNode('你说的是：' + res.pain.label + '　'));
    } else {
      basis.appendChild(document.createTextNode('你写的是：「' + res.text + '」　'));
    }
    basis.appendChild(document.createTextNode('对得上的点：'));
    var hitTags = res.pain ? res.pain.tags : res.tags;
    var hitSet = {};
    res.shown.forEach(function (r) { r.matched.forEach(function (t) { hitSet[t] = 1; }); });
    hitTags.forEach(function (t) {
      basis.appendChild(chip(D.tagLabels[t] || t, !!hitSet[t]));
    });

    basisEl.innerHTML = '';
    basisEl.appendChild(basis);

    res.shown.forEach(function (r, i) { cardsBox.appendChild(cardNode(r, i)); });

    currentRest = res.rest;
    hasMore = res.rest.length > 0;
    showMoreBtn.hidden = !hasMore;
    showMoreBtn.textContent = '看看其他 ' + res.rest.length + ' 个候选';

    fallbackSec.hidden = true;
    resultSec.hidden = false;
    resultSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  var pendingRes = null;

  function applyResult(res) {
    pendingRes = res;
    renderResult(res);
  }

  function showPain(p) {
    var res = recommend(p);
    res.text = p.label;
    applyResult(res);
  }

  /* ------------------------- 兜底 ------------------------- */

  function showFallback(res) {
    fallbackList.innerHTML = '';
    fallbackBasis.textContent = (res.pain ? '「' + res.pain.label + '」' : '这句话')
      + ' 下共有 ' + res.ranked.length + ' 个候选，按对得上的程度排序：';
    res.ranked.forEach(function (r) {
      var li = el('li');
      var b = el('button');
      b.type = 'button';
      b.appendChild(document.createTextNode(r.skill.name));
      b.appendChild(el('span', null, usageText(r.skill) + ' · 对得上：' + tagLabels(r.matched).join('、')));
      b.addEventListener('click', function () {
        cardsBox.innerHTML = '';
        cardsBox.appendChild(cardNode(r, 0));
        fallbackSec.hidden = true;
        resultSec.hidden = false;
        resultSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      li.appendChild(b);
      fallbackList.appendChild(li);
    });
    fallbackSec.hidden = false;
    fallbackSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ------------------------- 演示面板 ------------------------- */

  function openDemo(s, matched) {
    lastFocus = document.activeElement;
    demoTitle.textContent = s.name;
    demoSub.textContent = '作者 ' + s.author + ' · ' + usageText(s) + ' · ' + sourceText(s)
      + (s.marketName && s.marketName !== s.name ? ' · 市场页里叫「' + s.marketName + '」' : '');
    demoMarket.textContent = s.url ? '打开这个技能' : '去 Meoo 技能市场搜它';
    demoMarket.href = s.url || D.marketUrl;

    demoBody.innerHTML = '';

    var st1 = el('div', 'demo-step');
    var h1 = el('h4');
    h1.appendChild(el('i', null, '1'));
    h1.appendChild(document.createTextNode('你大概会这样输入'));
    st1.appendChild(h1);
    st1.appendChild(el('p', 'demo-quote', s.demo.input));
    demoBody.appendChild(st1);

    var st2 = el('div', 'demo-step');
    var h2 = el('h4');
    h2.appendChild(el('i', null, '2'));
    h2.appendChild(document.createTextNode('它会怎么做'));
    st2.appendChild(h2);
    var ol = el('ol', 'demo-ordered');
    s.demo.steps.forEach(function (x) { ol.appendChild(el('li', null, x)); });
    st2.appendChild(ol);
    demoBody.appendChild(st2);

    var st3 = el('div', 'demo-step');
    var h3 = el('h4');
    h3.appendChild(el('i', null, '3'));
    h3.appendChild(document.createTextNode('你会拿到什么'));
    st3.appendChild(h3);
    var ul = el('ul', 'demo-deliver');
    s.demo.deliverables.forEach(function (x) { ul.appendChild(el('li', null, x)); });
    st3.appendChild(ul);
    demoBody.appendChild(st3);

    demoLayer.hidden = false;
    document.body.style.overflow = 'hidden';
    demoLayer.querySelector('.btn-close').focus();
  }

  function closeDemo() {
    demoLayer.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  /* ------------------------- 事件绑定 ------------------------- */

  function bind() {
    $('free-go').addEventListener('click', function () { runFreeText(); });
    $('free-text').addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); runFreeText(); }
    });

    showMoreBtn.addEventListener('click', function () {
      cardsBox.innerHTML = '';
      currentRest.slice(0, 2).forEach(function (r, i) { cardsBox.appendChild(cardNode(r, i)); });
      currentRest = currentRest.slice(2);
      hasMore = currentRest.length > 0;
      showMoreBtn.hidden = !hasMore;
      showMoreBtn.textContent = '再看看其他 ' + currentRest.length + ' 个候选';
      cardsBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    $('none-fit').addEventListener('click', function () {
      var res = pendingRes;
      if (res) showFallback(res);
    });

    $('fallback-back').addEventListener('click', function () {
      fallbackSec.hidden = true;
      resultSec.hidden = false;
      resultSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    $('restart').addEventListener('click', function () {
      resultSec.hidden = true;
      fallbackSec.hidden = true;
      $('free-text').value = '';
      $('pick').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    demoLayer.addEventListener('click', function (e) {
      if (e.target.hasAttribute('data-close-demo')) closeDemo();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !demoLayer.hidden) closeDemo();
    });
  }

  function runFreeText() {
    var text = ($('free-text').value || '').trim();
    if (!text) { $('free-text').focus(); return; }
    var res = recommendByText(text);
    if (!res || !res.ranked.length) {
      // 没匹配上：给整片候选的兜底（全部技能，按使用量）
      var all = D.skills.slice().sort(function (a, b) {
        return (typeof b.usage === 'number' ? b.usage : -1) - (typeof a.usage === 'number' ? a.usage : -1);
      }).map(function (s) { return { skill: s, matched: [] }; });
      showFallback({ ranked: all, pain: null });
      return;
    }
    res.text = text;
    applyResult(res);
  }

  /* ------------------------- 启动 ------------------------- */

  function boot() {
    $('snapshot-line').textContent =
      '下面这些技能来自 Meoo 平台真实条目（市场页 + 共创计划页），快照日期 ' + D.snapshot + '，共 ' + D.skills.length + ' 条。';

    $('src-date').textContent = D.snapshot;
    $('src-market').href = D.sources.market.url;
    $('src-event').href = D.sources.event.url;
    $('fallback-market').href = D.marketUrl;

    renderPains();
    bind();
  }

  boot();
})();
