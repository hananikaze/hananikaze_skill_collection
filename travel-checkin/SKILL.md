---
name: travel-checkin
description: Travel check-in and expense tracking for active trips. Record location check-ins, expenses (transport/food/tickets/other), and view daily/total statistics. Integrates with lineline pipeline "旅行打卡" stage. Use when user is traveling and wants to check-in at locations, record expenses, or view spending statistics. Triggers on phrases like "打卡", "check-in", "花费", "记账", "今日统计", "总花费", or when user shares location/expense information during a trip.
---

# Travel Check-in (旅行打卡)

Record your travel journey in real-time: location check-ins, expenses, and statistics. This is the second stage of the budget travel pipeline.

## Core Commands

### 1. Check-in at Location 📍

**Format**: `打卡 <地点名称> [备注]`

**Examples**:
```
打卡 天坛公园
打卡 午饭 庆丰包子铺
打卡 景山公园 爬到山顶了
```

**Response**:
```
✅ 已打卡：天坛公园
🕐 时间：07:18
📊 今日第 3 个打卡点
```

### 2. Record Expense 💰

**Format**: `花费 <类别> [描述] <金额>`

**Categories** (类别):
- 交通 - buses, bikes, subway
- 餐饮 - food and drinks
- 门票 - attraction tickets
- 其他 - miscellaneous

**Examples**:
```
花费 门票 15
花费 午饭 麻辣烫 35
花费 交通 共享单车 1.5
花费 其他 明信片 8
```

**Response**:
```
✅ 已记录：午饭 ¥35
💵 今日累计：¥51.5
📊 本次旅行累计：¥218.5
```

### 4. Import GPS Track 🗺️

**Format**: `导入轨迹 <GPX文件>` or provide GPX file directly

**Examples**:
```
导入轨迹 /path/to/track.gpx
导入轨迹 2026-03-21.gpx --date 2026-03-21
```

**Response**:
```
✅ GPS 轨迹已导入
📍 轨迹点：1847 个
🚶 总距离：12.35 km
⏱️ 时间范围：2026-03-21 08:00 ~ 18:30

🎯 已为 5 个打卡点补充 GPS 坐标
```

**How it works**:
- Parses GPX file from phone's GPS logger
- Calculates total distance traveled
- Auto-matches check-ins with nearby GPS points (±10 min)
- Adds coordinates to existing check-ins
- Stores complete track for later visualization

**Supported sources**:
- iPhone Health app (export as GPX)
- Android GPSLogger
- Strava/Nike Run Club export
- Any standard GPX 1.1 file

**Commands**:
- `今日统计` - today's summary
- `总花费` or `总统计` - trip total summary

### 3. View Statistics 📊

**Commands**:
- `今日统计` - today's summary
- `总花费` or `总统计` - trip total summary

**Example Response**:
```
📊 今日统计 (2026-03-21)
━━━━━━━━━━━━━━━━━━━━
📍 打卡：5 个地点
💰 花费：¥127.5
  • 交通：¥12.5 (共享单车×3, 地铁×1)
  • 餐饮：¥85 (早餐×1, 午餐×1, 晚餐×1)
  • 门票：¥30 (天坛公园)
  • 其他：¥0

🏁 本次旅行累计
━━━━━━━━━━━━━━━━━━━━
📅 天数：2 天
💵 总花费：¥345.5
📍 总打卡：12 个地点
🗺️ GPS 轨迹：24.7 km
```

## Data Storage 📂

All data is stored in `data/` directory (gitignored, local-only):

```
travel-checkin/
└── data/
    ├── current_trip.json          # Active trip data
    └── trips/
        └── 2026-03-20-changsha.json  # Archived trips
```

### Data Format

**current_trip.json**:
```json
{
  "trip_id": "2026-03-20-changsha",
  "destination": "长沙",
  "start_date": "2026-03-20",
  "checkins": [
    {
      "timestamp": "2026-03-21T07:18:00+08:00",
      "location": "天坛公园",
      "note": "",
      "lat": 39.8822,
      "lng": 116.4066
    }
  ],
  "expenses": [
    {
      "timestamp": "2026-03-21T07:30:00+08:00",
      "category": "门票",
      "description": "天坛公园",
      "amount": 15.0
    }
  ],
  "gps_tracks": [
    {
      "imported_at": "2026-03-21T20:00:00+08:00",
      "source_file": "2026-03-21.gpx",
      "point_count": 1847,
      "total_distance_km": 12.35,
      "date_filter": "2026-03-21",
      "time_range": {
        "start": "2026-03-21T08:00:00Z",
        "end": "2026-03-21T18:30:00Z"
      },
      "points": [...]
    }
  ]
}
```

