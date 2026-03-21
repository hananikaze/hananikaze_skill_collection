---
name: html-to-pdf
description: Convert HTML to PDF using Playwright (Chromium headless rendering). Supports complex layouts, CSS, JavaScript, interactive maps (Leaflet/Folium), charts (ECharts), and any modern web content. Use when generating PDF reports, travel itineraries with maps, data visualizations, or any HTML document that needs perfect browser-quality rendering. Triggers on "生成PDF", "导出报告", "html转pdf", "render to pdf", "generate report".
---

# HTML to PDF Converter

High-quality PDF generation using Playwright's Chromium headless browser. Perfect for reports, itineraries, and any complex HTML/CSS/JS content.

## Overview

Converts HTML (file or string) to PDF with full browser rendering support:
- ✅ Modern CSS (Flexbox, Grid, animations)
- ✅ JavaScript execution (charts, maps, interactive elements)
- ✅ Web fonts, images, SVG
- ✅ Perfect layout consistency with real browsers
- ✅ Page breaks, headers, footers
- ✅ Print-optimized styling (@media print)

## Use Cases

1. **Travel Itinerary Reports** (for trip-planner)
   - Maps with Leaflet/Folium
   - Route visualization
   - Timeline with locations
   
2. **Data Reports**
   - Charts (ECharts, Chart.js)
   - Tables, graphs
   - Statistics dashboards

3. **Documentation**
   - Technical docs
   - User manuals
   - Style guides

## Installation

First-time setup (one-time only):

```bash
# Install Playwright
pip3 install playwright

# Install Chromium browser (~300MB)
playwright install chromium
```

**Optional**: Install system dependencies if needed:
```bash
# macOS (usually not needed)
# Linux may need: sudo apt-get install libnss3 libatk1.0-0 ...
```

## Usage

### Basic: Convert HTML file to PDF

```bash
python3 scripts/html_to_pdf.py input.html output.pdf
```

### From HTML string

```bash
python3 scripts/html_to_pdf.py --html "<h1>Hello</h1>" output.pdf
```

### With options

```bash
python3 scripts/html_to_pdf.py input.html output.pdf \
  --format A4 \
  --landscape \
  --margin "20mm" \
  --header-html "<div>Header</div>" \
  --footer-html "<div>Page <span class='pageNumber'></span></div>"
```

### Python API

```python
from html_to_pdf import render_pdf

# From file
render_pdf(
    input_html="report.html",
    output_pdf="report.pdf",
    format="A4",
    landscape=False,
    margin="10mm"
)

# From string
html_content = """
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial; }
    .highlight { color: red; }
  </style>
</head>
<body>
  <h1>My Report</h1>
  <div class="highlight">Important!</div>
</body>
</html>
"""

render_pdf(
    html_string=html_content,
    output_pdf="report.pdf"
)
```

## Options

### Page Format
- `--format`: Paper size (A4, Letter, A3, Legal, etc.)
- `--width`, `--height`: Custom dimensions (e.g., "210mm", "8.5in")
- `--landscape`: Landscape orientation (default: portrait)

### Margins
- `--margin`: All margins (e.g., "10mm")
- `--margin-top`, `--margin-right`, `--margin-bottom`, `--margin-left`: Individual margins

### Headers & Footers
- `--header-html`: HTML content for header
- `--footer-html`: HTML content for footer
- Special variables in headers/footers:
  - `<span class='pageNumber'></span>` - Current page number
  - `<span class='totalPages'></span>` - Total pages
  - `<span class='url'></span>` - Document URL
  - `<span class='title'></span>` - Document title
  - `<span class='date'></span>` - Print date

### Rendering
- `--wait-for`: Wait for selector before printing (e.g., `#map-loaded`)
- `--wait-timeout`: Max wait time in milliseconds (default: 30000)
- `--scale`: Zoom scale (0.1 to 2, default: 1)
- `--print-background`: Include background graphics (default: true)

### Advanced
- `--display-header-footer`: Show default header/footer
- `--prefer-css-page-size`: Use CSS-defined page size

## Examples

