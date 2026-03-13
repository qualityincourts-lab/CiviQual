#!/usr/bin/env python3
"""
Generate CiviQual icon files (ICO and PNG).

This script creates the CiviQual application icon in multiple formats
and sizes for use in Windows installers and application shortcuts.

Requirements:
    pip install pillow

Usage:
    python create_icon.py

Output:
    civiqual_icon.ico - Windows icon (16, 32, 48, 64, 128, 256 px)
    civiqual_icon.png - PNG icon (256x256 px)

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from PIL import Image, ImageDraw
from pathlib import Path


def create_civiqual_icon(output_dir: Path = None):
    """
    Create CiviQual icon at multiple sizes for ICO file.
    
    Args:
        output_dir: Directory to save icon files (default: current directory)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent
    
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    # Brand colors
    BURGUNDY = (109, 19, 42, 255)    # #6d132a
    GOLD = (220, 173, 115, 255)       # #dcad73
    WHITE = (255, 255, 255, 255)
    
    for size in sizes:
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Scale factor (base design is 64px)
        s = size / 64.0
        
        # Gold border (outer rounded rectangle)
        draw.rounded_rectangle(
            [0, 0, size-1, size-1],
            radius=int(4*s),
            fill=GOLD
        )
        
        # White inner area
        margin = int(4*s)
        draw.rounded_rectangle(
            [margin, margin, size-1-margin, size-1-margin],
            radius=int(2*s),
            fill=WHITE
        )
        
        # Four burgundy quadrants
        inner_margin = int(6*s)
        gap = int(2*s)
        center = size // 2
        
        # Upper left quadrant
        draw.rectangle(
            [inner_margin, inner_margin, center-gap, center-gap],
            fill=BURGUNDY
        )
        # Upper right quadrant
        draw.rectangle(
            [center+gap, inner_margin, size-1-inner_margin, center-gap],
            fill=BURGUNDY
        )
        # Lower left quadrant
        draw.rectangle(
            [inner_margin, center+gap, center-gap, size-1-inner_margin],
            fill=BURGUNDY
        )
        # Lower right quadrant
        draw.rectangle(
            [center+gap, center+gap, size-1-inner_margin, size-1-inner_margin],
            fill=BURGUNDY
        )
        
        # Gold dividing cross
        line_width = max(2, int(2*s))
        # Vertical line
        draw.rectangle(
            [center-line_width//2, margin, center+line_width//2, size-1-margin],
            fill=GOLD
        )
        # Horizontal line
        draw.rectangle(
            [margin, center-line_width//2, size-1-margin, center+line_width//2],
            fill=WHITE  # Use white for horizontal to create grid effect
        )
        draw.rectangle(
            [margin, center-line_width//2, size-1-margin, center+line_width//2],
            fill=GOLD
        )
        
        # Upper left: Bar chart (white bars on burgundy)
        if size >= 32:
            bar_width = max(2, int(4*s))
            bar_x = inner_margin + int(4*s)
            base_y = center - gap - int(2*s)
            
            # Bar 1 (shortest)
            draw.rectangle(
                [bar_x, int(22*s), bar_x+bar_width, base_y],
                fill=WHITE
            )
            # Bar 2 (medium)
            bar_x += bar_width + int(2*s)
            draw.rectangle(
                [bar_x, int(18*s), bar_x+bar_width, base_y],
                fill=WHITE
            )
            # Bar 3 (tallest)
            bar_x += bar_width + int(2*s)
            draw.rectangle(
                [bar_x, int(12*s), bar_x+bar_width, base_y],
                fill=WHITE
            )
        
        # Upper right: Control chart line (white on burgundy)
        if size >= 32:
            points = [
                (center + int(6*s), int(22*s)),
                (center + int(12*s), int(16*s)),
                (center + int(18*s), int(20*s)),
                (center + int(24*s), int(14*s)),
            ]
            for i in range(len(points) - 1):
                draw.line([points[i], points[i+1]], fill=WHITE, width=max(1, int(1.5*s)))
            # Data points
            for px, py in points:
                r = max(1, int(1.5*s))
                draw.ellipse([px-r, py-r, px+r, py+r], fill=WHITE)
        
        # Lower left: Histogram bars (gold on burgundy)
        if size >= 32:
            bar_width = max(2, int(3*s))
            bar_x = inner_margin + int(2*s)
            base_y = size - 1 - inner_margin - int(2*s)
            heights = [int(4*s), int(8*s), int(14*s), int(10*s), int(6*s)]
            for h in heights:
                if bar_x + bar_width < center - gap:
                    draw.rectangle(
                        [bar_x, base_y-h, bar_x+bar_width, base_y],
                        fill=GOLD
                    )
                bar_x += bar_width + int(1*s)
        
        # Lower right: Scatter points (gold on burgundy)
        if size >= 32:
            dot_r = max(1, int(2*s))
            dots = [
                (center + int(8*s), size - inner_margin - int(6*s)),
                (center + int(14*s), size - inner_margin - int(10*s)),
                (center + int(20*s), size - inner_margin - int(14*s)),
            ]
            for dx, dy in dots:
                if dx + dot_r < size - inner_margin and dy - dot_r > center + gap:
                    draw.ellipse(
                        [dx-dot_r, dy-dot_r, dx+dot_r, dy+dot_r],
                        fill=GOLD
                    )
        
        images.append(img)
    
    # Save as ICO (Windows icon with multiple sizes)
    ico_path = output_dir / 'civiqual_icon.ico'
    
    # Save the largest image with all sizes embedded
    ico_sizes = [(s, s) for s in sizes]
    images[-1].save(
        ico_path,
        format='ICO',
        sizes=ico_sizes
    )
    print(f"Created: {ico_path}")
    print(f"  Sizes: {', '.join(f'{s}x{s}' for s in sizes)}")
    
    # Save as PNG (256x256 for high-res use)
    png_path = output_dir / 'civiqual_icon.png'
    images[-1].save(png_path, format='PNG')
    print(f"Created: {png_path}")
    print(f"  Size: 256x256")
    
    return ico_path, png_path


if __name__ == '__main__':
    create_civiqual_icon()
