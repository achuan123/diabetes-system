<template>
  <view style="padding: 30rpx">
    <view class="card">
      <view style="font-size: 30rpx; font-weight: 600; color: #333; margin-bottom: 24rpx">绑定家属账号</view>
      <view style="font-size: 26rpx; color: #999; margin-bottom: 30rpx">
        家属绑定后，可使用家属手机号+密码登录，代您查看和录入健康数据。
      </view>

      <view class="row">
        <text class="label">家属姓名</text>
        <input class="input" v-model="form.name" placeholder="请输入家属姓名" />
      </view>
      <view class="row">
        <text class="label">手机号</text>
        <input class="input" v-model="form.phone" type="number" placeholder="家属手机号" />
      </view>
      <view class="row">
        <text class="label">登录密码</text>
        <input class="input" v-model="form.password" type="password" placeholder="为家属设置登录密码" />
      </view>
    </view>

    <view class="btn-primary" @tap="bindFamily">绑定家属</view>

    <!-- Existing family list -->
    <view class="card" v-if="familyList.length" style="margin-top: 24rpx">
      <view style="font-size: 28rpx; font-weight: 600; color: #333; margin-bottom: 16rpx">已绑定家属</view>
      <view v-for="f in familyList" :key="f.id" style="padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5; display: flex; align-items: center; gap: 16rpx">
        <text style="font-size: 40rpx">👤</text>
        <view>
          <view style="font-size: 28rpx; color: #333">{{ f.name }}</view>
          <view style="font-size: 24rpx; color: #999">{{ f.phone }}</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import http from '../../utils/request'

export default {
  data() {
    return {
      form: { name: '', phone: '', password: '' },
      familyList: []
    }
  },
  onLoad() {
    this.loadFamily()
  },
  methods: {
    async loadFamily() {
      try {
        // Get all users to find family members bound to this patient
        // This endpoint is not available to patients, so we just show nothing
        this.familyList = []
      } catch {}
    },
    async bindFamily() {
      if (!this.form.name || !this.form.phone || !this.form.password) {
        return uni.showToast({ title: '请填写完整信息', icon: 'none' })
      }
      uni.showLoading({ title: '绑定中...' })
      try {
        await http.post('/auth/family/register', this.form)
        uni.hideLoading()
        uni.showToast({ title: '家属绑定成功！', icon: 'success' })
        this.form = { name: '', phone: '', password: '' }
      } catch {
        uni.hideLoading()
      }
    }
  }
}
</script>
