/**
 * 隐私授权兜底。
 *
 * 自 2023-09-15 起，微信对隐私接口默认开启管控：开发者须先在
 * 《小程序用户隐私保护指引》声明所处理的个人信息，用户同意后才可调用。
 * 未声明时对应接口会被直接禁用；已声明但用户未同意时调用会静默失败。
 *
 * 本模块提供两层兜底：
 *   1. requirePrivacyAuthorize —— 调用隐私接口前主动校验用户是否已同意；
 *   2. onNeedPrivacyAuthorization —— 在 app.js 注册，响应平台触发的授权请求。
 *
 * 两者缺一不可：只有 requirePrivacyAuthorize 时，平台弹出的授权面板无人响应；
 * 只有 onNeedPrivacyAuthorization 时，接口调用时机不受控。
 */

/** 当前用户是否已同意隐私协议。 */
function getPrivacySetting() {
  return new Promise((resolve) => {
    if (typeof wx.getPrivacySetting !== 'function') {
      // 旧基础库无此接口：视为无需授权，由调用方按业务兜底。
      resolve({ needAuthorization: false, available: false })
      return
    }
    wx.getPrivacySetting({
      success: (res) => {
        resolve({
          needAuthorization: !!(res && res.needAuthorization),
          available: true
        })
      },
      fail: () => resolve({ needAuthorization: false, available: false })
    })
  })
}

/**
 * 确保用户已同意隐私协议，然后执行回调。
 *
 * @param {Function} onGranted 用户已同意或无需同意时执行
 * @param {Function} [onDenied] 用户拒绝或授权流程失败时执行
 */
function requirePrivacyAuthorize(onGranted, onDenied) {
  const denied = typeof onDenied === 'function' ? onDenied : function () {}

  getPrivacySetting().then((setting) => {
    if (!setting.available) {
      // 基础库不支持隐私管控：直接放行，由真机表现决定是否需要提示。
      onGranted()
      return
    }
    if (!setting.needAuthorization) {
      onGranted()
      return
    }
    if (typeof wx.requirePrivacyAuthorize !== 'function') {
      denied()
      return
    }
    wx.requirePrivacyAuthorize({
      success: () => onGranted(),
      fail: () => denied()
    })
  })
}

/**
 * 在 app.js 的 onLaunch 中调用，注册平台侧的隐私授权响应。
 *
 * 平台在用户首次触发隐私接口时抛出 onNeedPrivacyAuthorization 事件，
 * 开发者需在此决定是否展示自定义弹窗；本项目采用平台默认弹窗，
 * 因此只需在事件回调中调用 resolve 即可。
 */
function registerPrivacyAuthorization() {
  if (typeof wx.onNeedPrivacyAuthorization !== 'function') {
    return
  }
  wx.onNeedPrivacyAuthorization((resolve) => {
    // resolve() 表示交由平台默认的隐私授权弹窗处理。
    resolve({ event: 'agree' })
  })
}

module.exports = {
  getPrivacySetting,
  requirePrivacyAuthorize,
  registerPrivacyAuthorization
}
