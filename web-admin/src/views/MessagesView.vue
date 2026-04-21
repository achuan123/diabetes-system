<template>
  <div>
    <el-card>
      <template #header>消息中心</template>

      <el-row :gutter="16" v-if="isAdmin">
        <!-- Admin: show all messages -->
        <el-col :span="24">
          <el-table :data="messages" v-loading="loading" stripe>
            <el-table-column prop="sender_id" label="发送者ID" width="100" />
            <el-table-column prop="receiver_id" label="接收者ID" width="100" />
            <el-table-column prop="content" label="内容" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" :formatter="fmtTime" width="160" />
          </el-table>
        </el-col>
      </el-row>

      <el-row :gutter="16" v-else>
        <!-- Doctor: show patient list + chat -->
        <el-col :span="8">
          <div style="font-weight: 600; margin-bottom: 12px">我的患者</div>
          <el-menu :default-active="String(activePatientId)" @select="selectPatient">
            <el-menu-item v-for="p in patients" :key="p.id" :index="String(p.id)">
              {{ p.name }} ({{ p.phone }})
            </el-menu-item>
          </el-menu>
        </el-col>
        <el-col :span="16">
          <div v-if="activePatientId">
            <div style="height: 360px; overflow-y: auto; border: 1px solid #eee; border-radius: 8px; padding: 12px; margin-bottom: 12px" ref="chatBox">
              <div v-for="m in chatMessages" :key="m.id" style="margin-bottom: 12px">
                <div :style="{ textAlign: m.sender_id === myId ? 'right' : 'left' }">
                  <el-tag size="small" :type="m.sender_id === myId ? 'primary' : 'info'">
                    {{ m.sender_id === myId ? '我' : '患者' }}
                  </el-tag>
                  <div style="margin-top: 4px; padding: 8px 12px; background: #f5f7fb; border-radius: 8px; display: inline-block; max-width: 80%; text-align: left">
                    {{ m.content }}
                  </div>
                  <div style="font-size: 12px; color: #999; margin-top: 2px">{{ fmtTime(null, null, m.created_at) }}</div>
                </div>
              </div>
              <div v-if="!chatMessages.length" style="text-align: center; color: #ccc; line-height: 100px">暂无消息</div>
            </div>
            <div style="display: flex; gap: 8px">
              <el-input v-model="newMsg" placeholder="输入消息..." @keyup.enter="sendMsg" />
              <el-button type="primary" @click="sendMsg">发送</el-button>
            </div>
          </div>
          <el-empty v-else description="请选择患者" />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import http from '../utils/http'

const loading = ref(false)
const messages = ref([])
const patients = ref([])
const activePatientId = ref(null)
const newMsg = ref('')
const chatBox = ref(null)

const user = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null }
})
const isAdmin = computed(() => user.value?.role === 'admin')
const myId = computed(() => user.value?.id)

const chatMessages = computed(() => {
  if (!activePatientId.value) return []
  return messages.value.filter(m =>
    (m.sender_id === myId.value && m.receiver_id === activePatientId.value) ||
    (m.receiver_id === myId.value && m.sender_id === activePatientId.value)
  ).sort((a, b) => a.id - b.id)
})

function fmtTime(row, col, val) {
  return val ? val.replace('T', ' ').slice(0, 16) : ''
}

async function selectPatient(id) {
  activePatientId.value = Number(id)
  await loadMessages()
}

async function loadMessages() {
  loading.value = true
  try {
    messages.value = await http.get('/messages')
    await nextTick()
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  } finally {
    loading.value = false
  }
}

async function sendMsg() {
  if (!newMsg.value.trim() || !activePatientId.value) return
  await http.post('/messages', { receiver_id: activePatientId.value, content: newMsg.value })
  newMsg.value = ''
  await loadMessages()
}

onMounted(async () => {
  if (isAdmin.value) {
    loading.value = true
    try {
      const users = await http.get('/admin/users')
      messages.value = await http.get('/messages')
      // Enrich sender/receiver names
      const userMap = {}
      users.forEach(u => { userMap[u.id] = u.name })
      messages.value = messages.value.map(m => ({
        ...m,
        sender_name: userMap[m.sender_id] || m.sender_id,
        receiver_name: userMap[m.receiver_id] || m.receiver_id,
      }))
    } finally {
      loading.value = false
    }
  } else {
    patients.value = await http.get('/doctor/patients')
    if (patients.value.length) {
      activePatientId.value = patients.value[0].id
      await loadMessages()
    }
  }
})
</script>
