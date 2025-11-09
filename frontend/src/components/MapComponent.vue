<template>
  <div class="map-container">
    <div class="map-header">
      <h3><el-icon><MapLocation /></el-icon>智能路线规划</h3>
      <div class="map-controls">
        <el-button 
          v-if="aiExtractedLocations.length > 0"
          size="small" 
          type="success" 
          @click="planAIRoute"
          :loading="planning"
        >
          <el-icon><Guide /></el-icon>
          AI智能规划 ({{ aiExtractedLocations.length }}个地点)
        </el-button>
        <el-button 
          size="small" 
          type="primary" 
          @click="planRoute"
          :disabled="!startPoint || !endPoint"
          :loading="planning"
        >
          <el-icon><Guide /></el-icon>
          自定义规划
        </el-button>
        <el-button 
          size="small" 
          @click="clearRoute"
          :disabled="!hasRoute"
        >
          <el-icon><Delete /></el-icon>
          清除路线
        </el-button>
      </div>
    </div>
    
    <!-- AI提取的地点列表 -->
    <div v-if="aiExtractedLocations.length > 0" class="ai-locations">
      <div class="locations-header">
        <span class="label">AI识别的地点：</span>
        <el-button 
          size="small" 
          text 
          type="primary"
          @click="optimizeAIRoute"
          :loading="optimizing"
        >
          <el-icon><Promotion /></el-icon>
          优化路线顺序
        </el-button>
      </div>
      <div class="location-tags">
        <el-tag
          v-for="(location, index) in aiExtractedLocations"
          :key="index"
          :type="index === 0 ? 'success' : index === aiExtractedLocations.length - 1 ? 'danger' : 'primary'"
          class="location-tag"
        >
          {{ index + 1 }}. {{ location }}
        </el-tag>
      </div>
    </div>
    
    <!-- 手动输入区域 -->
    <div class="location-inputs">
      <div class="input-group">
        <label>起点：</label>
        <el-input
          v-model="startLocation"
          placeholder="请输入起点位置"
          @blur="geocodeLocation('start')"
          size="small"
        />
      </div>
      <div class="input-group">
        <label>终点：</label>
        <el-input
          v-model="endLocation"
          placeholder="请输入终点位置"
          @blur="geocodeLocation('end')"
          size="small"
        />
      </div>
    </div>
    
    <!-- 文字版路径规划 -->
    <div v-if="aiExtractedLocations.length > 0 && !hasRoute" class="text-route-plan">
      <div class="route-header">
        <h4><el-icon><Guide /></el-icon>智能路径规划方案</h4>
        <el-tag type="success">{{ aiExtractedLocations.length }}个地点</el-tag>
      </div>
      
      <div class="route-timeline">
        <div 
          v-for="(location, index) in aiExtractedLocations" 
          :key="index"
          class="timeline-item"
        >
          <div class="timeline-dot" :class="getLocationTypeClass(location)">
            {{ index + 1 }}
          </div>
          <div class="timeline-content">
            <div class="location-name">{{ location }}</div>
            <div class="location-type">{{ getLocationType(location) }}</div>
            <div class="location-suggestion">{{ getLocationSuggestion(location, index) }}</div>
          </div>
        </div>
      </div>
      
      <div class="route-summary">
        <div class="summary-item">
          <span class="label">总行程：</span>
          <span class="value">{{ aiExtractedLocations.length }}个地点</span>
        </div>
        <div class="summary-item">
          <span class="label">预计用时：</span>
          <span class="value">{{ estimateTime() }}</span>
        </div>
        <div class="summary-item">
          <span class="label">路线特色：</span>
          <span class="value">早茶文化 → 古典园林 → 淮扬美食</span>
        </div>
      </div>
    </div>
    
    <!-- 路线信息 -->
    <div v-if="routeInfo" class="route-info">
      <div class="info-item">
        <span class="label">总距离：</span>
        <span class="value">{{ routeInfo.distance }}公里</span>
      </div>
      <div class="info-item">
        <span class="label">预计时间：</span>
        <span class="value">{{ routeInfo.duration }}</span>
      </div>
      <div v-if="routeInfo.waypoints" class="info-item">
        <span class="label">途经地点：</span>
        <span class="value">{{ routeInfo.waypoints }}个</span>
      </div>
    </div>
    
    <!-- 详细出行参考 -->
    <div v-if="routeInfo && routeInfo.transportOptions" class="travel-reference">
      
      <!-- 交通选择 -->
      <div class="reference-section">
        <h4><el-icon><CaretRight /></el-icon>交通选择建议</h4>
        <div class="transport-options">
          <div 
            v-for="(option, index) in routeInfo.transportOptions" 
            :key="index"
            class="transport-card"
          >
            <div class="transport-header">
              <span class="transport-icon">{{ option.icon }}</span>
              <span class="transport-type">{{ option.type }}</span>
              <span class="transport-cost">{{ option.cost }}</span>
            </div>
            <div class="transport-description">{{ option.description }}</div>
            <div class="transport-duration">预计：{{ option.duration }}</div>
            <div class="transport-advantages">
              <el-tag 
                v-for="advantage in option.advantages" 
                :key="advantage"
                size="small"
                type="info"
              >
                {{ advantage }}
              </el-tag>
            </div>
            <div class="transport-suitable">适合：{{ option.suitable }}</div>
          </div>
        </div>
      </div>
      
      <!-- 时间安排表 -->
      <div class="reference-section">
        <h4><el-icon><Clock /></el-icon>详细时间安排</h4>
        <div class="time-table">
          <div class="time-table-header">
            <span>时间</span>
            <span>地点</span>
            <span>类型</span>
            <span>建议用时</span>
          </div>
          <div 
            v-for="(item, index) in routeInfo.timeTable" 
            :key="index"
            class="time-table-row"
          >
            <span class="time-range">{{ item.startTime }}-{{ item.endTime }}</span>
            <span class="location-name">{{ item.location }}</span>
            <span class="location-type">{{ item.type }}</span>
            <span class="duration">{{ item.duration }}</span>
          </div>
        </div>
      </div>
      
      <!-- 旅游贴士 -->
      <div class="reference-section">
        <h4><el-icon><InfoFilled /></el-icon>实用贴士</h4>
        <div class="tips-container">
          <div 
            v-for="(tip, index) in routeInfo.tips" 
            :key="index"
            class="tip-card"
          >
            <div class="tip-category">{{ tip.category }}</div>
            <div class="tip-content">{{ tip.content }}</div>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineProps } from 'vue'
