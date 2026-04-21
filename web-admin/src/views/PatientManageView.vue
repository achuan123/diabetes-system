<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>患者列表</span>
          <el-input v-model="search" placeholder="搜索姓名/手机号" style="width: 240px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
      </template>

      <el-table :data="filteredList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column label="绑定医生">
          <template #default="{ row }">
            {{ doctorMap[row.doctor_id] || '未绑定' }}
          </template>
        </el-table-column>
        <el-table-column label="角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'patient' ? 'primary' : 'warning'" size="small">
              {{ row.role === 'patient' ? '患者' : '家属' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" v-if="isAdmin">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="viewRecords(row)">查看记录</el-button>
            <el-popconfirm title="确认删除该用户？" @confirm="deleteUser(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Records Dialog -->
    <el-dialog v-model="recordsDialog" :title="`${selectedPatient?.name} 的健康记录`" width="700px">
      <el-tabs>
        <el-tab-pane label="血糖记录">
          <el-table :data="patientRecords.filter(r => r.record_type === 'blood_sugar')" size="small">
            <el-table-column label="血糖值">
              <template #default="{ row }">{{ row.value }} {{ row.unit }}</template>
            </el-table-column>
            <el-table-column prop="measured_at" label="时间" :formatter="fmtTime" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="血氧记录">
          <el-table :data="patientRecords.filter(r => r.record_type === 'oxygen')" size="small">
            <el-table-column label="血氧值">
              <template #default="{ row }">{{ row.value }} {{ row.unit }}</template>
            </el-table-column>
            <el-table-column prop="measured_at" label="时间" :formatter="fmtTime" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import http from '../utils/http'

const loading = ref(false)
const list = ref([])
const doctors = ref([])
const search = ref('')
const recordsDialog = ref(false)
const selectedPatient = ref(null)
const patientRecords = ref([])

const user = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null }
})
const isAdmin = computed(() => user.value?.role === 'admin')

const doctorMap = computed(() => {
  const m = {}
  doctors.value.forEach(d => { m[d.id] = d.name })
  return m
})

const filteredList = computed(() => {
  const q = search.value.toLowerCase()
  return list.value.filter(u =>
    (u.role === 'patient' || u.role === 'family') &&
    (!q || u.name?.toLowerCase().includes(q) || u.phone?.includes(q))
  )
})

function fmtTime(row, col, val) {
  return val ? val.replace('T', ' ').slice(0, 16) : ''
}

async function loadData() {
  loading.value = true
  try {
    if (isAdmin.value) {
      const users = await http.get('/admin/users')
      list.value = users
    } else {
      list.value = await http.get('/doctor/patients')
    }
    doctors.value = await http.get('/doctors')
  } finally {
    loading.value = false
  }
}

async function viewRecords(patient) {
  selectedPatient.value = patient
  recordsDialog.value = true
  try {
    if (isAdmin.value) {
      const all = await http.get('/admin/records')
      patientRecords.value = all.filter(r => r.patient_id === patient.id)
    } else {
      patientRecords.value = await http.get(`/patient/records?patient_id=${patient.id}`)
    }
  } catch {}
}

async function deleteUser(uid) {
  await http.delete(`/admin/users/${uid}`)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
