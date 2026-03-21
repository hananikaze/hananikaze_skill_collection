# Amap API Reference

## Geocoding API (地理编码)

Convert address to coordinates.

**Endpoint**: `https://restapi.amap.com/v3/geocode/geo`

**Parameters**:
- `key` - API key (from https://console.amap.com)
- `address` - Address string (e.g., "北京市朝阳区阜通东大街6号")
- `city` - Optional city filter (e.g., "北京")

**Example**:
```bash
curl "https://restapi.amap.com/v3/geocode/geo?address=北京市天安门&key=YOUR_KEY"
```

**Response**:
```json
{
  "status": "1",
  "geocodes": [{
    "formatted_address": "北京市东城区天安门",
    "location": "116.397499,39.908722"
  }]
}
```

**Python wrapper**:
```python
import requests

def geocode(address, city=None, api_key=None):
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {"key": api_key, "address": address}
    if city:
        params["city"] = city
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == '1' and data['geocodes']:
        location = data['geocodes'][0]['location']
        lng, lat = map(float, location.split(','))
        return {"lat": lat, "lng": lng}
    
    return None
```

## Static Map API (静态地图)

Generate map image with markers.

**Endpoint**: `https://restapi.amap.com/v3/staticmap`

**Parameters**:
- `key` - API key
- `markers` - Marker definitions (see below)
- `size` - Image size (e.g., "800*600")
- `zoom` - Zoom level (3-18, default auto)
- `scale` - Resolution (1 or 2 for retina)

**Marker format**:
```
size,color,label:lng1,lat1;lng2,lat2|size,color:lng3,lat3
```

Examples:
- `mid,0xFF0000,A:116.37,39.86` - Medium red marker with label "A"
- `small,0x0000FF:116.38,39.87` - Small blue marker
- Multiple: `mid,0xFF0000:116.37,39.86|116.38,39.87|116.39,39.88`

**Example**:
```bash
curl "https://restapi.amap.com/v3/staticmap?\
markers=mid,0xFF0000,1:116.397499,39.908722|\
mid,0x00FF00,2:116.407499,39.918722&\
size=800*600&zoom=13&key=YOUR_KEY" \
--output map.png
```

**Python wrapper**:
```python
import requests

def generate_static_map(locations, output_path, api_key):
    """
    locations: [{"name": "天安门", "lat": 39.90, "lng": 116.39}, ...]
    """
    # Build markers
    marker_strs = []
    for i, loc in enumerate(locations, 1):
        marker_strs.append(f"{loc['lng']},{loc['lat']}")
    
    markers = f"mid,0xFF0000:{';'.join(marker_strs)}"
    
    url = "https://restapi.amap.com/v3/staticmap"
    params = {
        "key": api_key,
        "markers": markers,
        "size": "800*600",
        "zoom": 13,
        "scale": 2
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    
    return False
```

## API Key Setup

1. Register at https://console.amap.com/dev/key/app
2. Create new key (Web service type)
3. Set environment variable:
   ```bash
   export AMAP_API_KEY="your_key_here"
   ```
4. Or store in config file:
   ```bash
   echo "your_key" > ~/.amap_api_key
   ```

## Fallback: OpenStreetMap

If no Amap API key, use OSM + Python:

```python
import folium

def generate_map_osm(locations, output_path):
    # Calculate center
    avg_lat = sum(loc['lat'] for loc in locations) / len(locations)
    avg_lng = sum(loc['lng'] for loc in locations) / len(locations)
    
    # Create map
    m = folium.Map(location=[avg_lat, avg_lng], zoom_start=13)
    
    # Add markers
    for i, loc in enumerate(locations, 1):
        folium.Marker(
            [loc['lat'], loc['lng']],
            popup=f"{i}. {loc['name']}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # Save
    m.save(output_path)
```

Requires: `pip install folium`
