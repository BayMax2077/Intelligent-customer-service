<template>
  <div class="login-page">
    <div class="login-title">智能客服管理台</div>
    <div class="section-card login-card">
      <p class="desc">使用管理员账号登录以管理店铺配置与审核队列。</p>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const username = ref('admin')
const password = ref('admin')
const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()

const onLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.error('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await http.post('/api/auth/login', { username: username.value, password: password.value })
    if ((res.status === 200 || res.status === 204) && res.data && (res.data.ok || res.data.OK || res.data.success)) {
      auth.setAuthed(true, username.value)
      router.push('/shops')
    } else {
      ElMessage.error('登录失败')
    }
  } catch (e:any) {
    const status = e?.response?.status
    const statusText = e?.response?.statusText
    const data = e?.response?.data
    const isNetwork = e?.message && String(e.message).includes('Network')
    const hint = isNetwork ? '网络或跨域被浏览器拦截（预检/CORS/证书）' : ''
    const brief = data?.error || data?.message || e?.message || '登录失败'
    ElMessage.error(`${brief}${hint ? ' - ' + hint : ''}`)
    try {
      const detail = {
        url: e?.config?.baseURL ? `${e.config.baseURL}${e?.config?.url || ''}` : (e?.config?.url || ''),
        method: e?.config?.method,
        withCredentials: e?.config?.withCredentials,
        requestHeaders: e?.config?.headers,
        status,
        statusText,
        responseHeaders: e?.response?.headers,
        data,
      }
      await ElMessageBox.alert(`<pre style="white-space:pre-wrap;word-break:break-all;max-height:60vh;overflow:auto">${
        typeof window !== 'undefined' ? window.location.href : ''
      }\n\n${hint ? '[提示] ' + hint + '\n\n' : ''}${
        JSON.stringify(detail, null, 2)
      }</pre>`, '登录失败 - 详细信息', { dangerouslyUseHTMLString: true, confirmButtonText: '我知道了' })
    } catch {}
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

