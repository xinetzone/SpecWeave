#!/usr/bin/env node
/**
 * 静态契约检查：小程序项目结构 / 配置 / 页面完整性 / 编码约定。
 * 不依赖任何第三方包，node tests/structure.test.js 即可运行。
 */
const assert = require('assert')
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')
const failures = []
let checks = 0

function check(name, fn) {
  checks += 1
  try {
    fn()
    console.log(`  ok   ${name}`)
  } catch (error) {
    failures.push({ name, message: error.message })
    console.log(`  FAIL ${name}: ${error.message}`)
  }
}

function read(rel) {
  return fs.readFileSync(path.join(ROOT, rel), 'utf8')
}

function exists(rel) {
  return fs.existsSync(path.join(ROOT, rel))
}

function readJSON(rel) {
  return JSON.parse(read(rel))
}

function walk(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      if (entry.name === 'node_modules' || entry.name === 'miniprogram_npm') {
        continue
      }
      walk(full, out)
    } else {
      out.push(full)
    }
  }
  return out
}

console.log('== 项目结构 ==')

check('project.config.json 存在且 miniprogramRoot 指向源码根', () => {
  const cfg = readJSON('project.config.json')
  assert.strictEqual(cfg.miniprogramRoot, './', 'miniprogramRoot 必须是 ./')
  assert.strictEqual(cfg.compileType, 'miniprogram', 'compileType 必须是 miniprogram')
  assert.ok(cfg.packOptions.ignore.some((r) => r.type === 'folder' && r.value === 'tests'), 'tests 目录必须被 packOptions.ignore 排除')
})

check('app.json 存在且四个页面全部登记', () => {
  const app = readJSON('app.json')
  const expected = ['pages/index/index', 'pages/detail/detail', 'pages/signup/signup', 'pages/records/records']
  assert.deepStrictEqual(app.pages, expected, 'pages 列表与预期不一致')
})

check('app.json 开启组件懒加载', () => {
  const app = readJSON('app.json')
  assert.strictEqual(app.lazyCodeLoading, 'requiredComponents', 'lazyCodeLoading 必须是 requiredComponents')
})

check('app.json / project.config.json 为严格 JSON', () => {
  for (const rel of ['app.json', 'project.config.json', 'sitemap.json']) {
    JSON.parse(read(rel))
  }
  for (const page of ['index', 'detail', 'signup', 'records']) {
    JSON.parse(read(`pages/${page}/${page}.json`))
  }
})

check('每个页面具备 wxml/js/json/wxss 四件套', () => {
  for (const page of ['index', 'detail', 'signup', 'records']) {
    for (const ext of ['wxml', 'js', 'json', 'wxss']) {
      assert.ok(exists(`pages/${page}/${page}.${ext}`), `缺少 pages/${page}/${page}.${ext}`)
    }
  }
})

check('app.js / app.wxss 存在', () => {
  assert.ok(exists('app.js'))
  assert.ok(exists('app.wxss'))
})

check('tabBar 引用的图标文件真实存在', () => {
  const app = readJSON('app.json')
  for (const item of app.tabBar.list) {
    assert.ok(exists(item.iconPath), `缺少 ${item.iconPath}`)
    assert.ok(exists(item.selectedIconPath), `缺少 ${item.selectedIconPath}`)
    assert.ok(app.pages.includes(item.pagePath), `${item.pagePath} 不在 pages 中`)
  }
})

console.log('== 云端集成 ==')

