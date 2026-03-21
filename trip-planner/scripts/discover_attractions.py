#!/usr/bin/env python3
"""
Attraction Discovery Tool
Uses Exa (via mcporter) to discover attractions in a city.
"""

import json
import subprocess
import sys
from typing import List, Dict

def exa_search(query: str, num_results: int = 5) -> List[Dict]:
    """Search using Exa via mcporter (agent-reach)."""
    cmd = [
        "mcporter", "call",
        f"exa.web_search_exa(query: \"{query}\", numResults: {num_results})"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"⚠️ Exa search failed: {result.stderr}", file=sys.stderr)
            return []
        
        # Parse mcporter output
        # Output format: multiple sections with Title/URL/Highlights
        results = []
        output = result.stdout
        
        # Split by "---" or parse line by line
        sections = output.split('\n---\n')
        for section in sections:
            if 'Title:' in section and 'URL:' in section:
                lines = section.split('\n')
                title = ""
                url = ""
                text = ""
                
                for line in lines:
                    if line.startswith('Title:'):
                        title = line.replace('Title:', '').strip()
                    elif line.startswith('URL:'):
                        url = line.replace('URL:', '').strip()
                    elif line.startswith('Highlights:'):
                        # Rest is content
                        idx = section.index('Highlights:')
                        text = section[idx+11:].strip()
                        break
                
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'text': text[:500]  # Truncate
                    })
        
        return results
    except Exception as e:
        print(f"⚠️ Exa search error: {e}", file=sys.stderr)
        return []


def discover_attractions(city: str, count: int = 20) -> List[Dict]:
    """
    Discover attractions in a city across multiple categories.
    
    Returns list of:
    {
        "name": str,
        "category": str,
        "description": str,
        "address": str (if available),
        "duration_minutes": int (estimate),
        "cost": str
    }
    """
    categories = {
        "🏛️ 历史文化": f"{city} 景点 博物馆 古迹 文物",
        "🍜 美食体验": f"{city} 美食街 小吃 特色餐厅",
        "🏭 工业创新": f"{city} 工业园区 创客空间 科技园",
        "🎨 艺术文创": f"{city} 艺术区 文创园 画廊",
        "🏫 大学校园": f"{city} 大学 校园",
        "🌳 公园自然": f"{city} 公园 湖泊 自然景观",
        "📚 文化场馆": f"{city} 图书馆 书店 文化中心",
        "🏪 本地市场": f"{city} 市场 集市 夜市"
    }
    
    all_attractions = []
    per_category = max(count // len(categories), 2)
    
    print(f"🔍 正在搜索 {city} 的景点...")
    
    for category, query in categories.items():
        print(f"  搜索 {category}...", end="")
        results = exa_search(query, num_results=per_category)
        
        for result in results:
            attraction = {
                "name": result.get('title', '未知'),
                "category": category,
                "description": result.get('text', '')[:100],  # First 100 chars
                "url": result.get('url', ''),
                "address": extract_address(result.get('text', '')),
                "duration_minutes": estimate_duration(category),
                "cost": estimate_cost(category)
            }
            all_attractions.append(attraction)
        
        print(f" ✓ {len(results)} 个")
    
    # Deduplicate by name
    seen = set()
    unique = []
    for attr in all_attractions:
        if attr['name'] not in seen:
            seen.add(attr['name'])
            unique.append(attr)
    
    # Return top N
    return unique[:count]


def extract_address(text: str) -> str:
    """Try to extract address from text (简单启发式)."""
    # Look for patterns like "地址：", "位于", "XX路XX号"
    import re
    
    patterns = [
        r'地址[：:]\s*([^\n]+)',
        r'位于\s*([^\n]+)',
        r'([^,。\n]*[路街道巷][\d号]+[^,。\n]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return ""


def estimate_duration(category: str) -> int:
    """Estimate visit duration in minutes based on category."""
    duration_map = {
        "🏛️ 历史文化": 90,
        "🍜 美食体验": 30,
        "🏭 工业创新": 120,
        "🎨 艺术文创": 60,
        "🏫 大学校园": 60,
        "🌳 公园自然": 60,
        "📚 文化场馆": 90,
        "🏪 本地市场": 45
    }
    return duration_map.get(category, 60)


def estimate_cost(category: str) -> str:
    """Estimate cost based on category."""
    cost_map = {
        "🏛️ 历史文化": "¥20-60",
        "🍜 美食体验": "¥20-50",
        "🏭 工业创新": "免费/预约",
        "🎨 艺术文创": "免费-¥30",
        "🏫 大学校园": "免费",
        "🌳 公园自然": "免费-¥20",
        "📚 文化场馆": "免费",
        "🏪 本地市场": "看消费"
    }
    return cost_map.get(category, "未知")


def main():
    if len(sys.argv) < 2:
        print("Usage: discover_attractions.py <城市> [--count 20] [--output file.json]")
        sys.exit(1)
    
    city = sys.argv[1]
    count = 20
    output_file = None
    
    # Parse args
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--count":
            count = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--output":
            output_file = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Discover
    attractions = discover_attractions(city, count)
    
    # Output
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(attractions, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 已保存到 {output_file}")
    else:
        # Print to console
        print(f"\n📍 {len(attractions)} 个可选地点（{city}）")
        print("━" * 40)
        
        by_category = {}
        for attr in attractions:
            cat = attr['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(attr)
        
        idx = 1
        for category, items in by_category.items():
            print(f"\n{category}")
            for attr in items:
                duration_h = attr['duration_minutes'] // 60
                duration_m = attr['duration_minutes'] % 60
                duration_str = f"{duration_h}h" if duration_h else f"{duration_m}min"
                
                print(f"{idx}. {attr['name']} - {attr['description'][:50]}...")
                print(f"   ⏱️ {duration_str} | 💰 {attr['cost']}")
                if attr['address']:
                    print(f"   📍 {attr['address']}")
                idx += 1
        
        print(f"\n请选择感兴趣的地点（输入编号，如 1,3,5）")


if __name__ == "__main__":
    main()
