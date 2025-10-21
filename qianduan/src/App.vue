<template>
  <el-container style="height:100%">
    <!-- 头部导航 -->
    <el-header v-if="!isLogin" height="64px" class="app-header">
      <div class="header-content">
        <div class="brand">
          <el-icon size="24" style="margin-right: 8px; color: var(--primary)">
            <Setting />
          </el-icon>
          <span>智能客服管理台</span>
        </div>
        
        <el-menu 
          mode="horizontal" 
          :ellipsis="false" 
          router 
          :default-active="$route.path"
          class="nav"
        >
          <el-menu-item index="/shops">
            <el-icon><Shop /></el-icon>
            <span>店铺配置</span>
          </el-menu-item>
          <el-menu-item index="/messages">
            <el-icon><Message /></el-icon>
            <span>消息列表</span>
          </el-menu-item>
          <el-menu-item index="/audit">
            <el-icon><Document /></el-icon>
            <span>审核队列</span>
          </el-menu-item>
          <el-menu-item index="/kb">
            <el-icon><Collection /></el-icon>
            <span>知识库管理</span>
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <span>统计报表</span>
          </el-menu-item>
          <el-menu-item index="/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </el-menu>
        
        <div class="header-actions">
          <el-button 
            v-if="!isLoggedIn" 
            type="primary" 
            size="default"
            @click="$router.push('/login')"
            class="login-btn"
          >
            <el-icon><User /></el-icon>
            登录
          </el-button>
          <el-dropdown v-else trigger="click" @command="handleUserAction">
            <el-button type="text" class="user-dropdown">
              <el-icon><Avatar /></el-icon>
              {{ auth.username }}
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>
    
    <!-- 主要内容区域 -->
    <el-main class="main-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from './store/auth'
import { ElMessage } from 'element-plus'
import http from './api/http'
import { 
  Setting, Shop, Message, Document, Collection, Upload,
  DataAnalysis, User, Avatar, ArrowDown, SwitchButton 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const isLogin = computed(() => route.path === '/login')
const isLoggedIn = computed(() => auth.isAuthed)

const handleUserAction = async (command: string) => {
  if (command === 'logout') {
    await logout()
  }
}

const logout = async () => {
  try {
    await http.post('/api/auth/logout')
    auth.setAuthed(false)
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    // 即使退出API失败，也清除本地状态
    auth.setAuthed(false)
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
/* 头部样式 */
.app-header {
  background: var(--card-bg);
  border-bottom: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 var(--space-lg);
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.brand {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-right: var(--space-xl);
  white-space: nowrap;
}

.nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav .el-menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 0 var(--space-md);
  margin: 0 var(--space-xs);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  color: var(--text-primary) !important;
  background: transparent !important;
}

.nav .el-menu-item:hover {
  background: var(--bg-secondary) !important;
  color: var(--primary) !important;
}

.nav .el-menu-item.is-active {
  background: var(--primary) !important;
  color: white !important;
}

.nav .el-menu-item span {
  color: inherit !important;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.login-btn {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--text-primary);
  font-weight: 500;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.user-dropdown:hover {
  background: var(--bg-secondary);
}

/* 主要内容区域 */
.main-content {
  background: var(--bg);
  padding: 0;
  overflow: auto;
}

.content-wrapper {
  min-height: calc(100vh - 64px);
  padding: var(--space-lg);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .header-content {
    padding: 0 var(--space-md);
  }
  
  .nav .el-menu-item span {
    display: none;
  }
  
  .nav .el-menu-item {
    padding: 0 var(--space-sm);
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 var(--space-sm);
  }
  
  .brand {
    font-size: 16px;
    margin-right: var(--space-md);
  }
  
  .nav {
    display: none;
  }
  
  .content-wrapper {
    padding: var(--space-md);
  }
}
</style>

