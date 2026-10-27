/**
 * 数据访问层：活动模板、活动与报名记录。
 *
 * 约束（与云端 schema 对齐，见 scripts/db/schema.sql）：
 * - 客户端绝不传 owner_id，由 DEFAULT auth.uid() 与 RLS 决定归属。
 * - 客户端也不读 owner_id：微信登录的 uid 含 openid 片段，
 *   下发给所有访问者等于泄露创建者身份。归属判定由服务端完成。
 * - 报名写入走 submit_signup RPC，容量校验（人数口径）在服务端原子完成。
 * - 客户端对 registrations 只有 SELECT 权限；取消报名走 cancel_registration RPC。
 * - 报名人数一律为「人数」（含本人），与服务端 sum(companions) 口径一致。
 * - 活动发布/编辑走 create_activity / update_activity RPC：
 *   归属、slug、封面白名单、活动数上限全部在服务端裁决。
 */
const { cloud } = require('./cloud')

const ACTIVITY_FIELDS =
  'id, slug, title, summary, cover_path, cover_slug, location, starts_at, ends_at, capacity, price_note, highlights, notes, published, template_id'

const TEMPLATE_FIELDS =
  'id, slug, title, summary, cover_slug, highlights, notes, default_capacity, default_duration_minutes, sort_order'

/** 拉取全部已发布活动（公开可读表）。 */
async function listActivities() {
  const { data, error } = await cloud.database
    .from('activities')
    .select(ACTIVITY_FIELDS)
    .order('starts_at', { ascending: true })
  if (error) {
    // 不透出后端原始错误：PostgREST 的 message 会带表名、列名等 SQL 细节。
    throw new Error('活动列表加载失败，请稍后重试')
  }
  // 读策略是「已发布全员可读 + 创建者可见自己下架的活动」，
  // 列表页只展示已发布活动：published 缺失一律按未发布处理。
  return (data || []).filter((row) => row.published === true)
}

/** 拉取单个活动；未发布或不存在时返回 null。 */
async function getActivity(id) {
  const { data, error } = await cloud.database
    .from('activities')
    .select(ACTIVITY_FIELDS)
    .eq('id', id)
    .maybeSingle()
  if (error) {
    throw new Error('活动信息加载失败，请稍后重试')
  }
  return data || null
}

/**
 * 拉取活动模板（平台维护的内容，只读）。
 * 模板不承载报名，仅作为「活动骨架」供发起人参考与套用。
 */
async function listTemplates() {
  const { data, error } = await cloud.database
    .from('activity_templates')
    .select(TEMPLATE_FIELDS)
    .order('sort_order', { ascending: true })
  if (error) {
    throw new Error('活动模板加载失败，请稍后重试')
  }
  return data || []
}

/**
 * 各活动已报名人数（跨用户聚合，由服务端 SECURITY DEFINER 函数提供，人数口径）。
 *
 * 失败必须抛出而不是静默返回空对象：静默返回会被页面当成「0 人已报名」，
 * 让用户误以为名额充足。调用方据此展示「名额待刷新」，或直接报错。
 */
async function getRegistrationStats() {
  const { data, error } = await cloud.database.rpc('registration_stats')
  if (error) {
    throw new Error('报名人数加载失败，请稍后重试')
  }
  const stats = {}
  ;(data || []).forEach((row) => {
    stats[row.activity_id] = Number(row.signed_up || 0)
  })
  return stats
}

/**
 * 提交报名。
 * @param {number} activityId
 * @param {{companions:number, contact:string, remark:string, ownerName:string, coverPath?:string}} payload
 */
async function signup(activityId, payload) {
  const { data, error } = await cloud.database.rpc('submit_signup', {
    p_activity_id: activityId,
    p_companions: payload.companions,
    p_contact: payload.contact,
    p_remark: payload.remark || null,
    p_owner_name: payload.ownerName || null,
    p_cover_path: payload.coverPath || null
  })
  if (error) {
    throw new Error(readableSignupError(error))
  }
  return (data || [])[0] || null
}

