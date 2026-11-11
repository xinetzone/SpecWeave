(function(){
  var D = window.ZHUANGZI || window.KONGZI || window.LAOZI;
  var P = D.person, pts = D.points;

  // ---- 填充人物信息 ----
  document.getElementById('pname').textContent = P.name;
  document.getElementById('paka').textContent = P.aka;
  document.getElementById('pera').textContent = P.era + ' ｜ ' + P.identity;
  document.getElementById('pquote').innerHTML =
    '“' + P.quote + '”<small>——' + P.quote_source + '</small>';
  document.getElementById('pbio').textContent = P.bio;
  document.getElementById('pdis').innerHTML = '<b>人物消歧：</b>' + P.disambiguation;
  document.getElementById('pfoot').innerHTML =
    (D.map_sources || '') + '<br>置信度：<span style="color:#4a8a52">■</span>高 '
    + '<span style="color:#c08a3e">■</span>中 <span style="color:#9c3b2e">■</span>低';

  // ---- 初始化地图（真实底图，多瓦片源容错）----
  var map = L.map('map', {zoomControl:true}).setView([33.5, 111.5], 6);
  // 主用 OSM，失败自动切换到备用源，保证联网即有真实底图
  var tileSources = [
    {url:'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
     opt:{maxZoom:18, subdomains:'abc', attribution:'© OpenStreetMap contributors'}},
    {url:'https://tile.openstreetmap.de/{z}/{x}/{y}.png',
     opt:{maxZoom:18, attribution:'© OpenStreetMap contributors'}},
    {url:'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
     opt:{maxZoom:17, subdomains:'abc', attribution:'© OpenStreetMap, © OpenTopoMap'}}
  ];
  // 离线兜底：Canvas 绘制经纬网格，确保无网络时地图不空白
  var GridFallback = L.GridLayer.extend({
    createTile: function(coords){
      var t = document.createElement('canvas'), sz = this.getTileSize();
      t.width = sz.x; t.height = sz.y;
      var g = t.getContext('2d');
      g.fillStyle = '#e9e3d6'; g.fillRect(0,0,sz.x,sz.y);
      g.strokeStyle = '#d2c6b0'; g.lineWidth = 1;
      for(var i=0;i<=sz.x;i+=32){ g.beginPath();g.moveTo(i,0);g.lineTo(i,sz.y);g.stroke(); }
      for(var j=0;j<=sz.y;j+=32){ g.beginPath();g.moveTo(0,j);g.lineTo(sz.x,j);g.stroke(); }
      return t;
    }
  });

  var tileIdx = 0, tileLayer = null, tileErr = 0;
  function loadTiles(){
    if(tileLayer){ map.removeLayer(tileLayer); }
    var s = tileSources[tileIdx];
    tileErr = 0;
    tileLayer = L.tileLayer(s.url, s.opt).addTo(map);
    tileLayer.on('tileerror', function(){
      tileErr++;
      if(tileErr > 6){
        if(tileIdx < tileSources.length-1){ tileIdx++; loadTiles(); }  // 换下一个在线源
        else { useFallback(); }                                        // 全部失败→离线网格
      }
    });
  }
  function useFallback(){
    if(tileLayer){ map.removeLayer(tileLayer); }
    tileLayer = new GridFallback({attribution:'离线网格底图（未连通在线地图服务）'}).addTo(map);
    var b = document.querySelector('.badge');
    if(b) b.innerHTML = '⚠ 在线地图瓦片未加载，已启用离线网格；联网后刷新即显示真实地图底图';
  }
  loadTiles();

  var cfClass = function(c){
    if(c.indexOf('高')===0) return 'cf-h';
    if(c.indexOf('低')===0) return 'cf-l';
    return 'cf-m';
  };

  // ---- 放置标记 + 构建弹窗 ----
  var markers = {}, latlngs = [];
  pts.forEach(function(p){
    var alt = (p.alt === true); // 涡阳异说点
    var icon = L.divIcon({
      className:'', html:'<div class="nmk'+(alt?' alt':'')+'">'+p.id+'</div>',
      iconSize:[30,30], iconAnchor:[15,15]
    });
    var m = L.marker([p.lat, p.lng], {icon:icon}).addTo(map);
    var html = '<div class="pop"><h3>'+p.id+'. '+p.title+'</h3>'
      + '<div class="row"><span class="k">时间：</span>'+p.time+'</div>'
      + '<div class="row"><span class="k">古地名：</span>'+p.ancient_place+'</div>'
      + '<div class="row"><span class="k">今地名：</span>'+p.today_place+'</div>'
      + '<div class="row"><span class="k">坐标：</span>'+p.lat.toFixed(4)+'°N, '+p.lng.toFixed(4)+'°E'
      + '<span class="cf '+cfClass(p.confidence)+'">'+p.confidence+'</span></div>'
      + '<div class="ev">'+p.event+'</div>'
      + '<div class="meta"><span class="k">定位方法：</span>'+p.method+'</div>';
    if(p.dispute){ html += '<div class="disp">⚠ '+p.dispute+'</div>'; }
    html += '<div class="src">依据：'+p.evidence+'</div></div>';
    m.bindPopup(html, {maxWidth:320});
    m.on('click', function(){ select(p.id, false); });
    markers[p.id] = m;
    latlngs.push([p.lat, p.lng]);
  });

  // ---- 讲述主线连线（按 teaching_order，虚线表路线）----
  var order = D.teaching_order;
  var path = order.map(function(id){
    var p = pts.filter(function(x){return x.id===id;})[0];
    return [p.lat, p.lng];
  });
  L.polyline(path, {color:'#9c3b2e', weight:2, dashArray:'6,8', opacity:.6}).addTo(map);

  // ---- 时间线列表 ----
  var tlBox = document.getElementById('timeline');
  pts.forEach(function(p){
    var div = document.createElement('div');
    div.className = 'tl' + (p.alt===true?' alt':'');
    div.id = 'tl-'+p.id;
    div.innerHTML = '<div class="dot"></div>'
      + '<div class="t">'+p.id+'. '+p.title+'</div>'
      + '<div class="yr">'+p.time+'</div>'
      + '<div class="pl">'+p.today_place+'</div>';
    div.onclick = function(){ select(p.id, true); };
    tlBox.appendChild(div);
  });

  // ---- 选中逻辑 ----
  var cur = null;
  function select(id, fly){
    cur = id;
    pts.forEach(function(p){
      var el = document.getElementById('tl-'+p.id);
      if(el) el.classList.toggle('active', p.id===id);
    });
    var m = markers[id];
    if(fly){
      var p = pts.filter(function(x){return x.id===id;})[0];
      map.flyTo([p.lat, p.lng], 8, {duration:.8});
      setTimeout(function(){ m.openPopup(); }, 650);
    } else {
      m.openPopup();
    }
    var ae = document.getElementById('tl-'+id);
    if(ae) ae.scrollIntoView({behavior:'smooth', block:'nearest'});
  }

  // ---- 导航按钮（按 teaching_order 巡览）----
  var idx = -1, timer = null;
  function go(step){
    idx = (idx + step + order.length) % order.length;
    select(order[idx], true);
  }
  document.getElementById('prev').onclick = function(){ stop(); go(-1); };
  document.getElementById('next').onclick = function(){ stop(); go(1); };
  var playBtn = document.getElementById('play');
  function stop(){ if(timer){ clearInterval(timer); timer=null; playBtn.textContent='▶ 自动巡览'; } }
  playBtn.onclick = function(){
    if(timer){ stop(); return; }
    playBtn.textContent = '⏸ 暂停巡览';
    go(1);
    timer = setInterval(function(){ go(1); }, 4500);
  };

  // 初始视野适配全部真实地点
  map.fitBounds(L.latLngBounds(latlngs).pad(0.25));
})();
