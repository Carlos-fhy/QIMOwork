// Markdown解析工具
export const parseMarkdown = (text) => {
  if (!text) return ''
  
  // 基础Markdown解析（简化版）
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // 粗体
    .replace(/\*(.*?)\*/g, '<em>$1</em>')              // 斜体
    .replace(/`(.*?)`/g, '<code>$1</code>')            // 行内代码
    .replace(/\n\n/g, '</p><p>')                       // 段落
    .replace(/\n/g, '<br>')                            // 换行
}

// 格式化时间
export const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 生成唯一ID
export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 防抖函数
export const debounce = (fn, delay) => {
  let timer = null
  return function (...args) {
    clearTimeout(timer)
    timer = setTimeout(() => fn.apply(this, args), delay)
  }
}

// 节流函数
export const throttle = (fn, delay) => {
  let timer = null
  return function (...args) {
    if (!timer) {
      timer = setTimeout(() => {
        fn.apply(this, args)
        timer = null
      }, delay)
    }
  }
}