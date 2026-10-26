const app = getApp()
const api = require('../../utils/api')
const format = require('../../utils/format')

Page({
  data: {
    loading: true,
    errorText: '',
    activityId: 0,
    detail: null,
    signedUp: 0,
    signedIn: false,
    signingIn: false
  },

  onLoad(options) {
    const id = Number(options.id)
    if (!id) {
      this.setData({ loading: false, errorText: '活动参数无效' })
      return
    }
    this.setData({ activityId: id })
    this.loadDetail()
  },

  async onShow() {
    const signedIn = await app.ensureSession()
    this.setData({ signedIn })
    // 从报名页返回时，名额可能已变化，回到详情页重新同步。
    if (this.data.detail) {
      this.refreshQuota()
    }
  },

  async loadDetail() {
    this.setData({ loading: true, errorText: '' })
    try {
      const activity = await api.getActivity(this.data.activityId)
      if (!activity) {
        this.setData({ loading: false, errorText: '活动不存在或已下架' })
        return
      }
      // 人数是增强信息，加载失败不应让整个详情页消失；
      // 但也不能当成 0，否则会把「还有名额」误报给用户。
      let signedUp = 0
      let quotaKnown = true
      try {
        const stats = await api.getRegistrationStats()
        signedUp = stats[activity.id] || 0
      } catch (statError) {
        quotaKnown = false
      }
      this.setData({
        loading: false,
        signedUp,
        detail: {
          id: activity.id,
          slug: activity.slug,
          title: activity.title,
          summary: activity.summary,
          location: activity.location,
          startsAt: format.formatEventTime(activity.starts_at),
          endsAt: format.formatEndTime(activity.ends_at),
          countdown: format.formatCountdown(activity.starts_at),
          capacity: activity.capacity,
          priceNote: activity.price_note,
          highlights: activity.highlights || [],
          notes: activity.notes || [],
          quotaKnown,
          quotaText: quotaKnown
            ? format.quotaText(activity.capacity, signedUp)
            : '人数待刷新',
          percent: quotaKnown ? format.percent(activity.capacity, signedUp) : 0,
          // 封面：优先云端主图，否则用内置素材（cover_slug）。
          // 不能用 slug 推导：真人发布的活动 slug 由服务端生成（act-xxx），
          // 随包没有同名素材，用 slug 推导会永远落默认图。
          cover: format.activityCover(activity.cover_path, activity.cover_slug),
          // 人数未知时不能断言「已满」，否则会误禁报名入口
          full: quotaKnown ? format.isFull(activity.capacity, signedUp) : false
        }
      })
      this.loadCover(activity)
    } catch (error) {
      this.setData({
        loading: false,
        errorText: (error && error.message) || '活动信息加载失败，请稍后重试'
      })
    }
  },

  /**
   * 内置主图缺失时降级到随包分发的默认图。
   * 云端签名地址失效、或内置副本未随包分发时触发。
   */
  onCoverError() {
    const fallback = format.defaultCover()
    if (this.data.detail.cover === fallback) {
      return
    }
    this.setData({ 'detail.cover': fallback })
  },

  /** 仅刷新名额与进度，不整页重载。 */
  async refreshQuota() {
    try {
      const stats = await api.getRegistrationStats()
      const activityId = this.data.detail.id
      const signedUp = stats[activityId] || 0
      this.setData({
        signedUp,
        'detail.quotaKnown': true,
        'detail.quotaText': format.quotaText(this.data.detail.capacity, signedUp),
        'detail.percent': format.percent(this.data.detail.capacity, signedUp),
        'detail.full': format.isFull(this.data.detail.capacity, signedUp)
      })
    } catch (error) {
      // 名额刷新失败不打断浏览，但也不能把已知人数清零当成 0 人
    }
  },

  async loadCover(activity) {
    if (!activity.cover_path) {
      return
    }
    try {
      const storage = require('../../utils/storage')
      const url = await storage.signedUrl(activity.cover_path, 3600)
      if (url) {
        this.setData({ 'detail.cover': url })
      }
    } catch (error) {
      // 保持内置降级主图
    }
  },

  async onTapSignIn() {
    this.setData({ signingIn: true })
    const result = await app.signIn()
    this.setData({ signingIn: false })
    if (!result.ok) {
      wx.showToast({ title: result.message || '授权失败', icon: 'none' })
      return
    }
    this.setData({ signedIn: true })
    wx.showToast({ title: '授权成功', icon: 'success' })
  },

  onTapSignup() {
    const detail = this.data.detail
    if (!detail) {
      return
    }
    if (detail.full) {
      wx.showToast({ title: '名额已满，看看其他场次吧', icon: 'none' })
      return
    }
    wx.navigateTo({ url: `/pages/signup/signup?id=${detail.id}` })
  }
})
