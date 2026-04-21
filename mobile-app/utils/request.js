// 修改此处为实际后端服务器地址
const BASE_URL = 'http://127.0.0.1:5000/api'

const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      success: (res) => {
        if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('user')
          uni.reLaunch({ url: '/pages/login/login' })
          return
        }
        if (res.statusCode >= 400) {
          const msg = res.data?.error || '请求失败'
          uni.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
          return
        }
        resolve(res.data)
      },
      fail: () => {
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(new Error('network error'))
      }
    })
  })
}

export default {
  get: (url, data) => request({ url, method: 'GET', data }),
  post: (url, data) => request({ url, method: 'POST', data }),
  delete: (url) => request({ url, method: 'DELETE' }),
}
