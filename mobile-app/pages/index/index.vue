<template>
  <view style="padding: 30rpx">
    <!-- User Info Banner -->
    <view style="background: linear-gradient(135deg, #1677ff, #36a3f7); border-radius: 16rpx; padding: 40rpx; margin-bottom: 24rpx; color: #fff">
      <view style="font-size: 34rpx; font-weight: 600">你好，{{ user.name || '患者' }} 👋</view>
      <view style="margin-top: 12rpx; font-size: 26rpx; opacity: 0.9">
        <text>{{ isFamily ? '家属代管账号' : '患者账号' }}</text>
        <text v-if="user.phone"> · {{ user.phone }}</text>
      </view>
      <view v-if="doctorName" style="margin-top: 10rpx; font-size: 26rpx; opacity: 0.85">
        主治医生：{{ doctorName }}
      </view>
    </view>

    <!-- Quick Actions -->
    <view style="display: grid; grid-template-columns: 1fr 1fr; gap: 16rpx; margin-bottom: 24rpx">
      <view v-for="action in quickActions" :key="action.title"
        class="card" style="text-align: center; padding: 30rpx"
        @tap="action.handler"
      >
        <view style="font-size: 48rpx">{{ action.icon }}</view>
        <view style="margin-top: 10rpx; font-size: 26rpx; color: #555">{{ action.title }}</view>
      </view>
    </view>

    <!-- Today's Latest -->
    <view class="card" v-if="latestRecord">
      <view style="font-size: 28rpx; color: #999; margin-bottom: 12rpx">最新记录</view>
      <view style="display: flex; justify-content: space-between">
        <view>
          <text style="font-size: 40rpx; font-weight: 700; color: #1677ff">{{ latestRecord.value }}</text>
          <text style="font-size: 24rpx; color: #999"> {{ latestRecord.unit }}</text>
        </view>
        <view style="font-size: 24rpx; color: #ccc; text-align: right">
          <view>{{ latestRecord.record_type === 'blood_sugar' ? '血糖' : '血氧' }}</view>
          <view>{{ latestRecord.measured_at && latestRecord.measured_at.slice(0,10) }}</view>
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
      user: {},
      doctorName: '',
      latestRecord: null
    }
  },
  computed: {
    isFamily() {
      return this.user.role === 'family'
    },
    quickActions() {
      return [
        { icon: '🩸', title: '记录血糖', handler: () => uni.navigateTo({ url: '/pages/records/add?type=blood_sugar' }) },
        { icon: '💨', title: '记录血氧', handler: () => uni.navigateTo({ url: '/pages/records/add?type=oxygen' }) },
        { icon: '💊', title: '用药提醒', handler: () => uni.switchTab({ url: '/pages/reminders/index' }) },
        { icon: '💬', title: '联系医生', handler: () => uni.switchTab({ url: '/pages/messages/index' }) },
      ]
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const userStr = uni.getStorageSync('user')
        this.user = userStr ? JSON.parse(userStr) : {}
        if (this.user.doctor_id) {
          const doctors = await http.get('/doctors')
          const doc = doctors.find(d => d.id === this.user.doctor_id)
          this.doctorName = doc?.name || ''
        }
        const records = await http.get('/patient/records')
        this.latestRecord = records[0] || null
      } catch {}
    }
  }
}
</script>
