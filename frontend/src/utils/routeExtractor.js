// 地点提取和路径规划工具
export const RouteExtractor = {
  // 从AI回答中提取地点信息
  extractLocations: (content) => {
    if (!content) return []
    
    // 先提取原始地点文本
    const rawLocations = RouteExtractor._extractRawLocations(content)
    
    if (!rawLocations || rawLocations.length === 0) {
      return []
    }
    
    // 使用前端简化清理（后端有AI清理）
    const cleanedLocations = RouteExtractor._frontendClean(rawLocations)
    
    console.log('原始提取:', rawLocations)
    console.log('前端清理后:', cleanedLocations)
    
    return cleanedLocations
  },

  // 增强的地点提取 - 支持景点+餐饮+住宿全类型
  _extractRawLocations: (content) => {
    const locations = []
    
    // 1. 【】和**标记的重点地点
    const markupPatterns = [
      /【([^】]+)】/g,
      /\*\*([^*]+)\*\*/g
    ]
    
    markupPatterns.forEach(pattern => {
      let match
      while ((match = pattern.exec(content)) !== null) {
        const location = match[1].trim()
        if (location && !locations.includes(location)) {
          locations.push(location)
        }
      }
    })
    
    // 2. 动词引导的地点（景点类）
    const tourismPatterns = [
      /前往\s*([^，。！？\n]+)/g,
      /参观\s*([^，。！？\n]+)/g,
      /游览\s*([^，。！？\n]+)/g,
      /到达\s*([^，。！？\n]+)/g,
      /登\s*([^，。！？\n]+)/g,
      /漫步\s*([^，。！？\n]+)/g,
      /体验\s*([^，。！？\n]+)/g
    ]
    
    // 3. 餐饮相关地点提取
    const diningPatterns = [
      /在\s*([^，。！？\n]*[社馆店屋厅])[，。用餐]/g,
      /推荐\s*([^，。！？\n]*[社馆店屋厅])/g,
      /品尝\s*([^，。！？\n]*[社馆店])/g,
      /([^，。！？\n]*茶社)/g,
      /([^，。！？\n]*饭店)/g,
      /([^，。！？\n]*酒家)/g,
      /([^，。！？\n]*餐厅)/g,
      /([^，。！？\n]*食府)/g
    ]
    
    // 4. 住宿相关地点
    const accommodationPatterns = [
      /夜宿\s*([^，。！？\n]+)/g,
      /入住\s*([^，。！？\n]+)/g,
      /([^，。！？\n]*酒店)/g,
      /([^，。！？\n]*宾馆)/g,
      /([^，。！？\n]*客栈)/g,
      /([^，。！？\n]*民宿)/g
    ]
    
    // 5. 购物娱乐地点
    const entertainmentPatterns = [
      /([^，。！？\n]*商场)/g,
      /([^，。！？\n]*步行街)/g,
      /([^，。！？\n]*古街)/g,
      /([^，。！？\n]*老街)/g,
      /([^，。！？\n]*市场)/g
    ]
    
    // 统一提取所有类型的地点
    const allPatterns = [
      ...tourismPatterns,
      ...diningPatterns, 
      ...accommodationPatterns,
      ...entertainmentPatterns
    ]
    
    allPatterns.forEach(pattern => {
      let match
      while ((match = pattern.exec(content)) !== null) {
        const location = match[1].trim()
        if (location && location.length > 1 && location.length < 50 && !locations.includes(location)) {
          locations.push(location)
        }
      }
    })
    
    // 6. 景点后缀匹配
    const suffixPatterns = [
      /([^，。！？\n]+景区)/g,
      /([^，。！？\n]+公园)/g,
      /([^，。！？\n]+古镇)/g,
      /([^，。！？\n]+寺庙?)/g,
      /([^，。！？\n]+塔)/g,
      /([^，。！？\n]+桥)/g,
      /([^，。！？\n]+湖)/g,
      /([^，。！？\n]+山)/g,
      /([^，。！？\n]+园)/g,
      /([^，。！？\n]+馆)/g
    ]
    
    suffixPatterns.forEach(pattern => {
      let match
      while ((match = pattern.exec(content)) !== null) {
        const location = match[1].trim()
        if (location && location.length > 1 && location.length < 30 && !locations.includes(location)) {
          locations.push(location)
        }
      }
    })
    
    console.log(`原始提取到 ${locations.length} 个地点:`, locations)
    return locations.slice(0, 15) // 增加到15个原始地点
  },

  // 智能地点分类和过滤
  _frontendClean: (rawLocations) => {
    // 分类地点数据库 - 支持全类型POI
    const locationDatabase = {
      // 旅游景点
      attractions: {
        '扬州': ['瘦西湖', '个园', '何园', '大明寺', '冶春园', '东关街', '文昌阁', '史可法纪念馆', '古运河'],
        '苏州': ['拙政园', '留园', '虎丘', '寒山寺', '狮子林', '网师园', '同里', '周庄', '锦溪', '甪直', '金鸡湖'],
        '南京': ['中山陵', '夫子庙', '总统府', '明孝陵', '玄武湖', '栖霞山', '雨花台', '秦淮河'],
        '无锡': ['太湖', '灵山大佛', '鼋头渚', '蠡湖', '三国城'],
        '常州': ['天目湖', '茅山', '春秋淹城', '恐龙园']
      },
      
      // 餐饮场所
      restaurants: {
        '扬州': ['富春茶社', '冶春茶社', '食为天酒家', '共和春', '趣园茶社', '三和四美酱菜', '赵氏叠汤圆'],
        '苏州': ['松鹤楼', '得月楼', '王四酒家', '朱鸿兴'],
        '南京': ['马祥兴菜馆', '绿柳居', '江苏酒家'],
        '无锡': ['聚丰园', '迎宾楼'],
        '常州': ['银丝面馆', '德泰恒']
      },
      
      // 住宿场所
      accommodations: {
        '扬州': ['扬州迎宾馆', '西园饭店', '扬州宾馆'],
        '苏州': ['苏州香格里拉', '书香世家'],
        '南京': ['金陵饭店', '南京饭店']
      },
      
      // 购物娱乐
      shopping: {
        '扬州': ['东关街', '四望亭路', '甘泉路', '文昌商圈'],
        '苏州': ['观前街', '石路步行街', '李公堤'],
        '南京': ['新街口', '湖南路']
      },
      
      // 城市中心（备用）
      cities: ['南京', '苏州', '无锡', '常州', '扬州', '镇江', '南通', '泰州', '盐城', '淮安', '徐州', '连云港', '宿迁']
    }
    
    // 分类提取不同类型的地点
    const extracted = {
      attractions: [],      // 景点
      restaurants: [],     // 餐饮
      accommodations: [],  // 住宿 
      shopping: [],        // 购物娱乐
      cities: []          // 城市（备用）
    }
    
    // 对每个原始地点进行分类识别
    for (const rawLocation of rawLocations) {
      const cleanLocation = RouteExtractor.cleanSingleLocation(rawLocation)
      if (!cleanLocation) continue
      
      let matched = false
      
      // 匹配各类型地点
      for (const [category, cityData] of Object.entries(locationDatabase)) {
        if (category === 'cities') {
          // 城市单独处理
          for (const city of cityData) {
            if (cleanLocation.includes(city) || city.includes(cleanLocation)) {
              if (!extracted.cities.includes(city)) {
                extracted.cities.push(city)
                console.log(`🏙️ 识别城市: ${city}`)
                matched = true
                break
              }
            }
          }
        } else {
          // 其他类型地点
          for (const [city, places] of Object.entries(cityData)) {
            for (const place of places) {
              if (cleanLocation.includes(place) || place.includes(cleanLocation)) {
                if (!extracted[category].includes(place)) {
                  extracted[category].push(place)
                  console.log(`${RouteExtractor.getCategoryIcon(category)} 识别${category}: ${place} (${city})`)
                  matched = true
                  break
                }
              }
            }
            if (matched) break
          }
        }
        if (matched) break
      }
    }
    
    // 智能路线规划 - 按旅游逻辑组合
    const routePoints = []
    
    // 1. 早餐：只选1个（优先级：冶春茶社 > 富春茶社 > 其他）
    const breakfastOptions = ['冶春茶社', '富春茶社', '冶春园']
    const selectedBreakfast = breakfastOptions.find(place => extracted.restaurants.includes(place))
    if (selectedBreakfast) {
      routePoints.push(selectedBreakfast)
      console.log(`🍽️ 选定早餐: ${selectedBreakfast}`)
    }
    
    // 2. 主要景点（最多4个）
    extracted.attractions.slice(0, 4).forEach(attraction => {
      if (!routePoints.includes(attraction)) {
        routePoints.push(attraction)
      }
    })
    
    // 3. 午餐：选1个（排除早餐地点）
    const lunchOptions = extracted.restaurants.filter(place => 
      !breakfastOptions.includes(place) && !routePoints.includes(place)
    )
    if (lunchOptions.length > 0) {
      routePoints.push(lunchOptions[0])
      console.log(`🍽️ 选定午餐: ${lunchOptions[0]}`)
    }
    
    // 4. 购物/娱乐地点（最多2个）
    extracted.shopping.slice(0, 2).forEach(shop => {
      if (!routePoints.includes(shop)) {
        routePoints.push(shop)
      }
    })
    
    // 5. 住宿（如果有，放最后）
    if (extracted.accommodations.length > 0 && routePoints.length < 7) {
      routePoints.push(extracted.accommodations[0])
    }
    
    // 如果路线点不足，补充城市
    if (routePoints.length < 2) {
      routePoints.push(...extracted.cities.slice(0, 3))
    }
    
    console.log(`🗺️ 路线规划点构成:`)
    console.log(`  景点: ${extracted.attractions.length}个`)
    console.log(`  餐饮: ${extracted.restaurants.length}个`)
    console.log(`  购物娱乐: ${extracted.shopping.length}个`) 
    console.log(`  住宿: ${extracted.accommodations.length}个`)
    console.log(`  总规划点: ${routePoints.length}个`)
    
    return routePoints.slice(0, 8) // 最多8个规划点
  },

  // 获取分类图标
  getCategoryIcon: (category) => {
    const icons = {
      attractions: '🎯',
      restaurants: '🍽️', 
      accommodations: '🏨',
      shopping: '🛍️'
    }
    return icons[category] || '📍'
  },

  // 清理单个地点名称
  cleanSingleLocation: (rawLocation) => {
    if (!rawLocation) return null
    
    let location = rawLocation.trim()
    
    // 移除常见描述词
    const removeWords = [
      '景区', '景点', '风景区', '旅游区', '公园', '广场',
      '步行约', '米即可', '达', '到达', '抵达', '前往',
      '参观', '游览', '逛逛', '看看', '走走', '转转',
      '约', '即可', '可到', '可达', '完', '后', '附近',
      '很多', '餐馆', '可以', '选择', '有'
    ]
    
    // 移除数字和单位
    location = location.replace(/\d+[米公里千米km]+/g, '')
    
    // 移除描述词
    removeWords.forEach(word => {
      location = location.replace(new RegExp(word, 'g'), '')
    })
    
    // 移除标点和特殊符号
    location = location.replace(/[，。！？：；、""''()（）\[\]【】\*\s]+/g, '')
    
    return location.length > 1 ? location : null
  },

  // 判断是否包含路径规划内容
  containsRouteContent: (content) => {
    const routeKeywords = [
      '路线', '路径', '怎么去', '怎么走', '交通', '行程',
      '自驾', '导航', '距离', '开车', '乘车', '线路',
      '从.*到.*', '先去.*再去', '游玩路线', '旅游路线',
      '一日游', '二日游', '三日游', '多日游', '游览顺序',
      '第一天', '第二天', '第三天', '上午', '下午', '晚上'
    ]
    
    return routeKeywords.some(keyword => {
      if (keyword.includes('.*')) {
        return new RegExp(keyword).test(content)
      }
      return content.includes(keyword)
    })
  }
}

