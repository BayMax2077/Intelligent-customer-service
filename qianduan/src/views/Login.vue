<template>
  <div class="login-page">
    <div class="login-title">智能客服管理台</div>
    <div class="section-card login-card">
      
      <el-form class="login-form" label-position="top" @submit.prevent="onLogin">
        <el-form-item label="用户名">
          <el-input v-model="username" @keyup.enter="onLogin" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" @keyup.enter="onLogin" />
        </el-form-item>
        <el-button type="primary" @click="onLogin" :loading="loading" class="login-btn">登录</el-button>
      </el-form>
    </div>
  </div>
 </template>

<script setup lang="ts">
import { ref } from 'vue'
import http from '../api/http'
import { useAuthStore } from '../store/auth'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()

const onLogin = async () => {
  // 前端验证
  if (!username.value || !password.value) {
    ElMessage.error('请输入用户名和密码')
    return
  }
  
  loading.value = true
  try {
    const res = await http.post('/api/auth/login', { 
      username: username.value, 
      password: password.value 
    })
    
    if ((res.status === 200 || res.status === 204) && 
        res.data && (res.data.ok || res.data.OK || res.data.success)) {
      auth.setAuthed(true, username.value)
      router.push('/shops')
    } else {
      ElMessage.error('登录失败')
    }
  } catch (e: any) {
    // 统一处理各种错误情况
    const status = e?.response?.status
    const data = e?.response?.data
    
    // 优先使用后端返回的错误信息
    let errorMsg = data?.error || data?.message
    
    // 如果没有后端错误信息，根据状态码提供友好提示
    if (!errorMsg) {
      if (status === 401) {
        errorMsg = '用户名或密码错误'
      } else if (status === 400) {
        errorMsg = '请求参数错误'
      } else if (status === 500) {
        errorMsg = '服务器错误，请稍后重试'
      } else if (e?.message && String(e.message).includes('Network')) {
        errorMsg = '网络连接失败，请检查网络设置'
      } else {
        errorMsg = '登录失败，请稍后重试'
      }
    }
    
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { min-height: 100%; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:40px 16px; }
.login-title { font-size:28px; font-weight:700; margin-bottom:18px; color:#303133; }
.login-card { 
  --size: 460px;
  width: var(--size);
  height: var(--size); /* 正方形背景 */
  max-width: 92vw; 
  max-height: 92vh;
  padding: 28px;
  display:flex; flex-direction:column; justify-content:center;
}
.login-form { width: 100%; }
.desc { color:#909399; font-size: 13px; margin: 0 0 16px; text-align:center }
.login-btn { width:100%; height:44px; font-size:16px }
.desc { color:#909399; font-size: 13px; margin: 0 0 16px; }
</style>

