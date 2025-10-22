<template>
  <div class="shops-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="title">
            <el-icon><Shop /></el-icon>
            店铺配置
          </h1>
          <p class="subtitle">
            管理千牛监控与AI参数，配置OCR区域和未读阈值
          </p>
        </div>
        <div class="header-actions">
          <el-button @click="load" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button type="primary" @click="addNewShop">
            <el-icon><Plus /></el-icon>
            新增店铺配置
          </el-button>
        </div>
      </div>
    </div>

    <!-- 使用引导 -->
    <el-alert
      title="使用引导"
      type="info"
      :closable="false"
      show-icon
      class="guide-alert"
    >
      <template #default>
        <div class="guide-content">
          <p><strong>配置步骤：</strong></p>
          <ol>
            <li>点击"新增店铺配置"按钮</li>
            <li>填写店铺名称和千牛窗口标题</li>
            <li>设置OCR区域坐标（建议覆盖聊天区域）</li>
            <li>配置未读消息阈值</li>
            <li>保存配置并启动监控</li>
          </ol>
        </div>
      </template>
    </el-alert>

    <!-- 店铺列表 -->
    <div class="shops-list">
      <div class="list-header">
        <h3>店铺列表</h3>
        <el-tag type="info" size="small">{{ shops.length }} 个店铺</el-tag>
      </div>
      
      <el-table 
        :data="shops" 
        v-loading="loading"
        empty-text="暂无店铺配置"
        class="shops-table"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="店铺名称" min-width="150">
          <template #default="{ row }">
            <div class="shop-name">
              <el-icon><Shop /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="qianniu_title" label="千牛标题" min-width="200" />
        <el-table-column label="OCR区域" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" v-if="row.ocr_region">
              {{ row.ocr_region.join(', ') }}
            </el-tag>
            <el-tag size="small" type="info" v-else>未配置</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="阈值" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="success" v-if="row.unread_threshold">
              {{ row.unread_threshold }}
            </el-tag>
            <el-tag size="small" type="info" v-else>未设置</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="editShop(row)" :loading="false">
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteShop(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑店铺对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingShop ? '编辑店铺配置' : '新增店铺配置'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="120px" class="shop-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="店铺名称" required>
              <el-input v-model="formData.name" placeholder="请输入店铺名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="千牛标题" required>
              <el-input v-model="formData.qianniu_title" placeholder="请输入千牛窗口标题" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">OCR配置</el-divider>
        
        <el-form-item label="选择模板">
          <el-select v-model="selectedTemplate" @change="applyTemplate" placeholder="选择OCR模板" style="width: 100%;">
            <el-option v-for="template in templates" :key="template.name" :label="template.name" :value="template" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="OCR区域" required>
          <el-input v-model="formData.ocr_region_text" placeholder="格式: x,y,w,h (例如: 800,200,600,300)" />
          <div class="form-tip">建议覆盖聊天区域，格式为：左上角x,左上角y,宽度,高度</div>
        </el-form-item>
        
        <el-form-item label="未读阈值" required>
          <el-input-number v-model="formData.unread_threshold" :min="0" :max="1" :step="0.01" :precision="2" />
          <div class="form-tip">检测到红点比例≥阈值视为有未读，建议0.02~0.06</div>
        </el-form-item>

        <el-divider content-position="left">AI配置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="AI模型">
              <el-select v-model="formData.ai_model" style="width: 100%;">
                <el-option label="占位(stub)" value="stub" />
                <el-option label="通义千问(qwen)" value="qwen" />
                <el-option label="文心一言(ernie)" value="ernie" />
                <el-option label="OpenAI(openai)" value="openai" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="自动模式">
              <el-switch v-model="formData.auto_mode" />
              <div class="form-tip">开启后高置信度将直接发送</div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">高级配置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="黑名单">
              <el-input 
                v-model="formData.blacklist_text" 
                type="textarea" 
                :rows="3" 
                placeholder="一行一个客户ID"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="白名单">
              <el-input 
                v-model="formData.whitelist_text" 
                type="textarea" 
                :rows="3" 
                placeholder="一行一个客户ID"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="营业时间">
              <el-time-picker
                v-model="formData.business_hours"
                is-range
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="回复延迟">
              <el-input-number v-model="formData.reply_delay" :min="1" :max="5" style="width: 100%;" />
              <div class="form-tip">随机延迟1-5秒，避免被识别为机器人</div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveShop" :loading="saving">
          {{ editingShop ? '更新' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import http from '../api/http'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Shop, Refresh, Plus, WarningFilled 
} from '@element-plus/icons-vue'

const shops = ref<any[]>([])
const templates = ref<any[]>([])
const selectedTemplate = ref<any>(null)
const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const editingShop = ref<any>(null)

const formData = reactive({
  name: '',
  qianniu_title: '',
  ocr_region_text: '800,200,600,300',
  unread_threshold: 0.02,
  ai_model: 'stub',
  auto_mode: false,
  blacklist_text: '',
  whitelist_text: '',
  business_hours: null,
  reply_delay: 2
})

const load = async () => {
  loading.value = true
  try {
    const res = await http.get('/api/shops')
    shops.value = res.data
  } catch (error: any) {
    console.error('加载店铺列表失败:', error)
    if (error.response?.status === 401) {
      ElMessage.warning('请先登录')
      // 可以在这里跳转到登录页面
    } else if (error.response?.status === 500) {
      ElMessage.error('服务器内部错误，请检查后端服务')
    } else {
      ElMessage.error('加载店铺列表失败')
    }
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  try {
    const res = await http.get('/api/shops/ocr_templates')
    templates.value = res.data
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

const applyTemplate = (template: any) => {
  if (template) {
    formData.ocr_region_text = template.ocr_region.join(',')
    formData.unread_threshold = template.unread_threshold
    ElMessage.success(`已应用模板: ${template.name}`)
  }
}

const addNewShop = () => {
  editingShop.value = null
  resetForm()
  showAddDialog.value = true
}

const editShop = (shop: any) => {
  console.log('编辑店铺被点击:', shop)
  
  try {
    // 设置编辑状态
    editingShop.value = shop
    
    // 填充表单数据
    formData.name = shop.name || ''
    formData.qianniu_title = shop.qianniu_title || ''
    
    // 安全处理ocr_region字段
    if (shop.ocr_region && Array.isArray(shop.ocr_region)) {
      formData.ocr_region_text = shop.ocr_region.join(',')
    } else if (shop.ocr_region && typeof shop.ocr_region === 'string') {
      formData.ocr_region_text = shop.ocr_region
    } else {
      formData.ocr_region_text = '800,200,600,300'
    }
    
    formData.unread_threshold = shop.unread_threshold || 0.02
    formData.ai_model = shop.ai_model || 'stub'
    formData.auto_mode = shop.auto_mode || false
    
    // 安全处理blacklist字段
    if (shop.blacklist && Array.isArray(shop.blacklist)) {
      formData.blacklist_text = shop.blacklist.join('\n')
    } else {
      formData.blacklist_text = ''
    }
    
    // 安全处理whitelist字段
    if (shop.whitelist && Array.isArray(shop.whitelist)) {
      formData.whitelist_text = shop.whitelist.join('\n')
    } else {
      formData.whitelist_text = ''
    }
    
    formData.business_hours = shop.business_hours ? [shop.business_hours.start, shop.business_hours.end] : null as any
    formData.reply_delay = shop.reply_delay || 2
    
    console.log('表单数据已填充:', formData)
    
    // 强制显示对话框
    showAddDialog.value = false
    setTimeout(() => {
      showAddDialog.value = true
      console.log('对话框已显示:', showAddDialog.value)
    }, 100)
    
  } catch (error) {
    console.error('编辑店铺时出错:', error)
    ElMessage.error('编辑店铺时出错: ' + error.message)
  }
}

const deleteShop = async (shop: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除店铺"${shop.name}"吗？

⚠️ 警告：删除店铺将同时删除以下关联数据：
• 该店铺的所有消息记录
• 该店铺的知识库条目
• 该店铺的回复模板
• 该店铺用户的店铺关联将被清除

此操作不可恢复，请谨慎操作！`,
      '确认删除店铺',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
        customClass: 'delete-confirm-dialog'
      }
    )
    
    await http.delete(`/api/shops/${shop.id}`)
    ElMessage.success('店铺删除成功')
    load()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveShop = async () => {
  if (!formData.name.trim() || !formData.qianniu_title.trim()) {
    ElMessage.warning('请填写店铺名称和千牛标题')
    return
  }

  saving.value = true
  try {
    const arr = formData.ocr_region_text.split(',').map(x => parseInt(x.trim(), 10)).filter(x => !Number.isNaN(x))
    
    // 处理黑白名单
    const blacklist = formData.blacklist_text.split('\n').map(x => x.trim()).filter(x => x)
    const whitelist = formData.whitelist_text.split('\n').map(x => x.trim()).filter(x => x)
    
    // 处理营业时间
    let business_hours: any = null
    if (formData.business_hours && Array.isArray(formData.business_hours) && formData.business_hours.length === 2) {
      business_hours = {
        start: formData.business_hours[0],
        end: formData.business_hours[1]
      }
    }
    
    const data = {
      name: formData.name,
      qianniu_title: formData.qianniu_title,
      ocr_region: arr,
      unread_threshold: formData.unread_threshold,
      ai_model: formData.ai_model,
      auto_mode: formData.auto_mode,
      blacklist: blacklist,
      whitelist: whitelist,
      business_hours: business_hours,
      reply_delay: formData.reply_delay,
    }

    if (editingShop.value) {
      await http.put(`/api/shops/${editingShop.value.id}`, data)
      ElMessage.success('店铺更新成功')
    } else {
      await http.post('/api/shops', data)
      ElMessage.success('店铺创建成功')
    }
    
    showAddDialog.value = false
    resetForm()
    load()
  } catch (error: any) {
    console.error('保存店铺失败:', error)
    
    // 根据操作类型显示具体的错误信息
    const operation = editingShop.value ? '更新' : '新增'
    let errorMessage = `${operation}店铺失败`
    
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status
      const data = error.response.data
      
      if (status === 400) {
        errorMessage = `${operation}店铺失败：请求参数错误`
        if (data?.error === 'name_required') {
          errorMessage = `${operation}店铺失败：店铺名称不能为空`
        }
      } else if (status === 401) {
        errorMessage = `${operation}店铺失败：请先登录`
      } else if (status === 403) {
        errorMessage = `${operation}店铺失败：权限不足`
      } else if (status === 500) {
        errorMessage = `${operation}店铺失败：服务器内部错误`
        if (data?.detail) {
          errorMessage = `${operation}店铺失败：${data.detail}`
        }
      } else {
        errorMessage = `${operation}店铺失败：服务器错误 (${status})`
      }
    } else if (error.request) {
      // 请求发送了但没有收到响应
      errorMessage = `${operation}店铺失败：网络连接失败`
    } else {
      // 其他错误
      errorMessage = `${operation}店铺失败：${error.message || '未知错误'}`
    }
    
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  editingShop.value = null
  formData.name = ''
  formData.qianniu_title = ''
  formData.ocr_region_text = '800,200,600,300'
  formData.unread_threshold = 0.02
  formData.ai_model = 'stub'
  formData.auto_mode = false
  formData.blacklist_text = ''
  formData.whitelist_text = ''
  formData.business_hours = null
  formData.reply_delay = 2
}

// 备用编辑处理函数
const handleEditClick = (shop: any) => {
  console.log('备用编辑处理函数被调用:', shop)
  editShop(shop)
}

// 强制绑定编辑按钮事件
const bindEditButtons = () => {
  setTimeout(() => {
    const editButtons = document.querySelectorAll('button')
    editButtons.forEach(button => {
      if (button.textContent?.includes('编辑')) {
        // 移除现有事件
        button.onclick = null
        // 添加新事件
        button.addEventListener('click', function(event) {
          event.preventDefault()
          event.stopPropagation()
          console.log('编辑按钮被点击 (备用处理)')
          const row = button.closest('tr')
          if (row) {
            const cells = row.querySelectorAll('td')
            const shopData = {
              id: parseInt(cells[0]?.textContent?.trim() || '0'),
              name: cells[1]?.textContent?.trim().replace('● ', '') || '',
              qianniu_title: cells[2]?.textContent?.trim() || '',
              ocr_region: [800, 200, 600, 300], // 默认OCR区域
              unread_threshold: 0.02,
              ai_model: 'stub',
              auto_mode: false,
              blacklist: [], // 确保是数组
              whitelist: [], // 确保是数组
              business_hours: null,
              reply_delay: 2
            }
            console.log('从表格提取的店铺数据:', shopData)
            editShop(shopData)
          }
        })
        console.log('编辑按钮事件已重新绑定')
      }
    })
  }, 1000)
}

// 初始化
load()
loadTemplates()
bindEditButtons()
</script>

<style scoped>
/* 页面布局 */
.shops-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* 页面头部 */
.page-header {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin-bottom: var(--space-lg);
  border: 1px solid var(--border-light);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--space-lg);
  gap: var(--space-lg);
}

.title-section {
  flex: 1;
}

.title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 var(--space-sm);
  color: var(--text-primary);
}

.subtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

/* 使用引导 */
.guide-alert {
  margin-bottom: var(--space-lg);
  border-radius: var(--radius);
}

.guide-content {
  line-height: 1.6;
}

.guide-content p {
  margin: 0 0 var(--space-sm);
  font-weight: 600;
}

.guide-content ol {
  margin: var(--space-sm) 0 0;
  padding-left: var(--space-lg);
}

.guide-content li {
  margin-bottom: var(--space-xs);
}

/* 店铺列表 */
.shops-list {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-secondary);
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.shops-table {
  border: none;
}

.shop-name {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-weight: 500;
}

/* 表单样式 */
.shop-form {
  max-width: none;
}

.form-tip {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: var(--space-xs);
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .header-actions .el-button {
    flex: 1;
  }
  
  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-xl);
  color: var(--text-muted);
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
  color: var(--text-muted);
}

/* 删除确认对话框样式 */
:deep(.delete-confirm-dialog) {
  .el-message-box__content {
    white-space: pre-line;
    line-height: 1.6;
  }
  
  .el-message-box__title {
    color: #e6a23c;
    font-weight: 600;
  }
  
  .el-button--primary {
    background-color: #f56c6c;
    border-color: #f56c6c;
  }
  
  .el-button--primary:hover {
    background-color: #f78989;
    border-color: #f78989;
  }
}
</style>

