<template>
  <view style="padding: 40rpx">
    <view class="card">
      <view style="font-size: 30rpx; font-weight: 600; color: #333; margin-bottom: 30rpx">
        {{ recordType === 'blood_sugar' ? '🩸 血糖记录' : '💨 血氧记录' }}
      </view>

      <!-- Type selector -->
      <view style="display: flex; gap: 16rpx; margin-bottom: 30rpx">
        <view
          @tap="recordType = 'blood_sugar'"
          :style="{
            flex: 1, textAlign: 'center', padding: '20rpx',
            borderRadius: '8rpx', fontSize: '28rpx',
            background: recordType === 'blood_sugar' ? '#1677ff' : '#f5f5f5',
            color: recordType === 'blood_sugar' ? '#fff' : '#666'
          }"
        >血糖</view>
        <view
          @tap="recordType = 'oxygen'"
          :style="{
            flex: 1, textAlign: 'center', padding: '20rpx',
            borderRadius: '8rpx', fontSize: '28rpx',
            background: recordType === 'oxygen' ? '#1677ff' : '#f5f5f5',
            color: recordType === 'oxygen' ? '#fff' : '#666'
          }"
        >血氧</view>
      </view>

      <view class="row">
        <text class="label">{{ recordType === 'blood_sugar' ? '血糖值' : '血氧值' }}</text>
        <input
          class="input"
          v-model="value"
          type="digit"
          :placeholder="recordType === 'blood_sugar' ? '单位: mmol/L（如 6.2）' : '百分比（如 98）'"
        />
      </view>

      <!-- Range hint -->
      <view style="background: #f0f7ff; border-radius: 8rpx; padding: 20rpx; margin-top: 10rpx; font-size: 24rpx; color: #555">
        <view v-if="recordType === 'blood_sugar'">
          <text>参考范围：空腹 3.9–6.1 mmol/L，餐后 3.9–7.8 mmol/L</text>
        </view>
        <view v-else>
          <text>参考范围：正常 ≥95%，轻度低氧 90–94%，危险 &lt;90%</text>
        </view>
      </view>
    </view>

    <view class="btn-primary" @tap="submit">保存记录</view>
  </view>
</template>

<script>
import http from '../../utils/request'

export default {
  data() {
    return {
      recordType: 'blood_sugar',
      value: ''
    }
  },
  onLoad(options) {
    if (options.type) this.recordType = options.type
  },
  methods: {
    async submit() {
      if (!this.value) {
        return uni.showToast({ title: '请输入数值', icon: 'none' })
      }
      const v = parseFloat(this.value)
      if (isNaN(v) || v <= 0) {
        return uni.showToast({ title: '请输入有效数值', icon: 'none' })
      }
      uni.showLoading({ title: '保存中...' })
      try {
        await http.post('/patient/records', { record_type: this.recordType, value: String(v) })
        uni.hideLoading()
        uni.showToast({ title: '记录成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 1200)
      } catch {
        uni.hideLoading()
      }
    }
  }
}
</script>
