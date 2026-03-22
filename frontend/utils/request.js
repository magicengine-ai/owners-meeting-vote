// utils/request.js
const config = {
  baseUrl: 'https://owners-vote-234350-9-1411900181.sh.run.tcloudbase.com',
  timeout: 10000
}

const TOKEN_KEY = 'access_token'
const USER_INFO_KEY = 'userInfo'

function getToken() {
  return wx.getStorageSync(TOKEN_KEY) || ''
}

function setToken(token) {
  wx.setStorageSync(TOKEN_KEY, token)
}

function clearToken() {
  wx.removeStorageSync(TOKEN_KEY)
  wx.removeStorageSync(USER_INFO_KEY)
}

function getUserInfo() {
  return wx.getStorageSync(USER_INFO_KEY) || null
}

function setUserInfo(userInfo) {
  wx.setStorageSync(USER_INFO_KEY, userInfo)
}

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
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          clearToken()
          wx.showToast({ title: '登录已过期', icon: 'none' })
          setTimeout(() => {
            wx.navigateTo({ url: '/pages/auth/login/login' })
          }, 1500)
          reject({ error: 'unauthorized' })
        } else if (res.statusCode === 403) {
          wx.showToast({ title: res.data.detail || '权限不足', icon: 'none' })
          reject(res.data)
        } else if (res.statusCode === 422) {
          wx.showToast({ title: '参数错误', icon: 'none' })
          reject(res.data)
        } else {
          wx.showToast({ title: res.data.message || '请求失败', icon: 'none' })
          reject(res.data)
        }
      },
      fail: (err) => {
        console.error('请求失败:', err)
        wx.showToast({ title: '网络错误', icon: 'none' })
        reject({ error: 'network_error' })
      }
    })
  })
}

function get(url, data = {}, header = {}) {
  return request({ url, method: 'GET', data, header })
}

function post(url, data = {}, header = {}) {
  return request({ url, method: 'POST', data, header })
}

function put(url, data = {}, header = {}) {
  return request({ url, method: 'PUT', data, header })
}

function del(url, data = {}, header = {}) {
  return request({ url, method: 'DELETE', data, header })
}

function uploadFile(url, filePath, formData = {}) {
  const token = getToken()
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: config.baseUrl + url,
      filePath: filePath,
      name: 'file',
      formData: formData,
      header: { 'Authorization': token ? `Bearer ${token}` : '' },
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data)
          } else {
            wx.showToast({ title: data.message || '上传失败', icon: 'none' })
            reject(data)
          }
        } catch (e) {
          reject({ error: 'parse_error' })
        }
      },
      fail: (err) => {
        wx.showToast({ title: '上传失败', icon: 'none' })
        reject({ error: 'upload_error' })
      }
    })
  })
}

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
