<template>
  <div class="chat-area">
    <div class="messages-container" ref="messagesContainer">
      <div class="welcome-message" v-if="messages.length === 0">
        <div class="welcome-content">
          <el-icon class="welcome-icon"><ChatDotRound /></el-icon>
          <h3>欢迎使用江苏旅游知识库</h3>
          <p>您可以询问关于江苏各地的旅游信息，例如：</p>
          <div class="example-questions">
            <el-tag 
              v-for="example in exampleQuestions" 
              :key="example"
              class="example-tag"
              @click="$emit('send-example', example)"
              type="info"
              effect="plain"
            >
              {{ example }}
            </el-tag>
          </div>
        </div>
      </div>

      <div 
        v-for="message in messages" 
        :key="message.id"
        :class="['message', message.type]"
      >
        <div class="message-content">
          <div class="message-header">
            <div class="message-avatar">
              <el-icon v-if="message.type === 'user'">
                <User />
              </el-icon>
              <el-icon v-else>
                <ChatDotRound />
              </el-icon>
            </div>
            <div class="message-info">
              <span class="message-sender">
                {{ message.type === 'user' ? '您' : 'AI助手' }}
              </span>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>
          </div>
          
          <div class="message-body">
            <div 
              v-if="message.type === 'user'"
              class="user-message"
            >
              {{ message.content }}
            </div>
            <div 
              v-else
              class="assistant-message"
            >
              <div 
                v-html="parseMarkdown(message.content)"
                class="message-text"
              ></div>
              
              <!-- 地图组件 - 当AI回答完成且涉及路线规划时显示 -->
              <MapComponent 
                v-if="shouldShowMap(message.content) && !message.loading && message.content"
                :key="message.id"
                :ai-content="message.content"
              />
              
              <!-- 加载状态 -->
              <div v-if="message.loading" class="loading-indicator">
                <el-icon class="rotating"><Loading /></el-icon>
                <span>AI正在思考中...</span>
              </div>
              
              <!-- 来源信息 -->
              <div v-if="message.sources && message.sources.length > 0 && showSources" class="sources-section">
                <el-collapse>
                  <el-collapse-item>
                    <template #title>
                      <div class="sources-title">
                        <el-icon><Document /></el-icon>
                        相关来源 ({{ message.sources.length }})
                      </div>
                    </template>
                    <div class="sources-content">
                      <div 
                        v-for="(source, index) in message.sources" 
                        :key="index"
                        class="source-item"
                      >
                        <div class="source-header">
                          <el-tag size="small" type="primary">{{ source.region }}</el-tag>
                          <span class="source-filename">{{ source.filename }}</span>
                        </div>
                        <div class="source-content">
                          {{ source.content_preview }}
                        </div>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误消息 -->
      <div v-if="error" class="error-message">
        <el-alert
          :title="error"
          type="error"
          show-icon
          :closable="false"
        />
      </div>
    </div>

    <!-- 快速跳转按钮 -->
    <div class="scroll-actions">
      <el-button 
        v-if="showScrollToBottom"
        type="primary" 
        :icon="ArrowDown" 
        circle 
        size="small"
        @click="scrollToBottom"
        class="scroll-button"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import { ChatDotRound, User, Loading, Document, ArrowDown } from '@element-plus/icons-vue'
import { parseMarkdown, formatTime } from '@/utils/helpers'
import MapComponent from '@/components/MapComponent.vue'

// 定义props
const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  showSources: {
    type: Boolean,
    default: true
  },
  error: {
    type: String,
    default: ''
  }
})

// 定义emits
const emit = defineEmits(['send-example'])

// 响应式数据
const messagesContainer = ref(null)
const showScrollToBottom = ref(false)

// 示例问题
const exampleQuestions = [
  '苏州有哪些著名景点？',
  '南京的美食有什么推荐？',
  '扬州三日游路线规划',
  '无锡的交通怎么样？',
  '同里古镇有什么特色？'
]

// 判断是否显示地图
const shouldShowMap = (content) => {
  if (!content) return false
  
  // 检查回答中是否包含路线规划相关关键词
  const routeKeywords = [
    '路线', '路径', '怎么去', '怎么走', '交通', 
    '自驾', '导航', '距离', '开车', '乘车',
    '线路', '行程', '从.*到.*', '规划'
  ]
  
  return routeKeywords.some(keyword => 
    content.includes(keyword) || 
    new RegExp(keyword).test(content)
  )
}

// 滚动到底部
const scrollToBottom = (smooth = true) => {
  nextTick(() => {
    if (messagesContainer.value) {
      const container = messagesContainer.value
      container.scrollTo({
        top: container.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
      })
    }
  })
}

// 检查是否需要显示滚动按钮
const checkScrollButton = () => {
  if (!messagesContainer.value) return
  
  const container = messagesContainer.value
  const isNearBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 100
  showScrollToBottom.value = !isNearBottom && props.messages.length > 0
}

// 监听消息变化，自动滚动到底部
watch(() => props.messages, (newMessages) => {
  console.log('ChatArea: 消息列表变化', newMessages.length, newMessages)
  // 强制重新渲染，确保内容更新
  nextTick(() => {
    console.log('ChatArea: 强制更新完成')
    scrollToBottom()
  })
}, { deep: true, immediate: true })

// 监听滚动事件
onMounted(() => {
  console.log('ChatArea: 组件已挂载')
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', checkScrollButton)
  }
})
</script>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%;
  min-height: 0;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: #fafafa;
}

.welcome-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
}

.welcome-content {
  text-align: center;
  max-width: 600px;
}

.welcome-icon {
  font-size: 4rem;
  color: #409eff;
  margin-bottom: 1rem;
}

.welcome-content h3 {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.welcome-content p {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 1rem;
}

.example-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
}

.example-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.example-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.message {
  margin-bottom: 2rem;
}

.message-content {
  max-width: 800px;
}

.message.user .message-content {
  margin-left: auto;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 0.75rem;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.message.user .message-avatar {
  background: #409eff;
  color: white;
}

.message.assistant .message-avatar {
  background: #67c23a;
  color: white;
}

.message-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.message-sender {
  font-weight: 500;
  font-size: 0.9rem;
  color: #333;
}

.message-time {
  font-size: 0.8rem;
  color: #999;
}

.message-body {
  margin-left: 48px;
}

.user-message {
  background: #409eff;
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 0 1rem 1rem 1rem;
  display: inline-block;
  max-width: 80%;
  word-wrap: break-word;
  line-height: 1.5;
}

.assistant-message {
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 1rem 0 1rem 1rem;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-text {
  line-height: 1.6;
  color: #333;
}

.message-text :deep(p) {
  margin-bottom: 0.5rem;
}

.message-text :deep(strong) {
  font-weight: 600;
  color: #333;
}

.message-text :deep(code) {
  background: #f5f5f5;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.sources-section {
  margin-top: 1rem;
  border-top: 1px solid #f0f0f0;
  padding-top: 1rem;
}

.sources-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.sources-content {
  margin-top: 0.5rem;
}

.source-item {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.source-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.source-filename {
  font-size: 0.8rem;
  color: #666;
  flex: 1;
}

.source-content {
  font-size: 0.85rem;
  color: #555;
  line-height: 1.4;
}

.error-message {
  margin: 1rem;
}

.scroll-actions {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
}

.scroll-button {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
</style>