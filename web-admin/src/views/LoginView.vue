<template>
  <div class="login-wrap">
    <el-card class="card">
      <h2>Web管理端登录</h2>
      <el-alert type="info" :closable="false" show-icon>
        <template #title>医生: doctor@123.com / doctor123456；管理员: admin@123 / admin123456</template>
      </el-alert>
      <el-form label-position="top" style="margin-top: 16px">
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="form.password" show-password /></el-form-item>
        <el-button type="primary" style="width: 100%" @click="goDashboard">登录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const form = reactive({ email: '', password: '' })
const goDashboard = () => router.push('/dashboard')
</script>

<style scoped>
.login-wrap { min-height: 100vh; display: grid; place-items: center; background: #f5f7fa; }
.card { width: min(92vw, 420px); }
</style>
