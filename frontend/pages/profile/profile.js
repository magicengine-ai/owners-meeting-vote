// pages/profile/profile.js
const app = getApp()
const { get, post, getToken, setToken, setUserInfo, clearToken } = require('../../../utils/request.js')

Page({
  data: {
    userInfo: null,
    verifyStatus: 'none', // none, pending, approved, rejected
    verifyText: '未认证',
    propertyInfo: null,
    voteCount: 0,
    meetingCount: 0,
    noticeCount: 0
  },

  onLoad(options) {
    // 检查登录状态
    const token = getToken()
    if (!token) {
      wx.redirectTo({
        url: '/pages/auth/login/login'
      })
      return
    }

    // 加载用户信息
    this.loadUserInfo()
  },

  onShow() {
    // 每次显示时刷新认证状态
    this.loadVerifyStatus()
  },

  /**
   * 加载用户信息
   */
  async loadUserInfo() {
    try {
      const res = await get('/api/auth/me')
      
      const userInfo = {
        openid: res.openid,
        nickname: res.nickname,
        avatar_url: res.avatar_url,
        phone: res.phone,
        is_verified: res.is_verified
      }
      
      this.setData({
        userInfo,
        verifyStatus: res.is_verified ? 'approved' : this.data.verifyStatus
      })
      
      setUserInfo(userInfo)
      
      // 加载房产信息
      if (res.is_verified) {
        this.loadPropertyInfo()
      }
      
    } catch (error) {
      console.error('获取用户信息失败:', error)
      
      // Token 失效，跳转登录
      if (error.error === 'unauthorized') {
        this.logout()
      }
    }
  },

  /**
   * 加载认证状态
   */
  async loadVerifyStatus() {
    try {
      const res = await get('/api/auth/verify/status')
      
      let verifyText = '未认证'
      if (res.status === 'approved') {
        verifyText = '已认证'
      } else if (res.status === 'pending') {
        verifyText = '审核中'
      } else if (res.status === 'rejected') {
        verifyText = '认证失败'
      }
      
      this.setData({
        verifyStatus: res.status,
        verifyText
      })
      
      // 如果已认证，加载房产信息
      if (res.status === 'approved') {
        this.loadPropertyInfo()
      }
      
    } catch (error) {
      console.error('获取认证状态失败:', error)
    }
  },

  /**
   * 加载房产信息
   */
  async loadPropertyInfo() {
    try {
      // TODO: 实现房产信息接口
      // const res = await get('/api/user/property')
      // this.setData({ propertyInfo: res })
      
      // 临时使用用户信息中的房产数据
      if (this.data.userInfo && this.data.userInfo.property_address) {
        this.setData({
          propertyInfo: {
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

  /**
   * 页面跳转
   */
  navigateTo(e) {
    const url = e.currentTarget.dataset.url
    if (url) {
      wx.navigateTo({
        url: url
      })
    }
  },

  /**
   * 跳转到认证页面
   */
  goToVerify() {
    wx.navigateTo({
      url: '/pages/auth/verify/verify'
    })
  },

  /**
   * 显示关于
   */
  showAbout() {
    wx.showModal({
      title: '关于业主大会投票',
      content: '版本号：v1.0.0\n\n业主大会投票系统是为小区业主提供的在线投票平台，支持房产证认证、在线投票、会议管理等功能。\n\n© 2026 业主大会投票系统',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  /**
   * 显示帮助与反馈
   */
  showFeedback() {
    wx.showModal({
      title: '帮助与反馈',
      content: '如有问题或建议，请联系：\n\n📞 客服电话：400-XXX-XXXX\n📧 邮箱：support@example.com\n\n工作时间：周一至周五 9:00-18:00',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  /**
   * 退出登录
   */
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除本地缓存
          clearToken()
          
          // 跳转到登录页
          wx.reLaunch({
            url: '/pages/auth/login/login'
          })
          
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          })
        }
      }
    })
  }
})
