/**
 * 云端存储：读取签名地址 + 上传二进制。
 *
 * 为什么上传不走 SDK 的 storage.upload：
 * SDK 的小程序端 fetch（createMiniProgramFetch）只接受字符串 body，
 * 传 ArrayBuffer 会直接抛 "暂不支持非字符串 body（ArrayBuffer/FormData 待补）"。
 * 而 wx.request 的 data 本身支持 ArrayBuffer。
 *
 * 因此这里用「SDK 签名 + wx.request 直传」的组合：
 * 1. 调 SDK 的 createSignedUploadUrl 拿到预签名上传 URL（鉴权与路径规则全在 SDK 内）；
 * 2. 用 wx.request 把字节 PUT 到该预签名 URL。
 * 这样既不硬编码云端路径，也不绕过 SDK 的鉴权模型。
 */
const { cloud } = require('./cloud')

/** 缓存控制：与 SDK 默认值一致（秒）。 */
const DEFAULT_CACHE_CONTROL = 3600

/**
 * 取某个存储对象的签名下载地址。
 * @param {string} path 形如 users/<uid>/registrations/1.png
 * @param {number} expiresIn 有效（秒）
 * @returns {Promise<string>} 签名 URL；失败返回空串
 */
async function signedUrl(path, expiresIn) {
  if (!path) {
    return ''
  }
  try {
    const signed = await cloud.storage.createSignedUrl(path, expiresIn || DEFAULT_CACHE_CONTROL)
    if (signed && !signed.error && signed.data) {
      // SDK 返回字段是 signedUrl（不是 url）
      return signed.data.signedUrl || ''
    }
  } catch (error) {
    // 路径非法时 SDK 会同步抛错；单个对象失败不应影响其它对象
  }
  return ''
}

/**
 * 批量取签名地址。单个失败不影响其它项。
 * @param {string[]} paths
 * @param {number} expiresIn
 * @returns {Promise<Object<string, string>>} path → 签名 URL
 */
async function signedUrls(paths, expiresIn) {
  const out = {}
  const list = (paths || []).filter(Boolean)
  for (const path of list) {
    const url = await signedUrl(path, expiresIn)
    if (url) {
      out[path] = url
    }
  }
  return out
}

/**
 * 上传二进制到云端存储。
 *
 * @param {string} path 形如 users/<uid>/registrations/1.png
 * @param {ArrayBuffer} buffer 文件字节
 * @param {{contentType?: string, cacheControl?: number}} options
 * @returns {Promise<{ok: boolean, message: string}>}
 */
async function uploadBinary(path, buffer, options) {
  const opts = options || {}
  if (!path || !buffer) {
    return { ok: false, message: '上传参数不完整' }
  }
  const contentType = opts.contentType || 'application/octet-stream'
  const cacheControl = opts.cacheControl || DEFAULT_CACHE_CONTROL

  // 1. 由 SDK 取得预签名上传 URL（含 token 与正确的对象路径）
  let signUrl = ''
  try {
    const signed = await cloud.storage.createSignedUploadUrl(path, { upsert: true })
    if (signed && !signed.error && signed.data && signed.data.signedUrl) {
      signUrl = signed.data.signedUrl
    }
  } catch (error) {
    return { ok: false, message: '上传准备失败，请稍后重试' }
  }
  if (!signUrl) {
    return { ok: false, message: '上传准备失败，请稍后重试' }
  }

  // 2. 用 wx.request 直传字节（其 data 支持 ArrayBuffer）
  //
  // 覆盖写策略：不依赖 upsert 语义，改用「撞名先删后传」。
  // 实测结论：预签名 PUT 对已存在对象返回 409 STORAGE_KEY_ALREADY_EXISTS，
  // 而带 x-upsert 头的行为在服务端并不一致（SDK 的 createSignedUploadUrl
  // 只把该头烧进签发请求，未必作用于最终 PUT）。
  // 因此先尝试直传；若返回 409，则删掉同名对象再重试一次。
  // 报名配图路径 users/<uid>/registrations/<id>.png 中 <id> 每次报名都不同，
  // 正常流程不会撞名；这条重试兜住的是「同一条报名换图重传」。
  const attempt = (targetUrl) =>
    new Promise((resolve) => {
      wx.request({
        url: targetUrl,
        method: 'PUT',
        header: {
          'content-type': contentType,
          'cache-control': `max-age=${cacheControl}`
        },
        data: buffer,
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve({ ok: true, message: '' })
            return
          }
          resolve({ ok: false, message: `上传失败（HTTP ${res.statusCode}）`, status: res.statusCode })
        },
        fail: (err) => {
          const msg = (err && err.errMsg) || ''
          if (msg.indexOf('timeout') >= 0) {
            resolve({ ok: false, message: '网络超时，请稍后重试' })
            return
          }
          resolve({ ok: false, message: '网络连接不稳定，请稍后重试' })
        }
      })
    })

  const first = await attempt(signUrl)
  if (first.ok || first.status !== 409) {
    return first
  }

  // 撞名：删掉同名对象后重试一次
  try {
    const removed = await cloud.storage.remove([path])
    if (removed && removed.error) {
      return { ok: false, message: '上传失败（同名文件替换未成功）' }
    }
  } catch (error) {
    return { ok: false, message: '上传失败（同名文件替换未成功）' }
  }
  return attempt(signUrl)
}

module.exports = {
  signedUrl,
  signedUrls,
  uploadBinary
}
