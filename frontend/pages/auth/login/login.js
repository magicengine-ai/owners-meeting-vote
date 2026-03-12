// pages/auth/login/login.js
const app = getApp()
const { request, post, get, setToken, setUserInfo } = require('../../../utils/request.js')

Page({
  data: {
    currentTab: 'wechat', // wechat | phone
    phone: '',
    smsCode: '',
    smsToken: '',
    canSendCode: true,
    sendCodeText: '获取验证码',
    countdown: 0,
    canPhoneLogin: false
  },

  onLoad(options) {
    // 检查是否已有登录状态
    const token = wx.getStorageSync('access_token')
    if (token) {
      // 已登录，跳转到首页
      wx.switchTab({
        url: '/pages/index/index'
      })
    }
  },

  /**
   * 切换登录方式
   */
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({
      currentTab: tab
    })
  },

  /**
   * 手机号输入
   */
  onPhoneInput(e) {
    const phone = e.detail.value
    this.setData({
      phone: phone
    })
    this.checkCanLogin()
  },

  /**
   * 验证码输入
   */
  onCodeInput(e) {
    const smsCode = e.detail.value
    this.setData({
      smsCode: smsCode
    })
    this.checkCanLogin()
  },

  /**
   * 检查是否可以登录
   */
  checkCanLogin() {
    const { phone, smsCode } = this.data
    const canLogin = /^1[3-9]\d{9}$/.test(phone) && smsCode.length === 6
    this.setData({
      canPhoneLogin: canLogin
    })
  },

  /**
   * 发送短信验证码
   */
  async sendSmsCode() {
    const { phone, canSendCode } = this.data
    
    if (!canSendCode) return
    
    // 验证手机号格式
    if (!/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      })
      return
    }

    try {
      wx.showLoading({ title: '发送中...' })
      
      const res = await post('/api/auth/phone/sms', {
        phone: phone
      })
      
      if (res.sms_token) {
        this.setData({
          smsToken: res.sms_token,
          canSendCode: false,
          countdown: 60
        })
        
        wx.showToast({
          title: '验证码已发送',
          icon: 'success'
        })
        
        // 开始倒计时
        this.startCountdown()
        
        // 开发环境：打印验证码（实际应该看短信）
        console.log('【开发环境验证码】', res)
      }
    } catch (error) {
      console.error('发送验证码失败:', error)
      wx.showToast({
        title: error.message || '发送失败，请重试',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  /**
   * 倒计时
   */
  startCountdown() {
    const timer = setInterval(() => {
      let { countdown } = this.data
      
      if (countdown <= 0) {
        clearInterval(timer)
        this.setData({
          canSendCode: true,
          sendCodeText: '获取验证码'
        })
        return
      }
      
      countdown--
      this.setData({
        countdown: countdown,
        sendCodeText: `${countdown}秒后重试`
      })
    }, 1000)
  },

  /**
   * 微信登录
   */
  async wechatLogin() {
    try {
      wx.showLoading({ title: '登录中...' })
      
      // 1. 获取微信登录 code
      const loginRes = await wx.login({
        timeout: 10000
      })
      
      if (!loginRes.code) {
        throw new Error('微信登录失败')
      }
      
      // 2. 调用后端登录接口
      const res = await post('/api/auth/wechat/login', {
        code: loginRes.code
      })
      
      if (res.access_token) {
        // 3. 保存 token 和用户信息
        setToken(res.access_token)
        setUserInfo({
          openid: res.openid,
          nickname: res.nickname,
          avatar_url: res.avatar_url,
          phone: res.phone,
          is_verified: res.is_verified
        })
        
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        // 4. 跳转到首页
        setTimeout(() => {
          wx.switchTab({
            url: '/pages/index/index'
          })
        }, 1500)
      }
    } catch (error) {
      console.error('微信登录失败:', error)
      wx.showToast({
        title: error.message || '登录失败，请重试',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  /**
   * 手机号登录
   */
  async phoneLogin() {
    const { phone, smsCode, smsToken } = this.data
    
    if (!this.data.canPhoneLogin) {
      wx.showToast({
        title: '请填写完整的登录信息',
        icon: 'none'
      })
      return
    }
    
    try {
      wx.showLoading({ title: '登录中...' })
      
      // 调用后端登录接口
      const res = await post('/api/auth/phone/login', {
        phone: phone,
        sms_code: smsCode,
        sms_token: smsToken
      })
      
      if (res.access_token) {
        // 保存 token 和用户信息
        setToken(res.access_token)
        setUserInfo({
          openid: res.openid,
          phone: res.phone,
          is_verified: res.is_verified
        })
        
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        // 跳转到首页
        setTimeout(() => {
          wx.switchTab({
            url: '/pages/index/index'
          })
        }, 1500)
      }
    } catch (error) {
      console.error('手机号登录失败:', error)
      wx.showToast({
        title: error.message || '登录失败，请重试',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  /**
   * 显示用户协议
   */
  showAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '欢迎使用业主大会投票小程序...',
      showCancel: false,
      confirmText: '我知道了'
    })
  },

  /**
   * 显示隐私政策
   */
  showPrivacy() {
    wx.showModal({
      title: '隐私政策',
      content: '我们非常重视您的隐私保护...',
      showCancel: false,
      confirmText: '我知道了'
    })
  }
})
