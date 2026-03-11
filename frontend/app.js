// app.js
App({
  onLaunch: function () {
    console.log('业主大会投票小程序启动');
    
    // 检查登录状态
    this.checkLoginStatus();
  },

  globalData: {
    userInfo: null,
    openid: null,
    isVerified: false,
    baseUrl: 'https://api.example.com' // 生产环境配置
  },

  // 检查登录状态
  checkLoginStatus: function() {
    const token = wx.getStorageSync('token');
    if (token) {
      // TODO: 验证 token 有效性
      console.log('已登录');
    } else {
      console.log('未登录');
    }
  },

  // 获取用户信息
  getUserInfo: function() {
    return this.globalData.userInfo;
  },

  // 设置用户信息
  setUserInfo: function(userInfo) {
    this.globalData.userInfo = userInfo;
    wx.setStorageSync('userInfo', userInfo);
  }
})
