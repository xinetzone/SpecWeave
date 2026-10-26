/**
 * 展示层格式化工具（纯函数，便于单测）。
 *
 * 口径约定：报名人数一律为「人数」（含本人），与云端 sum(companions) 一致。
 */

/** 2026-11-14T06:30:00+08:00 → 11月14日 周六 06:30 */
function formatEventTime(value) {
  if (!value) {
    return '待定'
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return '待定'
  }
  const week = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][date.getDay()]
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hh = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')
  return `${month}月${day}日 ${week} ${hh}:${mm}`
}

/** 区间时间的结束时刻。 */
function formatEndTime(value) {
  if (!value) {
    return ''
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  const hh = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
}

/**
 * 相对天数：还有 19 天 / 明天开始 / 今天开始 / 已结束。
 * 按「日历日」而非 24 小时整除计算，避免把「明天早上」多算成两天。
 */
function formatCountdown(value, now) {
  if (!value) {
    return ''
  }
  const target = new Date(value)
  if (Number.isNaN(target.getTime())) {
    return ''
  }
  const base = now ? new Date(now) : new Date()
  if (Number.isNaN(base.getTime())) {
    return ''
  }
  const startOfTarget = new Date(target.getFullYear(), target.getMonth(), target.getDate()).getTime()
  const startOfBase = new Date(base.getFullYear(), base.getMonth(), base.getDate()).getTime()
  const days = Math.round((startOfTarget - startOfBase) / 86400000)
  if (days > 1) {
    return `还有 ${days} 天`
  }
  if (days === 1) {
    return '明天开始'
  }
  if (days === 0) {
    return '今天开始'
  }
  return '已结束'
}

/** 报名记录创建时间：2026-11-02 14:30 */
function formatRecordTime(value) {
  if (!value) {
    return ''
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const hh = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${hh}:${mm}`
}

/** 报名状态文案。 */
function statusText(status) {
  if (status === 'confirmed') {
    return '已确认'
  }
  if (status === 'cancelled') {
    return '已取消'
  }
  return '处理中'
}

/** 名额文案：还剩 96 位 / 名额已满 / 不限名额（capacity<=0 表示不限）。 */
function quotaText(capacity, signedUp) {
  const total = Number(capacity) || 0
  const taken = Number(signedUp) || 0
  if (total <= 0) {
    return '不限名额'
  }
  const left = total - taken
  if (left <= 0) {
    return '名额已满'
  }
  return `还剩 ${left} 位`
}

/** 是否已满（capacity<=0 视为不限名额，永不满）。 */
function isFull(capacity, signedUp) {
  const total = Number(capacity) || 0
  if (total <= 0) {
    return false
  }
  return (Number(signedUp) || 0) >= total
}

/** 报名人数占比（0-100）。 */
function percent(capacity, signedUp) {
  const total = Number(capacity) || 0
  if (total <= 0) {
    return 0
  }
  const ratio = (Number(signedUp) || 0) / total
  return Math.max(0, Math.min(100, Math.round(ratio * 100)))
}

/**
 * 本次报名（含同行人）是否还能装下。
 * 口径与服务端 sum(companions) 一致；capacity<=0 表示不限名额，永不禁用。
 */
function canFit(capacity, signedUp, companions) {
  const total = Number(capacity) || 0
  if (total <= 0) {
    return true
  }
  const taken = Number(signedUp) || 0
  const want = Number(companions) || 1
  return taken + want <= total
}

/**
 * 内置主图降级策略。
 *
 * 背景：匿名访客无法签发云端存储地址（私有桶没有公开读通道），
 * 所以内置副本是匿名用户唯一能看到的主图来源。
 *
 * 早期实现是一张「slug → 路径」硬编码表，新增活动忘了改表就会一直落默认图，
 * 且新增活动必须同时改代码和加图片。现在改为规则化：
 *   - 路径按 `assets/covers/<slug>.png` 推导，与云端
 *     `shared/_application/activities/<slug>.png` 同一套命名规则；
 *   - 新增活动只要把 `<slug>.png` 放进 assets/covers/ 就自动命中，无需改代码；
 *   - 本地没有对应文件时 <image> 触发 error 事件，由页面降级到 defaultCover()。
 *
 * 另有一层安全约束：slug 必须先过形状校验再拼进路径，
 * 避免 '../' 之类的路径穿越；也不再走对象查表，
 * 因此 'constructor' / 'toString' 之类不会命中原型链。
 */
const COVER_DIR = '/assets/covers'
const DEFAULT_COVER = COVER_DIR + '/default.png'

/** slug 形状校验：小写字母、数字、连字符，1~64 位。 */
function isSafeSlug(slug) {
  return typeof slug === 'string' && /^[a-z0-9-]{1,64}$/.test(slug)
}

/** 兜底主图（始终存在，随包分发）。 */
function defaultCover() {
  return DEFAULT_COVER
}

/**
 * 推导某活动的内置主图路径。
 * 返回的是候选路径：本地没有该文件时，由 <image binderror> 降级到 defaultCover()。
 */
function fallbackCover(slug) {
  if (!isSafeSlug(slug)) {
    return DEFAULT_COVER
  }
  return COVER_DIR + '/' + slug + '.png'
}

module.exports = {
  formatEventTime,
  formatEndTime,
  formatCountdown,
  formatRecordTime,
  statusText,
  quotaText,
  isFull,
  percent,
  canFit,
  fallbackCover,
  defaultCover,
  isSafeSlug
}
