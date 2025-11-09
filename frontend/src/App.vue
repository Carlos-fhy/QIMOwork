<template>
  <div class="app">
    <Header />
    
    <div class="main-container">
      <Sidebar 
        @region-change="handleRegionChange"
        @mode-change="handleModeChange"
        @topk-change="handleTopKChange"
        @show-sources-change="handleShowSourcesChange"
        @stream-mode-change="handleStreamModeChange"
      />
      
      <div class="content-area">
        <ChatArea 
          :messages="messages"
          :show-sources="settings.showSources"
          :error="error"
          @send-example="handleSendMessage"
        />
        
        <InputBox 
          :disabled="loading"
          :loading="loading"
          :mode="settings.mode"
          @send="handleSendMessage"
          @clear="handleClearHistory"
        />
      </div>
    </div>

    <!-- 知识库构建对话框 -->
    <el-dialog 
      v-model="showBuildDialog"
      title="构建知识库"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="build-dialog-content">
        <p>检测到知识库尚未构建或为空，是否立即构建？</p>
        <p class="build-warning">
          <el-icon><Warning /></el-icon>
          构建过程可能需要几分钟时间，请耐心等待。
        </p>
      </div>
      <template #footer>
        <el-button @click="showBuildDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="buildKnowledgeBase"
          :loading="building"
        >
          {{ building ? '构建中' : '开始构建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning } from '@element-plus/icons-vue'

import Header from '@/components/Header.vue'
import Sidebar from '@/components/Sidebar.vue'
import ChatArea from '@/components/ChatArea.vue'
import InputBox from '@/components/InputBox.vue'
import { chatApi, createSSEConnection } from '@/api'
import { generateId } from '@/utils/helpers'

// 响应式数据
const messages = ref([])
const loading = ref(false)
const error = ref('')
const showBuildDialog = ref(false)
const building = ref(false)
const currentSSE = ref(null)

// 设置
const settings = reactive({
  region: 'all',
  mode: 'qa',
  topK: 3,
  showSources: true,
  streamMode: true  // 重新启用流式模式
})

// 事件处理函数
const handleRegionChange = (region) => {
  settings.region = region
}

const handleModeChange = (mode) => {
  settings.mode = mode
}

const handleTopKChange = (k) => {
  settings.topK = k
}

const handleShowSourcesChange = (show) => {
  settings.showSources = show
}

const handleStreamModeChange = (stream) => {
  settings.streamMode = stream
}

// 发送消息
const handleSendMessage = async (question) => {
  if (!question.trim() || loading.value) return
  
  console.log('=== 开始发送消息 ===')
  console.log('问题:', question)
  console.log('当前设置:', settings)
  
  // 清除之前的错误
  error.value = ''
  
  // 添加用户消息
  const userMessage = {
    id: generateId(),
    type: 'user',
    content: question,
    timestamp: Date.now()
  }
  messages.value.push(userMessage)
  console.log('用户消息已添加:', userMessage)
  
  // 添加AI消息占位符
  const assistantMessage = {
    id: generateId(),
    type: 'assistant',
    content: '',
    timestamp: Date.now(),
    loading: true,
    sources: []
  }
  messages.value.push(assistantMessage)
  console.log('AI消息占位符已添加:', assistantMessage)
  console.log('当前消息列表长度:', messages.value.length)
  
  loading.value = true
  
  try {
    if (settings.streamMode) {
      console.log('使用流式模式')
      // 流式输出
      await handleStreamResponse(question, assistantMessage)
    } else {
      console.log('使用普通模式')
      // 一次性输出
      await handleNormalResponse(question, assistantMessage)
    }
  } catch (err) {
    console.error('Send message error:', err)
    error.value = '发送消息失败，请稍后重试'
    assistantMessage.loading = false
    assistantMessage.content = '抱歉，发生了错误，请稍后重试。'
  }
  
  loading.value = false
  console.log('=== 消息发送完成 ===')
  console.log('最终消息列表:', messages.value)
}

// 处理流式响应
const handleStreamResponse = async (question, assistantMessage) => {
  return new Promise((resolve, reject) => {
    const sse = createSSEConnection(question, settings.region, settings.topK)
    currentSSE.value = sse
    
    sse.onopen = () => {
      console.log('SSE连接已打开')
      assistantMessage.loading = true
    }
    
    sse.onmessage = (event) => {
      console.log('SSE received:', event.data)
      
      if (event.data === '[DONE]') {
        console.log('SSE传输完成')
        sse.close()
        assistantMessage.loading = false
        resolve()
        return
      }
      
      // 忽略空数据
      if (!event.data || event.data.trim() === '') {
        return
      }
      
      try {
        const data = JSON.parse(event.data)
        console.log('Parsed SSE data:', data)
        
        if (data.content) {
          assistantMessage.content += data.content
          console.log('Updated message content length:', assistantMessage.content.length)
          
          // 强制触发更新
          const currentMessages = [...messages.value]
          messages.value = []
          nextTick(() => {
            messages.value = currentMessages
          })
        }
        
        if (data.done) {
          console.log('Stream完成，设置sources:', data.sources)
          assistantMessage.sources = data.sources || []
          assistantMessage.loading = false
          sse.close()
          resolve()
        }
      } catch (err) {
        console.error('Parse SSE data error:', err)
        console.error('Raw event data:', event.data)
      }
    }
    
    sse.onerror = (event) => {
      console.error('SSE error:', event)
      sse.close()
      assistantMessage.loading = false
      assistantMessage.content += '\n\n[连接错误，请刷新页面重试]'
      reject(new Error('SSE连接错误'))
    }
  })
}

// 处理普通响应
const handleNormalResponse = async (question, assistantMessage) => {
  try {
    console.log('开始调用普通API:', question)
    const response = await chatApi.chat(question, settings.region, settings.topK)
    console.log('API响应:', response)
    
    if (response.success) {
      console.log('API调用成功, 回答:', response.answer)
      
      // 更新消息内容
      assistantMessage.content = response.answer
      assistantMessage.sources = response.sources || []
      assistantMessage.loading = false
      
      console.log('更新后的消息:', assistantMessage)
      
      // 强制触发响应式更新 - 重建数组
      const currentMessages = [...messages.value]
      messages.value = []
      await nextTick()
      messages.value = currentMessages
      console.log('强制更新消息数组完成')
      
    } else {
      console.log('API调用失败:', response)
      assistantMessage.content = response.answer || '抱歉，我无法回答您的问题。'
      assistantMessage.loading = false
    }
    console.log('消息处理完成:', assistantMessage)
  } catch (error) {
    console.error('处理普通响应时出错:', error)
    assistantMessage.content = '发生错误，请稍后重试。'
    assistantMessage.loading = false
  }
}

// 清空历史记录
const handleClearHistory = () => {
  ElMessageBox.confirm(
    '确定要清空所有对话历史吗？',
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    messages.value = []
    ElMessage.success('对话历史已清空')
  }).catch(() => {
    // 取消操作
  })
}

// 构建知识库
const buildKnowledgeBase = async () => {
  building.value = true
  
  try {
    const response = await chatApi.buildKnowledgeBase(false)
    
    if (response.success) {
      ElMessage.success(`知识库构建成功！共处理 ${response.document_count} 个文档`)
      showBuildDialog.value = false
    } else {
      ElMessage.error(`知识库构建失败：${response.error}`)
    }
  } catch (err) {
    console.error('Build knowledge base error:', err)
    ElMessage.error('构建知识库时发生错误')
  }
  
  building.value = false
}

// 检查系统状态
const checkSystemStatus = async () => {
  try {
    const response = await chatApi.healthCheck()
    
    if (response.status === 'healthy') {
      if (response.vector_db && response.vector_db.document_count === 0) {
        // 知识库为空，提示构建
        showBuildDialog.value = true
      }
    } else {
      ElMessage.warning('后端服务状态异常，请检查服务是否正常运行')
    }
  } catch (err) {
    console.error('Health check error:', err)
    ElMessage.error('无法连接到后端服务，请检查网络连接')
  }
}

// 组件挂载时检查系统状态
onMounted(() => {
  checkSystemStatus()
})

// 组件卸载时清理SSE连接
const cleanup = () => {
  if (currentSSE.value) {
    currentSSE.value.close()
    currentSSE.value = null
  }
}

// 监听页面卸载事件
window.addEventListener('beforeunload', cleanup)
</script>

<style scoped>
.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.main-container {
  flex: 1;
  display: flex;
  min-height: 0;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.build-dialog-content {
  text-align: center;
  padding: 1rem 0;
}

.build-dialog-content p {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.build-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #e6a23c;
  font-size: 0.9rem;
}
</style>