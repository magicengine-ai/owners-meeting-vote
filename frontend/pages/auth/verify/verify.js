// pages/auth/verify/verify.js
const app = getApp()
const { post, get, getToken, setUserInfo } = require('../../../utils/request.js')

Page({
  data: {
    verifyStatus: 'none', // none, pending, approved, rejected
    rejectReason: '',
    currentStep: 1, // 1, 2, 3
    imagePath: '',
    imageBase64: '',
    ocrLoading: false,
    ocrData: null,
    userInfo: null
  },

  onLoad(options) {
    // 检查登录状态
    const token = getToken()
    if (!token) {
      wx.redirectTo({
        url: '/pages/auth/login/login'
      })
      return
    }

    // 获取用户信息
    this.loadUserInfo()
  },

  onShow() {
    // 每次显示时刷新认证状态
    this.loadVerifyStatus()
  },

  /**
   * 加载用户信息
   */
  async loadUserInfo() {
    try {
      const res = await get('/api/auth/me')
      const userInfo = {
        openid: res.openid,
        nickname: res.nickname,
        avatar_url: res.avatar_url,
        phone: res.phone,
        is_verified: res.is_verified
      }
      this.setData({ userInfo })
      setUserInfo(userInfo)

      if (res.is_verified) {
        this.setData({ verifyStatus: 'approved' })
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  },

  /**
   * 加载认证状态
   */
  async loadVerifyStatus() {
    try {
      const res = await get('/api/auth/verify/status')
      this.setData({
        verifyStatus: res.status,
        rejectReason: res.status === 'rejected' ? res.message : ''
      })
    } catch (error) {
      console.error('获取认证状态失败:', error)
    }
  },

  /**
   * 选择图片
   */
  chooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      sizeType: ['compressed'],
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath
        this.setData({
          imagePath: tempFilePath
        })

        // 转换为 Base64
        this.imageToBase64(tempFilePath)
      },
      fail: (err) => {
        console.error('选择图片失败:', err)
        wx.showToast({
          title: '选择失败，请重试',
          icon: 'none'
        })
      }
    })
  },

  /**
   * 图片转 Base64
   */
  imageToBase64(filePath) {
    const fs = wx.getFileSystemManager()
    fs.readFile({
      filePath: filePath,
      encoding: 'base64',
      success: (res) => {
        this.setData({
          imageBase64: res.data
        })
      },
      fail: (err) => {
        console.error('图片转换失败:', err)
        wx.showToast({
          title: '图片处理失败',
          icon: 'none'
        })
      }
    })
  },

  /**
   * 下一步
   */
  nextStep() {
    const { currentStep, imageBase64 } = this.data

    if (currentStep === 1) {
      if (!imageBase64) {
        wx.showToast({
          title: '请先上传图片',
          icon: 'none'
        })
        return
      }

      // 进入 OCR 识别步骤
      this.setData({
        currentStep: 2,
        ocrLoading: true
      })

      // 调用 OCR 识别
      this.performOCR()
    }
  },

  /**
   * 上一步
   */
  prevStep() {
    const { currentStep } = this.data
    if (currentStep > 1) {
      this.setData({
        currentStep: currentStep - 1
      })
    }
  },

  /**
   * 执行 OCR 识别
   */
  async performOCR() {
    const { imageBase64 } = this.data

    try {
      const res = await post('/api/auth/property/ocr', {
        image_base64: imageBase64,
        cert_type: 'property'
      })

      this.setData({
        ocrLoading: false,
        ocrData: res
      })
    } catch (error) {
      console.error('OCR 识别失败:', error)
      this.setData({
        ocrLoading: false
      })
      wx.showToast({
        title: error.message || '识别失败，请重试',
        icon: 'none'
      })
    }
  },

  /**
   * 提交认证
   */
  async submitVerify() {
    const { ocrData } = this.data

    if (!ocrData) {
      wx.showToast({
        title: '请先完成 OCR 识别',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '确认提交',
      content: '请确认房产证信息准确无误，提交后将进入审核流程',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '提交中...' })

            // 调用提交接口
            await post('/api/auth/property/verify', {
              owner_name: ocrData.owner_name,
              cert_number: ocrData.cert_number,
              address: ocrData.address,
              area: ocrData.area
            })

            wx.hideLoading()

            wx.showToast({
              title: '提交成功',
              icon: 'success'
            })

            // 更新状态
            this.setData({
              verifyStatus: 'pending',
              currentStep: 3
            })

            // 更新用户信息
            if (this.data.userInfo) {
              setUserInfo({
                ...this.data.userInfo,
                is_verified: false
              })
            }

          } catch (error) {
            wx.hideLoading()
            console.error('提交认证失败:', error)
            wx.showToast({
              title: error.message || '提交失败，请重试',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  /**
   * 重新认证
   */
  resetVerify() {
    wx.showModal({
      title: '重新认证',
      content: '确定要重新上传房产证吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            currentStep: 1,
            imagePath: '',
            imageBase64: '',
            ocrData: null,
            verifyStatus: 'none'
          })
        }
      }
    })
  }
})
