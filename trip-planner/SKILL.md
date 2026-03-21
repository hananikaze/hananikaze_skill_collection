---
name: trip-planner
description: Interactive detailed trip planning - Stage 1 of budget travel workflow. Discovers attractions via web search (Exa), generates map visualizations, optimizes routes, and creates hour-by-hour itineraries. Use when user has arrival time/destination from budget-travel and needs detailed day planning. Triggers on "详细规划", "精密行程", "优化路线", "plan my day", or when transitioning from budget-travel to stage 1.
---

# Trip Planner (精密行程规划)

Transform rough travel plans into executable hour-by-hour itineraries with optimized routes and interactive planning.

## Overview

This is **Stage 1** of the budget travel workflow:

```
前置：budget-travel → 决定去哪里（目的地+到达时间）
  ↓
阶段1：trip-planner → 精密规划（景点发现+路线优化+详细时间表）⭐ THIS
  ↓
阶段2：travel-checkin → 实时记录（打卡+记账）
  ↓
阶段3：travel-journal → 复盘总结（游记+预算对比）
```

## Input Requirements

Get from budget-travel or user:
- **到达时间** - When you arrive (e.g., 周六 09:15)
- **目的地** - Destination city
- **可用时间** - Available time (e.g., 1 day, 2 days)
- **返程时间** - Departure time (optional, for day trips)

## Planning Workflow (Multi-round Interactive)

### Round 1: Attraction Discovery 🔍

**Goal**: Discover ALL possible attractions (conventional + unconventional)

**Steps**:
1. Use Exa to search for attractions in the city
2. Query multiple categories:
   - 🏛️ Tourist attractions (景点)
   - 🍜 Local food streets (美食街/小吃)
   - 🏭 Industrial sites (工业园区/创客空间)
   - 🎨 Art districts (艺术区/文创园)
   - 🏫 Universities (大学校园)
   - 🌳 Parks and nature (公园/湖泊)
   - 📚 Museums and libraries
   - 🏪 Local markets (市场/集市)
3. Compile **20 diverse locations**
4. For each location, extract:
   - Name
   - Type (category)
   - Address (for mapping)
   - Brief description (1 line)
   - Estimated visit duration
   - Cost (if applicable)

**Output format**:
```
📍 20个可选地点（保定）
━━━━━━━━━━━━━━━━━━━━

🏛️ 历史文化
1. 直隶总督署 - 清代官署，保存完好，60分钟，¥30
2. 古莲花池 - 皇家园林，1小时，¥20

🍜 美食体验
3. 裕华路小吃街 - 当地特色小吃集中地，30分钟，¥20-50
4. 马家老鸡铺 - 保定名吃驴肉火烧，20分钟，¥15

🏭 工业与创新
5. 长城汽车工业园 - 汽车制造参观，2小时，预约制
6. 保定创客空间 - 本地创业氛围，1小时，免费

[... 继续到20个]

请选择你感兴趣的地点（输入编号，如 1,3,5,7）
```

### Round 2: Map Visualization 🗺️

**Goal**: Generate visual map with all selected attractions

**Steps**:
1. Extract coordinates for selected locations (use Amap Geocoding API)
2. Generate map image using one of:
   - **Option A**: Amap Static Map API (best for China)
   - **Option B**: Google Static Maps API (fallback)
   - **Option C**: OpenStreetMap + Python (offline)
3. Mark attractions with numbered pins
4. Show to user for spatial understanding

**API usage**:
```python
# Amap Static Map API
# https://lbs.amap.com/api/webservice/guide/api/staticmaps

import requests

def generate_map(locations, city):
    """
    locations: [{"name": "天坛", "lat": 39.88, "lng": 116.40}, ...]
    """
    # Build markers string
    markers = []
    for i, loc in enumerate(locations, 1):
        markers.append(f"{loc['lng']},{loc['lat']}")
    
    markers_str = "|".join(markers)
    
    url = f"https://restapi.amap.com/v3/staticmap"
    params = {
        "markers": f"mid,0xFF0000:{markers_str}",
        "size": "800*600",
        "zoom": 12,
        "key": AMAP_API_KEY
    }
    
    # Returns image URL or binary
    ...
```

**Output**:
```
🗺️ 地图已生成
━━━━━━━━━━━━━━━━━━━━
[地图图片，标记了所有选中的景点]

地点分布：
• 北部：直隶总督署(1)、古莲花池(2)
• 中部：裕华路美食街(3)、保定博物馆(4)
• 南部：竞秀公园(5)

继续规划路线？
```

### Round 3: Route Optimization 🚴

**Goal**: Calculate optimal visiting order

**Algorithm**:
1. Cluster attractions by geographic proximity
2. Consider opening hours and visit duration
3. Apply Traveling Salesman Problem (TSP) heuristic:
   - Greedy nearest-neighbor
   - Or use simple clustering + sequential visit
4. Insert meal times (11:30-13:00, 17:30-19:00)
5. Account for transportation modes:
   - 🚲 Bike sharing (<3km)
   - 🚌 Bus (3-10km)
   - 🚇 Subway (if available)

