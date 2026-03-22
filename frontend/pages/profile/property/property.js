// pages/profile/property/property.js
const { get, post } = require('../../../utils/request.js')

Page({
  data: {
    propertyInfo: null,
    verifyStatus: 'none'
  },

  onLoad() {
    this.loadPropertyInfo()
  },

  async loadPropertyInfo() {
    try {
      const res = await get('/api/user/property')
      this.setData({
        propertyInfo: res,
        verifyStatus: res.verify_status
      })
    } catch (error) {
      console.error('加载房产信息失败:', error)
      wx.showToast({ title: error.message || '加载失败', icon: 'none' })
    }
  },

  submitVerify() {
    wx.navigateTo({
      url: '/pages/auth/verify/verify'
    })
  }
})
