"""Standalone icon generator for Promethean Light"""

from PIL import Image, ImageDraw
from pathlib import Path


def create_prometheus_icon(output_path="promethean.ico"):
    """Create a Prometheus-themed torch icon"""
    # Create 64x64 icon with transparency
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Gradient fire colors
    colors = {
        'flame_outer': (255, 69, 0),     # Red-Orange
        'flame_mid': (255, 165, 0),       # Orange
        'flame_inner': (255, 255, 0),     # Yellow
        'handle': (101, 67, 33),          # Brown
        'bowl': (139, 90, 43),            # Bronze
        'glow': (255, 200, 0),            # Gold glow
    }

    # Draw handle
    draw.rectangle([(28, 45), (36, 60)], fill=colors['handle'])

    # Draw torch bowl
    draw.ellipse([(20, 35), (44, 50)], fill=colors['bowl'])
    # Bowl rim (lighter)
    draw.ellipse([(22, 35), (42, 42)], fill=(180, 120, 60))

    # Add glow effect (bottom layer)
    for i in range(4):
        alpha = 40 - (i * 10)
        glow_size = 54 - (i * 4)
        offset = (size - glow_size) // 2
        glow_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_draw.ellipse(
            [(offset, offset - 12), (offset + glow_size, offset + glow_size - 12)],
            fill=(*colors['glow'], alpha)
        )
        img = Image.alpha_composite(img, glow_layer)
        draw = ImageDraw.Draw(img)

    # Draw outer flame (red-orange)
    flame_outer = [
        (32, 10),   # Top point
        (20, 30),   # Left curve
        (32, 40),   # Bottom center
        (44, 30),   # Right curve
    ]
    draw.polygon(flame_outer, fill=colors['flame_outer'])

    # Draw middle flame (orange)
    flame_mid = [
        (32, 15),
        (24, 30),
        (32, 38),
        (40, 30),
    ]
    draw.polygon(flame_mid, fill=colors['flame_mid'])

    # Draw inner flame (yellow)
    flame_inner = [
        (32, 18),
        (28, 30),
        (32, 35),
        (36, 30),
    ]
    draw.polygon(flame_inner, fill=colors['flame_inner'])

    # Add flame highlights (white hot spots)
    highlight_points = [
        (32, 20),
        (30, 25),
        (34, 25),
    ]
    for point in highlight_points:
        draw.ellipse(
            [(point[0]-2, point[1]-2), (point[0]+2, point[1]+2)],
            fill=(255, 255, 255, 200)
        )

    # Save as multi-resolution .ico file
    output_path = Path(output_path)
    img.save(output_path, format='ICO', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128)])

    print(f"[OK] Icon created: {output_path.absolute()}")
    return output_path


if __name__ == "__main__":
    create_prometheus_icon()