## Workflow Integration 🔗

### Lineline Pipeline Integration

When user first checks in during a trip:

1. Check if lineline is available: `~/.openclaw/my-skills/lineline/dist/cli.js`
2. Check for active pipeline with template `budget-travel`
3. If found and current stage is "旅行打卡" → link this trip to that pipeline
4. Update pipeline metadata with trip_id reference

### Starting a New Trip

When user makes first check-in and no current trip exists:

1. Ask: "检测到新旅行，目的地是？"
2. Create `current_trip.json` with destination and start_date
3. Optional: Try to link to existing pipeline

### Ending a Trip

When user says "结束旅行" or similar:

1. Archive `current_trip.json` → `trips/YYYY-MM-DD-destination.json`
2. Generate trip summary
3. If linked to pipeline, advance to next stage (游记与总结)

## Script Usage 📜

Use `scripts/checkin_manager.py` for all operations:

```bash
# Check-in at location
python3 scripts/checkin_manager.py checkin "天坛公园" --note "爬到山顶了"

# Record expense
python3 scripts/checkin_manager.py expense --category 门票 --description "天坛公园" --amount 15

# View statistics
python3 scripts/checkin_manager.py stats today
python3 scripts/checkin_manager.py stats total

# Start new trip
python3 scripts/checkin_manager.py new-trip --destination 长沙

# End trip
python3 scripts/checkin_manager.py end-trip

# Import GPX track
python3 scripts/checkin_manager.py import-gpx /path/to/track.gpx
python3 scripts/checkin_manager.py import-gpx track.gpx --date 2026-03-21
```

Script handles:
- ✅ JSON file creation/updates
- ✅ Timestamp generation (Asia/Shanghai timezone)
- ✅ Statistics calculation
- ✅ Data validation
- ✅ Archive management
- ✅ GPX parsing and distance calculation
- ✅ Auto-matching check-ins with GPS coordinates

## Natural Language Parsing

Parse user input flexibly:

**Check-in patterns**:
- "打卡 X"
- "到了 X"
- "在 X"
- "check-in X"

**Expense patterns**:
- "花费 类别 金额"
- "花了 金额"
- "X 花了 Y 元"
- "买 X Y元"

Extract:
- Category from keywords (门票/交通/餐饮/吃饭/午饭/晚饭/早餐)
- Amount from numbers (支持 15/15.5/十五/一块五)
- Description from remaining text

## Quick Start (Minimum Viable Product)

For immediate use during travel:

1. **No setup needed** - first check-in auto-creates files
2. **QQ-based** - all interactions via QQ messages
3. **Manual check-ins** - text-based location recording
4. **Simple expenses** - quick category + amount recording
5. **Instant stats** - anytime summary on demand
6. **GPX import** - add GPS tracks after trip ends

**Workflow**:
```
旅行前：无需配置
  ↓
旅行中：手动打卡 + 记账（QQ消息）
  ↓
旅行后：导入手机 GPX → 自动补全坐标 → 完整轨迹
```

**How to export GPX from phone**:

**iPhone**:
1. 健康 app → 个人 → 运动与健身 → 导出健康数据
2. 解压 export.zip → workout-routes/route_*.gpx
3. 或使用第三方 GPS 记录 app（如 Trails）

**Android**:
1. 安装 GPSLogger app
2. 记录轨迹 → 分享 → GPX 格式
3. 或从 Google Timeline 导出

Future enhancements (v2):
- Real-time GPS tracking (OwnTracks integration)
- Automatic navigation generation (Amap links)
- Photo/media attachments
- Route visualization on map
- Budget comparison with planning stage

## Response Style

Keep responses concise and emoji-rich for mobile reading:

✅ Success → single line + key info
📊 Statistics → structured, scannable
⚠️ Errors → brief, actionable

Example:
```
✅ 已打卡：天坛公园 [07:18]
💰 今日第 3 个地点 | 累计花费 ¥127.5
```

Avoid:
- Long paragraphs
- Unnecessary confirmations
- Verbose explanations
