<template>
  <el-container style="height: 100vh; overflow: hidden">
    <el-aside width="200px" style="background: #001529; overflow: hidden">
      <div style="padding: 20px 16px; color: #fff; font-size: 14px; font-weight: 600; border-bottom: 1px solid #1e2a38">
        🩺 糖尿病管理系统
      </div>
      <el-menu
        :router="true"
        :default-active="$route.path"
        background-color="#001529"
        text-color="#ccc"
        active-text-color="#fff"
        style="border-right: none"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/patients">
          <el-icon><User /></el-icon>
          <span>患者管理</span>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/doctors">
          <el-icon><UserFilled /></el-icon>
          <span>医生管理</span>
        </el-menu-item>
        <el-menu-item index="/blood-sugar">
          <el-icon><TrendCharts /></el-icon>
          <span>血糖记录</span>
        </el-menu-item>
        <el-menu-item index="/oxygen">
          <el-icon><Odometer /></el-icon>
          <span>血氧记录</span>
        </el-menu-item>
        <el-menu-item index="/messages">
          <el-icon><ChatDotRound /></el-icon>
          <span>消息中心</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="background: #fff; border-bottom: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; padding: 0 20px">
        <span style="font-size: 16px; color: #333">{{ pageTitle }}</span>
        <div style="display: flex; align-items: center; gap: 12px">
          <el-tag :type="isAdmin ? 'danger' : 'primary'">{{ isAdmin ? '管理员' : '医生' }}</el-tag>
          <span style="color: #666">{{ user?.name }}</span>
          <el-button size="small" @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main style="background: #f5f7fb; overflow: auto">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataLine, User, UserFilled, TrendCharts, Odometer, ChatDotRound } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const user = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || 'null') } catch { return null }
})
const isAdmin = computed(() => user.value?.role === 'admin')

const titles = {
  '/dashboard': '仪表盘',
  '/patients': '患者管理',
  '/doctors': '医生管理',
  '/blood-sugar': '血糖记录管理',
  '/oxygen': '血氧记录管理',
  '/messages': '消息中心',
}
const pageTitle = computed(() => titles[route.path] || '管理平台')

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>
