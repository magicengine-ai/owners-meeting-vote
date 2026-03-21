/**
 * 缃戠粶璇锋眰灏佽
 */

// 閰嶇疆
const config = {
  baseUrl: 'https://owners-vote-234350-9-1411900181.sh.run.tcloudbase.com', // 鐢熶骇鐜
  // baseUrl: 'http://localhost:8000', // 寮€鍙戠幆澧?  timeout: 10000,
}

// Token 瀛樺偍
const TOKEN_KEY = 'access_token'
const USER_INFO_KEY = 'userInfo'

/**
 * 鑾峰彇瀛樺偍鐨?Token
 */
function getToken() {
  return wx.getStorageSync(TOKEN_KEY) || ''
}

/**
 * 淇濆瓨 Token
 */
function setToken(token) {
  wx.setStorageSync(TOKEN_KEY, token)
}

/**
 * 娓呴櫎 Token
 */
function clearToken() {
  wx.removeStorageSync(TOKEN_KEY)
  wx.removeStorageSync(USER_INFO_KEY)
}

/**
 * 鑾峰彇鐢ㄦ埛淇℃伅
 */
function getUserInfo() {
  return wx.getStorageSync(USER_INFO_KEY) || null
}

/**
 * 淇濆瓨鐢ㄦ埛淇℃伅
 */
function setUserInfo(userInfo) {
  wx.setStorageSync(USER_INFO_KEY, userInfo)
}

/**
 * 灏佽 request 璇锋眰
 * @param {Object} options 璇锋眰閰嶇疆
 * @returns {Promise} 璇锋眰缁撴灉
 */
function request(options) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    
    wx.request({
      url: config.baseUrl + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      timeout: config.timeout,
      success: (res) => {
        // HTTP 鐘舵€佺爜澶勭悊
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // Token 澶辨晥锛屾竻闄ゅ苟璺宠浆鐧诲綍
          clearToken()
          wx.showToast({
            title: '鐧诲綍宸茶繃鏈?,
            icon: 'none'
          })
          setTimeout(() => {
            wx.navigateTo({
              url: '/pages/auth/login/login'
            })
          }, 1500)
          reject({ error: 'unauthorized', message: '鐧诲綍宸茶繃鏈? })
        } else if (res.statusCode === 403) {
          // 鏉冮檺涓嶈冻
          wx.showToast({
            title: res.data.detail || '鏉冮檺涓嶈冻',
            icon: 'none'
          })
          reject(res.data)
        } else if (res.statusCode === 422) {
          // 鍙傛暟楠岃瘉澶辫触
          wx.showToast({
            title: '鍙傛暟閿欒',
            icon: 'none'
          })
          reject(res.data)
        } else {
          // 鍏朵粬閿欒
          const errorMsg = res.data.message || '璇锋眰澶辫触'
          wx.showToast({
            title: errorMsg,
            icon: 'none'
          })
          reject(res.data)
        }
      },
      fail: (err) => {
        // 缃戠粶閿欒
        console.error('璇锋眰澶辫触:', err)
        wx.showToast({
          title: '缃戠粶閿欒锛岃绋嶅悗閲嶈瘯',
          icon: 'none'
        })
        reject({ error: 'network_error', message: '缃戠粶閿欒' })
      }
    })
  })
}

/**
 * GET 璇锋眰
 * @param {String} url 璇锋眰鍦板潃
 * @param {Object} data 璇锋眰鍙傛暟
 * @param {Object} header 璇锋眰澶? */
function get(url, data = {}, header = {}) {
  return request({ url, method: 'GET', data, header })
}

/**
 * POST 璇锋眰
 * @param {String} url 璇锋眰鍦板潃
 * @param {Object} data 璇锋眰鏁版嵁
 * @param {Object} header 璇锋眰澶? */
function post(url, data = {}, header = {}) {
  return request({ url, method: 'POST', data, header })
}

/**
 * PUT 璇锋眰
 * @param {String} url 璇锋眰鍦板潃
 * @param {Object} data 璇锋眰鏁版嵁
 * @param {Object} header 璇锋眰澶? */
function put(url, data = {}, header = {}) {
  return request({ url, method: 'PUT', data, header })
}

/**
 * DELETE 璇锋眰
 * @param {String} url 璇锋眰鍦板潃
 * @param {Object} data 璇锋眰鍙傛暟
 * @param {Object} header 璇锋眰澶? */
function del(url, data = {}, header = {}) {
  return request({ url, method: 'DELETE', data, header })
}

/**
 * 涓婁紶鏂囦欢
 * @param {String} url 涓婁紶鍦板潃
 * @param {String} filePath 鏂囦欢璺緞
 * @param {Object} formData 琛ㄥ崟鏁版嵁
 */
function uploadFile(url, filePath, formData = {}) {
  const token = getToken()
  
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: config.baseUrl + url,
      filePath: filePath,
      name: 'file',
      formData: formData,
      header: {
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data)
          } else {
            wx.showToast({
              title: data.message || '涓婁紶澶辫触',
              icon: 'none'
            })
            reject(data)
          }
        } catch (e) {
          reject({ error: 'parse_error', message: '鍝嶅簲瑙ｆ瀽澶辫触' })
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '涓婁紶澶辫触',
          icon: 'none'
        })
        reject({ error: 'upload_error', message: '涓婁紶澶辫触' })
      }
    })
  })
}

// 瀵煎嚭
module.exports = {
  config,
  getToken,
  setToken,
  clearToken,
  getUserInfo,
  setUserInfo,
  request,
  get,
  post,
  put,
  del,
  uploadFile
}