/** 我的报名记录（RLS 已按 owner_id 过滤）。 */
async function listMyRegistrations() {
  const { data, error } = await cloud.database
    .from('registrations')
    .select('id, activity_id, companions, contact, remark, cover_path, status, created_at')
    // id 作二级排序键：created_at 精度有限时保证顺序稳定
    .order('created_at', { ascending: false })
    .order('id', { ascending: false })
  if (error) {
    throw new Error('报名记录加载失败，请稍后重试')
  }
  return data || []
}

/** 取消报名（服务端软取消，仅限本人有效记录）。 */
async function cancelRegistration(id) {
  const { data, error } = await cloud.database.rpc('cancel_registration', {
    p_registration_id: id
  })
  if (error) {
    throw new Error(readableCancelError(error))
  }
  return data === true || data === 'true'
}

/** 报名成功后补挂配图（服务端校验路径必须落在本人私有目录）。 */
async function attachCover(registrationId, coverPath) {
  const { data, error } = await cloud.database.rpc('attach_registration_cover', {
    p_registration_id: registrationId,
    p_cover_path: coverPath
  })
  if (error) {
    throw new Error(readableCancelError(error))
  }
  return data === true || data === 'true'
}

/**
 * 发布活动（真人发布活动的唯一入口）。
 *
 * 归属、slug、封面白名单、活动数上限全部由服务端裁决，
 * 客户端只提供用户填写的内容。
 *
 * @param {object} payload
 * @returns {Promise<{id:number, slug:string}>}
 */
async function createActivity(payload) {
  const { data, error } = await cloud.database.rpc('create_activity', {
    p_template_id: payload.templateId || null,
    p_title: payload.title,
    p_summary: payload.summary || null,
    p_location: payload.location,
    p_starts_at: payload.startsAt,
    p_ends_at: payload.endsAt || null,
    p_capacity: payload.capacity,
    p_price_note: payload.priceNote || null,
    p_highlights: payload.highlights || [],
    p_notes: payload.notes || [],
    p_cover_slug: payload.coverSlug || null
  })
  if (error) {
    throw new Error(readableActivityError(error))
  }
  const row = (data || [])[0] || null
  return row ? { id: row.activity_id, slug: row.activity_slug } : null
}

/**
 * 编辑活动（含下架 / 重新上架）。
 * 只有归属人可调用，服务端会校验归属。
 */
async function updateActivity(payload) {
  const { data, error } = await cloud.database.rpc('update_activity', {
    p_activity_id: payload.activityId,
    p_title: payload.title,
    p_summary: payload.summary || null,
    p_location: payload.location,
    p_starts_at: payload.startsAt,
    p_ends_at: payload.endsAt || null,
    p_capacity: payload.capacity,
    p_price_note: payload.priceNote || null,
    p_highlights: payload.highlights || [],
    p_notes: payload.notes || [],
    p_cover_slug: payload.coverSlug || null,
    p_published: payload.published !== false
  })
  if (error) {
    throw new Error(readableActivityError(error))
  }
  return data === true || data === 'true'
}

/** 我发布的活动（服务端按登录身份过滤，含已下架）。 */
async function listMyActivities() {
  const { data, error } = await cloud.database.rpc('my_activities')
  if (error) {
    throw new Error(readableActivityError(error))
  }
  return (data || []).map((row) => ({
    id: row.activity_id,
    slug: row.slug,
    title: row.title,
    summary: row.summary,
    coverSlug: row.cover_slug,
    location: row.location,
    startsAt: row.starts_at,
    endsAt: row.ends_at,
    capacity: row.capacity,
    priceNote: row.price_note,
    highlights: row.highlights || [],
    notes: row.notes || [],
    published: row.published === true,
    signedUp: Number(row.signed_up || 0)
  }))
}

/**
 * 把服务端错误映射为可读文案。
 * 兜底不得直出后端原始错误，避免把 SQL 细节暴露给终端用户。
 */
