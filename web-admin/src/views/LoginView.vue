<template>
  <div class="login-wrap">
    <el-card class="card">
      <h2>Web管理端登录</h2>
      <el-form label-position="top" style="margin-top: 16px">
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" show-password /></el-form-item>
        <el-button type="primary" :loading="loading" style="width: 100%" @click="goDashboard">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const form = reactive({ email: '', password: '' })
const loading = ref(false)

const goDashboard = async () => {
  if (!form.email || !form.password) {
    ElMessage.error('请输入邮箱和密码')
    return
  }
  try {
    loading.value = true
    const { data } = await axios.post('/api/auth/web/login', form)
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap { min-height: 100vh; display: grid; place-items: center; background: #f5f7fa; }
.card { width: min(92vw, 420px); }
</style>
