/**
 * 网络请求封装
 */

// 配置
const config = {
  baseUrl: 'https://api.example.com', // 生产环境
  // baseUrl: 'http://localhost:8000', // 开发环境
  timeout: 10000,
}

// Token 存储
const TOKEN_KEY = 'access_token'
const USER_INFO_KEY = 'userInfo'

/**
 * 获取存储的 Token
 */
function getToken() {
  return wx.getStorageSync(TOKEN_KEY) || ''
}

/**
 * 保存 Token
 */
function setToken(token) {
  wx.setStorageSync(TOKEN_KEY, token)
}

/**
 * 清除 Token
 */
function clearToken() {
  wx.removeStorageSync(TOKEN_KEY)
  wx.removeStorageSync(USER_INFO_KEY)
}

/**
 * 获取用户信息
 */
function getUserInfo() {
  return wx.getStorageSync(USER_INFO_KEY) || null
}

/**
 * 保存用户信息
 */
function setUserInfo(userInfo) {
  wx.setStorageSync(USER_INFO_KEY, userInfo)
}

/**
 * 封装 request 请求
 * @param {Object} options 请求配置
 * @returns {Promise} 请求结果
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
        // HTTP 状态码处理
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // Token 失效，清除并跳转登录
          clearToken()
          wx.showToast({
            title: '登录已过期',
            icon: 'none'
          })
          setTimeout(() => {
            wx.navigateTo({
              url: '/pages/auth/login/login'
            })
          }, 1500)
          reject({ error: 'unauthorized', message: '登录已过期' })
        } else if (res.statusCode === 403) {
          // 权限不足
          wx.showToast({
            title: res.data.detail || '权限不足',
            icon: 'none'
          })
          reject(res.data)
        } else if (res.statusCode === 422) {
          // 参数验证失败
          wx.showToast({
            title: '参数错误',
            icon: 'none'
          })
          reject(res.data)
        } else {
          // 其他错误
          const errorMsg = res.data.message || '请求失败'
          wx.showToast({
            title: errorMsg,
            icon: 'none'
          })
          reject(res.data)
        }
      },
      fail: (err) => {
        // 网络错误
        console.error('请求失败:', err)
        wx.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none'
        })
        reject({ error: 'network_error', message: '网络错误' })
      }
    })
  })
}

/**
 * GET 请求
 * @param {String} url 请求地址
 * @param {Object} data 请求参数
 * @param {Object} header 请求头
 */
function get(url, data = {}, header = {}) {
  return request({ url, method: 'GET', data, header })
}

/**
 * POST 请求
 * @param {String} url 请求地址
 * @param {Object} data 请求数据
 * @param {Object} header 请求头
 */
function post(url, data = {}, header = {}) {
  return request({ url, method: 'POST', data, header })
}

/**
 * PUT 请求
 * @param {String} url 请求地址
 * @param {Object} data 请求数据
 * @param {Object} header 请求头
 */
function put(url, data = {}, header = {}) {
  return request({ url, method: 'PUT', data, header })
}

/**
 * DELETE 请求
 * @param {String} url 请求地址
 * @param {Object} data 请求参数
 * @param {Object} header 请求头
 */
function del(url, data = {}, header = {}) {
  return request({ url, method: 'DELETE', data, header })
}

/**
 * 上传文件
 * @param {String} url 上传地址
 * @param {String} filePath 文件路径
 * @param {Object} formData 表单数据
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
              title: data.message || '上传失败',
              icon: 'none'
            })
            reject(data)
          }
        } catch (e) {
          reject({ error: 'parse_error', message: '响应解析失败' })
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '上传失败',
          icon: 'none'
        })
        reject({ error: 'upload_error', message: '上传失败' })
      }
    })
  })
}

// 导出
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
