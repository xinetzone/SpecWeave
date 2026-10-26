/**
 * 数据访问层：活动与报名记录。
 *
 * 约束（与云端 schema 对齐，见 scripts/db/schema.sql）：
 * - 客户端绝不传 owner_id，由 DEFAULT auth.uid() 与 RLS 决定归属。
 * - 客户端也不读 owner_id：微信登录的 uid 含 openid 片段，
 *   下发给所有访问者等于泄露创建者身份。归属判定由服务端完成。
 * - 报名写入走 submit_signup RPC，容量校验（人数口径）在服务端原子完成。
 * - 客户端对 registrations 只有 SELECT 权限；取消报名走 cancel_registration RPC。
 * - 报名人数一律为「人数」（含本人），与服务端 sum(companions) 口径一致。
 */
const { cloud } = require('./cloud')

const ACTIVITY_FIELDS =
  'id, slug, title, summary, cover_path, location, starts_at, ends_at, capacity, price_note, highlights, notes, published'

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

/** 主图绑定报错的文案映射（不直出后端原始错误）。 */
function readableCoverError(error) {
  const raw = String((error && error.message) || '')
  if (raw.indexOf('创建者') >= 0) {
    return '只有活动创建者可以设置主图'
  }
  if (raw.indexOf('主图路径') >= 0) {
    return '主图上传失败，请重新选择图片'
  }
  if (raw.indexOf('活动不存在') >= 0) {
    return '活动不存在或已下架'
  }
  if (raw.indexOf('42501') >= 0 || raw.indexOf('登录') >= 0) {
    return '登录状态已失效，请重新授权登录'
  }
  if (raw.indexOf('网络') >= 0 || raw.indexOf('network') >= 0) {
    return '网络连接不稳定，请稍后重试'
  }
  return '主图设置失败，请稍后重试'
}

module.exports = {
  listActivities,
  getActivity,
  getRegistrationStats,
  signup,
  listMyRegistrations,
  cancelRegistration,
  attachCover,
  readableSignupError
}
