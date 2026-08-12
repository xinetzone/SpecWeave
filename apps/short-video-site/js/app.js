/**
 * ReelVibe - 短视频网站交互逻辑
 * 数据从 assets/data/videos.json 加载，支持悬停预览
 */

(function () {
  'use strict';

  // ===== 状态 =====
  var videos = [];
  var currentVideoIndex = 0;
  var hoverTimer = null;

  // ===== DOM 元素 =====
  var mainVideo = document.getElementById('mainVideo');
  var playPauseBtn = document.getElementById('playPauseBtn');
  var muteBtn = document.getElementById('muteBtn');
  var fullscreenBtn = document.getElementById('fullscreenBtn');
  var progressBar = document.getElementById('progressBar');
  var progressFill = document.getElementById('progressFill');
  var timeDisplay = document.getElementById('timeDisplay');
  var mainPlayer = document.getElementById('mainPlayer');
  var subtitleOverlay = document.getElementById('subtitleOverlay');
  var recommendList = document.getElementById('recommendList');
  var videoGrid = document.getElementById('videoGrid');
  var searchInput = document.getElementById('searchInput');
  var categoryChips = document.querySelectorAll('.category-chip');
  var navItems = document.querySelectorAll('.nav-item');

  // ===== 播放器控制 =====
  function togglePlay() {
    if (mainVideo.paused) {
      mainVideo.play();
      playPauseBtn.querySelector('.material-icons-round').textContent = 'pause';
    } else {
      mainVideo.pause();
      playPauseBtn.querySelector('.material-icons-round').textContent = 'play_arrow';
    }
  }

  function toggleMute() {
    mainVideo.muted = !mainVideo.muted;
    muteBtn.querySelector('.material-icons-round').textContent = mainVideo.muted ? 'volume_off' : 'volume_up';
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      mainPlayer.requestFullscreen().catch(function () {});
    } else {
      document.exitFullscreen();
    }
  }

  function formatTime(seconds) {
    var s = Math.floor(seconds);
    var m = Math.floor(s / 60);
    s = s % 60;
    return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
  }

  function updateProgress() {
    if (mainVideo.duration) {
      var pct = (mainVideo.currentTime / mainVideo.duration) * 100;
      progressFill.style.width = pct + '%';
      timeDisplay.textContent = formatTime(mainVideo.currentTime) + ' / ' + formatTime(mainVideo.duration);
    }
  }

  function seekVideo(e) {
    var rect = progressBar.getBoundingClientRect();
    var pct = (e.clientX - rect.left) / rect.width;
    mainVideo.currentTime = pct * mainVideo.duration;
  }

  // ===== 加载视频 =====
  function loadVideo(index) {
    var v = videos[index];
    if (!v) return;
    currentVideoIndex = index;

    mainVideo.src = v.src;
    mainVideo.load();
    mainVideo.play().catch(function () {
      playPauseBtn.querySelector('.material-icons-round').textContent = 'play_arrow';
    });

    var playerInfo = document.querySelector('.player-info');
    if (playerInfo) {
      playerInfo.querySelector('.author-name').textContent = v.author;
      playerInfo.querySelector('.post-date').textContent = v.date;
      playerInfo.querySelector('.video-title').textContent = v.title;
      var tagsEl = playerInfo.querySelector('.video-tags');
      tagsEl.innerHTML = v.tags.map(function (t) { return '<span>' + t + '</span>'; }).join('');
    }

    if (subtitleOverlay) {
      subtitleOverlay.textContent = v.subtitle;
    }

    playPauseBtn.querySelector('.material-icons-round').textContent = 'pause';
  }

  // ===== 悬停预览 =====
  function enableHoverPreview(container) {
    container.addEventListener('mouseover', function (e) {
      var card = e.target.closest('[data-id]');
      if (!card) return;
      var videoEl = card.querySelector('video');
      if (!videoEl) return;

      hoverTimer = setTimeout(function () {
        videoEl.muted = true;
        videoEl.play().catch(function () {});
      }, 400);
    });

    container.addEventListener('mouseout', function (e) {
      var card = e.target.closest('[data-id]');
      if (!card) return;
      clearTimeout(hoverTimer);
      var videoEl = card.querySelector('video');
      if (videoEl) {
        videoEl.pause();
        videoEl.currentTime = 0;
      }
    });
  }

  // ===== 渲染推荐列表 =====
  function renderRecommendList() {
    var recommendVideos = videos.slice(1, 5);
    recommendList.innerHTML = recommendVideos.map(function (v) {
      return [
        '<div class="recommend-item" data-id="' + v.id + '">',
        '  <div class="recommend-thumb ' + v.gradient + '">',
        '    <video src="' + v.thumb + '" muted preload="metadata" playsinline onerror="this.style.display=\'none\'"></video>',
        '    <span class="recommend-duration">' + v.duration + '</span>',
        '  </div>',
        '  <div class="recommend-meta">',
        '    <p class="recommend-video-title">' + v.title + '</p>',
        '    <span class="recommend-author">' + v.author + '</span>',
        '    <span class="recommend-stats">' + v.views + ' 次观看</span>',
        '  </div>',
        '</div>'
      ].join('');
    }).join('');

    recommendList.querySelectorAll('.recommend-item').forEach(function (item) {
      item.addEventListener('click', function () {
        var id = parseInt(item.dataset.id);
        var idx = videos.findIndex(function (v) { return v.id === id; });
        if (idx !== -1) loadVideo(idx);
      });
    });

    enableHoverPreview(recommendList);
  }

  // ===== 渲染视频网格 =====
  function renderVideoGrid() {
    videoGrid.innerHTML = videos.map(function (v) {
      return [
        '<div class="grid-card" data-id="' + v.id + '">',
        '  <div class="grid-thumb ' + v.gradient + '">',
        '    <video src="' + v.thumb + '" muted preload="metadata" playsinline onerror="this.style.display=\'none\'"></video>',
        '    <div class="grid-thumb-overlay">',
        '      <span class="grid-views">',
        '        <span class="material-icons-round">play_circle</span>',
        '        ' + v.views,
        '      </span>',
        '    </div>',
        '  </div>',
        '  <p class="grid-card-title">' + v.title + '</p>',
        '  <span class="grid-card-author">' + v.author + ' · ' + v.date + '</span>',
        '</div>'
      ].join('');
    }).join('');

    videoGrid.querySelectorAll('.grid-card').forEach(function (card) {
      card.addEventListener('click', function () {
        var id = parseInt(card.dataset.id);
        var idx = videos.findIndex(function (v) { return v.id === id; });
        if (idx !== -1) {
          loadVideo(idx);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      });
    });

    enableHoverPreview(videoGrid);
  }

  // ===== 分类筛选 =====
  function filterByCategory(category) {
    var cards = videoGrid.querySelectorAll('.grid-card');
    cards.forEach(function (card) {
      var id = parseInt(card.dataset.id);
      var v = videos.find(function (vid) { return vid.id === id; });
      if (category === 'all' || (v && v.category === category)) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  }

  // ===== 搜索 =====
  function handleSearch(e) {
    if (e.key === 'Enter') {
      var query = searchInput.value.trim().toLowerCase();
      if (!query) {
        filterByCategory('all');
        return;
      }
      var cards = videoGrid.querySelectorAll('.grid-card');
      cards.forEach(function (card) {
        var id = parseInt(card.dataset.id);
        var v = videos.find(function (vid) { return vid.id === id; });
        var match = v && (
          v.title.toLowerCase().indexOf(query) !== -1 ||
          v.author.toLowerCase().indexOf(query) !== -1 ||
          v.tags.some(function (t) { return t.toLowerCase().indexOf(query) !== -1; })
        );
        card.style.display = match ? '' : 'none';
      });
    }
  }

  // ===== 键盘快捷键 =====
  function handleKeyboard(e) {
    if (e.target.tagName === 'INPUT') return;

    switch (e.key) {
      case ' ':
        e.preventDefault();
        togglePlay();
        break;
      case 'ArrowUp':
        e.preventDefault();
        loadVideo((currentVideoIndex - 1 + videos.length) % videos.length);
        break;
      case 'ArrowDown':
        e.preventDefault();
        loadVideo((currentVideoIndex + 1) % videos.length);
        break;
      case 'm':
      case 'M':
        toggleMute();
        break;
      case 'f':
      case 'F':
        toggleFullscreen();
        break;
    }
  }

  // ===== 事件绑定 =====
  function bindEvents() {
    playPauseBtn.addEventListener('click', togglePlay);
    muteBtn.addEventListener('click', toggleMute);
    fullscreenBtn.addEventListener('click', toggleFullscreen);
    mainVideo.addEventListener('click', togglePlay);
    mainVideo.addEventListener('timeupdate', updateProgress);
    mainVideo.addEventListener('loadedmetadata', updateProgress);
    progressBar.addEventListener('click', seekVideo);
    searchInput.addEventListener('keydown', handleSearch);
    document.addEventListener('keydown', handleKeyboard);

    categoryChips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        categoryChips.forEach(function (c) {
          c.classList.remove('active', 'active-underline');
        });
        chip.classList.add('active');
        filterByCategory(chip.dataset.category);
      });
    });

    navItems.forEach(function (item) {
      item.addEventListener('click', function (e) {
        e.preventDefault();
        navItems.forEach(function (n) { n.classList.remove('active'); });
        item.classList.add('active');
      });
    });

    document.querySelectorAll('.engage-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var icon = btn.querySelector('.engage-icon');
        if (icon.textContent === 'favorite') {
          icon.textContent = 'favorite_border';
          setTimeout(function () { icon.textContent = 'favorite'; }, 200);
        }
      });
    });
  }

  // ===== 加载数据并初始化 =====
  function init() {
    fetch('assets/data/videos.json')
      .then(function (res) { return res.json(); })
      .then(function (data) {
        videos = data;
        renderRecommendList();
        renderVideoGrid();
        bindEvents();
        loadVideo(0);
      })
      .catch(function (err) {
        console.error('视频数据加载失败:', err);
      });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
