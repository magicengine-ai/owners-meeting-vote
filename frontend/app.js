// app.js
App({
  onLaunch: function () {
    console.log('涓氫富澶т細鎶曠エ灏忕▼搴忓惎鍔?);
    
    // 妫€鏌ョ櫥褰曠姸鎬?    this.checkLoginStatus();
  },

  globalData: {
    userInfo: null,
    openid: null,
    isVerified: false,
    baseUrl: 'https://owners-vote-234350-9-1411900181.sh.run.tcloudbase.com' // 鐢熶骇鐜閰嶇疆
  },

  // 妫€鏌ョ櫥褰曠姸鎬?  checkLoginStatus: function() {
    const token = wx.getStorageSync('token');
    if (token) {
      // TODO: 楠岃瘉 token 鏈夋晥鎬?      console.log('宸茬櫥褰?);
    } else {
      console.log('鏈櫥褰?);
    }
  },

  // 鑾峰彇鐢ㄦ埛淇℃伅
  getUserInfo: function() {
    return this.globalData.userInfo;
  },

  // 璁剧疆鐢ㄦ埛淇℃伅
  setUserInfo: function(userInfo) {
    this.globalData.userInfo = userInfo;
    wx.setStorageSync('userInfo', userInfo);
  }
})
