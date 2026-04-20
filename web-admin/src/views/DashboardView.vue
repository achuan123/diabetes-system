<template>
  <div style="padding: 20px">
    <el-page-header content="社区糖尿病管理系统" @back="$router.push('/login')" />
    <el-row :gutter="12" style="margin-top: 12px">
      <el-col :span="6"><el-card>用户管理（患者/家属）</el-card></el-col>
      <el-col :span="6"><el-card>医生管理</el-card></el-col>
      <el-col :span="6"><el-card>血糖记录管理</el-card></el-col>
      <el-col :span="6"><el-card>血氧记录管理</el-card></el-col>
    </el-row>
  </div>
</template>