import { ElMessage } from 'element-plus'
import { MapLocation, Guide, Delete, Promotion, CaretRight, Clock, InfoFilled } from '@element-plus/icons-vue'
import { RouteExtractor, RouteOptimizer } from '@/utils/routeExtractor'
import { mapApi } from '@/api'

// 定义props
const props = defineProps({
  aiContent: {
    type: String,
    default: ''
  }
})

const mapContainer = ref(null)
let map = null
let geocoder = null
let driving = null

// 响应式数据
const startLocation = ref('')
const endLocation = ref('')
const startPoint = ref(null)
const endPoint = ref(null)
const planning = ref(false)
const optimizing = ref(false)
const hasRoute = ref(false)
const routeInfo = ref(null)
const aiExtractedLocations = ref([])

// 初始化时从AI回答中提取地点
const initAILocations = () => {
  console.log('🔍 开始初始化AI地点提取...')
  console.log('AI内容长度:', props.aiContent?.length || 0)
  
  if (props.aiContent && props.aiContent.length > 100) {
    try {
      console.log('🤖 调用RouteExtractor.extractLocations...')
      const locations = RouteExtractor.extractLocations(props.aiContent)
      
      if (locations && locations.length > 0) {
        aiExtractedLocations.value = locations
        console.log(`✅ AI提取成功: ${locations.length}个地点`)
        console.log('📍 提取的地点:', locations)
        
        // 立即显示地图组件
        console.log('🗺️ 准备显示地图组件...')
        
        // 如果超过2个地点，自动优化访问顺序
        if (locations.length > 2) {
          console.log('🔄 开始优化地点访问顺序...')
          setTimeout(() => {
            optimizeAIRoute()
          }, 1000)
        } else if (locations.length >= 2) {
          // 直接规划路线
          console.log('🚀 直接开始路线规划...')
          setTimeout(() => {
            planAIRoute()
          }, 1000)
        }
      } else {
        console.warn('⚠️ 未提取到有效地点')
      }
    } catch (error) {
      console.error('❌ 地点提取出错:', error)
      
      // 使用备用提取方法
      const simpleLocations = extractSimpleLocations(props.aiContent)
      if (simpleLocations.length > 0) {
        aiExtractedLocations.value = simpleLocations
        console.log('🔧 备用方法提取到地点:', simpleLocations)
        
        setTimeout(() => {
          if (simpleLocations.length > 2) {
            optimizeAIRoute()
          } else {
            planAIRoute()
          }
        }, 1000)
      }
    }
  } else {
    console.warn('⚠️ AI内容为空或过短，无法提取地点')
  }
}

// 简单地点提取作为备用方案
const extractSimpleLocations = (content) => {
  const jiangsuLocations = [
    '南京', '苏州', '无锡', '常州', '扬州', '镇江', 
    '南通', '泰州', '盐城', '淮安', '徐州', '连云港', '宿迁',
    '拙政园', '留园', '虎丘', '寒山寺', '狮子林', '网师园',
    '中山陵', '夫子庙', '总统府', '明孝陵', '玄武湖',
    '瘦西湖', '何园', '个园', '大明寺', '冶春园',
    '同里', '周庄', '锦溪', '甪直',
    '太湖', '天目湖', '茅山', '花果山', '金鸡湖',
    '古运河', '东关街'
  ]
  
  const found = []
  jiangsuLocations.forEach(location => {
    if (content.includes(location) && !found.includes(location)) {
      found.push(location)
    }
  })
  
  return found.slice(0, 6)
}

