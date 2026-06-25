(function() {
  var today = new Date();
  var dayIndex = today.getDate() % dailyQuestions.length;
  var dailyQ = dailyQuestions[dayIndex];

  document.getElementById('dailyDate').textContent =
    today.getFullYear() + '年' + (today.getMonth() + 1) + '月' + today.getDate() + '日';
  document.getElementById('dailyQuote').textContent = dailyQ.quote;
  document.getElementById('dailySource').textContent = dailyQ.source + ' — ' + dailyQ.hint;

  function submitDailyThought() {
    var input = document.getElementById('dailyInput');
    var response = document.getElementById('dailyResponse');
    var text = input.value.trim();
    if (!text) return;

    response.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

    setTimeout(function() {
      var replies = aiResponses.fallback;
      var reply = replies[dayIndex % replies.length];
      response.innerHTML =
        '<div class="chat-msg ai">' +
        '<div class="msg-label">竹简悟道</div>' +
        '<div class="msg-bubble">' + reply + '</div>' +
        '</div>' +
        '<p style="text-align:center;margin-top:16px;font-size:0.8rem;color:var(--text-muted);">' +
        '明天，再来问一个问题——不是找答案，而是练习"问"本身。' +
        '</p>';
      input.value = '';
    }, 1800);
  }

  function submitScenario() {
    var input = document.getElementById('scenarioInput');
    var chatArea = document.getElementById('chatArea');
    var text = input.value.trim();
    if (!text) return;

    var emptyState = chatArea.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    var userMsg = document.createElement('div');
    userMsg.className = 'chat-msg user';
    userMsg.innerHTML = '<div class="msg-bubble">' + escapeHtml(text) + '</div>';
    chatArea.appendChild(userMsg);

    var typingDiv = document.createElement('div');
    typingDiv.className = 'chat-msg ai';
    typingDiv.innerHTML =
      '<div class="msg-label">竹简悟道</div>' +
      '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    chatArea.appendChild(typingDiv);

    var activeTag = document.querySelector('.scenario-tag.active-tag');
    var scenario;
    if (activeTag && activeTag.dataset.scenario === 'flow') {
      activeTag.classList.remove('active-tag');
      scenario = null;
    } else {
      scenario = activeTag ? activeTag.dataset.scenario : null;
    }

    setTimeout(function() {
      typingDiv.remove();

      var responsePool;
      if (scenario && aiResponses[scenario]) {
        responsePool = aiResponses[scenario];
      } else {
        var keys = Object.keys(aiResponses).filter(function(k) { return k !== 'fallback'; });
        responsePool = aiResponses[keys[Math.floor(Math.random() * keys.length)]];
      }

      var reply = responsePool[Math.floor(Math.random() * responsePool.length)];

      var aiMsg = document.createElement('div');
      aiMsg.className = 'chat-msg ai';
      aiMsg.innerHTML =
        '<div class="msg-label">竹简悟道</div>' +
        '<div class="msg-bubble">' + reply + '</div>';
      chatArea.appendChild(aiMsg);

      chatArea.scrollTop = chatArea.scrollHeight;
      input.value = '';
    }, 1800);

    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function openFlowConversation() {
    var chatArea = document.getElementById('chatArea');
    var emptyState = chatArea.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    var openingQuestion = aiResponses.flow[Math.floor(Math.random() * aiResponses.flow.length)];

    var aiMsg = document.createElement('div');
    aiMsg.className = 'chat-msg ai';
    aiMsg.innerHTML =
      '<div class="msg-label">竹简悟道</div>' +
      '<div class="msg-bubble">' + openingQuestion + '</div>';
    chatArea.appendChild(aiMsg);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function renderBambooList() {
    var listEl = document.getElementById('bambooList');
    var html = '';
    bambooChapters.forEach(function(ch) {
      html +=
        '<div class="bamboo-chapter" onclick="openBambooDetail(\'' + ch.num + '\')">' +
        '<div class="bamboo-chapter-num">' + ch.num + '</div>' +
        '<div class="bamboo-chapter-info">' +
        '<div class="bamboo-chapter-title">' + ch.title + '</div>' +
        '<div class="bamboo-chapter-preview">' + ch.verse.substring(0, 32) + '……</div>' +
        '</div>' +
        '</div>';
    });
    listEl.innerHTML = html;
  }

  function openBambooDetail(num) {
    var ch = bambooChapters.find(function(c) { return c.num === num; });
    if (!ch) return;

    var listEl = document.getElementById('bambooList');
    var detailEl = document.getElementById('bambooDetail');

    listEl.style.display = 'none';
    detailEl.className = 'bamboo-detail open';
    detailEl.innerHTML =
      '<button class="btn-back" onclick="closeBambooDetail()">← 返回目录</button>' +
      '<h2 style="font-family:var(--font-title);font-size:1.3rem;margin-bottom:8px;letter-spacing:0.08em;">第' + ch.num + '章 · ' + ch.title + '</h2>' +
      '<div class="verse">' + ch.verse + '</div>' +
      '<div class="note">' + ch.note + '</div>' +
      '<div class="interpretation">' + ch.interpretation + '</div>' +
      '<div class="diff-note">📜 ' + ch.diff + '</div>';
  }

  function closeBambooDetail() {
    var listEl = document.getElementById('bambooList');
    var detailEl = document.getElementById('bambooDetail');
    listEl.style.display = 'block';
    detailEl.className = 'bamboo-detail';
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  window.openBambooDetail = openBambooDetail;
  window.closeBambooDetail = closeBambooDetail;
  window.submitDailyThought = submitDailyThought;
  window.submitScenario = submitScenario;
  window.openFlowConversation = openFlowConversation;

  document.querySelectorAll('.tab-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var tab = this.dataset.tab;
      document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
      this.classList.add('active');
      document.querySelectorAll('.tab-panel').forEach(function(p) { p.classList.remove('active'); });
      document.getElementById('tab-' + tab).classList.add('active');
    });
  });

  document.querySelectorAll('.scenario-tag').forEach(function(tag) {
    tag.addEventListener('click', function() {
      document.querySelectorAll('.scenario-tag').forEach(function(t) { t.classList.remove('active-tag'); });
      this.classList.add('active-tag');
      if (this.dataset.scenario === 'flow') {
        openFlowConversation();
      }
    });
  });

  document.getElementById('scenarioInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitScenario();
    }
  });

  document.getElementById('dailyInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      submitDailyThought();
    }
  });

  renderBambooList();
})();
