/**
 * 会话与授权登录。
 *
 * 小程序微信登录：wx.login 取 code → cloud.auth.signInWithWechat(code, appid)。
 * appid 取运行时真实值，不硬编码试用/正式任一 appid。
 */
const { cloud } = require('./cloud')

const SESSION_KEY = 'jbzl_session'

function currentAppId() {
  try {
    const info = wx.getAccountInfoSync()
    return (info && info.miniProgram && info.miniProgram.appId) || ''
  } catch (error) {
    return ''
  }
}

/** 恢复已有会话；无会话或已过期返回 null。 */
async function restoreSession() {
  try {
    const { data, error } = await cloud.auth.getSession()
    if (error || !data) {
      return null
    }
    return data
  } catch (error) {
    return null
  }
}

/** 读取本地缓存的会话快照，用于首屏秒开。 */
function readCachedUser() {
  try {
    const cached = wx.getStorageSync(SESSION_KEY) || null
    // 旧版本可能缓存了含令牌的完整会话对象，这里按白名单重新裁剪，
    // 避免历史数据里的 accessToken / refreshToken 继续留在本机。
    return toCachedUser(cached)
  } catch (error) {
    return null
  }
}

/**
 * 本地缓存的会话快照字段白名单。
 *
 * 刻意不缓存 accessToken / refreshToken：这两个是会话凭证，
 * 明文落 wx storage 会让任何能读本机存储的环节拿到长期有效凭证。
 * 只缓存展示需要的公开资料；真正的令牌由 SDK 自己管理生命周期。
 */
const CACHED_USER_FIELDS = ['id', 'name', 'avatarUrl', 'provider']

/** 裁剪为白名单字段后的用户快照。 */
function toCachedUser(user) {
  if (!user || typeof user !== 'object') {
    return null
  }
  const snapshot = {}
  CACHED_USER_FIELDS.forEach((key) => {
    if (user[key] !== undefined && user[key] !== null) {
      snapshot[key] = user[key]
    }
  })
  return snapshot.id ? snapshot : null
}

function cacheUser(user) {
  try {
    const snapshot = toCachedUser(user)
    if (snapshot) {
      wx.setStorageSync(SESSION_KEY, snapshot)
    } else {
      wx.removeStorageSync(SESSION_KEY)
    }
  } catch (error) {
    // 缓存失败不阻断主流程
  }
}

/**
 * 发起微信授权登录。
 * 返回 { ok, user, message }。
 */
function signIn() {
  return new Promise((resolve) => {
    wx.login({
      success: async (res) => {
        if (!res || !res.code) {
          resolve({ ok: false, message: '微信授权失败，请重试' })
          return
        }
        try {
          const appid = currentAppId()
          const { data, error } = await cloud.auth.signInWithWechat(res.code, appid)
          if (error || !data) {
            resolve({ ok: false, message: (error && error.message) || '微信授权失败，请重试' })
            return
          }
          cacheUser(data.user)
          resolve({ ok: true, user: data.user })
        } catch (error) {
          resolve({ ok: false, message: '微信授权失败，请重试' })
        }
      },
      fail: (error) => {
        resolve({ ok: false, message: (error && error.errMsg) || '微信授权失败，请重试' })
      }
    })
  })
}

/** 退出登录。 */
async function signOut() {
  try {
    await cloud.auth.signOut()
  } catch (error) {
    // 忽略：本地清理照常执行
  }
  cacheUser(null)
}

/** 取当前用户昵称（可能为空）。 */
function displayName(user) {
  if (!user) {
    return ''
  }
  return user.name || user.nickname || ''
}

module.exports = {
  restoreSession,
  readCachedUser,
  signIn,
  signOut,
  displayName
}