// 初始化地图
const initMap = () => {
  console.log('🗺️ initMap 开始执行')
  console.log('🌐 检查AMap对象:', typeof window.AMap)
  
  if (!window.AMap) {
    console.error('❌ AMap对象不存在，地图加载失败')
    ElMessage.error('地图加载失败，请检查网络连接')
    return
  }
  
  try {
    console.log('🔐 设置安全密钥')
    // 设置安全密钥
    window._AMapSecurityConfig = {
      securityJsCode: 'a4678acdb4e87c0318cdb19076f859ac'
    }
    
    console.log('📍 创建地图实例')
    map = new AMap.Map('amap-container', {
      zoom: 9,
      center: [120.1551, 32.5831], // 江苏省中心位置
      mapStyle: 'amap://styles/normal',
      // 优化Canvas性能配置
      features: ['bg', 'road', 'building', 'point'],
      viewMode: '2D', // 使用2D模式减少Canvas操作
      showLabel: true,
      animateEnable: false, // 禁用动画减少Canvas频繁刷新
      jogEnable: false, // 禁用惯性拖拽
      pitchEnable: false, // 禁用俯仰角
      rotateEnable: false, // 禁用旋转
      buildingAnimation: false, // 禁用建筑物动画
      expandZoomRange: true,
      dragEnable: true,
      zoomEnable: true,
      doubleClickZoom: true,
      keyboardEnable: true,
      scrollWheel: true
    })
    
    if (!map) {
      console.error('❌ 地图创建失败')
      return
    }
    
    console.log('✅ 地图创建成功')
    
    console.log('🗺️ 初始化地理编码器')
    // 初始化地理编码
    geocoder = new AMap.Geocoder({
      city: '江苏省'
    })
    
    if (!geocoder) {
      console.error('❌ 地理编码器创建失败')
      return
    }
    
    console.log('✅ 地理编码器创建成功')
    
    console.log('🚗 初始化驾车路线规划')
    // 初始化驾车路线规划
    driving = new AMap.Driving({
      map: map,
      showTraffic: false,
      showSteps: true,
      isOutline: true,
      outlineColor: '#ffeeff',
      autoFitView: true
    })
    
    if (!driving) {
      console.error('❌ 驾车路线规划器创建失败')
      return
    }
    
    console.log('✅ 驾车路线规划器创建成功')
    console.log('🎯 地图初始化完成，支持智能路径规划')
    
    // 延迟初始化AI地点
    setTimeout(() => {
      console.log('⏰ 开始AI地点初始化...')
      initAILocations()
    }, 1000)
    
  } catch (error) {
    console.error('❌ 地图初始化失败:', error)
    ElMessage.error('地图初始化失败: ' + error.message)
  }
}

// 地理编码
const geocodeLocation = async (type) => {
  if (!geocoder) return
  
  const location = type === 'start' ? startLocation.value : endLocation.value
  if (!location.trim()) return
  
  try {
    geocoder.getLocation(location, (status, result) => {
      if (status === 'complete' && result.geocodes.length) {
        const lnglat = [result.geocodes[0].location.lng, result.geocodes[0].location.lat]
        
        if (type === 'start') {
          startPoint.value = lnglat
        } else {
          endPoint.value = lnglat
        }
        
        // 在地图上标记点
        const marker = new AMap.Marker({
          position: lnglat,
          title: type === 'start' ? '起点' : '终点',
          icon: type === 'start' ? 
            'https://webapi.amap.com/theme/v1.3/markers/n/start.png' :
            'https://webapi.amap.com/theme/v1.3/markers/n/end.png'
        })
        map.add(marker)
        
      } else {
        ElMessage.warning(`无法找到${type === 'start' ? '起点' : '终点'}位置`)
      }
    })
  } catch (error) {
    console.error('地理编码失败:', error)
    ElMessage.error('地址解析失败')
  }
}

// AI智能路线规划
const planAIRoute = async () => {
  console.log(`🎯 planAIRoute 开始执行，地点数量: ${aiExtractedLocations.value.length}`)
  console.log(`📍 地点列表:`, aiExtractedLocations.value)
  
  if (aiExtractedLocations.value.length < 2) {
    console.error('❌ 地点不足2个，无法规划路线')
    ElMessage.warning('需要至少2个地点才能规划路线')
    return
  }
  
  planning.value = true
  console.log('🔄 设置planning状态为true')
  
  try {
    // 跳过地图可视化，直接生成出行参考
    console.log('📋 生成文字版出行参考...')
    await generateTravelReference()
    console.log('✅ 出行参考生成完成')
    
  } catch (error) {
    console.error('❌ 路线规划失败:', error)
    ElMessage.error('路线规划失败: ' + error.message)
  }
  
  planning.value = false
  console.log('🏁 planAIRoute 执行完成，planning设为false')
}

// 生成出行参考
const generateTravelReference = async () => {
  console.log('🚗 开始生成出行参考...')
  
  // 标记路线已生成
  hasRoute.value = true
  
  // 计算基础路线信息
  const totalLocations = aiExtractedLocations.value.length
  const estimatedDistance = calculateEstimatedDistance()
  const estimatedTime = calculateEstimatedTime()
  
  // 设置路线信息
  routeInfo.value = {
    distance: estimatedDistance,
    duration: estimatedTime,
    waypoints: Math.max(0, totalLocations - 2),
    locations: aiExtractedLocations.value,
    transportOptions: await generateTransportOptions(),
    timeTable: generateTimeTable(),
    tips: generateTravelTips()
  }
  
  console.log('📊 路线信息已设置:', routeInfo.value)
}

// 地理编码Promise封装
const geocodeWithPromise = (address) => {
  return new Promise((resolve) => {
    console.log(`🔍 开始地理编码: ${address}`)
    
    if (!geocoder) {
      console.error('❌ geocoder对象不存在！')
      resolve({ success: false, error: 'geocoder not initialized' })
      return
    }
    
    geocoder.getLocation(address, (status, result) => {
      console.log(`📍 ${address} 编码状态: ${status}`)
      console.log(`📍 ${address} 编码结果:`, result)
      
      if (status === 'complete' && result.geocodes && result.geocodes.length > 0) {
        const location = result.geocodes[0].location
        const response = {
          success: true,
          longitude: location.lng,
          latitude: location.lat
        }
        console.log(`✅ ${address} 编码成功:`, response)
        resolve(response)
      } else {
        console.warn(`⚠️ ${address} 编码失败，状态: ${status}`)
        resolve({ success: false, status, result })
      }
    })
  })
}

