#!/usr/bin/env node
/**
 * 纯函数单元测试：utils/format.js。
 * 不依赖任何第三方包，node tests/format.test.js 即可运行。
 */
const assert = require('assert')
const path = require('path')

const format = require(path.resolve(__dirname, '..', 'utils', 'format.js'))

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

/** 构造本地时区的某一天，避免时区导致的跨日漂移。 */
function local(y, m, d, hh = 0, mm = 0) {
  return new Date(y, m - 1, d, hh, mm, 0, 0).toISOString()
}

console.log('== formatCountdown：按日历日计算 ==')

check('同一天早上 9 点显示今天开始', () => {
  const now = local(2026, 11, 10, 8, 0)
  const target = local(2026, 11, 10, 9, 0)
  assert.strictEqual(format.formatCountdown(target, now), '今天开始')
})

check('明天早上 6 点显示明天开始（不再多算一天）', () => {
  const now = local(2026, 11, 10, 23, 30)
  const target = local(2026, 11, 11, 6, 0)
  assert.strictEqual(format.formatCountdown(target, now), '明天开始')
})

check('今天晚上 23 点对明早 6 点也显示明天开始', () => {
  const now = local(2026, 11, 10, 23, 0)
  const target = local(2026, 11, 11, 6, 0)
  assert.strictEqual(format.formatCountdown(target, now), '明天开始')
})

check('后天显示还有 2 天', () => {
  const now = local(2026, 11, 10, 10, 0)
  const target = local(2026, 11, 12, 10, 0)
  assert.strictEqual(format.formatCountdown(target, now), '还有 2 天')
})

check('19 天后显示还有 19 天', () => {
  const now = local(2026, 11, 10, 10, 0)
  const target = local(2026, 11, 29, 10, 0)
  assert.strictEqual(format.formatCountdown(target, now), '还有 19 天')
})

check('昨天显示已结束', () => {
  const now = local(2026, 11, 10, 10, 0)
  const target = local(2026, 11, 9, 10, 0)
  assert.strictEqual(format.formatCountdown(target, now), '已结束')
})

check('跨月边界：3月30日到4月1日为还有 2 天', () => {
  const now = local(2026, 3, 30, 12, 0)
  const target = local(2026, 4, 1, 12, 0)
  assert.strictEqual(format.formatCountdown(target, now), '还有 2 天')
})

check('今天同一时刻已过点仍显示今天开始（当日活动当天可参加）', () => {
  // 活动今天 09:00 开始，现在已是今天 15:00：
  // 倒计时文案按「日历日」判断，当天仍是「今天开始」；
  // 是否还能报名由服务端 starts_at 校验决定，不依赖这段文案。
  const now = local(2026, 11, 10, 15, 0)
  const target = local(2026, 11, 10, 9, 0)
  assert.strictEqual(format.formatCountdown(target, now), '今天开始')
})

check('空值与非法值返回空串', () => {
  assert.strictEqual(format.formatCountdown(''), '')
  assert.strictEqual(format.formatCountdown(null), '')
  assert.strictEqual(format.formatCountdown('not-a-date'), '')
})

console.log('== quotaText / isFull / percent：人数口径 ==')

check('capacity=120 已报名 24 时显示还剩 96 位', () => {
  assert.strictEqual(format.quotaText(120, 24), '还剩 96 位')
})

check('capacity=120 已报名 120 时显示名额已满', () => {
  assert.strictEqual(format.quotaText(120, 120), '名额已满')
})

check('capacity=120 已报名 130（并发超写）仍视为已满', () => {
  assert.strictEqual(format.quotaText(120, 130), '名额已满')
  assert.strictEqual(format.isFull(120, 130), true)
})

check('capacity<=0 表示不限名额，且永不满', () => {
  assert.strictEqual(format.quotaText(0, 999), '不限名额')
  assert.strictEqual(format.isFull(0, 999), false)
  assert.strictEqual(format.quotaText(-1, 0), '不限名额')
  assert.strictEqual(format.percent(0, 50), 0)
})

check('人数口径：isFull 与 quotaText 判定一致', () => {
  assert.strictEqual(format.isFull(120, 119), false)
  assert.strictEqual(format.isFull(120, 120), true)
})

check('percent 按人数比例计算并夹在 0-100', () => {
  assert.strictEqual(format.percent(120, 60), 50)
  assert.strictEqual(format.percent(120, 0), 0)
  assert.strictEqual(format.percent(120, 300), 100)
})

console.log('== canFit：本次报名人数是否装得下（人数口径） ==')

check('剩余名额恰好等于本次人数时允许报名', () => {
  assert.strictEqual(format.canFit(120, 117, 3), true)
})

check('剩余名额少于本次人数时拒绝报名', () => {
  assert.strictEqual(format.canFit(120, 118, 3), false)
})

check('本次人数为 1 时按单人占用计算', () => {
  assert.strictEqual(format.canFit(120, 119, 1), true)
  assert.strictEqual(format.canFit(120, 120, 1), false)
})