// 路径优化算法
export const RouteOptimizer = {
  // 简化的TSP(旅行商问题)算法 - 最近邻算法
  optimizeRoute: async (locations, mapApi) => {
    if (locations.length <= 2) return locations
    
    try {
      // 获取所有地点的坐标
      const locationData = []
      for (const location of locations) {
        const geoResult = await mapApi.geocode(location)
        if (geoResult.success) {
          locationData.push({
            name: location,
            longitude: geoResult.longitude,
            latitude: geoResult.latitude
          })
        }
      }
      
      if (locationData.length <= 2) return locations
      
      // 计算地点间的距离矩阵
      const distanceMatrix = RouteOptimizer.calculateDistanceMatrix(locationData)
      
      // 使用最近邻算法优化路径
      const optimizedRoute = RouteOptimizer.nearestNeighborTSP(locationData, distanceMatrix)
      
      return optimizedRoute.map(loc => loc.name)
      
    } catch (error) {
      console.error('路径优化失败:', error)
      return locations // 返回原始顺序
    }
  },

  // 计算两点间的直线距离（简化版）
  calculateDistance: (loc1, loc2) => {
    const R = 6371 // 地球半径(km)
    const dLat = (loc2.latitude - loc1.latitude) * Math.PI / 180
    const dLon = (loc2.longitude - loc1.longitude) * Math.PI / 180
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(loc1.latitude * Math.PI / 180) * Math.cos(loc2.latitude * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
    return R * c
  },

  // 计算距离矩阵
  calculateDistanceMatrix: (locations) => {
    const matrix = []
    for (let i = 0; i < locations.length; i++) {
      matrix[i] = []
      for (let j = 0; j < locations.length; j++) {
        if (i === j) {
          matrix[i][j] = 0
        } else {
          matrix[i][j] = RouteOptimizer.calculateDistance(locations[i], locations[j])
        }
      }
    }
    return matrix
  },

  // 最近邻TSP算法
  nearestNeighborTSP: (locations, distanceMatrix) => {
    if (locations.length <= 1) return locations
    
    const visited = new Array(locations.length).fill(false)
    const route = []
    let currentIndex = 0 // 从第一个地点开始
    
    visited[currentIndex] = true
    route.push(locations[currentIndex])
    
    for (let i = 1; i < locations.length; i++) {
      let nearestIndex = -1
      let nearestDistance = Infinity
      
      for (let j = 0; j < locations.length; j++) {
        if (!visited[j] && distanceMatrix[currentIndex][j] < nearestDistance) {
          nearestDistance = distanceMatrix[currentIndex][j]
          nearestIndex = j
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
}