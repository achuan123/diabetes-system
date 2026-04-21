<template>
  <view style="padding: 30rpx">
    <view v-if="!doctorId" class="card" style="text-align: center; padding: 60rpx">
      <view style="font-size: 60rpx">👨‍⚕️</view>
      <view style="color: #999; margin-top: 16rpx">您还未绑定医生</view>
      <view style="color: #999; font-size: 26rpx; margin-top: 8rpx">请联系管理员或重新注册绑定医生</view>
    </view>

    <view v-else>
      <!-- Chat box -->
      <view style="background: #fff; border-radius: 12rpx; padding: 20rpx; height: 65vh; overflow-y: auto; margin-bottom: 20rpx" id="chatBox">
        <view v-if="!messages.length" style="text-align: center; padding: 60rpx; color: #ccc">
          暂无消息，发送第一条消息吧
        </view>
        <view v-for="m in messages" :key="m.id" style="margin-bottom: 20rpx"
          :style="{ textAlign: m.sender_id === myId ? 'right' : 'left' }"
        >
          <view style="display: inline-block; max-width: 72%">
            <view style="font-size: 22rpx; color: #ccc; margin-bottom: 6rpx">
              {{ m.sender_id === myId ? '我' : '医生' }} · {{ m.created_at && m.created_at.replace('T',' ').slice(0,16) }}
            </view>
            <view :style="{
              display: 'inline-block',
              padding: '16rpx 24rpx',
              borderRadius: m.sender_id === myId ? '16rpx 4rpx 16rpx 16rpx' : '4rpx 16rpx 16rpx 16rpx',
              background: m.sender_id === myId ? '#1677ff' : '#f5f5f5',
              color: m.sender_id === myId ? '#fff' : '#333',
              fontSize: '28rpx',
              wordBreak: 'break-all'
            }">{{ m.content }}</view>
          </view>
        </view>
      </view>

      <!-- Input area -->
      <view style="display: flex; gap: 16rpx; background: #fff; border-radius: 12rpx; padding: 16rpx">
        <input
          v-model="newMsg"
          style="flex: 1; font-size: 28rpx; padding: 16rpx; background: #f5f7fb; border-radius: 8rpx"
          placeholder="输入消息..."
          @confirm="sendMsg"
        />
        <view class="btn-primary" style="padding: 16rpx 32rpx; margin: 0" @tap="sendMsg">发送</view>
      </view>
    </view>
  </view>
</template>

<script>
import http from '../../utils/request'

export default {
  data() {
    return {
      messages: [],
      newMsg: '',
      doctorId: null,
      myId: null,
      loading: false
    }
  },
  onShow() { this.loadData() },
  methods: {
    async loadData() {
      try {
        const userStr = uni.getStorageSync('user')
        const user = userStr ? JSON.parse(userStr) : {}
        this.myId = user.id
        this.doctorId = user.doctor_id || (user.role === 'family' ? await this.getFamilyDoctorId(user) : null)
        if (this.doctorId) {
          this.messages = (await http.get('/messages')).sort((a, b) => a.id - b.id)
        }
      } catch {}
    },
    async getFamilyDoctorId(user) {
      // family users act as their bound patient
      return null
    },
    async sendMsg() {
      if (!this.newMsg.trim() || !this.doctorId) return
      try {
        await http.post('/messages', { receiver_id: this.doctorId, content: this.newMsg })
        this.newMsg = ''
        this.messages = (await http.get('/messages')).sort((a, b) => a.id - b.id)
        // Scroll to bottom
        uni.pageScrollTo({ scrollTop: 99999, duration: 100 })
      } catch {}
    }
  }
}
</script>
