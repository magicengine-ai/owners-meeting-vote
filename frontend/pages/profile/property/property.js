// pages/profile/property/property.js
const { get } = require('../../../../utils/request.js')

Page({
  data: {
    propertyInfo: null,
    verifyStatus: 'none',
    verifyText: '未认证',
    voteRights: 0,
    votePercent: 0
  },

  onLoad(options) {
    this.loadPropertyInfo()
  },

  onShow() {
    // 刷新认证状态
    this.loadVerifyStatus()
  },

  /**
   * 加载房产信息
   */
  async loadPropertyInfo() {
    try {
      // TODO: 实现获取房产信息接口
      // const res = await get('/api/user/property')
      
      // 临时模拟数据
      const userInfo = wx.getStorageSync('userInfo')
      if (userInfo && userInfo.property_address) {
        const propertyInfo = {
          owner_name: userInfo.property_owner || '张三',
          cert_number: userInfo.property_cert_number || '京 (2024) 朝阳区不动产权第 1234567 号',
          address: userInfo.property_address || '北京市朝阳区 XX 路 XX 号院',
          area: userInfo.property_area || 89.5,
          verified_at: userInfo.verified_at || '2026-03-12'
        }
        
        const voteRights = Math.floor(propertyInfo.area)
        
        this.setData({
          propertyInfo,
          voteRights,
          votePercent: (voteRights / 10000 * 100).toFixed(2) // 假设总面积 10000 票
        })
      }
    } catch (error) {
      console.error('加载房产信息失败:', error)
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
    } catch (error) {
      console.error('获取认证状态失败:', error)
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
   * 重新认证
   */
  reVerify() {
    wx.showModal({
      title: '重新认证',
      content: '确定要重新提交房产证认证吗？',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: '/pages/auth/verify/verify'
          })
        }
      }
    })
  }
})