check('capacity<=0 表示不限名额，任何人数都装得下', () => {
  assert.strictEqual(format.canFit(0, 999, 4), true)
  assert.strictEqual(format.canFit(-1, 0, 4), true)
})

check('并发超写后已报名数超过容量时不再允许报名', () => {
  assert.strictEqual(format.canFit(120, 130, 1), false)
})

check('缺省值按「至少本人 1 人」兜底，不放行非法输入', () => {
  // companions 缺失/非法时按 1 人计，仍要受容量约束
  assert.strictEqual(format.canFit(120, 120, undefined), false)
  assert.strictEqual(format.canFit(120, 119, undefined), true)
  assert.strictEqual(format.canFit(120, 119, 0), true)
})

check('canFit 与 isFull 判定不矛盾：已满时必然装不下', () => {
  for (const taken of [0, 1, 119, 120, 130]) {
    if (format.isFull(120, taken)) {
      assert.strictEqual(format.canFit(120, taken, 1), false, `已报名 ${taken} 人时应拒绝`)
    }
  }
})

console.log('== statusText / fallbackCover ==')

check('状态文案映射正确', () => {
  assert.strictEqual(format.statusText('confirmed'), '已确认')
  assert.strictEqual(format.statusText('cancelled'), '已取消')
  assert.strictEqual(format.statusText('unknown'), '处理中')
})

check('slug 命中时按规则推导主图路径', () => {
  // 规则化推导，不再依赖硬编码映射表：
  // 新增活动只要把 <slug>.png 放进 assets/covers/ 就自动命中，无需改代码。
  assert.strictEqual(format.fallbackCover('dawn-trek'), '/assets/covers/dawn-trek.png')
  assert.strictEqual(format.fallbackCover('night-market'), '/assets/covers/night-market.png')
  assert.strictEqual(format.fallbackCover('island-week'), '/assets/covers/island-week.png')
})

check('slug 形状非法时回落到中性兜底图', () => {
  assert.strictEqual(format.defaultCover(), '/assets/covers/default.png')
  assert.strictEqual(format.fallbackCover(''), '/assets/covers/default.png')
  assert.strictEqual(format.fallbackCover(null), '/assets/covers/default.png')
  assert.strictEqual(format.fallbackCover(undefined), '/assets/covers/default.png')
  assert.strictEqual(format.fallbackCover(123), '/assets/covers/default.png')
})

check('slug 形状合法但本地无对应文件时给出候选路径，由图片 error 事件降级', () => {
  // 候选路径规则化，不查映射表；本地文件缺失时 <image> 触发 binderror，
  // 由页面换成 defaultCover()。
  assert.strictEqual(format.fallbackCover('unknown-slug'), '/assets/covers/unknown-slug.png')
})

check('slug 为 Object.prototype 上的键时返回字符串路径而非原型成员', () => {
  // 原型污染防护：不再走对象查表，因此 'constructor' 之类
  // 只会被当成普通 slug 拼进路径，<image src> 永远拿到字符串。
  assert.strictEqual(format.fallbackCover('constructor'), '/assets/covers/constructor.png')
  // 'toString' / 'hasOwnProperty' 含大写字母，不满足 slug 形状
  // （与服务端 ^[a-z0-9-]{1,64}$ 一致）→ 兜底图
  assert.strictEqual(format.fallbackCover('toString'), '/assets/covers/default.png')
  assert.strictEqual(format.fallbackCover('hasOwnProperty'), '/assets/covers/default.png')
  // '__proto__' 含下划线，不满足 slug 形状 → 兜底图
  assert.strictEqual(format.fallbackCover('__proto__'), '/assets/covers/default.png')
})

check('slug 形状校验拒绝路径穿越', () => {
  assert.strictEqual(format.isSafeSlug('dawn-trek'), true)
  assert.strictEqual(format.isSafeSlug('../etc/passwd'), false)
  assert.strictEqual(format.isSafeSlug('a/b'), false)
  assert.strictEqual(format.isSafeSlug('a.b'), false)
  assert.strictEqual(format.isSafeSlug('a\\b'), false)
  assert.strictEqual(format.isSafeSlug(''), false)
  assert.strictEqual(format.isSafeSlug('x'.repeat(65)), false)
  assert.strictEqual(format.fallbackCover('../secret'), '/assets/covers/default.png')
})

console.log('== formatEventTime / formatEndTime / formatRecordTime ==')

check('活动时间格式化', () => {
  const text = format.formatEventTime(local(2026, 11, 14, 6, 30))
  assert.ok(text.indexOf('11月14日') >= 0, `期望包含 11月14日，实际 ${text}`)
  assert.ok(text.indexOf('06:30') >= 0, `期望包含 06:30，实际 ${text}`)
})

check('结束时间格式化', () => {
  assert.strictEqual(format.formatEndTime(local(2026, 11, 14, 20, 5)), '20:05')
})

check('记录时间格式化', () => {
  const text = format.formatRecordTime(local(2026, 11, 2, 14, 30))
  assert.ok(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(text), `格式不符：${text}`)
})

check('空值返回兜底文案', () => {
  assert.strictEqual(format.formatEventTime(''), '待定')
  assert.strictEqual(format.formatEndTime(''), '')
  assert.strictEqual(format.formatRecordTime(''), '')
})

