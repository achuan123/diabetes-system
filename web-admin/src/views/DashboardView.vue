<template>
  <div>
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :span="6" v-for="item in statCards" :key="item.title">
        <el-card shadow="hover" style="text-align: center; cursor: pointer" @click="$router.push(item.route)">
          <div style="font-size: 32px; margin-bottom: 8px">{{ item.icon }}</div>
          <div style="font-size: 28px; font-weight: 700; color: #409EFF">{{ item.value ?? '—' }}</div>
          <div style="color: #999; margin-top: 4px">{{ item.title }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card header="最新血糖记录">
          <el-table :data="recentRecords.filter(r => r.record_type === 'blood_sugar')" size="small">
            <el-table-column prop="patient_name" label="患者" />
            <el-table-column label="血糖值">
              <template #default="{ row }">{{ row.value }} {{ row.unit }}</template>
            </el-table-column>
            <el-table-column prop="measured_at" label="时间" :formatter="fmtTime" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="最新血氧记录">
          <el-table :data="recentRecords.filter(r => r.record_type === 'oxygen')" size="small">
            <el-table-column prop="patient_name" label="患者" />
            <el-table-column label="血氧值">
              <template #default="{ row }">{{ row.value }} {{ row.unit }}</template>
            </el-table-column>
            <el-table-column prop="measured_at" label="时间" :formatter="fmtTime" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import http from '../utils/http'

const stats = ref({})
const recentRecords = ref([])
const user = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null }
})
const isAdmin = computed(() => user.value?.role === 'admin')

const statCards = computed(() => {
  if (isAdmin.value) {
    return [
      { icon: '👥', title: '患者总数', value: stats.value.patients, route: '/patients' },
      { icon: '👨‍⚕️', title: '医生总数', value: stats.value.doctors, route: '/doctors' },
      { icon: '🩸', title: '血糖记录', value: stats.value.blood_sugar_records, route: '/blood-sugar' },
      { icon: '💨', title: '血氧记录', value: stats.value.oxygen_records, route: '/oxygen' },
    ]
  }
  return [
    { icon: '👥', title: '我的患者', value: stats.value.patients, route: '/patients' },
    { icon: '🩸', title: '血糖记录', value: stats.value.blood_sugar_records, route: '/blood-sugar' },
    { icon: '💨', title: '血氧记录', value: stats.value.oxygen_records, route: '/oxygen' },
    { icon: '💬', title: '消息', value: stats.value.messages, route: '/messages' },
  ]
})

function fmtTime(row, col, val) {
  return val ? val.replace('T', ' ').slice(0, 16) : ''
}

onMounted(async () => {
  try {
    if (isAdmin.value) {
      stats.value = await http.get('/admin/stats')
      recentRecords.value = (await http.get('/admin/records')).slice(0, 10)
    } else {
      const patients = await http.get('/doctor/patients')
      stats.value = { patients: patients.length }
    }
  } catch {}
})
</script>