// 多点路线规划
const planMultiPointRoute = async (waypoints) => {
  return new Promise((resolve, reject) => {
    console.log(`🛣️ planMultiPointRoute 开始，waypoints数量: ${waypoints.length}`)
    console.log(`🗺️ waypoints:`, waypoints)
    
    if (!driving) {
      console.error('❌ driving对象不存在！')
      resolve()
      return
    }
    
    try {
      if (waypoints.length === 2) {
        console.log('🚗 两点路线规划模式')
        // 两点之间直接规划
        driving.search(waypoints[0], waypoints[1], (status, result) => {
          console.log(`🛣️ 两点路线规划状态: ${status}`)
          console.log(`🛣️ 两点路线规划结果:`, result)
          
          if (status.includes('USERKEY')) {
            console.warn('⚠️ API密钥问题，使用模拟路线')
            createMockRoute(waypoints)
            resolve()
          } else {
            handleRouteResult(status, result, waypoints.length)
            resolve()
          }
        })
      } else {
        console.log('🚗 多点路线规划模式')
        // 多点路线规划
        const origin = waypoints[0]
        const destination = waypoints[waypoints.length - 1]
        const viaPoints = waypoints.slice(1, -1)
        
        console.log(`🎯 起点: [${origin[0]}, ${origin[1]}]`)
        console.log(`🏁 终点: [${destination[0]}, ${destination[1]}]`)
        console.log(`🗺️ 途经点数量: ${viaPoints.length}`)
        console.log(`📍 途经点:`, viaPoints)
        
        driving.search(origin, destination, {
          waypoints: viaPoints
        }, (status, result) => {
          console.log(`🛣️ 多点路线规划状态: ${status}`)
          console.log(`🛣️ 多点路线规划结果:`, result)
          
          if (status.includes('USERKEY')) {
            console.warn('⚠️ API密钥问题，使用模拟路线')
            createMockRoute(waypoints)
            resolve()
          } else {
            handleRouteResult(status, result, waypoints.length)
            resolve()
          }
        })
      }
    } catch (error) {
      console.error('❌ 路线规划异常，使用模拟路线:', error)
      createMockRoute(waypoints)
      resolve()
    }
  })
}

// 处理路线规划结果
const handleRouteResult = (status, result, waypointCount) => {
  console.log('路线规划状态:', status, '结果:', result)
  
  if (status === 'complete' && result.routes && result.routes.length > 0) {
    console.log('路线规划成功:', result)
    hasRoute.value = true
    
    const route = result.routes[0]
    routeInfo.value = {
      distance: (route.distance / 1000).toFixed(1),
      duration: formatDuration(route.time),
      waypoints: waypointCount - 2 // 不包括起点和终点
    }
    
    // 设置地图视野以包含所有路线
    map.setFitView()
    
    ElMessage.success(`智能路线规划成功！途经${waypointCount}个地点`)
  } else {
    console.error('路线规划失败:', status, result)
    
    // 处理不同的错误类型
    let errorMessage = '路线规划失败'
    if (status.includes('USERKEY')) {
      errorMessage = '地图服务配置有误，请联系管理员'
    } else if (status.includes('QUOTA')) {
      errorMessage = '地图服务使用配额已达上限'
    } else {
      errorMessage = '请检查地点名称是否正确，或稍后重试'
    }
    
    ElMessage.error(errorMessage)
  }
}

// 优化AI路线顺序
const optimizeAIRoute = async () => {
  if (aiExtractedLocations.value.length < 3) {
    console.log('地点少于3个，无需优化顺序')
    // 直接进行路线规划
    if (aiExtractedLocations.value.length >= 2) {
      planAIRoute()
    }
    return
  }
  
  optimizing.value = true
  
  try {
    console.log('开始优化路线顺序...')
    
    // 使用简化的距离优化（不依赖API）
    const optimizedLocations = await simpleOptimizeRoute(aiExtractedLocations.value)
    
    if (optimizedLocations && optimizedLocations.length > 0) {
      aiExtractedLocations.value = optimizedLocations
      console.log('✅ 路线顺序已优化:', optimizedLocations.join(' → '))
      console.log('🎯 期望路线: 早餐 → 景点 → 午餐 → 购物')
      
      // 自动规划优化后的路线
      setTimeout(() => {
        console.log('🚀 开始规划优化后的路线...')
        planAIRoute()
      }, 500)
    } else {
      console.log('⚠️ 优化失败，使用原始顺序')
      planAIRoute()
    }
  } catch (error) {
    console.error('路线优化失败:', error)
    console.log('使用原始顺序进行路线规划')
    planAIRoute()
  }
  
  optimizing.value = false
}