check('云客户端同时传入 endpoint 与 publishableKey', () => {
  const src = read('utils/cloud.js')
  assert.ok(/endpoint:\s*publicConfig\.endpoint/.test(src), 'endpoint 必须来自 publicConfig')
  assert.ok(/publishableKey:\s*publicConfig\.publishableKey/.test(src), 'publishableKey 必须来自 publicConfig')
  assert.ok(/createMiniProgramWorkBuddyCloud/.test(src), '必须使用小程序专用工厂')
  assert.ok(!/createWorkBuddyCloud\(/.test(src.replace('createMiniProgramWorkBuddyCloud(', '')), '不得使用浏览器端工厂')
})

check('诊断适配器已复制进项目且未被二次包装', () => {
  const src = read('utils/workbuddy-cloud-diagnostics.js')
  assert.ok(src.includes('createDiagnosticWx'), '诊断适配器内容异常')
  const cloud = read('utils/cloud.js')
  const wraps = (cloud.match(/createDiagnosticWx\(wx\)/g) || []).length
  assert.strictEqual(wraps, 1, 'createDiagnosticWx 只能包装一次')
})

check('客户端不手工构造 owner_id', () => {
  const src = read('utils/api.js')
  assert.ok(!/owner_id\s*:/.test(src), 'api.js 不得出现 owner_id 字段')
  assert.ok(!/Authorization/.test(src), '不得手工设置 Authorization')
})

check('数据层未绕过 SDK 直连 /.cloud 路径', () => {
  // 扫描范围只含本项目自研代码：
  // - 排除 tests/（本文件自身）
  // - 排除 node_modules/ 与 vendor/（第三方产物，其内部实现不受本项目约束）
  // - 排除 .temp/（临时探针）
  const files = walk(ROOT).filter(
    (f) =>
      f.endsWith('.js') &&
      !f.includes('node_modules') &&
      !f.includes('vendor') &&
      !f.includes(`${path.sep}tests${path.sep}`) &&
      !f.includes(`${path.sep}.temp${path.sep}`)
  )
  for (const file of files) {
    const src = fs.readFileSync(file, 'utf8')
    assert.ok(!/\/\.cloud\//.test(src), `${path.relative(ROOT, file)} 出现 /.cloud/ 直连`)
  }
})

check('报名走服务端 RPC 做容量校验', () => {
  const src = read('utils/api.js')
  assert.ok(src.includes("rpc('submit_signup'"), '报名必须调用 submit_signup RPC')
})

check('取消报名走服务端 RPC，不直接改表', () => {
  const src = read('utils/api.js')
  assert.ok(src.includes("rpc('cancel_registration'"), '取消报名必须调用 cancel_registration RPC')
  assert.ok(!/\.from\('registrations'\)[\s\S]{0,400}?\.(update|delete)\(/.test(src), '客户端不得直接更新或删除 registrations 行')
})

check('报名人数口径为人数（与服务端 sum(companions) 对齐）', () => {
  const src = read('utils/api.js')
  assert.ok(src.includes('signed_up'), '必须读取服务端聚合的 signed_up 人数')
  const stats = read('scripts/db/fn_registration_stats.sql')
  assert.ok(stats.includes('sum(r.companions)'), '服务端聚合必须按人数口径 sum(companions)')
  const submit = read('scripts/db/fn_submit_signup.sql')
  assert.ok(submit.includes('sum(r.companions)'), '服务端容量校验必须按人数口径 sum(companions)')
  assert.ok(!submit.includes('count(*)'), '服务端容量校验不得使用 count(*) 行数口径')
})

check('服务端函数含登录态、字段与活动状态校验', () => {
  const submit = read('scripts/db/fn_submit_signup.sql')
  assert.ok(submit.includes('auth.uid()'), 'submit_signup 必须校验登录态')
  assert.ok(submit.includes('p_companions < 1 OR p_companions > 4'), '必须校验同行人数范围')
  assert.ok(submit.includes("p_contact !~ '^1[0-9]{10}$'"), '必须校验手机号格式')
  assert.ok(submit.includes('length(p_remark) > 100'), '必须校验备注长度')
  assert.ok(submit.includes('starts_at <= now()'), '必须校验活动是否已开始')
  assert.ok(submit.includes('FOR UPDATE'), '容量校验必须加行锁')
  assert.ok(submit.includes('unique_violation'), '必须处理重复报名唯一约束冲突')
})

check('活动主图绑定函数不可被终端用户调用', () => {
  const fn = read('scripts/db/fn_set_activity_cover.sql')
  assert.ok(fn.includes('shared/_application/activities/'), '主图路径必须限定在应用公共目录')
  const schema = read('scripts/db/schema.sql')
  assert.ok(
    /REVOKE ALL ON FUNCTION public\.set_activity_cover\(TEXT, TEXT\) FROM PUBLIC/.test(schema),
    'set_activity_cover 必须撤销 PUBLIC 执行权'
  )
  assert.ok(
    /GRANT EXECUTE ON FUNCTION public\.set_activity_cover\(TEXT, TEXT\) TO service_role/.test(schema),
    'set_activity_cover 只能授予 service_role'
  )
})

check('客户端对报名表只有读权限，写入全部走 RPC', () => {
  const schema = read('scripts/db/schema.sql')
  assert.ok(
    /REVOKE ALL ON TABLE public\.registrations FROM anon, authenticated/.test(schema),
    '必须撤销终端用户对 registrations 的写权限'
  )
  assert.ok(
    /GRANT SELECT ON TABLE public\.registrations TO anon, authenticated/.test(schema),
    'registrations 只保留 SELECT'
  )
  assert.ok(
    /CREATE UNIQUE INDEX IF NOT EXISTS registrations_activity_owner_confirmed_uniq/.test(schema),
    '必须有 (activity_id, owner_id) 部分唯一索引防重复报名'
  )
})

check('页面读取活动 id 使用 this.data 而非实例属性', () => {
  for (const page of ['detail', 'signup']) {
    const src = read(`pages/${page}/${page}.js`)
    assert.ok(!/this\.activityId\b/.test(src), `${page} 页不得使用 this.activityId（小程序不会把 data 镜像到实例）`)
    assert.ok(/this\.data\.activityId/.test(src), `${page} 页应使用 this.data.activityId`)
  }
})

check('配图上传走本人私有目录且限制大小与类型', () => {
  const src = read('pages/signup/signup.js')
  assert.ok(src.includes('cloud.storage.userPath'), '配图必须上传到本人私有目录 users/<uid>')
  assert.ok(!src.includes('cloud.storage.sharedPath'), '配图不得放在全体可读的 shared 目录')
  assert.ok(src.includes('MAX_UPLOAD_BYTES'), '必须限制上传体积')
  assert.ok(src.includes('ALLOWED_IMAGE_TYPES'), '必须限制上传类型')
})

check('服务端配图路径校验限定在本人目录', () => {
  // 校验形态：按 '/' 结构化分段比较（scope/owner/dir/file），
  // 并要求 owner 段等于调用者 uid。
  // 这里刻意断言「结构化分段 + owner 等值比较」而不是某种具体 SQL 写法：
  // 关键安全性质是「uid 不作为正则模式拼接，且 owner 段必须等于本人 uid」。
  const fn = read('scripts/db/fn_attach_registration_cover.sql')
  assert.ok(
    /v_owner\s*IS DISTINCT FROM v_uid/.test(fn),
    '配图路径必须按分段比较且 owner 段等于本人 uid'
  )
  assert.ok(
    /v_scope\s*IS DISTINCT FROM 'users'/.test(fn),
    '配图路径的 scope 段必须是 users'
  )
  assert.ok(
    !/\^users\/'\s*\|\|\s*v_uid/.test(fn),
    '不得把 uid 拼进正则模式（uid 含 . 等元字符时会放宽校验）'
  )

  const submit = read('scripts/db/fn_submit_signup.sql')
  assert.ok(
    /v_owner\s*IS DISTINCT FROM v_uid/.test(submit),
    '提交报名时配图路径必须按分段比较且 owner 段等于本人 uid'
  )
  assert.ok(
    /v_scope\s*IS DISTINCT FROM 'users'/.test(submit),
    '提交报名时配图路径的 scope 段必须是 users'
  )
  assert.ok(
    !/\^users\/'\s*\|\|\s*v_uid/.test(submit),
    '提交报名时不得把 uid 拼进正则模式'
  )
})

check('报名记录页对元数据失败做隔离', () => {
  const src = read('pages/records/records.js')
  assert.ok(src.includes('Promise.allSettled'), '必须用 allSettled 隔离元数据失败')
  assert.ok(!src.includes('Promise.all(['), '不得用 Promise.all 让元数据失败拖垮核心列表')
})

check('会话恢复有明确的完成信号，页面据此判定登录态', () => {
  const app = read('app.js')
  assert.ok(app.includes('sessionReady'), 'app.js 必须暴露会话就绪标记')
  assert.ok(app.includes('ensureSession'), 'app.js 必须提供 ensureSession')
  for (const page of ['index', 'detail', 'signup', 'records']) {
    const src = read(`pages/${page}/${page}.js`)
    assert.ok(src.includes('ensureSession'), `${page} 页必须等待会话恢复后再判定登录态`)
  }
})

check('首页支持下拉刷新', () => {
  const cfg = readJSON('pages/index/index.json')
  assert.strictEqual(cfg.enablePullDownRefresh, true, '首页必须开启下拉刷新')
})

check('错误文案不直出后端原始错误', () => {
  const src = read('utils/api.js')
  const fallback = src.match(/return '报名失败，请稍后重试'/)
  assert.ok(fallback, '未知错误必须有固定兜底文案')
  assert.ok(
    !/return raw \|\|/.test(src),
    '不得把后端原始错误直接返回给用户'
  )
})

check('微信登录使用运行时 appid', () => {
  const src = read('utils/auth.js')
  assert.ok(src.includes('wx.getAccountInfoSync'), '必须读取运行时 appid')
  assert.ok(src.includes('signInWithWechat'), '必须调用 signInWithWechat')
  assert.ok(!/wx\.getUserProfile/.test(src), 'getUserProfile 已被回收，不得使用')
})

console.log('== 视图与编码约定 ==')

const WXML_FILES = walk(path.join(ROOT, 'pages')).filter((f) => f.endsWith('.wxml'))

check('WXML 不含可选链、空值合并与箭头函数', () => {
  for (const file of WXML_FILES) {
    const src = fs.readFileSync(file, 'utf8')
    const rel = path.relative(ROOT, file)
    assert.ok(!/\{\{[^}]*\?\./.test(src), `${rel} 的 {{ }} 中使用了可选链`)
    assert.ok(!/\{\{[^}]*\?\?/.test(src), `${rel} 的 {{ }} 中使用了空值合并`)
    assert.ok(!/\{\{[^}]*=>/.test(src), `${rel} 的 {{ }} 中使用了箭头函数`)
  }
})

check('WXML 仅使用小程序原生标签', () => {
  const banned = ['<div', '<span', '<img', '<p ', '<button class="x"']
  for (const file of WXML_FILES) {
    const src = fs.readFileSync(file, 'utf8')
    const rel = path.relative(ROOT, file)
    for (const tag of banned) {
      if (tag === '<button class="x"') {
        continue
      }
      assert.ok(!src.includes(tag), `${rel} 使用了非小程序标签 ${tag}`)
    }
  }
})

check('WXML 内引用的本地资源全部存在', () => {
  const resourceRe = /["'](\/assets\/[^"']+)["']/g
  for (const file of WXML_FILES) {
    const src = fs.readFileSync(file, 'utf8')
    const rel = path.relative(ROOT, file)
    let match = resourceRe.exec(src)
    while (match) {
      assert.ok(exists(match[1]), `${rel} 引用的资源不存在: ${match[1]}`)
      match = resourceRe.exec(src)
    }
  }
})

check('源码不含 Emoji', () => {
  const emojiRe = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\u{1F000}-\u{1F02F}]/u
  const files = walk(ROOT).filter(
    (f) => /\.(js|wxml|wxss|json|md)$/.test(f) && !f.includes('node_modules')
  )
  for (const file of files) {
    const src = fs.readFileSync(file, 'utf8')
    const rel = path.relative(ROOT, file)
    const hit = src.match(emojiRe)
    assert.ok(!hit, `${rel} 含 Emoji: ${hit ? hit[0] : ''}`)
  }
})

check('全部文件为 UTF-8 无 BOM', () => {
  const files = walk(ROOT).filter((f) => /\.(js|wxml|wxss|json|md|py)$/.test(f))
  for (const file of files) {
    const buf = fs.readFileSync(file)
    assert.ok(!(buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf), `${path.relative(ROOT, file)} 含 BOM`)
    buf.toString('utf8')
  }
})

console.log('== 交付完整性 ==')

check('隐私清单已生成', () => {
  const candidates = fs.readdirSync(ROOT).filter((f) => /^\..+\.privacy\.json$/.test(f))
  assert.ok(candidates.length === 1, '项目根目录应存在且仅存在一个 .<applicationId>.privacy.json')
  const parsed = JSON.parse(read(path.join('.', candidates[0])))
  assert.ok(Array.isArray(parsed), '隐私清单必须是数组')
  for (const entry of parsed) {
    const keys = Object.keys(entry)
    assert.strictEqual(keys.length, 1, '每项必须只有一个 privacy_key')
    assert.ok(typeof entry[keys[0]] === 'string' && entry[keys[0]].length > 0, 'privacy_text 不得为空')
  }
})

check('README 说明页面与云端能力', () => {
  const src = read('README.md')
  for (const keyword of ['首页', '详情', '报名', '云端数据库', '云端存储', '授权登录']) {
    assert.ok(src.includes(keyword), `README 缺少说明: ${keyword}`)
  }
})

// ---------------------------------------------------------------------------
// schema.sql 是云端数据库的最终态真相源（云端以它为准执行）。
// 下面这组断言直接锁住关键不变量，避免「磁盘改了但云端没改」或
// 「口径漂移」这类只在生产环境暴露的问题。
// ---------------------------------------------------------------------------

console.log('')
console.log('== 云端真相源 schema.sql 的关键不变量 ==')

const schema = read('scripts/db/schema.sql')

check('schema.sql 里的 submit_signup 按人数口径聚合且带行锁', () => {
  const body = schema.slice(schema.indexOf('CREATE OR REPLACE FUNCTION public.submit_signup'))
  const fn = body.slice(0, body.indexOf('$fn$;'))
  assert.ok(/sum\(r\.companions\)/.test(fn), '人数口径必须是 sum(companions)')
  assert.ok(/status\s*=\s*'confirmed'/.test(fn), '只统计已确认的报名')
  assert.ok(/FOR UPDATE/.test(fn), '容量校验前必须对活动行加锁')
  // 顺序断言：行锁必须早于聚合，否则并发下仍可能超卖
  const lockAt = fn.indexOf('FOR UPDATE')
  const sumAt = fn.indexOf('sum(r.companions)')
  assert.ok(lockAt >= 0 && sumAt >= 0, '必须同时含行锁与人数聚合')
  assert.ok(lockAt < sumAt, `行锁(${lockAt}) 必须早于人数聚合(${sumAt})，否则并发下会超卖`)
})

check('schema.sql 的人数聚合结果使用 BIGINT，避免溢出与口径不一致', () => {
  const body = schema.slice(schema.indexOf('CREATE OR REPLACE FUNCTION public.submit_signup'))
  const fn = body.slice(0, body.indexOf('$fn$;'))
  assert.ok(/v_taken\s+BIGINT/.test(fn), 'v_taken 必须是 BIGINT')
  assert.ok(/::BIGINT/.test(fn), '聚合结果必须显式转 BIGINT')
})

check('schema.sql 的 activities 读策略只放行已发布活动与创建者本人', () => {
  const at = schema.indexOf('CREATE POLICY activities_read_all')
  assert.ok(at >= 0, '缺少 activities_read_all 策略')
  const policy = schema.slice(at, schema.indexOf(';', at))
  assert.ok(/published\s*=\s*TRUE/.test(policy), '已发布活动必须全员可读')
  assert.ok(/owner_id\s*=\s*auth\.uid\(\)/.test(policy), '创建者必须能看到自己下架的活动')
})

check('schema.sql 的 registrations 只对客户端开放 SELECT', () => {
  assert.ok(
    /REVOKE ALL ON TABLE public\.registrations FROM anon, authenticated;/.test(schema),
    '必须收回 registrations 的 anon/authenticated 全部权限'
  )
  assert.ok(
    /GRANT SELECT ON TABLE public\.registrations TO anon, authenticated;/.test(schema),
    'registrations 只应开放 SELECT'
  )
  for (const table of ['activities', 'registrations']) {
    assert.ok(
      !new RegExp(`GRANT (INSERT|UPDATE|DELETE).*ON TABLE public\\.${table}`).test(schema),
      `${table} 不得对客户端开放写权限`
    )
  }
})

check('schema.sql 的函数 EXECUTE 权限矩阵符合最小权限', () => {
  // 客户端可调：写报名、取消报名、绑配图
  const clientFns = [
    'public.submit_signup(BIGINT, INTEGER, TEXT, TEXT, TEXT, TEXT)',
    'public.cancel_registration(BIGINT)',
    'public.attach_registration_cover(BIGINT, TEXT)'
  ]
  for (const fn of clientFns) {
    assert.ok(
      new RegExp(`REVOKE ALL ON FUNCTION ${fn.replace(/[()]/g, '\\$&')} FROM PUBLIC;`).test(schema),
      `${fn} 必须先 REVOKE FROM PUBLIC`
    )
    assert.ok(
      new RegExp(`GRANT EXECUTE ON FUNCTION ${fn.replace(/[()]/g, '\\$&')} TO authenticated;`).test(schema),
      `${fn} 必须只授予 authenticated`
    )
  }

  // 管理侧专用：客户端一律不得调用
  const adminFns = [
    'public.set_activity_cover(TEXT, TEXT)',
    'public.claim_activity(BIGINT, TEXT)'
  ]
  for (const fn of adminFns) {
    assert.ok(
      new RegExp(`REVOKE ALL ON FUNCTION ${fn.replace(/[()]/g, '\\$&')} FROM PUBLIC;`).test(schema),
      `${fn} 必须先 REVOKE FROM PUBLIC`
    )
    assert.ok(
      new RegExp(`REVOKE ALL ON FUNCTION ${fn.replace(/[()]/g, '\\$&')} FROM anon, authenticated;`).test(schema),
      `${fn} 必须显式收回 anon/authenticated`
    )
    assert.ok(
      new RegExp(`GRANT EXECUTE ON FUNCTION ${fn.replace(/[()]/g, '\\$&')} TO service_role;`).test(schema),
      `${fn} 只能授予 service_role`
    )
  }

  // 主图绑定（canonical 通道）：授予 authenticated + service_role。
  // 安全依据在函数体内——目标路径由服务端拼出、调用方不可指定，
  // 文件名由 slug 决定，字节写入仍需管理员权限。
  assert.ok(
    /REVOKE ALL ON FUNCTION public\.sync_activity_cover\(TEXT\) FROM PUBLIC;/.test(schema),
    'sync_activity_cover 必须先 REVOKE FROM PUBLIC'
  )
  assert.ok(
    /REVOKE ALL ON FUNCTION public\.sync_activity_cover\(TEXT\) FROM anon;/.test(schema),
    'sync_activity_cover 必须显式收回 anon'
  )
  assert.ok(
    /GRANT EXECUTE ON FUNCTION public\.sync_activity_cover\(TEXT\) TO authenticated, service_role;/.test(schema),
    'sync_activity_cover 必须授予 authenticated 与 service_role'
  )
  const coverFn = read('scripts/db/fn_sync_activity_cover.sql')
  assert.ok(
    /v_path\s*:=\s*'shared\/_application\/activities\/'\s*\|\|\s*p_slug\s*\|\|\s*'\.png'/.test(coverFn),
    'sync_activity_cover 必须在函数体内拼出规范路径，路径不得由调用方指定'
  )
  assert.ok(
    !/p_path/.test(coverFn),
    'sync_activity_cover 不得接受调用方传入的路径参数（否则又会出现含 uid 的路径）'
  )
  assert.ok(
    /RETURNS TEXT/.test(coverFn),
    'sync_activity_cover 必须只返回路径，不能返回 activities 行（含 owner_id）'
  )
  // 管理侧通道同样只返回路径：旧版返回 SETOF activities，一旦被误授权给
  // authenticated，创建者标识会经 RPC 响应体下发，绕开列级授权。
  const adminCoverFn = read('scripts/db/fn_set_activity_cover.sql')
  assert.ok(
    /RETURNS TEXT/.test(adminCoverFn),
    'set_activity_cover 必须只返回路径，不能返回 activities 行（含 owner_id）'
  )
  assert.ok(
    !/SETOF\s+public\.activities/.test(adminCoverFn),
    'set_activity_cover 不得返回整行 activities（响应体会带出 owner_id）'
  )

  // 旧通道 claim_activity_cover 必须被显式 DROP：
  // 它允许把主图写进 shared/<uid>/activities/，使公开可读的 cover_path
  // 内嵌 owner uid —— 等于绕回创建者标识泄露的后门。
  assert.ok(
    /DROP FUNCTION IF EXISTS public\.claim_activity_cover\(TEXT, TEXT\);/.test(schema),
    'claim_activity_cover 必须显式 DROP'
  )
  assert.ok(
    !/CREATE OR REPLACE FUNCTION public\.claim_activity_cover/.test(schema),
    'schema.sql 不得再定义 claim_activity_cover'
  )
  assert.ok(
    !fs.existsSync(path.join(ROOT, 'scripts', 'db', 'fn_claim_activity_cover.sql')),
    'fn_claim_activity_cover.sql 必须删除'
  )

  // 旧签名（单参数自行认领）必须被显式 DROP，不能留作遗留入口
  assert.ok(
    /DROP FUNCTION IF EXISTS public\.claim_activity\(BIGINT\);/.test(schema),
    '旧签名 claim_activity(BIGINT) 必须显式 DROP'
  )
  assert.ok(
    !/CREATE OR REPLACE FUNCTION public\.claim_activity\(p_activity_id BIGINT\)/.test(schema),
    'claim_activity 不得保留单参数自行认领版本'
  )

  // 历史入口必须保持关闭
  assert.ok(
    /REVOKE ALL ON FUNCTION public\.signup\(BIGINT, INTEGER, TEXT, TEXT, TEXT\) FROM PUBLIC;/.test(schema),
    '历史 signup 入口必须 REVOKE FROM PUBLIC'
  )
  assert.ok(
    /REVOKE ALL ON FUNCTION public\.signup\(BIGINT, INTEGER, TEXT, TEXT, TEXT\) FROM anon, authenticated;/.test(schema),
    '历史 signup 入口必须显式收回 anon/authenticated'
  )
  assert.ok(
    !/GRANT EXECUTE ON FUNCTION public\.signup\(/.test(schema),
    '历史 signup 入口不得再授予任何角色'
  )
})

check('activities 采用列级授权，不下发 owner_id', () => {
  // owner_id 存的是微信 uid（形态 wx:<openid>）。表级 SELECT 会让访客
  // 直接 GET ?select=owner_id 绕过客户端读到创建者 openid，
  // 因此必须撤销表级 SELECT 并改为列级授权。
  assert.ok(
    /REVOKE SELECT ON TABLE public\.activities FROM anon, authenticated;/.test(schema),
    'activities 必须撤销表级 SELECT'
  )
  const colGrant = /GRANT SELECT \(([\s\S]*?)\)\s+ON TABLE public\.activities TO anon, authenticated;/.exec(schema)
  assert.ok(colGrant, 'activities 必须以列级 GRANT 授予 SELECT')
  const cols = colGrant[1].split(',').map((c) => c.trim()).filter(Boolean)
  assert.ok(cols.length >= 10, `activities 列级授权列数异常: ${cols.length}`)
  assert.ok(
    !cols.includes('owner_id'),
    'owner_id 不得出现在 activities 的列级授权里'
  )
  // 客户端字段白名单必须与列级授权对齐，不得请求未授权列
  const apiSrc = read('utils/api.js')
  const fieldMatch = /const ACTIVITY_FIELDS\s*=\s*'([^']+)'/.exec(apiSrc)
  assert.ok(fieldMatch, 'api.js 必须显式声明 ACTIVITY_FIELDS 白名单')
  const fields = fieldMatch[1].split(',').map((c) => c.trim()).filter(Boolean)
  fields.forEach((field) => {
    assert.ok(
      cols.includes(field),
      `客户端请求的列 ${field} 未在服务端列级授权名单内，会导致 42501`
    )
  })
  assert.ok(
    !fields.includes('owner_id'),
    '客户端字段白名单不得包含 owner_id'
  )
  // 最小权限：客户端与运营脚本都不读 created_at，就不授权它。
  // 授权列越少，「select=*」隐式展开越早被拒，不会因某次改动误读内部列。
  assert.ok(
    !cols.includes('created_at'),
    'created_at 不应授予 anon/authenticated（最小权限）'
  )
})

check('主图路径取值域被服务端锁死，不含用户标识', () => {
  // 历史教训：主图曾放在 shared/<运营账号 uid>/activities/ 下，
  // 于是公开可读的 activities.cover_path 内嵌了 owner uid——
  // 等于用「主图路径」这条后门，把已经从 owner_id 撤掉的创建者标识
  // 又原样下发给了所有访客。现在从取值域上根除。
  const syncFn = read('scripts/db/fn_sync_activity_cover.sql')
  const adminFn = read('scripts/db/fn_set_activity_cover.sql')

  // 1) canonical 通道：路径完全由服务端拼出
  assert.ok(
    /v_path\s*:=\s*'shared\/_application\/activities\/'\s*\|\|\s*p_slug\s*\|\|\s*'\.png'/.test(syncFn),
    'sync_activity_cover 必须在函数体内拼出 shared/_application/activities/<slug>.png'
  )
  assert.ok(
    !/p_path/.test(syncFn),
    'sync_activity_cover 不得接受调用方传入的路径'
  )

  // 2) 管理侧通道：只接受 _application 前缀
  assert.ok(
    /split_part\(p_path, '\/', 2\)\s+IS DISTINCT FROM '_application'/.test(adminFn),
    'set_activity_cover 必须只接受 shared/_application/ 前缀'
  )
  assert.ok(
    !/auth\.uid\(\)/.test(adminFn),
    'set_activity_cover 不得依赖 auth.uid()（它是 service_role 专用通道）'
  )

  // 3) 旧通道已废止：它是唯一能写入含 uid 路径的入口
  assert.ok(
    /DROP FUNCTION IF EXISTS public\.claim_activity_cover\(TEXT, TEXT\);/.test(schema),
    'claim_activity_cover 必须显式 DROP'
  )

  // 4) 客户端拿到的 cover_path 必须落在规范作用域
  const apiSrc = read('utils/api.js')
  assert.ok(
    /cover_path/.test(apiSrc),
    '客户端仍需读取 cover_path 用于签发主图地址'
  )
  const script = read('scripts/tools/sync-activity-covers.cjs')
  assert.ok(
    /shared\/_application\/activities/.test(script),
    '运营脚本必须使用规范作用域'
  )
})

check('schema.sql 的 registration_stats 不泄露未发布活动的人数', () => {
  const at = schema.indexOf('CREATE OR REPLACE FUNCTION public.registration_stats')
  assert.ok(at >= 0, '缺少 registration_stats 函数')
  const fn = schema.slice(at, schema.indexOf('$fn$;', at))
  assert.ok(
    /published\s*=\s*TRUE/.test(fn),
    '统计必须过滤未发布活动，否则匿名可读到下架活动的人数'
  )
})

check('schema.sql 的 attach_registration_cover 只允许已确认记录绑图', () => {
  const at = schema.indexOf('CREATE OR REPLACE FUNCTION public.attach_registration_cover')
  assert.ok(at >= 0, '缺少 attach_registration_cover 函数')
  const fn = schema.slice(at, schema.indexOf('$fn$;', at))
  assert.ok(
    /status\s*=\s*'confirmed'/.test(fn),
    '绑图必须限制 status=confirmed，已取消的记录不应允许补图'
  )
})

check('运营脚本与云端权限模型一致', () => {
  const script = read('scripts/tools/sync-activity-covers.cjs')
  // 归属建立只有 service_role 能调，脚本用 authenticated 会话调用必然 42501。
  assert.ok(
    !/rpc\('claim_activity'/.test(script),
    '脚本不得调用 claim_activity（仅 service_role 可执行，authenticated 调用必然 42501）'
  )
  // 主图绑定走 canonical 通道：路径由服务端拼出，脚本不传路径。
  assert.ok(
    /rpc\('sync_activity_cover'/.test(script),
    '脚本必须通过 sync_activity_cover 绑定主图'
  )
  assert.ok(
    !/rpc\('claim_activity_cover'/.test(script),
    '脚本不得调用已废止的 claim_activity_cover'
  )
  assert.ok(
    !/p_path/.test(script),
    '脚本不得向服务端传主图路径（路径必须由服务端拼出）'
  )
  // 上传不在脚本内：shared/_application/ 是应用归属作用域，
  // 端用户会话写不进去（RLS with_check 要求 owner_id = auth.uid()），
  // 唯一写入通道是 WorkBuddy 管理页。脚本只做校验与绑定。
  assert.ok(
    !/storage\.upload\(|createSignedUploadUrl/.test(script),
    '脚本不得上传字节到应用归属作用域（写权限仅管理员，走管理页）'
  )
  assert.ok(
    /shared\/_application\/activities/.test(script),
    '脚本必须使用规范作用域 shared/_application/activities'
  )
  // activities 改为列级授权后，owner_id 不再可查，脚本不得再 select 它。
  const selects = script.match(/\.select\(([^)]*)\)/g) || []
  assert.ok(selects.length > 0, '脚本必须显式列出查询字段')
  selects.forEach((sel) => {
    assert.ok(
      !/owner_id/.test(sel),
      `脚本查询不得包含 owner_id（activities 已改为列级授权，查询它会 42501）：${sel}`
    )
  })
  // 凭据不得硬编码
  assert.ok(
    !/@[a-z0-9.-]+\.[a-z]{2,}/i.test(script.replace(/https?:\/\/[^\s'"]+/g, '')),
    '脚本不得硬编码邮箱账号'
  )
  assert.ok(
    /process\.env\.JBZL_EMAIL/.test(script) && /process\.env\.JBZL_PASSWORD/.test(script),
    '运营凭据必须来自环境变量'
  )
  // 令牌不得进日志
  assert.ok(
    !/console\.[a-z]+\([^)]*accessToken/.test(script),
    '脚本不得打印 accessToken'
  )
})

check('schema.sql 的配图路径校验不把 uid 拼进正则模式', () => {
  // uid 含 '.' 等正则元字符时，拼进模式会放宽校验；
  // 正确做法是结构化分段比较。
  assert.ok(
    !/\^users\/'\s*\|\|\s*v_uid/.test(schema),
    'schema.sql 不得出现把 uid 拼进正则模式的写法'
  )
  assert.ok(
    /v_owner\s*IS DISTINCT FROM v_uid/.test(schema),
    '必须以分段等值比较校验路径 owner 段'
  )
})

check('schema.sql 的部分唯一索引只约束有效报名', () => {
  assert.ok(
    /CREATE UNIQUE INDEX IF NOT EXISTS registrations_activity_owner_confirmed_uniq/.test(schema),
    '缺少同一用户同一活动的有效报名唯一索引'
  )
  const at = schema.indexOf('CREATE UNIQUE INDEX IF NOT EXISTS registrations_activity_owner_confirmed_uniq')
  const stmt = schema.slice(at, schema.indexOf(';', at))
  assert.ok(
    /WHERE\s+status\s*=\s*'confirmed'/.test(stmt),
    '唯一索引必须只约束 status=confirmed（取消后允许再次报名）'
  )
})

check('schema.sql 与分文件脚本保持同源', () => {
  // 每个 fn_*.sql 的函数体都应能在 schema.sql 中找到同名函数定义，
  // 避免「只改分文件、忘了改真相源」导致云端与磁盘漂移。
  const files = fs
    .readdirSync(path.join(ROOT, 'scripts', 'db'))
    .filter((f) => /^fn_.*\.sql$/.test(f))
  assert.ok(files.length >= 6, `分文件脚本数量异常: ${files.length}`)
  for (const file of files) {
    const src = read(`scripts/db/${file}`)
    const m = /CREATE OR REPLACE FUNCTION public\.([a-z_]+)\s*\(/.exec(src)
    assert.ok(m, `${file} 未能解析出函数名`)
    const fnName = m[1]
    assert.ok(
      schema.includes(`CREATE OR REPLACE FUNCTION public.${fnName}`),
      `schema.sql 缺少函数 ${fnName}（分文件 ${file} 有，schema 无）`
    )
  }
})

check('本地主图资源与活动清单、客户端兜底规则三方对齐', () => {
  // 三方必须一致，否则会出现「运营以为上传了 A 的图、客户端却拿 B 的兜底图」：
  //   运营脚本 TARGETS（活动清单） → assets/covers/<slug>.png（本地资源）
  //                          → utils/format.js 的 fallbackCover（客户端推导）
  // 早期 fallbackCover 是硬编码映射表，新增活动漏改表就永远落默认图；
  // 现在改为规则推导，这条断言防止规则与资源再次脱节。
  const script = read('scripts/tools/sync-activity-covers.cjs')
  const block = /const TARGETS = \[([\s\S]*?)\]/.exec(script)
  assert.ok(block, '运营脚本必须声明 TARGETS 活动清单')
  const pairs = [...block[1].matchAll(/slug:\s*'([^']+)'\s*,\s*file:\s*'([^']+)'/g)]
  assert.ok(pairs.length > 0, '未能从运营脚本解析出活动清单')

  const format = require(path.join(ROOT, 'utils', 'format.js'))
  pairs.forEach((row) => {
    const slug = row[1]
    const file = row[2]
    assert.strictEqual(
      file,
      `${slug}.png`,
      `主图文件名必须等于 slug（云端路径规则 shared/_application/activities/<slug>.png 要求）：${slug}`
    )
    assert.ok(
      exists(path.join('assets', 'covers', file)),
      `本地主图缺失: assets/covers/${file}（slug=${slug}）`
    )
    assert.strictEqual(
      format.fallbackCover(slug),
      `/assets/covers/${file}`,
      `客户端兜底路径与本地主图不一致：slug=${slug}`
    )
  })

  // 兜底图必须存在：本地无对应文件时 <image binderror> 要降级到它
  assert.ok(
    exists(path.join('assets', 'covers', 'default.png')),
    '兜底主图缺失: assets/covers/default.png'
  )
  assert.strictEqual(format.defaultCover(), '/assets/covers/default.png')
})

// ---------------------------------------------------------------------------
// 隐私合规面（提审拦截防线）
// 2026-10-26 提审被拒教训：代码调了隐私接口，但《用户隐私保护指引》未声明对应信息类型
// → 平台在提审时逐项比对「本次版本的隐私接口调用」与「已填协议内容」，缺项即拦截。
// 这几条断言把该防线固化为可回归项。
// ---------------------------------------------------------------------------
console.log('')
console.log('== 隐私合规面 ==')

check('存在平台侧隐私声明文件', () => {
  assert.ok(
    exists(path.join('docs', 'privacy-declaration.md')),
    '缺少 docs/privacy-declaration.md：提审入口2 需要填写隐私协议内容，空协议会被直接拦截'
  )
})

check('隐私声明覆盖代码调用的隐私接口', () => {
  const decl = read(path.join('docs', 'privacy-declaration.md'))
  const signup = read(path.join('pages', 'signup', 'signup.js'))
  if (signup.includes('wx.chooseMedia')) {
    assert.ok(
      decl.includes('选中的照片或视频信息'),
      '代码调用了 wx.chooseMedia（收集你选中的照片或视频信息），隐私声明缺少对应条目'
    )
  }
})

check('隐私接口调用前有授权兜底', () => {
  const privacy = read(path.join('utils', 'privacy.js'))
  assert.ok(
    privacy.includes('requirePrivacyAuthorize'),
    'utils/privacy.js 必须提供 requirePrivacyAuthorize：隐私接口在用户未同意时静默失败'
  )
  assert.ok(
    privacy.includes('onNeedPrivacyAuthorization'),
    'utils/privacy.js 必须提供 onNeedPrivacyAuthorization：否则平台授权面板无人响应'
  )
  const app = read('app.js')
  assert.ok(
    app.includes('registerPrivacyAuthorization'),
    'app.js 必须注册隐私授权响应（privacy.registerPrivacyAuthorization）'
  )
})

check('隐私接口调用点已接入授权兜底', () => {
  const signup = read(path.join('pages', 'signup', 'signup.js'))
  assert.ok(
    signup.includes('ensurePrivacyAuthorized'),
    'pages/signup/signup.js 调用隐私接口前必须先过 ensurePrivacyAuthorized'
  )
  // 判定顺序必须基于「真实调用点」而非注释里出现的接口名——
  // 注释里的 wx.chooseMedia 出现在方法定义上方，会让顺序判断恒为假。
  const codeOnly = signup
    .split('\n')
    .filter((line) => !/^\s*(\*|\/\/)/.test(line))
    .join('\n')
  const callIdx = codeOnly.indexOf('wx.chooseMedia')
  const guardIdx = codeOnly.indexOf('this.ensurePrivacyAuthorized()')
  assert.ok(callIdx > 0 && guardIdx > 0, '未找到隐私接口调用点或授权兜底调用点')
  assert.ok(
    guardIdx < callIdx,
    '授权兜底必须早于 wx.chooseMedia 调用：先授权再调用，顺序反了等于没兜底'
  )
})

console.log('')
if (failures.length) {
  console.error(`失败 ${failures.length}/${checks} 项：`)
  failures.forEach((f) => console.error(`  - ${f.name}: ${f.message}`))
  process.exit(1)
}
console.log(`全部通过：${checks}/${checks}`)
