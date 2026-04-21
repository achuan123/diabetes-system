<script>
export default {
  onLaunch() {
    const token = uni.getStorageSync('token')
    if (!token) {
      uni.reLaunch({ url: '/pages/login/login' })
    }
  },
  onShow() {},
  onHide() {}
}
</script>

<style>
page { background-color: #f5f7fb; }
.card { background: #fff; border-radius: 12rpx; padding: 24rpx; margin-bottom: 20rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06); }
.btn-primary { background: #1677ff; color: #fff; border-radius: 8rpx; padding: 20rpx; text-align: center; font-size: 30rpx; }
.btn-default { background: #f0f0f0; color: #333; border-radius: 8rpx; padding: 20rpx; text-align: center; font-size: 30rpx; }
.row { display: flex; align-items: center; margin-bottom: 20rpx; }
.label { width: 160rpx; color: #666; font-size: 28rpx; flex-shrink: 0; }
.input { flex: 1; border: 1rpx solid #e0e0e0; border-radius: 8rpx; padding: 16rpx; font-size: 28rpx; background: #fafafa; }
</style>
