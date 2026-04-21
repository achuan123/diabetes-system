<template>
  <view style="padding: 40rpx">
    <view class="card">
      <view style="font-size: 32rpx; font-weight: 600; margin-bottom: 30rpx; color: #333">患者注册</view>

      <view class="row">
        <text class="label">姓名</text>
        <input class="input" v-model="form.name" placeholder="请输入姓名" />
      </view>
      <view class="row">
        <text class="label">手机号</text>
        <input class="input" v-model="form.phone" type="number" placeholder="请输入手机号" />
      </view>
      <view class="row">
        <text class="label">密码</text>
        <input class="input" v-model="form.password" type="password" placeholder="6位以上密码" />
      </view>

      <view style="margin-bottom: 20rpx">
        <view style="color: #666; font-size: 28rpx; margin-bottom: 16rpx">选择医生（可选）</view>
        <scroll-view scroll-y style="height: 300rpx; border: 1rpx solid #eee; border-radius: 8rpx">
          <view
            v-for="d in doctors"
            :key="d.id"
            @tap="selectDoctor(d)"
            :style="{
              padding: '20rpx 24rpx',
              background: form.doctor_id === d.id ? '#e8f4ff' : '#fff',
              borderBottom: '1rpx solid #f5f5f5'
            }"
          >
            <text style="font-size: 28rpx; color: #333">👨‍⚕️ {{ d.name }}</text>
            <text v-if="form.doctor_id === d.id" style="color: #1677ff; float: right; font-size: 26rpx">✓ 已选</text>
          </view>
          <view v-if="!doctors.length" style="padding: 40rpx; text-align: center; color: #ccc">加载中...</view>
        </scroll-view>
      </view>
    </view>

    <view class="btn-primary" @tap="register">立即注册</view>
    <view style="text-align: center; margin-top: 24rpx" @tap="$navigateBack()">
      <text style="color: #1677ff; font-size: 28rpx">已有账号，去登录</text>
    </view>
  </view>
</template>

<script>
import http from '../../utils/request'

export default {
  data() {
    return {
      form: { name: '', phone: '', password: '', doctor_id: null },
      doctors: []
    }
  },
  onLoad() {
    this.loadDoctors()
  },
  methods: {
    async loadDoctors() {
      try {
        this.doctors = await http.get('/doctors')
      } catch {}
    },
    selectDoctor(d) {
      this.form.doctor_id = this.form.doctor_id === d.id ? null : d.id
    },
    async register() {
      if (!this.form.phone || !this.form.password || !this.form.name) {
        return uni.showToast({ title: '请填写完整信息', icon: 'none' })
      }
      uni.showLoading({ title: '注册中...' })
      try {
        const res = await http.post('/auth/patient/register', this.form)
        uni.setStorageSync('token', res.token)
        uni.setStorageSync('user', JSON.stringify(res.user))
        uni.hideLoading()
        uni.showToast({ title: '注册成功！', icon: 'success' })
        setTimeout(() => uni.switchTab({ url: '/pages/index/index' }), 1200)
      } catch {
        uni.hideLoading()
      }
    }
  }
}
</script>
