// pages/profile/profile.js
const app = getApp()
const { get, post, getToken, setToken, setUserInfo, clearToken } = require('../../utils/request.js')

Page({
  data: {
    userInfo: null,
    verifyStatus: 'none',
    verifyText: '未认证',
    propertyInfo: null,
    voteCount: 0,
    meetingCount: 0,
    noticeCount: 0
  },

  onLoad(options) {
    const token = getToken()
    if (!token) {
      wx.redirectTo({ url: '/pages/auth/login/login' })
      return
    }
    this.loadUserInfo()
  },

  onShow() {
    this.loadVerifyStatus()
  },

  async loadUserInfo() {
    try {
      const res = await get('/api/auth/me')
      const userInfo = {
        openidSubstring: res.openid ? res.openid.substring(0, 8) : '',
        openid: res.openid,
        nickname: res.nickname,
        avatar_url: res.avatar_url,
        phone: res.phone,
        is_verified: res.is_verified
      }
      this.setData({ userInfo, verifyStatus: res.is_verified ? 'approved' : this.data.verifyStatus })
      setUserInfo(userInfo)
      if (res.is_verified) {
        this.loadPropertyInfo()
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      if (error.error === 'unauthorized') {
        this.logout()
      }
    }
  },

  async loadVerifyStatus() {
    try {
      const res = await get('/api/auth/verify/status')
      let verifyText = '未认证'
      if (res.status === 'approved') verifyText = '已认证'
      else if (res.status === 'pending') verifyText = '审核中'
      else if (res.status === 'rejected') verifyText = '认证失败'
      this.setData({ verifyStatus: res.status, verifyText })
      if (res.status === 'approved') {
        this.loadPropertyInfo()
      }
    } catch (error) {
      console.error('获取认证状态失败:', error)
    }
  },

  async loadPropertyInfo() {
    try {
      if (this.data.userInfo && this.data.userInfo.property_address) {
        this.setData({
          propertyInfo: {
            addressSubstring: this.data.userInfo.property_address ? this.data.userInfo.property_address.substring(0, 10) + '...' : '',
            address: this.data.userInfo.property_address,
            area: this.data.userInfo.property_area,
            cert_number: this.data.userInfo.property_cert_number
          }
        })
      }
    } catch (error) {
      console.error('加载房产信息失败:', error)
    }
  },

  navigateTo(e) {
    const url = e.currentTarget.dataset.url
    if (url) {
      wx.navigateTo({ url })
    }
  },

  goToVerify() {
    wx.navigateTo({ url: '/pages/auth/verify/verify' })
  },

  showAbout() {
    wx.showModal({
      title: '关于业主大会投票',
      content: '版本号：v1.0.0\n\n业主大会投票系统是为小区业主提供的在线投票平台。\n\n© 2026 业主大会投票系统',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  showFeedback() {
    wx.showModal({
      title: '帮助与反馈',
      content: '如有问题或建议，请联系：\n\n客服电话：400-XXX-XXXX\n邮箱：support@example.com\n\n工作时间：周一至周五 9:00-18:00',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          clearToken()
          wx.reLaunch({ url: '/pages/auth/login/login' })
          wx.showToast({ title: '已退出登录', icon: 'success' })
        }
      }
    })
  }
})