function readableSignupError(error) {
  const raw = String((error && error.message) || '')
  if (raw.indexOf('名额已满') >= 0) {
    return '名额已满，看看其他场次吧'
  }
  if (raw.indexOf('活动已开始') >= 0) {
    return '活动已开始，报名通道已关闭'
  }
  if (raw.indexOf('活动不存在') >= 0 || raw.indexOf('已下架') >= 0) {
    return '活动不存在或已下架'
  }
  if (raw.indexOf('你已报名') >= 0 || raw.indexOf('23505') >= 0) {
    return '你已报名该活动'
  }
  if (raw.indexOf('同行人数') >= 0) {
    return '同行人数需在 1 到 4 之间'
  }
  if (raw.indexOf('手机号') >= 0) {
    return '请输入正确的 11 位手机号'
  }
  if (raw.indexOf('备注') >= 0) {
    return '备注不能超过 100 字'
  }
  if (raw.indexOf('配图路径') >= 0) {
    return '配图上传失败，请重新选择'
  }
  if (raw.indexOf('42501') >= 0 || raw.indexOf('登录') >= 0) {
    return '登录状态已失效，请重新授权登录'
  }
  if (raw.indexOf('401') >= 0) {
    return '登录状态已失效，请重新授权登录'
  }
  if (raw.indexOf('网络') >= 0 || raw.indexOf('network') >= 0 || raw.indexOf('timeout') >= 0) {
    return '网络连接不稳定，请稍后重试'
  }
  return '报名失败，请稍后重试'
}

/** 取消报错的文案映射。 */
function readableCancelError(error) {
  const raw = String((error && error.message) || '')
  if (raw.indexOf('42501') >= 0 || raw.indexOf('登录') >= 0) {
    return '登录状态已失效，请重新授权登录'
  }
  if (raw.indexOf('网络') >= 0 || raw.indexOf('network') >= 0) {
    return '网络连接不稳定，请稍后重试'
  }
  return '操作失败，请稍后重试'
}

/**
 * 发布/编辑活动的错误文案映射。
 *
 * 服务端已经用中文抛出了可直接展示的业务错误（如「活动名称不能超过 40 字」），
 * 这里按关键字透传；未识别的错误一律落到通用兜底，不直出 SQL 细节。
 */
function readableActivityError(error) {
  const raw = String((error && error.message) || '')
  const known = [
    '请先完成微信授权登录',
    '活动模板不可用',
    '请填写活动名称',
    '活动名称不能超过',
    '活动简介不能超过',
    '请填写活动地点',
    '活动地点不能超过',
    '请选择活动开始时间',
    '活动开始时间必须晚于当前时间',
    '活动结束时间必须晚于开始时间',
    '名额不能为负数',
    '名额不能超过',
    '费用说明不能超过',
    '活动亮点格式不正确',
    '活动亮点最多',
    '每条活动亮点需在',
    '报名须知格式不正确',
    '报名须知最多',
    '每条报名须知需在',
    '封面选择无效',
    '你同时进行的活动过多',
    '活动不存在或无权修改',
    '名额不能少于已报名人数',
    '发布状态无效'
  ]
  for (let i = 0; i < known.length; i += 1) {
    if (raw.indexOf(known[i]) >= 0) {
      return known[i]
    }
  }
  if (raw.indexOf('42501') >= 0 || raw.indexOf('登录') >= 0) {
    return '登录状态已失效，请重新授权登录'
  }
  if (raw.indexOf('网络') >= 0 || raw.indexOf('network') >= 0 || raw.indexOf('timeout') >= 0) {
    return '网络连接不稳定，请稍后重试'
  }
  return '操作失败，请稍后重试'
}

module.exports = {
  listActivities,
  getActivity,
  listTemplates,
  getRegistrationStats,
  signup,
  listMyRegistrations,
  cancelRegistration,
  attachCover,
  createActivity,
  updateActivity,
  listMyActivities,
  readableSignupError
}
