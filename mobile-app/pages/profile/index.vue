<template>
  <view style="padding: 30rpx">
    <!-- Profile card -->
    <view class="card" style="display: flex; align-items: center; gap: 30rpx; margin-bottom: 24rpx">
      <view style="width: 120rpx; height: 120rpx; border-radius: 60rpx; background: #1677ff; display: flex; align-items: center; justify-content: center; font-size: 56rpx; color: #fff">
        {{ user.role === 'family' ? '👨‍👩‍👧' : '🧑' }}
      </view>
      <view>
        <view style="font-size: 34rpx; font-weight: 600; color: #333">{{ user.name || '—' }}</view>
        <view style="font-size: 24rpx; color: #999; margin-top: 8rpx">{{ user.phone }}</view>
        <view style="margin-top: 8rpx">
          <text style="font-size: 22rpx; padding: 4rpx 16rpx; background: #e8f4ff; color: #1677ff; border-radius: 20rpx">
            {{ user.role === 'family' ? '家属账号' : '患者账号' }}
          </text>
        </view>
      </view>
    </view>

    <!-- Menu items -->
    <view class="card" v-if="user.role === 'patient'">
      <view style="font-size: 28rpx; font-weight: 600; color: #333; margin-bottom: 20rpx">家属管理</view>
      <view @tap="uni.navigateTo({ url: '/pages/family/index' })" style="display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5">
        <view style="display: flex; align-items: center; gap: 16rpx">
          <text style="font-size: 36rpx">👨‍👩‍👧</text>
          <text style="font-size: 28rpx; color: #333">绑定家属</text>
        </view>
        <text style="color: #ccc">›</text>
      </view>
    </view>

    <view class="card">
      <view style="font-size: 28rpx; font-weight: 600; color: #333; margin-bottom: 20rpx">其他</view>
      <view @tap="logout" style="display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0">
        <view style="display: flex; align-items: center; gap: 16rpx">
          <text style="font-size: 36rpx">🚪</text>
          <text style="font-size: 28rpx; color: #ff4d4f">退出登录</text>
        </view>
        <text style="color: #ccc">›</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return { user: {} }
  },
  onShow() {
    const userStr = uni.getStorageSync('user')
    this.user = userStr ? JSON.parse(userStr) : {}
  },
  methods: {
    logout() {
      uni.showModal({
        title: '提示',
        content: '确认退出登录？',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync('token')
            uni.removeStorageSync('user')
            uni.reLaunch({ url: '/pages/login/login' })
          }
        }
      })
    }
  }
}
</script>