// 简化的路线优化（基于预设坐标）
const simpleOptimizeRoute = async (locations) => {
  try {
    // 分层级的江苏地点坐标库 + 餐饮住宿坐标
    const coordinateMap = {
      // === 扬州地区精确坐标 ===
      // 景点
      '瘦西湖': [119.4342, 32.4064],
      '个园': [119.4298, 32.3952],
      '何园': [119.4185, 32.3889],
      '大明寺': [119.4342, 32.4120],
      '冶春园': [119.4201, 32.3941],
      '东关街': [119.4234, 32.3967],
      '文昌阁': [119.4216, 32.3932],
      '史可法纪念馆': [119.4156, 32.3978],
      '古运河': [119.4123, 32.3845],
      
      // 餐饮
      '富春茶社': [119.4189, 32.3923],
      '冶春茶社': [119.4201, 32.3941],
      '食为天酒家': [119.4234, 32.3967],
      '共和春': [119.4245, 32.3956],
      '趣园茶社': [119.4298, 32.3952],
      '三和四美酱菜': [119.4234, 32.3967],
      '赵氏叠汤圆': [119.4234, 32.3967],
      
      // === 苏州地区精确坐标 ===
      // 景点
      '拙政园': [120.6263, 31.3235],
      '虎丘': [120.5895, 31.3394],
      '留园': [120.6065, 31.3156],
      '狮子林': [120.6234, 31.3198],
      '网师园': [120.6245, 31.3012],
      '寒山寺': [120.5534, 31.3045],
      '同里': [120.7356, 31.1523],
      '周庄': [120.8493, 31.1168],
      '金鸡湖': [120.7123, 31.3456],
      
      // 餐饮
      '松鹤楼': [120.6194, 31.3089],
      '得月楼': [120.6245, 31.3156],
      '王四酒家': [120.6234, 31.3098],
      '朱鸿兴': [120.6189, 31.3067],
      
      // === 南京地区精确坐标 ===
      // 景点
      '中山陵': [118.8432, 32.0684],
      '夫子庙': [118.7969, 32.0260],
      '总统府': [118.7934, 32.0456],
      '明孝陵': [118.8456, 32.0589],
      '玄武湖': [118.7823, 32.0734],
      '栖霞山': [118.9612, 32.1734],
      '雨花台': [118.7542, 32.0123],
      '秦淮河': [118.7969, 32.0260],
      
      // 餐饮
      '马祥兴菜馆': [118.7945, 32.0289],
      '绿柳居': [118.7969, 32.0260],
      '江苏酒家': [118.7923, 32.0567],
      
      // === 无锡常州等其他地区 ===
      '太湖': [120.2176, 31.2189],
      '灵山大佛': [120.0956, 31.4389],
      '鼋头渚': [120.2234, 31.5567],
      '蠡湖': [120.2856, 31.4923],
      '天目湖': [119.4234, 31.4156],
      '茅山': [119.2456, 31.7789],
      '春秋淹城': [120.0123, 31.7234],
      
      // === 城市中心坐标（仅在无具体景点时使用） ===
      '扬州': [119.4216, 32.3932],
      '苏州': [120.6194, 31.3089],
      '南京': [118.7969, 32.0603],
      '无锡': [120.3019, 31.5744],
      '常州': [119.9742, 31.8059],
      '镇江': [119.4763, 32.2044],
      '南通': [120.8644, 32.0186],
      '泰州': [119.9152, 32.4849]
    }
    
    // 获取有坐标的地点
    const locationsWithCoords = []
    for (const location of locations) {
      const coords = coordinateMap[location]
      if (coords) {
        // 使用预设的高精度坐标
        locationsWithCoords.push({
          name: location,
          longitude: coords[0],
          latitude: coords[1],
          source: 'preset' // 标记数据来源
        })
      } else {
        // 如果没有预设坐标，尝试使用高德地理编码
        try {
          const geoResult = await geocodeWithPromise(location)
          if (geoResult.success) {
            locationsWithCoords.push({
              name: location,
              longitude: geoResult.longitude,
              latitude: geoResult.latitude,
              source: 'amap' // 标记数据来源
            })
            console.log(`${location} 使用高德地理编码: (${geoResult.longitude}, ${geoResult.latitude})`)
          } else {
            console.warn(`${location} 地理编码失败，使用默认坐标`)
            // 使用江苏省中心坐标作为默认值
            locationsWithCoords.push({
              name: location,
              longitude: 119.4216,
              latitude: 32.3932,
              source: 'default'
            })
          }
        } catch (error) {
          console.warn(`${location} 地理编码异常，使用默认坐标:`, error)
          locationsWithCoords.push({
            name: location,
            longitude: 119.4216,
            latitude: 32.3932,
            source: 'default'
          })
        }
      }
    }
    
    if (locationsWithCoords.length <= 2) {
      return locations
    }
    
    // 生成准确性报告
    const presetCount = locationsWithCoords.filter(loc => loc.source === 'preset').length
    const amapCount = locationsWithCoords.filter(loc => loc.source === 'amap').length
    const defaultCount = locationsWithCoords.filter(loc => loc.source === 'default').length
    
    console.log(`路线优化数据源分析:`)
    console.log(`  预设坐标(高精度): ${presetCount}个`)
    console.log(`  高德地理编码: ${amapCount}个`) 
    console.log(`  默认坐标(低精度): ${defaultCount}个`)
    console.log(`  总体准确性: ${((presetCount + amapCount) / locationsWithCoords.length * 100).toFixed(1)}%`)
    
    // 使用最近邻算法优化
    const optimized = nearestNeighborOptimize(locationsWithCoords)
    return optimized.map(loc => loc.name)
    
  } catch (error) {
    console.error('简化优化失败:', error)
    return locations
  }
}

// 最近邻优化算法（简化版）
const nearestNeighborOptimize = (locations) => {
  if (locations.length <= 1) return locations
  
  const visited = new Array(locations.length).fill(false)
  const route = []
  let currentIndex = 0
  
  visited[currentIndex] = true
  route.push(locations[currentIndex])
  
  for (let i = 1; i < locations.length; i++) {
    let nearestIndex = -1
    let nearestDistance = Infinity
    
    for (let j = 0; j < locations.length; j++) {
      if (!visited[j]) {
        const distance = calculateSimpleDistance(locations[currentIndex], locations[j])
        if (distance < nearestDistance) {
          nearestDistance = distance
          nearestIndex = j
        }
      }
    }
    
    if (nearestIndex !== -1) {
      visited[nearestIndex] = true
      route.push(locations[nearestIndex])
      currentIndex = nearestIndex
    }
  }
  
  return route
}

