<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>医生列表</span>
          <el-button type="primary" @click="openAdd">+ 新增医生</el-button>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="患者数量">
          <template #default="{ row }">
            {{ patientCounts[row.id] ?? 0 }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-popconfirm title="确认删除该医生？" @confirm="deleteUser(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="addDialog" title="新增医生账号" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" type="password" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialog = false">取消</el-button>
        <el-button type="primary" @click="addDoctor">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../utils/http'

const loading = ref(false)
const list = ref([])
const allPatients = ref([])
const addDialog = ref(false)
const form = ref({ name: '', email: '', password: '' })

const patientCounts = computed(() => {
  const m = {}
  allPatients.value.forEach(p => {
    if (p.doctor_id) m[p.doctor_id] = (m[p.doctor_id] || 0) + 1
  })
  return m
})

async function loadData() {
  loading.value = true
  try {
    const users = await http.get('/admin/users')
    list.value = users.filter(u => u.role === 'doctor')
    allPatients.value = users.filter(u => u.role === 'patient')
  } finally {
    loading.value = false
  }
}

function openAdd() {
  form.value = { name: '', email: '', password: '' }
  addDialog.value = true
}

async function addDoctor() {
  if (!form.value.email || !form.value.password) {
    return ElMessage.warning('请填写邮箱和密码')
  }
  await http.post('/auth/web/register', { ...form.value, role: 'doctor' })
  ElMessage.success('医生账号创建成功')
  addDialog.value = false
  loadData()
}

async function deleteUser(uid) {
  await http.delete(`/admin/users/${uid}`)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(loadData)
</script>
