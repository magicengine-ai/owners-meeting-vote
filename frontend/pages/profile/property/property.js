// pages/profile/property/property.js
const { get } = require('../../../utils/request.js')

Page({
  data: {
    propertyInfo: null,
    verifyStatus: 'none',
    verifyText: '鏈璇?,
    voteRights: 0,
    votePercent: 0
  },

  onLoad(options) {
    this.loadPropertyInfo()
  },

  onShow() {
    // 鍒锋柊璁よ瘉鐘舵€?
    this.loadVerifyStatus()
  },

  /**
   * 鍔犺浇鎴夸骇淇℃伅
   */
  async loadPropertyInfo() {
    try {
      // TODO: 瀹炵幇鑾峰彇鎴夸骇淇℃伅鎺ュ彛
      // const res = await get('/api/user/property')
      
      // 涓存椂妯℃嫙鏁版嵁
      const userInfo = wx.getStorageSync('userInfo')
      if (userInfo && userInfo.property_address) {
        const propertyInfo = {
          owner_name: userInfo.property_owner || '寮犱笁',
          cert_number: userInfo.property_cert_number || '浜?(2024) 鏈濋槼鍖轰笉鍔ㄤ骇鏉冪 1234567 鍙?,
          address: userInfo.property_address || '鍖椾含甯傛湞闃冲尯 XX 璺?XX 鍙烽櫌',
          area: userInfo.property_area || 89.5,
          verified_at: userInfo.verified_at || '2026-03-12'
        }
        
        const voteRights = Math.floor(propertyInfo.area)
        
        this.setData({
          propertyInfo,
          voteRights,
          votePercent: (voteRights / 10000 * 100).toFixed(2) // 鍋囪鎬婚潰绉?10000 绁?
        })
      }
    } catch (error) {
      console.error('鍔犺浇鎴夸骇淇℃伅澶辫触:', error)
    }
  },

  /**
   * 鍔犺浇璁よ瘉鐘舵€?
   */
  async loadVerifyStatus() {
    try {
      const res = await get('/api/auth/verify/status')
      
      let verifyText = '鏈璇?
      if (res.status === 'approved') {
        verifyText = '宸茶璇?
      } else if (res.status === 'pending') {
        verifyText = '瀹℃牳涓?
      } else if (res.status === 'rejected') {
        verifyText = '璁よ瘉澶辫触'
      }
      
      this.setData({
        verifyStatus: res.status,
        verifyText
      })
    } catch (error) {
      console.error('鑾峰彇璁よ瘉鐘舵€佸け璐?', error)
    }
  },

  /**
   * 璺宠浆鍒拌璇侀〉闈?
   */
  goToVerify() {
    wx.navigateTo({
      url: '/pages/auth/verify/verify'
    })
  },

  /**
   * 閲嶆柊璁よ瘉
   */
  reVerify() {
    wx.showModal({
      title: '閲嶆柊璁よ瘉',
      content: '纭畾瑕侀噸鏂版彁浜ゆ埧浜ц瘉璁よ瘉鍚楋紵',
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