console.log('')
console.log('== 活动封面：内置素材白名单 ==')

check('activityCover 优先用云端主图', () => {
  assert.strictEqual(
    format.activityCover('shared/_application/activities/dawn-trek.png', 'city-walk'),
    'shared/_application/activities/dawn-trek.png'
  )
})

check('activityCover 无云端主图时用内置素材', () => {
  assert.strictEqual(format.activityCover('', 'city-walk'), '/assets/covers/city-walk.png')
  assert.strictEqual(format.activityCover(null, 'co-reading'), '/assets/covers/co-reading.png')
})

check('activityCover 封面键非法时落到中性兜底图', () => {
  assert.strictEqual(format.activityCover('', '../etc/passwd'), '/assets/covers/default.png')
  assert.strictEqual(format.activityCover('', 'a/b'), '/assets/covers/default.png')
  assert.strictEqual(format.activityCover('', ''), '/assets/covers/default.png')
  assert.strictEqual(format.activityCover('', undefined), '/assets/covers/default.png')
})

check('isAllowedCover 只认白名单内的封面键', () => {
  assert.strictEqual(format.isAllowedCover('city-walk'), true)
  assert.strictEqual(format.isAllowedCover('default'), true)
  assert.strictEqual(format.isAllowedCover('dawn-trek'), true)
  assert.strictEqual(format.isAllowedCover('not-exist'), false)
  assert.strictEqual(format.isAllowedCover('../secret'), false)
  assert.strictEqual(format.isAllowedCover(''), false)
})

check('COVER_SLUGS 每一项都能推导出随包素材路径', () => {
  assert.ok(Array.isArray(format.COVER_SLUGS) && format.COVER_SLUGS.length > 0)
  format.COVER_SLUGS.forEach((slug) => {
    assert.strictEqual(format.fallbackCover(slug), `/assets/covers/${slug}.png`)
  })
})

console.log('== parseLines / joinLines：多行文本与条目数组互转 ==')

check('多行文本拆成条目并去空行', () => {
  assert.deepStrictEqual(format.parseLines('第一条\n第二条\n\n第三条\n'), ['第一条', '第二条', '第三条'])
  assert.deepStrictEqual(format.parseLines('  带空格  '), ['带空格'])
  assert.deepStrictEqual(format.parseLines(''), [])
  assert.deepStrictEqual(format.parseLines(null), [])
  assert.deepStrictEqual(format.parseLines(undefined), [])
})

check('条目数组拼回多行文本', () => {
  assert.strictEqual(format.joinLines(['第一条', '第二条']), '第一条\n第二条')
  assert.strictEqual(format.joinLines([]), '')
  assert.strictEqual(format.joinLines(null), '')
})

check('parseLines 与 joinLines 可往返', () => {
  const lines = ['专业领队与安全保障', '全程补给点与医疗包']
  assert.strictEqual(format.joinLines(format.parseLines(format.joinLines(lines))), format.joinLines(lines))
})

console.log('== activityStatus：活动状态判定 ==')

check('下架优先于其它状态', () => {
  assert.strictEqual(format.activityStatus(false, '2026-01-01T00:00:00Z', '2025-12-31T00:00:00Z', '2026-06-01T00:00:00Z'), '已下架')
})

check('已结束优先于未开始', () => {
  const now = '2026-06-01T00:00:00Z'
  assert.strictEqual(format.activityStatus(true, '2026-05-30T00:00:00Z', '2026-05-29T00:00:00Z', now), '已结束')
})

check('未来开始的活动显示未开始', () => {
  const now = '2026-06-01T00:00:00Z'
  assert.strictEqual(format.activityStatus(true, '2026-06-05T00:00:00Z', '2026-06-03T00:00:00Z', now), '未开始')
})

check('正在进行中的活动显示进行中', () => {
  const now = '2026-06-01T00:00:00Z'
  assert.strictEqual(format.activityStatus(true, '2026-06-05T00:00:00Z', '2026-05-30T00:00:00Z', now), '进行中')
})

check('无结束时间时按开始时间判定', () => {
  const now = '2026-06-01T00:00:00Z'
  assert.strictEqual(format.activityStatus(true, null, '2026-06-03T00:00:00Z', now), '未开始')
  assert.strictEqual(format.activityStatus(true, null, '2026-05-30T00:00:00Z', now), '进行中')
})

check('状态对应的语义色 class 稳定', () => {
  assert.strictEqual(format.activityStatusClass('已下架'), 'off')
  assert.strictEqual(format.activityStatusClass('已结束'), 'ended')
  assert.strictEqual(format.activityStatusClass('未开始'), 'upcoming')
  assert.strictEqual(format.activityStatusClass('进行中'), 'live')
})

console.log('')
if (failures.length) {
  console.error(`失败 ${failures.length}/${checks} 项：`)
  failures.forEach((f) => console.error(`  - ${f.name}: ${f.message}`))
  process.exit(1)
}
console.log(`全部通过：${checks}/${checks}`)
