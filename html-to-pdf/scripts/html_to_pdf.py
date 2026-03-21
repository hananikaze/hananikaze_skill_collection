#!/usr/bin/env python3
"""
HTML to PDF Converter using Playwright
High-quality PDF generation with full browser rendering.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any


def render_pdf(
    input_html: Optional[str] = None,
    html_string: Optional[str] = None,
    output_pdf: str = "output.pdf",
    format: str = "A4",
    landscape: bool = False,
    width: Optional[str] = None,
    height: Optional[str] = None,
    margin: Optional[str] = None,
    margin_top: Optional[str] = None,
    margin_right: Optional[str] = None,
    margin_bottom: Optional[str] = None,
    margin_left: Optional[str] = None,
    header_html: Optional[str] = None,
    footer_html: Optional[str] = None,
    display_header_footer: bool = False,
    wait_for: Optional[str] = None,
    wait_timeout: int = 30000,
    scale: float = 1.0,
    print_background: bool = True,
    prefer_css_page_size: bool = False
) -> bool:
    """
    Render HTML to PDF using Playwright.
    
    Args:
        input_html: Path to HTML file
        html_string: HTML content as string
        output_pdf: Output PDF path
        format: Paper format (A4, Letter, etc.)
        landscape: Landscape orientation
        width, height: Custom page dimensions
        margin: All margins (e.g., "10mm")
        margin_*: Individual margins
        header_html, footer_html: Header/footer HTML
        display_header_footer: Show default header/footer
        wait_for: CSS selector to wait for
        wait_timeout: Wait timeout in ms
        scale: Page scale (0.1-2)
        print_background: Include backgrounds
        prefer_css_page_size: Use CSS page size
    
    Returns:
        True if successful
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed. Run:")
        print("   pip3 install playwright")
        print("   playwright install chromium")
        return False
    
    # Read HTML content
    if input_html:
        html_path = Path(input_html).resolve()
        if not html_path.exists():
            print(f"❌ File not found: {input_html}")
            return False
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        base_url = f"file://{html_path.parent}/"
    elif html_string:
        html_content = html_string
        base_url = "about:blank"
    else:
        print("❌ Must provide either input_html or html_string")
        return False
    
    # Build PDF options
    pdf_options: Dict[str, Any] = {
        'format': format,
        'landscape': landscape,
        'print_background': print_background,
        'prefer_css_page_size': prefer_css_page_size,
        'scale': scale
    }
    
    # Custom dimensions
    if width:
        pdf_options['width'] = width
    if height:
        pdf_options['height'] = height
    
    # Margins
    if margin:
        pdf_options['margin'] = {
            'top': margin,
            'right': margin,
            'bottom': margin,
            'left': margin
        }
    else:
        margins = {}
        if margin_top:
            margins['top'] = margin_top
        if margin_right:
            margins['right'] = margin_right
        if margin_bottom:
            margins['bottom'] = margin_bottom
        if margin_left:
            margins['left'] = margin_left
        if margins:
            pdf_options['margin'] = margins
    
    # Headers & footers
    if display_header_footer or header_html or footer_html:
        pdf_options['display_header_footer'] = True
        if header_html:
            pdf_options['header_template'] = header_html
        if footer_html:
            pdf_options['footer_template'] = footer_html
    
    # Render
    print(f"🚀 Starting Chromium...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"📄 Loading HTML...")
        page.set_content(html_content, wait_until='load')
        
        # Wait for specific element if requested
        if wait_for:
            print(f"⏳ Waiting for: {wait_for}")
            try:
                page.wait_for_selector(wait_for, timeout=wait_timeout)
            except Exception as e:
                print(f"⚠️ Wait timeout: {e}")
        
        print(f"🖨️ Generating PDF...")
        page.pdf(path=output_pdf, **pdf_options)
        
        browser.close()
    
    output_path = Path(output_pdf).resolve()
    print(f"✅ PDF generated: {output_path}")
    print(f"📦 Size: {output_path.stat().st_size / 1024:.1f} KB")
    
    return True


def render_from_template(
    template: str,
    data: Dict[str, Any],
    output_pdf: str,
    **kwargs
) -> bool:
    """
    Render PDF from template file with data substitution.
    
    Args:
        template: Path to HTML template
        data: Dictionary for template variables
        output_pdf: Output PDF path
        **kwargs: Additional render_pdf options
    
    Returns:
        True if successful
    """
    template_path = Path(template)
    if not template_path.exists():
        print(f"❌ Template not found: {template}")
        return False
    
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_html = f.read()
    
    # Simple variable substitution
    # For complex templating, use Jinja2
    import json
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            # Embed as JSON for JS
            value_str = json.dumps(value)
            template_html = template_html.replace(f'{{{{ {key}_json }}}}', value_str)
        else:
            # Simple string replacement
            template_html = template_html.replace(f'{{{{ {key} }}}}', str(value))
    
    return render_pdf(html_string=template_html, output_pdf=output_pdf, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="Convert HTML to PDF using Playwright"
    )
    
    # Input
    parser.add_argument('input', nargs='?', help='Input HTML file')
    parser.add_argument('output', nargs='?', default='output.pdf', help='Output PDF file')
    parser.add_argument('--html', help='HTML content as string')
    
    # Page format
    parser.add_argument('--format', default='A4', help='Paper format (A4, Letter, etc.)')
    parser.add_argument('--landscape', action='store_true', help='Landscape orientation')
    parser.add_argument('--width', help='Page width (e.g., "210mm")')
    parser.add_argument('--height', help='Page height (e.g., "297mm")')
    
    # Margins
    parser.add_argument('--margin', help='All margins (e.g., "10mm")')
    parser.add_argument('--margin-top', help='Top margin')
    parser.add_argument('--margin-right', help='Right margin')
    parser.add_argument('--margin-bottom', help='Bottom margin')
    parser.add_argument('--margin-left', help='Left margin')
    
    # Headers & footers
    parser.add_argument('--header-html', help='Header HTML template')
    parser.add_argument('--footer-html', help='Footer HTML template')
    parser.add_argument('--display-header-footer', action='store_true', help='Show default header/footer')
    
    # Rendering
    parser.add_argument('--wait-for', help='CSS selector to wait for')
    parser.add_argument('--wait-timeout', type=int, default=30000, help='Wait timeout (ms)')
    parser.add_argument('--scale', type=float, default=1.0, help='Page scale (0.1-2)')
    parser.add_argument('--no-print-background', action='store_true', help='Exclude backgrounds')
    parser.add_argument('--prefer-css-page-size', action='store_true', help='Use CSS page size')
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input and not args.html:
        parser.print_help()
        sys.exit(1)
    
    # Render
    success = render_pdf(
        input_html=args.input,
        html_string=args.html,
        output_pdf=args.output,
        format=args.format,
        landscape=args.landscape,
        width=args.width,
        height=args.height,
        margin=args.margin,
        margin_top=args.margin_top,
        margin_right=args.margin_right,
        margin_bottom=args.margin_bottom,
        margin_left=args.margin_left,
        header_html=args.header_html,
        footer_html=args.footer_html,
        display_header_footer=args.display_header_footer,
        wait_for=args.wait_for,
        wait_timeout=args.wait_timeout,
        scale=args.scale,
        print_background=not args.no_print_background,
        prefer_css_page_size=args.prefer_css_page_size
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
