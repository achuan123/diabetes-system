<template>
  <view style="padding: 60rpx 40rpx">
    <view style="text-align: center; margin-bottom: 60rpx">
      <text style="font-size: 48rpx; font-weight: 700; color: #1677ff">🩺 糖尿病管理</text>
      <view style="margin-top: 12rpx; color: #999; font-size: 26rpx">社区患者健康管理平台</view>
    </view>

    <view class="card">
      <view class="row">
        <text class="label">手机号</text>
        <input class="input" v-model="form.phone" type="number" placeholder="请输入手机号" />
      </view>
      <view class="row">
        <text class="label">密码</text>
        <input class="input" v-model="form.password" type="password" placeholder="请输入密码" />
      </view>
    </view>

    <view class="btn-primary" @tap="login" style="margin-bottom: 20rpx">登 录</view>
    <view class="btn-default" @tap="toRegister">注册新账号</view>

    <view style="margin-top: 40rpx; text-align: center">
      <view class="btn-default" @tap="toFamilyLogin" style="margin-top: 20rpx; background: #f0f7ff; color: #1677ff">
        家属登录
      </view>
    </view>
  </view>
</template>

<script>
import http from '../../utils/request'

export default {
  data() {
    return {
      form: { phone: '', password: '' }
    }
  },
  methods: {
    async login() {
      if (!this.form.phone || !this.form.password) {
        return uni.showToast({ title: '请填写手机号和密码', icon: 'none' })
      }
      uni.showLoading({ title: '登录中...' })
      try {
        const res = await http.post('/auth/patient/login', this.form)
        uni.setStorageSync('token', res.token)
        uni.setStorageSync('user', JSON.stringify(res.user))
        uni.hideLoading()
        uni.switchTab({ url: '/pages/index/index' })
      } catch {
        uni.hideLoading()
      }
    },
    toRegister() {
      uni.navigateTo({ url: '/pages/register/register' })
    },
    async toFamilyLogin() {
      if (!this.form.phone || !this.form.password) {
        return uni.showToast({ title: '请填写手机号和密码', icon: 'none' })
      }
      uni.showLoading({ title: '登录中...' })
      try {
        const res = await http.post('/auth/family/login', this.form)
        uni.setStorageSync('token', res.token)
        uni.setStorageSync('user', JSON.stringify(res.user))
        uni.hideLoading()
        uni.switchTab({ url: '/pages/index/index' })
      } catch {
        uni.hideLoading()
      }
    }
  }
}
</script>
