Page({
  onTapUploadCover() {
    this.requirePrivacy(() => {
      wx.chooseMedia({
        count: 1,
        mediaType: ['image'],
        success: (res) => { console.log(res.tempFiles) }
      })
    })
  },
  requirePrivacy(onGranted) {
    if (typeof wx.requirePrivacyAuthorize !== 'function') {
      onGranted()
      return
    }
    wx.requirePrivacyAuthorize({ success: onGranted, fail: () => {} })
  }
})
