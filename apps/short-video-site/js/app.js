/**
 * ReelVibe - 短视频网站交互逻辑
 */

(function () {
  'use strict';

  // ===== 视频数据 =====
  const videos = [
    {
      id: 1,
      title: '航拍中国：云雾缭绕的金色山峦，治愈系自然风光 4K',
      author: '@自然探索家',
      avatar: 'assets/logo.jpg',
      src: 'assets/videos/nature.mp4',
      thumb: 'assets/videos/nature.mp4',
      duration: '00:05',
      views: '18.2万',
      likes: '18.2万',
      comments: '3,421',
      date: '8月10日',
      tags: ['#自然风光', '#航拍', '#治愈系', '#4K'],
      category: 'travel',
      subtitle: '云雾缭绕的金色山峦',
      gradient: 'placeholder-nature'
    },
    {
      id: 2,
      title: '深夜美食：手工和牛汉堡的极致诱惑，一口爆汁',
      author: '@美食研究所',
      avatar: 'assets/logo.jpg',
      src: 'assets/videos/food.mp4',
      thumb: 'assets/videos/food.mp4',
      duration: '00:05',
      views: '25.6万',
      likes: '25.6万',
      comments: '5,832',
      date: '8月9日',
      tags: ['#美食', '#汉堡', '#深夜放毒'],
      category: 'food',
      subtitle: '一口爆汁的极致诱惑',
      gradient: 'placeholder-food'
    },
    {
      id: 3,
      title: '护肤分享：晨间护肤routine，焕发光彩肌',
      author: '@美妆日记',
      avatar: 'assets/logo.jpg',
      src: 'assets/videos/beauty.mp4',
      thumb: 'assets/videos/beauty.mp4',
      duration: '00:05',
      views: '12.8万',
      likes: '12.8万',
      comments: '2,156',
      date: '8月8日',
      tags: ['#美妆', '#护肤', '#日常'],
      category: 'beauty',
      subtitle: '焕发光彩肌的秘密',
      gradient: 'placeholder-beauty'
    },
    {
      id: 4,
      title: '瑞士旅行｜第一次出国时的人生回忆',
      author: '@卷卷的日记',
      avatar: 'assets/logo.jpg',
      src: 'assets/videos/nature.mp4',
      thumb: 'assets/videos/nature.mp4',
      duration: '01:07',
      views: '7,282',
      likes: '7,282',
      comments: '892',
      date: '3月19日',
      tags: ['#瑞士', '#旅行', '#回忆'],
      category: 'travel',
      subtitle: '阿尔卑斯山的少女峰',
      gradient: 'placeholder-travel'
    },
    {
      id: 5,
      title: '悉尼Vlog｜总有一天你也会来到悉尼',
      author: '@笑西西Stacy',
      avatar: 'assets/logo.jpg',
      src: 'assets/videos/nature.mp4',
      thumb: 'assets/videos/nature.mp4',
      duration: '01:15',
      views: '4,983',
      likes: '4,983',
      comments: '534',
      date: '4月6日',
      tags: ['#悉尼', '#交换生', '#澳洲'],
      category: 'travel',
      subtitle: '海港大桥下的日落',
      gradient: 'placeholder-travel'
    },
    {
      id: 6,
      title: '泸州合江｜把世界装进眼睛',
      author: '@哈雷光',
      avatar: 'assets/logo.jpg',
      src: 'assets/videos/nature.mp4',
      thumb: 'assets/videos/nature.mp4',
      duration: '10:28',
      views: '1.6万',
      likes: '1.6万',
      comments: '1,203',
      date: '4月22日',
      tags: ['#泸州', '#旅行', '#四川'],
      category: 'travel',
      subtitle: '长江与赤水河的交汇处',
      gradient: 'placeholder-lifestyle'
    },
    {
      id: 7,
      title: 'Hello Kitty乐园攻略｜少女心爆棚',
      author: '@阿星去玩了',
      avatar: 'assets/logo.jpg',
      src: 'assets/videos/nature.mp4',
      thumb: 'assets/videos/nature.mp4',
      duration: '03:20',
      views: '2.7万',
      likes: '2.7万',
      comments: '2,890',
      date: '4月15日',
      tags: ['#HelloKitty', '#乐园', '#攻略'],
      category: 'vlog',
      subtitle: '世界上最可爱的地方',
      gradient: 'placeholder-beauty'
    },
    {
      id: 8,
      title: '家常菜教程｜十分钟搞定三菜一汤',
      author: '@厨房小帮手',
      avatar: 'assets/logo.jpg',
      src: 'assets/videos/food.mp4',
      thumb: 'assets/videos/food.mp4',
      duration: '05:30',
      views: '9.3万',
      likes: '9.3万',
      comments: '4,521',
      date: '8月5日',
      tags: ['#家常菜', '#教程', '#美食'],
      category: 'food',
      subtitle: '新手也能轻松学会',
      gradient: 'placeholder-food'
    }
  ];

  // ===== DOM 元素 =====
  const mainVideo = document.getElementById('mainVideo');
  const playPauseBtn = document.getElementById('playPauseBtn');
  const muteBtn = document.getElementById('muteBtn');
  const fullscreenBtn = document.getElementById('fullscreenBtn');
  const progressBar = document.getElementById('progressBar');
  const progressFill = document.getElementById('progressFill');
  const timeDisplay = document.getElementById('timeDisplay');
  const mainPlayer = document.getElementById('mainPlayer');
  const subtitleOverlay = document.getElementById('subtitleOverlay');
  const recommendList = document.getElementById('recommendList');
  const videoGrid = document.getElementById('videoGrid');
  const searchInput = document.getElementById('searchInput');
  const categoryChips = document.querySelectorAll('.category-chip');
  const navItems = document.querySelectorAll('.nav-item');

  let currentVideoIndex = 0;

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
      // autoplay may be blocked
      playPauseBtn.querySelector('.material-icons-round').textContent = 'play_arrow';
    });

    // 更新标题信息
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

  // ===== 渲染推荐列表 =====
  function renderRecommendList() {
    var recommendVideos = videos.slice(1, 5);
    recommendList.innerHTML = recommendVideos.map(function (v) {
      return [
        '<div class="recommend-item" data-id="' + v.id + '">',
        '  <div class="recommend-thumb ' + v.gradient + '">',
        '    <video src="' + v.thumb + '" muted preload="metadata" onerror="this.style.display=\'none\'"></video>',
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

    // 点击推荐切换主视频
    recommendList.querySelectorAll('.recommend-item').forEach(function (item) {
      item.addEventListener('click', function () {
        var id = parseInt(item.dataset.id);
        var idx = videos.findIndex(function (v) { return v.id === id; });
        if (idx !== -1) loadVideo(idx);
      });
    });
  }

  // ===== 渲染视频网格 =====
  function renderVideoGrid() {
    videoGrid.innerHTML = videos.map(function (v) {
      return [
        '<div class="grid-card" data-id="' + v.id + '">',
        '  <div class="grid-thumb ' + v.gradient + '">',
        '    <video src="' + v.thumb + '" muted preload="metadata" onerror="this.style.display=\'none\'"></video>',
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
        var prevIdx = (currentVideoIndex - 1 + videos.length) % videos.length;
        loadVideo(prevIdx);
        break;
      case 'ArrowDown':
        e.preventDefault();
        var nextIdx = (currentVideoIndex + 1) % videos.length;
        loadVideo(nextIdx);
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

    // 互动按钮动画
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

  // ===== 初始化 =====
  function init() {
    renderRecommendList();
    renderVideoGrid();
    bindEvents();

    // 尝试自动播放
    mainVideo.play().catch(function () {
      playPauseBtn.querySelector('.material-icons-round').textContent = 'play_arrow';
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
