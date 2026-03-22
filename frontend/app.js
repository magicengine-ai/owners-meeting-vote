// app.js
App({
  onLaunch: function () {
    console.log('业主大会投票小程序已启动');
    this.checkLoginStatus();
  },

  globalData: {
    userInfo: null,
    openid: null,
    isVerified: false,
    baseUrl: 'https://owners-vote-234350-9-1411900181.sh.run.tcloudbase.com'
  },

  checkLoginStatus: function() {
    const token = wx.getStorageSync('token');
    if (token) {
      console.log('已登录');
    } else {
      console.log('未登录');
    }
  },

  getUserInfo: function() {
    return this.globalData.userInfo;
  },

  setUserInfo: function(userInfo) {
    this.globalData.userInfo = userInfo;
    wx.setStorageSync('userInfo', userInfo);
  }
})
