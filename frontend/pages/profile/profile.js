// pages/profile/profile.js
const app = getApp()
const { get, post, getToken, setToken, setUserInfo, clearToken } = require('../../../utils/request.js')

Page({
  data: {
    userInfo: null,
    verifyStatus: 'none', // none, pending, approved, rejected
    verifyText: '鏈璇?,
    propertyInfo: null,
    voteCount: 0,
    meetingCount: 0,
    noticeCount: 0
  },

  onLoad(options) {
    // 妫€鏌ョ櫥褰曠姸鎬?    const token = getToken()
    if (!token) {
      wx.redirectTo({
        url: '/pages/auth/login/login'
      })
      return
    }

    // 鍔犺浇鐢ㄦ埛淇℃伅
    this.loadUserInfo()
  },

  onShow() {
    // 姣忔鏄剧ず鏃跺埛鏂拌璇佺姸鎬?    this.loadVerifyStatus()
  },

  /**
   * 鍔犺浇鐢ㄦ埛淇℃伅
   */
  async loadUserInfo() {
    try {
      const res = await get('/api/auth/me')
      
      const userInfo = {\n        openidSubstring: res.openid ? res.openid.substring(0, 8) : '
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
      
      // 鍔犺浇鎴夸骇淇℃伅
      if (res.is_verified) {
        this.loadPropertyInfo()
      }
      
    } catch (error) {
      console.error('鑾峰彇鐢ㄦ埛淇℃伅澶辫触:', error)
      
      // Token 澶辨晥锛岃烦杞櫥褰?      if (error.error === 'unauthorized') {
        this.logout()
      }
    }
  },

  /**
   * 鍔犺浇璁よ瘉鐘舵€?   */
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
      
      // 濡傛灉宸茶璇侊紝鍔犺浇鎴夸骇淇℃伅
      if (res.status === 'approved') {
        this.loadPropertyInfo()
      }
      
    } catch (error) {
      console.error('鑾峰彇璁よ瘉鐘舵€佸け璐?', error)
    }
  },

  /**
   * 鍔犺浇鎴夸骇淇℃伅
   */
  async loadPropertyInfo() {
    try {
      // TODO: 瀹炵幇鎴夸骇淇℃伅鎺ュ彛
      // const res = await get('/api/user/property')
      // this.setData({ propertyInfo: res })
      
      // 涓存椂浣跨敤鐢ㄦ埛淇℃伅涓殑鎴夸骇鏁版嵁
      if (this.data.userInfo && this.data.userInfo.property_address) {
        this.setData({
          propertyInfo: {\n            addressSubstring: this.data.userInfo.property_address ? this.data.userInfo.property_address.substring(0, 10) + '...' : ''
            address: this.data.userInfo.property_address,
            area: this.data.userInfo.property_area,
            cert_number: this.data.userInfo.property_cert_number
          }
        })
      }
    } catch (error) {
      console.error('鍔犺浇鎴夸骇淇℃伅澶辫触:', error)
    }
  },

  /**
   * 椤甸潰璺宠浆
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
   * 璺宠浆鍒拌璇侀〉闈?   */
  goToVerify() {
    wx.navigateTo({
      url: '/pages/auth/verify/verify'
    })
  },

  /**
   * 鏄剧ず鍏充簬
   */
  showAbout() {
    wx.showModal({
      title: '鍏充簬涓氫富澶т細鎶曠エ',
      content: '鐗堟湰鍙凤細v1.0.0\n\n涓氫富澶т細鎶曠エ绯荤粺鏄负灏忓尯涓氫富鎻愪緵鐨勫湪绾挎姇绁ㄥ钩鍙帮紝鏀寔鎴夸骇璇佽璇併€佸湪绾挎姇绁ㄣ€佷細璁鐞嗙瓑鍔熻兘銆俓n\n漏 2026 涓氫富澶т細鎶曠エ绯荤粺',
      showCancel: false,
      confirmText: '鎴戠煡閬撲簡'
    })
  },

  /**
   * 鏄剧ず甯姪涓庡弽棣?   */
  showFeedback() {
    wx.showModal({
      title: '甯姪涓庡弽棣?,
      content: '濡傛湁闂鎴栧缓璁紝璇疯仈绯伙細\n\n馃摓 瀹㈡湇鐢佃瘽锛?00-XXX-XXXX\n馃摟 閭锛歴upport@example.com\n\n宸ヤ綔鏃堕棿锛氬懆涓€鑷冲懆浜?9:00-18:00',
      showCancel: false,
      confirmText: '鎴戠煡閬撲簡'
    })
  },

  /**
   * 閫€鍑虹櫥褰?   */
  logout() {
    wx.showModal({
      title: '閫€鍑虹櫥褰?,
      content: '纭畾瑕侀€€鍑虹櫥褰曞悧锛?,
      success: (res) => {
        if (res.confirm) {
          // 娓呴櫎鏈湴缂撳瓨
          clearToken()
          
          // 璺宠浆鍒扮櫥褰曢〉
          wx.reLaunch({
            url: '/pages/auth/login/login'
          })
          
          wx.showToast({
            title: '宸查€€鍑虹櫥褰?,
            icon: 'success'
          })
        }
      }
    })
  }
})
