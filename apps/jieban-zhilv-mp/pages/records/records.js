const app = getApp()
const api = require('../../utils/api')
const format = require('../../utils/format')

Page({
  data: {
    loading: true,
    errorText: '',
    records: [],
    signedIn: false,
    signingIn: false,
    cancellingId: 0
  },

  onLoad() {
    this.refreshSession()
  },

  async onShow() {
    const signedIn = await app.ensureSession()
    this.setData({ signedIn })
    if (signedIn) {
      this.loadRecords()
    } else {
      this.setData({ loading: false, records: [] })
    }
  },

  /** 首次进入时等待会话恢复，避免误判为未登录。 */
  async refreshSession() {
    const signedIn = await app.ensureSession()
    this.setData({ signedIn })
  },

  async loadRecords() {
    this.setData({ loading: true, errorText: '' })
    try {
      // 报名列表是核心数据，活动元数据是补充；两者用 allSettled 隔离，
      // 避免元数据接口失败导致整页报名记录一起消失。
      const [listResult, activitiesResult] = await Promise.allSettled([
        api.listMyRegistrations(),
        api.listActivities()
      ])

      if (listResult.status === 'rejected') {
        throw listResult.reason
      }
      const list = listResult.value || []

      const activityMap = {}
      if (activitiesResult.status === 'fulfilled') {
        ;(activitiesResult.value || []).forEach((item) => {
          activityMap[item.id] = item
        })
      }

      const records = list.map((item) => {
        const activity = activityMap[item.activity_id] || {}
        return {
          id: item.id,
          activityId: item.activity_id,
          title: activity.title || '活动已下架',
          location: activity.location || '—',
          startsAt: format.formatEventTime(activity.starts_at),
          countdown: format.formatCountdown(activity.starts_at),
          companions: item.companions,
          contact: item.contact,
          remark: item.remark,
          coverPath: item.cover_path || '',
          status: item.status,
          statusText: format.statusText(item.status),
          createdAt: format.formatRecordTime(item.created_at),
          cover: format.fallbackCover(activity.slug)
        }
      })
      this.setData({ records, loading: false })
      this.loadRecordCovers(records)
    } catch (error) {
      this.setData({
        loading: false,
        errorText: (error && error.message) || '报名记录加载失败，请稍后重试'
      })
    }
  },

  /** 报名配图存在云端存储，生成签名地址后展示。 */
  async loadRecordCovers(records) {
    const withCover = records.filter((item) => item.coverPath)
    if (!withCover.length) {
      return
    }
    try {
      const storage = require('../../utils/storage')
      const updates = {}
      for (const item of withCover) {
        // 单张配图失败时沿用活动封面，不影响其他记录。
        const url = await storage.signedUrl(item.coverPath, 3600)
        if (url) {
          updates[item.id] = url
        }
      }
      if (!Object.keys(updates).length) {
        return
      }
      this.setData({
        records: this.data.records.map((row) =>
          updates[row.id] ? Object.assign({}, row, { cover: updates[row.id] }) : row
        )
      })
    } catch (error) {
      // 配图是增强信息，失败时沿用活动封面
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
    this.loadRecords()
  },

  onTapGoHome() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  onTapRecord(event) {
    const id = Number(event.currentTarget.dataset.id)
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  onTapCancel(event) {
    const id = Number(event.currentTarget.dataset.id)
    const record = this.data.records.find((item) => item.id === id)
    if (!record) {
      return
    }
    wx.showModal({
      title: '取消报名',
      content: `确认取消「${record.title}」的报名吗？`,
      confirmText: '确认取消',
      cancelText: '再想想',
      confirmColor: '#e05a5a',
      success: async (res) => {
        if (!res.confirm) {
          return
        }
        this.setData({ cancellingId: id })
        try {
          const removed = await api.cancelRegistration(id)
          if (!removed) {
            wx.showToast({ title: '报名记录不存在或已处理', icon: 'none' })
          } else {
            wx.showToast({ title: '已取消报名', icon: 'success' })
          }
          this.loadRecords()
        } catch (error) {
          wx.showToast({ title: (error && error.message) || '取消失败，请稍后重试', icon: 'none' })
        } finally {
          this.setData({ cancellingId: 0 })
        }
      }
    })
  }
})
