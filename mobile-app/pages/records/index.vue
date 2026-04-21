<template>
  <view style="padding: 30rpx">
    <!-- Filter tabs -->
    <view style="display: flex; background: #fff; border-radius: 12rpx; padding: 8rpx; margin-bottom: 20rpx">
      <view
        v-for="tab in tabs" :key="tab.value"
        @tap="activeTab = tab.value"
        :style="{
          flex: 1, textAlign: 'center', padding: '16rpx',
          borderRadius: '8rpx', fontSize: '28rpx',
          background: activeTab === tab.value ? '#1677ff' : 'transparent',
          color: activeTab === tab.value ? '#fff' : '#666'
        }"
      >{{ tab.label }}</view>
    </view>

    <view v-if="loading" style="text-align: center; padding: 60rpx; color: #ccc">加载中...</view>

    <view v-else-if="!filteredRecords.length" style="text-align: center; padding: 80rpx; color: #ccc">
      <view style="font-size: 80rpx">📋</view>
      <view style="margin-top: 20rpx">暂无记录，去首页添加</view>
    </view>

    <view v-else>
      <view v-for="r in filteredRecords" :key="r.id" class="card">
        <view style="display: flex; justify-content: space-between; align-items: center">
          <view>
            <text style="font-size: 44rpx; font-weight: 700; color: #1677ff">{{ r.value }}</text>
            <text style="font-size: 24rpx; color: #999"> {{ r.unit }}</text>
          </view>
          <view style="text-align: right">
            <view>
              <text :style="{ fontSize: '22rpx', color: getStatusColor(r), background: getStatusBg(r), padding: '4rpx 12rpx', borderRadius: '20rpx' }">
                {{ getStatus(r) }}
              </text>
            </view>
            <view style="font-size: 22rpx; color: #ccc; margin-top: 8rpx">{{ r.measured_at && r.measured_at.replace('T',' ').slice(0,16) }}</view>
          </view>
        </view>
      </view>
    </view>

    <view class="btn-primary" style="margin-top: 20rpx" @tap="uni.navigateTo({ url: '/pages/records/add' })">
      + 添加记录
    </view>
  </view>
</template>

<script>
import http from '../../utils/request'

export default {
  data() {
    return {
      loading: false,
      records: [],
      activeTab: 'all',
      tabs: [
        { label: '全部', value: 'all' },
        { label: '血糖', value: 'blood_sugar' },
        { label: '血氧', value: 'oxygen' },
      ]
    }
  },
  computed: {
    filteredRecords() {
      if (this.activeTab === 'all') return this.records
      return this.records.filter(r => r.record_type === this.activeTab)
    }
  },
  onShow() { this.loadRecords() },
  methods: {
    async loadRecords() {
      this.loading = true
      try {
        this.records = await http.get('/patient/records')
      } catch {
      } finally {
        this.loading = false
      }
    },
    getStatus(r) {
      if (r.record_type === 'blood_sugar') {
        const v = parseFloat(r.value)
        if (v < 3.9) return '偏低'
        if (v > 11.1) return '过高'
        if (v > 7.0) return '偏高'
        return '正常'
      }
      const v = parseFloat(r.value)
      if (v < 90) return '危险'
      if (v < 95) return '偏低'
      return '正常'
    },
    getStatusColor(r) {
      const s = this.getStatus(r)
      return s === '正常' ? '#52c41a' : s === '危险' || s === '过高' ? '#ff4d4f' : '#fa8c16'
    },
    getStatusBg(r) {
      const s = this.getStatus(r)
      return s === '正常' ? '#f6ffed' : s === '危险' || s === '过高' ? '#fff2f0' : '#fff7e6'
    }
  }
}
</script>
