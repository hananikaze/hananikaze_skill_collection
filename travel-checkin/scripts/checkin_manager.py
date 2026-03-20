#!/usr/bin/env python3
"""
Travel Check-in Manager
Handles check-ins, expenses, and statistics for active trips.
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from math import radians, sin, cos, sqrt, atan2

# Paths
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
CURRENT_TRIP = DATA_DIR / "current_trip.json"
TRIPS_DIR = DATA_DIR / "trips"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
TRIPS_DIR.mkdir(exist_ok=True)


def get_timestamp() -> str:
    """Get current timestamp in Asia/Shanghai timezone."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")


def get_date() -> str:
    """Get current date."""
    return datetime.now().strftime("%Y-%m-%d")


def load_current_trip() -> Optional[Dict]:
    """Load current trip data."""
    if not CURRENT_TRIP.exists():
        return None
    with open(CURRENT_TRIP, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current_trip(data: Dict):
    """Save current trip data."""
    with open(CURRENT_TRIP, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def new_trip(destination: str) -> Dict:
    """Create a new trip."""
    trip_id = f"{get_date()}-{destination}"
    data = {
        "trip_id": trip_id,
        "destination": destination,
        "start_date": get_date(),
        "checkins": [],
        "expenses": []
    }
    save_current_trip(data)
    return data


def checkin(location: str, note: str = ""):
    """Record a check-in."""
    data = load_current_trip()
    if not data:
        print("❌ 没有活跃的旅行。请先创建新旅行或在第一次打卡时会自动创建。")
        sys.exit(1)
    
    checkin_entry = {
        "timestamp": get_timestamp(),
        "location": location,
        "note": note,
        "lat": None,
        "lng": None
    }
    data["checkins"].append(checkin_entry)
    save_current_trip(data)
    
    # Output
    time_str = datetime.now().strftime("%H:%M")
    count = len(data["checkins"])
    print(f"✅ 已打卡：{location}")
    if note:
        print(f"📝 备注：{note}")
    print(f"🕐 时间：{time_str}")
    print(f"📊 今日第 {count} 个打卡点")


def expense(category: str, amount: float, description: str = ""):
    """Record an expense."""
    data = load_current_trip()
    if not data:
        print("❌ 没有活跃的旅行。")
        sys.exit(1)
    
    expense_entry = {
        "timestamp": get_timestamp(),
        "category": category,
        "description": description,
        "amount": amount
    }
    data["expenses"].append(expense_entry)
    save_current_trip(data)
    
    # Calculate totals
    today = get_date()
    today_total = sum(e["amount"] for e in data["expenses"] 
                     if e["timestamp"].startswith(today))
    trip_total = sum(e["amount"] for e in data["expenses"])
    
    # Output
    desc_str = f" {description}" if description else ""
    print(f"✅ 已记录：{category}{desc_str} ¥{amount}")
    print(f"💵 今日累计：¥{today_total:.1f}")
    print(f"📊 本次旅行累计：¥{trip_total:.1f}")


def stats_today():
    """Show today's statistics."""
    data = load_current_trip()
    if not data:
        print("❌ 没有活跃的旅行。")
        sys.exit(1)
    
    today = get_date()
    today_checkins = [c for c in data["checkins"] 
                     if c["timestamp"].startswith(today)]
    today_expenses = [e for e in data["expenses"] 
                     if e["timestamp"].startswith(today)]
    
    # Calculate by category
    categories = {"交通": 0, "餐饮": 0, "门票": 0, "其他": 0}
    for exp in today_expenses:
        cat = exp["category"]
        if cat not in categories:
            categories["其他"] += exp["amount"]
        else:
            categories[cat] += exp["amount"]
    
    total = sum(categories.values())
    
    print(f"📊 今日统计 ({today})")
    print("━━━━━━━━━━━━━━━━━━━━")
    print(f"📍 打卡：{len(today_checkins)} 个地点")
    print(f"💰 花费：¥{total:.1f}")
    for cat, amt in categories.items():
        if amt > 0:
            print(f"  • {cat}：¥{amt:.1f}")


def stats_total():
    """Show trip total statistics."""
    data = load_current_trip()
    if not data:
        print("❌ 没有活跃的旅行。")
        sys.exit(1)
    
    start = datetime.strptime(data["start_date"], "%Y-%m-%d")
    today = datetime.now()
    days = (today - start).days + 1
    
    # Calculate by category
    categories = {"交通": 0, "餐饮": 0, "门票": 0, "其他": 0}
    for exp in data["expenses"]:
        cat = exp["category"]
        if cat not in categories:
            categories["其他"] += exp["amount"]
        else:
            categories[cat] += exp["amount"]
    
    total = sum(categories.values())
    
    print(f"🏁 本次旅行统计 - {data['destination']}")
    print("━━━━━━━━━━━━━━━━━━━━")
    print(f"📅 天数：{days} 天")
    print(f"💵 总花费：¥{total:.1f}")
    print(f"📍 总打卡：{len(data['checkins'])} 个地点")
    print()
    print("分类明细：")
    for cat, amt in categories.items():
        if amt > 0:
            pct = (amt / total * 100) if total > 0 else 0
            print(f"  • {cat}：¥{amt:.1f} ({pct:.0f}%)")


def end_trip():
    """End current trip and archive."""
    data = load_current_trip()
    if not data:
        print("❌ 没有活跃的旅行。")
        sys.exit(1)
    
    # Archive
    archive_path = TRIPS_DIR / f"{data['trip_id']}.json"
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Remove current
    CURRENT_TRIP.unlink()
    
    print(f"✅ 旅行已结束：{data['destination']}")
    print(f"📦 数据已归档：{archive_path}")
    
    # Show summary
    stats_total()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS points in kilometers."""
    R = 6371  # Earth radius in km
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def parse_gpx(gpx_path: str) -> List[Dict]:
    """Parse GPX file and extract track points."""
    tree = ET.parse(gpx_path)
    root = tree.getroot()
    
    # Handle GPX namespace
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    if not root.tag.endswith('gpx'):
        # Try without namespace
        ns = {}
    
    points = []
    
    # Try to find track points
    for trkpt in root.findall('.//gpx:trkpt', ns) or root.findall('.//trkpt'):
        lat = float(trkpt.get('lat'))
        lon = float(trkpt.get('lon'))
        
        # Extract time
        time_elem = trkpt.find('gpx:time', ns) or trkpt.find('time')
        timestamp = time_elem.text if time_elem is not None else None
        
        # Extract elevation (optional)
        ele_elem = trkpt.find('gpx:ele', ns) or trkpt.find('ele')
        elevation = float(ele_elem.text) if ele_elem is not None else None
        
        points.append({
            'lat': lat,
            'lon': lon,
            'timestamp': timestamp,
            'elevation': elevation
        })
    
    return points


def import_gpx(gpx_path: str, date_filter: Optional[str] = None):
    """Import GPX track and merge with current trip."""
    data = load_current_trip()
    if not data:
        print("❌ 没有活跃的旅行。请先创建旅行或进行首次打卡。")
        sys.exit(1)
    
    print(f"📂 解析 GPX 文件：{gpx_path}")
    
    try:
        points = parse_gpx(gpx_path)
    except Exception as e:
        print(f"❌ GPX 解析失败：{e}")
        sys.exit(1)
    
    if not points:
        print("❌ GPX 文件中没有找到轨迹点")
        sys.exit(1)
    
    # Filter by date if specified
    if date_filter:
        points = [p for p in points if p['timestamp'] and p['timestamp'].startswith(date_filter)]
    
    # Calculate statistics
    if len(points) < 2:
        print(f"⚠️ 轨迹点太少（{len(points)} 个），无法计算距离")
        total_distance = 0
    else:
        total_distance = 0
        for i in range(1, len(points)):
            p1, p2 = points[i-1], points[i]
            total_distance += haversine_distance(p1['lat'], p1['lon'], p2['lat'], p2['lon'])
    
    # Add GPS track to trip data
    if 'gps_tracks' not in data:
        data['gps_tracks'] = []
    
    track_entry = {
        'imported_at': get_timestamp(),
        'source_file': os.path.basename(gpx_path),
        'point_count': len(points),
        'total_distance_km': round(total_distance, 2),
        'date_filter': date_filter,
        'time_range': {
            'start': points[0]['timestamp'] if points[0]['timestamp'] else None,
            'end': points[-1]['timestamp'] if points[-1]['timestamp'] else None
        },
        'points': points
    }
    
    data['gps_tracks'].append(track_entry)
    save_current_trip(data)
    
    # Output
    print(f"✅ GPS 轨迹已导入")
    print(f"📍 轨迹点：{len(points)} 个")
    if total_distance > 0:
        print(f"🚶 总距离：{total_distance:.2f} km")
    if points[0]['timestamp'] and points[-1]['timestamp']:
        start_time = points[0]['timestamp'][:19]
        end_time = points[-1]['timestamp'][:19]
        print(f"⏱️ 时间范围：{start_time} ~ {end_time}")
    
    # Match with check-ins
    matched = match_checkins_with_gps(data, points)
    if matched:
        save_current_trip(data)
        print(f"\n🎯 已为 {matched} 个打卡点补充 GPS 坐标")


def match_checkins_with_gps(data: Dict, gps_points: List[Dict]) -> int:
    """Match check-ins with nearby GPS points and add coordinates."""
    matched_count = 0
    
    for checkin in data['checkins']:
        if checkin.get('lat') is not None:
            continue  # Already has GPS
        
        # Parse checkin timestamp
        try:
            checkin_time = datetime.fromisoformat(checkin['timestamp'].replace('+08:00', ''))
        except:
            continue
        
        # Find GPS points within ±10 minutes
        nearby_points = []
        for gps in gps_points:
            if not gps['timestamp']:
                continue
            try:
                gps_time = datetime.fromisoformat(gps['timestamp'].replace('Z', ''))
                time_diff = abs((gps_time - checkin_time).total_seconds())
                if time_diff <= 600:  # 10 minutes
                    nearby_points.append((time_diff, gps))
            except:
                continue
        
        if nearby_points:
            # Use closest point
            nearby_points.sort(key=lambda x: x[0])
            closest_gps = nearby_points[0][1]
            checkin['lat'] = closest_gps['lat']
            checkin['lon'] = closest_gps['lon']
            matched_count += 1
    
    return matched_count


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  checkin_manager.py new-trip --destination <地点>")
        print("  checkin_manager.py checkin <地点> [--note <备注>]")
        print("  checkin_manager.py expense --category <类别> --amount <金额> [--description <描述>]")
        print("  checkin_manager.py stats today|total")
        print("  checkin_manager.py import-gpx <GPX文件路径> [--date YYYY-MM-DD]")
        print("  checkin_manager.py end-trip")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "new-trip":
        if "--destination" not in sys.argv:
            print("❌ 需要指定 --destination")
            sys.exit(1)
        dest_idx = sys.argv.index("--destination") + 1
        destination = sys.argv[dest_idx]
        data = new_trip(destination)
        print(f"✅ 新旅行已创建：{destination}")
        print(f"📅 开始日期：{data['start_date']}")
    
    elif command == "checkin":
        if len(sys.argv) < 3:
            print("❌ 需要指定地点")
            sys.exit(1)
        location = sys.argv[2]
        note = ""
        if "--note" in sys.argv:
            note_idx = sys.argv.index("--note") + 1
            note = sys.argv[note_idx]
        
        # Auto-create trip if needed
        if not load_current_trip():
            print("🆕 检测到首次打卡，请问目的地是？")
            destination = input("目的地: ").strip()
            if not destination:
                destination = location
            new_trip(destination)
        
        checkin(location, note)
    
    elif command == "expense":
        if "--category" not in sys.argv or "--amount" not in sys.argv:
            print("❌ 需要指定 --category 和 --amount")
            sys.exit(1)
        cat_idx = sys.argv.index("--category") + 1
        amt_idx = sys.argv.index("--amount") + 1
        category = sys.argv[cat_idx]
        amount = float(sys.argv[amt_idx])
        description = ""
        if "--description" in sys.argv:
            desc_idx = sys.argv.index("--description") + 1
            description = sys.argv[desc_idx]
        expense(category, amount, description)
    
    elif command == "stats":
        if len(sys.argv) < 3:
            print("❌ 需要指定 today 或 total")
            sys.exit(1)
        stat_type = sys.argv[2]
        if stat_type == "today":
            stats_today()
        elif stat_type == "total":
            stats_total()
        else:
            print(f"❌ 未知统计类型：{stat_type}")
            sys.exit(1)
    
    elif command == "import-gpx":
        if len(sys.argv) < 3:
            print("❌ 需要指定 GPX 文件路径")
            sys.exit(1)
        gpx_path = sys.argv[2]
        if not os.path.exists(gpx_path):
            print(f"❌ 文件不存在：{gpx_path}")
            sys.exit(1)
        
        date_filter = None
        if "--date" in sys.argv:
            date_idx = sys.argv.index("--date") + 1
            date_filter = sys.argv[date_idx]
        
        import_gpx(gpx_path, date_filter)
    
    elif command == "end-trip":
        end_trip()
    
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
