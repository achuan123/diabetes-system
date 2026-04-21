<template>
  <view style="padding: 30rpx">
    <!-- Add reminder button -->
    <view class="btn-primary" style="margin-bottom: 24rpx" @tap="showAdd = true">+ 添加提醒</view>

    <view v-if="loading" style="text-align: center; padding: 60rpx; color: #ccc">加载中...</view>

    <view v-else-if="!reminders.length" style="text-align: center; padding: 80rpx; color: #ccc">
      <view style="font-size: 80rpx">⏰</view>
      <view style="margin-top: 20rpx">暂无提醒，点击上方添加</view>
    </view>

    <view v-else>
      <view v-for="r in reminders" :key="r.id" class="card">
        <view style="display: flex; justify-content: space-between; align-items: flex-start">
          <view style="flex: 1">
            <view style="display: flex; align-items: center; gap: 12rpx; margin-bottom: 10rpx">
              <text style="font-size: 36rpx">{{ r.reminder_type === 'medication' ? '💊' : '🥗' }}</text>
              <text style="font-size: 26rpx; padding: 4rpx 16rpx; border-radius: 20rpx; background: #e8f4ff; color: #1677ff">
                {{ r.reminder_type === 'medication' ? '用药' : '饮食' }}
              </text>
              <text style="font-size: 28rpx; font-weight: 600; color: #1677ff">{{ r.remind_time }}</text>
            </view>
            <view style="font-size: 28rpx; color: #555">{{ r.content }}</view>
          </view>
        </view>
      </view>
    </view>

    <!-- Add Dialog -->
    <view v-if="showAdd" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 100" @tap.self="showAdd = false">
      <view style="background: #fff; margin: 200rpx 40rpx; border-radius: 16rpx; padding: 40rpx">
        <view style="font-size: 32rpx; font-weight: 600; margin-bottom: 30rpx">添加提醒</view>

        <view class="row">
          <text class="label">类型</text>
          <view style="display: flex; gap: 16rpx; flex: 1">
            <view
              @tap="form.reminder_type = 'medication'"
              :style="{ padding: '12rpx 24rpx', borderRadius: '8rpx', fontSize: '26rpx', background: form.reminder_type === 'medication' ? '#1677ff' : '#f5f5f5', color: form.reminder_type === 'medication' ? '#fff' : '#666' }"
            >💊 用药</view>
            <view
              @tap="form.reminder_type = 'diet'"
              :style="{ padding: '12rpx 24rpx', borderRadius: '8rpx', fontSize: '26rpx', background: form.reminder_type === 'diet' ? '#1677ff' : '#f5f5f5', color: form.reminder_type === 'diet' ? '#fff' : '#666' }"
            >🥗 饮食</view>
          </view>
        </view>

        <view class="row">
          <text class="label">提醒时间</text>
          <input class="input" v-model="form.remind_time" placeholder="如 08:00" />
        </view>

        <view class="row">
          <text class="label">内容</text>
          <input class="input" v-model="form.content" placeholder="提醒内容" />
        </view>

        <view style="display: flex; gap: 16rpx; margin-top: 20rpx">
          <view class="btn-default" style="flex: 1" @tap="showAdd = false">取消</view>
          <view class="btn-primary" style="flex: 1" @tap="addReminder">确认</view>
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
      loading: false,
      reminders: [],
      showAdd: false,
      form: { reminder_type: 'medication', remind_time: '08:00', content: '' }
    }
  },
  onShow() { this.loadReminders() },
  methods: {
    async loadReminders() {
      this.loading = true
      try {
        this.reminders = await http.get('/patient/reminders')
      } catch {
      } finally {
        this.loading = false
      }
    },
    async addReminder() {
      if (!this.form.content) {
        return uni.showToast({ title: '请填写提醒内容', icon: 'none' })
      }
      await http.post('/patient/reminders', this.form)
      uni.showToast({ title: '添加成功', icon: 'success' })
      this.showAdd = false
      this.form = { reminder_type: 'medication', remind_time: '08:00', content: '' }
      this.loadReminders()
    }
  }
}
</script>
