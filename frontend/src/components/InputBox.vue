<template>
  <div class="input-box">
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="3"
        :placeholder="placeholder"
        resize="none"
        :disabled="disabled"
        @keydown.enter.exact.prevent="handleSend"
        @keydown.ctrl.enter.exact="handleNewLine"
        class="message-input"
      />
      <div class="input-actions">
        <div class="input-tips">
          <span class="tip">Enter 发送 | Ctrl+Enter 换行</span>
        </div>
        <div class="action-buttons">
          <el-button 
            type="info" 
            size="small" 
            :disabled="!inputText.trim() && !disabled"
            @click="handleClear"
          >
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            :disabled="!inputText.trim() || disabled"
            :loading="loading"
            @click="handleSend"
          >
            <el-icon><Promotion /></el-icon>
            {{ loading ? '发送中' : '发送' }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Delete, Promotion } from '@element-plus/icons-vue'

// 定义props
const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'qa'
  }
})

// 定义emits
const emit = defineEmits(['send', 'clear'])

// 响应式数据
const inputText = ref('')

// 计算属性
const placeholder = computed(() => {
  if (props.mode === 'plan') {
    return '请描述您的旅游需求，如："想去苏州玩3天，求推荐路线"'
  }
  return '请输入您的问题，如："苏州有哪些著名景点？"'
})

// 事件处理
const handleSend = () => {
  if (!inputText.value.trim() || props.disabled || props.loading) {
    return
  }
  
  emit('send', inputText.value.trim())
  inputText.value = ''
}

const handleClear = () => {
  inputText.value = ''
  emit('clear')
}

const handleNewLine = () => {
  // Ctrl+Enter 插入换行
  const textarea = document.querySelector('.message-input textarea')
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    inputText.value = inputText.value.substring(0, start) + '\n' + inputText.value.substring(end)
    
    // 恢复光标位置
    setTimeout(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 1
    }, 0)
  }
}
</script>

<style scoped>
.input-box {
  background: white;
  border-top: 1px solid #e6e6e6;
  padding: 1rem;
}

.input-area {
  max-width: 800px;
  margin: 0 auto;
}

.message-input {
  margin-bottom: 0.75rem;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  font-size: 0.95rem;
  line-height: 1.5;
  padding: 0.75rem;
  transition: border-color 0.3s;
}

.message-input :deep(.el-textarea__inner):focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-tips {
  font-size: 0.8rem;
  color: #999;
}

.tip {
  margin-right: 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}
</style>