// 简单距离计算
const calculateSimpleDistance = (loc1, loc2) => {
  const dx = loc2.longitude - loc1.longitude
  const dy = loc2.latitude - loc1.latitude
  return Math.sqrt(dx * dx + dy * dy)
}

// 创建模拟路线（当API密钥无法使用时）
const createMockRoute = (waypoints) => {
  try {
    console.log('API限制，使用模拟路线显示')
    
    // 创建路线路径
    const routePath = new AMap.Polyline({
      path: waypoints,
      strokeColor: '#FF5722',
      strokeWeight: 6,
      strokeOpacity: 0.8,
      strokeStyle: 'solid'
    })
    
    map.add(routePath)
    
    // 计算模拟距离和时间
    let totalDistance = 0
    for (let i = 0; i < waypoints.length - 1; i++) {
      const distance = calculateStraightDistance(waypoints[i], waypoints[i + 1])
      totalDistance += distance
    }
    
    // 设置路线信息
    hasRoute.value = true
    routeInfo.value = {
      distance: totalDistance.toFixed(1),
      duration: Math.ceil(totalDistance * 0.8) + '分钟', // 模拟时间
      waypoints: waypoints.length - 2
    }
    
    // 设置地图视野
    map.setFitView([routePath])
    
    console.log(`模拟路线已生成: ${totalDistance.toFixed(1)}km`)
    ElMessage.success(`智能路线规划成功！途经${waypoints.length}个地点（模拟路线）`)
    
  } catch (error) {
    console.error('模拟路线创建失败:', error)
    ElMessage.warning('路线规划遇到问题，但地点已在地图上标记')
  }
}

// 计算两点间直线距离
const calculateStraightDistance = (point1, point2) => {
  const R = 6371 // 地球半径(km)
  const lat1 = point1[1] * Math.PI / 180
  const lat2 = point2[1] * Math.PI / 180
  const deltaLat = (point2[1] - point1[1]) * Math.PI / 180
  const deltaLng = (point2[0] - point1[0]) * Math.PI / 180

  const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
          Math.cos(lat1) * Math.cos(lat2) *
          Math.sin(deltaLng/2) * Math.sin(deltaLng/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))

  return R * c
}

// 传统两点路线规划
const planRoute = async () => {
  if (!driving || !startPoint.value || !endPoint.value) return
  
  planning.value = true
  
  try {
    driving.search(startPoint.value, endPoint.value, (status, result) => {
      handleRouteResult(status, result, 2)
      planning.value = false
    })
  } catch (error) {
    planning.value = false
    console.error('路线规划异常:', error)
    ElMessage.error('路线规划异常')
  }
}

// 清除路线
const clearRoute = () => {
  if (map) {
    map.clearMap()
  }
  hasRoute.value = false
  routeInfo.value = null
  startPoint.value = null
  endPoint.value = null
  startLocation.value = ''
  endLocation.value = ''
}

// 获取地点类型
const getLocationType = (location) => {
  const types = {
    '冶春茶社': '🍵 传统早茶',
    '富春茶社': '🍵 传统早茶', 
    '冶春园': '🌸 古典园林',
    '个园': '🎋 竹石园林',
    '何园': '🏛️ 晚清园林',
    '瘦西湖': '🌊 风景名胜',
    '大明寺': '🏮 古刹名寺',
    '东关街': '🛍️ 古街购物',
    '食为天酒家': '🍽️ 淮扬菜',
    '共和春': '🥟 特色小吃'
  }
  return types[location] || '📍 旅游景点'
}

// 获取地点类型样式
const getLocationTypeClass = (location) => {
  const restaurants = ['冶春茶社', '富春茶社', '食为天酒家', '共和春']
  const attractions = ['冶春园', '个园', '何园', '瘦西湖', '大明寺']
  const shopping = ['东关街']
  
  if (restaurants.includes(location)) return 'restaurant'
  if (attractions.includes(location)) return 'attraction'
  if (shopping.includes(location)) return 'shopping'
  return 'default'
}

// 获取地点建议
const getLocationSuggestion = (location, index) => {
  const suggestions = {
    '冶春茶社': '建议7:30-9:00，必点蟹黄汤包、千层油糕',
    '富春茶社': '建议7:30-9:00，翡翠烧卖、烫干丝经典',
    '冶春园': '早茶后可就近游览，园林茶肆融合',
    '个园': '游览1-1.5小时，四季假山是亮点',
    '何园': '游览1小时，复道回廊堪称一绝', 
    '瘦西湖': '主要景点，建议2-3小时游览',
    '大明寺': '登塔俯瞰扬州全景，游览1小时',
    '东关街': '古街漫步购物，品尝当地小吃',
    '食为天酒家': '正宗淮扬菜，推荐扬州炒饭',
    '共和春': '百年老店，饺面是招牌'
  }
  
  const timeAdvice = [
    '上午7:30-9:00（早餐时间）',
    '上午9:30-10:30（园林游览）', 
    '上午10:30-11:30（街区漫步）',
    '中午12:00-13:00（午餐时间）',
    '下午14:00-17:00（主要景点）'
  ]
  
  const suggestion = suggestions[location] || '精心安排的旅游地点'
  const time = timeAdvice[index] || '灵活安排时间'
  
  return `${time} - ${suggestion}`
}

// 计算预估距离
const calculateEstimatedDistance = () => {
  const locations = aiExtractedLocations.value
  if (locations.length < 2) return '0.0'
  
  // 基于地点数量和类型估算距离
  let totalDistance = 0
  
  // 扬州市内景点间平均距离约2-5公里
  for (let i = 0; i < locations.length - 1; i++) {
    const current = locations[i]
    const next = locations[i + 1]
    
    // 根据地点类型估算距离
    if (isNearbyLocation(current, next)) {
      totalDistance += 0.5 // 相邻景点500米
    } else {
      totalDistance += 2.8 // 市内平均距离2.8公里
    }
  }
  
  return totalDistance.toFixed(1)
}

