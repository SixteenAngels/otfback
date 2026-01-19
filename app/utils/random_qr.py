import random
from PIL import Image, ImageDraw
from io import BytesIO
import base64


def generate_random_qr_pattern(size=29, module_size=10, border=4):
    """
    Generate a random QR code-like pattern.

    Args:
        size: Number of modules (blocks) per side (default 29 for QR code Version 3)
        module_size: Pixel size of each module/block
        border: Number of quiet zone modules around the pattern

    Returns:
        PIL Image object
    """
    # Total size including border
    total_size = size + (border * 2)

    # Create image
    img_size = total_size * module_size
    img = Image.new('RGB', (img_size, img_size), 'white')
    draw = ImageDraw.Draw(img)

    # Create random pattern
    pattern = [[random.choice([0, 1]) for _ in range(size)] for _ in range(size)]

    # Add position detection patterns (the three corner squares)
    # Top-left
    add_position_pattern(pattern, 0, 0)
    # Top-right
    add_position_pattern(pattern, size - 7, 0)
    # Bottom-left
    add_position_pattern(pattern, 0, size - 7)

    # Draw the pattern
    for y in range(size):
        for x in range(size):
            if pattern[y][x] == 1:
                x_pos = (x + border) * module_size
                y_pos = (y + border) * module_size
                draw.rectangle(
                    [x_pos, y_pos, x_pos + module_size - 1, y_pos + module_size - 1],
                    fill='black'
                )

    return img


def add_position_pattern(pattern, x_offset, y_offset):
    """Add a QR code position detection pattern (7x7 square pattern)."""
    # Outer 7x7 black square
    for y in range(7):
        for x in range(7):
            if y_offset + y < len(pattern) and x_offset + x < len(pattern[0]):
                pattern[y_offset + y][x_offset + x] = 1

    # Inner 5x5 white square
    for y in range(1, 6):
        for x in range(1, 6):
            if y_offset + y < len(pattern) and x_offset + x < len(pattern[0]):
                pattern[y_offset + y][x_offset + x] = 0

    # Center 3x3 black square
    for y in range(2, 5):
        for x in range(2, 5):
            if y_offset + y < len(pattern) and x_offset + x < len(pattern[0]):
                pattern[y_offset + y][x_offset + x] = 1


def get_png_bytes(size=29, module_size=10, border=4):
    """Return PNG image bytes for a generated random QR-like pattern."""
    img = generate_random_qr_pattern(size=size, module_size=module_size, border=border)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


def get_base64_png(size=29, module_size=10, border=4):
    """Return base64-encoded PNG data (without data URI prefix)."""
    return base64.b64encode(get_png_bytes(size, module_size, border)).decode()