**Output**:
```
🗓️ 推荐路线（已优化）
━━━━━━━━━━━━━━━━━━━━

📍 路线1（文化+美食线）
━━━━━━━━━━━━━━━━━━━━
09:15 到达保定站
09:30 出站，骑共享单车（15分钟）
09:45 直隶总督署（60分钟，¥30）
10:45 步行至古莲花池（5分钟）
10:50 古莲花池（60分钟，¥20）
11:50 骑车去裕华路（10分钟）
12:00 午餐：裕华路小吃街（60分钟，¥40）
13:00 骑车去保定博物馆（15分钟）
13:15 保定博物馆（90分钟，免费）
14:45 骑车去竞秀公园（20分钟）
15:05 竞秀公园（60分钟，免费）
16:05 返回火车站（20分钟骑行）
16:30 预留候车时间
17:30 返程列车

💰 预算：¥110（门票¥50 + 餐饮¥40 + 单车¥5 + 其他¥15）
🚶 总距离：~8 km（主要骑行）

路线2（工业+创新线）...
路线3（悠闲放松线）...

选择路线或调整？
```

### Round 4: Finalize Itinerary 📋

**Goal**: Generate final executable plan

**Includes**:
- Hour-by-hour timeline
- Navigation links (Amap URLs for each leg)
- Contingency plans (rain/closed/tired)
- Packing checklist
- Export to lineline pipeline

**Output**:
```
✅ 最终行程（保定一日游）
━━━━━━━━━━━━━━━━━━━━

📅 2026-03-22（周六）晴转多云 15-22°C

⏰ 时间表
━━━━━━━━━━━━━━━━━━━━
09:15 🚄 到达保定站
09:30 🚲 出站 → 直隶总督署
      导航：https://uri.amap.com/...
09:45 🏛️ 直隶总督署（60分钟）
      门票：¥30（现场购买）
      
... [详细每个环节]

💡 备选方案
━━━━━━━━━━━━━━━━━━━━
• 下雨：博物馆路线（室内景点）
• 太累：缩短为上午半日游
• 景点关闭：改去竞秀公园

🎒 必带物品
━━━━━━━━━━━━━━━━━━━━
• 身份证（景点实名）
• 充电宝（拍照+导航）
• 遮阳伞（下午晴热）
• 零食+水（节省时间）

🔗 已创建 lineline pipeline
━━━━━━━━━━━━━━━━━━━━
运行以下命令进入阶段2（旅行打卡）：
  lineline advance <pipeline-id>
```

## Script Tools 🛠️

### 1. Attraction Discovery (`scripts/discover_attractions.py`)

```bash
python3 scripts/discover_attractions.py 保定 --count 20
```

Uses Exa to search and extract:
- Tourist sites
- Food spots
- Industrial/creative spaces
- Universities
- Parks

Output: JSON with 20 locations

### 2. Geocoding (`scripts/geocode.py`)

```bash
python3 scripts/geocode.py "保定市直隶总督署"
```

Returns: `{"lat": 38.87, "lng": 115.46}`

### 3. Map Generator (`scripts/generate_map.py`)

```bash
python3 scripts/generate_map.py locations.json --output map.png
```

Generates static map with numbered markers.

### 4. Route Optimizer (`scripts/optimize_route.py`)

```bash
python3 scripts/optimize_route.py selected.json \
  --start-time "09:15" \
  --end-time "17:30" \
  --mode bike
```

Output: Optimized itinerary JSON

## Data Flow

```
budget-travel (前置)
  ↓
  输出：目的地+到达时间
  ↓
trip-planner (阶段1) ⭐
  ↓
  Round 1: discover_attractions.py → 20 locations
  Round 2: geocode.py + generate_map.py → map.png
  Round 3: optimize_route.py → itinerary.json
  Round 4: export to lineline
  ↓
travel-checkin (阶段2)
```

## Integration with Lineline Pipeline

When planning is complete:

1. Check if lineline is available
2. Create or update pipeline from `budget-travel` template
3. Attach itinerary JSON as stage 1 data
4. Advance to stage 2 (旅行打卡)

```python
# Save itinerary
itinerary_path = f"~/.openclaw/my-skills/lineline/data/itineraries/{trip_id}.json"
save_itinerary(itinerary, itinerary_path)

# Update pipeline
lineline_cli = "~/.openclaw/my-skills/lineline/dist/cli.js"
os.system(f"node {lineline_cli} attach {pipeline_id} {itinerary_path}")
```

## Natural Language Parsing

Trigger phrases:
- "详细规划一下"
- "具体怎么玩"
- "帮我优化路线"
- "plan my day"
- "generate itinerary"

Extract from context:
- Arrival time from budget-travel output
- City name from budget-travel
- Available hours

## Reference Documents

See `references/` for:
- `amap_api.md` - Amap API documentation (geocoding + static maps)
- `route_optimization.md` - TSP algorithms and heuristics
- `attraction_categories.md` - Search keywords for different attraction types

## Quick Start

**Minimal workflow**:
1. User: "我周六9点到保定，帮我规划一天"
2. Agent: Discover 20 attractions → show list
3. User: Select 5-7 attractions
4. Agent: Generate map → show image
5. Agent: Optimize route → show timeline
6. User: Confirm
7. Agent: Export to lineline → ready for stage 2

**No API key needed**:
- Exa search is free (via mcporter)
- Map generation can use OpenStreetMap fallback
- Route optimization is pure algorithm (no API)

Optional enhancements:
- Amap API for better China maps
- Real-time traffic data
- Indoor navigation for museums

## Response Style

Keep multi-round interactions engaging:
- Use emojis for visual clarity
- Number all options clearly
- Provide previews (map thumbnails)
- Summarize before moving to next round
- Allow backtracking ("返回上一步")

Example:
```
第1轮：景点发现 ✅
第2轮：地图查看 ← 当前
第3轮：路线优化
第4轮：最终确认
```
