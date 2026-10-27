const auth = require('./utils/auth')
const privacy = require('./utils/privacy')

App({
  globalData: {
    user: null,
    signedIn: false,
    /** 会话恢复是否已完成：页面据此决定是否需要等待。 */
    sessionReady: false
  },

  onLaunch() {
    // 注册平台隐私授权响应：用户首次触发隐私接口时由平台抛出该事件，
    // 不注册则授权面板无人响应，接口调用静默失败。
    privacy.registerPrivacyAuthorization()
    const cached = auth.readCachedUser()
    if (cached) {
      this.globalData.user = cached
      this.globalData.signedIn = true
    }
    this.restoreSession()
  },

  /**
   * 恢复服务端会话。
   *
   * 幂等：多个调用方共享同一个 in-flight promise。
   * onLaunch 会启动一次恢复，页面 onShow 又会调 ensureSession，
   * 若各自独立发起请求就会并发两次 restoreSession。
   * 失败不阻塞首屏（保留本地缓存快照），但一定会把 sessionReady 置为 true，
   * 让页面知道「登录态已确定」，避免读到竞态中的中间态。
   */
  async restoreSession() {
    if (this._restorePromise) {
      return this._restorePromise
    }
    this._restorePromise = (async () => {
      try {
        const session = await auth.restoreSession()
        if (session && session.user) {
          this.globalData.user = session.user
          this.globalData.signedIn = true
          auth.cacheUser(session.user)
        } else {
          this.globalData.user = auth.readCachedUser()
          this.globalData.signedIn = !!this.globalData.user
        }
      } catch (error) {
        this.globalData.user = auth.readCachedUser()
        this.globalData.signedIn = !!this.globalData.user
      } finally {
        this.globalData.sessionReady = true
      }
      return this.globalData.signedIn
    })()
    return this._restorePromise
  },

  /** 等待会话恢复完成；供页面在需要确定登录态时 await。 */
  async ensureSession() {
    if (!this.globalData.sessionReady) {
      await this.restoreSession()
    }
    return this.globalData.signedIn
  },

  /** 统一的授权登录入口，返回 { ok, message }。 */
  async signIn() {
    const result = await auth.signIn()
    if (result.ok) {
      this.globalData.user = result.user
      this.globalData.signedIn = true
      this.globalData.sessionReady = true
    }
    return result
  },

  async signOut() {
    await auth.signOut()
    this.globalData.user = null
    this.globalData.signedIn = false
  }
})
