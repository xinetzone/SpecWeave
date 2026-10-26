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

/**
 * 内置封面素材白名单。
 *
 * 为什么封面只能从白名单里选、不能由用户上传图片：
 *   端用户可写的云存储作用域只有 users/<uid>/（私有）与 shared/<uid>/（路径内嵌 uid），
 *   而不含用户标识的 shared/_application/ 仅管理员可写（端用户会话一律 403）。
 *   因此「用户上传封面 + 所有人可见 + 路径不含创建者标识」三者在当前平台约束下
 *   不可兼得。封面改走内置素材：路径不含任何用户标识，随包分发，匿名访客也能看到。
 *
 * 这份名单必须与云端 create_activity / update_activity 里的白名单一致，
 * 也必须与 assets/covers/ 下实际存在的素材一致——三者由结构测试逐项对齐。
 */
const COVER_SLUGS = [
  'dawn-trek',
  'night-market',
  'island-week',
  'city-walk',
  'co-reading',
  'default'
]

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

/**
 * 活动的展示封面。
 *
 * 优先用云端主图（cover_path 命中平台已发布主图时），
 * 否则退回内置素材（cover_slug 指向的随包素材）。
 * 两者都缺时落到中性兜底图。
 *
 * @param {string} coverPath 云端主图路径（可能为空）
 * @param {string} coverSlug 内置素材键（可能为空）
 * @returns {string}
 */
function activityCover(coverPath, coverSlug) {
  if (coverPath) {
    return coverPath
  }
  if (isSafeSlug(coverSlug)) {
    return fallbackCover(coverSlug)
  }
  return DEFAULT_COVER
}

/** 封面是否在白名单内（服务端同款判定，客户端先做一次以减少无效请求）。 */
function isAllowedCover(slug) {
  return COVER_SLUGS.indexOf(slug) >= 0
}

/**
 * 把多行文本拆成条目数组（用于「亮点」「报名须知」输入框）。
 * 空行丢弃，每条去首尾空白。
 */
function parseLines(text) {
  if (typeof text !== 'string') {
    return []
  }
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
}

/** 把条目数组拼回多行文本（用于编辑时回填输入框）。 */
function joinLines(list) {
  if (!Array.isArray(list)) {
    return ''
  }
  return list.join('\n')
}

/**
 * 活动状态文案（我的活动页）。
 * 优先级：已下架 > 已结束 > 进行中 > 未开始。
 *
 * @param {boolean} published 是否已发布
 * @param {string} endsAt 结束时间
 * @param {string} startsAt 开始时间
 * @param {string} now 当前时间（可注入，便于测试）
 */
function activityStatus(published, endsAt, startsAt, now) {
  if (!published) {
    return '已下架'
  }
  const base = now ? new Date(now) : new Date()
  if (endsAt) {
    const end = new Date(endsAt)
    if (!Number.isNaN(end.getTime()) && end.getTime() <= base.getTime()) {
      return '已结束'
    }
  }
  if (startsAt) {
    const start = new Date(startsAt)
    if (!Number.isNaN(start.getTime()) && start.getTime() > base.getTime()) {
      return '未开始'
    }
  }
  return '进行中'
}

/** 状态对应的语义色 class 后缀（wxss 里按 class 取色）。 */
function activityStatusClass(status) {
  if (status === '已下架') {
    return 'off'
  }
  if (status === '已结束') {
    return 'ended'
  }
  if (status === '未开始') {
    return 'upcoming'
  }
  return 'live'
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
  isSafeSlug,
  activityCover,
  isAllowedCover,
  COVER_SLUGS,
  parseLines,
  joinLines,
  activityStatus,
  activityStatusClass
}
