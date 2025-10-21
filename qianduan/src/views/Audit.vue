<template>
  <div class="audit-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">
            <el-icon class="title-icon"><DocumentChecked /></el-icon>
            审核队列
          </h1>
          <p class="page-subtitle">AI 生成的候选回复会进入此处等待审核，支持编辑后发送或直接拒绝</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Refresh" @click="load" :loading="loading">
            刷新
          </el-button>
        </div>
      </div>
    </div>

    <!-- 审核项列表 -->
    <div v-if="items.length === 0" class="empty-state">
      <el-empty description="暂无待审核项目" />
    </div>

    <div v-else class="audit-list">
      <el-card v-for="item in items" :key="item.id" class="audit-card" style="margin-bottom: 16px;">
        <template #header>
          <div class="card-header">
            <span>审核项 #{{ item.id }}</span>
            <el-tag :type="getStatusType(item.status)">{{ getStatusText(item.status) }}</el-tag>
          </div>
        </template>

        <!-- 消息详情 -->
        <div v-if="item.message" class="message-section">
          <h4>客户消息</h4>
          <div class="message-info">
            <p><strong>客户ID:</strong> {{ item.message.customer_id }}</p>
            <p><strong>时间:</strong> {{ formatDate(item.message.created_at) }}</p>
            <p><strong>内容:</strong></p>
            <div class="message-content">{{ item.message.content }}</div>
          </div>
        </div>

        <!-- AI回复详情 -->
        <div v-if="item.ai_reply" class="ai-reply-section">
          <h4>AI建议回复</h4>
          <div class="ai-reply-info">
            <p><strong>模型:</strong> {{ item.ai_reply.model }}</p>
            <p><strong>置信度:</strong> {{ (item.ai_reply.confidence * 100).toFixed(1) }}%</p>
            <p><strong>回复内容:</strong></p>
            <el-input
              v-model="item.edited_reply"
              type="textarea"
              :rows="3"
              placeholder="可编辑AI回复内容"
              :default-value="item.ai_reply.reply"
            />
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="card-actions">
          <!-- 待审核状态：显示通过、拒绝、查看上下文 -->
          <template v-if="item.status === 'pending'">
            <el-button type="success" @click="approveItem(item)">通过并发送</el-button>
            <el-button type="danger" @click="rejectItem(item)">拒绝</el-button>
            <el-button type="info" @click="showContext(item)">查看上下文</el-button>
          </template>
          
          <!-- 已通过状态：显示撤回、查看上下文 -->
          <template v-else-if="item.status === 'approved'">
            <el-button type="warning" @click="recallItem(item)">撤回</el-button>
            <el-button type="info" @click="showContext(item)">查看上下文</el-button>
          </template>
          
          <!-- 已拒绝状态：显示重新审核、查看上下文 -->
          <template v-else-if="item.status === 'rejected'">
            <el-button type="primary" @click="reviewAgainItem(item)">重新审核</el-button>
            <el-button type="info" @click="showContext(item)">查看上下文</el-button>
          </template>
          
          <!-- 其他状态：只显示查看上下文 -->
          <template v-else>
            <el-button type="info" @click="showContext(item)">查看上下文</el-button>
          </template>
        </div>
      </el-card>
    </div>

    <!-- 上下文对话框 -->
    <el-dialog title="历史消息上下文" v-model="contextDialogVisible" width="800px">
      <div v-if="contextData">
        <h4>当前消息</h4>
        <div class="context-message">{{ contextData.current_message.content }}</div>
        
        <h4 style="margin-top: 20px;">历史消息</h4>
        <div v-if="contextData.context_messages.length === 0" class="no-context">
          暂无历史消息
        </div>
        <div v-else>
          <el-card v-for="msg in contextData.context_messages" :key="msg.id" style="margin-bottom: 8px;">
            <div class="context-item">
              <div class="context-time">{{ formatDate(msg.created_at) }}</div>
              <div class="context-content">{{ msg.content }}</div>
              <el-tag :type="getStatusType(msg.status)" size="small">{{ getStatusText(msg.status) }}</el-tag>
            </div>
          </el-card>
        </div>
      </div>
      <template #footer>
        <el-button @click="contextDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import http from '../api/http'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentChecked, Refresh } from '@element-plus/icons-vue'

const items = ref<any[]>([])
const contextDialogVisible = ref(false)
const contextData = ref<any>(null)

const load = async () => {
  try {
    const r = await http.get('/api/audit')
    items.value = r.data.map((item: any) => ({
      ...item,
      edited_reply: item.ai_reply?.reply || ''  // 初始化编辑回复
    }))
  } catch (error) {
    ElMessage.error('加载审核队列失败')
  }
}

const approveItem = async (item: any) => {
  try {
    await ElMessageBox.confirm('确定要通过并发送这条回复吗？', '确认操作', {
      type: 'warning'
    })
    
    await http.post('/api/audit/approve', { 
      id: item.id, 
      title_kw: '千牛',
      edited_reply: item.edited_reply || item.ai_reply?.reply
    })
    ElMessage.success('已通过并发送')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const rejectItem = async (item: any) => {
  try {
    await ElMessageBox.confirm('确定要拒绝这条回复吗？', '确认操作', {
      type: 'warning'
    })
    
    await http.post('/api/audit/reject', { id: item.id })
    ElMessage.success('已拒绝')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const recallItem = async (item: any) => {
  try {
    await ElMessageBox.confirm('确定要撤回这条已通过的回复吗？', '确认撤回', {
      type: 'warning'
    })
    
    await http.post('/api/audit/recall', { id: item.id })
    ElMessage.success('已撤回')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('撤回失败')
    }
  }
}

const reviewAgainItem = async (item: any) => {
  try {
    await ElMessageBox.confirm('确定要重新审核这条已拒绝的回复吗？', '确认重新审核', {
      type: 'info'
    })
    
    await http.post('/api/audit/review_again', { id: item.id })
    ElMessage.success('已重新提交审核')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新审核失败')
    }
  }
}

const showContext = async (item: any) => {
  try {
    const res = await http.get(`/api/audit/${item.id}/context`)
    contextData.value = res.data
    contextDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取上下文失败')
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'new': 'info',
    'answered': 'success',
    'queued': 'warning',
    'review': 'primary'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已拒绝',
    'new': '新消息',
    'answered': '已回复',
    'queued': '排队中',
    'review': '审核中'
  }
  return statusMap[status] || status
}

load()
</script>

<style scoped>
/* 页面整体样式 */
.audit-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  color: white;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.title-icon {
  margin-right: 12px;
  font-size: 32px;
}

.page-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.audit-list {
  max-width: 1000px;
}

.audit-card {
  border: 1px solid #e4e7ed;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-section, .ai-reply-section {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.message-section h4, .ai-reply-section h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.message-info p, .ai-reply-info p {
  margin: 4px 0;
  font-size: 13px;
}

.message-content {
  background: white;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  margin-top: 4px;
  white-space: pre-wrap;
  word-break: break-word;
}

.card-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.context-message {
  background: #f0f9ff;
  padding: 12px;
  border-radius: 4px;
  border-left: 4px solid #409eff;
  margin-bottom: 16px;
}

.context-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.context-time {
  font-size: 12px;
  color: #909399;
}

.context-content {
  font-size: 14px;
  line-height: 1.4;
}

.no-context {
  text-align: center;
  color: #909399;
  padding: 20px;
}
</style>

