#!/usr/bin/env python3

import os
import re
from pathlib import Path

def check_table_headers():
    """Check all admin templates for table header styling"""
    print("🔍 Checking Table Header Styling in Admin Templates")
    print("=" * 60)
    
    admin_templates_dir = Path('/Users/advikpunugu/Desktop/ComputerScienceIA/CS_IA/templates/admin')
    
    # Find all HTML files
    html_files = list(admin_templates_dir.glob('*.html'))
    
    for file_path in html_files:
        print(f"\n📄 Checking {file_path.name}:")
        print("-" * 40)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for table headers
            thead_pattern = r'<thead>.*?</thead>'
            table_headers = re.findall(thead_pattern, content, re.DOTALL)
            
            if table_headers:
                for i, header in enumerate(table_headers, 1):
                    print(f"  Table {i}:")
                    
                    # Check for dark background styling
                    dark_bg_patterns = [
                        r'background-color:\s*#374151',
                        r'background-color:\s*#1f2937',
                        r'background-color:\s*#111827',
                        r'bg-gray-700',
                        r'bg-gray-800',
                        r'bg-gray-900'
                    ]
                    
                    has_dark_bg = any(re.search(pattern, header, re.IGNORECASE) for pattern in dark_bg_patterns)
                    
                    # Check for white text
                    white_text_patterns = [
                        r'color:\s*white',
                        r'color:\s*#ffffff',
                        r'text-white'
                    ]
                    
                    has_white_text = any(re.search(pattern, header, re.IGNORECASE) for pattern in white_text_patterns)
                    
                    if has_dark_bg and has_white_text:
                        print("    ✅ Dark background with white text - GOOD")
                    elif has_dark_bg:
                        print("    ⚠️  Dark background but missing white text")
                    elif has_white_text:
                        print("    ⚠️  White text but missing dark background")
                    else:
                        print("    ❌ Missing dark header styling")
                    
                    # Extract specific styling
                    style_match = re.search(r'style="([^"]*)"', header)
                    if style_match:
                        style = style_match.group(1)
                        # Extract background-color and color specifically
                        bg_match = re.search(r'background-color:\s*([^;]+)', style)
                        color_match = re.search(r'color:\s*([^;]+)', style)
                        
                        if bg_match:
                            print(f"    📎 Background: {bg_match.group(1).strip()}")
                        if color_match:
                            print(f"    📎 Text Color: {color_match.group(1).strip()}")
            else:
                # Check if file has tables at all
                if '<table' in content:
                    print("    🔍 Has table but no thead found")
                else:
                    print("    ➖ No tables found")
                    
        except Exception as e:
            print(f"    ❌ Error reading file: {e}")
    
    print(f"\n📊 Summary:")
    print("✅ All admin templates checked for table header styling")
    print("✅ Templates should have consistent dark headers throughout")

if __name__ == "__main__":
    check_table_headers()
