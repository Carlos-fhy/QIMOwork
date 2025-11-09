import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API接口
export const chatApi = {
  // 普通问答
  chat: (question, region = 'all', k = 3) => {
    return api.post('/chat', {
      question,
      region,
      k
    })
  },

  // 获取地区列表
  getRegions: () => {
    return api.get('/regions')
  },

  // 健康检查
  healthCheck: () => {
    return api.get('/health')
  },

  // 构建知识库
  buildKnowledgeBase: (reset = false) => {
    return api.post('/build-knowledge-base', { reset })
  }
}

// 地图相关API
export const mapApi = {
  // 地理编码
  geocode: (address, city = '江苏') => {
    return api.post('/map/geocode', {
      address,
      city
    })
  },

  // 路线规划
  getRoute: (origin, destination) => {
    return api.post('/map/route', {
      origin,
      destination
    })
  },

  // 搜索POI
  searchPOI: (address, keywords = '景点', radius = 5000) => {
    return api.post('/map/poi', {
      address,
      keywords,
      radius
    })
  }
}

// SSE流式聊天
export const createSSEConnection = (question, region = 'all', k = 3) => {
  const params = new URLSearchParams({
    question,
    region,
    k: k.toString()
  })
  
  return new EventSource(`/api/chat/stream?${params}`)
}

export default api