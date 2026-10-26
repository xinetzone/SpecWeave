const app = getApp()
const api = require('../../utils/api')
const format = require('../../utils/format')
const privacy = require('../../utils/privacy')

const CONTACT_RE = /^1\d{10}$/
const MAX_COMPANIONS = 4
const MAX_UPLOAD_BYTES = 5 * 1024 * 1024
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png']

Page({
  data: {
    loading: true,
    errorText: '',
    activityId: 0,
    detail: null,
    signedIn: false,
    signingIn: false,
    submitting: false,
    companions: 1,
    maxCompanions: MAX_COMPANIONS,
    fits: true,
    contact: '',
    contactError: '',
    remark: '',
    remarkLen: 0,
    uploadedCover: '',
    uploadedCoverUrl: '',
    uploadingCover: false,
    coverPicked: false,
    coverTempPath: '',
    coverContentType: '',
    coverUploadMessage: ''
  },

  onLoad(options) {
    const id = Number(options.id)
    if (!id) {
      this.setData({ loading: false, errorText: '活动参数无效' })
      return
    }
    this.setData({ activityId: id })
    this.loadActivity()
  },

  async onShow() {
    const signedIn = await app.ensureSession()
    this.setData({ signedIn })
  },

  async loadActivity() {
    this.setData({ loading: true, errorText: '' })
    try {
      const activity = await api.getActivity(this.data.activityId)
      if (!activity) {
        this.setData({ loading: false, errorText: '活动不存在或已下架' })
        return
      }
      // 人数加载失败不应让整个报名表单消失；
      // 但也不能当成 0 人（那会让用户以为名额充足）。
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
        detail: {
          id: activity.id,
          slug: activity.slug,
          title: activity.title,
          startsAt: format.formatEventTime(activity.starts_at),
          location: activity.location,
          capacity: activity.capacity,
          signedUp,
          quotaKnown,
          quotaText: quotaKnown
            ? format.quotaText(activity.capacity, signedUp)
            : '人数待刷新',
          full: quotaKnown ? format.isFull(activity.capacity, signedUp) : false,
          cover: format.fallbackCover(activity.slug)
        }
      })
      this.refreshQuota()
    } catch (error) {
      this.setData({
        loading: false,
        errorText: (error && error.message) || '活动信息加载失败，请稍后重试'
      })
    }
  },

  /** 刷新名额口径（人数），并据此更新可提交状态。 */
  async refreshQuota() {
    const detail = this.data.detail
    if (!detail) {
      return
    }
    try {
      const stats = await api.getRegistrationStats()
      const signedUp = stats[detail.id] || 0
      this.setData({
        'detail.signedUp': signedUp,
        'detail.quotaKnown': true,
        'detail.quotaText': format.quotaText(detail.capacity, signedUp),
        'detail.full': format.isFull(detail.capacity, signedUp),
        fits: format.canFit(detail.capacity, signedUp, this.data.companions)
      })
    } catch (error) {
      // 名额刷新失败不阻断浏览：保留上一次的已知值，不清零成「0 人」。
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

  onTapMinus() {
    if (this.data.companions <= 1) {
      return
    }
    this.setData({ companions: this.data.companions - 1 })
    this.refreshQuota()
  },

  onTapPlus() {
    if (this.data.companions >= this.data.maxCompanions) {
      wx.showToast({ title: '单次最多报名 4 人', icon: 'none' })
      return
    }
    this.setData({ companions: this.data.companions + 1 })
    this.refreshQuota()
  },

  onInputContact(event) {
    this.setData({ contact: event.detail.value, contactError: '' })
  },

  onInputRemark(event) {
    const value = event.detail.value.slice(0, 100)
    this.setData({ remark: value, remarkLen: value.length })
  },

  /**
   * 确保用户已同意《小程序用户隐私保护指引》。
   *
   * 隐私接口（如 wx.chooseMedia）在用户未同意时调用会静默失败——
   * 不抛错、不回调，用户只看到「点了没反应」。这里在调用前显式兜底，
   * 把失败转成可读的提示。
   *
   * @returns {Promise<boolean>} 是否已获授权（false 表示用户拒绝，调用方应中止操作）
   */
  async ensurePrivacyAuthorized() {
    return new Promise((resolve) => {
      privacy.requirePrivacyAuthorize(
        () => resolve(true),
        () => {
          wx.showToast({ title: '需同意隐私保护指引才能选择图片', icon: 'none' })
          resolve(false)
        }
      )
    })
  },

  /**
   * 选择报名配图。
   * 此处只做本地预览（临时文件路径），不做上传：
   * 上传推迟到提交成功之后，按报名记录 id 命名，避免放弃表单时留下孤儿文件。
   *
   * 隐私约束：wx.chooseMedia 属于「收集你选中的照片或视频信息」隐私接口，
   * 自 2023-09-15 起受平台管控——未在《用户隐私保护指引》声明时接口被直接禁用，
   * 已声明但用户未同意时调用会静默失败。调用前必须先过授权兜底。
   */
  async onTapUploadCover() {
    if (this.data.uploadingCover) {
      return
    }
    if (!this.data.signedIn) {
      wx.showToast({ title: '请先完成微信授权登录', icon: 'none' })
      return
    }
    const granted = await this.ensurePrivacyAuthorized()
    if (!granted) {
      return
    }
    try {
      const picked = await new Promise((resolve) => {
        wx.chooseMedia({
          count: 1,
          mediaType: ['image'],
          sizeType: ['compressed'],
          sourceType: ['album', 'camera'],
          success: (res) => resolve(res.tempFiles || []),
          fail: (res) => resolve({ failed: true, errMsg: (res && res.errMsg) || '' })
        })
      })
      if (!picked || picked.failed) {
        const msg = String((picked && picked.errMsg) || '')
        if (msg.indexOf('auth deny') >= 0 || msg.indexOf('authorize') >= 0) {
          wx.showToast({ title: '需要相册权限才能选择图片', icon: 'none' })
        }
        return
      }
      const file = picked[0]
      if (!file) {
        return
      }
      if (typeof file.size === 'number' && file.size > MAX_UPLOAD_BYTES) {
        wx.showToast({ title: '图片不能超过 5MB', icon: 'none' })
        return
      }
      const contentType = guessContentType(file)
      if (!ALLOWED_IMAGE_TYPES.indexOf(contentType)) {
        wx.showToast({ title: '仅支持 JPG 或 PNG 图片', icon: 'none' })
        return
      }
      this.setData({
        coverPicked: true,
        coverTempPath: file.tempFilePath,
        coverContentType: contentType,
        uploadedCover: '',
        uploadedCoverUrl: file.tempFilePath
      })
    } catch (error) {
      wx.showToast({ title: (error && error.message) || '选择图片失败', icon: 'none' })
    }
  },

  /**
   * 上传报名配图并绑定到报名记录。
   * 路径形如 users/<uid>/registrations/<registrationId>.<ext>，与服务端校验规则一致。
   * @param {number} registrationId
   * @returns {Promise<boolean>} 是否绑定成功（失败不影响报名本身）
   */
  async uploadAndAttachCover(registrationId) {
    const tempPath = this.data.coverTempPath
    if (!tempPath || !registrationId) {
      return false
    }
    try {
      const storage = require('../../utils/storage')
      const { cloud } = require('../../utils/cloud')
      const uid = await currentUid()
      if (!uid) {
        return false
      }
      const fs = wx.getFileSystemManager()
      const buffer = fs.readFileSync(tempPath)
      const contentType = this.data.coverContentType || 'image/jpeg'
      const ext = contentType === 'image/png' ? 'png' : 'jpg'
      // 路径落在本人私有目录（服务端强校验：users/<调用者uid>/registrations/<id>.<ext>）
      const path = cloud.storage.userPath(uid, `registrations/${registrationId}.${ext}`)
      const uploaded = await storage.uploadBinary(path, buffer, { contentType })
      if (!uploaded.ok) {
        this.setData({ coverUploadMessage: uploaded.message || '配图上传失败' })
        return false
      }
      const attached = await api.attachCover(registrationId, path)
      if (attached) {
        this.setData({ uploadedCover: path, coverUploadMessage: '' })
      } else {
        this.setData({ coverUploadMessage: '配图绑定失败' })
      }
      return attached
    } catch (error) {
      this.setData({ coverUploadMessage: '配图上传失败，请稍后重试' })
      return false
    }
  },

  async onSubmit() {
    if (this.data.submitting) {
      return
    }
    if (!this.data.signedIn) {
      wx.showToast({ title: '请先完成微信授权登录', icon: 'none' })
      return
    }
    const detail = this.data.detail
    if (!detail) {
      return
    }
    if (detail.full) {
      wx.showToast({ title: '该活动名额已满', icon: 'none' })
      return
    }
    // 提交前按人数口径预校验：本次报名人数装不下时直接拦截，
    // 避免用户填完表单才被服务端拒绝。
    if (!format.canFit(detail.capacity, detail.signedUp, this.data.companions)) {
      wx.showToast({ title: `剩余名额不足 ${this.data.companions} 人`, icon: 'none' })
      return
    }
    const contact = (this.data.contact || '').trim()
    if (!CONTACT_RE.test(contact)) {
      this.setData({ contactError: '请输入正确的 11 位手机号' })
      return
    }
    this.setData({ submitting: true, contactError: '' })
    try {
      const row = await api.signup(detail.id, {
        companions: this.data.companions,
        contact,
        remark: (this.data.remark || '').trim(),
        ownerName: (app.globalData.user && app.globalData.user.name) || null,
        coverPath: null
      })
      // 报名成功后再上传配图并绑定：路径按报名记录 id 命名，
      // 失败只影响配图，不影响报名结果，也不会留下孤儿文件。
      let coverFailed = false
      if (row && row.id && this.data.coverPicked) {
        this.setData({ uploadingCover: true })
        coverFailed = !(await this.uploadAndAttachCover(row.id))
        this.setData({ uploadingCover: false })
      }
      // 报名已成功，但配图没传上去时要明确告知，不能静默跳过后只报「报名成功」。
      if (coverFailed) {
        wx.showToast({
          title: this.data.coverUploadMessage || '报名成功，配图未上传',
          icon: 'none',
          duration: 2500
        })
      } else {
        wx.showToast({ title: '报名成功', icon: 'success' })
      }
      setTimeout(() => {
        wx.switchTab({ url: '/pages/records/records' })
      }, coverFailed ? 2500 : 900)
    } catch (error) {
      wx.showToast({ title: (error && error.message) || '报名失败，请稍后重试', icon: 'none' })
      this.setData({ submitting: false })
      // 名额已满时同步刷新页面上的名额状态
      this.loadActivity()
    }
  }
})

/** 取当前登录用户的 uid（优先用实时会话，避免缓存中的旧 uid）。 */
async function currentUid() {
  try {
    const { cloud } = require('../../utils/cloud')
    const { data } = await cloud.auth.getSession()
    if (data && data.user && data.user.id) {
      return data.user.id
    }
  } catch (error) {
    // 落到下面的兜底
  }
  const user = app.globalData.user
  return (user && user.id) || ''
}

/** 从临时文件路径推断内容类型。 */
function guessContentType(file) {
  if (file.fileType) {
    return String(file.fileType).toLowerCase()
  }
  const path = String(file.tempFilePath || '').toLowerCase()
  if (path.indexOf('.png') >= 0) {
    return 'image/png'
  }
  return 'image/jpeg'
}