// 判断是否为相邻地点
const isNearbyLocation = (loc1, loc2) => {
  const nearbyPairs = [
    ['冶春茶社', '冶春园'],
    ['个园', '东关街'],
    ['何园', '瘦西湖'],
    ['瘦西湖', '大明寺']
  ]
  
  return nearbyPairs.some(pair => 
    (pair[0] === loc1 && pair[1] === loc2) || 
    (pair[0] === loc2 && pair[1] === loc1)
  )
}

// 计算预估时间
const calculateEstimatedTime = () => {
  const locations = aiExtractedLocations.value
  const distance = parseFloat(calculateEstimatedDistance())
  
  // 基于距离和地点数量估算时间
  let totalMinutes = 0
  
  // 行程时间：每公里约3-5分钟（考虑扬州市内交通）
  totalMinutes += distance * 4
  
  // 游览时间：每个地点平均60-90分钟
  locations.forEach(location => {
    const visitTime = getLocationVisitTime(location)
    totalMinutes += visitTime
  })
  
  const hours = Math.floor(totalMinutes / 60)
  const minutes = Math.round(totalMinutes % 60)
  
  return hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`
}

// 获取地点游览时间
const getLocationVisitTime = (location) => {
  const timeMap = {
    '冶春茶社': 90,    // 早茶1.5小时
    '富春茶社': 90,    // 早茶1.5小时
    '冶春园': 45,      // 小园林45分钟
    '个园': 75,        // 游览1.25小时
    '何园': 60,        // 游览1小时
    '瘦西湖': 180,     // 主景点3小时
    '大明寺': 60,      // 游览1小时
    '东关街': 90,      // 购物用餐1.5小时
    '食为天酒家': 75,  // 正餐1.25小时
    '共和春': 45       // 小吃45分钟
  }
  
  return timeMap[location] || 60 // 默认1小时
}

// 生成交通选择建议
const generateTransportOptions = async () => {
  const locations = aiExtractedLocations.value
  const distance = parseFloat(calculateEstimatedDistance())
  
  const options = []
  
  // 步行方案
  if (distance <= 5) {
    options.push({
      type: '步行',
      icon: '🚶',
      description: '扬州古城区景点集中，步行游览最佳',
      duration: `${Math.ceil(distance * 12)}分钟`,
      cost: '免费',
      advantages: ['环保健康', '可随时停留拍照', '体验古城韵味'],
      suitable: '体力良好，天气适宜'
    })
  }
  
  // 自行车方案  
  if (distance <= 15) {
    options.push({
      type: '共享单车',
      icon: '🚲',
      description: '扬州有完善的共享单车系统',
      duration: `${Math.ceil(distance * 5)}分钟`,
      cost: '约5-15元',
      advantages: ['灵活便捷', '覆盖面广', '成本较低'],
      suitable: '短中距离，平坦路段'
    })
  }
  
  // 出租车方案
  options.push({
    type: '出租车/网约车',
    icon: '🚗',
    description: '扬州市内出行便利',
    duration: `${Math.ceil(distance * 3)}分钟`,
    cost: `约${Math.ceil(distance * 3 + 8)}元`,
    advantages: ['舒适快捷', '不受天气影响', '可直达景点'],
    suitable: '携带行李，老人小孩'
  })
  
  // 公交方案（如果距离适中）
  if (distance > 3 && distance <= 20) {
    options.push({
      type: '公交车',
      icon: '🚌',
      description: '扬州公交线路覆盖主要景点',
      duration: `${Math.ceil(distance * 4 + 10)}分钟`,
      cost: '每次2元',
      advantages: ['经济实惠', '环保出行', '体验当地生活'],
      suitable: '不赶时间，熟悉线路'
    })
  }
  
  return options
}

// 生成时间安排表
const generateTimeTable = () => {
  const locations = aiExtractedLocations.value
  const timeTable = []
  let currentTime = 7.5 // 7:30开始
  
  locations.forEach((location, index) => {
    const visitTime = getLocationVisitTime(location) / 60 // 转换为小时
    const startTime = Math.floor(currentTime)
    const startMinutes = Math.round((currentTime - startTime) * 60)
    const endTime = currentTime + visitTime
    const endHour = Math.floor(endTime)
    const endMinutes = Math.round((endTime - endHour) * 60)
    
    timeTable.push({
      location,
      startTime: `${startTime.toString().padStart(2, '0')}:${startMinutes.toString().padStart(2, '0')}`,
      endTime: `${endHour.toString().padStart(2, '0')}:${endMinutes.toString().padStart(2, '0')}`,
      duration: `${Math.round(visitTime * 60)}分钟`,
      type: getLocationType(location),
      priority: index < 2 ? '重要' : '推荐'
    })
    
    currentTime = endTime + 0.25 // 每个地点间15分钟交通时间
  })
  
  return timeTable
}

// 生成旅游贴士
const generateTravelTips = () => {
  const locations = aiExtractedLocations.value
  const tips = []
  
  // 基础贴士
  tips.push({
    category: '📱 预订建议',
    content: '建议提前1天预订知名餐厅，避免排队等位'
  })
  
  // 根据地点生成专属贴士
  if (locations.includes('冶春茶社') || locations.includes('富春茶社')) {
    tips.push({
      category: '🍵 早茶贴士',
      content: '扬州早茶建议7:30-9:00前往，晚了招牌点心容易售罄'
    })
  }
  
  if (locations.includes('瘦西湖')) {
    tips.push({
      category: '🌊 瘦西湖攻略',
      content: '建议购买景点联票(220元)，包含瘦西湖、个园、何园等多个景点'
    })
  }
  
  if (locations.includes('东关街')) {
    tips.push({
      category: '🛍️ 购物提醒',
      content: '东关街晚上更热闹，可安排在下午4点后前往'
    })
  }
  
  // 通用贴士
  tips.push({
    category: '🌤️ 天气准备',
    content: '扬州四季分明，建议携带雨具，夏季注意防晒'
  })
  
  tips.push({
    category: '💰 费用预算',
    content: `预计总费用：餐饮200-300元，门票220元，交通50-100元/人`
  })
  
  return tips
}

// 生命周期钩子
onMounted(() => {
  console.log('🎯 MapComponent已挂载')
  console.log('AI内容:', props.aiContent?.substring(0, 200) + '...')
  
  setTimeout(() => {
    console.log('🗺️ 开始初始化地图...')
    initMap()
  }, 100)
  
  // 监听AI内容变化
  setTimeout(() => {
    console.log('📊 检查AI内容是否有效...')
    initAILocations()
  }, 500)
})

onUnmounted(() => {
  if (map) {
    map.destroy()
  }
})
</script>

<style scoped>
.map-container {
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  margin-top: 1rem;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
}

.map-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #333;
  font-size: 1.1rem;
}

.map-controls {
  display: flex;
  gap: 0.5rem;
}

.location-inputs {
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.input-group {
  flex: 1;
  min-width: 200px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.input-group label {
  color: #666;
  font-size: 0.9rem;
  white-space: nowrap;
}

.map-content {
  width: 100%;
  height: 400px;
}

.route-info {
  padding: 1rem;
  background: #f8f9fa;
  border-top: 1px solid #e6e6e6;
  display: flex;
  gap: 2rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.label {
  color: #666;
  font-size: 0.9rem;
}

.value {
  color: #333;
  font-weight: 500;
}

/* AI地点展示样式 */
.ai-locations {
  padding: 1rem;
  background: #f0f9ff;
  border-bottom: 1px solid #e6e6e6;
}

.locations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.locations-header .label {
  font-weight: 500;
  color: #333;
}

.location-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* 文字版路径规划样式 */
.text-route-plan {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1rem;
  border: 1px solid #e6e6e6;
}

.route-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f0f0;
}

.route-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #333;
  font-size: 1.2rem;
}

.route-timeline {
  margin-bottom: 1.5rem;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 20px;
  top: 40px;
  bottom: -24px;
  width: 2px;
  background: linear-gradient(to bottom, #e6e6e6, transparent);
}

.timeline-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  margin-right: 1rem;
  flex-shrink: 0;
}

.timeline-dot.restaurant {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

.timeline-dot.attraction {
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
}

.timeline-dot.shopping {
  background: linear-gradient(135deg, #a55eea, #8b3a8b);
}

.timeline-dot.default {
  background: linear-gradient(135deg, #74b9ff, #0984e3);
}

.timeline-content {
  flex: 1;
}

.location-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.3rem;
}

.location-type {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.location-suggestion {
  font-size: 0.85rem;
  color: #888;
  line-height: 1.4;
  background: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  border-left: 3px solid #007AFF;
}

.route-summary {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.summary-item .label {
  color: #666;
  font-size: 0.9rem;
}

/* 详细出行参考样式 */
.travel-reference {
  margin-top: 1rem;
}

.reference-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid #e6e6e6;
}

.reference-section h4 {
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #333;
  font-size: 1.1rem;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 0.5rem;
}

/* 交通选择样式 */
.transport-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.transport-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 1rem;
  border: 1px solid #e9ecef;
  transition: transform 0.2s, box-shadow 0.2s;
}

.transport-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.transport-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.transport-icon {
  font-size: 1.5rem;
}

.transport-type {
  font-weight: 600;
  color: #333;
}

.transport-cost {
  color: #007AFF;
  font-weight: 500;
}

.transport-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.transport-duration {
  color: #28a745;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.transport-advantages {
  margin-bottom: 0.5rem;
}

.transport-advantages .el-tag {
  margin-right: 0.25rem;
  margin-bottom: 0.25rem;
}

.transport-suitable {
  color: #888;
  font-size: 0.85rem;
}

/* 时间安排表样式 */
.time-table {
  background: #f8f9fa;
  border-radius: 6px;
  overflow: hidden;
}

.time-table-header {
  background: #007AFF;
  color: white;
  display: grid;
  grid-template-columns: 120px 1fr 120px 100px;
  gap: 1rem;
  padding: 0.75rem 1rem;
  font-weight: 600;
}

.time-table-row {
  display: grid;
  grid-template-columns: 120px 1fr 120px 100px;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e9ecef;
  align-items: center;
}

.time-table-row:last-child {
  border-bottom: none;
}

.time-range {
  font-family: monospace;
  font-weight: 600;
  color: #007AFF;
}

.location-name {
  font-weight: 500;
}

.location-type {
  color: #666;
  font-size: 0.9rem;
}

.duration {
  color: #28a745;
  font-weight: 500;
}

/* 贴士样式 */
.tips-container {
  display: grid;
  gap: 0.75rem;
}

.tip-card {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 6px;
  padding: 1rem;
  border-left: 4px solid #007AFF;
}

.tip-category {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.tip-content {
  color: #666;
  line-height: 1.5;
}
</style>