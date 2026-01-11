#!/usr/bin/env python3
"""
Script to create an icon for Pomodoro Timer app.
Creates an icon with a tomato and piano keys.
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow is required. Install it with: pip install Pillow")
    sys.exit(1)

def draw_tomato(draw, center_x, center_y, size):
    """Draw a tomato/pomodoro"""
    # Main body - red circle
    tomato_color = (239, 71, 111)  # Red color matching app theme
    body_radius = size * 0.35
    draw.ellipse(
        [center_x - body_radius, center_y - body_radius,
         center_x + body_radius, center_y + body_radius],
        fill=tomato_color,
        outline=(200, 50, 80), width=2
    )
    
    # Stem/leaf at top
    stem_color = (76, 175, 80)  # Green
    stem_top = center_y - size * 0.35
    stem_bottom = center_y - size * 0.25
    stem_width = size * 0.08
    
    # Draw stem
    draw.rectangle(
        [center_x - stem_width/2, stem_top,
         center_x + stem_width/2, stem_bottom],
        fill=stem_color
    )
    
    # Small leaf
    leaf_points = [
        (center_x - stem_width/2, stem_bottom),
        (center_x - size * 0.15, stem_bottom + size * 0.05),
        (center_x, stem_bottom)
    ]
    draw.polygon(leaf_points, fill=stem_color)
    
    # Highlight on tomato
    highlight_x = center_x - size * 0.15
    highlight_y = center_y - size * 0.15
    highlight_radius = size * 0.08
    draw.ellipse(
        [highlight_x - highlight_radius, highlight_y - highlight_radius,
         highlight_x + highlight_radius, highlight_y + highlight_radius],
        fill=(255, 200, 200)
    )

def draw_piano_keys(draw, x, y, width, height):
    """Draw piano keys (black and white)"""
    num_white_keys = 4
    num_black_keys = 3
    
    white_key_width = width / num_white_keys
    black_key_width = white_key_width * 0.6
    black_key_height = height * 0.6
    
    # Draw white keys
    for i in range(num_white_keys):
        key_x = x + i * white_key_width
        draw.rectangle(
            [key_x, y,
             key_x + white_key_width - 1, y + height],
            fill=(255, 255, 255),
            outline=(200, 200, 200), width=1
        )
    
    # Draw black keys (positioned between white keys)
    black_positions = [0.7, 1.7, 2.7]  # Positions relative to white keys
    for pos in black_positions:
        key_x = x + pos * white_key_width - black_key_width / 2
        draw.rectangle(
            [key_x, y,
             key_x + black_key_width, y + black_key_height],
            fill=(45, 45, 55),  # Dark gray/black
            outline=(30, 30, 40), width=1
        )

def create_icon(size=1024):
    """Create icon image with tomato and piano keys"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background - rounded square with gradient-like effect
    margin = size * 0.05
    bg_color = (250, 250, 252)  # Light background matching app
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size * 0.1,
        fill=bg_color,
        outline=(220, 220, 230), width=2
    )
    
    # Draw piano keys at the bottom
    piano_y = size * 0.65
    piano_height = size * 0.25
    piano_x = size * 0.15
    piano_width = size * 0.7
    draw_piano_keys(draw, piano_x, piano_y, piano_width, piano_height)
    
    # Draw tomato above piano keys
    tomato_center_x = size / 2
    tomato_center_y = size * 0.35
    draw_tomato(draw, tomato_center_x, tomato_center_y, size)
    
    return img

def create_icns_from_png(png_path, icns_path):
    """Convert PNG to ICNS using macOS iconutil"""
    # Create .iconset directory
    iconset_name = icns_path.replace('.icns', '.iconset')
    
    # Remove existing iconset if present
    import shutil
    if os.path.exists(iconset_name):
        shutil.rmtree(iconset_name)
    os.makedirs(iconset_name)
    
    # Required icon sizes for macOS
    sizes = [
        (16, '16x16'),
        (32, '16x16@2x'),
        (32, '32x32'),
        (64, '32x32@2x'),
        (128, '128x128'),
        (256, '128x128@2x'),
        (256, '256x256'),
        (512, '256x256@2x'),
        (512, '512x512'),
        (1024, '512x512@2x'),
    ]
    
    # Generate all required sizes
    base_img = Image.open(png_path)
    for size, name in sizes:
        resized = base_img.resize((size, size), Image.Resampling.LANCZOS)
        filename = f'icon_{name}.png'
        filepath = os.path.join(iconset_name, filename)
        resized.save(filepath, 'PNG')
    
    # Convert iconset to icns
    import subprocess
    result = subprocess.run(
        ['iconutil', '-c', 'icns', iconset_name, '-o', icns_path],
        capture_output=True,
        text=True
    )
    
    # Clean up iconset directory
    shutil.rmtree(iconset_name)
    
    if result.returncode != 0:
        print(f"Error converting to ICNS: {result.stderr}")
        return False
    
    return True

def main():
    project_root = Path(__file__).parent.parent
    resources_dir = project_root / "resources"
    resources_dir.mkdir(exist_ok=True)
    
    # Create high-res PNG first
    png_path = resources_dir / "icon.png"
    icns_path = resources_dir / "icon.icns"
    
    print("🎨 Creating icon image...")
    icon_img = create_icon(1024)
    icon_img.save(png_path, 'PNG')
    print(f"✅ PNG icon created: {png_path}")
    
    # Convert to ICNS
    if sys.platform == 'darwin':
        print("🔄 Converting to ICNS format...")
        if create_icns_from_png(str(png_path), str(icns_path)):
            print(f"✅ ICNS icon created: {icns_path}")
        else:
            print("⚠️  Failed to create ICNS, but PNG is available")
            sys.exit(1)
    else:
        print("⚠️  ICNS conversion only works on macOS. PNG is available.")
        sys.exit(0)

if __name__ == "__main__":
    main()

