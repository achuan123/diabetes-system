<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>血糖记录管理</span>
          <div style="display: flex; gap: 8px">
            <el-input v-model="search" placeholder="搜索患者姓名" style="width: 200px" clearable />
          </div>
        </div>
      </template>

      <el-table :data="filteredList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="patient_name" label="患者" />
        <el-table-column label="血糖值 (mmol/L)">
          <template #default="{ row }">
            <el-tag :type="getTag(row.value)">{{ row.value }} mmol/L</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="measured_at" label="测量时间" :formatter="fmtTime" />
      </el-table>

      <div style="margin-top: 12px; color: #666; font-size: 13px">
        共 {{ filteredList.length }} 条记录 &nbsp;|&nbsp;
        <span style="color: #67c23a">正常 (3.9–7.0): {{ normalCount }}</span> &nbsp;|&nbsp;
        <span style="color: #e6a23c">偏高 (>7.0): {{ highCount }}</span> &nbsp;|&nbsp;
        <span style="color: #f56c6c">过高 (>11.1): {{ veryHighCount }}</span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '../utils/http'

const loading = ref(false)
const list = ref([])
const search = ref('')

const user = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null }
})
const isAdmin = computed(() => user.value?.role === 'admin')

const filteredList = computed(() => {
  const q = search.value.toLowerCase()
  return list.value.filter(r =>
    !q || r.patient_name?.toLowerCase().includes(q)
  )
})

const normalCount = computed(() => filteredList.value.filter(r => { const v = parseFloat(r.value); return v >= 3.9 && v <= 7.0 }).length)
const highCount = computed(() => filteredList.value.filter(r => { const v = parseFloat(r.value); return v > 7.0 && v <= 11.1 }).length)
const veryHighCount = computed(() => filteredList.value.filter(r => parseFloat(r.value) > 11.1).length)

function getTag(value) {
  const v = parseFloat(value)
  if (v > 11.1) return 'danger'
  if (v > 7.0) return 'warning'
  if (v < 3.9) return 'warning'
  return 'success'
}

function fmtTime(row, col, val) {
  return val ? val.replace('T', ' ').slice(0, 16) : ''
}

async function loadData() {
  loading.value = true
  try {
    if (isAdmin.value) {
      list.value = await http.get('/admin/records?record_type=blood_sugar')
    } else {
      list.value = await http.get('/doctor/records?record_type=blood_sugar')
    }
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