### Travel Itinerary with Map

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>北京一日游行程</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body { font-family: "PingFang SC", Arial; margin: 0; }
    .header { background: #4CAF50; color: white; padding: 20px; }
    #map { height: 400px; margin: 20px; }
    .timeline { margin: 20px; }
    .timeline-item { margin: 10px 0; padding: 10px; border-left: 3px solid #4CAF50; }
    @media print {
      body { -webkit-print-color-adjust: exact; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>北京一日游行程</h1>
    <p>2026-03-22 | 总预算：¥350 | 总距离：12km</p>
  </div>
  
  <div id="map"></div>
  
  <div class="timeline">
    <h2>详细行程</h2>
    <div class="timeline-item">
      <strong>09:15</strong> 到达北京站
    </div>
    <div class="timeline-item">
      <strong>09:30</strong> 天安门广场 (60分钟)
    </div>
    <!-- More items... -->
  </div>
  
  <script>
    // Initialize map
    var map = L.map('map').setView([39.9042, 116.4074], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    // Add markers
    L.marker([39.9042, 116.4074]).addTo(map).bindPopup('天安门');
    L.marker([39.9163, 116.3972]).addTo(map).bindPopup('故宫');
    // More markers...
    
    // Signal ready
    document.body.classList.add('map-loaded');
  </script>
</body>
</html>
```

**Generate PDF**:
```bash
python3 scripts/html_to_pdf.py itinerary.html itinerary.pdf \
  --wait-for ".map-loaded" \
  --format A4 \
  --margin "15mm"
```

### Data Report with Chart

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    .chart-container { width: 80%; margin: 20px auto; }
  </style>
</head>
<body>
  <h1>花费统计报告</h1>
  <div class="chart-container">
    <canvas id="expenseChart"></canvas>
  </div>
  <script>
    const ctx = document.getElementById('expenseChart');
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['交通', '餐饮', '门票', '其他'],
        datasets: [{
          data: [50, 150, 100, 50],
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
        }]
      }
    });
    document.body.classList.add('chart-ready');
  </script>
</body>
</html>
```

## Template System

Assets folder contains ready-to-use templates:

### `assets/report_template.html`
Basic report structure with header, content area, footer.

### `assets/itinerary_template.html`
Travel itinerary with map, timeline, expense summary.

### Using templates:
```python
from html_to_pdf import render_from_template

data = {
    'title': '北京一日游',
    'date': '2026-03-22',
    'locations': [
        {'name': '天安门', 'lat': 39.9042, 'lng': 116.4074, 'time': '09:30'},
        {'name': '故宫', 'lat': 39.9163, 'lng': 116.3972, 'time': '11:00'}
    ],
    'expenses': {'交通': 50, '餐饮': 150, '门票': 100}
}

render_from_template(
    template='assets/itinerary_template.html',
    data=data,
    output_pdf='itinerary.pdf'
)
```

## Integration with trip-planner

In trip-planner's final stage, generate PDF report:

```python
# trip-planner calls html-to-pdf
import subprocess

html_content = generate_itinerary_html(itinerary_data)
with open('/tmp/itinerary.html', 'w') as f:
    f.write(html_content)

subprocess.run([
    'python3',
    '~/.openclaw/my-skills/html-to-pdf/scripts/html_to_pdf.py',
    '/tmp/itinerary.html',
    '/tmp/itinerary.pdf',
    '--format', 'A4',
    '--margin', '15mm',
    '--wait-for', '.map-loaded'
])

# Send PDF via QQ
print(f"<qqfile>/tmp/itinerary.pdf</qqfile>")
```

## Troubleshooting

### "playwright not installed"
```bash
pip3 install playwright
playwright install chromium
```

### "chromium browser not found"
```bash
playwright install chromium
```

### Map/chart not rendering
- Use `--wait-for` to wait for element
- Increase `--wait-timeout` (default 30s)
- Check JavaScript console errors

### Fonts missing (Chinese characters)
macOS usually fine. Linux may need:
```bash
sudo apt-get install fonts-noto-cjk
```

### Large file size
- Optimize images before embedding
- Use CSS `@media print` to hide unnecessary elements
- Consider `--scale 0.9` to reduce page count

## Performance

- First run: ~3-5 seconds (browser startup)
- Subsequent: ~1-2 seconds
- Complex pages with JS: +2-3 seconds

Tips:
- Keep Chromium running between conversions (batch processing)
- Pre-optimize images
- Minimize external resources

## Limitations

- Requires ~300MB for Chromium
- Not suitable for serverless (use WeasyPrint instead)
- JavaScript execution adds latency

## Advanced: Custom Page Breaks

```html
<style>
  .page-break { page-break-after: always; }
  @media print {
    h1 { page-break-before: always; }
  }
</style>

<div>Page 1 content</div>
<div class="page-break"></div>
<div>Page 2 content</div>
```

## See Also

- Playwright docs: https://playwright.dev/python/docs/api/class-page#page-pdf
- Leaflet (maps): https://leafletjs.com
- Chart.js: https://www.chartjs.org
